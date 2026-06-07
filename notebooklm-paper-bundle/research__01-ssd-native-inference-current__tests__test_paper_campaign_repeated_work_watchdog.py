from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import paper_campaign_repeated_work_watchdog as watchdog  # noqa: E402


class RepeatedWorkWatchdogTests(unittest.TestCase):
    def test_kv_record_paths_include_resumed_kv_arms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            (out_dir / "bfcl-repeated-work-speed-v1-kv-model-loop-records.jsonl").write_text(
                "{}\n", encoding="utf-8"
            )
            (out_dir / "bfcl-repeated-work-speed-v1-kv-resume-kv-model-loop-records.jsonl").write_text(
                "{}\n{}\n", encoding="utf-8"
            )
            (out_dir / "bfcl-repeated-work-speed-v1-codex-0000.stdout.jsonl").write_text(
                "{}\n", encoding="utf-8"
            )

            paths = watchdog.kv_record_paths(out_dir, "bfcl-repeated-work-speed-v1")

        self.assertEqual([path.name for path in paths], [
            "bfcl-repeated-work-speed-v1-kv-model-loop-records.jsonl",
            "bfcl-repeated-work-speed-v1-kv-resume-kv-model-loop-records.jsonl",
        ])

    def test_speed_summary_paths_include_resumed_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            (out_dir / "bfcl-repeated-work-speed-v1-speed-summary.json").write_text(
                "{}", encoding="utf-8"
            )
            (out_dir / "bfcl-repeated-work-speed-v1-kv-resume-speed-summary.json").write_text(
                "{}", encoding="utf-8"
            )

            paths = watchdog.speed_summary_paths(out_dir, "bfcl-repeated-work-speed-v1")

        self.assertEqual([path.name for path in paths], [
            "bfcl-repeated-work-speed-v1-kv-resume-speed-summary.json",
            "bfcl-repeated-work-speed-v1-speed-summary.json",
        ])

    def test_preferred_summary_path_uses_newest_resume_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            original = out_dir / "bfcl-repeated-work-speed-v1-speed-summary.json"
            resumed = out_dir / "bfcl-repeated-work-speed-v1-kv-resume-speed-summary.json"
            original.write_text("{}", encoding="utf-8")
            resumed.write_text("{}", encoding="utf-8")

            preferred = watchdog.preferred_summary_path(out_dir, "bfcl-repeated-work-speed-v1")

        self.assertEqual(preferred.name, "bfcl-repeated-work-speed-v1-kv-resume-speed-summary.json")

    def test_speed_record_paths_include_resumed_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            (out_dir / "bfcl-repeated-work-speed-v1-speed-records.jsonl").write_text(
                "{}\n", encoding="utf-8"
            )
            (out_dir / "bfcl-repeated-work-speed-v1-kv-resume-speed-records.jsonl").write_text(
                "{}\n{}\n", encoding="utf-8"
            )

            paths = watchdog.speed_record_paths(out_dir, "bfcl-repeated-work-speed-v1")

        self.assertEqual([path.name for path in paths], [
            "bfcl-repeated-work-speed-v1-kv-resume-speed-records.jsonl",
            "bfcl-repeated-work-speed-v1-speed-records.jsonl",
        ])


if __name__ == "__main__":
    unittest.main()
