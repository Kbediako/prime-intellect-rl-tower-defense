#!/usr/bin/env python3
"""Serve actual-game command decisions from a local base model plus optional LoRA adapter."""

from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
from typing import Any, Dict, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from prime_td_env import actual_game_env as actual_env

import run_actual_game_command_local_eval as local_eval


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8789


def _resolve_path(raw_path: Path | str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _extract_completion_text(payload: Dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("chat completion response is missing choices")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise ValueError("chat completion choice must be an object")
    message = first_choice.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, str):
            return content
    text = first_choice.get("text")
    if isinstance(text, str):
        return text
    raise ValueError("chat completion response is missing assistant text")


def _non_empty_string(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _session_key(request_payload: Dict[str, Any], bridge_input: Dict[str, Any]) -> str:
    context = request_payload.get("context")
    if isinstance(context, dict):
        session = context.get("session")
        if isinstance(session, dict):
            for key in ("matchId", "sessionId", "lobbyId"):
                value = _non_empty_string(session.get(key))
                if value:
                    return value
        for key in ("sessionId", "lobbyId"):
            value = _non_empty_string(context.get(key))
            if value:
                return value
    lobby = bridge_input.get("lobby")
    if isinstance(lobby, dict):
        lobby_id = _non_empty_string(lobby.get("lobbyId"))
        if lobby_id:
            return lobby_id
    if isinstance(context, dict):
        for key in ("playerId", "llmPlayerId", "targetPlayerId"):
            value = _non_empty_string(context.get(key))
            if value:
                return value
    player_id = _non_empty_string(bridge_input.get("playerId"))
    if player_id:
        return player_id
    return "__default__"


def noop_decision(reason: str) -> Dict[str, Any]:
    return {
        "kind": "noop",
        "reason": str(reason).strip() or "no_decision",
    }


def build_decision_from_request(
    request_payload: Dict[str, Any],
    *,
    prediction_fn,
    known_tower_owners_by_session: Dict[str, Dict[int, str]],
) -> Dict[str, Any]:
    if not isinstance(request_payload, dict):
        raise ValueError("request payload must be a JSON object")
    bridge_input = request_payload.get("input")
    if not isinstance(bridge_input, dict):
        raise ValueError("request payload must include object field 'input'")

    session_key = _session_key(request_payload, bridge_input)
    prior_known_owners = known_tower_owners_by_session.get(session_key, {})
    updated_known_owners = actual_env._sync_known_tower_owners(bridge_input, prior_known_owners)
    summary = actual_env.create_command_summary_from_bridge_input(
        bridge_input,
        known_tower_owners=updated_known_owners,
    )
    known_tower_owners_by_session[session_key] = updated_known_owners

    messages = actual_env.build_actual_game_command_messages(summary)
    raw_response = prediction_fn({}, messages)
    completion_text = _extract_completion_text(raw_response)
    parsed_decision, is_strict_json = actual_env._extract_json_object(completion_text)
    if not parsed_decision:
        return noop_decision("model response was not valid JSON")

    try:
        normalized_decision = actual_env.normalize_command_decision(
            parsed_decision,
            summary["allowedCommands"],
        )
    except ValueError as exc:
        return noop_decision(str(exc))

    result = dict(normalized_decision)
    if not is_strict_json:
        result["warning"] = "response contained surrounding text"
    return result


class AdapterDecisionService:
    def __init__(self, *, prediction_fn, model: str, adapter_path: str | None, token: str) -> None:
        self.prediction_fn = prediction_fn
        self.model = model
        self.adapter_path = adapter_path
        self.token = token
        self._lock = threading.Lock()
        self._known_tower_owners_by_session: Dict[str, Dict[int, str]] = {}

    def health_payload(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "model": self.model,
            "adapter_path": self.adapter_path,
            "active_sessions": len(self._known_tower_owners_by_session),
        }

    def decide(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            return build_decision_from_request(
                request_payload,
                prediction_fn=self.prediction_fn,
                known_tower_owners_by_session=self._known_tower_owners_by_session,
            )


def make_handler(service: AdapterDecisionService):
    class _Handler(BaseHTTPRequestHandler):
        server_version = "ActualGameAdapterServer/0.1"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - BaseHTTPRequestHandler API
            return

        def _send_json(self, status_code: int, payload: Dict[str, Any]) -> None:
            body = (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json_body(self) -> Dict[str, Any]:
            content_length = int(self.headers.get("Content-Length", "0") or "0")
            raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON body: {exc.msg}") from exc
            if not isinstance(payload, dict):
                raise ValueError("request body must be a JSON object")
            return payload

        def _require_token(self) -> bool:
            if not service.token:
                return True
            header = str(self.headers.get("Authorization", "") or "")
            expected = f"Bearer {service.token}"
            return header.strip() == expected

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            if self.path == "/health":
                self._send_json(HTTPStatus.OK, service.health_payload())
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            if self.path != "/decide":
                self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
                return
            if not self._require_token():
                self._send_json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
                return
            try:
                payload = self._read_json_body()
                decision = service.decide(payload)
                request_id = payload.get("requestId")
                if isinstance(request_id, str) and request_id.strip():
                    decision = dict(decision)
                    decision["requestId"] = request_id.strip()
                self._send_json(HTTPStatus.OK, {"ok": True, "decision": decision})
            except ValueError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            except Exception as exc:  # pragma: no cover - runtime safeguard
                print(
                    json.dumps(
                        {
                            "ok": False,
                            "error": "internal_server_error",
                            "detail": str(exc),
                        },
                        sort_keys=True,
                    ),
                    file=sys.stderr,
                    flush=True,
                )
                self._send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"ok": False, "error": "internal_server_error"},
                )

    return _Handler


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Base Hugging Face model id or local model path.")
    parser.add_argument("--adapter-path", default="", help="Optional PEFT adapter directory.")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Bind host. Default: {DEFAULT_HOST}")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Bind port. Default: {DEFAULT_PORT}")
    parser.add_argument("--token", default="", help="Optional bearer token required by POST /decide.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Generation temperature. Default: 0.0")
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=128,
        help="Maximum generated completion tokens. Default: 128",
    )
    parser.add_argument(
        "--load-in-4bit",
        action="store_true",
        help="Load the base model in 4-bit quantized mode.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    adapter_path = _resolve_path(args.adapter_path) if args.adapter_path else None
    bundle = local_eval._load_model_bundle(
        model_name=args.model,
        adapter_path=adapter_path,
        load_in_4bit=bool(args.load_in_4bit),
    )
    prediction_fn = local_eval._build_prediction_fn(
        bundle=bundle,
        temperature=float(args.temperature),
        max_new_tokens=int(args.max_new_tokens),
    )
    service = AdapterDecisionService(
        prediction_fn=prediction_fn,
        model=args.model,
        adapter_path=str(adapter_path) if adapter_path is not None else None,
        token=str(args.token or ""),
    )
    server = ThreadingHTTPServer((args.host, args.port), make_handler(service))
    print(
        json.dumps(
            {
                "ok": True,
                "host": args.host,
                "port": args.port,
                "model": args.model,
                "adapter_path": str(adapter_path) if adapter_path is not None else None,
                "load_in_4bit": bool(args.load_in_4bit),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:  # pragma: no cover - manual stop path
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
