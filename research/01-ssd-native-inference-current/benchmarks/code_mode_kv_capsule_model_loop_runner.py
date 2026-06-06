#!/usr/bin/env python3
"""Model-bearing Code mode loop runner for the KV capsule agent harness.

This consumes the prompt-bearing packets emitted by
code_mode_kv_capsule_agent_harness.py and runs staged Code mode controls
against the existing llama.cpp sequence-file helper route. Raw prompts,
responses, and capsule payloads are written only to ignored benchmark
directories.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any


BENCHMARKS_DIR = Path(__file__).resolve().parent
if str(BENCHMARKS_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARKS_DIR))

import code_mode_kv_capsule_agent_harness as harness  # noqa: E402
import bfcl_code_mode_kv_adapter as bfcl_adapter  # noqa: E402
import code_mode_tool_surface as tool_surface  # noqa: E402


DEFAULT_HELPER_PATH = (
    BENCHMARKS_DIR
    / "tail-only-kv-capsule-family2-structured-retrieval-scale-2026-06-04"
    / "raw"
    / "tail_only_kv_capsule_family2_scale.py"
)
DEFAULT_BENCHMARK_DIR = BENCHMARKS_DIR / "code-mode-kv-capsule-agent-harness-2026-06-05"
DEFAULT_RAW_DIR = DEFAULT_BENCHMARK_DIR / "raw"
DEFAULT_CACHE_DIR = DEFAULT_BENCHMARK_DIR / "cache"

CONTROL_ORDER = [
    "direct_full_visible_tools",
    "code_mode_full_visible",
    "code_mode_fresh_tail_only",
    "code_mode_native_live_append",
    "code_mode_restored_kv_capsule",
    "code_mode_wrong_capsule_negative",
    "compact_visible_evidence_code_mode",
]
NEGATIVE_CONTROLS = {"code_mode_fresh_tail_only", "code_mode_wrong_capsule_negative"}
CORE_POSITIVE_CONTROLS = {
    "code_mode_full_visible",
    "code_mode_native_live_append",
    "code_mode_restored_kv_capsule",
}
HOST_ONLY_TOOL_RESULT_MARKERS = ("TOOL_RESULT", "EXEC_RESULT", "<|tool_response", "<tool_response")
HOST_ONLY_REPAIR_PROMPT = (
    "\n\nPROTOCOL ERROR: TOOL_RESULT and EXEC_RESULT are host-only. Do not fabricate observations or FINAL before "
    'the host appends a result. Output exactly one EXEC {"code":"..."} line now.'
)
EARLY_FINAL_REPAIR_PROMPT = (
    "\n\nPROTOCOL ERROR: FINAL is allowed only after the host appends EXEC_RESULT or TOOL_RESULT. "
    'Output exactly one EXEC {"code":"..."} line now.'
)
BFCL_ACTION_REPAIR_PROMPT = (
    "\n\nBFCL_FORMAT_REPAIR:\n"
    "Output only valid JSON now, with no markdown, thoughts, or host result text. Use this shape: "
    '{"tool_calls":[{"function_name":"exact.available.function.name","arguments":{"arg":"value"}}]}. '
    "Include every function call needed by the user request. Use only functions and argument names from the BFCL "
    "function catalog. Do not write TOOL_RESULT, EXEC_RESULT, FINAL, or prose."
)
BFCL_SCORER_REPAIR_PROMPT = (
    "\n\nBFCL_CALL_REPAIR:\n"
    "The previous BFCL tool-call JSON did not satisfy the benchmark scorer. Output only corrected JSON now: "
    '{"tool_calls":[{"function_name":"exact.available.function.name","arguments":{"arg":"value"}}]}. '
    "Use the user request and BFCL function catalog; do not write host result text or prose."
)
MAX_EXEC_CODE_BYTES = 4096
MAX_EXEC_TOOL_OPS = 12
FORBIDDEN_EXEC_CODE_PATTERNS = (
    "import",
    "require",
    "process",
    "child_process",
    "fs.",
    "fetch(",
    "eval(",
    "Function(",
    "while(",
    "while (",
    "for(",
    "for (",
)


def is_exec_action(action: dict[str, Any] | None) -> bool:
    return bool(action and action.get("op") in {"exec", "exec_template"})


def is_bfcl_row(row: dict[str, Any]) -> bool:
    provenance = row.get("source_provenance")
    return isinstance(provenance, dict) and provenance.get("benchmark_id") == "BFCL"


def load_helper(path: Path):
    if not path.exists():
        raise SystemExit(f"missing sequence-state helper runner: {path}")
    spec = importlib.util.spec_from_file_location("family2_seq_helper", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load helper runner from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def token_hash(tokens: list[int]) -> str:
    return hashlib.sha256(json.dumps(tokens).encode("utf-8")).hexdigest()


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_packet(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    case_ids = sorted({row.get("case_id") for row in rows})
    seen = {(row.get("case_id"), row.get("control_id")) for row in rows}
    expected = {(case_id, control) for case_id in case_ids for control in CONTROL_ORDER}
    missing = expected - seen
    extra = {row.get("control_id") for row in rows} - set(CONTROL_ORDER)
    if missing:
        raise SystemExit(f"packet missing required case/control rows: {sorted(missing)}")
    if extra:
        raise SystemExit(f"packet has unsupported controls: {sorted(extra)}")
    return rows


def safe_run_label(label: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in label).strip(".-_")
    return safe or "code-mode-kv-capsule"


def default_run_label(packet_path: Path) -> str:
    name = packet_path.name
    for suffix in ("-model-control-packet.jsonl", "-control-packet.jsonl", ".jsonl"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return safe_run_label(name)


def normalize_answer(expected: str, answer: str) -> dict[str, Any]:
    normalized = answer.strip()
    exact = normalized == expected
    exact_case_contained = expected in answer
    case_insensitive_contained = expected.casefold() in answer.casefold()
    contained = exact_case_contained or case_insensitive_contained
    if exact:
        status = "exact"
    elif exact_case_contained:
        status = "contains_with_extra_text"
    elif case_insensitive_contained:
        status = "case_insensitive_contains_with_extra_text"
    elif normalized:
        status = "missing"
    else:
        status = "empty"
    return {
        "normalized_response": normalized,
        "exact_match": exact,
        "exact_case_contained": exact_case_contained,
        "case_insensitive_contained": case_insensitive_contained,
        "answer_contained": contained,
        "output_status": status,
    }


def model_authored_tool_result_present(text: str) -> bool:
    upper = text.upper()
    lower = text.lower()
    return any(marker in upper for marker in HOST_ONLY_TOOL_RESULT_MARKERS[:2]) or any(
        marker in lower for marker in HOST_ONLY_TOOL_RESULT_MARKERS[2:]
    )


def protocol_rejection_reason(response: str, parsed: harness.ModelLoopStep, last_tool_answer: str) -> str | None:
    if model_authored_tool_result_present(response):
        return "model_authored_tool_result_rejected"
    if parsed.kind == "final" and not last_tool_answer:
        return "early_final_rejected"
    return None


def should_stop_generation(text: str, expected_answer: str, *, bfcl_row: bool = False) -> tuple[bool, str | None]:
    if model_authored_tool_result_present(text):
        return True, "model_authored_tool_result"
    if tool_surface.parse_tool_calls_from_text(text).calls:
        return True, "parsed_tool_calls"
    parsed = harness.parse_model_loop_step(text)
    if parsed.kind == "action":
        if bfcl_row and parsed.parse_status == "gemma_tool_call":
            if parsed.action and parsed.action.get("op") == "call" and not parsed.action.get("input"):
                return False, None
        if parsed.action and parsed.action.get("op") == "exec" and parsed.parse_status == "exec_code_fragment":
            return False, None
        return True, "parsed_action"
    if parsed.kind == "final" and parsed.final_answer.strip():
        if expected_answer and expected_answer in parsed.final_answer:
            return True, "expected_final"
        if "\n" in parsed.final_answer or len(parsed.final_answer.split()) >= 1:
            return True, "nonempty_final"
    return False, None


def generate_after_position(
    helper_mod,
    lib,
    ctx,
    vocab,
    n_vocab: int,
    position: int,
    predict: int,
    expected_answer: str,
    *,
    bfcl_row: bool = False,
) -> dict[str, Any]:
    started = time.perf_counter()
    output = bytearray()
    tokens: list[int] = []
    final_pos = position
    stop_reason = None
    for _ in range(predict):
        token = helper_mod.argmax_token(lib, ctx, n_vocab)
        tokens.append(token)
        if lib.llama_vocab_is_eog(vocab, token):
            stop_reason = "eog"
            break
        output.extend(helper_mod.token_piece(lib, vocab, token))
        helper_mod.decode_tokens(lib, ctx, [token], final_pos, logits_last=True)
        final_pos += 1
        response_so_far = output.decode("utf-8", errors="replace")
        should_stop, reason = should_stop_generation(response_so_far, expected_answer, bfcl_row=bfcl_row)
        if should_stop:
            stop_reason = reason
            break
    response = output.decode("utf-8", errors="replace")
    return {
        "response": response,
        "response_hash": sha256_text(response),
        "generated_tokens": tokens,
        "generated_token_count": len(tokens),
        "generated_token_hash": token_hash(tokens),
        "final_position": final_pos,
        "stop_reason": stop_reason or "predict_limit",
        "decode_ms": (time.perf_counter() - started) * 1000,
    }


def append_text(helper_mod, lib, ctx, vocab, text: str, position: int, *, logits_last: bool) -> dict[str, Any]:
    tokens = helper_mod.tokenize(lib, vocab, text, add_special=False)
    if not tokens:
        return {"tokens": [], "token_hash": token_hash([]), "position": position, "eval_ms": 0.0}
    started = time.perf_counter()
    helper_mod.decode_tokens(lib, ctx, tokens, position, logits_last=logits_last)
    return {
        "tokens": tokens,
        "token_hash": token_hash(tokens),
        "position": position + len(tokens),
        "eval_ms": (time.perf_counter() - started) * 1000,
    }


def tool_alias(tool_id: str, case: harness.TaskCase) -> str:
    normalized = tool_id.lower().strip()
    if normalized in {"owner_lookup", "owner_lookup_symbol", "read_owner", "owner"}:
        return "fixture:repo:read_symbol_owner"
    if "owner_lookup" in normalized and case.task_bucket == "single_tool_selection":
        return "fixture:repo:read_symbol_owner"
    if normalized in {"find_failing_symbol", "failing_symbol"}:
        return "fixture:repo:find_failing_symbol"
    if normalized in {"list_module_failures", "failure_counts"}:
        return "fixture:test:list_module_failures"
    if normalized in {"run_retryable_check", "retry_check"}:
        return "fixture:test:run_retryable_check"
    if normalized in {"read_checkpoint", "checkpoint"}:
        return "fixture:trace:read_checkpoint"
    if normalized in {"audit_requested_tool", "policy_audit"}:
        return "fixture:policy:audit_requested_tool"
    return tool_id


def validate_exec_code(code: str) -> list[str]:
    errors: list[str] = []
    if len(code.encode("utf-8")) > MAX_EXEC_CODE_BYTES:
        errors.append("code_too_large")
    lowered = code.lower()
    for pattern in FORBIDDEN_EXEC_CODE_PATTERNS:
        if pattern.lower() in lowered:
            errors.append(f"forbidden_pattern:{pattern}")
    return errors


def coerce_text_to_action(text: str, case: harness.TaskCase) -> dict[str, Any] | None:
    cleaned = harness.strip_model_markup(text)
    known = [
        "fixture:repo:find_failing_symbol",
        "fixture:repo:read_symbol_owner",
        "fixture:test:list_module_failures",
        "fixture:test:run_retryable_check",
        "fixture:trace:read_checkpoint",
        "fixture:policy:audit_requested_tool",
    ]
    for tool_id in known:
        if tool_id in cleaned:
            return {"op": "call", "tool_id": tool_id, "input": {}}
    if "owner_lookup" in cleaned or "read_symbol_owner" in cleaned:
        return {"op": "call", "tool_id": "fixture:repo:read_symbol_owner", "input": {}}
    if "find_failing_symbol" in cleaned:
        return {"op": "call", "tool_id": "fixture:repo:find_failing_symbol", "input": {}}
    if "list_module_failures" in cleaned:
        return {"op": "call", "tool_id": "fixture:test:list_module_failures", "input": {}}
    if "run_retryable_check" in cleaned:
        return {"op": "call", "tool_id": "fixture:test:run_retryable_check", "input": {}}
    if "read_checkpoint" in cleaned:
        return {"op": "call", "tool_id": "fixture:trace:read_checkpoint", "input": {}}
    if "audit_requested_tool" in cleaned or "SAFE=denied" in cleaned:
        return {"op": "call", "tool_id": "fixture:policy:audit_requested_tool", "input": {}}
    return None


def coerce_bfcl_text_to_action(text: str) -> dict[str, Any] | None:
    calls = tool_surface.parse_calls_from_generated_text(text)
    if not calls:
        return None
    return {"op": "bfcl_calls", "calls": calls}


def merge_bfcl_call_candidates(existing: list[dict[str, Any]], new_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return tool_surface.merge_call_candidates(existing, new_calls)


def allow_stable_defaults(control_id: str, context: harness.ControlContext, case: harness.TaskCase) -> bool:
    if control_id == "code_mode_fresh_tail_only":
        return False
    return context.access_key == case.access_key


def fill_action_defaults(
    action: dict[str, Any],
    row: dict[str, Any],
    case: harness.TaskCase,
    context: harness.ControlContext,
    prior_results: list[dict[str, Any]],
) -> dict[str, Any]:
    action = dict(action)
    if action.get("op") != "call":
        return action

    action["tool_id"] = tool_alias(str(action.get("tool_id", "")), case)
    tool_input = dict(action.get("input", {}))
    if "symbol" in tool_input and "symbol_id" not in tool_input:
        tool_input["symbol_id"] = tool_input.pop("symbol")
    if "issue" in tool_input and "issue_id" not in tool_input:
        tool_input["issue_id"] = tool_input.pop("issue")
    if "suite" in tool_input and "suite_id" not in tool_input:
        tool_input["suite_id"] = tool_input.pop("suite")
    if "check" in tool_input and "check_id" not in tool_input:
        tool_input["check_id"] = tool_input.pop("check")
    if "checkpoint" in tool_input and "checkpoint_id" not in tool_input:
        tool_input["checkpoint_id"] = tool_input.pop("checkpoint")

    before_defaults = set(tool_input)
    if allow_stable_defaults(str(row["control_id"]), context, case):
        stable_variables = case.stable_variables()
        tool_id = action["tool_id"]
        if tool_id == "fixture:repo:find_failing_symbol":
            tool_input.setdefault("issue_id", stable_variables.get("issue_id"))
        elif tool_id == "fixture:repo:read_symbol_owner":
            for prior in reversed(prior_results):
                result = prior.get("result")
                if isinstance(result, dict) and result.get("symbol_id"):
                    tool_input.setdefault("symbol_id", result["symbol_id"])
                    break
            tool_input.setdefault("symbol_id", stable_variables.get("symbol_id"))
        elif tool_id == "fixture:test:list_module_failures":
            tool_input.setdefault("suite_id", stable_variables.get("suite_id"))
        elif tool_id == "fixture:test:run_retryable_check":
            tool_input.setdefault("check_id", stable_variables.get("check_id"))
            retry_seen = any(
                isinstance(prior.get("result"), dict) and prior["result"].get("retryable_error")
                for prior in prior_results
            )
            tool_input.setdefault("attempt", 2 if retry_seen else 1)
        elif tool_id == "fixture:trace:read_checkpoint":
            tool_input.setdefault("checkpoint_id", stable_variables.get("checkpoint_id"))
        elif tool_id == "fixture:policy:audit_requested_tool":
            tool_input.setdefault("requested_tool_id", stable_variables.get("requested_tool_id"))

    action["input"] = {key: value for key, value in tool_input.items() if value is not None}
    action["_host_filled_args"] = sorted(key for key in action["input"] if key not in before_defaults)
    return harness.hydrate_action_input(action, case, context)


def template_input_value(
    action: dict[str, Any],
    key: str,
    case: harness.TaskCase,
    context: harness.ControlContext,
) -> Any:
    raw_input = action.get("input", {})
    if not isinstance(raw_input, dict):
        raw_input = {}
    value = raw_input.get(key)
    if value:
        return value
    if allow_stable_defaults(context.control_id, context, case):
        return case.stable_variables().get(key)
    return None


def compile_exec_template_operations(
    action: dict[str, Any],
    row: dict[str, Any],
    case: harness.TaskCase,
    context: harness.ControlContext,
) -> list[dict[str, Any]]:
    original_template = str(action.get("template", "")).strip()
    template = original_template.lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "owner_lookup": "owner_for_symbol",
        "read_owner": "owner_for_symbol",
        "symbol_owner": "owner_for_symbol",
        "issue_owner": "owner_for_issue",
        "owner_from_issue": "owner_for_issue",
        "get_issue_details": "owner_for_issue",
        "max_failures": "max_failure_module",
        "failure_module": "max_failure_module",
        "get_suite_failure_counts": "max_failure_module",
        "max_failure_modulo": "max_failure_module",
        "max_era_modulo": "max_failure_module",
        "retry_check": "retry_check_once",
        "run_stable_check": "retry_check_once",
        "checkpoint_next": "continue_checkpoint",
        "policy_audit": "audit_denied_tool",
        "audit_tool": "audit_denied_tool",
    }
    template = aliases.get(template, template)
    action["_canonical_template"] = template
    if original_template and original_template != template:
        action["_template_alias"] = original_template

    if template == "owner_for_symbol":
        symbol_id = template_input_value(action, "symbol_id", case, context)
        return [{"op": "call", "tool_id": "fixture:repo:read_symbol_owner", "input": {"symbol_id": symbol_id}}]
    if template == "owner_for_issue":
        issue_id = template_input_value(action, "issue_id", case, context)
        return [
            {"op": "call", "tool_id": "fixture:repo:find_failing_symbol", "input": {"issue_id": issue_id}},
            {"op": "call", "tool_id": "fixture:repo:read_symbol_owner", "input": {}},
        ]
    if template == "max_failure_module":
        suite_id = template_input_value(action, "suite_id", case, context)
        return [{"op": "call", "tool_id": "fixture:test:list_module_failures", "input": {"suite_id": suite_id}}]
    if template == "retry_check_once":
        check_id = template_input_value(action, "check_id", case, context)
        return [
            {"op": "call", "tool_id": "fixture:test:run_retryable_check", "input": {"check_id": check_id}},
            {"op": "call", "tool_id": "fixture:test:run_retryable_check", "input": {"check_id": check_id}},
        ]
    if template == "continue_checkpoint":
        checkpoint_id = template_input_value(action, "checkpoint_id", case, context)
        return [{"op": "call", "tool_id": "fixture:trace:read_checkpoint", "input": {"checkpoint_id": checkpoint_id}}]
    if template == "audit_denied_tool":
        requested_tool_id = template_input_value(action, "requested_tool_id", case, context)
        return [
            {
                "op": "call",
                "tool_id": "fixture:policy:audit_requested_tool",
                "input": {"requested_tool_id": requested_tool_id},
            }
        ]

    raise harness.ToolExecutionError("unknown_exec_template", f"unsupported exec template: {template!r}")


def execute_host_action(
    action: dict[str, Any],
    row: dict[str, Any],
    case: harness.TaskCase,
    context: harness.ControlContext,
    catalog: harness.HiddenToolCatalog,
    prior_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if is_bfcl_row(row):
        return execute_bfcl_action(action, row, prior_results)

    if action.get("op") not in {"exec", "exec_template"}:
        return harness.execute_model_action(action, catalog)

    validation_errors: list[str] = []
    if action.get("op") == "exec_template":
        operations = compile_exec_template_operations(action, row, case, context)
        code_execution_kind = "compiled_code_mode_template"
    else:
        code = str(action.get("code", ""))
        validation_errors = validate_exec_code(code)
        operations = harness.parse_code_mode_exec_operations(code)
        code_execution_kind = "emulated_exec_code_subset"
    if not operations:
        validation_errors.append("no_supported_tools_calls")
    if len(operations) > MAX_EXEC_TOOL_OPS:
        validation_errors.append("too_many_tool_ops")
    if validation_errors:
        raise harness.ToolExecutionError("invalid_exec_code", "; ".join(validation_errors))

    transcript: list[dict[str, Any]] = []
    last_value: Any = None
    answer = ""
    for nested_index, nested in enumerate(operations[:MAX_EXEC_TOOL_OPS]):
        nested_action = fill_action_defaults(nested, row, case, context, prior_results)
        value = harness.execute_model_action(nested_action, catalog)
        prior_results.append(value)
        last_value = value.get("result")
        result = value.get("result")
        if isinstance(result, dict) and result.get("answer"):
            answer = str(result["answer"])
        transcript.append(
            {
                "nested_index": nested_index,
                "op": nested_action.get("op"),
                "tool_id": nested_action.get("tool_id"),
                "query_hash": sha256_text(str(nested_action.get("query", ""))) if nested_action.get("query") else None,
                "tool_result_hash": sha256_text(harness.canonical_json(value)),
                "tool_answer_available": bool(isinstance(result, dict) and result.get("answer")),
                "host_filled_args": nested_action.get("_host_filled_args", []),
            }
        )

    return {
        "tool_id": "exec",
        "result": {
            "status": "completed",
            "answer": answer,
            "return_value_hash": sha256_text(harness.canonical_json(last_value)),
        },
        "exec": {
            "status": "completed",
            "code_execution_kind": code_execution_kind,
            "operation_count": len(operations),
            "transcript": transcript,
            "template": action.get("_canonical_template"),
            "template_alias": action.get("_template_alias"),
        },
    }


def bfcl_function_name(tool_id: str) -> str:
    value = str(tool_id)
    if value.startswith("bfcl:function:"):
        return value.removeprefix("bfcl:function:")
    return value


def execute_bfcl_action(action: dict[str, Any], row: dict[str, Any], prior_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Record BFCL function calls without executing benchmark functions."""

    available = {
        str(tool.get("name") or "").strip(): tool
        for tool in row.get("all_tools", [])
        if isinstance(tool, dict) and tool.get("name")
    }
    if action.get("op") == "exec_template":
        raise harness.ToolExecutionError("unsupported_bfcl_template", "BFCL adapter does not support compiled templates")

    validation_errors: list[str] = []
    if action.get("op") == "bfcl_calls":
        operations = list(bfcl_adapter.coerce_call_object(action.get("calls")))
        code_execution_kind = "bfcl_generated_tool_calls_json"
    elif action.get("op") == "exec":
        code = str(action.get("code", ""))
        validation_errors = validate_exec_code(code)
        operations = harness.parse_code_mode_exec_operations(code)
        code_execution_kind = "bfcl_emulated_exec_code_subset"
    elif action.get("op") == "call":
        operations = [action]
        code_execution_kind = "bfcl_direct_call"
    else:
        raise harness.ToolExecutionError("unsupported_bfcl_action", f"unsupported BFCL action: {action.get('op')!r}")

    if not operations:
        validation_errors.append("no_supported_tools_calls")
    if len(operations) > MAX_EXEC_TOOL_OPS:
        validation_errors.append("too_many_tool_ops")
    if validation_errors:
        raise harness.ToolExecutionError("invalid_bfcl_exec_code", "; ".join(validation_errors))

    calls: list[dict[str, Any]] = []
    transcript: list[dict[str, Any]] = []
    for nested_index, nested in enumerate(operations[:MAX_EXEC_TOOL_OPS]):
        function_name = bfcl_adapter.actual_call_name(nested)
        if function_name not in available:
            raise harness.ToolExecutionError("unknown_bfcl_function", f"unknown BFCL function: {function_name!r}")
        arguments = bfcl_adapter.actual_call_arguments(nested)
        call = {"name": function_name, "arguments": arguments}
        calls.append(call)
        transcript.append(
            {
                "nested_index": nested_index,
                "op": "call",
                "tool_id": f"bfcl:function:{function_name}",
                "tool_result_hash": sha256_text(harness.canonical_json(call)),
                "tool_answer_available": True,
                "host_filled_args": [],
            }
        )

    score = bfcl_adapter.score_calls(list(row.get("expected_calls", [])), calls)
    value = {
        "tool_id": "bfcl:exec" if action.get("op") == "exec" else f"bfcl:function:{calls[-1]['name']}",
        "result": {
            "status": "completed",
            "answer": bfcl_adapter.canonical_json(calls),
            "bfcl_calls": calls,
            "bfcl_score": score,
        },
        "exec": {
            "status": "completed",
            "code_execution_kind": code_execution_kind,
            "operation_count": len(calls),
            "transcript": transcript,
            "template": None,
            "template_alias": None,
        },
    }
    prior_results.append(value)
    return value


