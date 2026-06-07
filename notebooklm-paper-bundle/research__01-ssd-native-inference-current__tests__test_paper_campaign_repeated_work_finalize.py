from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import paper_campaign_repeated_work_finalize as finalize  # noqa: E402
import paper_campaign_repeated_work_speed as speed  # noqa: E402


def packet_row(case_id: str, control_id: str) -> dict[str, object]:
    return {
        "case_id": case_id,
        "control_id": control_id,
        "expected_calls": [
            {
                "name": "GeometryPresentation.createPresentation",
                "arguments": {"controller": ["mapController"], "parent": ["mapArea"]},
            }
        ],
        "visible_prompt": "Prompt",
    }


class RepeatedWorkFinalizeTests(unittest.TestCase):
    def test_reconstruct_codex_records_scores_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            run_label = "bfcl-repeated-work-speed-v1"
            prompt_dir = out_dir / f"{run_label}-codex-prompts"
            prompt_dir.mkdir()
            case_id = "bfcl:java:java_0"
            (prompt_dir / "0000-bfcl-java-java_0.txt").write_text("prompt", encoding="utf-8")
            (out_dir / f"{run_label}-codex-0000.stdout.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "item.completed",
                                "item": {
                                    "text": json.dumps(
                                        {
                                            "case_id": case_id,
                                            "tool_calls": [
                                                {
                                                    "function_name": "GeometryPresentation.createPresentation",
                                                    "arguments": {
                                                        "controller": "mapController",
                                                        "parent": "mapArea",
                                                    },
                                                }
                                            ],
                                            "final_answer": "",
                                        }
                                    )
                                },
                            }
                        ),
                        json.dumps({"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 3}}),
                    ]
                ),
                encoding="utf-8",
            )
            (out_dir / f"{run_label}-codex-0000.stderr.txt").write_text("", encoding="utf-8")
            packet_rows = [packet_row(case_id, control_id) for control_id in speed.CONTROL_ORDER]

            records = finalize.reconstruct_codex_records(
                packet_rows=packet_rows,
                out_dir=out_dir,
                run_label=run_label,
                expected_cases=1,
                codex_profile="gemma4-ollama-compact",
            )

        self.assertEqual(len(records), 1)
        self.assertTrue(records[0]["passed"])
        self.assertEqual(records[0]["visible_input_tokens"], 10)
        self.assertTrue(records[0]["metadata"]["reconstructed_from_artifacts"])

    def test_reconstruct_kv_records_uses_resume_source_label_but_original_run_label(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            source_label = "bfcl-repeated-work-speed-v1-kv-resume"
            speed.write_jsonl(
                out_dir / f"{source_label}-kv-model-loop-records.jsonl",
                [
                    {
                        "case_id": "bfcl:java:java_0",
                        "control_id": "code_mode_native_live_append",
                    },
                    {
                        "case_id": "bfcl:java:java_0",
                        "control_id": "code_mode_restored_kv_capsule",
                        "control_gate_passed": True,
                        "timing": {"total_ms": 123.0},
                        "positions": {"tail_token_count": 45, "prefix_token_count": 500},
                        "quality": {"generated_token_count": 9},
                    },
                ],
            )

            records = finalize.reconstruct_kv_records(
                out_dir=out_dir,
                source_label=source_label,
                run_label="bfcl-repeated-work-speed-v1",
            )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["run_label"], "bfcl-repeated-work-speed-v1")
        self.assertEqual(records[0]["system"], "kv_capsule_code_mode")


if __name__ == "__main__":
    unittest.main()
