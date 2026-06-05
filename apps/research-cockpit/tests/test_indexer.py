import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server


class IndexerTests(unittest.TestCase):
    def test_extract_controls_from_by_control(self):
        controls = server.extract_controls(
            {
                "by_control": {
                    "full": {"gate_pass_count": 8, "record_count": 10},
                    "tail": {"pass_rate": 0.4, "mean_score": 0.2, "record_count": 10},
                }
            }
        )

        by_name = {control["name"]: control for control in controls}
        self.assertEqual(by_name["full"]["passRate"], 0.8)
        self.assertEqual(by_name["tail"]["meanScore"], 0.2)

    def test_task_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.md"
            path.write_text("- [x] done\n- [ ] todo\n", encoding="utf-8")
            counts = server.task_counts(path)

        self.assertEqual(counts["completed"], 1)
        self.assertEqual(counts["total"], 2)
        self.assertEqual(counts["status"], "in-progress")

    def test_flatten_failure_classes(self):
        failures = server.flatten_failure_classes(
            {
                "control_a": {"prompt": 2, "scorer": 1},
                "nested": {"control_b": {"prompt": 3}},
            }
        )

        self.assertEqual(failures["prompt"], 5)
        self.assertEqual(failures["scorer"], 1)

    def test_safe_repo_file_rejects_parent_escape(self):
        with self.assertRaises(ValueError):
            server.safe_repo_file("../../etc/passwd")


if __name__ == "__main__":
    unittest.main()