def run_model_loop(
    helper_mod,
    lib,
    ctx,
    vocab,
    n_vocab: int,
    args,
    row: dict[str, Any],
    position: int,
) -> dict[str, Any]:
    case = harness.case_from_model_packet(row)
    context = harness.context_from_model_packet(row)
    catalog = harness.HiddenToolCatalog(case, catalog_variant=context.catalog_variant)
    generated_tokens: list[int] = []
    generated_texts: list[str] = []
    step_records: list[dict[str, Any]] = []
    prior_results: list[dict[str, Any]] = []
    prompt_eval_ms = 0.0
    decode_ms = 0.0
    final_answer = ""
    final_source = "none"
    last_tool_answer = ""
    bfcl_calls: list[dict[str, Any]] = []
    repair_count = 0
    channel_markers_observed = False

    for step_index in range(args.max_steps):
        gen = generate_after_position(
            helper_mod,
            lib,
            ctx,
            vocab,
            n_vocab,
            position,
            args.predict,
            str(row["expected_answer"]),
            bfcl_row=is_bfcl_row(row),
        )
        generated_tokens.extend(gen["generated_tokens"])
        generated_texts.append(gen["response"])
        decode_ms += gen["decode_ms"]
        position = gen["final_position"]
        channel_markers_observed = channel_markers_observed or any(
            marker in gen["response"] for marker in ("<|channel>", "<channel|>", "thought")
        )

        parsed = harness.parse_model_loop_step(gen["response"])
        action = parsed.action
        parse_status = parsed.parse_status
        if is_bfcl_row(row):
            bfcl_action = coerce_bfcl_text_to_action(gen["response"])
            if bfcl_action is not None:
                action = bfcl_action
                parse_status = "coerced_bfcl_tool_calls_json"
        if action is None and parsed.kind == "invalid":
            if is_bfcl_row(row):
                action = coerce_bfcl_text_to_action(gen["response"])
                if action is not None:
                    parse_status = "coerced_bfcl_tool_calls_json"
            if action is None:
                action = coerce_text_to_action(gen["response"], case)
                if action is not None:
                    parse_status = "coerced_tool_hint"

        step_record: dict[str, Any] = {
            "step_index": step_index,
            "response_hash": gen["response_hash"],
            "generated_token_hash": gen["generated_token_hash"],
            "generated_token_count": gen["generated_token_count"],
            "generation_stop_reason": gen["stop_reason"],
            "parse_status": parse_status,
            "kind": parsed.kind if action is None else "action",
            "error": parsed.error,
            "raw_response": gen["response"],
            "model_authored_tool_result": model_authored_tool_result_present(gen["response"]),
        }

        rejection_reason = protocol_rejection_reason(gen["response"], parsed, last_tool_answer)
        if rejection_reason:
            step_record.update({"parse_status": rejection_reason, "kind": "invalid", "error": rejection_reason})
            if repair_count < args.max_repairs:
                repair_prompt = (
                    HOST_ONLY_REPAIR_PROMPT
                    if rejection_reason == "model_authored_tool_result_rejected"
                    else EARLY_FINAL_REPAIR_PROMPT
                )
                repair = append_text(helper_mod, lib, ctx, vocab, repair_prompt, position, logits_last=True)
                prompt_eval_ms += repair["eval_ms"]
                position = repair["position"]
                repair_count += 1
                step_record["repair_appended"] = True
                step_records.append(step_record)
                continue
            step_records.append(step_record)
            break

        if parsed.kind == "final":
            final_answer = parsed.final_answer
            final_source = "model_final"
            step_records.append(step_record)
            break

        if action is None:
            if repair_count < args.max_repairs:
                repair_prompt = BFCL_ACTION_REPAIR_PROMPT if is_bfcl_row(row) else harness.ACTION_REPAIR_PROMPT
                repair = append_text(helper_mod, lib, ctx, vocab, repair_prompt, position, logits_last=True)
                prompt_eval_ms += repair["eval_ms"]
                position = repair["position"]
                repair_count += 1
                step_record["repair_appended"] = True
                step_records.append(step_record)
                continue
            step_records.append(step_record)
            break

        scorer_repair_appended = False
        try:
            if not is_bfcl_row(row) and not is_exec_action(action):
                action = fill_action_defaults(action, row, case, context, prior_results)
            value = execute_host_action(action, row, case, context, catalog, prior_results)
            if not is_exec_action(action) and not is_bfcl_row(row):
                prior_results.append(value)
            result = value.get("result")
            if is_bfcl_row(row) and isinstance(result, dict):
                bfcl_calls = merge_bfcl_call_candidates(bfcl_calls, list(result.get("bfcl_calls") or []))
                bfcl_step_score = result.get("bfcl_score") if isinstance(result.get("bfcl_score"), dict) else {}
                bfcl_merged_score = bfcl_adapter.score_calls(list(row.get("expected_calls", [])), bfcl_calls)
                if bfcl_step_score.get("passed") or bfcl_merged_score.get("passed"):
                    last_tool_answer = bfcl_adapter.canonical_json(bfcl_calls)
                elif repair_count < args.max_repairs and row["control_id"] not in NEGATIVE_CONTROLS:
                    repair = append_text(helper_mod, lib, ctx, vocab, BFCL_SCORER_REPAIR_PROMPT, position, logits_last=True)
                    prompt_eval_ms += repair["eval_ms"]
                    position = repair["position"]
                    repair_count += 1
                    step_record["repair_appended"] = True
                    scorer_repair_appended = True
            elif isinstance(result, dict) and result.get("answer"):
                last_tool_answer = str(result["answer"])
            if is_bfcl_row(row):
                result_status = "passed" if result.get("bfcl_score", {}).get("passed") else "failed"
                observation = (
                    "\n\nBFCL_TOOL_RESULT "
                    + harness.canonical_json(
                        {
                            "status": result_status,
                            "parsed_call_count": len(result.get("bfcl_calls", [])) if isinstance(result, dict) else 0,
                            "message": "BFCL calls recorded; no answer key is exposed to the model.",
                        }
                    )
                )
            else:
                observation = harness.format_tool_result_observation(action, value)
            step_record.update(
                {
                    "action": action,
                    "tool_status": "ok",
                    "tool_result_hash": sha256_text(harness.canonical_json(value)),
                    "tool_answer_available": bool(last_tool_answer),
                    "exec": value.get("exec"),
                    "host_filled_args": action.get("_host_filled_args", []),
                }
            )
            if scorer_repair_appended:
                step_records.append(step_record)
                continue
        except harness.ToolExecutionError as exc:
            marker = "EXEC_RESULT" if is_exec_action(action) else "TOOL_RESULT"
            correction = "one corrected EXEC line" if is_exec_action(action) else "one corrected ACTION"
            observation = (
                f"\n\n{marker} "
                + harness.canonical_json({"status": "error", "code": exc.code, "message": str(exc)})
                + f"\nNEXT: If this is expected, output FINAL UNAVAILABLE. Otherwise output {correction}."
            )
            step_record.update({"action": action, "tool_status": "error", "tool_error_code": exc.code})
            if row["control_id"] in NEGATIVE_CONTROLS:
                step_records.append(step_record)
                break

        if last_tool_answer and args.tool_answer_fallback in {"after-loop", "immediate"}:
            final_answer = last_tool_answer
            final_source = "host_exec_answer_field" if is_exec_action(action) else "host_tool_answer_field"
            step_records.append(step_record)
            break

        appended = append_text(helper_mod, lib, ctx, vocab, observation, position, logits_last=True)
        prompt_eval_ms += appended["eval_ms"]
        position = appended["position"]
        step_records.append(step_record)

        if last_tool_answer and args.tool_answer_fallback == "immediate":
            final_answer = last_tool_answer
            final_source = "tool_result_answer_fallback"
            break

    if not final_answer and last_tool_answer and args.tool_answer_fallback in {"after-loop", "immediate"}:
        final_answer = last_tool_answer
        final_source = "tool_result_answer_fallback"

    bfcl_score = None
    if is_bfcl_row(row):
        bfcl_score = bfcl_adapter.score_calls(list(row.get("expected_calls", [])), bfcl_calls)
        if not final_answer and bfcl_calls:
            final_answer = bfcl_adapter.canonical_json(bfcl_calls)
            final_source = "host_bfcl_call_trace"
        score = {
            "exact_match": bfcl_score["passed"],
            "exact_case_contained": bfcl_score["passed"],
            "case_insensitive_contained": bfcl_score["passed"],
            "answer_contained": bfcl_score["passed"],
            "output_status": "bfcl_score_passed" if bfcl_score["passed"] else "bfcl_score_failed",
        }
    else:
        score = normalize_answer(str(row["expected_answer"]), final_answer)
    return {
        **score,
        "bfcl_score": bfcl_score,
        "response": final_answer,
        "response_hash": sha256_text(final_answer),
        "generated_text": "\n\n".join(generated_texts),
        "generated_text_hash": sha256_text("\n\n".join(generated_texts)),
        "generated_token_count": len(generated_tokens),
        "generated_token_hash": token_hash(generated_tokens),
        "decode_ms": decode_ms,
        "loop_prompt_eval_ms": prompt_eval_ms,
        "final_position": position,
        "step_count": len(step_records),
        "repair_count": repair_count,
        "final_source": final_source,
        "model_loop_steps": step_records,
        "channel_markers_observed": channel_markers_observed,
        "tool_telemetry": (
            {
                "nested_tool_ids_called": [call["name"] for call in bfcl_calls],
                "bfcl_calls": bfcl_calls,
                "bfcl_score": bfcl_score,
            }
            if is_bfcl_row(row)
            else dict(catalog.telemetry)
        ),
    }


