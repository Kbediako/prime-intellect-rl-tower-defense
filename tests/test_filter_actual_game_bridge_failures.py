import json
import tempfile
import unittest
from pathlib import Path

import filter_actual_game_bridge_failures as BRIDGE_FAILURE_FILTER


def _make_row(*, request_id: str, command_type: str, payload: dict, success: bool, reason: str | None = None) -> dict:
    result = {"success": success}
    if reason is not None:
        result["reasonCode"] = reason
    return {
        "input": {
            "playerId": "bot-bridge",
            "stateVersion": 7,
        },
        "decision": {
            "kind": "command",
            "commandType": command_type,
            "payload": payload,
            "provenance": {"requestId": request_id},
        },
        "poll": {
            "commandResults": [
                {
                    "command": {
                        "playerId": "bot-bridge",
                        "type": command_type,
                        "payload": payload,
                        "provenance": {"requestId": request_id, "stateVersion": 7},
                    },
                    "result": result,
                }
            ]
        },
    }


class FilterActualGameBridgeFailuresTests(unittest.TestCase):
    def test_filters_exact_failed_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "bridge-decisions.json"
            rows = [
                _make_row(
                    request_id="req-failed-place",
                    command_type="place_tower",
                    payload={"type": "dart", "x": 10, "y": 10},
                    success=False,
                    reason="INSUFFICIENT_PLAYER_CASH",
                ),
                _make_row(
                    request_id="req-success-place",
                    command_type="place_tower",
                    payload={"type": "dart", "x": 20, "y": 20},
                    success=True,
                ),
                _make_row(
                    request_id="req-failed-upgrade",
                    command_type="upgrade_tower",
                    payload={"towerId": 1, "path": "top"},
                    success=False,
                    reason="INSUFFICIENT_PLAYER_CASH",
                ),
            ]
            source_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

            filtered = BRIDGE_FAILURE_FILTER.filter_rows(source_paths=[source_path])

            self.assertEqual(len(filtered["rows"]), 2)
            self.assertEqual(
                filtered["report"]["command_type_counts"],
                {"place_tower": 1, "upgrade_tower": 1},
            )
            self.assertEqual(
                filtered["report"]["reason_counts"],
                {
                    "place_tower:INSUFFICIENT_PLAYER_CASH": 1,
                    "upgrade_tower:INSUFFICIENT_PLAYER_CASH": 1,
                },
            )

    def test_filters_by_failure_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "bridge-decisions.json"
            rows = [
                _make_row(
                    request_id="req-failed-place",
                    command_type="place_tower",
                    payload={"type": "dart", "x": 10, "y": 10},
                    success=False,
                    reason="INSUFFICIENT_PLAYER_CASH",
                ),
                _make_row(
                    request_id="req-failed-upgrade",
                    command_type="upgrade_tower",
                    payload={"towerId": 1, "path": "top"},
                    success=False,
                    reason="INSUFFICIENT_PLAYER_CASH",
                ),
            ]
            source_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

            filtered = BRIDGE_FAILURE_FILTER.filter_rows(
                source_paths=[source_path],
                failure_reasons=["place_tower:INSUFFICIENT_PLAYER_CASH"],
            )

            self.assertEqual(len(filtered["rows"]), 1)
            self.assertEqual(filtered["report"]["command_type_counts"], {"place_tower": 1})


if __name__ == "__main__":
    unittest.main()
