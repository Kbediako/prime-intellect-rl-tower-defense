import importlib.util
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "score_actual_game_bridge_run.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("score_actual_game_bridge_run", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BRIDGE_SCORE = _load_module()


class ScoreActualGameBridgeRunTest(unittest.TestCase):
    def _make_row(
        self,
        *,
        request_id: str,
        command_type: str,
        payload: dict,
        state_version: int = 7,
        result: dict | None = None,
        enqueue_success: bool = True,
    ) -> dict:
        command_result = []
        if result is not None:
            command_result = [
                {
                    "id": 1,
                    "command": {
                        "type": command_type,
                        "playerId": "bot-bridge",
                        "payload": payload,
                        "provenance": {
                            "requestId": request_id,
                            "stateVersion": state_version,
                        },
                    },
                    "result": result,
                }
            ]
        return {
            "input": {
                "playerId": "bot-bridge",
                "stateVersion": state_version,
            },
            "decision": {
                "kind": "command",
                "commandType": command_type,
                "payload": payload,
                "provenance": {
                    "requestId": request_id,
                },
            },
            "enqueueResult": {
                "success": enqueue_success,
            },
            "poll": {
                "commandResults": command_result,
            },
        }

    def test_match_command_result_prefers_request_id(self) -> None:
        row = self._make_row(
            request_id="req-1",
            command_type="place_tower",
            payload={"type": "dart", "x": 336, "y": 152},
            result={"success": True, "towerId": 3},
        )
        matched = BRIDGE_SCORE.match_command_result(row)
        self.assertIsNotNone(matched)
        self.assertEqual(matched["result"]["towerId"], 3)

    def test_analyze_rows_uses_realized_results_for_strict_coverage(self) -> None:
        rows = [
            self._make_row(
                request_id="place-ok",
                command_type="place_tower",
                payload={"type": "dart", "x": 336, "y": 152},
                result={"success": True, "towerId": 1},
            ),
            self._make_row(
                request_id="upgrade-fail",
                command_type="upgrade_tower",
                payload={"towerId": 1, "path": "top"},
                result={"success": False, "reasonCode": "INSUFFICIENT_PLAYER_CASH"},
            ),
            self._make_row(
                request_id="trigger-unmatched",
                command_type="trigger_next_round",
                payload={},
                result=None,
            ),
        ]

        report = BRIDGE_SCORE.analyze_rows(rows)

        self.assertEqual(report["strict_success_counts"], {"place_tower": 1})
        self.assertEqual(report["failed_command_counts"], {"upgrade_tower": 1})
        self.assertEqual(report["unmatched_command_counts"], {"trigger_next_round": 1})
        self.assertEqual(
            report["failure_reason_counts"],
            {"upgrade_tower:INSUFFICIENT_PLAYER_CASH": 1},
        )
        self.assertTrue(report["optimistic_enqueued_coverage"]["by_type"]["trigger_next_round"])
        self.assertFalse(report["strict_success_coverage"]["by_type"]["trigger_next_round"])
        self.assertEqual(report["strict_status"], "fail")


if __name__ == "__main__":
    unittest.main()
