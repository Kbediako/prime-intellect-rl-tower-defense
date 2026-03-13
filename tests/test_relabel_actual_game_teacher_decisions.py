import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "relabel_actual_game_teacher_decisions.mjs"
NODE_BIN = shutil.which("node")


def _bridge_row(
    *,
    tick: int,
    state_version: int,
    cash: int,
    status: str,
    towers: list[dict],
    last_command_results: list[dict],
    historical_decision: dict,
) -> dict:
    return {
        "index": state_version - 1,
        "input": {
            "version": "td.multiplayer.llm-bridge.input.v1",
            "tick": tick,
            "stateVersion": state_version,
            "stateDigest": f"digest-{state_version}",
            "economy": {
                "players": {
                    "bot-bridge": {"cash": cash},
                    "owner": {"cash": 325},
                }
            },
            "lobby": {
                "lobbyId": "fixture-lobby",
                "ownerId": "owner",
                "players": ["bot-bridge", "owner"],
                "playerMeta": {},
            },
            "playerId": "bot-bridge",
            "allowedCommands": [
                "place_tower",
                "upgrade_tower",
                "sell_tower",
                "trigger_next_round",
            ],
            "lastCommandResults": last_command_results,
            "deadlineAt": 1738800000000 + tick,
            "budgetMs": 1200,
            "state": {
                "round": 1,
                "status": status,
                "lives": 100,
                "width": 960,
                "height": 540,
                "towers": towers,
                "enemies": [],
            },
        },
        "decision": historical_decision,
        "enqueueResult": {"accepted": True},
        "stepResult": {"success": True},
        "poll": {"commandResults": []},
    }


