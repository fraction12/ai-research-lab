#!/usr/bin/env python3
"""No-model BFCL adapter for the Code-mode KV capsule control ladder.

This module intentionally stops before any llama.cpp/model execution. It
materializes BFCL source rows into the same seven-control experiment shape and
reconstructs a deterministic expected-call scorer from upstream BFCL JSONL and
possible_answer JSONL files.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BENCHMARKS_DIR = Path(__file__).resolve().parent
if str(BENCHMARKS_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARKS_DIR))

import code_mode_kv_capsule_agent_harness as harness  # noqa: E402
import code_mode_tool_surface as tool_surface  # noqa: E402


ADAPTER_VERSION = "bfcl_code_mode_kv_adapter_v1"
TRANSFORM_VERSION = "bfcl_code_mode_kv_transform_v1"
SCORER_VERSION = "bfcl_expected_call_scorer_v1"
PROMPT_PROTOCOL_VERSION = "bfcl_programmatic_tool_interface_v3"
PTI_SCHEMA_VALIDATOR_VERSION = "bfcl_pti_schema_validator_v3"
EXPERIMENT_ID = "nonhandmade-code-mode-kv-agent-benchmark-2026-06-05"
BFCL_LEADERBOARD_CHECKPOINT = "f7cf735"
BFCL_DATASET_REVISION = "61fc0608cfd831fcfbbaa676ebdfef0ed963eeda"
BFCL_EVAL_PACKAGE = "bfcl-eval==2025.12.17"
REMOTE_BASE = (
    "https://huggingface.co/datasets/gorilla-llm/"
    f"Berkeley-Function-Calling-Leaderboard/raw/{BFCL_DATASET_REVISION}"
)

CONTROL_IDS = list(harness.CONTROL_IDS)
NEGATIVE_CONTROLS = {"code_mode_fresh_tail_only", "code_mode_wrong_capsule_negative"}

BFCL_CATEGORY_FILES = {
    "simple_python": "BFCL_v4_simple_python.json",
    "simple_java": "BFCL_v4_simple_java.json",
    "simple_javascript": "BFCL_v4_simple_javascript.json",
    "simple": "BFCL_v3_simple.json",
    "multiple": "BFCL_v3_multiple.json",
    "parallel": "BFCL_v3_parallel.json",
    "parallel_multiple": "BFCL_v3_parallel_multiple.json",
    "irrelevance": "BFCL_v3_irrelevance.json",
    "format_sensitivity": "BFCL_v4_format_sensitivity.json",
    "exec_simple": "BFCL_v3_exec_simple.json",
    "exec_multiple": "BFCL_v3_exec_multiple.json",
    "exec_parallel": "BFCL_v3_exec_parallel.json",
    "exec_parallel_multiple": "BFCL_v3_exec_parallel_multiple.json",
    "java": "BFCL_v3_java.json",
    "javascript": "BFCL_v3_javascript.json",
    "sql": "BFCL_v3_sql.json",
    "rest": "BFCL_v3_rest.json",
    "chatable": "BFCL_v3_chatable.json",
    "live_simple": "BFCL_v3_live_simple.json",
    "live_multiple": "BFCL_v3_live_multiple.json",
    "live_parallel": "BFCL_v3_live_parallel.json",
    "live_parallel_multiple": "BFCL_v3_live_parallel_multiple.json",
    "live_relevance": "BFCL_v3_live_relevance.json",
    "live_irrelevance": "BFCL_v3_live_irrelevance.json",
    "multi_turn_base": "BFCL_v3_multi_turn_base.json",
    "multi_turn_long_context": "BFCL_v3_multi_turn_long_context.json",
    "multi_turn_miss_func": "BFCL_v3_multi_turn_miss_func.json",
    "multi_turn_miss_param": "BFCL_v3_multi_turn_miss_param.json",
    "web_search": "BFCL_v4_web_search.json",
    "memory": "BFCL_v4_memory.json",
}
INITIAL_CATEGORY_FILES = BFCL_CATEGORY_FILES
DEFAULT_COMPATIBILITY_CATEGORIES = [
    "simple_python",
    "simple_java",
    "simple_javascript",
    "simple",
    "multiple",
    "parallel",
    "parallel_multiple",
    "irrelevance",
    "exec_simple",
    "exec_multiple",
    "exec_parallel",
    "exec_parallel_multiple",
    "java",
    "javascript",
    "sql",
    "rest",
    "live_simple",
    "live_multiple",
    "live_parallel",
    "live_parallel_multiple",
    "live_relevance",
    "live_irrelevance",
    "multi_turn_base",
    "multi_turn_composite",
    "multi_turn_long_context",
    "multi_turn_miss_func",
    "multi_turn_miss_param",
]
MULTI_TURN_CATEGORIES = {
    "multi_turn_base",
    "multi_turn_long_context",
    "multi_turn_miss_func",
    "multi_turn_miss_param",
}
LIVE_OR_API_CATEGORIES = {
    "rest",
    "live_simple",
    "live_multiple",
    "live_parallel",
    "live_parallel_multiple",
    "live_relevance",
    "live_irrelevance",
}
CALL_STRING_RE = re.compile(r"^\s*(?P<name>[A-Za-z_][A-Za-z0-9_.:-]*)\s*\((?P<args>.*)\)\s*$")


@dataclass(frozen=True)
class BFCLCase:
    case_id: str
    category: str
    source_row: dict[str, Any]
    answer_row: dict[str, Any] | None
    source_row_index: int
    source_row_hash: str
    functions: list[dict[str, Any]]
    user_messages: list[dict[str, str]]
    expected_calls: list[dict[str, Any]]
    scorer_mode: str
    primary_eligible: bool
    primary_eligibility_reason: str
    prefix_dependency_class: str


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def json_hash(value: Any) -> str:
    return sha256_text(canonical_json(value))


def load_jsonl_text(text: str) -> list[dict[str, Any]]:
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            rows.append(json.loads(stripped))
    return rows


def read_text(source_dir: Path | None, relative_path: str, *, remote_base: str = REMOTE_BASE) -> str:
    if source_dir is not None:
        return (source_dir / relative_path).read_text(encoding="utf-8")
    url = f"{remote_base.rstrip('/')}/{relative_path}"
    with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310 - fixed public benchmark URL.
        return response.read().decode("utf-8")


def load_jsonl(source_dir: Path | None, relative_path: str, *, remote_base: str = REMOTE_BASE) -> list[dict[str, Any]]:
    return load_jsonl_text(read_text(source_dir, relative_path, remote_base=remote_base))


def load_possible_answers(
    source_dir: Path | None,
    file_name: str,
    *,
    remote_base: str = REMOTE_BASE,
) -> dict[str, dict[str, Any]]:
    relative = f"possible_answer/{file_name}"
    try:
        rows = load_jsonl(source_dir, relative, remote_base=remote_base)
    except (FileNotFoundError, urllib.error.HTTPError):
        return {}
    return {str(row["id"]): row for row in rows}


def flatten_messages(question: Any) -> list[dict[str, str]]:
    """BFCL stores questions as nested turns; flatten while preserving order."""

    messages: list[dict[str, str]] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict) and "role" in value and "content" in value:
            messages.append({"role": str(value["role"]), "content": str(value["content"])})
            return
        if isinstance(value, list):
            for item in value:
                visit(item)

    visit(question)
    return messages


def user_query_text(messages: list[dict[str, str]]) -> str:
    return "\n".join(f"{message['role'].upper()}: {message['content']}" for message in messages)


def parse_call_string(call_text: str) -> dict[str, Any] | None:
    match = CALL_STRING_RE.match(call_text)
    if not match:
        return None
    name = match.group("name")
    args_text = match.group("args").strip()
    if not args_text:
        return {"name": name, "arguments": {}}
    try:
        expr = ast.parse(f"f({args_text})", mode="eval").body
    except SyntaxError:
        return {"name": name, "arguments": {"_raw": [call_text]}}
    if not isinstance(expr, ast.Call):
        return None
    arguments: dict[str, list[Any]] = {}
    for index, arg in enumerate(expr.args):
        try:
            value = ast.literal_eval(arg)
        except ValueError:
            value = ast.unparse(arg) if hasattr(ast, "unparse") else call_text
        arguments[f"arg{index}"] = [value]
    for keyword in expr.keywords:
        if keyword.arg is None:
            continue
        try:
            value = ast.literal_eval(keyword.value)
        except ValueError:
            value = ast.unparse(keyword.value) if hasattr(ast, "unparse") else call_text
        arguments[str(keyword.arg)] = [value]
    return {"name": name, "arguments": arguments}


def expected_calls_from_answer(answer_row: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not answer_row:
        return []
    calls: list[dict[str, Any]] = []
    def visit(call_spec: Any) -> None:
        if isinstance(call_spec, str):
            parsed = parse_call_string(call_spec)
            if parsed:
                calls.append(parsed)
            return
        if isinstance(call_spec, list):
            for item in call_spec:
                visit(item)
            return
        if not isinstance(call_spec, dict):
            return
        for name, arguments in call_spec.items():
            calls.append(
                {
                    "name": str(name),
                    "arguments": {
                        str(key): list(value) if isinstance(value, list) else [value]
                        for key, value in dict(arguments).items()
                    },
                }
            )
    for call_spec in answer_row.get("ground_truth", []):
        visit(call_spec)
    return calls


def source_fields_used(row: dict[str, Any], answer_row: dict[str, Any] | None) -> list[str]:
    fields = ["id", "question", "function"]
    if "initial_config" in row:
        fields.append("initial_config")
    if "path" in row:
        fields.append("path")
    if "involved_classes" in row:
        fields.append("involved_classes")
    if answer_row is not None:
        fields.append("possible_answer.ground_truth")
    return fields


def source_fields_excluded(row: dict[str, Any], answer_row: dict[str, Any] | None) -> list[str]:
    used = set(source_fields_used(row, answer_row))
    return sorted(key for key in row if key not in used)


def make_bfcl_case(category: str, row: dict[str, Any], answer_row: dict[str, Any] | None, index: int) -> BFCLCase:
    row_id = str(row.get("id") or f"{category}_{index}")
    source_row_hash = json_hash(row)
    expected_calls = expected_calls_from_answer(answer_row)
    functions = normalize_functions(row, expected_calls)
    messages = flatten_messages(row.get("question"))
    if expected_calls and category in MULTI_TURN_CATEGORIES:
        scorer_mode = "multi_turn_expected_call_match"
    elif expected_calls:
        scorer_mode = "expected_call_match"
    elif answer_row is None and category != "irrelevance":
        scorer_mode = "unsupported_missing_possible_answer"
    else:
        scorer_mode = "no_call_irrelevance"
    diagnostic_reason = (
        "diagnostic_only_missing_possible_answer"
        if scorer_mode == "unsupported_missing_possible_answer"
        else "pending_code_mode_full_visible_calibration"
    )
    return BFCLCase(
        case_id=f"bfcl:{category}:{row_id}",
        category=category,
        source_row=row,
        answer_row=answer_row,
        source_row_index=index,
        source_row_hash=source_row_hash,
        functions=functions,
        user_messages=messages,
        expected_calls=expected_calls,
        scorer_mode=scorer_mode,
        primary_eligible=False,
        primary_eligibility_reason=diagnostic_reason,
        prefix_dependency_class="tool_schema_required_by_design_pending_negative_controls",
    )


def normalize_functions(row: dict[str, Any], expected_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw_functions = row.get("function")
    if isinstance(raw_functions, list):
        return [function for function in raw_functions if isinstance(function, dict)]
    if isinstance(raw_functions, dict):
        return [raw_functions]
    if isinstance(raw_functions, str) and raw_functions.strip():
        return [
            {
                "name": raw_functions.strip(),
                "description": "BFCL chatable function string.",
                "parameters": {"type": "dict", "properties": {}},
            }
        ]
    path = row.get("path")
    names: list[str] = []
    if isinstance(path, list):
        names.extend(str(item) for item in path if item)
    names.extend(call["name"] for call in expected_calls if call.get("name"))
    seen: set[str] = set()
    functions: list[dict[str, Any]] = []
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        functions.append(
            {
                "name": name,
                "description": "Synthetic BFCL multi-turn tool entry derived from source path/answer metadata.",
                "parameters": {"type": "dict", "properties": {}},
            }
        )
    return functions


def function_catalog_text(functions: list[dict[str, Any]]) -> str:
    return canonical_json(functions)


def compact_function_evidence(functions: list[dict[str, Any]]) -> str:
    entries = []
    for function in functions:
        name = str(function.get("name", ""))
        description = str(function.get("description", ""))
        entries.append(f"- {name}: {description}")
    return "\n".join(entries)


def stable_prefix(case: BFCLCase, *, code_mode: bool) -> str:
    mode = "Code mode hidden-tool" if code_mode else "direct visible-tool"
    contract = (
        "Output one EXEC JSON line using the hidden tools API."
        if code_mode
        else "Output one ACTION JSON line using the visible tool schema."
    )
    return (
        "SYSTEM:\n"
        f"You are evaluating BFCL benchmark row {case.source_row.get('id', case.case_id)} under a {mode} harness.\n\n"
        "BENCHMARK:\n"
        "benchmark_id = BFCL\n"
        f"benchmark_checkpoint = {BFCL_LEADERBOARD_CHECKPOINT}\n"
        f"dataset_revision = {BFCL_DATASET_REVISION}\n"
        f"category = {case.category}\n\n"
        "TOOL/FUNCTION CATALOG:\n"
        f"{function_catalog_text(case.functions)}\n\n"
        "OUTPUT CONTRACT:\n"
        f"PTI protocol version = {PROMPT_PROTOCOL_VERSION}\n"
        f"{contract}\n"
        "Return only the function call plan, not a natural-language answer.\n"
        "If no provided function can satisfy the user request, output an empty call list.\n"
        "Count the independent operations requested by the user before emitting calls; emit exactly those calls.\n"
        "Do not emit helper, search, validation, explanation, or planning calls.\n"
        "Use function names and parameter names exactly as written in the catalog.\n"
        "Do not invent functions, parameters, or values that are not supported by the user request and schema.\n"
        "Omit optional/default parameters unless the user request clearly specifies them."
        "\nPTI v3 repair boundary: if a validator asks for repair, use only the user request, catalog, prior output, and schema errors."
    )


def tail_prompt(case: BFCLCase) -> str:
    return "BFCL USER REQUEST:\n" + user_query_text(case.user_messages)


def expected_answer_text(case: BFCLCase) -> str:
    return canonical_json(case.expected_calls)


def prompt_parts(case: BFCLCase, control_id: str) -> dict[str, str]:
    code_mode = control_id != "direct_full_visible_tools"
    stable = stable_prefix(case, code_mode=code_mode)
    tail = tail_prompt(case)
    full = f"{stable}\n\n{tail}"
    visible = tail
    compact = ""
    if control_id in {"direct_full_visible_tools", "code_mode_full_visible"}:
        visible = full
    elif control_id == "compact_visible_evidence_code_mode":
        compact = compact_function_evidence(case.functions)
        visible = f"{tail}\n\nVISIBLE FUNCTION EVIDENCE:\n{compact}"
    if control_id == "direct_full_visible_tools":
        visible = f"{visible}\n\nDIRECT VISIBLE TOOL SCHEMAS:\n{function_catalog_text(case.functions)}"
    return {
        "stable_prefix": stable,
        "tail_prompt": tail,
        "full_prompt": full,
        "visible_prompt": visible,
        "compact_evidence": compact,
    }


def prompt_sizes(parts: dict[str, str]) -> dict[str, int]:
    return {
        "stable_prefix_bytes": len(parts["stable_prefix"].encode("utf-8")),
        "stable_prefix_tokens": harness.count_tokens_approx(parts["stable_prefix"]),
        "tail_bytes": len(parts["tail_prompt"].encode("utf-8")),
        "tail_tokens": harness.count_tokens_approx(parts["tail_prompt"]),
        "visible_evidence_bytes": len(parts["compact_evidence"].encode("utf-8")),
        "visible_evidence_tokens": harness.count_tokens_approx(parts["compact_evidence"]),
        "full_prompt_bytes": len(parts["full_prompt"].encode("utf-8")),
        "full_prompt_tokens": harness.count_tokens_approx(parts["full_prompt"]),
        "visible_prompt_bytes": len(parts["visible_prompt"].encode("utf-8")),
        "visible_prompt_tokens": harness.count_tokens_approx(parts["visible_prompt"]),
    }


def prompt_hashes(parts: dict[str, str], case: BFCLCase) -> dict[str, str]:
    return {
        "stable_prefix_hash": sha256_text(parts["stable_prefix"]),
        "tail_hash": sha256_text(parts["tail_prompt"]),
        "full_prompt_hash": sha256_text(parts["full_prompt"]),
        "visible_prompt_hash": sha256_text(parts["visible_prompt"]),
        "prompt_protocol_hash": sha256_text(PROMPT_PROTOCOL_VERSION),
        "source_row_hash": case.source_row_hash,
        "function_catalog_hash": json_hash(case.functions),
        "expected_call_hash": json_hash(case.expected_calls),
    }


def bfcl_tool_entries(case: BFCLCase) -> list[dict[str, Any]]:
    entries = []
    for function in case.functions:
        name = str(function.get("name", ""))
        entries.append(
            {
                "tool_id": f"bfcl:function:{name}",
                "name": name,
                "namespace": "bfcl",
                "description": str(function.get("description", "")),
                "tags": ["bfcl", case.category],
                "input_schema": function.get("parameters", {}),
            }
        )
    return entries


def source_provenance(case: BFCLCase) -> dict[str, Any]:
    row_id = str(case.source_row.get("id") or f"{case.category}_{case.source_row_index}")
    source_file = BFCL_CATEGORY_FILES[case.category]
    release = "BFCL_v4" if source_file.startswith("BFCL_v4") else "BFCL_v3"
    return {
        "benchmark_id": "BFCL",
        "benchmark_release": release,
        "leaderboard_checkpoint": BFCL_LEADERBOARD_CHECKPOINT,
        "dataset_revision": BFCL_DATASET_REVISION,
        "dataset_url": f"https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard/tree/{BFCL_DATASET_REVISION}",
        "eval_package": BFCL_EVAL_PACKAGE,
        "license_id": "apache-2.0",
        "source_category": case.category,
        "source_file": source_file,
        "source_answer_file": (
            f"possible_answer/{source_file}" if case.answer_row is not None else None
        ),
        "source_row_id": row_id,
        "source_row_index": case.source_row_index,
        "source_row_locator": f"{BFCL_CATEGORY_FILES[case.category]}:{case.source_row_index}:{row_id}",
        "source_row_hash": case.source_row_hash,
        "answer_row_hash": json_hash(case.answer_row) if case.answer_row is not None else None,
        "source_fields_used": source_fields_used(case.source_row, case.answer_row),
        "source_fields_excluded": source_fields_excluded(case.source_row, case.answer_row),
        "transform_version": TRANSFORM_VERSION,
        "transform_hash": json_hash(
            {
                "adapter": ADAPTER_VERSION,
                "transform": TRANSFORM_VERSION,
                "category": case.category,
                "row_id": row_id,
            }
        ),
    }


def control_packet(case: BFCLCase, control_id: str) -> dict[str, Any]:
    if control_id not in CONTROL_IDS:
        raise ValueError(f"unsupported control: {control_id}")
    parts = prompt_parts(case, control_id)
    expected_calls = case.expected_calls
    expected_to_pass = control_id not in NEGATIVE_CONTROLS
    row_id = str(case.source_row.get("id") or f"{case.category}_{case.source_row_index}")
    unsupported_scorer_features = []
    scorer_limitations = [
        "No model smoke may use categories whose BFCL-native semantics cannot be represented by this adapter.",
        "This adapter reconstructs expected function-call matching from BFCL possible_answer rows; it is not a substitute for BFCL executable/live environment scoring.",
    ]
    if case.scorer_mode == "unsupported_missing_possible_answer":
        unsupported_scorer_features.append("missing_possible_answer")
        scorer_limitations.append(
            "This row is diagnostic-only because the pinned BFCL source has no possible_answer row for deterministic scoring."
        )
    return {
        "experiment_id": EXPERIMENT_ID,
        "adapter_version": ADAPTER_VERSION,
        "harness_version": harness.HARNESS_VERSION,
        "prompt_protocol_version": PROMPT_PROTOCOL_VERSION,
        "case_id": case.case_id,
        "task_bucket": f"bfcl_{case.category}",
        "control_id": control_id,
        "code_mode_route": "bfcl_code_mode" if control_id != "direct_full_visible_tools" else "bfcl_direct_tools",
        "capsule_route": {
            "code_mode_native_live_append": "seq_file_live_append",
            "code_mode_restored_kv_capsule": "seq_file_restored_capsule",
            "code_mode_wrong_capsule_negative": "seq_file_wrong_capsule",
        }.get(control_id),
        "expected_to_pass": expected_to_pass,
        "expected_answer": expected_answer_text(case),
        "expected_answer_hash": sha256_text(expected_answer_text(case)),
        "expected_calls": expected_calls,
        "expected_call_hash": json_hash(expected_calls),
        "expected_argument_hash": json_hash([call["arguments"] for call in expected_calls]),
        "required_tool_path": [call["name"] for call in expected_calls],
        "session_id": f"bfcl-session:{case.case_id}",
        "access_key": "bfcl-source-context" if control_id != "code_mode_wrong_capsule_negative" else "wrong-bfcl-source-context",
        "catalog_id": f"bfcl:{case.category}:{row_id}",
        "catalog_hash": json_hash(case.functions),
        "all_tools": bfcl_tool_entries(case),
        "model_loop_protocol": "BFCL_CODE_MODE_PROTOCOL",
        "stable_prefix": parts["stable_prefix"],
        "tail_prompt": parts["tail_prompt"],
        "full_prompt": parts["full_prompt"],
        "visible_prompt": parts["visible_prompt"],
        "compact_evidence": parts["compact_evidence"],
        "prompt_sizes": prompt_sizes(parts),
        "hashes": prompt_hashes(parts, case),
        "source_provenance": source_provenance(case),
        "scoring": {
            "native_bfcl_scorer_used": False,
            "scorer_kind": "deterministic_expected_call_adapter",
            "native_scorer_name": "bfcl_expected_call_scorer",
            "native_scorer_version": SCORER_VERSION,
            "scorer_mode": case.scorer_mode,
            "unsupported_scorer_features": unsupported_scorer_features,
            "scorer_limitations": scorer_limitations,
        },
        "pti_runtime": {
            "runtime_version": PROMPT_PROTOCOL_VERSION,
            "schema_validator_version": PTI_SCHEMA_VALIDATOR_VERSION,
            "repair_prompt_version": "bfcl_pti_schema_only_repair_prompt_v1",
            "inference_allowed_inputs": [
                "source_user_request",
                "visible_function_catalog_schema",
                "model_output",
                "parser_decoder_errors",
                "schema_validator_errors",
                "user_request_literal_diagnostics",
                "user_request_operation_count_diagnostics",
            ],
            "inference_disallowed_inputs": [
                "possible_answer",
                "official_expected_calls",
                "answer_key_postprocessing",
            ],
        },
        "eligibility": {
            "primary_eligible": case.primary_eligible,
            "primary_eligibility_reason": case.primary_eligibility_reason,
            "prefix_dependency_class": case.prefix_dependency_class,
        },
        "host_boundary": {
            "template": None,
            "template_alias": None,
            "alias_registry_version": None,
            "host_filled_args": [],
            "final_source": None,
            "parse_status": "not_run_no_model_materialization",
        },
        "wrong_capsule": {
            "source_case_id": None,
            "source_catalog_hash": None,
            "mismatch_rationale": (
                "runner_must_restore_prefix_from_a_different_bfcl_case"
                if control_id == "code_mode_wrong_capsule_negative"
                else None
            ),
        },
        "fixture": {
            "source_row": case.source_row,
            "answer_row": case.answer_row,
            "functions": case.functions,
            "expected_calls": expected_calls,
        },
    }


def normalize_value(value: Any) -> Any:
    return tool_surface.normalize_value(value)


def normalize_generated_json_keys(value: Any) -> Any:
    return tool_surface.normalize_wrapper_keys(value)


def expected_value_matches(expected: Any, actual: Any) -> bool:
    if isinstance(expected, list):
        return any(expected_value_matches(option, actual) for option in expected)
    if isinstance(expected, dict):
        normalized_actual = normalize_value(actual)
        if not isinstance(normalized_actual, dict):
            return False
        expected_dict = {str(key): value for key, value in expected.items()}
        if any(key not in expected_dict for key in normalized_actual):
            return False
        for key, nested_expected in expected_dict.items():
            if key not in normalized_actual:
                return False
            if not expected_value_matches(nested_expected, normalized_actual[key]):
                return False
        return True

    normalized_actual = normalize_value(actual)
    normalized_expected = normalize_value(expected)
    if normalized_actual == normalized_expected:
        return True
    return str(normalized_actual) == str(normalized_expected)


def value_matches(expected_options: list[Any], actual: Any) -> bool:
    for option in expected_options:
        if expected_value_matches(option, actual):
            return True
    return False


def actual_call_name(actual: dict[str, Any]) -> str:
    return tool_surface.actual_call_name(actual)


def actual_call_arguments(actual: dict[str, Any]) -> dict[str, Any]:
    return tool_surface.actual_call_arguments(actual)


def call_names_match(expected_name: str, actual_name: str) -> bool:
    if actual_name == expected_name:
        return True
    return actual_name.split(".")[-1] == expected_name.split(".")[-1]


def expected_options_allow_omission(expected_options: list[Any]) -> bool:
    return any(normalize_value(option) == "" for option in expected_options)


def optional_omitted_arguments(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    if not call_names_match(str(expected["name"]), actual_call_name(actual)):
        return []
    actual_args = actual_call_arguments(actual)
    expected_args = dict(expected.get("arguments") or {})
    return [
        key
        for key, options in expected_args.items()
        if key not in actual_args and expected_options_allow_omission(list(options))
    ]


def call_matches(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    actual_name = actual_call_name(actual)
    if not call_names_match(str(expected["name"]), actual_name):
        return False
    actual_args = actual_call_arguments(actual)
    expected_args = dict(expected.get("arguments") or {})
    if any(key not in expected_args for key in actual_args):
        return False
    for key, options in expected_args.items():
        expected_options = list(options)
        if key not in actual_args:
            if expected_options_allow_omission(expected_options):
                continue
            return False
        if not value_matches(expected_options, actual_args[key]):
            return False
    return True


def score_calls(expected_calls: list[dict[str, Any]], parsed_calls: list[dict[str, Any]]) -> dict[str, Any]:
    unmatched = list(parsed_calls)
    matched: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    optional_omissions: list[dict[str, Any]] = []
    for expected in expected_calls:
        found_index = None
        for index, actual in enumerate(unmatched):
            if call_matches(expected, actual):
                found_index = index
                break
        if found_index is None:
            missing.append(expected)
        else:
            actual = unmatched.pop(found_index)
            matched.append(actual)
            omitted = optional_omitted_arguments(expected, actual)
            if omitted:
                optional_omissions.append({"name": expected["name"], "arguments": omitted})
    extra = unmatched
    passed = not missing and not extra
    return {
        "passed": passed,
        "expected_count": len(expected_calls),
        "parsed_count": len(parsed_calls),
        "matched_count": len(matched),
        "missing": missing,
        "extra": extra,
        "optional_omitted_arguments": optional_omissions,
        "optional_omitted_argument_count": sum(len(item["arguments"]) for item in optional_omissions),
        "expected_call_hash": json_hash(expected_calls),
        "parsed_call_hash": json_hash(parsed_calls),
        "expected_argument_hash": json_hash([call.get("arguments", {}) for call in expected_calls]),
        "parsed_argument_hash": json_hash([actual_call_arguments(call) for call in parsed_calls]),
    }


def validate_external_provenance(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    provenance = packet.get("source_provenance")
    if not isinstance(provenance, dict):
        return ["missing_source_provenance"]
    required = [
        "benchmark_id",
        "dataset_revision",
        "source_category",
        "source_row_locator",
        "source_row_hash",
        "source_fields_used",
        "transform_version",
        "transform_hash",
    ]
    for key in required:
        if not provenance.get(key):
            errors.append(f"missing_source_provenance.{key}")
    if provenance.get("benchmark_id") != "BFCL":
        errors.append("unsupported_benchmark_id")
    return errors


def primary_selection_status(packet: dict[str, Any]) -> dict[str, Any]:
    errors = validate_external_provenance(packet)
    scoring = packet.get("scoring") if isinstance(packet.get("scoring"), dict) else {}
    unsupported = list(scoring.get("unsupported_scorer_features") or [])
    if unsupported:
        errors.append("unsupported_scorer_features")
    eligibility = packet.get("eligibility") if isinstance(packet.get("eligibility"), dict) else {}
    if not eligibility.get("primary_eligible"):
        errors.append(str(eligibility.get("primary_eligibility_reason") or "not_primary_eligible"))
    if not eligibility.get("prefix_dependency_class"):
        errors.append("missing_prefix_dependency_class")
    return {
        "primary_ready": not errors,
        "errors": errors,
        "primary_eligible": bool(eligibility.get("primary_eligible")),
        "primary_eligibility_reason": eligibility.get("primary_eligibility_reason"),
        "prefix_dependency_class": eligibility.get("prefix_dependency_class"),
    }


def classify_control_scorer_outcome(packet: dict[str, Any], scorer_result: dict[str, Any]) -> str | None:
    control_id = str(packet.get("control_id"))
    passed = bool(scorer_result.get("passed"))
    expected_to_pass = bool(packet.get("expected_to_pass", True))
    if control_id == "code_mode_fresh_tail_only" and passed:
        return "fresh_tail_leak_or_non_prefix_dependent"
    if control_id == "code_mode_wrong_capsule_negative" and passed:
        return "wrong_capsule_leak_or_scorer_looseness"
    if control_id in NEGATIVE_CONTROLS and not passed:
        return "negative_control_closed"
    if expected_to_pass and not passed:
        return "positive_control_failure"
    if expected_to_pass and passed:
        return "positive_control_passed"
    return None


def coerce_call_object(value: Any) -> list[dict[str, Any]]:
    return [call.as_call_dict() for call in tool_surface.coerce_call_object(value)]


def parse_calls_from_json_text(text: str) -> list[dict[str, Any]]:
    return [call.as_call_dict() for call in tool_surface.parse_calls_from_json_text(text)]


def parse_calls_from_generated_text(text: str) -> list[dict[str, Any]]:
    """Extract the first complete BFCL-style call payload from raw model text."""
    return tool_surface.parse_calls_from_generated_text(text)


def _function_catalog_by_name(functions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(function.get("name")): function for function in functions if function.get("name")}


def _resolve_catalog_function(
    catalog: dict[str, dict[str, Any]], emitted_name: str
) -> tuple[str | None, dict[str, Any] | None, list[str], dict[str, Any] | None]:
    if emitted_name in catalog:
        return emitted_name, catalog[emitted_name], [], None
    suffix_matches = [
        name for name in catalog if name.rsplit(".", 1)[-1] == emitted_name or name.rsplit(":", 1)[-1] == emitted_name
    ]
    if len(suffix_matches) == 1:
        name = suffix_matches[0]
        return name, catalog[name], ["function_suffix_match"], None
    if len(suffix_matches) > 1:
        return (
            None,
            None,
            [],
            {
                "code": "ambiguous_function",
                "function": emitted_name,
                "candidates": suffix_matches,
            },
        )
    return None, None, [], {"code": "unknown_function", "function": emitted_name}


def _parameter_schema(function: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], set[str]]:
    parameters = function.get("parameters") if isinstance(function.get("parameters"), dict) else {}
    properties = parameters.get("properties") if isinstance(parameters.get("properties"), dict) else {}
    required_raw = parameters.get("required") if isinstance(parameters.get("required"), list) else []
    required = {str(item) for item in required_raw}
    return {str(key): value for key, value in properties.items() if isinstance(value, dict)}, required


def _schema_type(schema: dict[str, Any]) -> str | None:
    raw_type = schema.get("type")
    if isinstance(raw_type, list):
        raw_type = next((item for item in raw_type if item != "null"), None)
    if raw_type is None:
        return None
    normalized = str(raw_type).lower()
    aliases = {
        "int": "integer",
        "long": "integer",
        "float": "number",
        "double": "number",
        "dict": "object",
        "map": "object",
        "hashmap": "object",
        "boolean": "boolean",
        "bool": "boolean",
        "array": "array",
        "list": "array",
        "string": "string",
        "str": "string",
    }
    return aliases.get(normalized, normalized)


def _value_matches_schema_type(value: Any, expected_type: str | None) -> bool:
    if expected_type is None or expected_type in {"any", "unknown"}:
        return True
    if value is None:
        return True
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "object":
        return isinstance(value, dict)
    return True


def _validate_value_against_schema(
    value: Any,
    schema: dict[str, Any],
    *,
    path: str,
    call_index: int,
    function: str,
) -> list[dict[str, Any]]:
    expected_type = _schema_type(schema)
    errors: list[dict[str, Any]] = []
    if not _value_matches_schema_type(value, expected_type):
        errors.append(
            {
                "code": "type_mismatch" if "." not in path else "nested_type_mismatch",
                "call_index": call_index,
                "function": function,
                "argument": path,
                "expected_type": expected_type,
                "actual_type": type(value).__name__,
            }
        )
        return errors
    if value is None:
        return errors
    if expected_type == "object" and isinstance(value, dict):
        properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
        for key, child in value.items():
            child_schema = properties.get(str(key))
            if isinstance(child_schema, dict):
                errors.extend(
                    _validate_value_against_schema(
                        child,
                        child_schema,
                        path=f"{path}.{key}",
                        call_index=call_index,
                        function=function,
                    )
                )
    if expected_type == "array" and isinstance(value, list):
        item_schema = schema.get("items") if isinstance(schema.get("items"), dict) else None
        if item_schema:
            for index, child in enumerate(value):
                errors.extend(
                    _validate_value_against_schema(
                        child,
                        item_schema,
                        path=f"{path}[{index}]",
                        call_index=call_index,
                        function=function,
                    )
                )
    return errors


def _identifier_like_schema(argument: str, schema: dict[str, Any]) -> bool:
    haystack = f"{argument} {schema.get('description', '')} {schema.get('title', '')}".lower()
    return any(token in haystack for token in ("callback", "function", "identifier", "handler", "method"))


def _exact_identifier_tokens(text: str) -> set[str]:
    tokens = set(re.findall(r"\b[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*\b", text))
    boring = {
        "a",
        "an",
        "and",
        "as",
        "callback",
        "call",
        "function",
        "handler",
        "method",
        "the",
        "to",
        "use",
        "with",
    }
    return {token for token in tokens if token.lower() not in boring and (re.search(r"[A-Z_$]", token) or "." in token)}


def _literal_preservation_errors(
    *,
    argument: str,
    value: Any,
    schema: dict[str, Any],
    user_request: str,
    call_index: int,
    function: str,
) -> list[dict[str, Any]]:
    if not isinstance(value, str) or not _identifier_like_schema(argument, schema):
        return []
    candidates = _exact_identifier_tokens(user_request)
    enum_values = schema.get("enum") if isinstance(schema.get("enum"), list) else []
    candidates.update(str(item) for item in enum_values if isinstance(item, str))
    if not candidates or value in candidates:
        return []
    value_words = set(re.findall(r"[A-Za-z0-9_$]+", value))
    for candidate in sorted(candidates, key=len, reverse=True):
        if candidate not in value and candidate not in value_words:
            return [
                {
                    "code": "literal_preservation_suspect",
                    "call_index": call_index,
                    "function": function,
                    "argument": argument,
                    "candidate_literal": candidate,
                    "actual_value": value,
                }
            ]
    return []


def infer_minimum_call_count(user_request: str, functions: list[dict[str, Any]]) -> int | None:
    """Best-effort generic operation-count diagnostic from request text only."""
    text = " ".join(user_request.strip().split())
    if not text:
        return None
    word_numbers = {
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }
    word_pattern = "|".join(word_numbers)
    word_count = re.search(
        rf"\b({word_pattern})\s+(?:different\s+|separate\s+|independent\s+)?(?:calls|operations|tasks|requests|items|songs|calculations|queries|shapes)\b",
        text,
        re.I,
    )
    if word_count:
        return word_numbers[word_count.group(1).lower()]
    explicit = re.search(r"\b(?:exactly|all|both|these)?\s*(\d+)\s+(?:independent\s+)?(?:calls|operations|tasks|requests|items)\b", text, re.I)
    if explicit:
        return max(1, int(explicit.group(1)))
    if re.search(r"\b(both|respectively)\b", text, re.I):
        return 2
    # Useful for BFCL parallel-style requests: "draw a rectangle and a circle"
    object_pair = re.search(
        r"\b(?:a|an|the)\s+([A-Za-z][A-Za-z0-9_-]*)\s+(?:and|plus)\s+(?:a|an|the)\s+([A-Za-z][A-Za-z0-9_-]*)\b",
        text,
        re.I,
    )
    if object_pair and object_pair.group(1).lower() != object_pair.group(2).lower():
        return 2
    if len(functions) == 1:
        function_name = str(functions[0].get("name", "")).rsplit(".", 1)[-1].lower()
        if function_name and len(re.findall(rf"\b{re.escape(function_name)}\b", text.lower())) > 1:
            return 2
    return None


def validate_pti_calls_against_catalog(
    functions: list[dict[str, Any]], calls: list[dict[str, Any]], *, user_request: str = ""
) -> dict[str, Any]:
    """Validate parsed PTI calls against visible function schema only.

    This validator intentionally uses no BFCL possible_answer rows. It is safe
    for inference-time telemetry and schema-only repair prompting.
    """
    catalog = _function_catalog_by_name(functions)
    errors: list[dict[str, Any]] = []
    canonical_calls: list[dict[str, Any]] = []
    for call_index, call in enumerate(calls):
        source_name = actual_call_name(call)
        arguments = actual_call_arguments(call)
        name, function, normalizations, resolution_error = _resolve_catalog_function(catalog, source_name)
        if resolution_error is not None:
            errors.append({"call_index": call_index, **resolution_error})
            continue
        assert name is not None
        assert function is not None
        canonical_calls.append(
            {
                "name": name,
                "source_name": source_name,
                "arguments": arguments,
                "normalizations": normalizations,
            }
        )
        if function is None:
            continue
        properties, required = _parameter_schema(function)
        for key in sorted(required):
            if key not in arguments:
                errors.append(
                    {
                        "code": "missing_required_argument",
                        "call_index": call_index,
                        "function": name,
                        "argument": key,
                    }
                )
        for key, value in arguments.items():
            schema = properties.get(str(key))
            if schema is None:
                case_style_hint = "camelCase_parameter_expected" if any(re.search(r"[a-z][A-Z]", item) for item in properties) else None
                errors.append(
                    {
                        "code": "unexpected_argument",
                        "call_index": call_index,
                        "function": name,
                        "argument": str(key),
                        **({"hint": case_style_hint} if case_style_hint else {}),
                    }
                )
                continue
            errors.extend(
                _validate_value_against_schema(value, schema, path=str(key), call_index=call_index, function=name)
            )
            errors.extend(
                _literal_preservation_errors(
                    argument=str(key),
                    value=value,
                    schema=schema,
                    user_request=user_request,
                    call_index=call_index,
                    function=name,
                )
            )
    minimum_call_count = infer_minimum_call_count(user_request, functions)
    if minimum_call_count is not None and len(canonical_calls) < minimum_call_count:
        errors.append(
            {
                "code": "likely_call_count_mismatch",
                "expected_min_calls": minimum_call_count,
                "actual_calls": len(canonical_calls),
                "evidence": "user_request_only",
            }
        )
    return {
        "validator_version": PTI_SCHEMA_VALIDATOR_VERSION,
        "valid": not errors,
        "call_count": len(canonical_calls),
        "error_count": len(errors),
        "errors": errors,
        "canonical_calls": canonical_calls,
        "minimum_call_count": minimum_call_count,
    }


def build_schema_only_repair_prompt(
    *,
    user_request: str,
    functions: list[dict[str, Any]],
    model_output: str,
    calls: list[dict[str, Any]],
    validation: dict[str, Any],
) -> str:
    """Build a paper-safe repair prompt from schema and validator errors only."""
    payload = {
        "user_request": user_request,
        "visible_function_catalog": functions,
        "previous_model_output": model_output,
        "parsed_call_plan": calls,
        "validator_errors": validation.get("errors", []),
    }
    text = canonical_json(payload)
    forbidden = ("possible_answer", "expected_answer", "expected_calls", "ground_truth")
    lowered = text.lower()
    if any(token in lowered for token in forbidden):
        raise ValueError("schema-only repair prompt received forbidden answer-key material")
    return (
        "SYSTEM:\n"
        "Repair this PTI call plan using only the user request, visible function catalog, "
        "previous model output, parsed call plan, and validator errors. Do not use or infer any answer key.\n\n"
        "VISIBLE FUNCTION CATALOG / USER REQUEST / VALIDATOR ERRORS:\n"
        f"{text}\n\n"
        "Return only the repaired function call list. Use no explanation."
    )


def materialize_cases(
    *,
    source_dir: Path | None,
    categories: list[str],
    per_category: int,
    remote_base: str = REMOTE_BASE,
) -> list[BFCLCase]:
    cases: list[BFCLCase] = []
    for category in categories:
        if category not in BFCL_CATEGORY_FILES:
            raise ValueError(f"unsupported BFCL category: {category}")
        file_name = BFCL_CATEGORY_FILES[category]
        rows = load_jsonl(source_dir, file_name, remote_base=remote_base)
        answers = load_possible_answers(source_dir, file_name, remote_base=remote_base)
        for index, row in enumerate(rows[:per_category]):
            answer_row = answers.get(str(row["id"]))
            cases.append(make_bfcl_case(category, row, answer_row, index))
    return cases


def compatibility_audit(cases: list[BFCLCase]) -> dict[str, Any]:
    by_category: dict[str, dict[str, Any]] = {}
    for case in cases:
        item = by_category.setdefault(
            case.category,
            {
                "case_count": 0,
                "scoreable_case_count": 0,
                "diagnostic_only_case_count": 0,
                "expected_call_count": 0,
                "scorer_modes": {},
                "unsupported_scorer_features": set(),
                "function_catalog_empty_count": 0,
                "multi_turn": case.category in MULTI_TURN_CATEGORIES,
                "live_or_api": case.category in LIVE_OR_API_CATEGORIES,
            },
        )
        item["case_count"] += 1
        item["expected_call_count"] += len(case.expected_calls)
        item["scorer_modes"][case.scorer_mode] = item["scorer_modes"].get(case.scorer_mode, 0) + 1
        if case.scorer_mode == "unsupported_missing_possible_answer":
            item["diagnostic_only_case_count"] += 1
            item["unsupported_scorer_features"].add("missing_possible_answer")
        else:
            item["scoreable_case_count"] += 1
        if not case.functions:
            item["function_catalog_empty_count"] += 1

    normalized_by_category = {}
    for category, item in sorted(by_category.items()):
        normalized = dict(item)
        normalized["unsupported_scorer_features"] = sorted(item["unsupported_scorer_features"])
        normalized_by_category[category] = normalized

    scoreable = sum(item["scoreable_case_count"] for item in normalized_by_category.values())
    diagnostic = sum(item["diagnostic_only_case_count"] for item in normalized_by_category.values())
    transform_errors = [
        category
        for category, item in normalized_by_category.items()
        if item["function_catalog_empty_count"] and category not in {"irrelevance"}
    ]
    return {
        "status": "bfcl_compatibility_audit_passed" if not transform_errors else "bfcl_compatibility_audit_failed",
        "category_count": len(normalized_by_category),
        "case_count": len(cases),
        "scoreable_case_count": scoreable,
        "diagnostic_only_case_count": diagnostic,
        "scoreable_categories": sorted(
            category for category, item in normalized_by_category.items() if item["scoreable_case_count"]
        ),
        "diagnostic_only_categories": sorted(
            category for category, item in normalized_by_category.items() if item["diagnostic_only_case_count"]
        ),
        "transform_error_categories": transform_errors,
        "categories": normalized_by_category,
    }


def materialize_control_packets(cases: list[BFCLCase], controls: list[str] | None = None) -> list[dict[str, Any]]:
    selected_controls = controls or CONTROL_IDS
    return [control_packet(case, control_id) for case in cases for control_id in selected_controls]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def summarize_packets(packets: list[dict[str, Any]]) -> dict[str, Any]:
    cases = {(row["case_id"], row["source_provenance"]["source_category"]) for row in packets}
    categories = sorted({category for _, category in cases})
    by_category = {}
    for category in categories:
        case_ids = sorted(case_id for case_id, item_category in cases if item_category == category)
        by_category[category] = {
            "case_count": len(case_ids),
            "control_record_count": sum(
                1 for row in packets if row["source_provenance"]["source_category"] == category
            ),
            "case_ids": case_ids,
        }
    return {
        "experiment_id": EXPERIMENT_ID,
        "adapter_version": ADAPTER_VERSION,
        "transform_version": TRANSFORM_VERSION,
        "scorer_version": SCORER_VERSION,
        "bfcl_dataset_revision": BFCL_DATASET_REVISION,
        "bfcl_leaderboard_checkpoint": BFCL_LEADERBOARD_CHECKPOINT,
        "controls": CONTROL_IDS,
        "case_count": len({row["case_id"] for row in packets}),
        "control_record_count": len(packets),
        "categories": by_category,
        "scoreable_case_count": sum(
            1
            for case_id, _ in cases
            if any(
                row["case_id"] == case_id
                and row.get("scoring", {}).get("scorer_mode") != "unsupported_missing_possible_answer"
                for row in packets
            )
        ),
        "diagnostic_only_case_count": sum(
            1
            for case_id, _ in cases
            if any(
                row["case_id"] == case_id
                and row.get("scoring", {}).get("scorer_mode") == "unsupported_missing_possible_answer"
                for row in packets
            )
        ),
        "status": "no_model_materialization_complete",
        "model_run_status": "not_started",
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize BFCL cases for the Code-mode KV control ladder.")
    parser.add_argument("--source-dir", type=Path, help="Local BFCL dataset directory. If omitted, raw HF URLs are used.")
    parser.add_argument(
        "--category",
        action="append",
        choices=sorted(BFCL_CATEGORY_FILES),
        help="BFCL category to materialize. May be repeated.",
    )
    parser.add_argument("--per-category", type=int, default=1)
    parser.add_argument("--out", type=Path, required=True, help="Output control packet JSONL path.")
    parser.add_argument("--summary-out", type=Path, help="Optional summary JSON path.")
    parser.add_argument(
        "--compatibility-audit-out",
        type=Path,
        help="Optional BFCL category compatibility audit JSON path.",
    )
    parser.add_argument(
        "--all-compatibility-categories",
        action="store_true",
        help="Materialize the broad BFCL support surface, including live/API and multi-turn diagnostic categories.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    categories = args.category or (
        DEFAULT_COMPATIBILITY_CATEGORIES
        if args.all_compatibility_categories
        else ["simple", "multiple", "parallel", "parallel_multiple", "irrelevance"]
    )
    cases = materialize_cases(source_dir=args.source_dir, categories=categories, per_category=args.per_category)
    packets = materialize_control_packets(cases)
    write_jsonl(args.out, packets)
    if args.summary_out:
        write_json(args.summary_out, summarize_packets(packets))
    if args.compatibility_audit_out:
        write_json(args.compatibility_audit_out, compatibility_audit(cases))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
