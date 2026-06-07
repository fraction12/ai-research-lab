from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "benchmarks"))

import bfcl_code_mode_kv_adapter as adapter  # noqa: E402
import code_mode_kv_capsule_model_loop_runner as model_runner  # noqa: E402
import code_mode_tool_surface as tool_surface  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


class BFCLCodeModeKVAdapterTests(unittest.TestCase):
    def make_source_dir(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        write_jsonl(
            root / "BFCL_v3_simple.json",
            [
                {
                    "id": "simple_0",
                    "question": [[{"role": "user", "content": "Find the area of a triangle."}]],
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
            root / "possible_answer" / "BFCL_v3_simple.json",
            [
                {
                    "id": "simple_0",
                    "ground_truth": [{"calculate_triangle_area": {"base": [10], "height": [5]}}],
                }
            ],
        )
        write_jsonl(
            root / "BFCL_v3_parallel.json",
            [
                {
                    "id": "parallel_0",
                    "question": [[{"role": "user", "content": "Play two songs."}]],
                    "function": [
                        {
                            "name": "spotify.play",
                            "description": "Play music.",
                            "parameters": {"type": "dict", "properties": {}},
                        }
                    ],
                }
            ],
        )
        write_jsonl(
            root / "possible_answer" / "BFCL_v3_parallel.json",
            [
                {
                    "id": "parallel_0",
                    "ground_truth": [
                        {"spotify.play": {"artist": ["Taylor Swift"], "duration": [20]}},
                        {"spotify.play": {"artist": ["Maroon 5"], "duration": [15]}},
                    ],
                }
            ],
        )
        write_jsonl(
            root / "BFCL_v3_irrelevance.json",
            [
                {
                    "id": "irrelevance_0",
                    "question": [[{"role": "user", "content": "Calculate triangle area."}]],
                    "function": [
                        {
                            "name": "determine_body_mass_index",
                            "description": "Calculate BMI.",
                            "parameters": {"type": "dict", "properties": {}},
                        }
                    ],
                }
            ],
        )
        write_jsonl(
            root / "BFCL_v3_multi_turn_base.json",
            [
                {
                    "id": "multi_turn_base_0",
                    "question": [
                        [{"role": "user", "content": "Move final_report.pdf into temp."}],
                        [{"role": "user", "content": "Search it for budget analysis."}],
                    ],
                    "initial_config": {
                        "GorillaFileSystem": {
                            "root": {"workspace": {"type": "directory", "contents": {}}},
                        }
                    },
                    "path": [
                        "GorillaFileSystem.cd",
                        "GorillaFileSystem.mkdir",
                        "GorillaFileSystem.mv",
                        "GorillaFileSystem.grep",
                    ],
                    "involved_classes": ["GorillaFileSystem"],
                }
            ],
        )
        write_jsonl(
            root / "possible_answer" / "BFCL_v3_multi_turn_base.json",
            [
                {
                    "id": "multi_turn_base_0",
                    "ground_truth": [
                        [
                            "cd(folder='document')",
                            "mkdir(dir_name='temp')",
                            "mv(source='final_report.pdf', destination='temp')",
                        ],
                        ["cd(folder='temp')", "grep(file_name='final_report.pdf',pattern='budget analysis')"],
                    ],
                }
            ],
        )
        write_jsonl(
            root / "BFCL_v3_rest.json",
            [
                {
                    "id": "rest_0",
                    "question": [{"role": "user", "content": "Get pet 123."}],
                    "function": [
                        {
                            "name": "getPetById",
                            "description": "Find pet by id.",
                            "parameters": {"type": "dict", "properties": {"petId": {"type": "integer"}}},
                        }
                    ],
                }
            ],
        )
        return root

    def test_materializes_control_packets_with_provenance_and_required_fields(self) -> None:
        source_dir = self.make_source_dir()

        cases = adapter.materialize_cases(
            source_dir=source_dir,
            categories=["simple", "parallel", "irrelevance"],
            per_category=1,
        )
        packets = adapter.materialize_control_packets(cases)

        self.assertEqual(len(cases), 3)
        self.assertEqual(len(packets), 3 * len(adapter.CONTROL_IDS))
        first = packets[0]
        self.assertEqual(first["source_provenance"]["benchmark_id"], "BFCL")
        self.assertEqual(first["source_provenance"]["dataset_revision"], adapter.BFCL_DATASET_REVISION)
        self.assertEqual(first["eligibility"]["primary_eligible"], False)
        self.assertEqual(
            first["eligibility"]["primary_eligibility_reason"],
            "pending_code_mode_full_visible_calibration",
        )
        self.assertIn("prefix_dependency_class", first["eligibility"])
        self.assertIn("expected_call_hash", first)
        self.assertIn("expected_argument_hash", first)
        self.assertIn("source_fields_used", first["source_provenance"])
        self.assertIn("host_filled_args", first["host_boundary"])
        self.assertIn(adapter.BFCL_DATASET_REVISION, adapter.REMOTE_BASE)
        self.assertNotIn("/raw/main", adapter.REMOTE_BASE)
        self.assertFalse(first["scoring"]["native_bfcl_scorer_used"])

    def test_control_visibility_preserves_tail_only_for_restored_and_fresh_controls(self) -> None:
        source_dir = self.make_source_dir()
        case = adapter.materialize_cases(source_dir=source_dir, categories=["simple"], per_category=1)[0]

        full = adapter.control_packet(case, "code_mode_full_visible")
        restored = adapter.control_packet(case, "code_mode_restored_kv_capsule")
        fresh = adapter.control_packet(case, "code_mode_fresh_tail_only")
        compact = adapter.control_packet(case, "compact_visible_evidence_code_mode")

        self.assertIn("TOOL/FUNCTION CATALOG", full["visible_prompt"])
        self.assertNotIn("TOOL/FUNCTION CATALOG", restored["visible_prompt"])
        self.assertNotIn("TOOL/FUNCTION CATALOG", fresh["visible_prompt"])
        self.assertIn("VISIBLE FUNCTION EVIDENCE", compact["visible_prompt"])
        self.assertFalse(fresh["expected_to_pass"])
        self.assertEqual(
            adapter.control_packet(case, "code_mode_wrong_capsule_negative")["wrong_capsule"]["mismatch_rationale"],
            "runner_must_restore_prefix_from_a_different_bfcl_case",
        )

    def test_scores_single_parallel_and_no_call_cases(self) -> None:
        expected_single = [{"name": "calculate_triangle_area", "arguments": {"base": [10], "height": [5]}}]
        parsed_single = [{"name": "calculate_triangle_area", "arguments": {"base": 10, "height": 5}}]
        self.assertTrue(adapter.score_calls(expected_single, parsed_single)["passed"])

        expected_parallel = [
            {"name": "spotify.play", "arguments": {"artist": ["Taylor Swift"], "duration": [20]}},
            {"name": "spotify.play", "arguments": {"artist": ["Maroon 5"], "duration": [15]}},
        ]
        parsed_parallel_reordered = [
            {"name": "spotify.play", "arguments": {"artist": "Maroon 5", "duration": 15}},
            {"name": "spotify.play", "arguments": {"artist": "Taylor Swift", "duration": 20}},
        ]
        self.assertTrue(adapter.score_calls(expected_parallel, parsed_parallel_reordered)["passed"])

        parsed_with_formatting_space = [
            {"name": "spotify.play", "arguments": {"artist": " Taylor Swift", "duration": 20}},
            {"name": "spotify.play", "arguments": {"artist": " Maroon 5", "duration": 15}},
        ]
        self.assertTrue(adapter.score_calls(expected_parallel, parsed_with_formatting_space)["passed"])

        self.assertTrue(adapter.score_calls([], [])["passed"])
        self.assertFalse(adapter.score_calls([], [{"name": "irrelevant.call", "arguments": {}}])["passed"])

    def test_materializes_multi_turn_string_ground_truth_and_synthesized_tool_catalog(self) -> None:
        source_dir = self.make_source_dir()

        case = adapter.materialize_cases(source_dir=source_dir, categories=["multi_turn_base"], per_category=1)[0]
        packet = adapter.control_packet(case, "code_mode_full_visible")

        self.assertEqual(case.scorer_mode, "multi_turn_expected_call_match")
        self.assertEqual([call["name"] for call in case.expected_calls], ["cd", "mkdir", "mv", "cd", "grep"])
        self.assertEqual(case.expected_calls[0]["arguments"], {"folder": ["document"]})
        self.assertIn("Move final_report.pdf", packet["tail_prompt"])
        self.assertIn("Search it for budget analysis", packet["tail_prompt"])
        self.assertIn("initial_config", packet["source_provenance"]["source_fields_used"])
        self.assertIn("GorillaFileSystem.mkdir", [tool["name"] for tool in case.functions])
        self.assertTrue(
            adapter.score_calls(
                [{"name": "mkdir", "arguments": {"dir_name": ["temp"]}}],
                [{"name": "GorillaFileSystem.mkdir", "arguments": {"dir_name": "temp"}}],
            )["passed"]
        )

    def test_live_or_api_rows_without_possible_answers_are_diagnostic_only_not_no_call(self) -> None:
        source_dir = self.make_source_dir()

        case = adapter.materialize_cases(source_dir=source_dir, categories=["rest"], per_category=1)[0]
        packet = adapter.control_packet(case, "code_mode_full_visible")

        self.assertEqual(case.expected_calls, [])
        self.assertEqual(case.scorer_mode, "unsupported_missing_possible_answer")
        self.assertIn("missing_possible_answer", packet["scoring"]["unsupported_scorer_features"])
        self.assertEqual(packet["eligibility"]["primary_eligibility_reason"], "diagnostic_only_missing_possible_answer")
        self.assertFalse(adapter.primary_selection_status(packet)["primary_ready"])

    def test_compatibility_audit_reports_scoreable_and_diagnostic_categories(self) -> None:
        source_dir = self.make_source_dir()
        cases = adapter.materialize_cases(
            source_dir=source_dir,
            categories=["simple", "multi_turn_base", "rest"],
            per_category=1,
        )
        audit = adapter.compatibility_audit(cases)

        self.assertEqual(audit["status"], "bfcl_compatibility_audit_passed")
        self.assertEqual(audit["category_count"], 3)
        self.assertEqual(audit["scoreable_case_count"], 2)
        self.assertEqual(audit["diagnostic_only_case_count"], 1)
        self.assertIn("rest", audit["diagnostic_only_categories"])

    def test_scores_nested_bfcl_expected_argument_options(self) -> None:
        expected_budget = [
            {
                "name": "realestate.find_properties",
                "arguments": {
                    "bedrooms": [3],
                    "budget": [{"max": [400000], "min": [300000]}],
                    "location": ["SD", "San Diego", "San Diego, CA", "CA"],
                    "propertyType": ["villa"],
                },
            }
        ]
        parsed_budget = [
            {
                "name": "realestate.find_properties",
                "arguments": {
                    "bedrooms": 3,
                    "budget": {"max": 400000.0, "min": 300000.0},
                    "location": "San Diego",
                    "propertyType": "villa",
                },
            }
        ]
        self.assertTrue(adapter.score_calls(expected_budget, parsed_budget)["passed"])

        expected_grades = [
            {
                "name": "calculate_average",
                "arguments": {"gradeDict": [{"history": [82], "math": [90], "music": [89], "science": [75]}]},
            }
        ]
        parsed_grades = [
            {
                "name": "calculate_average",
                "arguments": {"gradeDict": {"history": 82, "math": 90, "music": 89, "science": 75}},
            }
        ]
        self.assertTrue(adapter.score_calls(expected_grades, parsed_grades)["passed"])

    def test_optional_expected_argument_omission_is_allowed_but_required_omission_fails(self) -> None:
        expected = [
            {
                "name": "triangle_properties.get",
                "arguments": {
                    "side1": [5],
                    "side2": [4],
                    "side3": [3],
                    "get_area": ["", True],
                    "get_perimeter": ["", True],
                    "get_angles": ["", True],
                },
            }
        ]
        parsed = [{"name": "triangle_properties.get", "arguments": {"side1": 5, "side2": 4, "side3": 3}}]
        self.assertTrue(adapter.score_calls(expected, parsed)["passed"])

        required_missing = [
            {"name": "triangle_properties.get", "arguments": {"side1": [5], "side2": [4], "side3": [3]}}
        ]
        self.assertFalse(
            adapter.score_calls(required_missing, [{"name": "triangle_properties.get", "arguments": {"side1": 5}}])[
                "passed"
            ]
        )

    def test_parses_common_json_call_shapes(self) -> None:
        calls = adapter.parse_calls_from_json_text(
            '{"calls":[{"name":"calculate_triangle_area","arguments":{"base":10,"height":5}}]}'
        )
        self.assertEqual(calls[0]["name"], "calculate_triangle_area")

        dict_call = adapter.parse_calls_from_json_text('{"calculate_triangle_area":{"base":10,"height":5}}')
        self.assertEqual(dict_call[0]["arguments"]["base"], 10)

        generated = (
            "\n<|channel>thought\n<channel|>```json\n"
            '{"tool_calls":[{"function_name":"calculate_triangle_area",'
            '"arguments":{"base":10,"height":5}}]}\n```'
        )
        generated_calls = adapter.parse_calls_from_generated_text(generated)
        self.assertEqual(adapter.actual_call_name(generated_calls[0]), "calculate_triangle_area")
        self.assertEqual(adapter.actual_call_arguments(generated_calls[0])["height"], 5)
        self.assertTrue(
            adapter.score_calls(
                [{"name": "calculate_triangle_area", "arguments": {"base": [10], "height": [5]}}],
                generated_calls,
            )["passed"]
        )

        openai_shape = adapter.parse_calls_from_generated_text(
            '{"tool_calls":[{"function":{"name":"calculate_triangle_area",'
            '"arguments":"{\\"base\\":10,\\"height\\":5}"}}]}'
        )
        self.assertTrue(
            adapter.score_calls(
                [{"name": "calculate_triangle_area", "arguments": {"base": [10], "height": [5]}}],
                openai_shape,
            )["passed"]
        )

    def test_parses_observed_model_json_call_shapes(self) -> None:
        action_input = adapter.parse_calls_from_generated_text(
            '{"action":"calculate_em_force","action_input":{"charge1":12,"charge2":10,"distance":5}}\n'
            '{"action":"calculate_em_force","action_input":{"charge1":12,"charge2":12,"distance":5}}'
        )
        self.assertEqual([adapter.actual_call_name(call) for call in action_input], ["calculate_em_force"] * 2)
        self.assertEqual(adapter.actual_call_arguments(action_input[1])["charge2"], 12)

        action_parameters = adapter.parse_calls_from_generated_text(
            '{"action":"math_toolkit.sum_of_multiples","parameters":{"number":1000,"multiple":3}}\n'
            '{"action":"math_toolkit.product_of_primes","parameters":{"primes":[2,3,5]}}'
        )
        self.assertEqual(
            [adapter.actual_call_name(call) for call in action_parameters],
            ["math_toolkit.sum_of_multiples", "math_toolkit.product_of_primes"],
        )

        plan = adapter.parse_calls_from_generated_text(
            '{"plan":[{" function":"spotify.play"," arguments":{" artist":"Taylor Swift","duration":20}},'
            '{" function_call":{" name":"spotify.play"," arguments":{" artist":"Maroon 5","duration":15}}}]}'
        )
        self.assertEqual([adapter.actual_call_name(call) for call in plan], ["spotify.play", "spotify.play"])
        self.assertEqual(adapter.actual_call_arguments(plan[0])["artist"], "Taylor Swift")
        self.assertEqual(adapter.actual_call_arguments(plan[1])["artist"], "Maroon 5")

        native_calls = adapter.parse_calls_from_generated_text(
            '<|tool_call>call:spotify.play{artist: "Taylor Swift", duration: 20}<tool_call|>'
            '<|tool_call>call:spotify.play{artist: " Maroon 5", duration: 15}<tool_call|>'
        )
        self.assertEqual([adapter.actual_call_name(call) for call in native_calls], ["spotify.play", "spotify.play"])
        self.assertTrue(
            adapter.score_calls(
                [
                    {"name": "spotify.play", "arguments": {"artist": ["Taylor Swift"], "duration": [20]}},
                    {"name": "spotify.play", "arguments": {"artist": ["Maroon 5"], "duration": [15]}},
                ],
                native_calls,
            )["passed"]
        )

        capitalized_wrapper = adapter.parse_calls_from_generated_text(
            '{"tool_calls":[{"Function_name":"area_circle.calculate","arguments":{"radius":5.0}}]}'
        )
        self.assertEqual(adapter.actual_call_name(capitalized_wrapper[0]), "area_circle.calculate")
        self.assertEqual(adapter.actual_call_arguments(capitalized_wrapper[0])["radius"], 5)

        doubled_quote_keys = adapter.parse_calls_from_generated_text(
            '<|channel>thought\n<channel|>```json\n'
            '{"tool_calls": [{""name"": "math_roots.quadratic", '
            '"arguments"": {""a"": 5, "b"": 20, "c"": -25}}]}\n```'
        )
        self.assertEqual(adapter.actual_call_name(doubled_quote_keys[0]), "math_roots.quadratic")
        self.assertEqual(adapter.actual_call_arguments(doubled_quote_keys[0]), {"a": 5, "b": 20, "c": -25})

        truncated_outer_wrapper = adapter.parse_calls_from_generated_text(
            '<|channel>thought\n<channel|>```json\n'
            '{"tool_calls": [{"function_name": "realestate.find_properties", '
            '"arguments": {"location": "San Diego", "propertyType": "villa", "bedrooms": 3, '
            '"budget": {"min": 300000.0, "max": 400000.0}}\n```'
        )
        self.assertEqual(adapter.actual_call_name(truncated_outer_wrapper[0]), "realestate.find_properties")
        self.assertEqual(adapter.actual_call_arguments(truncated_outer_wrapper[0])["budget"]["max"], 400000)

        truncated_doubled_quote_wrapper = adapter.parse_calls_from_generated_text(
            '<|channel>thought\n<channel|>```json\n'
            '{"tool_calls": [{""function_name"": "calculate_average", '
            '""arguments"": {""gradeDict"": {""math"": 90, ""science"": 75}}'
        )
        self.assertEqual(adapter.actual_call_name(truncated_doubled_quote_wrapper[0]), "calculate_average")
        self.assertEqual(adapter.actual_call_arguments(truncated_doubled_quote_wrapper[0])["gradeDict"]["science"], 75)

    def test_stable_prefix_contains_pti_v3_contract(self) -> None:
        case = adapter.materialize_cases(source_dir=self.make_source_dir(), categories=["simple"], per_category=1)[0]
        prefix = adapter.stable_prefix(case, code_mode=True)

        self.assertIn("PTI protocol version = bfcl_programmatic_tool_interface_v3", prefix)
        self.assertIn("If no provided function can satisfy the user request, output an empty call list", prefix)
        self.assertIn("Count the independent operations requested by the user before emitting calls", prefix)
        self.assertIn("Do not emit helper, search, validation, explanation, or planning calls", prefix)
        self.assertIn("Use function names and parameter names exactly as written in the catalog", prefix)
        self.assertIn("Omit optional/default parameters unless the user request clearly specifies them", prefix)
        self.assertIn("PTI v3 repair boundary", prefix)

        packet = adapter.control_packet(case, "code_mode_full_visible")
        self.assertEqual(packet["pti_runtime"]["schema_validator_version"], "bfcl_pti_schema_validator_v3")
        self.assertEqual(packet["pti_runtime"]["repair_prompt_version"], "bfcl_pti_schema_only_repair_prompt_v1")

    def test_schema_validator_uses_visible_catalog_without_expected_answers(self) -> None:
        functions = [
            {
                "name": "calculate_triangle_area",
                "description": "Calculate triangle area.",
                "parameters": {
                    "type": "dict",
                    "properties": {
                        "base": {"type": "integer"},
                        "height": {"type": "integer"},
                        "units": {"type": "string"},
                    },
                    "required": ["base", "height"],
                },
            }
        ]

        valid = adapter.validate_pti_calls_against_catalog(
            functions,
            [{"name": "calculate_triangle_area", "arguments": {"base": 10, "height": 5}}],
        )
        self.assertTrue(valid["valid"])
        self.assertEqual(valid["error_count"], 0)
        self.assertNotIn("expected", json.dumps(valid).lower())
        self.assertNotIn("possible_answer", json.dumps(valid).lower())

        invalid = adapter.validate_pti_calls_against_catalog(
            functions,
            [
                {"name": "missing.fn", "arguments": {}},
                {"name": "calculate_triangle_area", "arguments": {"base": "10", "colour": "blue"}},
            ],
        )
        self.assertFalse(invalid["valid"])
        codes = {error["code"] for error in invalid["errors"]}
        self.assertIn("unknown_function", codes)
        self.assertIn("missing_required_argument", codes)
        self.assertIn("unexpected_argument", codes)
        self.assertIn("type_mismatch", codes)

    def test_pti_v3_canonicalizes_schema_referenced_function_names(self) -> None:
        functions = [
            {"name": "GorillaFileSystem.mkdir", "parameters": {"type": "dict", "properties": {}}},
            {"name": "GorillaFileSystem.mv", "parameters": {"type": "dict", "properties": {}}},
        ]

        valid = adapter.validate_pti_calls_against_catalog(
            functions,
            [{"name": "mkdir", "arguments": {}}],
            user_request="Make a temp directory.",
        )
        self.assertTrue(valid["valid"])
        self.assertEqual(valid["canonical_calls"][0]["name"], "GorillaFileSystem.mkdir")
        self.assertEqual(valid["canonical_calls"][0]["source_name"], "mkdir")
        self.assertIn("function_suffix_match", valid["canonical_calls"][0]["normalizations"])

        ambiguous = adapter.validate_pti_calls_against_catalog(
            [
                {"name": "A.lookup", "parameters": {"type": "dict", "properties": {}}},
                {"name": "B.lookup", "parameters": {"type": "dict", "properties": {}}},
            ],
            [{"name": "lookup", "arguments": {}}],
            user_request="Run lookup.",
        )
        self.assertFalse(ambiguous["valid"])
        self.assertIn("ambiguous_function", {error["code"] for error in ambiguous["errors"]})

    def test_pti_v3_reports_call_count_without_expected_answers(self) -> None:
        functions = [
            {
                "name": "draw_shape",
                "description": "Draw one shape.",
                "parameters": {"type": "dict", "properties": {"shape": {"type": "string"}}},
            }
        ]

        result = adapter.validate_pti_calls_against_catalog(
            functions,
            [{"name": "draw_shape", "arguments": {"shape": "rectangle"}}],
            user_request="Draw a rectangle and a circle.",
        )
        self.assertFalse(result["valid"])
        mismatch = [error for error in result["errors"] if error["code"] == "likely_call_count_mismatch"]
        self.assertEqual(mismatch[0]["expected_min_calls"], 2)
        self.assertNotIn("expected_calls", json.dumps(result))
        self.assertNotIn("possible_answer", json.dumps(result))

    def test_pti_v3_reports_identifier_literal_paraphrase(self) -> None:
        functions = [
            {
                "name": "register_callback",
                "description": "Register a callback function.",
                "parameters": {
                    "type": "dict",
                    "properties": {
                        "callbackName": {
                            "type": "string",
                            "description": "Exact callback function identifier.",
                        }
                    },
                    "required": ["callbackName"],
                },
            }
        ]

        result = adapter.validate_pti_calls_against_catalog(
            functions,
            [{"name": "register_callback", "arguments": {"callbackName": "processing function"}}],
            user_request="Register processFunction as the callback.",
        )
        self.assertFalse(result["valid"])
        literal_errors = [error for error in result["errors"] if error["code"] == "literal_preservation_suspect"]
        self.assertEqual(literal_errors[0]["candidate_literal"], "processFunction")

    def test_pti_v3_validates_nested_schema_shapes(self) -> None:
        functions = [
            {
                "name": "search_properties",
                "parameters": {
                    "type": "dict",
                    "properties": {
                        "budget": {
                            "type": "object",
                            "properties": {
                                "min": {"type": "integer"},
                                "max": {"type": "integer"},
                            },
                        },
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                },
            }
        ]

        result = adapter.validate_pti_calls_against_catalog(
            functions,
            [{"name": "search_properties", "arguments": {"budget": {"min": "300000"}, "tags": "villa"}}],
            user_request="Find villa properties between 300000 and 400000.",
        )
        self.assertFalse(result["valid"])
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("nested_type_mismatch", codes)
        self.assertIn("type_mismatch", codes)

    def test_pti_v3_repair_prompt_is_schema_only(self) -> None:
        functions = [
            {
                "name": "draw_shape",
                "parameters": {"type": "dict", "properties": {"shape": {"type": "string"}}},
            }
        ]
        validation = adapter.validate_pti_calls_against_catalog(
            functions,
            [{"name": "draw_shape", "arguments": {"shape": "rectangle"}}],
            user_request="Draw a rectangle and a circle.",
        )
        prompt = adapter.build_schema_only_repair_prompt(
            user_request="Draw a rectangle and a circle.",
            functions=functions,
            model_output='{"calls":[{"name":"draw_shape","arguments":{"shape":"rectangle"}}]}',
            calls=validation["canonical_calls"],
            validation=validation,
        )

        self.assertIn("VISIBLE FUNCTION CATALOG", prompt)
        self.assertIn("VALIDATOR ERRORS", prompt)
        forbidden = ["possible_answer", "expected_answer", "expected_calls", "ground_truth"]
        for token in forbidden:
            self.assertNotIn(token, prompt)

    def test_tool_surface_runtime_normalizes_dialects_without_expected_answers(self) -> None:
        samples = [
            '{"tool_calls":[{"function_name":"area_circle.calculate","arguments":{"radius":5.0}}]}',
            '{"action":"area_circle.calculate","action_input":{"radius":5.0}}',
            '{"plan":[{" function_call":{" Function_name":"area_circle.calculate"," arguments":{" radius":5.0}}}]}',
            '<|tool_call>call:area_circle.calculate{radius: 5.0}<tool_call|>',
        ]

        identities = []
        for text in samples:
            result = tool_surface.parse_tool_calls_from_text(text)
            self.assertEqual(len(result.calls), 1)
            call = result.calls[0]
            self.assertEqual(call.name, "area_circle.calculate")
            self.assertEqual(call.arguments["radius"], 5)
            self.assertIn(call.source_format, {"tool_calls", "action", "function_call", "gemma_native_call"})
            identities.append(tool_surface.call_identity(call))

        self.assertEqual(len(set(identities)), 1)

    def test_tool_surface_merge_dedupes_retries_but_preserves_distinct_calls(self) -> None:
        existing = [{"name": "spotify.play", "arguments": {"artist": "Taylor Swift", "duration": 20}}]
        repeated = {"function_name": "spotify.play", "arguments": {"artist": " Taylor Swift", "duration": 20}}
        distinct = {"function_name": "spotify.play", "arguments": {"artist": "Maroon 5", "duration": 15}}

        merged = tool_surface.merge_call_candidates(existing, [repeated, distinct])

        self.assertEqual(len(merged), 2)
        self.assertEqual([tool_surface.actual_call_name(call) for call in merged], ["spotify.play", "spotify.play"])

    def test_cli_writes_packet_and_summary(self) -> None:
        source_dir = self.make_source_dir()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "packets.jsonl"
            summary = Path(tmp) / "summary.json"
            exit_code = adapter.main(
                [
                    "--source-dir",
                    str(source_dir),
                    "--category",
                    "simple",
                    "--per-category",
                    "1",
                    "--out",
                    str(out),
                    "--summary-out",
                    str(summary),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(len(out.read_text(encoding="utf-8").splitlines()), len(adapter.CONTROL_IDS))
            summary_data = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(summary_data["status"], "no_model_materialization_complete")
            self.assertEqual(summary_data["case_count"], 1)

    def test_primary_selection_rejects_missing_provenance_and_pending_calibration(self) -> None:
        source_dir = self.make_source_dir()
        case = adapter.materialize_cases(source_dir=source_dir, categories=["simple"], per_category=1)[0]
        packet = adapter.control_packet(case, "code_mode_full_visible")

        status = adapter.primary_selection_status(packet)
        self.assertFalse(status["primary_ready"])
        self.assertIn("pending_code_mode_full_visible_calibration", status["errors"])

        broken = dict(packet)
        broken.pop("source_provenance")
        broken_status = adapter.primary_selection_status(broken)
        self.assertFalse(broken_status["primary_ready"])
        self.assertIn("missing_source_provenance", broken_status["errors"])

    def test_negative_control_passes_are_flagged_as_leakage_or_protocol_failures(self) -> None:
        source_dir = self.make_source_dir()
        case = adapter.materialize_cases(source_dir=source_dir, categories=["simple"], per_category=1)[0]
        fresh = adapter.control_packet(case, "code_mode_fresh_tail_only")
        wrong = adapter.control_packet(case, "code_mode_wrong_capsule_negative")

        self.assertEqual(
            adapter.classify_control_scorer_outcome(fresh, {"passed": True}),
            "fresh_tail_leak_or_non_prefix_dependent",
        )
        self.assertEqual(
            adapter.classify_control_scorer_outcome(wrong, {"passed": True}),
            "wrong_capsule_leak_or_scorer_looseness",
        )
        self.assertEqual(
            adapter.classify_control_scorer_outcome(fresh, {"passed": False}),
            "negative_control_closed",
        )

    def test_model_runner_records_and_scores_bfcl_exec_calls(self) -> None:
        source_dir = self.make_source_dir()
        case = adapter.materialize_cases(source_dir=source_dir, categories=["simple"], per_category=1)[0]
        packet = adapter.control_packet(case, "code_mode_full_visible")

        value = model_runner.execute_bfcl_action(
            {
                "op": "exec",
                "code": (
                    "const result = await tools.call('bfcl:function:calculate_triangle_area', "
                    "{base:10, height:5}); return result;"
                ),
            },
            packet,
            [],
        )
        calls = value["result"]["bfcl_calls"]
        score = adapter.score_calls(packet["expected_calls"], calls)
        record = model_runner.build_record(
            packet,
            {
                "answer_contained": score["passed"],
                "bfcl_score": score,
                "tool_telemetry": {
                    "nested_tool_ids_called": [call["name"] for call in calls],
                    "bfcl_calls": calls,
                    "bfcl_score": score,
                },
                "response": adapter.canonical_json(calls),
                "normalized_response": adapter.canonical_json(calls),
                "response_hash": adapter.sha256_text(adapter.canonical_json(calls)),
                "generated_token_hash": model_runner.token_hash([]),
                "generated_token_count": 0,
                "final_source": "host_bfcl_call_trace",
            },
        )

        self.assertTrue(score["passed"])
        self.assertTrue(record["control_gate_passed"])
        self.assertTrue(record["quality"]["bfcl_score"]["passed"])
        self.assertEqual(record["tool_use"]["called_tool_ids"], ["calculate_triangle_area"])
        self.assertEqual(record["tool_use"]["parsed_call_hash"], score["parsed_call_hash"])

    def test_model_runner_scores_generated_bfcl_tool_calls_json(self) -> None:
        source_dir = self.make_source_dir()
        case = adapter.materialize_cases(source_dir=source_dir, categories=["simple"], per_category=1)[0]
        packet = adapter.control_packet(case, "code_mode_full_visible")
        generated = (
            "\n<|channel>thought\n<channel|>```json\n"
            '{"tool_calls":[{"function_name":"calculate_triangle_area",'
            '"arguments":{"base":10,"height":5}}]}\n```'
        )

        should_stop, reason = model_runner.should_stop_generation(generated, str(packet["expected_answer"]))
        self.assertTrue(should_stop)
        self.assertEqual(reason, "parsed_tool_calls")

        action = model_runner.coerce_bfcl_text_to_action(generated)
        self.assertEqual(action["op"], "bfcl_calls")
        value = model_runner.execute_bfcl_action(action, packet, [])
        self.assertTrue(value["result"]["bfcl_score"]["passed"])
        self.assertEqual(value["exec"]["code_execution_kind"], "bfcl_generated_tool_calls_json")

    def test_model_runner_does_not_stop_bfcl_generation_on_empty_native_call_fragment(self) -> None:
        fragment = "<|channel>thought\n<channel|><|tool_call>call:spotify"

        self.assertEqual(model_runner.should_stop_generation(fragment, "", bfcl_row=True), (False, None))
        self.assertEqual(model_runner.should_stop_generation(fragment, "", bfcl_row=False), (False, None))

    def test_model_runner_coerces_native_bfcl_calls_and_dedupes_retries(self) -> None:
        generated = (
            '<|tool_call>call:spotify.play{artist: "Taylor Swift", duration: 20}<tool_call|>'
            '<|tool_call>call:spotify.play{artist: " Maroon 5", duration: 15}<tool_call|>'
        )
        action = model_runner.coerce_bfcl_text_to_action(generated)

        self.assertEqual(action["op"], "bfcl_calls")
        self.assertEqual(len(action["calls"]), 2)
        merged = model_runner.merge_bfcl_call_candidates(
            [{"name": "spotify.play", "arguments": {"artist": "Taylor Swift", "duration": 20}}],
            action["calls"],
        )
        self.assertEqual(len(merged), 2)

    def test_model_runner_uses_schema_only_bfcl_repair_prompt(self) -> None:
        source_dir = self.make_source_dir()
        case = adapter.materialize_cases(source_dir=source_dir, categories=["parallel"], per_category=1)[0]
        packet = adapter.control_packet(case, "code_mode_full_visible")
        action = {
            "op": "bfcl_calls",
            "calls": [{"name": "spotify.play", "arguments": {"artist": "Taylor Swift", "duration": 20}}],
        }

        validation = model_runner.validate_bfcl_action_schema(packet, action)
        self.assertFalse(validation["valid"])
        self.assertIn("likely_call_count_mismatch", {error["code"] for error in validation["errors"]})

        prompt = model_runner.build_bfcl_schema_repair_prompt(
            packet,
            action,
            '{"tool_calls":[{"function_name":"spotify.play","arguments":{"artist":"Taylor Swift","duration":20}}]}',
        )
        self.assertIn("VALIDATOR ERRORS", prompt)
        self.assertIn("spotify.play", prompt)
        for forbidden in ("possible_answer", "expected_answer", "expected_calls", "ground_truth"):
            self.assertNotIn(forbidden, prompt)

    def test_model_runner_canonicalizes_bfcl_suffix_before_execution(self) -> None:
        row = {
            "source_provenance": {"benchmark_id": "BFCL"},
            "all_tools": [
                {
                    "name": "GorillaFileSystem.mkdir",
                    "description": "Create directory.",
                    "input_schema": {
                        "type": "dict",
                        "properties": {"dir_name": {"type": "string"}},
                        "required": ["dir_name"],
                    },
                }
            ],
            "tail_prompt": "BFCL USER REQUEST:\nCreate a temp directory.",
            "expected_calls": [{"name": "mkdir", "arguments": {"dir_name": ["temp"]}}],
        }

        value = model_runner.execute_bfcl_action(
            {"op": "bfcl_calls", "calls": [{"name": "mkdir", "arguments": {"dir_name": "temp"}}]},
            row,
            [],
        )

        self.assertEqual(value["result"]["bfcl_calls"][0]["name"], "GorillaFileSystem.mkdir")
        self.assertTrue(value["result"]["bfcl_schema_validation"]["valid"])

    def test_model_runner_flags_bfcl_negative_control_success(self) -> None:
        source_dir = self.make_source_dir()
        case = adapter.materialize_cases(source_dir=source_dir, categories=["simple"], per_category=1)[0]
        packet = adapter.control_packet(case, "code_mode_fresh_tail_only")
        calls = [{"name": "calculate_triangle_area", "arguments": {"base": 10, "height": 5}}]
        score = adapter.score_calls(packet["expected_calls"], calls)

        record = model_runner.build_record(
            packet,
            {
                "answer_contained": score["passed"],
                "bfcl_score": score,
                "tool_telemetry": {
                    "nested_tool_ids_called": [call["name"] for call in calls],
                    "bfcl_calls": calls,
                    "bfcl_score": score,
                },
                "response": adapter.canonical_json(calls),
                "normalized_response": adapter.canonical_json(calls),
                "response_hash": adapter.sha256_text(adapter.canonical_json(calls)),
                "generated_token_hash": model_runner.token_hash([]),
                "generated_token_count": 0,
                "final_source": "host_bfcl_call_trace",
            },
        )

        self.assertTrue(score["passed"])
        self.assertFalse(record["control_gate_passed"])
        self.assertEqual(record["failure_class"], "fresh_tail_leak_or_non_prefix_dependent")


if __name__ == "__main__":
    unittest.main()
