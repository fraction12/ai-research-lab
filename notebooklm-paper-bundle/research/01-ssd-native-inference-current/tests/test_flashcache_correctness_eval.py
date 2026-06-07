from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import flashcache_correctness_eval as correctness  # noqa: E402


class FlashcacheCorrectnessEvalTests(unittest.TestCase):
    def test_dataset_registry_lists_selected_huggingface_datasets(self) -> None:
        datasets = {row["id"]: row for row in correctness.list_datasets()}

        self.assertEqual(datasets["ifeval"]["hf_repo"], "google/IFEval")
        self.assertEqual(datasets["ifeval"]["license"], "apache-2.0")
        self.assertEqual(datasets["mrcr"]["hf_repo"], "openai/mrcr")
        self.assertEqual(datasets["mrcr"]["license"], "mit")
        self.assertEqual(datasets["graphwalks"]["hf_repo"], "openai/graphwalks")
        self.assertEqual(datasets["graphwalks"]["license"], "mit")

    def test_builds_ifeval_case_with_full_prompt_parts(self) -> None:
        case = correctness.build_case(
            "ifeval",
            {
                "key": 1001,
                "prompt": "Write one sentence. Do not use commas.",
                "instruction_id_list": ["punctuation:no_comma"],
                "kwargs": [{}],
            },
        )

        self.assertEqual(case["case_id"], "ifeval-1001")
        self.assertIn("instruction-following assistant", case["stable_prefix"])
        self.assertEqual(case["tail_prompt"], "Write one sentence. Do not use commas.")
        self.assertIn(case["tail_prompt"], case["full_prompt"])

    def test_scores_supported_ifeval_instruction_checks(self) -> None:
        case = correctness.build_case(
            "ifeval",
            {
                "key": 7,
                "prompt": "Avoid commas and write at least 3 words.",
                "instruction_id_list": ["punctuation:no_comma", "length_constraints:number_words"],
                "kwargs": [{}, {"relation": "at least", "num_words": 3}],
            },
        )

        score = correctness.score_response(case, "Three plain words")

        self.assertEqual(score.score, 1.0)
        self.assertTrue(score.passed)
        self.assertEqual(score.unsupported_checks, [])

    def test_records_unsupported_ifeval_checks(self) -> None:
        case = correctness.build_case(
            "ifeval",
            {
                "key": 8,
                "prompt": "Use a custom unsupported format.",
                "instruction_id_list": ["custom:unknown"],
                "kwargs": [{}],
            },
        )

        score = correctness.score_response(case, "answer")

        self.assertIsNone(score.score)
        self.assertIsNone(score.passed)
        self.assertEqual(score.unsupported_checks, ["custom:unknown"])

    def test_builds_and_scores_mrcr_case(self) -> None:
        row = {
            "prompt": (
                '[{"role": "user", "content": "Context A"}, '
                '{"role": "assistant", "content": "Reply A"}, '
                '{"role": "user", "content": "Return the second poem"}]'
            ),
            "answer": "ABCThe matching poem",
            "random_string_to_prepend": "ABC",
            "desired_msg_index": 2,
        }
        case = correctness.build_case("mrcr", row, index=0)

        self.assertIn("ASSISTANT:", case["stable_prefix"])
        self.assertIn("Return the second poem", case["tail_prompt"])

        score = correctness.score_response(case, "ABCThe matching poem")

        self.assertEqual(score.score, 1.0)
        self.assertTrue(score.passed)

    def test_builds_and_scores_graphwalks_case(self) -> None:
        row = {
            "prompt": (
                "You will be given a graph.\n"
                "The graph has the following edges:\n"
                "aa -> bb\n"
                "aa -> cc\n"
                "\nOperation:\n"
                "Perform a BFS from node aa with depth 1.\n"
                "Final Answer:"
            ),
            "answer_nodes": ["bb", "cc"],
            "problem_type": "bfs",
        }
        case = correctness.build_case("graphwalks", row, index=3)

        self.assertIn("aa -> bb", case["stable_prefix"])
        self.assertTrue(case["tail_prompt"].startswith("Operation:"))

        score = correctness.score_response(case, 'Final Answer: ["bb", "cc"]')

        self.assertEqual(score.score, 1.0)
        self.assertTrue(score.passed)
        self.assertEqual(score.metrics["precision"], 1.0)
        self.assertEqual(score.metrics["recall"], 1.0)

    def test_score_response_pairs_reports_mode_delta(self) -> None:
        case = correctness.build_case(
            "graphwalks",
            {
                "prompt": "Graph\nOperation:\nFind nodes.",
                "answer_nodes": ["a", "b"],
            },
        )
        result = correctness.score_response_pairs(
            [case],
            [
                {"case_id": case["case_id"], "mode": "full", "response": '["a", "b"]', "latency_ms": 10.0},
                {"case_id": case["case_id"], "mode": "session-tail", "response": '["a"]', "latency_ms": 4.0},
            ],
        )

        case_result = result["cases"][0]
        self.assertEqual(case_result["scores"]["full"]["score"], 1.0)
        self.assertAlmostEqual(case_result["scores"]["session-tail"]["score"], 2 / 3)
        self.assertAlmostEqual(case_result["session_tail_minus_full_score"], -1 / 3)
        self.assertEqual(case_result["latency_ms"]["session-tail"], 4.0)
        self.assertEqual(result["summary"]["full"]["mean_score"], 1.0)

    def test_parse_error_scores_as_failed_generation(self) -> None:
        case = correctness.build_case(
            "ifeval",
            {
                "key": 11,
                "prompt": "Do not use commas.",
                "instruction_id_list": ["punctuation:no_comma"],
                "kwargs": [{}],
            },
        )
        result = correctness.score_response_pairs(
            [case],
            [
                {
                    "case_id": case["case_id"],
                    "mode": "session-tail",
                    "response": "No comma here",
                    "answer_parse_error": "invalid JSON",
                },
            ],
        )

        score = result["cases"][0]["scores"]["session-tail"]
        self.assertEqual(score["score"], 0.0)
        self.assertFalse(score["passed"])
        self.assertEqual(score["metrics"]["answer_parse_error"], "invalid JSON")

    def test_selected_run_modes_expands_both(self) -> None:
        self.assertEqual(correctness.selected_run_modes("full"), ["full"])
        self.assertEqual(correctness.selected_run_modes("session-tail"), ["session-tail"])
        self.assertEqual(correctness.selected_run_modes("live-tail"), ["live-tail"])
        self.assertEqual(correctness.selected_run_modes("both"), ["full", "session-tail"])

    def test_parse_candidate_mix(self) -> None:
        specs = correctness.parse_candidate_mix("ifeval:8,graphwalks:2")

        self.assertEqual([(spec.dataset_id, spec.limit) for spec in specs], [("ifeval", 8), ("graphwalks", 2)])

        with self.assertRaises(correctness.CorrectnessEvalError):
            correctness.parse_candidate_mix("ifeval:0")

    def test_easy_ifeval_filter_limits_to_simple_supported_rows(self) -> None:
        easy_row = {
            "instruction_id_list": ["length_constraints:number_words"],
            "kwargs": [{"num_words": 20}],
        }
        hard_row = {
            "instruction_id_list": ["length_constraints:number_words"],
            "kwargs": [{"num_words": 300}],
        }
        unsupported_row = {
            "instruction_id_list": ["custom:unknown"],
            "kwargs": [{}],
        }

        self.assertTrue(correctness.is_easy_ifeval_row(easy_row))
        self.assertFalse(correctness.is_easy_ifeval_row(hard_row))
        self.assertFalse(correctness.is_easy_ifeval_row(unsupported_row))

    def test_build_candidates_writes_mixed_case_file_with_metadata(self) -> None:
        rows_by_dataset = {
            "ifeval": [
                {
                    "key": 1,
                    "prompt": "Write three words.",
                    "instruction_id_list": ["length_constraints:number_words"],
                    "kwargs": [{"num_words": 3}],
                },
                {
                    "key": 2,
                    "prompt": "Write three hundred words.",
                    "instruction_id_list": ["length_constraints:number_words"],
                    "kwargs": [{"num_words": 300}],
                },
            ],
            "graphwalks": [
                {
                    "prompt": "Graph\nOperation:\nFind nodes.",
                    "answer_nodes": ["a"],
                    "problem_type": "toy",
                }
            ],
        }

        old_loader = correctness.load_remote_rows

        def fake_loader(
            dataset_id: str,
            *,
            limit: int,
            offset: int = 0,
            max_prompt_chars: int | None = None,
            streaming: bool = True,
            row_filter=None,
        ):
            del offset, max_prompt_chars, streaming
            rows = list(rows_by_dataset[dataset_id])
            if row_filter is not None:
                rows = [row for row in rows if row_filter(row)]
            return rows[:limit]

        try:
            correctness.load_remote_rows = fake_loader  # type: ignore[assignment]
            with tempfile.TemporaryDirectory() as tmp_dir:
                output_path = Path(tmp_dir) / "candidates.jsonl"
                args = correctness.parse_args(
                    [
                        "build-candidates",
                        "--mix",
                        "ifeval:2,graphwalks:1",
                        "--profile",
                        "easy",
                        "--output",
                        str(output_path),
                    ]
                )

                exit_code = correctness.command_build_candidates(args)

                self.assertEqual(exit_code, 0)
                records = correctness.read_jsonl(output_path)
                self.assertEqual([record["dataset_id"] for record in records], ["ifeval", "graphwalks"])
                self.assertEqual(records[0]["candidate_builder"]["profile"], "easy")
                self.assertEqual(records[0]["candidate_builder"]["requested_count"], 2)
        finally:
            correctness.load_remote_rows = old_loader  # type: ignore[assignment]

    def test_dry_run_record_has_response_jsonl_shape(self) -> None:
        args = correctness.parse_args(["run", "--cases", "cases.jsonl", "--dry-run"])
        case = correctness.build_case(
            "ifeval",
            {
                "key": 10,
                "prompt": "Write three words.",
                "instruction_id_list": ["length_constraints:number_words"],
                "kwargs": [{"num_words": 3}],
            },
        )

        record = correctness.build_dry_run_record(args, case, "session-tail")

        self.assertEqual(record["case_id"], "ifeval-10")
        self.assertEqual(record["mode"], "session-tail")
        self.assertEqual(record["answer_protocol"], "raw")
        self.assertIsNone(record["answer_hint_id"])
        self.assertEqual(record["response"], "")
        self.assertEqual(record["raw_response"], "")
        self.assertEqual(record["answer_parse_error"], "dry-run has no model response")
        self.assertTrue(record["dry_run"])
        self.assertIn("completion_prompt_sha256", record)
        self.assertTrue(record["session_setup"]["dry_run"])

    def test_json_answer_protocol_wraps_prompt_and_extracts_answer(self) -> None:
        case = correctness.build_case(
            "graphwalks",
            {
                "prompt": "Graph\nOperation:\nFind nodes.",
                "answer_nodes": ["a"],
            },
        )

        stable_prefix, tail_prompt, full_prompt = correctness.protocol_case_parts(case, "json-answer")
        response, parse_error = correctness.extract_protocol_response('{"answer": "[\\"a\\"]"}', "json-answer")

        self.assertIn("Return only a JSON object", stable_prefix)
        self.assertIn("GraphWalks task", stable_prefix)
        self.assertEqual(tail_prompt, case["tail_prompt"])
        self.assertIn(case["tail_prompt"], full_prompt)
        self.assertEqual(correctness.answer_hint_id_for_case(case, "json-answer"), "graphwalks-node-list")
        self.assertIsNone(correctness.answer_hint_id_for_case(case, "raw"))
        self.assertEqual(response, '["a"]')
        self.assertIsNone(parse_error)

    def test_json_answer_dry_run_records_answer_hint_id(self) -> None:
        args = correctness.parse_args(["run", "--cases", "cases.jsonl", "--dry-run", "--answer-protocol", "json-answer"])
        case = correctness.build_case(
            "ifeval",
            {
                "key": 13,
                "prompt": "Do not use commas.",
                "instruction_id_list": ["punctuation:no_comma"],
                "kwargs": [{}],
            },
        )

        record = correctness.build_dry_run_record(args, case, "full")

        self.assertEqual(record["answer_hint_id"], "ifeval-final-answer")

    def test_json_answer_parse_error_preserves_raw_response(self) -> None:
        response, parse_error = correctness.extract_protocol_response("not json", "json-answer")

        self.assertEqual(response, "not json")
        self.assertIn("invalid JSON", str(parse_error))

    def test_llama_completion_accepts_json_schema_payload(self) -> None:
        captured = {}

        def fake_http_json(method: str, url: str, payload: dict[str, object] | None, timeout: float) -> dict[str, object]:
            captured.update({"method": method, "url": url, "payload": payload, "timeout": timeout})
            return {"content": '{"answer":"ok"}', "timings": {}}

        from flashcache import llama_cpp

        old_http_json = llama_cpp.http_json
        try:
            llama_cpp.http_json = fake_http_json  # type: ignore[assignment]
            client = llama_cpp.LlamaClient("http://127.0.0.1:8080")
            client.completion(
                "prompt",
                n_predict=8,
                temperature=0,
                json_schema=correctness.ANSWER_JSON_SCHEMA,
            )
        finally:
            llama_cpp.http_json = old_http_json

        self.assertEqual(captured["payload"]["json_schema"], correctness.ANSWER_JSON_SCHEMA)

    def test_run_dry_run_writes_responses_and_optional_scores(self) -> None:
        case = correctness.build_case(
            "graphwalks",
            {
                "prompt": "Graph\nOperation:\nFind nodes.",
                "answer_nodes": [],
            },
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cases_path = tmp_path / "cases.jsonl"
            responses_path = tmp_path / "responses.jsonl"
            score_path = tmp_path / "scores.json"
            correctness.write_jsonl([case], cases_path)
            args = correctness.parse_args(
                [
                    "run",
                    "--cases",
                    str(cases_path),
                    "--dry-run",
                    "--score",
                    "--output",
                    str(responses_path),
                    "--score-output",
                    str(score_path),
                ]
            )

            exit_code = correctness.command_run(args)

            self.assertEqual(exit_code, 0)
            responses = correctness.read_jsonl(responses_path)
            self.assertEqual([record["mode"] for record in responses], ["full", "session-tail"])
            score = json.loads(score_path.read_text(encoding="utf-8"))
            self.assertEqual(score["metadata"]["response_count"], 2)

    def test_live_tail_case_primes_without_slot_save_or_restore(self) -> None:
        case = correctness.build_case(
            "graphwalks",
            {
                "prompt": "Graph\nOperation:\nFind nodes.",
                "answer_nodes": ["a"],
            },
        )
        args = correctness.parse_args(
            [
                "run",
                "--cases",
                "cases.jsonl",
                "--mode",
                "live-tail",
                "--answer-protocol",
                "json-answer",
            ]
        )
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
                return {"content": '{"answer":"[\\"a\\"]"}', "timings": {"prompt_ms": 2.0}}

            def save_slot(self, filename):
                raise AssertionError(f"live-tail should not save slot {filename}")

            def restore_slot(self, filename):
                raise AssertionError(f"live-tail should not restore slot {filename}")

        class FakeManagedServer:
            def __init__(self, config, label="flashcache"):
                self.config = config
                self.label = label

            def __enter__(self):
                return FakeClient()

            def __exit__(self, exc_type, exc, tb):
                return None

        old_server = correctness.ManagedLlamaServer
        try:
            correctness.ManagedLlamaServer = FakeManagedServer  # type: ignore[assignment]
            record = correctness.run_live_tail_case(args, case)
        finally:
            correctness.ManagedLlamaServer = old_server  # type: ignore[assignment]

        self.assertEqual(record["mode"], "live-tail")
        self.assertEqual(record["response"], '["a"]')
        self.assertEqual(len(calls), 2)
        self.assertFalse(calls[0]["cache_prompt"])
        self.assertTrue(calls[1]["cache_prompt"])
        self.assertIsNone(calls[0]["json_schema"])
        self.assertEqual(calls[1]["json_schema"], correctness.ANSWER_JSON_SCHEMA)
        self.assertIsNone(record["session_setup"]["save_response"])
        self.assertIsNone(record["session_setup"]["restore_response"])

    def test_selects_cases_by_full_score_threshold(self) -> None:
        score_result = {
            "cases": [
                {"case_id": "a", "scores": {"full": {"score": 1.0}}},
                {"case_id": "b", "scores": {"full": {"score": 0.5}}},
                {"case_id": "c", "scores": {"session-tail": {"score": 1.0}}},
            ]
        }

        self.assertEqual(correctness.selected_case_ids(score_result, min_score=1.0), ["a"])
        self.assertEqual(correctness.selected_case_ids(score_result, min_score=0.5), ["a", "b"])

    def test_filters_cases_and_responses_by_selected_ids(self) -> None:
        cases = [{"case_id": "a"}, {"case_id": "b"}]
        responses = [
            {"case_id": "a", "mode": "full"},
            {"case_id": "a", "mode": "session-tail"},
            {"case_id": "b", "mode": "full"},
        ]

        self.assertEqual(correctness.filter_cases_by_id(cases, ["a"]), [{"case_id": "a"}])
        self.assertEqual(
            correctness.filter_responses_by_id(responses, ["a"], mode="full"),
            [{"case_id": "a", "mode": "full"}],
        )

    def test_baseline_ladder_dry_run_reports_zero_selected_cases(self) -> None:
        case = correctness.build_case(
            "ifeval",
            {
                "key": 12,
                "prompt": "Do not use commas.",
                "instruction_id_list": ["punctuation:no_comma"],
                "kwargs": [{}],
            },
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cases_path = tmp_path / "cases.jsonl"
            output_dir = tmp_path / "out"
            correctness.write_jsonl([case], cases_path)
            args = correctness.parse_args(
                [
                    "baseline-ladder",
                    "--cases",
                    str(cases_path),
                    "--output-dir",
                    str(output_dir),
                    "--label",
                    "dry",
                    "--dry-run",
                ]
            )

            exit_code = correctness.command_baseline_ladder(args)

            self.assertEqual(exit_code, 0)
            report = json.loads((output_dir / "dry-ladder-report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["metadata"]["candidate_case_count"], 1)
            self.assertEqual(report["metadata"]["selected_case_count"], 0)
            self.assertTrue((output_dir / "dry-full-responses.jsonl").exists())
            self.assertEqual((output_dir / "dry-selected-cases.jsonl").read_text(encoding="utf-8"), "")


if __name__ == "__main__":
    unittest.main()