@unittest.skipUnless(NODE_BIN, "node is required for relabel exporter tests")
class RelabelActualGameTeacherDecisionsTest(unittest.TestCase):
    def _write_source_rows(self, root: Path) -> Path:
        rows = [
            _bridge_row(
                tick=15,
                state_version=1,
                cash=325,
                status="spawning",
                towers=[],
                last_command_results=[],
                historical_decision={"kind": "noop", "reason": "waiting_for_resources"},
            ),
            _bridge_row(
                tick=30,
                state_version=2,
                cash=225,
                status="spawning",
                towers=[{"id": 1, "x": 120, "y": 220, "type": "dart"}],
                last_command_results=[
                    {
                        "command": {
                            "type": "place_tower",
                            "playerId": "bot-bridge",
                            "payload": {"type": "dart", "x": 120, "y": 220},
                        },
                        "result": {"success": True, "towerId": 1},
                    }
                ],
                historical_decision={
                    "kind": "command",
                    "commandType": "place_tower",
                    "payload": {"type": "dart", "x": 120, "y": 220},
                },
            ),
        ]
        source_path = root / "fixture_source" / "bridge-decisions.json"
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        return source_path

    def _run_exporter(
        self,
        *,
        source_path: Path,
        out_dir: Path,
        teacher_mode: str,
        include_noop: bool = False,
    ) -> tuple[Path, dict]:
        report_path = out_dir / "relabel_report.json"
        command = [
            NODE_BIN,
            str(SCRIPT_PATH),
            "--source",
            str(source_path),
            "--out-dir",
            str(out_dir),
            "--report",
            str(report_path),
            "--teacher-mode",
            teacher_mode,
        ]
        if include_noop:
            command.append("--include-noop")
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(completed.stdout)
        output_files = sorted(path for path in out_dir.glob("*.json") if path.name != report_path.name)
        self.assertEqual(len(output_files), 1)
        return output_files[0], report

    def test_hybrid_opening_exports_opening_place_then_upgrade(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = self._write_source_rows(root)
            output_path, report = self._run_exporter(
                source_path=source_path,
                out_dir=root / "hybrid_out",
                teacher_mode="hybrid-opening",
            )
            exported_rows = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(report["hybrid_opening_override_count"], 1)
        self.assertEqual(report["output_row_count"], 2)
        self.assertEqual(
            [row["decision"]["commandType"] for row in exported_rows],
            ["place_tower", "upgrade_tower"],
        )
        self.assertEqual(exported_rows[0]["decision"]["payload"], {"type": "dart", "x": 120, "y": 220})
        self.assertEqual(exported_rows[1]["decision"]["payload"], {"towerId": 1, "path": "top"})
        self.assertNotIn("poll", exported_rows[0])
        self.assertNotIn("enqueueResult", exported_rows[0])
        self.assertNotIn("stepResult", exported_rows[0])
        self.assertEqual(exported_rows[0]["metadata"]["historical_decision_kind"], "noop")
        self.assertEqual(exported_rows[0]["metadata"]["teacher_mode"], "hybrid-opening")

    def test_codex_safe_mode_drops_opening_noop_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = self._write_source_rows(root)
            output_path, report = self._run_exporter(
                source_path=source_path,
                out_dir=root / "codex_safe_out",
                teacher_mode="codex-safe",
            )
            exported_rows = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(report["hybrid_opening_override_count"], 0)
        self.assertEqual(report["noop_count"], 1)
        self.assertEqual(report["output_row_count"], 1)
        self.assertEqual(exported_rows[0]["decision"]["commandType"], "upgrade_tower")

    def test_hybrid_opening_still_overrides_when_other_player_already_acted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "fixture_source" / "bridge-decisions.json"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            rows = [
                _bridge_row(
                    tick=15,
                    state_version=1,
                    cash=325,
                    status="spawning",
                    towers=[{"id": 9, "x": 400, "y": 200, "type": "dart"}],
                    last_command_results=[
                        {
                            "command": {
                                "type": "place_tower",
                                "playerId": "owner",
                                "payload": {"type": "dart", "x": 400, "y": 200},
                            },
                            "result": {"success": True, "towerId": 9},
                        }
                    ],
                    historical_decision={"kind": "noop", "reason": "waiting_for_resources"},
                )
            ]
            source_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

            output_path, report = self._run_exporter(
                source_path=source_path,
                out_dir=root / "hybrid_owner_present",
                teacher_mode="hybrid-opening",
            )
            exported_rows = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(report["hybrid_opening_override_count"], 1)
        self.assertEqual(report["output_row_count"], 1)
        self.assertEqual(exported_rows[0]["decision"]["commandType"], "place_tower")

    def test_relabel_respects_row_allowed_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = self._write_source_rows(root)
            rows = json.loads(source_path.read_text(encoding="utf-8"))
            rows[1]["input"]["allowedCommands"] = ["place_tower"]
            source_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

            output_path, report = self._run_exporter(
                source_path=source_path,
                out_dir=root / "allowed_commands_out",
                teacher_mode="codex-safe",
            )
            exported_rows = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(report["noop_count"], 2)
        self.assertEqual(report["output_row_count"], 0)
        self.assertEqual(exported_rows, [])

    def test_invalid_placement_repair_snaps_to_nearest_unoccupied_safe_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "fixture_source" / "bridge-decisions.json"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            row = _bridge_row(
                tick=420,
                state_version=28,
                cash=142,
                status="active",
                towers=[
                    {
                        "id": 1,
                        "position": {"x": 760, "y": 500},
                        "type": "dart",
                    }
                ],
                last_command_results=[],
                historical_decision={
                    "kind": "command",
                    "commandType": "place_tower",
                    "payload": {"type": "dart", "x": 760, "y": 500},
                    "provenance": {"requestId": "pi-req-invalid-1"},
                },
            )
            row["poll"] = {
                "commandResults": [
                    {
                        "command": {
                            "type": "place_tower",
                            "playerId": "bot-bridge",
                            "payload": {"type": "dart", "x": 760, "y": 500},
                            "provenance": {"requestId": "pi-req-invalid-1", "stateVersion": 28},
                        },
                        "result": {"success": False, "reason": "Invalid placement"},
                    }
                ]
            }
            source_path.write_text(json.dumps([row], indent=2) + "\n", encoding="utf-8")

            for teacher_mode in ("codex-safe", "hybrid-opening", "deterministic"):
                output_path, report = self._run_exporter(
                    source_path=source_path,
                    out_dir=root / teacher_mode,
                    teacher_mode=teacher_mode,
                )
                exported_rows = json.loads(output_path.read_text(encoding="utf-8"))
                self.assertEqual(report["output_row_count"], 1)
                self.assertEqual(exported_rows[0]["decision"]["commandType"], "place_tower")
                self.assertEqual(
                    exported_rows[0]["decision"]["payload"],
                    {"type": "dart", "x": 630, "y": 499},
                )
                self.assertEqual(
                    exported_rows[0]["metadata"]["historical_failure_reason"],
                    "Invalid placement",
                )

    def test_invalid_placement_repair_uses_historical_failed_payload_before_teacher_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "fixture_source" / "bridge-decisions.json"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            row = _bridge_row(
                tick=5,
                state_version=1,
                cash=325,
                status="intermission",
                towers=[],
                last_command_results=[],
                historical_decision={
                    "kind": "command",
                    "commandType": "place_tower",
                    "payload": {"type": "dart", "x": 760, "y": 500},
                    "provenance": {"requestId": "pi-req-invalid-historical"},
                },
            )
            row["input"]["state"]["round"] = 0
            row["poll"] = {
                "commandResults": [
                    {
                        "command": {
                            "type": "place_tower",
                            "playerId": "bot-bridge",
                            "payload": {"type": "dart", "x": 760, "y": 500},
                            "provenance": {"requestId": "pi-req-invalid-historical", "stateVersion": 1},
                        },
                        "result": {"success": False, "reason": "Invalid placement"},
                    }
                ]
            }
            source_path.write_text(json.dumps([row], indent=2) + "\n", encoding="utf-8")

            output_path, report = self._run_exporter(
                source_path=source_path,
                out_dir=root / "codex_safe_repair",
                teacher_mode="codex-safe",
            )
            exported_rows = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(report["output_row_count"], 1)
        self.assertEqual(exported_rows[0]["decision"]["commandType"], "place_tower")
        self.assertEqual(
            exported_rows[0]["decision"]["payload"],
            {"type": "dart", "x": 630, "y": 499},
        )
        self.assertEqual(
            exported_rows[0]["metadata"]["historical_failure_reason"],
            "Invalid placement",
        )

    def test_invalid_placement_repair_preserves_historical_tower_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "fixture_source" / "bridge-decisions.json"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            row = _bridge_row(
                tick=420,
                state_version=28,
                cash=500,
                status="active",
                towers=[],
                last_command_results=[],
                historical_decision={
                    "kind": "command",
                    "commandType": "place_tower",
                    "payload": {"type": "sniper", "x": 760, "y": 500},
                    "provenance": {"requestId": "pi-req-invalid-sniper"},
                },
            )
            row["poll"] = {
                "commandResults": [
                    {
                        "command": {
                            "type": "place_tower",
                            "playerId": "bot-bridge",
                            "payload": {"type": "sniper", "x": 760, "y": 500},
                            "provenance": {"requestId": "pi-req-invalid-sniper", "stateVersion": 28},
                        },
                        "result": {"success": False, "reason": "Invalid placement"},
                    }
                ]
            }
            source_path.write_text(json.dumps([row], indent=2) + "\n", encoding="utf-8")

            output_path, _report = self._run_exporter(
                source_path=source_path,
                out_dir=root / "invalid_sniper_repair",
                teacher_mode="deterministic",
            )
            exported_rows = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(exported_rows[0]["decision"]["commandType"], "place_tower")
        self.assertEqual(
            exported_rows[0]["decision"]["payload"],
            {"type": "sniper", "x": 630, "y": 499},
        )

    def test_active_insufficient_cash_failure_repairs_to_noop_when_including_noops(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "fixture_source" / "bridge-decisions.json"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            filler_row = _bridge_row(
                tick=405,
                state_version=27,
                cash=325,
                status="active",
                towers=[],
                last_command_results=[],
                historical_decision={"kind": "noop", "reason": "filler"},
            )
            filler_row["input"]["allowedCommands"] = ["upgrade_tower"]
            target_row = _bridge_row(
                tick=420,
                state_version=28,
                cash=325,
                status="active",
                towers=[
                    {
                        "id": 1,
                        "position": {"x": 120, "y": 220},
                        "type": "dart",
                    }
                ],
                last_command_results=[
                    {
                        "command": {
                            "type": "place_tower",
                            "playerId": "bot-bridge",
                            "payload": {"type": "dart", "x": 120, "y": 220},
                        },
                        "result": {"success": True, "towerId": 1},
                    }
                ],
                historical_decision={
                    "kind": "command",
                    "commandType": "upgrade_tower",
                    "payload": {"towerId": 1, "path": "top"},
                    "provenance": {"requestId": "pi-req-cash-1"},
                },
            )
            target_row["poll"] = {
                "commandResults": [
                    {
                        "command": {
                            "type": "upgrade_tower",
                            "playerId": "bot-bridge",
                            "payload": {"towerId": 1, "path": "top"},
                            "provenance": {"requestId": "pi-req-cash-1", "stateVersion": 28},
                        },
                        "result": {
                            "success": False,
                            "reasonCode": "INSUFFICIENT_PLAYER_CASH",
                            "reason": "Player bot-bridge has insufficient cash for upgrade top",
                        },
                    }
                ]
            }
            source_path.write_text(json.dumps([filler_row, target_row], indent=2) + "\n", encoding="utf-8")

            output_path, report = self._run_exporter(
                source_path=source_path,
                out_dir=root / "cash_repair",
                teacher_mode="deterministic",
                include_noop=True,
            )
            exported_rows = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(report["output_row_count"], 2)
        self.assertEqual(report["noop_count"], 2)
        self.assertEqual(exported_rows[1]["decision"]["kind"], "noop")
        self.assertEqual(exported_rows[1]["decision"]["reason"], "waiting_for_resources")
        self.assertEqual(
            exported_rows[1]["decision"]["provenance"]["repair"],
            "insufficient_cash_wait",
        )
        self.assertEqual(
            exported_rows[1]["metadata"]["historical_failure_reason"],
            "INSUFFICIENT_PLAYER_CASH",
        )

    def test_insufficient_cash_repair_requires_matching_teacher_command_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "fixture_source" / "bridge-decisions.json"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            row = _bridge_row(
                tick=420,
                state_version=28,
                cash=325,
                status="active",
                towers=[
                    {
                        "id": 1,
                        "position": {"x": 120, "y": 220},
                        "type": "dart",
                    }
                ],
                last_command_results=[],
                historical_decision={
                    "kind": "command",
                    "commandType": "upgrade_tower",
                    "payload": {"towerId": 1, "path": "top"},
                    "provenance": {"requestId": "pi-req-cash-mismatch"},
                },
            )
            row["poll"] = {
                "commandResults": [
                    {
                        "command": {
                            "type": "upgrade_tower",
                            "playerId": "bot-bridge",
                            "payload": {"towerId": 1, "path": "top"},
                            "provenance": {"requestId": "pi-req-cash-mismatch", "stateVersion": 28},
                        },
                        "result": {
                            "success": False,
                            "reasonCode": "INSUFFICIENT_PLAYER_CASH",
                            "reason": "Player bot-bridge has insufficient cash for upgrade top",
                        },
                    }
                ]
            }
            source_path.write_text(json.dumps([row], indent=2) + "\n", encoding="utf-8")

            output_path, report = self._run_exporter(
                source_path=source_path,
                out_dir=root / "cash_mismatch",
                teacher_mode="deterministic",
                include_noop=True,
            )
            exported_rows = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(report["noop_count"], 0)
        self.assertEqual(exported_rows[0]["decision"]["kind"], "command")
        self.assertEqual(exported_rows[0]["decision"]["commandType"], "place_tower")

    def test_structural_payload_match_without_request_id_still_repairs_insufficient_cash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "fixture_source" / "bridge-decisions.json"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            filler_row = _bridge_row(
                tick=405,
                state_version=27,
                cash=325,
                status="active",
                towers=[],
                last_command_results=[],
                historical_decision={"kind": "noop", "reason": "filler"},
            )
            filler_row["input"]["allowedCommands"] = ["upgrade_tower"]
            target_row = _bridge_row(
                tick=420,
                state_version=28,
                cash=325,
                status="active",
                towers=[
                    {
                        "id": 1,
                        "position": {"x": 120, "y": 220},
                        "type": "dart",
                    }
                ],
                last_command_results=[
                    {
                        "command": {
                            "type": "place_tower",
                            "playerId": "bot-bridge",
                            "payload": {"type": "dart", "x": 120, "y": 220},
                        },
                        "result": {"success": True, "towerId": 1},
                    }
                ],
                historical_decision={
                    "kind": "command",
                    "commandType": "upgrade_tower",
                    "payload": {"path": "top", "towerId": 1},
                    "provenance": {},
                },
            )
            target_row["poll"] = {
                "commandResults": [
                    {
                        "command": {
                            "type": "upgrade_tower",
                            "playerId": "bot-bridge",
                            "payload": {"towerId": 1, "path": "top"},
                            "provenance": {"stateVersion": 28},
                        },
                        "result": {
                            "success": False,
                            "reasonCode": "INSUFFICIENT_PLAYER_CASH",
                            "reason": "Player bot-bridge has insufficient cash for upgrade top",
                        },
                    }
                ]
            }
            source_path.write_text(json.dumps([filler_row, target_row], indent=2) + "\n", encoding="utf-8")

            output_path, report = self._run_exporter(
                source_path=source_path,
                out_dir=root / "cash_reordered_payload",
                teacher_mode="deterministic",
                include_noop=True,
            )
            exported_rows = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(report["output_row_count"], 2)
        self.assertEqual(exported_rows[1]["decision"]["kind"], "noop")
        self.assertEqual(exported_rows[1]["decision"]["reason"], "waiting_for_resources")
        self.assertEqual(
            exported_rows[1]["metadata"]["historical_failure_reason"],
            "INSUFFICIENT_PLAYER_CASH",
        )


if __name__ == "__main__":
    unittest.main()
