from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import summarize_results as summary  # noqa: E402


class BenchmarkSummaryTests(unittest.TestCase):
    def write_json(self, payload: object) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        with tmp:
            json.dump(payload, tmp)
        return Path(tmp.name)

    def test_summarizes_direct_prompt_cache_result(self) -> None:
        path = self.write_json(
            {
                "metadata": {
                    "model": "model.gguf",
                    "fixture": "fixture.json",
                    "started_at": "2026-06-02T00:00:00Z",
                    "server_mode": "persistent",
                    "cache_mode": "hot",
                },
                "prompt_set": {"prefix_prompt_bytes": 5487},
                "slot_cache": {"file_bytes": 31_108_988},
                "comparison": {
                    "baseline_prompt_ms_sum": 8751.671,
                    "restored_prompt_ms_sum": 8503.763,
                    "baseline_minus_restored_prompt_ms": 247.908,
                    "baseline_minus_restored_prompt_ratio": 0.0283,
                },
            }
        )

        row = summary.summarize_path(path)

        self.assertEqual(row.kind, "llama-cpp-prompt-cache")
        self.assertEqual(row.before_ms, 8751.671)
        self.assertEqual(row.after_ms, 8503.763)
        self.assertEqual(row.slot_file_bytes, 31_108_988)

    def test_summarizes_flashcache_wrapper_result(self) -> None:
        path = self.write_json(
            {
                "metadata": {
                    "model": "model.gguf",
                    "fixture": "fixture.json",
                    "started_at": "2026-06-02T00:00:00Z",
                    "server_mode": "persistent",
                    "cache_mode": "hot",
                },
                "prompt_set": {"prefix_prompt_bytes": 5487},
                "direct_full_prompt": [
                    {"boundary_timings": {"direct_completion_ms": 10.0}},
                    {"boundary_timings": {"direct_completion_ms": 20.0}},
                ],
                "wrapper_cache_aware": [
                    {
                        "cache_state": "miss",
                        "boundary_timings": {
                            "total_wrapper_ms": 8.0,
                            "server_version_ms": 4.0,
                            "server_enter_ms": 3.0,
                            "server_exit_ms": 0.25,
                            "slot_save_ms": 1.5,
                            "tail_completion_ms": 6.0,
                        },
                    },
                    {
                        "cache_state": "hit",
                        "telemetry": {
                            "boundary_timings": {
                                "total_wrapper_ms": 7.0,
                                "server_version_ms": 0.25,
                                "server_enter_ms": 0.5,
                                "server_exit_ms": 0.0,
                                "slot_restore_ms": 2.5,
                                "tail_completion_ms": 4.0,
                            }
                        },
                    },
                ],
                "wrapper_session_setup": {
                    "slot_file_bytes": 42_000,
                    "boundary_timings": {
                        "total_wrapper_ms": 11.0,
                        "slot_restore_ms": 3.5,
                    }
                },
                "comparison": {
                    "direct_prompt_ms_sum": 8320.438,
                    "wrapper_prompt_ms_sum": 7374.344,
                    "direct_minus_wrapper_prompt_ms": 946.094,
                    "direct_minus_wrapper_prompt_ratio": 0.1137,
                    "wrapper_cache_hit_rate": 0.5,
                },
            }
        )

        row = summary.summarize_path(path)

        self.assertEqual(row.kind, "flashcache-wrapper")
        self.assertEqual(row.server_mode, "persistent")
        self.assertEqual(row.cache_mode, "hot")
        self.assertEqual(row.before_ms, 8320.438)
        self.assertEqual(row.after_ms, 7374.344)
        self.assertEqual(row.cache_states, "miss,hit")
        self.assertEqual(row.hit_rate, 0.5)
        self.assertEqual(row.boundary_direct_ms, 30.0)
        self.assertEqual(row.boundary_wrapper_ms, 15.0)
        self.assertEqual(row.boundary_server_version_ms, 4.25)
        self.assertEqual(row.boundary_save_ms, 1.5)
        self.assertEqual(row.boundary_restore_ms, 2.5)
        self.assertEqual(row.boundary_tail_ms, 10.0)
        self.assertEqual(row.boundary_server_enter_ms, 3.5)
        self.assertEqual(row.boundary_server_exit_ms, 0.25)
        self.assertEqual(row.boundary_session_setup_ms, 11.0)
        self.assertEqual(row.boundary_session_restore_ms, 3.5)
        self.assertEqual(row.slot_file_bytes, 42_000)

        rendered = summary.render([row])
        self.assertIn("cache_mode", rendered)
        self.assertIn("boundary_wrapper_ms", rendered)
        self.assertIn("boundary_session_setup_ms", rendered)
        self.assertIn("boundary_session_restore_ms", rendered)
        self.assertIn("boundary_server_version_ms", rendered)
        self.assertIn("boundary_server_enter_ms", rendered)
        self.assertIn("15.000", rendered)

    def test_unsupported_json_continues_as_row(self) -> None:
        path = self.write_json({"metadata": {"model": "unknown"}})

        row = summary.summarize_path(path)
        rendered = summary.render([row])

        self.assertEqual(row.kind, "unsupported")
        self.assertIn("unsupported", rendered)
        self.assertIn("unrecognized benchmark result schema", rendered)

    def test_missing_optional_values_render_as_na(self) -> None:
        row = summary.summarize_data({"metadata": {}, "comparison": {"direct_prompt_ms_sum": 1}}, Path("result.json"))

        rendered = summary.render([row])

        self.assertIn("n/a", rendered)


if __name__ == "__main__":
    unittest.main()
