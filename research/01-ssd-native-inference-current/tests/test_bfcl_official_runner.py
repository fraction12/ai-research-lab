from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "benchmarks"))

import bfcl_official_runner as official  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


class BFCLOfficialRunnerTests(unittest.TestCase):
    def make_v4_data_dir(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        write_jsonl(
            root / "BFCL_v4_simple_python.json",
            [
                {
                    "id": "simple_python_0",
                    "question": [[{"role": "user", "content": "Triangle area base 10 height 5."}]],
                    "function": [
                        {
                            "name": "calculate_triangle_area",
                            "description": "Calculate triangle area.",
                            "parameters": {
                                "type": "dict",
                                "properties": {"base": {"type": "integer"}, "height": {"type": "integer"}},
                                "required": ["base", "height"],
                            },
                        }
                    ],
                }
            ],
        )
        write_jsonl(
            root / "possible_answer" / "BFCL_v4_simple_python.json",
            [
                {
                    "id": "simple_python_0",
                    "ground_truth": [{"calculate_triangle_area": {"base": [10], "height": [5]}}],
                }
            ],
        )
        write_jsonl(
            root / "BFCL_v4_multiple.json",
            [
                {
                    "id": "multiple_0",
                    "question": [[{"role": "user", "content": "Area of triangle sides 3 4 5."}]],
                    "function": [
                        {
                            "name": "math.triangle_area_heron",
                            "description": "Calculate area by Heron.",
                            "parameters": {"type": "dict", "properties": {}},
                        }
                    ],
                }
            ],
        )
        write_jsonl(
            root / "possible_answer" / "BFCL_v4_multiple.json",
            [
                {
                    "id": "multiple_0",
                    "ground_truth": [{"math.triangle_area_heron": {"side1": [3], "side2": [4], "side3": [5]}}],
                }
            ],
        )
        return root

    def test_stage_official_data_creates_adapter_aliases(self) -> None:
        source = self.make_v4_data_dir()
        with tempfile.TemporaryDirectory() as tmp:
            staged = official.stage_official_data(source, Path(tmp) / "staged", ["simple_python", "multiple"])

            staged_root = Path(staged["staged_dir"])
            self.assertTrue((staged_root / "BFCL_v4_simple_python.json").exists())
            self.assertTrue((staged_root / "BFCL_v3_multiple.json").exists())
            self.assertTrue((staged_root / "possible_answer" / "BFCL_v3_multiple.json").exists())

    def test_python_call_formatter_matches_bfcl_prompt_mode_shape(self) -> None:
        calls = [
            {"name": "calculate_triangle_area", "arguments": {"base": 10, "height": 5}},
            {"name": "math.echo", "arguments": {"items": ["a", "b"], "opts": {"loud": True}}},
        ]

        self.assertEqual(
            official.calls_to_bfcl_prompt_result(calls),
            "[calculate_triangle_area(base=10, height=5), math.echo(items=['a', 'b'], opts={'loud': True})]",
        )
        self.assertEqual(official.calls_to_bfcl_prompt_result([]), "[]")

    def test_export_official_results_writes_bfcl_result_tree_and_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records = root / "records.jsonl"
            write_jsonl(
                records,
                [
                    {
                        "case_id": "bfcl:simple_python:simple_python_0",
                        "control_id": "code_mode_restored_kv_capsule",
                        "catalog_hash": "catalog",
                        "source_provenance": {
                            "source_category": "simple_python",
                            "source_row_id": "simple_python_0",
                            "source_row_hash": "rowhash",
                        },
                        "positions": {"tail_token_count": 12},
                        "quality": {
                            "generated_token_count": 7,
                            "response_hash": "responsehash",
                            "generated_text_hash": "generatedhash",
                            "bfcl_score": {"passed": True},
                        },
                        "timing": {"total_ms": 123.4},
                        "capsule": {"state_route_internal": "seq-file"},
                        "raw": {
                            "response": json.dumps(
                                [{"name": "calculate_triangle_area", "arguments": {"base": 10, "height": 5}}]
                            )
                        },
                    }
                ],
            )

            exported = official.export_official_results(
                records,
                root / "export",
                model_dir="gemma4-kv-capsule-pti",
                control_id="code_mode_restored_kv_capsule",
            )

            result_file = (
                root
                / "export"
                / "result"
                / "gemma4-kv-capsule-pti"
                / "non_live"
                / "BFCL_v4_simple_python_result.json"
            )
            self.assertTrue(result_file.exists())
            row = json.loads(result_file.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(row["id"], "simple_python_0")
            self.assertEqual(row["result"], "[calculate_triangle_area(base=10, height=5)]")
            self.assertEqual(exported["record_count"], 1)
            self.assertTrue(Path(exported["sidecar_path"]).exists())

    def test_export_maps_adapter_simple_alias_ids_to_official_bfcl_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            records = root / "records.jsonl"
            write_jsonl(
                records,
                [
                    {
                        "case_id": "bfcl:simple_java:java_0",
                        "control_id": "code_mode_restored_kv_capsule",
                        "catalog_hash": "catalog",
                        "source_provenance": {
                            "source_category": "simple_java",
                            "source_row_id": "java_0",
                            "source_row_hash": "rowhash",
                        },
                        "positions": {"tail_token_count": 12},
                        "quality": {"generated_token_count": 7, "bfcl_score": {"passed": True}},
                        "timing": {"total_ms": 123.4},
                        "raw": {
                            "response": json.dumps(
                                [{"name": "GeometryPresentation.createPresentation", "arguments": {"controller": "mapController", "parent": "mapArea"}}]
                            )
                        },
                    }
                ],
            )

            official.export_official_results(
                records,
                root / "export",
                model_dir="gemma4-kv-capsule-pti",
                control_id="code_mode_restored_kv_capsule",
            )

            result_file = (
                root
                / "export"
                / "result"
                / "gemma4-kv-capsule-pti"
                / "non_live"
                / "BFCL_v4_simple_java_result.json"
            )
            row = json.loads(result_file.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(row["id"], "simple_java_0")

    def test_prepare_materializes_packet_from_v4_fixture(self) -> None:
        source = self.make_v4_data_dir()
        with tempfile.TemporaryDirectory() as tmp:
            args = official.parse_args(
                [
                    "prepare",
                    "--lane-root",
                    str(Path(tmp) / "lane"),
                    "--bfcl-data-dir",
                    str(source),
                    "--category",
                    "simple_python",
                    "--category",
                    "multiple",
                    "--per-category",
                    "1",
                ]
            )

            materialized = official.materialize(args)

            packet = Path(materialized["packet_path"])
            self.assertTrue(packet.exists())
            lines = packet.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2 * 7)
            self.assertEqual(materialized["case_count"], 2)


if __name__ == "__main__":
    unittest.main()
