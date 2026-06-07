from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import flashcache_restored_prefix_full_resend_probe as probe  # noqa: E402


class RestoredPrefixFullResendProbeTests(unittest.TestCase):
    def test_extracts_and_scores_exact_json_answer(self) -> None:
        answer, error = probe.extract_answer('{"answer":"RPF-1047-ALPHA"}')

        self.assertEqual(answer, "RPF-1047-ALPHA")
        self.assertIsNone(error)
        self.assertTrue(probe.score_answer(answer, "RPF-1047-ALPHA")["passed"])
        self.assertFalse(probe.score_answer("token RPF-1047-ALPHA", "RPF-1047-ALPHA")["passed"])

    def test_default_cases_have_distinct_exact_tokens(self) -> None:
        cases = probe.default_cases()

        self.assertEqual(len(cases), 3)
        for case in cases:
            probe.validate_case(case)
            self.assertIn(case.secret_token, case.full_prompt)
            self.assertIn(case.perturbed_token, case.perturbed_full_prompt)
            self.assertNotIn(case.secret_token, case.perturbed_prefix)

    def test_summary_recommends_graphwalks_when_controls_and_timing_pass(self) -> None:
        records = [
            self._record("c", "cold-full", True, 20.0, 120),
            self._record("c", "restored-full", True, 8.0, 48),
            self._record("c", "perturbed-full", True, 19.0, 118),
            self._record("c", "wrong-slot-full", True, 20.0, 120),
        ]

        summary = probe.summarize(records)

        self.assertEqual(summary["gate"]["overall_interpretation"], "correctness_safe_with_useful_acceleration_evidence")
        self.assertTrue(summary["gate"]["recommend_graphwalks_follow_up"])
        self.assertEqual(summary["by_case"]["c"]["interpretation"], "correctness_safe_with_prompt_reduction")

    def test_summary_requires_mean_or_token_acceleration_not_one_noisy_case(self) -> None:
        records = []
        for case_id, cold_ms, restored_ms in [
            ("a", 660.0, 718.0),
            ("b", 648.0, 698.0),
            ("c", 665.0, 646.0),
        ]:
            records.extend(
                [
                    self._record(case_id, "cold-full", True, cold_ms, 80),
                    self._record(case_id, "restored-full", True, restored_ms, 80),
                    self._record(case_id, "perturbed-full", True, cold_ms + 20.0, 80),
                    self._record(case_id, "wrong-slot-full", True, cold_ms, 80),
                ]
            )

        summary = probe.summarize(records)

        self.assertTrue(summary["gate"]["correctness_and_safety_controls_pass"])
        self.assertEqual(summary["gate"]["prompt_reduction_cases"], 1)
        self.assertFalse(summary["gate"]["useful_acceleration_evidence"])
        self.assertFalse(summary["gate"]["recommend_graphwalks_follow_up"])

    def test_run_restored_full_primes_saves_restores_then_sends_full_prompt(self) -> None:
        case = probe.default_cases()[0]
        args = probe.parse_args(["--model", "fake-model.gguf"])
        calls: list[dict[str, object]] = []

        class FakeClient:
            def completion(self, prompt, *, n_predict, temperature, cache_prompt=True, json_schema=None):
                calls.append(
                    {
                        "kind": "completion",
                        "prompt": prompt,
                        "n_predict": n_predict,
                        "temperature": temperature,
                        "cache_prompt": cache_prompt,
                        "json_schema": json_schema,
                    }
                )
                if json_schema is None:
                    return {"content": "", "timings": {"prompt_ms": 1.0, "prompt_n": 10}}
                return {"content": json.dumps({"answer": case.secret_token}), "timings": {"prompt_ms": 2.0, "prompt_n": 20}}

            def save_slot(self, filename):
                calls.append({"kind": "save", "filename": filename})
                return {"n_saved": 10, "n_written": 100, "_wall_ms": 3.0}

            def restore_slot(self, filename):
                calls.append({"kind": "restore", "filename": filename})
                return {"n_restored": 10, "n_read": 100, "_wall_ms": 4.0}

        class FakeManagedServer:
            def __init__(self, config, label="probe"):
                self.config = config
                self.label = label
                self.log_path = Path("fake.log")

            def __enter__(self):
                return FakeClient()

            def __exit__(self, exc_type, exc, tb):
                return None

        old_server = probe.ManagedLlamaServer
        try:
            probe.ManagedLlamaServer = FakeManagedServer  # type: ignore[assignment]
            with tempfile.TemporaryDirectory() as tmp_dir:
                record = probe.run_restored_full(args, case, Path(tmp_dir))
        finally:
            probe.ManagedLlamaServer = old_server  # type: ignore[assignment]

        self.assertTrue(record["passed"])
        self.assertEqual(record["mode"], "restored-full")
        self.assertEqual([call["kind"] for call in calls], ["completion", "save", "restore", "completion"])
        self.assertEqual(calls[0]["prompt"], case.stable_prefix)
        self.assertFalse(calls[0]["cache_prompt"])
        self.assertEqual(calls[3]["prompt"], case.full_prompt)
        self.assertTrue(calls[3]["cache_prompt"])
        self.assertEqual(calls[3]["json_schema"], probe.ANSWER_JSON_SCHEMA)

    def test_wrong_slot_control_scores_visible_prompt_not_slot_source(self) -> None:
        cases = probe.default_cases()
        case = cases[0]
        wrong_slot_case = cases[1]
        args = probe.parse_args(["--model", "fake-model.gguf"])
        final_prompts = []

        class FakeClient:
            def completion(self, prompt, *, n_predict, temperature, cache_prompt=True, json_schema=None):
                if json_schema is None:
                    return {"content": "", "timings": {"prompt_ms": 1.0, "prompt_n": 10}}
                final_prompts.append(prompt)
                return {"content": json.dumps({"answer": case.secret_token}), "timings": {"prompt_ms": 2.0, "prompt_n": 20}}

            def save_slot(self, filename):
                return {"n_saved": 10, "n_written": 100, "_wall_ms": 3.0}

            def restore_slot(self, filename):
                return {"n_restored": 10, "n_read": 100, "_wall_ms": 4.0}

        class FakeManagedServer:
            def __init__(self, config, label="probe"):
                self.config = config
                self.label = label
                self.log_path = Path("fake.log")

            def __enter__(self):
                return FakeClient()

            def __exit__(self, exc_type, exc, tb):
                return None

        old_server = probe.ManagedLlamaServer
        try:
            probe.ManagedLlamaServer = FakeManagedServer  # type: ignore[assignment]
            with tempfile.TemporaryDirectory() as tmp_dir:
                record = probe.run_wrong_slot_full(args, case, wrong_slot_case, Path(tmp_dir))
        finally:
            probe.ManagedLlamaServer = old_server  # type: ignore[assignment]

        self.assertTrue(record["passed"])
        self.assertEqual(record["slot_source_case_id"], wrong_slot_case.case_id)
        self.assertEqual(final_prompts, [case.full_prompt])
        self.assertFalse(record["score_details"]["leakage_detected"])

    def test_command_writes_dry_run_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output = Path(tmp_dir) / "probe.json"
            exit_code = probe.main(["--dry-run", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["summary"]["by_mode"]["cold-full"]["case_count"], 3)
            self.assertEqual(data["summary"]["by_mode"]["prime-save"]["scored_count"], 0)
            self.assertTrue(data["summary"]["gate"]["recommend_graphwalks_follow_up"])

    @staticmethod
    def _record(case_id: str, mode: str, passed: bool, prompt_ms: float, prompt_n: int) -> dict[str, object]:
        record = {
            "case_id": case_id,
            "mode": mode,
            "scored": True,
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "answer_parse_error": None,
            "timings": {"prompt_ms": prompt_ms, "prompt_n": prompt_n},
        }
        record["failure_classification"] = probe.classify_record(record)
        return record


if __name__ == "__main__":
    unittest.main()
