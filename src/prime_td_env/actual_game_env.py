"""Actual-game command replay environment for offline legality-first training."""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Tuple

try:
    from datasets import Dataset
except ImportError:  # pragma: no cover - utility callers may only need schema helpers
    Dataset = None

try:
    import verifiers as vf
except ImportError:  # pragma: no cover - utility callers may only need schema helpers
    vf = None


_SINGLE_TURN_ENV_BASE = vf.SingleTurnEnv if vf is not None else object

MODULE_DIR = Path(__file__).resolve().parent


BRIDGE_INPUT_VERSION = "td.multiplayer.llm-bridge.input.v1"
COMMAND_SUMMARY_SCHEMA_VERSION = "td.actual_game.command_summary.v1"
COMMAND_TYPES = (
    "place_tower",
    "upgrade_tower",
    "sell_tower",
    "trigger_next_round",
)
NOOP_KIND = "noop"
DECISION_KIND = "command"
STATUS_VALUES = {
    "warmup",
    "spawning",
    "intermission",
    "active",
    "defeat",
    "complete",
}
PLACE_TOWER_TYPES = {"dart", "sniper", "cannon"}
UPGRADE_PATHS = {"top", "middle", "bottom"}
SAFE_PLACEMENT_ANCHORS = [
    {"x": 60, "y": 60},
    {"x": 336, "y": 64},
    {"x": 432, "y": 64},
    {"x": 336, "y": 152},
    {"x": 432, "y": 152},
    {"x": 336, "y": 230},
    {"x": 336, "y": 310},
    {"x": 600, "y": 150},
    {"x": 632, "y": 228},
    {"x": 714, "y": 312},
    {"x": 900, "y": 180},
    {"x": 900, "y": 300},
    {"x": 630, "y": 499},
    {"x": 760, "y": 500},
    {"x": 900, "y": 500},
]
MAX_COMMAND_RESULTS_TAIL = 8
MAX_TOWERS_IN_SUMMARY = 12
MAX_DECISION_CHARS = 4000
FORMAT_INVALID_REWARD = -1.0

DEFAULT_ACTUAL_GAME_COMMAND_CONFIG: Dict[str, Any] = {
    "wrapper": "actual_game_command",
    "dataset": {
        "examples_inline": [],
    },
    "reward_weights": {
        "format": 0.5,
        "env": 1.0,
    },
}

ACTUAL_GAME_COMMAND_SYSTEM_PROMPT = (
    "You are a tower defence teammate controller.\n"
    "Return exactly one JSON object and no extra text.\n"
    "Goal: survive as long as possible.\n"
    "Allowed commands: place_tower, sell_tower, upgrade_tower, trigger_next_round, noop.\n"
    "Prefer legal commands only.\n"
    "Use only the tower ids and commands present in the current state.\n"
    "For place_tower choose type in [dart,sniper,cannon] and coordinates near safePlacementAnchors.\n"
    "Output schema:\n"
    "{\"kind\":\"command\"|\"noop\",\"commandType\":\"place_tower|sell_tower|upgrade_tower|trigger_next_round\",\"payload\":{},\"reason\":\"...for noop\"}"
)


def _require_training_runtime() -> None:
    if Dataset is None or vf is None:
        raise ImportError(
            "actual_game_command requires both 'datasets' and 'verifiers' to build datasets or "
            "load the environment"
        )


def _is_plain_object(value: Any) -> bool:
    return isinstance(value, dict)


def _normalize_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _normalize_non_negative_integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be an integer >= 0")
    return value


def _normalize_positive_integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be an integer > 0")
    return value


def _normalize_non_negative_number(value: Any, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
    ):
        raise ValueError(f"{field} must be a number >= 0")
    return float(value)


def _normalize_finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite number")
    return float(value)


def _sorted_object(value: Any) -> Any:
    if isinstance(value, list):
        return [_sorted_object(item) for item in value]
    if not isinstance(value, dict):
        return value
    return {key: _sorted_object(value[key]) for key in sorted(value)}


def _ensure_only_keys(value: Dict[str, Any], allowed_keys: Iterable[str], field: str) -> None:
    allowed = set(allowed_keys)
    extra_keys = sorted(set(value) - allowed)
    if extra_keys:
        raise ValueError(f"{field} has unsupported keys: {', '.join(extra_keys)}")


