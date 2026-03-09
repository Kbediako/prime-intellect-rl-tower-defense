import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import threading
import types
import unittest
import urllib.error
import urllib.request


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = REPO_ROOT / "scripts" / "run_actual_game_command_adapter_server.py"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "actual_game_command_examples.json"


def _ensure_test_deps() -> None:
    if "verifiers" not in sys.modules:
        vf = types.SimpleNamespace()
        vf.Messages = list
        vf.State = dict
        vf.Info = dict

        class SingleTurnEnv:  # pragma: no cover - stub
            def __init__(self, *args, **kwargs) -> None:
                self.args = args
                self.kwargs = kwargs

        vf.SingleTurnEnv = SingleTurnEnv

        class MultiTurnEnv:  # pragma: no cover - stub
            def __init__(self, *args, **kwargs) -> None:
                self.args = args
                self.kwargs = kwargs

            async def setup_state(self, state):
                return state

            def add_trajectory_step(self, state, step):
                return step

        vf.MultiTurnEnv = MultiTurnEnv

        def stop(func=None, **_kwargs):  # pragma: no cover - stub
            if func is None:
                def _decorator(inner):
                    return inner
                return _decorator
            return func

        vf.stop = stop

        class Rubric:  # pragma: no cover - stub
            def __init__(self, *args, **kwargs) -> None:
                self.args = args
                self.kwargs = kwargs

        vf.Rubric = Rubric
        vf.Environment = object
        sys.modules["verifiers"] = vf

    if "datasets" not in sys.modules:
        ds = types.SimpleNamespace()

        class Dataset:  # pragma: no cover - stub
            @staticmethod
            def from_dict(payload):
                return payload

        ds.Dataset = Dataset
        sys.modules["datasets"] = ds


_ensure_test_deps()


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SERVER = _load_module("run_actual_game_command_adapter_server", SERVER_PATH)


class ActualGameCommandAdapterServerTest(unittest.TestCase):
    def _load_fixture(self) -> dict:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        return payload["examples"][0]

    def _request_payload(
        self,
        *,
        context_overrides: dict | None = None,
        bridge_input_overrides: dict | None = None,
    ) -> dict:
        example = self._load_fixture()
        context = {
            "playerId": "bot-bridge",
            "session": {"matchId": "match-default"},
        }
        if context_overrides:
            context.update(context_overrides)
        bridge_input = dict(example["bridge_input"])
        if bridge_input_overrides:
            bridge_input.update(bridge_input_overrides)
        return {
            "version": "td.multiplayer.llm-bridge.request.v1",
            "providerId": "pi",
            "modelId": "fixture-model",
            "requestId": "req-0001",
            "context": context,
            "input": bridge_input,
        }

    def _prediction_fn(self, _example: dict, _messages: list[dict[str, str]]) -> dict:
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "kind": "command",
                                "commandType": "upgrade_tower",
                                "payload": {"towerId": 7, "path": "top"},
                            }
                        )
                    }
                }
            ]
        }

    def _start_server(self, service):
        server = SERVER.ThreadingHTTPServer(("127.0.0.1", 0), SERVER.make_handler(service))
        thread = threading.Thread(
            target=server.serve_forever,
            kwargs={"poll_interval": 0.05},
            daemon=True,
        )
        thread.start()
        return server, thread

    def _post_json(self, url: str, payload: dict) -> bytes:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.read()

    def test_build_decision_from_request_returns_normalized_command(self) -> None:
        request_payload = self._request_payload()

        decision = SERVER.build_decision_from_request(
            request_payload,
            prediction_fn=self._prediction_fn,
            known_tower_owners_by_session={},
        )
        self.assertEqual(
            decision,
            {
                "kind": "command",
                "commandType": "upgrade_tower",
                "payload": {"towerId": 7, "path": "top"},
            },
        )

    def test_build_decision_from_request_returns_noop_for_invalid_json(self) -> None:
        request_payload = self._request_payload()

        def _prediction_fn(_example: dict, _messages: list[dict[str, str]]) -> dict:
            return {"choices": [{"message": {"content": "not-json"}}]}

        decision = SERVER.build_decision_from_request(
            request_payload,
            prediction_fn=_prediction_fn,
            known_tower_owners_by_session={},
        )
        self.assertEqual(decision["kind"], "noop")
        self.assertIn("valid JSON", decision["reason"])

    def test_build_decision_from_request_returns_noop_for_disallowed_command(self) -> None:
        request_payload = self._request_payload()

        def _prediction_fn(_example: dict, _messages: list[dict[str, str]]) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "kind": "command",
                                    "commandType": "sell_tower",
                                    "payload": {"towerId": 7},
                                }
                            )
                        }
                    }
                ]
            }

        decision = SERVER.build_decision_from_request(
            request_payload,
            prediction_fn=_prediction_fn,
            known_tower_owners_by_session={},
        )
        self.assertEqual(decision["kind"], "noop")
        self.assertIn("not allowed", decision["reason"])

    def test_adapter_service_tracks_match_sessions_independently(self) -> None:
        service = SERVER.AdapterDecisionService(
            prediction_fn=self._prediction_fn,
            model="fixture-model",
            adapter_path=None,
            token="",
        )

        first_payload = self._request_payload(context_overrides={"session": {"matchId": "match-001"}})
        second_payload = self._request_payload(context_overrides={"session": {"matchId": "match-002"}})

        first_decision = service.decide(first_payload)
        second_decision = service.decide(second_payload)

        self.assertEqual(first_decision["kind"], "command")
        self.assertEqual(second_decision["kind"], "command")
        self.assertEqual(
            set(service._known_tower_owners_by_session.keys()),
            {"match-001", "match-002"},
        )

    def test_handler_returns_http_500_for_internal_server_error(self) -> None:
        def _failing_prediction(_example: dict, _messages: list[dict[str, str]]) -> dict:
            raise RuntimeError("boom")

        service = SERVER.AdapterDecisionService(
            prediction_fn=_failing_prediction,
            model="fixture-model",
            adapter_path=None,
            token="",
        )
        server, thread = self._start_server(service)
        try:
            url = f"http://127.0.0.1:{server.server_address[1]}/decide"
            stderr_buffer = io.StringIO()
            with contextlib.redirect_stderr(stderr_buffer):
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    self._post_json(url, self._request_payload())
            self.assertEqual(ctx.exception.code, 500)
            payload = json.loads(ctx.exception.read().decode("utf-8"))
            self.assertEqual(payload, {"ok": False, "error": "internal_server_error"})
            ctx.exception.close()
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()


if __name__ == "__main__":
    unittest.main()
