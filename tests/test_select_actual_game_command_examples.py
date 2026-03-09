import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "select_actual_game_command_examples.py"


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SELECT = _load_module("select_actual_game_command_examples", MODULE_PATH)


def _example(
    *,
    summary_sha256: str,
    tick: int,
    state_version: int,
    round_num: int,
    status: str,
    player_tower_count: int,
    command_type: str,
    source_paths: list[str],
) -> dict:
    if command_type == "noop":
        target = {"kind": "noop", "reason": "waiting_for_resources"}
    else:
        target = {
            "kind": "command",
            "commandType": command_type,
            "payload": {"towerId": 1, "path": "top"} if command_type == "upgrade_tower" else {"type": "dart", "x": 600.0, "y": 180.0},
        }
    return {
        "bridge_input": {"version": "td.multiplayer.llm-bridge.input.v1"},
        "summary": {
            "schemaVersion": "td.actual_game.command_summary.v1",
            "tick": tick,
            "stateVersion": state_version,
            "round": round_num,
            "status": status,
            "playerTowerCount": player_tower_count,
            "allowedCommands": ["place_tower", "upgrade_tower", "trigger_next_round"],
        },
        "target": target,
        "metadata": {
            "summary_sha256": summary_sha256,
            "target_sha256": f"target-{summary_sha256}",
            "source_instances": [
                {"source_index": index, "source_path": source_path}
                for index, source_path in enumerate(source_paths)
            ],
        },
    }


