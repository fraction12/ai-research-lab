from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import flashcache_session_continuation_litmus as litmus  # noqa: E402


class SessionContinuationLitmusTests(unittest.TestCase):
    def test_extracts_json_answer(self) -> None:
        answer, error = litmus.extract_answer('{"answer":"ZXQ-7419-ALPHA"}')

        self.assertEqual(answer, "ZXQ-7419-ALPHA")
        self.assertIsNone(error)

    def test_scores_exact_secret_token(self) -> None:
        self.assertTrue(litmus.score_answer("token ZXQ-7419-ALPHA", "ZXQ-7419-ALPHA")["passed"])
        self.assertFalse(litmus.score_answer("wrong", "ZXQ-7419-ALPHA")["passed"])

    def test_summary_interprets_passing_continuation(self) -> None:
        records = [
            {"case_id": "c", "mode": "full", "passed": True, "score": 1.0},
            {"case_id": "c", "mode": "fresh-tail", "passed": False, "score": 0.0},
            {"case_id": "c", "mode": "live-tail", "passed": True, "score": 1.0},
            {"case_id": "c", "mode": "restored-tail", "passed": True, "score": 1.0},
        ]

        summary = litmus.summarize(records)

        self.assertEqual(summary["by_case"]["c"]["interpretation"], "same_slot_and_restore_continue")
        self.assertEqual(summary["by_mode"]["live-tail"]["pass_rate"], 1.0)

    def test_run_live_tail_primes_without_save_or_restore(self) -> None:
        case = litmus.default_cases()[0]
        args = litmus.parse_args(["--dry-run"])
        calls = []

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
                if json_schema is None:
                    return {"content": "", "timings": {"prompt_ms": 1.0}}
                return {"content": json.dumps({"answer": case.secret_token}), "timings": {"prompt_ms": 2.0}}

            def save_slot(self, filename):
                raise AssertionError(f"live-tail should not save {filename}")

            def restore_slot(self, filename):
                raise AssertionError(f"live-tail should not restore {filename}")

        class FakeManagedServer:
            def __init__(self, config, label="litmus"):
                self.config = config
                self.label = label

            def __enter__(self):
                return FakeClient()

            def __exit__(self, exc_type, exc, tb):
                return None

        old_server = litmus.ManagedLlamaServer
        try:
            litmus.ManagedLlamaServer = FakeManagedServer  # type: ignore[assignment]
            record = litmus.run_live_tail(args, case, Path("cache"))
        finally:
            litmus.ManagedLlamaServer = old_server  # type: ignore[assignment]

        self.assertTrue(record["passed"])
        self.assertEqual(record["mode"], "live-tail")
        self.assertEqual(len(calls), 2)
        self.assertFalse(calls[0]["cache_prompt"])
        self.assertTrue(calls[1]["cache_prompt"])
        self.assertIsNone(calls[0]["json_schema"])
        self.assertEqual(calls[1]["json_schema"], litmus.ANSWER_JSON_SCHEMA)

    def test_command_writes_dry_run_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output = Path(tmp_dir) / "litmus.json"
            exit_code = litmus.main(["--dry-run", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["summary"]["by_mode"]["full"]["case_count"], 3)
            self.assertEqual(data["summary"]["by_mode"]["fresh-tail"]["case_count"], 3)


if __name__ == "__main__":
    unittest.main()
