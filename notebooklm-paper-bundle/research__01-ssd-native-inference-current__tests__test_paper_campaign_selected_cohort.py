from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "benchmarks"))

import paper_campaign_selected_cohort as selected_cohort  # noqa: E402


def record(case_id: str, category: str, control_id: str, passed: bool, *, answer: bool | None = None) -> dict:
    if answer is None:
        answer = passed
    return {
        "case_id": case_id,
        "task_bucket": f"bfcl_{category}",
        "control_id": control_id,
        "control_gate_passed": passed,
        "failure_class": None if passed else "failed",
        "quality": {
            "answer_contained": answer,
            "response_hash": f"{case_id}:{control_id}:{passed}:{answer}",
            "normalized_response_hash": f"{case_id}:{control_id}:{passed}:{answer}",
        },
        "source_provenance": {"benchmark_id": "BFCL", "source_category": category},
    }


def clean_case(case_id: str, category: str = "simple") -> list[dict]:
    rows = []
    for control in selected_cohort.CONTROL_ORDER:
        if control in selected_cohort.PRIMARY_NEGATIVE_CONTROLS:
            rows.append(record(case_id, category, control, True, answer=False))
        else:
            rows.append(record(case_id, category, control, True, answer=True))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


class PaperCampaignSelectedCohortTests(unittest.TestCase):
    def test_selects_clean_cases_and_excludes_no_call_categories(self) -> None:
        records = clean_case("case_a", "simple") + clean_case("case_b", "irrelevance")
        packet = [{"case_id": row["case_id"], "control_id": row["control_id"]} for row in records]

        summary, selected = selected_cohort.summarize_and_select(
            calibration_records=records,
            source_packet_rows=packet,
            target_rows=200,
        )

        self.assertEqual(selected, ["case_a"])
        self.assertEqual(summary["clean_primary_eligible_count"], 1)
        self.assertEqual(summary["rejection_counts"]["no_call_category"], 1)

    def test_rejects_negative_control_leaks(self) -> None:
        records = clean_case("case_a")
        for row in records:
            if row["control_id"] == "code_mode_fresh_tail_only":
                row["quality"]["answer_contained"] = True

        summary, selected = selected_cohort.summarize_and_select(
            calibration_records=records,
            source_packet_rows=[{"case_id": row["case_id"], "control_id": row["control_id"]} for row in records],
            target_rows=200,
        )

        self.assertEqual(selected, [])
        self.assertEqual(summary["clean_primary_eligible_count"], 0)
        self.assertEqual(summary["rejection_counts"]["code_mode_fresh_tail_only_leaked"], 1)

    def test_selected_packet_keeps_all_controls_for_selected_cases(self) -> None:
        source_rows = clean_case("case_a") + clean_case("case_b")

        rows = selected_cohort.selected_packet_rows(source_rows, ["case_b"])

        self.assertEqual(len(rows), len(selected_cohort.CONTROL_ORDER))
        self.assertEqual({row["case_id"] for row in rows}, {"case_b"})
        self.assertEqual([row["control_id"] for row in rows], selected_cohort.CONTROL_ORDER)

    def test_cli_blocks_below_minimum(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        raw = root / "raw"
        summary_dir = root / "summary"
        label = "calibration"
        records = clean_case("case_a")
        write_jsonl(raw / f"{label}-model-loop-records.jsonl", records)
        write_jsonl(raw / f"{label}-control-packet.jsonl", records)

        exit_code = selected_cohort.main(
            [
                "--calibration-run-label",
                label,
                "--raw-dir",
                str(raw),
                "--summary-dir",
                str(summary_dir),
                "--min-clean-rows",
                "2",
                "--target-rows",
                "3",
            ]
        )

        self.assertEqual(exit_code, 3)
        summary = json.loads((summary_dir / f"{label}-calibration-summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["clean_primary_eligible_count"], 1)


if __name__ == "__main__":
    unittest.main()
