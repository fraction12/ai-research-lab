from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import paper_campaign_repeated_work_speed as speed  # noqa: E402


def packet_row(case_id: str, control_id: str, expected_answer: str = "ANSWER") -> dict[str, object]:
    return {
        "case_id": case_id,
        "control_id": control_id,
        "expected_answer": expected_answer,
        "expected_calls": [
            {
                "name": "GeometryPresentation.createPresentation",
                "arguments": {"controller": ["mapController"], "parent": ["mapArea"]},
            }
        ],
        "visible_prompt": f"Use visible tools for {case_id}. Expected shape only.",
    }


def full_packet(case_ids: list[str]) -> list[dict[str, object]]:
    return [packet_row(case_id, control_id, f"ANSWER-{case_id}") for case_id in case_ids for control_id in speed.CONTROL_ORDER]


class RepeatedWorkSpeedTests(unittest.TestCase):
    def test_select_cases_is_sorted_and_limited_for_both_arms(self) -> None:
        rows = full_packet(["bfcl:z:z_2", "bfcl:a:a_1", "bfcl:m:m_3"])

        selected = speed.select_cases(rows, 2)

        self.assertEqual(selected, ["bfcl:a:a_1", "bfcl:m:m_3"])
        direct_rows = speed.selected_rows(rows, selected, "direct_full_visible_tools")
        self.assertEqual([row["case_id"] for row in direct_rows], selected)

    def test_codex_prompt_uses_regular_visible_tools_not_code_mode(self) -> None:
        row = packet_row("bfcl:simple:simple_0", "direct_full_visible_tools", "ANSWER-0")

        prompt = speed.build_codex_prompt(row, task_index=0, task_count=2)

        self.assertIn("regular visible tool schemas", prompt)
        self.assertIn("Do not use hidden KV capsule state or Code Mode", prompt)
        self.assertIn("VISIBLE REGULAR TOOL TASK", prompt)
        self.assertIn("bfcl:simple:simple_0", prompt)

    def test_parse_codex_json_events_extracts_compaction_and_token_telemetry(self) -> None:
        stdout = "\n".join(
            [
                json.dumps({"type": "turn", "usage": {"input_tokens": 123, "output_tokens": 9}}),
                json.dumps({"type": "event", "message": "context_compacted after threshold"}),
                json.dumps({"type": "item.completed", "item": {"text": "ANSWER-bfcl"}}),
            ]
        )

        telemetry = speed.parse_codex_json_events(stdout)

        self.assertEqual(telemetry["event_count"], 3)
        self.assertEqual(telemetry["compaction_events_seen"], 1)
        self.assertEqual(telemetry["last_compaction_marker"], "context_compacted")
        self.assertEqual(telemetry["visible_input_tokens"], 123)
        self.assertEqual(telemetry["output_tokens"], 9)
        self.assertEqual(telemetry["last_message"], "ANSWER-bfcl")

    def test_score_codex_response_uses_bfcl_expected_calls(self) -> None:
        row = packet_row("bfcl:java:java_0", "direct_full_visible_tools")
        response = json.dumps(
            {
                "case_id": "bfcl:java:java_0",
                "tool_calls": [
                    {
                        "function_name": "GeometryPresentation.createPresentation",
                        "arguments": {"controller": "mapController", "parent": "mapArea"},
                    }
                ],
                "final_answer": "",
            }
        )

        scored = speed.score_codex_response(row, response)

        self.assertTrue(scored["passed"])
        self.assertEqual(scored["scorer"]["matched_count"], 1)

    def test_build_kv_runner_command_wraps_existing_model_loop_runner(self) -> None:
        args = argparse.Namespace(
            packet=Path("packet.jsonl"),
            out_dir=Path("out"),
            cache_dir=Path("cache"),
            kv_controls="code_mode_native_live_append,code_mode_restored_kv_capsule",
            model_profile="gemma4-12b",
            case_limit=2,
        )

        command = speed.build_kv_runner_command(args, run_label="smoke-kv")

        joined = " ".join(command)
        self.assertIn("code_mode_kv_capsule_model_loop_runner.py", joined)
        self.assertIn("--controls code_mode_native_live_append,code_mode_restored_kv_capsule", joined)
        self.assertIn("--case-limit 2", joined)

    def test_build_kv_runner_command_omits_case_limit_for_full_run(self) -> None:
        args = argparse.Namespace(
            packet=Path("packet.jsonl"),
            out_dir=Path("out"),
            cache_dir=Path("cache"),
            kv_controls="code_mode_native_live_append,code_mode_restored_kv_capsule",
            model_profile="gemma4-12b",
            case_limit=None,
        )

        command = speed.build_kv_runner_command(args, run_label="full-kv")

        self.assertNotIn("--case-limit", command)
        self.assertNotIn("None", command)

    def test_codex_command_wraps_windows_powershell_shim(self) -> None:
        args = argparse.Namespace(
            codex_bin=r"C:\Users\Dushyant\AppData\Roaming\npm\codex.ps1",
            node_bin="node",
            codex_profile="gemma",
        )

        command = speed.codex_command(args, resume=True)

        self.assertEqual(command[:5], ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"])
        self.assertIn("resume", command)
        self.assertIn("--last", command)
        self.assertLess(command.index("--profile"), command.index("exec"))
        self.assertEqual(command[-1], "-")

    def test_codex_command_wraps_node_entrypoint(self) -> None:
        args = argparse.Namespace(
            codex_bin=r"C:\Users\Dushyant\AppData\Roaming\npm\node_modules\@openai\codex\bin\codex.js",
            node_bin=r"C:\Program Files\nodejs\node.exe",
            codex_profile="gemma",
        )

        command = speed.codex_command(args, resume=False)

        self.assertEqual(command[:4], [r"C:\Program Files\nodejs\node.exe", args.codex_bin, "--profile", "gemma"])
        self.assertLess(command.index("--profile"), command.index("exec"))
        self.assertIn("--json", command)
        self.assertEqual(command[-1], "-")

    def test_dry_run_writes_codex_prompts_and_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet_path = root / "packet.jsonl"
            speed.write_jsonl(packet_path, full_packet(["bfcl:java:java_0", "bfcl:java:java_12"]))
            out_dir = root / "out"

            exit_code = speed.run(
                [
                    "--packet",
                    str(packet_path),
                    "--out-dir",
                    str(out_dir),
                    "--cache-dir",
                    str(root / "cache"),
                    "--systems",
                    "codex",
                    "--case-limit",
                    "2",
                    "--dry-run",
                    "--run-label",
                    "dry-smoke",
                ]
            )

            self.assertEqual(exit_code, 0)
            records = speed.read_jsonl(out_dir / "dry-smoke-speed-records.jsonl")
            self.assertEqual(len(records), 2)
            self.assertTrue((out_dir / "dry-smoke-codex-prompts" / "0000-bfcl-java-java_0.txt").exists())
            self.assertEqual(records[0]["system"], "codex_ollama_regular_tools_compaction")

    def test_summary_counts_by_system(self) -> None:
        records = [
            {"system": "codex", "case_id": "a", "wall_ms": 10, "passed": True, "visible_input_tokens": 100},
            {"system": "codex", "case_id": "b", "wall_ms": 20, "passed": False, "visible_input_tokens": 110},
            {"system": "kv", "case_id": "a", "wall_ms": 5, "passed": True, "visible_input_tokens": 10},
        ]

        summary = speed.summarize_speed_records(records)

        self.assertEqual(summary["record_count"], 3)
        self.assertEqual(summary["systems"]["codex"]["record_count"], 2)
        self.assertEqual(summary["systems"]["codex"]["pass_count"], 1)
        self.assertEqual(summary["systems"]["codex"]["cumulative_wall_ms"], 30)
        self.assertEqual(summary["systems"]["kv"]["visible_input_tokens"], 10)

    def test_kv_speed_record_uses_total_timing_and_position_tokens(self) -> None:
        row = {
            "case_id": "bfcl:java:java_0",
            "control_id": "code_mode_restored_kv_capsule",
            "control_gate_passed": True,
            "failure_class": None,
            "timing": {
                "total_ms": 1200.0,
                "prompt_eval_ms": 30.0,
                "decode_ms": 400.0,
                "capsule_restore_ms": 7.0,
            },
            "quality": {"generated_token_count": 12, "final_source": "host_tool_answer_field", "repair_count": 0},
            "positions": {"tail_token_count": 45, "prefix_token_count": 232},
        }

        record = speed.kv_speed_record(row, task_index=0, run_label="smoke")

        self.assertEqual(record["wall_ms"], 1200.0)
        self.assertEqual(record["visible_input_tokens"], 45)
        self.assertEqual(record["stable_context_tokens"], 232)
        self.assertEqual(record["capsule_restore_ms"], 7.0)


if __name__ == "__main__":
    unittest.main()