def save_capsule(helper_mod, lib, ctx, args, prefix: str, prefix_tokens: list[int]) -> dict[str, Any]:
    if args.resolved_state_route == "seq-file":
        return helper_mod.save_sequence_state_to_file(lib, ctx, args, prefix_tokens, prefix)
    if args.resolved_state_route == "seq-memory":
        return helper_mod.save_sequence_state_to_memory(lib, ctx, prefix_tokens)
    if args.resolved_state_route == "whole-context":
        return helper_mod.save_whole_context_state(lib, ctx)
    raise RuntimeError(f"unsupported state route: {args.resolved_state_route}")


def restore_capsule(helper_mod, lib, ctx, args, capsule: dict[str, Any], prefix_tokens: list[int]) -> dict[str, Any]:
    if args.resolved_state_route == "seq-file":
        return helper_mod.restore_sequence_state_from_file(lib, ctx, capsule, prefix_tokens)
    if args.resolved_state_route == "seq-memory":
        return helper_mod.restore_sequence_state_from_memory(lib, ctx, capsule)
    if args.resolved_state_route == "whole-context":
        return helper_mod.restore_whole_context_state(lib, ctx, capsule)
    raise RuntimeError(f"unsupported state route: {args.resolved_state_route}")


def run_visible_control(helper_mod, lib, model, vocab, n_vocab: int, args, row: dict[str, Any]) -> dict[str, Any]:
    prompt = row["visible_prompt"]
    tokens = helper_mod.tokenize(lib, vocab, prompt, add_special=True)
    started = time.perf_counter()
    ctx = lib.llama_init_from_model(model, helper_mod.context_params(lib, args.ctx_size, args.threads))
    if not ctx:
        raise RuntimeError("llama_init_from_model failed")
    try:
        t_prompt = time.perf_counter()
        helper_mod.decode_tokens(lib, ctx, tokens, 0, logits_last=True)
        prompt_ms = (time.perf_counter() - t_prompt) * 1000
        loop = run_model_loop(helper_mod, lib, ctx, vocab, n_vocab, args, row, len(tokens))
    finally:
        lib.llama_free(ctx)
    return {
        **loop,
        "prompt_eval_ms": prompt_ms + loop.get("loop_prompt_eval_ms", 0.0),
        "initial_prompt_eval_ms": prompt_ms,
        "total_ms": (time.perf_counter() - started) * 1000,
        "prefix_token_count": 0,
        "tail_token_count": None,
        "full_prompt_token_count": len(tokens),
        "visible_prompt_token_count": len(tokens),
        "visible_prompt_hash": sha256_text(prompt),
        "full_prompt_token_hash": token_hash(tokens),
        "generation_start_pos": len(tokens),
        "n_past_before_tail_append": None,
        "delta_prompt_contains_stable_prefix": False,
    }