def _completion_to_text(completion: vf.Messages) -> str:
    if isinstance(completion, list) and completion:
        last = completion[-1]
        if isinstance(last, dict):
            return str(last.get("content", ""))
    return str(completion or "")


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
    return stripped.strip()


def _extract_json_object(text: str) -> Tuple[Dict[str, Any] | None, bool]:
    raw = _strip_code_fences(text)
    if not raw or len(raw) > MAX_DECISION_CHARS:
        return None, False
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed, True
    except Exception:
        pass
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        return None, False
    candidate = match.group(0)
    if len(candidate) > MAX_DECISION_CHARS:
        return None, False
    try:
        parsed = json.loads(candidate)
    except Exception:
        return None, False
    if not isinstance(parsed, dict):
        return None, False
    return parsed, candidate.strip() == raw.strip()


def _normalize_allowed_commands(value: Any) -> List[str]:
    if not isinstance(value, list) or not value:
        raise ValueError("allowedCommands must be a non-empty list")
    normalized: List[str] = []
    seen = set()
    for entry in value:
        command = _normalize_non_empty_string(entry, "allowedCommands[]").lower()
        if command not in COMMAND_TYPES:
            raise ValueError(f"Unsupported allowed command: {command}")
        if command not in seen:
            normalized.append(command)
            seen.add(command)
    return normalized


def validate_bridge_input(value: Any) -> Dict[str, Any]:
    if not _is_plain_object(value):
        raise ValueError("bridge input must be a plain object")
    required_fields = (
        "version",
        "tick",
        "stateVersion",
        "stateDigest",
        "playerId",
        "allowedCommands",
        "lastCommandResults",
        "deadlineAt",
        "budgetMs",
        "state",
    )
    for field in required_fields:
        if field not in value:
            raise ValueError(f"bridge input missing required field: {field}")
    version = _normalize_non_empty_string(value.get("version"), "version")
    if version != BRIDGE_INPUT_VERSION:
        raise ValueError(f"Unsupported bridge input version: {version}")
    tick = _normalize_non_negative_integer(value.get("tick"), "tick")
    state_version = _normalize_non_negative_integer(value.get("stateVersion"), "stateVersion")
    state_digest = _normalize_non_empty_string(value.get("stateDigest"), "stateDigest")
    player_id = _normalize_non_empty_string(value.get("playerId"), "playerId")
    allowed_commands = _normalize_allowed_commands(value.get("allowedCommands"))
    if not isinstance(value.get("lastCommandResults"), list):
        raise ValueError("lastCommandResults must be a list")
    deadline_at = _normalize_non_negative_integer(value.get("deadlineAt"), "deadlineAt")
    budget_ms = _normalize_positive_integer(value.get("budgetMs"), "budgetMs")
    state = value.get("state")
    if not _is_plain_object(state):
        raise ValueError("state must be a plain object")
    normalized: Dict[str, Any] = {
        "version": version,
        "tick": tick,
        "stateVersion": state_version,
        "stateDigest": state_digest,
        "playerId": player_id,
        "allowedCommands": allowed_commands,
        "lastCommandResults": copy.deepcopy(value.get("lastCommandResults")),
        "deadlineAt": deadline_at,
        "budgetMs": budget_ms,
        "state": copy.deepcopy(state),
    }
    for optional_field in ("economy", "lobby"):
        optional_value = value.get(optional_field)
        if optional_value is None or _is_plain_object(optional_value):
            normalized[optional_field] = copy.deepcopy(optional_value)
        elif optional_field in value:
            raise ValueError(f"{optional_field} must be an object or null")
    return normalized


def _get_player_cash(bridge_input: Dict[str, Any]) -> float:
    player_id = bridge_input.get("playerId", "")
    economy = bridge_input.get("economy")
    if not isinstance(player_id, str) or not isinstance(economy, dict):
        return 0.0
    players = economy.get("players")
    if not isinstance(players, dict):
        return 0.0
    player = players.get(player_id)
    if not isinstance(player, dict):
        return 0.0
    cash = player.get("cash")
    if isinstance(cash, bool) or not isinstance(cash, (int, float)):
        return 0.0
    return float(cash)