class SelectActualGameCommandExamplesTest(unittest.TestCase):
    def _write_examples(self, root: Path, name: str, examples: list[dict]) -> Path:
        path = root / f"{name}.json"
        path.write_text(
            json.dumps(
                {
                    "schemaVersion": "td.actual_game.command_examples.v1",
                    "examples": examples,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return path

    def _write_examples_jsonl(self, root: Path, name: str, examples: list[dict]) -> Path:
        path = root / f"{name}.jsonl"
        path.write_text(
            "\n".join(json.dumps(example, sort_keys=True) for example in examples) + "\n",
            encoding="utf-8",
        )
        return path

    def test_select_examples_filters_and_caps_by_source(self) -> None:
        examples = [
            _example(
                summary_sha256="keep-a-1",
                tick=15,
                state_version=1,
                round_num=1,
                status="spawning",
                player_tower_count=1,
                command_type="upgrade_tower",
                source_paths=["artifacts/x582/x557.teacher.json"],
            ),
            _example(
                summary_sha256="drop-status",
                tick=30,
                state_version=2,
                round_num=1,
                status="active",
                player_tower_count=1,
                command_type="upgrade_tower",
                source_paths=["artifacts/x582/x557.teacher.json"],
            ),
            _example(
                summary_sha256="keep-a-2",
                tick=45,
                state_version=3,
                round_num=1,
                status="spawning",
                player_tower_count=1,
                command_type="upgrade_tower",
                source_paths=["artifacts/x582/x557.teacher.json"],
            ),
            _example(
                summary_sha256="keep-b-1",
                tick=60,
                state_version=4,
                round_num=1,
                status="spawning",
                player_tower_count=1,
                command_type="upgrade_tower",
                source_paths=["artifacts/x582/x558.teacher.json"],
            ),
            _example(
                summary_sha256="drop-round",
                tick=75,
                state_version=5,
                round_num=2,
                status="spawning",
                player_tower_count=1,
                command_type="upgrade_tower",
                source_paths=["artifacts/x582/x558.teacher.json"],
            ),
            _example(
                summary_sha256="drop-command",
                tick=90,
                state_version=6,
                round_num=1,
                status="spawning",
                player_tower_count=1,
                command_type="place_tower",
                source_paths=["artifacts/x582/x558.teacher.json"],
            ),
        ]

        selected_examples, report = SELECT.select_examples(
            examples,
            include_command_types=["upgrade_tower"],
            include_statuses=["spawning"],
            include_rounds=[1],
            min_player_tower_count=1,
            include_source_contains=["x557.teacher", "x558.teacher"],
            limit_per_source=1,
            sampling_mode="evenly_spaced",
        )

        self.assertEqual(
            [example["metadata"]["summary_sha256"] for example in selected_examples],
            ["keep-a-1", "keep-b-1"],
        )
        self.assertEqual(
            report["selected_by_source"],
            {
                "artifacts/x582/x557.teacher.json": 1,
                "artifacts/x582/x558.teacher.json": 1,
            },
        )
        self.assertEqual(report["skip_reasons"]["status_excluded"], 1)
        self.assertEqual(report["skip_reasons"]["round_excluded"], 1)
        self.assertEqual(report["skip_reasons"]["command_type_excluded"], 1)

    def test_reject_source_contains_drops_mixed_provenance_rows(self) -> None:
        examples = [
            _example(
                summary_sha256="keep-clean",
                tick=15,
                state_version=1,
                round_num=1,
                status="spawning",
                player_tower_count=1,
                command_type="upgrade_tower",
                source_paths=["artifacts/x582/x557.teacher.json"],
            ),
            _example(
                summary_sha256="drop-mixed",
                tick=30,
                state_version=2,
                round_num=1,
                status="spawning",
                player_tower_count=1,
                command_type="upgrade_tower",
                source_paths=[
                    "artifacts/x582/x557.teacher.json",
                    "artifacts/x582/x567.teacher.json",
                ],
            ),
        ]

        selected_examples, report = SELECT.select_examples(
            examples,
            include_command_types=["upgrade_tower"],
            include_statuses=["spawning"],
            include_rounds=[1],
            min_player_tower_count=1,
            max_player_tower_count=1,
            include_source_contains=["x557.teacher"],
            reject_source_contains=["x567.teacher"],
        )

        self.assertEqual(
            [example["metadata"]["summary_sha256"] for example in selected_examples],
            ["keep-clean"],
        )
        self.assertEqual(report["skip_reasons"]["source_rejected"], 1)

    def test_include_summary_sha256_keeps_only_requested_rows(self) -> None:
        examples = [
            _example(
                summary_sha256="keep-me",
                tick=15,
                state_version=1,
                round_num=1,
                status="spawning",
                player_tower_count=1,
                command_type="trigger_next_round",
                source_paths=["artifacts/x673.teacher.json"],
            ),
            _example(
                summary_sha256="drop-me",
                tick=30,
                state_version=2,
                round_num=1,
                status="spawning",
                player_tower_count=1,
                command_type="trigger_next_round",
                source_paths=["artifacts/x674.teacher.json"],
            ),
        ]

        selected_examples, report = SELECT.select_examples(
            examples,
            include_summary_sha256=["keep-me"],
            include_command_types=["trigger_next_round"],
        )

        self.assertEqual(
            [example["metadata"]["summary_sha256"] for example in selected_examples],
            ["keep-me"],
        )
        self.assertEqual(report["skip_reasons"]["summary_sha256_excluded"], 1)
        self.assertEqual(report["filters"]["include_summary_sha256"], ["keep-me"])

    def test_read_examples_payload_accepts_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = self._write_examples_jsonl(
                root,
                "examples",
                [
                    _example(
                        summary_sha256="row-1",
                        tick=15,
                        state_version=1,
                        round_num=1,
                        status="active",
                        player_tower_count=1,
                        command_type="place_tower",
                        source_paths=["artifacts/x581.teacher.json"],
                    ),
                    _example(
                        summary_sha256="row-2",
                        tick=30,
                        state_version=2,
                        round_num=1,
                        status="active",
                        player_tower_count=1,
                        command_type="place_tower",
                        source_paths=["artifacts/x581.teacher.json"],
                    ),
                ],
            )

            schema_version, rows = SELECT._read_examples_payload(path)

        self.assertEqual(schema_version, "td.actual_game.command_examples.v1")
        self.assertEqual(len(rows), 2)

    def test_main_writes_selected_examples_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = self._write_examples(
                root,
                "examples",
                [
                    _example(
                        summary_sha256="keep-1",
                        tick=15,
                        state_version=1,
                        round_num=1,
                        status="active",
                        player_tower_count=1,
                        command_type="place_tower",
                        source_paths=["artifacts/x581.teacher.json"],
                    ),
                    _example(
                        summary_sha256="drop-1",
                        tick=30,
                        state_version=2,
                        round_num=1,
                        status="spawning",
                        player_tower_count=0,
                        command_type="noop",
                        source_paths=["artifacts/x581.teacher.json"],
                    ),
                ],
            )
            output_path = root / "selected.json"
            report_path = root / "report.json"

            exit_code = SELECT.main(
                [
                    "--examples",
                    str(input_path),
                    "--out",
                    str(output_path),
                    "--report",
                    str(report_path),
                    "--include-command-type",
                    "place_tower",
                    "--include-status",
                    "active",
                    "--min-player-tower-count",
                    "1",
                ]
            )

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(payload["examples"]), 1)
        self.assertEqual(payload["examples"][0]["metadata"]["summary_sha256"], "keep-1")
        self.assertEqual(report["selected_count"], 1)


if __name__ == "__main__":
    unittest.main()
