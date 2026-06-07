from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import llama_cpp_prefix_reuse_audit as audit  # noqa: E402


class LlamaCppPrefixReuseAuditTests(unittest.TestCase):
    def test_default_case_is_long_and_valid(self) -> None:
        case = audit.build_default_case(4)

        audit.validate_case(case)
        self.assertIn(case.secret_token, case.stable_prefix)
        self.assertNotIn(case.secret_token, case.tail_prompt)
        self.assertIn(case.tail_prompt, case.full_prompt)

    def test_score_requires_exact_json_answer(self) -> None:
        answer, error = audit.extract_answer('{"answer":"LCPR-7319-SIGNAL"}')

        self.assertEqual(answer, "LCPR-7319-SIGNAL")
        self.assertIsNone(error)
        self.assertTrue(audit.score_answer(answer, "LCPR-7319-SIGNAL")["passed"])
        self.assertFalse(audit.score_answer("token LCPR-7319-SIGNAL", "LCPR-7319-SIGNAL")["passed"])

    def test_reduction_metrics_detect_token_or_large_timing_reduction(self) -> None:
        baseline = {"timings": {"prompt_ms": 1000.0, "prompt_n": 2000}}
        measured = {"timings": {"prompt_ms": 100.0, "prompt_n": 50}}

        metrics = audit.reduction_metrics(baseline, measured)

        self.assertTrue(metrics["token_reduction"])
        self.assertTrue(metrics["timing_reduction"])
        self.assertTrue(metrics["reuse_observed"])

    def test_summary_separates_exact_repeat_from_restore_reuse(self) -> None:
        records = [
            self._record("cold-full", "baseline_passed", True, {}),
            self._record("same-server-exact-repeat", "exact_repeat_reuse_observed", True, {"reuse_observed": True}),
            self._record("same-server-restore-full", "restore_no_reuse", True, {"reuse_observed": False}),
            self._record("fresh-server-restore-full", "restore_no_reuse", True, {"reuse_observed": False}),
        ]

        summary = audit.summarize(records)

        self.assertTrue(summary["gate"]["exact_repeat_reuse_observed"])
        self.assertFalse(summary["gate"]["fresh_server_restore_reuse_observed"])
        self.assertEqual(summary["gate"]["overall_interpretation"], "exact_repeat_reuse_but_restore_no_reuse")

    def test_same_server_exact_repeat_sends_same_prompt_twice_with_cache_prompt(self) -> None:
        case = audit.build_default_case(2)
        args = audit.parse_args(["--model", "fake-model.gguf"])
        calls: list[dict[str, object]] = []

        class FakeClient:
            def completion(self, prompt, *, n_predict, temperature, cache_prompt=True, json_schema=None):
                calls.append(
                    {
                        "prompt": prompt,
                        "n_predict": n_predict,
                        "temperature": temperature,
                        "cache_prompt": cache_prompt,
                        "json_schema": json_schema,
                    }
                )
                prompt_ms = 1000.0 if len(calls) == 1 else 50.0
                prompt_n = 2000 if len(calls) == 1 else 40
                return {
                    "content": json.dumps({"answer": case.secret_token}),
                    "timings": {"prompt_ms": prompt_ms, "prompt_n": prompt_n},
                }

        class FakeManagedServer:
            def __init__(self, config, label="audit"):
                self.config = config
                self.label = label
                self.log_path = Path("fake.log")

            def __enter__(self):
                return FakeClient()

            def __exit__(self, exc_type, exc, tb):
                return None

        old_server = audit.ManagedLlamaServer
        try:
            audit.ManagedLlamaServer = FakeManagedServer  # type: ignore[assignment]
            with tempfile.TemporaryDirectory() as tmp_dir:
                record = audit.run_same_server_exact_repeat(args, case, Path(tmp_dir))
        finally:
            audit.ManagedLlamaServer = old_server  # type: ignore[assignment]

        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]["prompt"], case.full_prompt)
        self.assertEqual(calls[1]["prompt"], case.full_prompt)
        self.assertTrue(calls[0]["cache_prompt"])
        self.assertTrue(calls[1]["cache_prompt"])
        self.assertEqual(calls[0]["json_schema"], audit.ANSWER_JSON_SCHEMA)
        self.assertEqual(record["failure_classification"], "exact_repeat_reuse_observed")

    def test_fresh_server_restore_primes_saves_restores_then_full_prompt(self) -> None:
        case = audit.build_default_case(2)
        args = audit.parse_args(["--model", "fake-model.gguf"])
        calls: list[dict[str, object]] = []
        cold_record = self._cold_record(case)

        class FakeClient:
            def completion(self, prompt, *, n_predict, temperature, cache_prompt=True, json_schema=None):
                calls.append({"kind": "completion", "prompt": prompt, "cache_prompt": cache_prompt, "json_schema": json_schema})
                prompt_ms = 900.0 if json_schema is None else 800.0
                prompt_n = 1800 if json_schema is None else 1900
                return {
                    "content": "" if json_schema is None else json.dumps({"answer": case.secret_token}),
                    "timings": {"prompt_ms": prompt_ms, "prompt_n": prompt_n},
                }

            def save_slot(self, filename):
                calls.append({"kind": "save", "filename": filename})
                return {"n_saved": 1800, "n_written": 1234, "_wall_ms": 3.0}

            def restore_slot(self, filename):
                calls.append({"kind": "restore", "filename": filename})
                return {"n_restored": 1800, "n_read": 1234, "_wall_ms": 4.0}

        class FakeManagedServer:
            def __init__(self, config, label="audit"):
                self.config = config
                self.label = label
                self.log_path = Path("fake.log")

            def __enter__(self):
                return FakeClient()

            def __exit__(self, exc_type, exc, tb):
                return None

        old_server = audit.ManagedLlamaServer
        try:
            audit.ManagedLlamaServer = FakeManagedServer  # type: ignore[assignment]
            with tempfile.TemporaryDirectory() as tmp_dir:
                record = audit.run_fresh_server_restore_full(args, case, cold_record, Path(tmp_dir))
        finally:
            audit.ManagedLlamaServer = old_server  # type: ignore[assignment]

        self.assertEqual([call["kind"] for call in calls], ["completion", "save", "restore", "completion"])
        self.assertEqual(calls[0]["prompt"], case.stable_prefix)
        self.assertFalse(calls[0]["cache_prompt"])
        self.assertEqual(calls[3]["prompt"], case.full_prompt)
        self.assertTrue(calls[3]["cache_prompt"])
        self.assertEqual(record["session_setup"]["restore_response"]["n_restored"], 1800)

    def test_command_writes_dry_run_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output = Path(tmp_dir) / "audit.json"
            exit_code = audit.main(["--dry-run", "--prefix-repeat", "4", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["summary"]["by_mode"]["cold-full"]["case_count"], 1)
            self.assertTrue(data["summary"]["gate"]["exact_repeat_reuse_observed"])
            self.assertFalse(data["summary"]["gate"]["fresh_server_restore_reuse_observed"])

    @staticmethod
    def _record(mode: str, classification: str, passed: bool, reduction: dict[str, object]) -> dict[str, object]:
        return {
            "case_id": "c",
            "mode": mode,
            "passed": passed,
            "timings": {"prompt_ms": 100.0, "prompt_n": 100},
            "reduction": reduction,
            "failure_classification": classification,
        }

    @staticmethod
    def _cold_record(case: audit.AuditCase) -> dict[str, object]:
        return {
            "raw_response": json.dumps({"answer": case.secret_token}),
            "timings": {"prompt_ms": 1000.0, "prompt_n": 2000},
        }


if __name__ == "__main__":
    unittest.main()