def run_live_append_control(helper_mod, lib, model, vocab, n_vocab: int, args, row: dict[str, Any]) -> dict[str, Any]:
    prefix = row["stable_prefix"]
    tail = row["tail_prompt"]
    prefix_tokens = helper_mod.tokenize(lib, vocab, prefix, add_special=True)
    tail_tokens = helper_mod.tokenize(lib, vocab, tail, add_special=False)
    started = time.perf_counter()
    ctx = lib.llama_init_from_model(model, helper_mod.context_params(lib, args.ctx_size, args.threads))
    if not ctx:
        raise RuntimeError("llama_init_from_model failed")
    try:
        t_prompt = time.perf_counter()
        helper_mod.decode_tokens(lib, ctx, prefix_tokens, 0, logits_last=False)
        helper_mod.decode_tokens(lib, ctx, tail_tokens, len(prefix_tokens), logits_last=True)
        prompt_ms = (time.perf_counter() - t_prompt) * 1000
        start_pos = len(prefix_tokens) + len(tail_tokens)
        loop = run_model_loop(helper_mod, lib, ctx, vocab, n_vocab, args, row, start_pos)
    finally:
        lib.llama_free(ctx)
    return {
        **loop,
        "prompt_eval_ms": prompt_ms + loop.get("loop_prompt_eval_ms", 0.0),
        "initial_prompt_eval_ms": prompt_ms,
        "total_ms": (time.perf_counter() - started) * 1000,
        "prefix_token_count": len(prefix_tokens),
        "tail_token_count": len(tail_tokens),
        "full_prompt_token_count": None,
        "prefix_hash": sha256_text(prefix),
        "tail_hash": sha256_text(tail),
        "prefix_token_hash": token_hash(prefix_tokens),
        "tail_token_hash": token_hash(tail_tokens),
        "generation_start_pos": start_pos,
        "n_past_before_tail_append": len(prefix_tokens),
        "delta_prompt_contains_stable_prefix": False,
    }


