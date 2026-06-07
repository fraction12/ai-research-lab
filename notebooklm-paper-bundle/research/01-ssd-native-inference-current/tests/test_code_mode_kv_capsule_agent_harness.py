from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import code_mode_kv_capsule_agent_harness as harness  # noqa: E402
import code_mode_kv_capsule_model_loop_runner as model_runner  # noqa: E402


class CodeModeKvCapsuleAgentHarnessTests(unittest.TestCase):
    def test_hidden_catalog_omits_denied_tools_and_supports_search_describe_call(self) -> None:
        case = harness.make_case("single_tool_selection", 0)
        catalog = harness.HiddenToolCatalog(case)

        all_tool_ids = {entry["tool_id"] for entry in catalog.all_tools()}
        self.assertIn("fixture:repo:read_symbol_owner", all_tool_ids)
        self.assertNotIn("fixture:danger:read_secret", all_tool_ids)

        matches = catalog.search("owner symbol")
        self.assertEqual(matches[0]["tool_id"], "fixture:repo:read_symbol_owner")

        described = catalog.describe("fixture:repo:read_symbol_owner")
        self.assertEqual(described["policy"]["allowed"], True)

        result = catalog.call(
            "fixture:repo:read_symbol_owner",
            {
                "case_id": case.case_id,
                "session_id": case.session_id,
                "access_key": case.access_key,
                "symbol_id": case.fixture["symbol_id"],
            },
        )
        self.assertEqual(result["answer"], case.expected_answer)

    def test_denied_and_wrong_session_calls_fail_closed(self) -> None:
        case = harness.make_case("denied_invalid_tool_access", 5)
        catalog = harness.HiddenToolCatalog(case)

        with self.assertRaises(harness.ToolExecutionError) as denied:
            catalog.call(
                "fixture:danger:read_secret",
                {"case_id": case.case_id, "session_id": case.session_id, "access_key": case.access_key},
            )
        self.assertEqual(denied.exception.code, "policy_denied")

        with self.assertRaises(harness.ToolExecutionError) as wrong_session:
            catalog.call(
                "fixture:policy:audit_requested_tool",
                {
                    "case_id": case.case_id,
                    "session_id": "wrong-session",
                    "access_key": case.access_key,
                    "requested_tool_id": "fixture:danger:read_secret",
                },
            )
        self.assertEqual(wrong_session.exception.code, "wrong_session")

    def test_prompts_use_exec_code_mode_protocol(self) -> None:
        case = harness.make_case("single_tool_selection", 0)
        dependent_case = harness.make_case("dependent_multi_tool", 1)
        catalog = harness.HiddenToolCatalog(case)
        dependent_catalog = harness.HiddenToolCatalog(dependent_case)

        stable_prefix = case.stable_prefix(catalog.catalog_id, catalog.catalog_hash())
        dependent_prefix = dependent_case.stable_prefix(
            dependent_catalog.catalog_id,
            dependent_catalog.catalog_hash(),
        )
        tail_prompt = case.tail_prompt()

        self.assertIn("EXEC {", stable_prefix)
        self.assertIn('"template":"owner_for_symbol"', stable_prefix)
        self.assertIn("owner_for_issue", dependent_prefix)
        self.assertIn("host compiles templates", dependent_prefix)
        self.assertNotIn("symbol.symbol_id", dependent_prefix)
        self.assertIn("FINAL <answer>", stable_prefix)
        self.assertIn("STABLE VARIABLES FOR TOOL INPUTS", stable_prefix)
        self.assertIn(case.fixture["symbol_id"], stable_prefix)
        self.assertNotIn("Return exactly the final answer string", tail_prompt)

    def test_direct_baseline_uses_action_protocol_and_visible_schemas(self) -> None:
        case = harness.make_case("single_tool_selection", 0)

        direct = harness.control_model_packet(case, "direct_full_visible_tools")
        code_mode = harness.control_model_packet(case, "code_mode_full_visible")

        self.assertIn("ACTION {", direct["visible_prompt"])
        self.assertIn("DIRECT VISIBLE TOOL SCHEMAS", direct["visible_prompt"])
        self.assertNotIn("EXEC {", direct["visible_prompt"])
        self.assertNotIn("tools.call", direct["visible_prompt"])
        self.assertIn("EXEC {", code_mode["visible_prompt"])
        self.assertIn("owner_for_symbol", code_mode["visible_prompt"])
        self.assertNotIn("DIRECT VISIBLE TOOL SCHEMAS", code_mode["visible_prompt"])

    def test_dependent_case_does_not_expose_symbol_as_stable_default(self) -> None:
        case = harness.make_case("dependent_multi_tool", 1)
        context = harness.context_for_control(case, "code_mode_full_visible")

        self.assertEqual(set(case.stable_variables()), {"issue_id"})

        action = {
            "op": "call",
            "tool_id": "fixture:repo:read_symbol_owner",
            "input": {},
        }
        row = harness.control_model_packet(case, "code_mode_full_visible")
        filled = model_runner.fill_action_defaults(action, row, case, context, [])

        self.assertNotIn("symbol_id", filled["input"])

    def test_wrong_capsule_packet_keeps_true_case_access_for_policy(self) -> None:
        case = harness.make_case("single_tool_selection", 0)
        row = harness.control_model_packet(case, "code_mode_wrong_capsule_negative")
        packet_case = harness.case_from_model_packet(row)
        context = harness.context_from_model_packet(row)
        catalog = harness.HiddenToolCatalog(packet_case)

        self.assertEqual(packet_case.access_key, case.access_key)
        self.assertTrue(str(context.access_key).startswith("wrong-"))

        action = model_runner.fill_action_defaults(
            {
                "op": "call",
                "tool_id": "fixture:repo:read_symbol_owner",
                "input": {"symbol_id": case.fixture["symbol_id"]},
            },
            row,
            packet_case,
            context,
            [],
        )
        with self.assertRaises(harness.ToolExecutionError) as wrong_access:
            harness.execute_model_action(action, catalog)
        self.assertEqual(wrong_access.exception.code, "wrong_access_key")

        defaulted = model_runner.fill_action_defaults(
            {"op": "call", "tool_id": "fixture:repo:read_symbol_owner", "input": {}},
            row,
            packet_case,
            context,
            [],
        )
        self.assertNotIn("symbol_id", defaulted["input"])

    def test_model_loop_parser_accepts_json_final_and_gemma_tool_call(self) -> None:
        json_step = harness.parse_model_loop_step(
            'ACTION {"op":"call","tool_id":"fixture:repo:read_symbol_owner","input":{"symbol_id":"abc"}}'
        )
        self.assertEqual(json_step.kind, "action")
        self.assertEqual(json_step.action["op"], "call")
        self.assertEqual(json_step.action["tool_id"], "fixture:repo:read_symbol_owner")
        self.assertEqual(json_step.action["input"]["symbol_id"], "abc")

        final_step = harness.parse_model_loop_step("FINAL TOOL=owner-sing-00")
        self.assertEqual(final_step.kind, "final")
        self.assertEqual(final_step.final_answer, "TOOL=owner-sing-00")

        gemma_step = harness.parse_model_loop_step(
            '<|channel>thought\n<channel|><|tool_call>call:fixture:repo:find_failing_symbol'
            '{issue_id: "ISS-01"}<tool_call|>'
        )
        self.assertEqual(gemma_step.kind, "action")
        self.assertEqual(gemma_step.action["tool_id"], "fixture:repo:find_failing_symbol")
        self.assertEqual(gemma_step.action["input"]["issue_id"], "ISS-01")
        self.assertEqual(gemma_step.parse_status, "tool_surface_gemma_native_call")

        dotted_tool_step = harness.parse_model_loop_step(
            '<|tool_call>call:area_circle.calculate{radius: 5.0}<tool_call|>'
        )
        self.assertEqual(dotted_tool_step.kind, "action")
        self.assertEqual(dotted_tool_step.action["tool_id"], "area_circle.calculate")
        self.assertEqual(dotted_tool_step.action["input"]["radius"], 5)

        exec_step = harness.parse_model_loop_step(
            'EXEC {"language":"javascript","code":"const result = await tools.call(\\"fixture:repo:read_symbol_owner\\", {\\"symbol_id\\":\\"abc\\"}); return result.answer;"}'
        )
        self.assertEqual(exec_step.kind, "action")
        self.assertEqual(exec_step.action["op"], "exec")
        self.assertIn("tools.call", exec_step.action["code"])

        template_step = harness.parse_model_loop_step(
            'EXEC {"template":"owner_for_issue","args":{"issue_id":"ISS-01"}}'
        )
        self.assertEqual(template_step.kind, "action")
        self.assertEqual(template_step.action["op"], "exec_template")
        self.assertEqual(template_step.action["template"], "owner_for_issue")
        self.assertEqual(template_step.action["input"]["issue_id"], "ISS-01")

        template_hint_step = harness.parse_model_loop_step("EXEC owner_for_symbol symbol_id=sym-1")
        self.assertEqual(template_hint_step.kind, "action")
        self.assertEqual(template_hint_step.action["op"], "exec_template")
        self.assertEqual(template_hint_step.action["template"], "owner_for_symbol")
        self.assertEqual(template_hint_step.action["input"]["symbol_id"], "sym-1")

        fragment_step = harness.parse_model_loop_step(
            '<|channel>thought\n<channel|>EXEC {"language":"javascript","code":" const result = await tools.call(\\"fixture:repo:read_symbol_owner\\"", {\\"issue_id\\":\\"ISS-01\\"}); return result.answer;"}'
        )
        self.assertEqual(fragment_step.kind, "action")
        self.assertEqual(fragment_step.action["op"], "exec")
        self.assertEqual(fragment_step.parse_status, "exec_code_fragment")

    def test_exec_code_parser_extracts_bounded_tools_api_operations(self) -> None:
        code = (
            "const symbol = await tools.call('fixture:repo:find_failing_symbol', {issue_id:'ISS-01'});\n"
            "const result = await tools.call('fixture:repo:read_symbol_owner', {symbol_id:symbol.symbol_id});\n"
            "return result.answer;"
        )

        operations = harness.parse_code_mode_exec_operations(code)

        self.assertEqual([operation["op"] for operation in operations], ["call", "call"])
        self.assertEqual(operations[0]["tool_id"], "fixture:repo:find_failing_symbol")
        self.assertEqual(operations[0]["input"]["issue_id"], "ISS-01")
        self.assertEqual(operations[1]["tool_id"], "fixture:repo:read_symbol_owner")

    def test_exec_code_parser_recovers_malformed_tool_call_fragments(self) -> None:
        code = 'EXEC {"language":"javascript","code":" const result = await tools.call(\\"fixture:repo:read_symbol_owner\\"", {\\"issue_id\\":\\"ISS-01\\"}); return result.answer;"}'

        operations = harness.parse_code_mode_exec_operations(code)

        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0]["tool_id"], "fixture:repo:read_symbol_owner")
        self.assertEqual(operations[0]["input"]["issue_id"], "ISS-01")

    def test_action_hydration_and_tool_result_observation(self) -> None:
        case = harness.make_case("single_tool_selection", 0)
        context = harness.context_for_control(case, "code_mode_full_visible")
        catalog = harness.HiddenToolCatalog(case)
        action = {
            "op": "call",
            "tool_id": "fixture:repo:read_symbol_owner",
            "input": {"symbol_id": case.fixture["symbol_id"]},
        }

        hydrated = harness.hydrate_action_input(action, case, context)
        self.assertEqual(hydrated["input"]["case_id"], case.case_id)
        self.assertEqual(hydrated["input"]["session_id"], case.session_id)
        self.assertEqual(hydrated["input"]["access_key"], case.access_key)

        value = harness.execute_model_action(hydrated, catalog)
        observation = harness.format_tool_result_observation(hydrated, value)

        self.assertEqual(value["result"]["answer"], case.expected_answer)
        self.assertIn("TOOL_RESULT", observation)
        self.assertIn("FINAL <answer>", observation)

    def test_model_runner_rejects_model_authored_tool_result_before_scoring(self) -> None:
        parsed = harness.parse_model_loop_step('EXEC_RESULT {"result":{"answer":"owner-123"}}\nFINAL owner-123')

        self.assertEqual(parsed.kind, "final")
        self.assertTrue(model_runner.model_authored_tool_result_present(parsed.raw_text))
        self.assertEqual(
            model_runner.protocol_rejection_reason(parsed.raw_text, parsed, last_tool_answer=""),
            "model_authored_tool_result_rejected",
        )
        self.assertEqual(
            model_runner.protocol_rejection_reason(parsed.raw_text, parsed, last_tool_answer="owner-123"),
            "model_authored_tool_result_rejected",
        )

    def test_model_runner_rejects_early_final_until_host_tool_answer_exists(self) -> None:
        parsed = harness.parse_model_loop_step("FINAL owner-123")

        self.assertEqual(parsed.kind, "final")
        self.assertEqual(
            model_runner.protocol_rejection_reason(parsed.raw_text, parsed, last_tool_answer=""),
            "early_final_rejected",
        )
        self.assertIsNone(model_runner.protocol_rejection_reason(parsed.raw_text, parsed, last_tool_answer="owner-123"))

    def test_model_runner_stops_on_valid_action_before_host_observation(self) -> None:
        response = 'EXEC {"code":"const result = await tools.call(\\"fixture:repo:read_symbol_owner\\", {\\"symbol_id\\":\\"sym-1\\"}); return result.answer;"}'
        parsed = harness.parse_model_loop_step(response)

        self.assertEqual(parsed.kind, "action")
        self.assertEqual(parsed.action["op"], "exec")
        self.assertIsNone(model_runner.protocol_rejection_reason(response, parsed, last_tool_answer=""))
        self.assertEqual(model_runner.should_stop_generation(response, "owner-123"), (True, "parsed_action"))

    def test_model_runner_does_not_stop_on_incomplete_exec_fragment(self) -> None:
        fragments = [
            'EXEC {"language":"javascript","code":"const result = await tools.call',
            'EXEC {"language":"javascript","code":"const result = await tools.call(\\"fixture:repo',
        ]

        for response in fragments:
            with self.subTest(response=response):
                parsed = harness.parse_model_loop_step(response)

                self.assertEqual(parsed.kind, "action")
                self.assertEqual(parsed.action["op"], "exec")
                self.assertEqual(parsed.parse_status, "exec_code_fragment")
                self.assertEqual(model_runner.should_stop_generation(response, "owner-123"), (False, None))

    def test_exec_code_parser_does_not_promote_partial_tool_namespace(self) -> None:
        code = '{"language":"javascript","code":"const result = await tools.call(\\"fixture:repo'

        self.assertEqual(harness.parse_code_mode_exec_operations(code), [])

    def test_model_runner_exec_code_emulator_uses_host_tool_answer_field(self) -> None:
        case = harness.make_case("dependent_multi_tool", 1)
        row = harness.control_model_packet(case, "code_mode_full_visible")
        context = harness.context_from_model_packet(row)
        catalog = harness.HiddenToolCatalog(case)
        action = {
            "op": "exec",
            "language": "javascript",
            "code": (
                "const symbol = await tools.call('fixture:repo:find_failing_symbol', {issue_id:'ISS-01'});\n"
                "const result = await tools.call('fixture:repo:read_symbol_owner', {symbol_id:symbol.symbol_id});\n"
                "return result.answer;"
            ),
        }

        value = model_runner.execute_host_action(action, row, case, context, catalog, [])

        self.assertEqual(value["result"]["answer"], case.expected_answer)
        self.assertEqual(catalog.telemetry["nested_tool_ids_called"], case.required_tool_path)
        self.assertEqual(value["exec"]["code_execution_kind"], "emulated_exec_code_subset")
        self.assertEqual(value["exec"]["operation_count"], 2)
        self.assertIn("symbol_id", value["exec"]["transcript"][1]["host_filled_args"])

    def test_model_runner_exec_template_compiler_chains_dependent_tools(self) -> None:
        case = harness.make_case("dependent_multi_tool", 1)
        row = harness.control_model_packet(case, "code_mode_full_visible")
        context = harness.context_from_model_packet(row)
        catalog = harness.HiddenToolCatalog(case)
        action = {"op": "exec_template", "template": "owner_for_issue", "input": {"issue_id": case.fixture["issue_id"]}}

        value = model_runner.execute_host_action(action, row, case, context, catalog, [])

        self.assertEqual(value["result"]["answer"], case.expected_answer)
        self.assertEqual(catalog.telemetry["nested_tool_ids_called"], case.required_tool_path)
        self.assertEqual(value["exec"]["code_execution_kind"], "compiled_code_mode_template")
        self.assertEqual(value["exec"]["operation_count"], 2)
        self.assertIn("symbol_id", value["exec"]["transcript"][1]["host_filled_args"])

    def test_model_runner_exec_template_compiler_normalizes_observed_aliases(self) -> None:
        case = harness.make_case("parallel_aggregation", 8)
        row = harness.control_model_packet(case, "code_mode_full_visible")
        context = harness.context_from_model_packet(row)
        catalog = harness.HiddenToolCatalog(case)
        action = {
            "op": "exec_template",
            "template": "max_failure_modulo",
            "input": {"suite_id": case.fixture["suite_id"]},
        }

        value = model_runner.execute_host_action(action, row, case, context, catalog, [])

        self.assertEqual(value["result"]["answer"], case.expected_answer)
        self.assertEqual(catalog.telemetry["nested_tool_ids_called"], case.required_tool_path)
        self.assertEqual(value["exec"]["template"], "max_failure_module")
        self.assertEqual(value["exec"]["template_alias"], "max_failure_modulo")

    def test_model_runner_derives_stage_run_label_from_packet_name(self) -> None:
        self.assertEqual(
            model_runner.default_run_label(Path("/tmp/twelve-case-model-control-packet.jsonl")),
            "twelve-case",
        )
        self.assertEqual(model_runner.safe_run_label("../twelve case"), "twelve-case")

    def test_model_runner_decision_separates_core_and_secondary_failures(self) -> None:
        def record(control_id: str, failure_class: str | None = None) -> dict[str, object]:
            return {"control_id": control_id, "failure_class": failure_class}

        secondary_records = [
            record("direct_full_visible_tools", "prompt_or_model_weakness"),
            record("code_mode_full_visible"),
            record("code_mode_native_live_append"),
            record("code_mode_restored_kv_capsule"),
            record("compact_visible_evidence_code_mode", "prompt_or_model_weakness"),
        ]
        secondary_summary = {
            "wrong_capsule_unexpected_pass_count": 0,
            "fresh_tail_leakage_count": 0,
        }
        self.assertEqual(
            model_runner.decision_for_summary("twelve-case", secondary_summary, secondary_records),
            "twelve-case_passed_core_with_secondary_gap",
        )

        core_records = [
            record("direct_full_visible_tools"),
            record("code_mode_full_visible", "prompt_or_model_weakness"),
        ]
        self.assertEqual(
            model_runner.decision_for_summary("twelve-case", secondary_summary, core_records),
            "twelve-case_completed_with_core_failure",
        )

    def test_model_runner_positive_gate_requires_required_tool_path(self) -> None:
        case = harness.make_case("dependent_multi_tool", 1)
        row = harness.control_model_packet(case, "code_mode_full_visible")
        record = model_runner.build_record(
            row,
            {
                "answer_contained": True,
                "exact_match": True,
                "exact_case_contained": True,
                "case_insensitive_contained": True,
                "output_status": "exact",
                "response_hash": "response",
                "normalized_response": case.expected_answer,
                "tool_telemetry": {
                    "nested_tool_ids_called": ["fixture:repo:read_symbol_owner"],
                    "search_count": 0,
                    "describe_count": 0,
                    "call_count": 1,
                },
            },
        )

        self.assertFalse(record["control_gate_passed"])
        self.assertEqual(record["failure_class"], "tool_path_mismatch")
        self.assertFalse(record["tool_use"]["required_tool_path_called"])

    def test_control_matrix_negative_controls_fail_as_expected(self) -> None:
        case = harness.make_case("dependent_multi_tool", 1)

        full = harness.run_control(case, "code_mode_full_visible")
        fresh = harness.run_control(case, "code_mode_fresh_tail_only")
        restored = harness.run_control(case, "code_mode_restored_kv_capsule")
        wrong = harness.run_control(case, "code_mode_wrong_capsule_negative")

        self.assertTrue(full["quality"]["task_success"])
        self.assertTrue(restored["quality"]["task_success"])
        self.assertFalse(fresh["quality"]["task_success"])
        self.assertTrue(fresh["control_gate_passed"])
        self.assertFalse(wrong["quality"]["task_success"])
        self.assertTrue(wrong["control_gate_passed"])
        self.assertEqual(wrong["failure_class"], None)

    def test_code_mode_prompt_surface_hides_direct_tools(self) -> None:
        case = harness.make_case("single_tool_selection", 0)

        direct = harness.run_control(case, "direct_full_visible_tools")
        code_mode = harness.run_control(case, "code_mode_full_visible")

        self.assertGreater(len(direct["code_mode"]["visible_tool_names"]), 2)
        self.assertEqual(code_mode["code_mode"]["visible_tool_names"], ["exec", "wait"])

    def test_dry_run_writes_raw_and_distilled_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = harness.build_parser().parse_args(
                [
                    "--mode",
                    "dry-run",
                    "--stage",
                    "two-case",
                    "--raw-dir",
                    str(root / "raw"),
                    "--input-dir",
                    str(root / "inputs"),
                    "--summary-dir",
                    str(root / "summary"),
                ]
            )

            summary = harness.run_dry_stage(args)

            self.assertEqual(summary["metadata"]["case_count"], 2)
            self.assertEqual(summary["metadata"]["record_count"], 14)
            self.assertTrue((root / "summary" / "summary.json").exists())
            self.assertTrue((root / "summary" / "artifact-manifest.json").exists())
            manifest = json.loads((root / "summary" / "artifact-manifest.json").read_text())
            self.assertTrue(Path(manifest["raw_task_suite_path"]).exists())
            self.assertTrue(Path(manifest["raw_records_path"]).exists())
            self.assertTrue(Path(manifest["model_control_packet_path"]).exists())


if __name__ == "__main__":
    unittest.main()