def _get_team_cash(bridge_input: Dict[str, Any]) -> float:
    economy = bridge_input.get("economy")
    if isinstance(economy, dict):
        team_totals = economy.get("team_totals")
        if isinstance(team_totals, dict):
            cash = team_totals.get("current_cash")
            if not isinstance(cash, bool) and isinstance(cash, (int, float)):
                return float(cash)
    state = bridge_input.get("state")
    if isinstance(state, dict):
        cash = state.get("cash")
        if not isinstance(cash, bool) and isinstance(cash, (int, float)):
            return float(cash)
    return _get_player_cash(bridge_input)


def _to_tower_id(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 1:
        return value
    if isinstance(value, float) and value.is_integer() and value >= 1:
        return int(value)
    if isinstance(value, str) and value.isdigit():
        parsed = int(value)
        if parsed >= 1:
            return parsed
    return None


def _get_state_towers(bridge_input: Dict[str, Any]) -> List[Dict[str, Any]]:
    state = bridge_input.get("state")
    towers = state.get("towers") if isinstance(state, dict) else None
    return towers if isinstance(towers, list) else []


def _sync_known_tower_owners(
    bridge_input: Dict[str, Any],
    known_tower_owners: Dict[int, str] | None = None,
) -> Dict[int, str]:
    owners = dict(known_tower_owners or {})
    current_tower_ids = {
        tower_id
        for tower_id in (
            _to_tower_id(tower.get("id")) for tower in _get_state_towers(bridge_input) if isinstance(tower, dict)
        )
        if tower_id is not None
    }
    for tower_id in list(owners):
        if tower_id not in current_tower_ids:
            owners.pop(tower_id, None)

    for entry in bridge_input.get("lastCommandResults", []):
        if not isinstance(entry, dict):
            continue
        command = entry.get("command")
        result = entry.get("result")
        if not isinstance(command, dict) or not isinstance(result, dict):
            continue
        player_id = str(command.get("playerId", "")).strip()
        if not player_id or result.get("success") is not True:
            continue
        command_type = str(command.get("type", "")).strip().lower()
        if command_type == "place_tower":
            tower_id = _to_tower_id(result.get("towerId"))
            if tower_id is not None:
                owners[tower_id] = player_id
        elif command_type == "sell_tower":
            tower_id = _to_tower_id(command.get("payload", {}).get("towerId") if isinstance(command.get("payload"), dict) else None)
            if tower_id is not None:
                owners.pop(tower_id, None)
        elif command_type == "upgrade_tower":
            tower_id = _to_tower_id(command.get("payload", {}).get("towerId") if isinstance(command.get("payload"), dict) else None)
            if tower_id is not None and tower_id not in owners:
                owners[tower_id] = player_id
    return owners


def _get_player_tower_ids(
    bridge_input: Dict[str, Any],
    known_tower_owners: Dict[int, str],
) -> List[int]:
    player_id = bridge_input.get("playerId", "")
    if not isinstance(player_id, str) or not player_id:
        return []
    tower_ids = [
        tower_id
        for tower_id in (
            _to_tower_id(tower.get("id")) for tower in _get_state_towers(bridge_input) if isinstance(tower, dict)
        )
        if tower_id is not None and known_tower_owners.get(tower_id) == player_id
    ]
    tower_ids.sort(reverse=True)
    return tower_ids


def _get_summary_tower_ids(
    bridge_input: Dict[str, Any],
    known_tower_owners: Dict[int, str],
) -> List[int]:
    player_tower_ids = _get_player_tower_ids(bridge_input, known_tower_owners)
    if player_tower_ids:
        return player_tower_ids

    visible_tower_ids = [
        tower_id
        for tower_id in (
            _to_tower_id(tower.get("id")) for tower in _get_state_towers(bridge_input) if isinstance(tower, dict)
        )
        if tower_id is not None
    ]
    visible_tower_ids.sort(reverse=True)
    if not visible_tower_ids:
        return []

    known_visible_tower_ids = {tower_id for tower_id in visible_tower_ids if tower_id in known_tower_owners}
    if len(known_visible_tower_ids) != len(visible_tower_ids):
        return visible_tower_ids
    return []


def _get_visible_safe_placement_anchors(towers: Iterable[Dict[str, Any]]) -> List[Dict[str, int]]:
    occupied_positions = set()
    for tower in towers:
        if not isinstance(tower, dict):
            continue
        position = tower.get("position")
        if not isinstance(position, dict):
            continue
        try:
            x = _normalize_finite_number(position.get("x"), "tower.position.x")
            y = _normalize_finite_number(position.get("y"), "tower.position.y")
        except ValueError:
            continue
        occupied_positions.add((x, y))
    return [
        copy.deepcopy(anchor)
        for anchor in SAFE_PLACEMENT_ANCHORS
        if (float(anchor["x"]), float(anchor["y"])) not in occupied_positions
    ]


def _create_command_summary_from_validated_bridge_input(
    normalized_input: Dict[str, Any],
    known_tower_owners: Dict[int, str] | None = None,
) -> Dict[str, Any]:
    state = normalized_input["state"]
    towers = state.get("towers") if isinstance(state.get("towers"), list) else []
    enemies = state.get("enemies") if isinstance(state.get("enemies"), list) else []
    synced_owners = _sync_known_tower_owners(normalized_input, known_tower_owners)
    player_tower_ids = _get_summary_tower_ids(normalized_input, synced_owners)
    summary = {
        "schemaVersion": COMMAND_SUMMARY_SCHEMA_VERSION,
        "tick": normalized_input["tick"],
        "stateVersion": normalized_input["stateVersion"],
        "playerId": normalized_input["playerId"],
        "allowedCommands": list(normalized_input["allowedCommands"]),
        "round": _normalize_non_negative_integer(state.get("round", 0), "state.round"),
        "status": _normalize_non_empty_string(state.get("status", ""), "state.status").lower(),
        "lives": _normalize_non_negative_number(state.get("lives", 0), "state.lives"),
        "playerCash": _get_player_cash(normalized_input),
        "teamCash": _get_team_cash(normalized_input),
        "map": {
            "width": _normalize_finite_number(state.get("width", 960), "state.width"),
            "height": _normalize_finite_number(state.get("height", 540), "state.height"),
        },
        "safePlacementAnchors": _get_visible_safe_placement_anchors(towers),
        "playerTowerIds": player_tower_ids,
        "playerTowerCount": len(player_tower_ids),
        "towers": [],
        "enemyCount": len(enemies),
        "commandResultsTail": [],
    }
    if summary["status"] not in STATUS_VALUES:
        raise ValueError(f"Unsupported status: {summary['status']}")
    for tower in towers[:MAX_TOWERS_IN_SUMMARY]:
        if not isinstance(tower, dict):
            continue
        summary["towers"].append(
            {
                "id": _to_tower_id(tower.get("id")),
                "type": str(tower.get("type", "")).strip(),
                "x": _normalize_finite_number(tower.get("position", {}).get("x", 0), "tower.position.x")
                if isinstance(tower.get("position"), dict)
                else None,
                "y": _normalize_finite_number(tower.get("position", {}).get("y", 0), "tower.position.y")
                if isinstance(tower.get("position"), dict)
                else None,
                "invested": _normalize_non_negative_number(tower.get("invested", 0), "tower.invested")
                if tower.get("invested") is not None
                else None,
                "upgrades": copy.deepcopy(tower.get("upgrades")) if _is_plain_object(tower.get("upgrades")) else None,
            }
        )
    for entry in normalized_input["lastCommandResults"][-MAX_COMMAND_RESULTS_TAIL:]:
        if not isinstance(entry, dict):
            continue
        command = entry.get("command") if isinstance(entry.get("command"), dict) else {}
        result = entry.get("result") if isinstance(entry.get("result"), dict) else {}
        summary["commandResultsTail"].append(
            {
                "id": _to_tower_id(entry.get("id")),
                "type": str(command.get("type", "")).strip().lower(),
                "playerId": str(command.get("playerId", "")).strip(),
                "success": result.get("success") is True,
                "reason": str(result.get("reason", "")).strip(),
            }
        )
    return validate_command_summary(summary)


def create_command_summary_from_bridge_input(
    bridge_input: Dict[str, Any],
    known_tower_owners: Dict[int, str] | None = None,
) -> Dict[str, Any]:
    normalized_input = validate_bridge_input(bridge_input)
    return _create_command_summary_from_validated_bridge_input(normalized_input, known_tower_owners)


def validate_command_summary(value: Any) -> Dict[str, Any]:
    if not _is_plain_object(value):
        raise ValueError("command summary must be a plain object")
    schema_version = _normalize_non_empty_string(value.get("schemaVersion"), "schemaVersion")
    if schema_version != COMMAND_SUMMARY_SCHEMA_VERSION:
        raise ValueError(f"Unsupported command summary version: {schema_version}")
    status = _normalize_non_empty_string(value.get("status"), "status").lower()
    if status not in STATUS_VALUES:
        raise ValueError(f"Unsupported status: {status}")
    map_payload = value.get("map")
    if not _is_plain_object(map_payload):
        raise ValueError("map must be an object")
    towers = value.get("towers")
    if not isinstance(towers, list):
        raise ValueError("towers must be a list")
    command_results_tail = value.get("commandResultsTail")
    if not isinstance(command_results_tail, list):
        raise ValueError("commandResultsTail must be a list")
    safe_anchors = value.get("safePlacementAnchors")
    if not isinstance(safe_anchors, list) or not safe_anchors:
        raise ValueError("safePlacementAnchors must be a non-empty list")
    normalized = {
        "schemaVersion": schema_version,
        "tick": _normalize_non_negative_integer(value.get("tick"), "tick"),
        "stateVersion": _normalize_non_negative_integer(value.get("stateVersion"), "stateVersion"),
        "playerId": _normalize_non_empty_string(value.get("playerId"), "playerId"),
        "allowedCommands": _normalize_allowed_commands(value.get("allowedCommands")),
        "round": _normalize_non_negative_integer(value.get("round"), "round"),
        "status": status,
        "lives": _normalize_non_negative_number(value.get("lives"), "lives"),
        "playerCash": _normalize_non_negative_number(value.get("playerCash"), "playerCash"),
        "teamCash": _normalize_non_negative_number(
            value.get("teamCash", value.get("playerCash")),
            "teamCash",
        ),
        "map": {
            "width": _normalize_finite_number(map_payload.get("width"), "map.width"),
            "height": _normalize_finite_number(map_payload.get("height"), "map.height"),
        },
        "safePlacementAnchors": [],
        "playerTowerIds": [],
        "playerTowerCount": _normalize_non_negative_integer(value.get("playerTowerCount"), "playerTowerCount"),
        "towers": [],
        "enemyCount": _normalize_non_negative_integer(value.get("enemyCount"), "enemyCount"),
        "commandResultsTail": [],
    }
    player_tower_ids = value.get("playerTowerIds")
    if not isinstance(player_tower_ids, list):
        raise ValueError("playerTowerIds must be a list")
    for tower_id in player_tower_ids:
        normalized_id = _to_tower_id(tower_id)
        if normalized_id is None:
            raise ValueError("playerTowerIds entries must be integers >= 1")
        normalized["playerTowerIds"].append(normalized_id)
    if len(normalized["playerTowerIds"]) != normalized["playerTowerCount"]:
        raise ValueError("playerTowerCount must equal len(playerTowerIds)")
    for anchor in safe_anchors:
        if not _is_plain_object(anchor):
            raise ValueError("safePlacementAnchors entries must be objects")
        normalized["safePlacementAnchors"].append(
            {
                "x": _normalize_finite_number(anchor.get("x"), "safePlacementAnchors[].x"),
                "y": _normalize_finite_number(anchor.get("y"), "safePlacementAnchors[].y"),
            }
        )
    for tower in towers:
        if not _is_plain_object(tower):
            raise ValueError("towers entries must be objects")
        tower_id = _to_tower_id(tower.get("id"))
        if tower_id is None:
            raise ValueError("towers[].id must be an integer >= 1")
        tower_type = _normalize_non_empty_string(tower.get("type"), "towers[].type")
        upgrades = tower.get("upgrades")
        if not _is_plain_object(upgrades):
            raise ValueError("towers[].upgrades must be an object")
        normalized["towers"].append(
            {
                "id": tower_id,
                "type": tower_type,
                "x": _normalize_finite_number(tower.get("x"), "towers[].x"),
                "y": _normalize_finite_number(tower.get("y"), "towers[].y"),
                "invested": _normalize_non_negative_number(tower.get("invested"), "towers[].invested"),
                "upgrades": copy.deepcopy(upgrades),
            }
        )
    for entry in command_results_tail:
        if not _is_plain_object(entry):
            raise ValueError("commandResultsTail entries must be objects")
        result_id = _to_tower_id(entry.get("id"))
        if result_id is None:
            raise ValueError("commandResultsTail[].id must be an integer >= 1")
        normalized["commandResultsTail"].append(
            {
                "id": result_id,
                "type": _normalize_non_empty_string(entry.get("type"), "commandResultsTail[].type").lower(),
                "playerId": _normalize_non_empty_string(entry.get("playerId"), "commandResultsTail[].playerId"),
                "success": bool(entry.get("success")),
                "reason": str(entry.get("reason", "")).strip(),
            }
        )
    return normalized


def normalize_command_decision(
    value: Any,
    allowed_commands: Iterable[str],
) -> Dict[str, Any]:
    if not _is_plain_object(value):
        raise ValueError("decision must be a plain object")
    kind = _normalize_non_empty_string(value.get("kind"), "kind").lower()
    allowed = {str(entry).strip().lower() for entry in allowed_commands}
    if kind == NOOP_KIND:
        _ensure_only_keys(value, {"kind", "reason", "payload"}, "noop decision")
        command_type = value.get("commandType")
        if command_type not in (None, ""):
            raise ValueError("noop commandType must be omitted")
        payload = value.get("payload")
        if payload not in (None, {}) and not (_is_plain_object(payload) and not payload):
            raise ValueError("noop payload must be omitted, null, or empty")
        reason = _normalize_non_empty_string(value.get("reason"), "reason")
        return {"kind": NOOP_KIND, "reason": reason}
    if kind != DECISION_KIND:
        raise ValueError(f"Unsupported decision kind: {kind}")
    _ensure_only_keys(value, {"kind", "commandType", "payload"}, "command decision")
    command_type = _normalize_non_empty_string(value.get("commandType"), "commandType").lower()
    if command_type not in COMMAND_TYPES:
        raise ValueError(f"Unsupported commandType: {command_type}")
    if command_type not in allowed:
        raise ValueError(f"Command is not allowed: {command_type}")
    payload = value.get("payload")
    if payload is None:
        payload = {}
    if not _is_plain_object(payload):
        raise ValueError("payload must be an object")
    normalized_payload: Dict[str, Any]
    if command_type == "place_tower":
        _ensure_only_keys(payload, {"type", "x", "y"}, "place_tower payload")
        tower_type = _normalize_non_empty_string(payload.get("type"), "payload.type").lower()
        if tower_type not in PLACE_TOWER_TYPES:
            raise ValueError(f"Unsupported tower type: {tower_type}")
        normalized_payload = {
            "type": tower_type,
            "x": _normalize_finite_number(payload.get("x"), "payload.x"),
            "y": _normalize_finite_number(payload.get("y"), "payload.y"),
        }
    elif command_type == "upgrade_tower":
        _ensure_only_keys(payload, {"towerId", "path"}, "upgrade_tower payload")
        tower_id = _to_tower_id(payload.get("towerId"))
        if tower_id is None:
            raise ValueError("payload.towerId must be an integer >= 1")
        path = _normalize_non_empty_string(payload.get("path"), "payload.path").lower()
        if path not in UPGRADE_PATHS:
            raise ValueError(f"Unsupported upgrade path: {path}")
        normalized_payload = {
            "towerId": tower_id,
            "path": path,
        }
    elif command_type == "sell_tower":
        _ensure_only_keys(payload, {"towerId"}, "sell_tower payload")
        tower_id = _to_tower_id(payload.get("towerId"))
        if tower_id is None:
            raise ValueError("payload.towerId must be an integer >= 1")
        normalized_payload = {
            "towerId": tower_id,
        }
    else:
        _ensure_only_keys(payload, set(), "trigger_next_round payload")
        if payload:
            raise ValueError("trigger_next_round payload must be empty")
        normalized_payload = {}
    return {
        "kind": DECISION_KIND,
        "commandType": command_type,
        "payload": normalized_payload,
    }


def _normalize_example(raw_example: Dict[str, Any]) -> Dict[str, Any]:
    if not _is_plain_object(raw_example):
        raise ValueError("dataset example must be an object")
    if "summary" in raw_example:
        summary = validate_command_summary(raw_example["summary"])
    elif "bridge_input" in raw_example:
        bridge_input = validate_bridge_input(raw_example["bridge_input"])
        known_tower_owners = raw_example.get("known_tower_owners")
        if known_tower_owners is not None and not _is_plain_object(known_tower_owners):
            raise ValueError("known_tower_owners must be an object when provided")
        owners: Dict[int, str] = {}
        for raw_tower_id, player_id in (known_tower_owners or {}).items():
            tower_id = _to_tower_id(raw_tower_id)
            normalized_player_id = str(player_id).strip()
            if tower_id is not None and normalized_player_id:
                owners[tower_id] = normalized_player_id
        summary = _create_command_summary_from_validated_bridge_input(bridge_input, owners)
    else:
        raise ValueError("dataset example must provide either summary or bridge_input")
    target_value = raw_example.get("target", raw_example.get("answer"))
    target = normalize_command_decision(target_value, summary["allowedCommands"])
    metadata = raw_example.get("metadata")
    return {
        "summary": summary,
        "target": target,
        "metadata": copy.deepcopy(metadata) if _is_plain_object(metadata) else {},
    }


def _read_examples_from_path(path: Path) -> List[Dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [
            json.loads(line)
            for line in raw.splitlines()
            if line.strip()
        ]
    parsed = json.loads(raw)
    if isinstance(parsed, list):
        return parsed
    if _is_plain_object(parsed) and isinstance(parsed.get("examples"), list):
        return parsed["examples"]
    raise ValueError(f"Unsupported dataset payload in {path}")


def _resolve_examples_source_path(raw_path: str) -> Path:
    expanded = Path(raw_path).expanduser()
    if expanded.is_absolute():
        return expanded
    cwd_candidate = Path.cwd() / expanded
    if cwd_candidate.exists():
        return cwd_candidate
    module_candidate = MODULE_DIR / expanded
    if module_candidate.exists():
        return module_candidate
    return cwd_candidate


def _resolve_examples(dataset_cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    examples: List[Dict[str, Any]] = []
    inline_examples = dataset_cfg.get("examples_inline")
    if isinstance(inline_examples, list):
        examples.extend(copy.deepcopy(inline_examples))
    paths: List[Path] = []
    single_path = dataset_cfg.get("examples_path")
    if isinstance(single_path, str) and single_path.strip():
        paths.append(_resolve_examples_source_path(single_path))
    multiple_paths = dataset_cfg.get("examples_paths")
    if isinstance(multiple_paths, list):
        for raw_path in multiple_paths:
            if isinstance(raw_path, str) and raw_path.strip():
                paths.append(_resolve_examples_source_path(raw_path))
    for path in paths:
        examples.extend(_read_examples_from_path(path))
    if not examples:
        raise ValueError("actual_game_command dataset requires at least one example")
    return [_normalize_example(example) for example in examples]


def build_actual_game_command_messages(summary: Dict[str, Any]) -> List[Dict[str, str]]:
    validated_summary = validate_command_summary(summary)
    return [
        {"role": "system", "content": ACTUAL_GAME_COMMAND_SYSTEM_PROMPT},
        {"role": "user", "content": f"State:\n{json.dumps(validated_summary, sort_keys=True)}"},
    ]


def _build_actual_game_command_dataset(
    config: Dict[str, Any],
    num_examples: int,
    seed_start: int,
) -> Dataset:
    _require_training_runtime()
    dataset_cfg = config.get("dataset", {}) if isinstance(config.get("dataset"), dict) else {}
    examples = _resolve_examples(dataset_cfg)
    prompts: List[List[Dict[str, str]]] = []
    answers: List[str] = []
    infos: List[Dict[str, Any]] = []
    total_examples = len(examples)
    requested_examples = total_examples if num_examples < 0 else max(0, num_examples)
    for offset in range(requested_examples):
        example = examples[(seed_start + offset) % total_examples]
        summary = example["summary"]
        target = example["target"]
        prompts.append(build_actual_game_command_messages(summary))
        answers.append(json.dumps(target, sort_keys=True))
        infos.append(
            {
                "summary": copy.deepcopy(summary),
                "target": copy.deepcopy(target),
                "metadata": copy.deepcopy(example.get("metadata", {})),
            }
        )
    return Dataset.from_dict(
        {
            "prompt": prompts,
            "answer": answers,
            "info": infos,
            "task": ["train"] * len(prompts),
        }
    )


def _actual_game_command_format_reward(
    prompt: vf.Messages,
    completion: vf.Messages,
    answer: str,
    state: vf.State,
    task: str = "default",
    info: vf.Info | None = None,
    **_kwargs: Any,
) -> float:
    content = _completion_to_text(completion)
    decision, strict = _extract_json_object(content)
    if decision is None or not strict:
        return FORMAT_INVALID_REWARD
    info = info or {}
    summary = validate_command_summary(info.get("summary", {}))
    try:
        normalize_command_decision(decision, summary["allowedCommands"])
    except ValueError:
        return FORMAT_INVALID_REWARD
    return 1.0 if strict else 0.0


def _actual_game_command_env_reward(
    prompt: vf.Messages,
    completion: vf.Messages,
    answer: str,
    state: vf.State,
    task: str = "default",
    info: vf.Info | None = None,
    **_kwargs: Any,
) -> float:
    content = _completion_to_text(completion)
    decision, strict = _extract_json_object(content)
    if decision is None or not strict:
        return FORMAT_INVALID_REWARD
    info = info or {}
    summary = validate_command_summary(info.get("summary", {}))
    target = normalize_command_decision(info.get("target", {}), summary["allowedCommands"])
    try:
        normalized_decision = normalize_command_decision(decision, summary["allowedCommands"])
    except ValueError:
        return FORMAT_INVALID_REWARD
    if normalized_decision["kind"] == NOOP_KIND and target["kind"] == NOOP_KIND:
        return 1.0
    return 1.0 if _sorted_object(normalized_decision) == _sorted_object(target) else 0.0


class TowerDefenseActualGameCommandEnv(_SINGLE_TURN_ENV_BASE):
    """Offline single-decision replay environment on the actual command surface."""

    def __init__(
        self,
        config: Dict[str, Any],
        num_examples: int = 64,
        seed_start: int = 0,
        **kwargs: Any,
    ) -> None:
        dataset = _build_actual_game_command_dataset(config, num_examples, seed_start)
        weight_cfg = config.get("reward_weights", {}) if isinstance(config.get("reward_weights"), dict) else {}
        format_weight = float(weight_cfg.get("format", 0.5))
        env_weight = float(weight_cfg.get("env", 1.0))
        rubric = vf.Rubric(
            funcs=[_actual_game_command_format_reward, _actual_game_command_env_reward],
            weights=[format_weight, env_weight],
        )
        super().__init__(dataset=dataset, rubric=rubric, **kwargs)


def load_environment(
    config: Dict[str, Any] | None = None,
    num_examples: int = 64,
    seed_start: int = 0,
    **kwargs: Any,
) -> vf.Environment:
    _require_training_runtime()
    resolved = copy.deepcopy(DEFAULT_ACTUAL_GAME_COMMAND_CONFIG)
    if isinstance(config, dict):
        resolved.update(copy.deepcopy(config))
        if isinstance(DEFAULT_ACTUAL_GAME_COMMAND_CONFIG.get("dataset"), dict):
            dataset_cfg = copy.deepcopy(DEFAULT_ACTUAL_GAME_COMMAND_CONFIG["dataset"])
            if isinstance(config.get("dataset"), dict):
                dataset_cfg.update(copy.deepcopy(config["dataset"]))
            resolved["dataset"] = dataset_cfg
        if isinstance(DEFAULT_ACTUAL_GAME_COMMAND_CONFIG.get("reward_weights"), dict):
            reward_weights = copy.deepcopy(DEFAULT_ACTUAL_GAME_COMMAND_CONFIG["reward_weights"])
            if isinstance(config.get("reward_weights"), dict):
                reward_weights.update(copy.deepcopy(config["reward_weights"]))
            resolved["reward_weights"] = reward_weights
    return TowerDefenseActualGameCommandEnv(resolved, num_examples=num_examples, seed_start=seed_start, **kwargs)


__all__ = [
    "ACTUAL_GAME_COMMAND_SYSTEM_PROMPT",
    "BRIDGE_INPUT_VERSION",
    "COMMAND_SUMMARY_SCHEMA_VERSION",
    "DEFAULT_ACTUAL_GAME_COMMAND_CONFIG",
    "SAFE_PLACEMENT_ANCHORS",
    "TowerDefenseActualGameCommandEnv",
    "build_actual_game_command_messages",
    "create_command_summary_from_bridge_input",
    "load_environment",
    "normalize_command_decision",
    "validate_bridge_input",
    "validate_command_summary",
]