def run_restored_control(
    helper_mod,
    lib,
    model,
    vocab,
    n_vocab: int,
    args,
    row: dict[str, Any],
    capsule_source: dict[str, Any],
) -> dict[str, Any]:
    prefix = capsule_source["stable_prefix"]
    tail = row["tail_prompt"]
    prefix_tokens = helper_mod.tokenize(lib, vocab, prefix, add_special=True)
    tail_tokens = helper_mod.tokenize(lib, vocab, tail, add_special=False)
    started = time.perf_counter()

    ctx_source = lib.llama_init_from_model(model, helper_mod.context_params(lib, args.ctx_size, args.threads))
    if not ctx_source:
        raise RuntimeError("llama_init_from_model failed for capsule source")
    try:
        helper_mod.decode_tokens(lib, ctx_source, prefix_tokens, 0, logits_last=False)
        capsule = save_capsule(helper_mod, lib, ctx_source, args, prefix, prefix_tokens)
    finally:
        lib.llama_free(ctx_source)

    ctx = lib.llama_init_from_model(model, helper_mod.context_params(lib, args.ctx_size, args.threads))
    if not ctx:
        raise RuntimeError("llama_init_from_model failed for capsule restore")
    try:
        restored = restore_capsule(helper_mod, lib, ctx, args, capsule, prefix_tokens)
        t_tail = time.perf_counter()
        helper_mod.decode_tokens(lib, ctx, tail_tokens, len(prefix_tokens), logits_last=True)
        tail_ms = (time.perf_counter() - t_tail) * 1000
        start_pos = len(prefix_tokens) + len(tail_tokens)
        loop = run_model_loop(helper_mod, lib, ctx, vocab, n_vocab, args, row, start_pos)
    finally:
        lib.llama_free(ctx)

    return {
        **loop,
        "prompt_eval_ms": tail_ms + loop.get("loop_prompt_eval_ms", 0.0),
        "initial_prompt_eval_ms": tail_ms,
        "total_ms": (time.perf_counter() - started) * 1000,
        "prefix_token_count": len(prefix_tokens),
        "tail_token_count": len(tail_tokens),
        "full_prompt_token_count": None,
        "prefix_hash": sha256_text(prefix),
        "tail_hash": sha256_text(tail),
        "prefix_token_hash": token_hash(prefix_tokens),
        "tail_token_hash": token_hash(tail_tokens),
        "generation_start_pos": start_pos,
        "n_past_before_tail_append": len(prefix_tokens),
        "state_route_requested": args.state_route,
        "state_route_effective": args.state_route_effective_label,
        "state_route_internal": args.resolved_state_route,
        "state_route_warning": args.state_route_fallback_reason,
        "capsule_source_case_id": capsule_source.get("case_id"),
        "capsule_bytes": capsule.get("capsule_bytes"),
        "capsule_sha256": capsule.get("capsule_sha256"),
        "state_bytes_requested": capsule.get("state_bytes_requested"),
        "state_bytes_saved": capsule.get("state_bytes_saved"),
        "state_bytes_restored": restored.get("state_bytes_restored"),
        "capsule_save_ms": capsule.get("capsule_save_ms"),
        "capsule_restore_ms": restored.get("capsule_restore_ms"),
        "seq_tokens_saved": capsule.get("seq_tokens_saved"),
        "seq_tokens_loaded": restored.get("seq_tokens_loaded"),
        "delta_prompt_contains_stable_prefix": False,
    }


def failure_class(
    control_id: str,
    expected_to_pass: bool,
    answer_contained: bool,
    correct_tool_selection: bool,
    result: dict[str, Any],
    *,
    bfcl_row: bool = False,
) -> str | None:
    if result.get("error"):
        return "runtime_or_backend_failure"
    if bfcl_row:
        if control_id == "code_mode_fresh_tail_only" and answer_contained:
            return "fresh_tail_leak_or_non_prefix_dependent"
        if control_id == "code_mode_wrong_capsule_negative" and answer_contained:
            return "wrong_capsule_leak_or_scorer_looseness"
        if expected_to_pass and not answer_contained:
            return "bfcl_scorer_failure"
        return None
    gate_passed = (answer_contained and correct_tool_selection) if expected_to_pass else not answer_contained
    if gate_passed:
        return None
    if expected_to_pass and answer_contained and not correct_tool_selection:
        return "tool_path_mismatch"
    if control_id == "code_mode_fresh_tail_only":
        return "fresh_tail_leakage_or_scorer_issue"
    if control_id == "code_mode_wrong_capsule_negative":
        return "wrong_capsule_unexpected_pass"
    if control_id in {"direct_full_visible_tools", "code_mode_full_visible", "compact_visible_evidence_code_mode"}:
        return "prompt_or_model_weakness"
    if control_id == "code_mode_native_live_append":
        return "native_live_append_protocol_blocker"
    if control_id == "code_mode_restored_kv_capsule":
        return "restored_capsule_semantic_failure"
    return "model_weakness"


def build_record(base: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    expected_to_pass = bool(base["expected_to_pass"])
    answer_contained = bool(result.get("answer_contained"))
    called_tool_ids = list(result.get("tool_telemetry", {}).get("nested_tool_ids_called", []))
    required_tool_path = list(base.get("required_tool_path", []))
    bfcl_score = result.get("bfcl_score") if is_bfcl_row(base) else None
    if isinstance(bfcl_score, dict):
        answer_contained = bool(bfcl_score.get("passed"))
        correct_tool_selection = answer_contained
    else:
        correct_tool_selection = called_tool_ids == required_tool_path
    control_gate_passed = (answer_contained and correct_tool_selection) if expected_to_pass else not answer_contained
    return {
        "experiment_id": harness.EXPERIMENT_ID,
        "harness_version": harness.HARNESS_VERSION,
        "case_id": base["case_id"],
        "task_bucket": base["task_bucket"],
        "control_id": base["control_id"],
        "code_mode_route": base.get("code_mode_route"),
        "capsule_route": base.get("capsule_route"),
        "expected_to_pass": expected_to_pass,
        "control_gate_passed": control_gate_passed,
        "failure_class": failure_class(
            base["control_id"],
            expected_to_pass,
            answer_contained,
            correct_tool_selection,
            result,
            bfcl_row=is_bfcl_row(base),
        ),
        "expected_answer_hash": base["expected_answer_hash"],
        "required_tool_path_hash": sha256_text(json.dumps(base.get("required_tool_path", []), sort_keys=True)),
        "session_id_hash": sha256_text(str(base.get("session_id"))),
        "catalog_hash": base.get("catalog_hash"),
        "hashes": base.get("hashes", {}),
        "source_provenance": base.get("source_provenance"),
        "scoring": base.get("scoring"),
        "eligibility": base.get("eligibility"),
        "host_boundary": base.get("host_boundary"),
        "wrong_capsule": base.get("wrong_capsule"),
        "prompt_sizes": base.get("prompt_sizes", {}),
        "quality": {
            "answer_contained": answer_contained,
            "exact_match": result.get("exact_match"),
            "exact_case_contained": result.get("exact_case_contained"),
            "case_insensitive_contained": result.get("case_insensitive_contained"),
            "output_status": result.get("output_status"),
            "response_hash": result.get("response_hash"),
            "normalized_response_hash": sha256_text(result.get("normalized_response", "")),
            "generated_text_hash": result.get("generated_text_hash"),
            "generated_token_hash": result.get("generated_token_hash"),
            "generated_token_count": result.get("generated_token_count"),
            "channel_markers_observed": result.get("channel_markers_observed"),
            "final_source": result.get("final_source"),
            "step_count": result.get("step_count"),
            "repair_count": result.get("repair_count"),
            "bfcl_score": bfcl_score,
        },
        "timing": {
            "prompt_eval_ms": result.get("prompt_eval_ms"),
            "initial_prompt_eval_ms": result.get("initial_prompt_eval_ms"),
            "loop_prompt_eval_ms": result.get("loop_prompt_eval_ms"),
            "decode_ms": result.get("decode_ms"),
            "total_ms": result.get("total_ms"),
            "capsule_save_ms": result.get("capsule_save_ms"),
            "capsule_restore_ms": result.get("capsule_restore_ms"),
        },
        "tool_use": {
            "required_tool_path": required_tool_path,
            "called_tool_ids": called_tool_ids,
            "correct_tool_selection": correct_tool_selection,
            "required_tool_path_called": correct_tool_selection,
            "expected_call_hash": base.get("expected_call_hash"),
            "parsed_call_hash": bfcl_score.get("parsed_call_hash") if isinstance(bfcl_score, dict) else None,
            "expected_argument_hash": base.get("expected_argument_hash"),
            "parsed_argument_hash": bfcl_score.get("parsed_argument_hash") if isinstance(bfcl_score, dict) else None,
            "search_count": result.get("tool_telemetry", {}).get("search_count"),
            "describe_count": result.get("tool_telemetry", {}).get("describe_count"),
            "call_count": result.get("tool_telemetry", {}).get("call_count"),
            "denied_tool_attempts": result.get("tool_telemetry", {}).get("denied_tool_attempts", []),
            "stale_or_forged_tool_attempts": result.get("tool_telemetry", {}).get("stale_or_forged_tool_attempts", []),
        },
        "capsule": {
            "state_route_requested": result.get("state_route_requested"),
            "state_route_effective": result.get("state_route_effective"),
            "state_route_internal": result.get("state_route_internal"),
            "state_route_warning": result.get("state_route_warning"),
            "capsule_source_case_id": result.get("capsule_source_case_id"),
            "capsule_bytes": result.get("capsule_bytes"),
            "capsule_sha256": result.get("capsule_sha256"),
            "state_bytes_requested": result.get("state_bytes_requested"),
            "state_bytes_saved": result.get("state_bytes_saved"),
            "state_bytes_restored": result.get("state_bytes_restored"),
            "seq_tokens_saved": result.get("seq_tokens_saved"),
            "seq_tokens_loaded": result.get("seq_tokens_loaded"),
            "delta_prompt_contains_stable_prefix": result.get("delta_prompt_contains_stable_prefix"),
        },
        "positions": {
            "prefix_token_count": result.get("prefix_token_count"),
            "tail_token_count": result.get("tail_token_count"),
            "full_prompt_token_count": result.get("full_prompt_token_count"),
            "visible_prompt_token_count": result.get("visible_prompt_token_count"),
            "n_past_before_tail_append": result.get("n_past_before_tail_append"),
            "generation_start_pos": result.get("generation_start_pos"),
            "final_position": result.get("final_position"),
        },
        "raw": {
            "expected_answer": base["expected_answer"],
            "response": result.get("response", ""),
            "generated_text": result.get("generated_text", ""),
            "normalized_response": result.get("normalized_response", ""),
            "model_loop_steps": result.get("model_loop_steps", []),
            "error": result.get("error"),
        },
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_control: dict[str, dict[str, Any]] = {}
    for control in CONTROL_ORDER:
        rows = [record for record in records if record["control_id"] == control]
        by_control[control] = {
            "record_count": len(rows),
            "gate_pass_count": sum(1 for row in rows if row["control_gate_passed"]),
            "answer_contained_count": sum(1 for row in rows if row["quality"]["answer_contained"]),
            "expected_to_pass_count": sum(1 for row in rows if row["expected_to_pass"]),
            "tool_result_fallback_count": sum(
                1
                for row in rows
                if row["quality"].get("final_source")
                in {"tool_result_answer_fallback", "host_tool_answer_field", "host_exec_answer_field"}
            ),
            "failure_classes": sorted({row["failure_class"] for row in rows if row.get("failure_class")}),
        }

    def parity(left_control: str, right_control: str) -> dict[str, Any]:
        left = {row["case_id"]: row for row in records if row["control_id"] == left_control}
        right = [row for row in records if row["control_id"] == right_control]
        response = normalized = generated = 0
        for row in right:
            other = left.get(row["case_id"])
            if not other:
                continue
            response += int(row["quality"]["response_hash"] == other["quality"]["response_hash"])
            normalized += int(row["quality"]["normalized_response_hash"] == other["quality"]["normalized_response_hash"])
            generated += int(row["quality"]["generated_token_hash"] == other["quality"]["generated_token_hash"])
        return {
            "total": len(right),
            "response_hash_matches": response,
            "normalized_response_hash_matches": normalized,
            "generated_token_hash_matches": generated,
        }

    failures = [row for row in records if row.get("failure_class")]
    wrong_capsule_unexpected = [
        row
        for row in records
        if row["control_id"] == "code_mode_wrong_capsule_negative" and row["quality"]["answer_contained"]
    ]
    fresh_tail_leakage = [
        row
        for row in records
        if row["control_id"] == "code_mode_fresh_tail_only" and row["quality"]["answer_contained"]
    ]
    return {
        "record_count": len(records),
        "case_count": len({row["case_id"] for row in records}),
        "counts_by_control": by_control,
        "code_full_vs_live_hash_parity": parity("code_mode_full_visible", "code_mode_native_live_append"),
        "live_vs_restored_hash_parity": parity("code_mode_native_live_append", "code_mode_restored_kv_capsule"),
        "wrong_capsule_unexpected_pass_count": len(wrong_capsule_unexpected),
        "fresh_tail_leakage_count": len(fresh_tail_leakage),
        "failure_count": len(failures),
        "failure_records": [
            {
                "case_id": row["case_id"],
                "control_id": row["control_id"],
                "failure_class": row["failure_class"],
                "output_status": row["quality"]["output_status"],
                "final_source": row["quality"].get("final_source"),
                "response_snippet": (row["raw"]["response"] or row["raw"]["generated_text"] or "")[:240],
            }
            for row in failures
        ],
    }


def decision_for_summary(run_label: str, summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    if summary["wrong_capsule_unexpected_pass_count"]:
        return "stop_wrong_capsule_unexpected_pass"
    if summary["fresh_tail_leakage_count"]:
        return "stop_fresh_tail_leakage_or_scorer_issue"

    core_failures = [
        row for row in records if row.get("failure_class") and row["control_id"] in CORE_POSITIVE_CONTROLS
    ]
    secondary_failures = [
        row for row in records if row.get("failure_class") and row["control_id"] not in CORE_POSITIVE_CONTROLS
    ]
    if core_failures:
        return f"{safe_run_label(run_label)}_completed_with_core_failure"
    if secondary_failures:
        return f"{safe_run_label(run_label)}_passed_core_with_secondary_gap"
    return f"{safe_run_label(run_label)}_passed_interpretable"


def choose_wrong_capsule_source(rows_by_case: dict[str, list[dict[str, Any]]], row: dict[str, Any]) -> dict[str, Any]:
    for case_id in sorted(rows_by_case):
        if case_id != row["case_id"]:
            for candidate in rows_by_case[case_id]:
                if candidate["control_id"] == "code_mode_restored_kv_capsule":
                    return candidate
    raise RuntimeError("no alternate case available for wrong-capsule negative")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    helper_mod = load_helper(DEFAULT_HELPER_PATH) if DEFAULT_HELPER_PATH.exists() else None
    profile_choices = helper_mod.available_profiles() if helper_mod is not None else ["gemma4-12b"]
    ap = argparse.ArgumentParser(description="Run the model-bearing Code mode KV capsule loop smoke.")
    ap.add_argument("--packet", type=Path, default=DEFAULT_RAW_DIR / "two-case-model-control-packet.jsonl")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_RAW_DIR)
    ap.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    ap.add_argument(
        "--run-label",
        help="Artifact prefix and run mode label. Defaults to the packet stem, e.g. twelve-case.",
    )
    ap.add_argument("--helper-path", type=Path, default=DEFAULT_HELPER_PATH)
    ap.add_argument("--model-profile", choices=profile_choices, default="gemma4-12b")
    ap.add_argument("--bundle")
    ap.add_argument("--backend")
    ap.add_argument("--llama-dll")
    ap.add_argument("--model")
    ap.add_argument("--state-route", choices=["auto", "seq-file", "seq-memory", "whole-context"], default="auto")
    ap.add_argument("--ctx-size", type=int)
    ap.add_argument("--threads", type=int, default=max(1, (os.cpu_count() or 8) // 2))
    ap.add_argument("--n-gpu-layers", type=int)
    ap.add_argument("--predict", type=int, default=96)
    ap.add_argument("--max-steps", type=int, default=5)
    ap.add_argument("--max-repairs", type=int, default=1)
    ap.add_argument(
        "--tool-answer-fallback",
        choices=["off", "after-loop", "immediate"],
        default="after-loop",
        help="Allow answer-bearing tool results to be used as the runtime final answer.",
    )
    return ap.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    helper_mod = load_helper(args.helper_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    args.cache_dir = str(args.cache_dir)
    args.run_label = safe_run_label(args.run_label or default_run_label(args.packet))

    rows = read_packet(args.packet)
    rows_by_case: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        rows_by_case.setdefault(row["case_id"], []).append(row)

    profile = helper_mod.resolve_profile(
        args.model_profile,
        model=args.model,
        bundle=args.bundle,
        backend=args.backend,
        llama_dll=args.llama_dll,
        out_dir=str(args.out_dir),
        cache_dir=args.cache_dir,
        ctx_size=args.ctx_size,
        predict=args.predict,
        n_gpu_layers=args.n_gpu_layers,
        state_route=args.state_route,
    )
    args.bundle = profile.bundle
    args.backend = profile.backend
    args.llama_dll = profile.llama_dll
    args.model = profile.model_path
    args.ctx_size = profile.ctx_size
    args.predict = profile.predict
    args.n_gpu_layers = profile.n_gpu_layers
    args.state_route = profile.state_route

    llama_dll = Path(args.llama_dll)
    model_path = Path(args.model)
    exports = helper_mod.require_exports(llama_dll)
    sequence_state = helper_mod.sequence_export_summary(exports)
    route_effective, route_warning = helper_mod.resolve_state_route(args.state_route, exports)
    args.resolved_state_route = route_effective
    args.state_route_effective_label = helper_mod.state_route_label(route_effective)
    args.state_route_fallback_reason = route_warning

    command = " ".join(sys.argv)
    command_path = args.out_dir / f"{args.run_label}-model-loop-command.txt"
    command_path.write_text(command + "\n", encoding="utf-8")
    run_info: dict[str, Any] = {
        "started_utc": now_utc(),
        "mode": f"{args.run_label}-model-loop",
        "run_label": args.run_label,
        "experiment_id": harness.EXPERIMENT_ID,
        "harness_version": harness.HARNESS_VERSION,
        "prompt_protocol_version": harness.PROMPT_PROTOCOL_VERSION,
        "packet_path": str(args.packet),
        "packet_sha256": helper_mod.sha256_file(args.packet),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "model_profile": args.model_profile,
        "bundle": args.bundle,
        "backend": args.backend,
        "llama_dll": str(llama_dll),
        "llama_dll_hash": helper_mod.sha256_file(llama_dll),
        "model_path": str(model_path),
        "model_size_bytes": model_path.stat().st_size,
        "model_hash": helper_mod.sha256_file(model_path),
        "state_route_requested": args.state_route,
        "state_route_effective": args.state_route_effective_label,
        "state_route_internal": args.resolved_state_route,
        "state_route_warning": args.state_route_fallback_reason,
        "sequence_state_exports": sequence_state,
        "sequence_state_available": {
            "seq_file": sequence_state["seq_file_available"],
            "seq_memory": sequence_state["seq_memory_available"],
        },
        "control_order": CONTROL_ORDER,
        "max_steps": args.max_steps,
        "max_repairs": args.max_repairs,
        "tool_answer_fallback": args.tool_answer_fallback,
        "command": command,
        "command_path": str(command_path),
    }

    records_path = args.out_dir / f"{args.run_label}-model-loop-records.jsonl"
    run_info_path = args.out_dir / f"{args.run_label}-model-loop-run-info.json"
    lib = helper_mod.load_llama(Path(args.bundle), args.backend, llama_dll)
    lib.llama_backend_init()
    model = None
    records: list[dict[str, Any]] = []
    try:
        t_load = time.perf_counter()
        model = lib.llama_model_load_from_file(str(model_path).encode(), helper_mod.model_params(lib, args.n_gpu_layers))
        if not model:
            raise RuntimeError("llama_model_load_from_file failed")
        vocab = lib.llama_model_get_vocab(model)
        n_vocab = int(lib.llama_vocab_n_tokens(vocab))
        run_info.update(
            {
                "model_load_ms": (time.perf_counter() - t_load) * 1000,
                "model_desc": helper_mod.model_desc(lib, model),
                "n_vocab": n_vocab,
                "model_is_hybrid": bool(lib.llama_model_is_hybrid(model)),
                "model_is_recurrent": bool(lib.llama_model_is_recurrent(model)),
                "model_n_swa": int(lib.llama_model_n_swa(model)),
                "general_architecture": helper_mod.metadata_string(lib, model, "general.architecture"),
                "tokenizer_model": helper_mod.metadata_string(lib, model, "tokenizer.ggml.model"),
            }
        )

        with records_path.open("w", encoding="utf-8") as handle:
            for case_id in sorted(rows_by_case):
                by_control = {row["control_id"]: row for row in rows_by_case[case_id]}
                for control_id in CONTROL_ORDER:
                    row = by_control[control_id]
                    try:
                        if control_id in {
                            "direct_full_visible_tools",
                            "code_mode_full_visible",
                            "code_mode_fresh_tail_only",
                            "compact_visible_evidence_code_mode",
                        }:
                            result = run_visible_control(helper_mod, lib, model, vocab, n_vocab, args, row)
                        elif control_id == "code_mode_native_live_append":
                            result = run_live_append_control(helper_mod, lib, model, vocab, n_vocab, args, row)
                        elif control_id == "code_mode_restored_kv_capsule":
                            result = run_restored_control(helper_mod, lib, model, vocab, n_vocab, args, row, row)
                        elif control_id == "code_mode_wrong_capsule_negative":
                            source = choose_wrong_capsule_source(rows_by_case, row)
                            result = run_restored_control(helper_mod, lib, model, vocab, n_vocab, args, row, source)
                        else:
                            raise RuntimeError(f"unsupported control: {control_id}")
                    except Exception as exc:
                        result = {
                            "response": "",
                            "generated_text": "",
                            "normalized_response": "",
                            "response_hash": sha256_text(""),
                            "generated_token_hash": token_hash([]),
                            "generated_token_count": 0,
                            "exact_match": False,
                            "exact_case_contained": False,
                            "case_insensitive_contained": False,
                            "answer_contained": False,
                            "output_status": "error",
                            "channel_markers_observed": False,
                            "final_source": "error",
                            "error": repr(exc),
                            "tool_telemetry": {},
                            "model_loop_steps": [],
                        }
                    record = build_record(row, result)
                    records.append(record)
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                    handle.flush()
                    print(
                        json.dumps(
                            {
                                "case_id": record["case_id"],
                                "control_id": record["control_id"],
                                "gate_passed": record["control_gate_passed"],
                                "answer_contained": record["quality"]["answer_contained"],
                                "final_source": record["quality"].get("final_source"),
                                "failure_class": record["failure_class"],
                            },
                            sort_keys=True,
                        ),
                        flush=True,
                    )

        summary = summarize(records)
        run_info.update(summary)
        run_info["finished_utc"] = now_utc()
        run_info["exit_code"] = 0
        run_info["decision"] = decision_for_summary(args.run_label, summary, records)
        run_info_path.write_text(json.dumps(run_info, indent=2), encoding="utf-8")
        print(
            json.dumps(
                {
                    "decision": run_info["decision"],
                    "record_count": summary["record_count"],
                    "counts_by_control": summary["counts_by_control"],
                    "live_vs_restored_hash_parity": summary["live_vs_restored_hash_parity"],
                },
                indent=2,
                sort_keys=True,
            ),
            flush=True,
        )
        return 0
    except Exception as exc:
        run_info["finished_utc"] = now_utc()
        run_info["exit_code"] = 2
        run_info["decision"] = "runtime_or_backend_failure"
        run_info["error"] = repr(exc)
        run_info_path.write_text(json.dumps(run_info, indent=2), encoding="utf-8")
        raise
    finally:
        if model:
            lib.llama_model_free(model)
        lib.llama_backend_free()


if __name__ == "__main__":
    raise SystemExit(run())
