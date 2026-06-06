#!/usr/bin/env python3
"""No-model BFCL adapter for the Code-mode KV capsule control ladder.

This module intentionally stops before any llama.cpp/model execution. It
materializes BFCL source rows into the same seven-control experiment shape and
reconstructs a deterministic expected-call scorer from upstream BFCL JSONL and
possible_answer JSONL files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
PROMPT_PROTOCOL_VERSION = "bfcl_openclaw_code_mode_compiled_template_v1"
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

INITIAL_CATEGORY_FILES = {
    "simple": "BFCL_v3_simple.json",
    "multiple": "BFCL_v3_multiple.json",
    "parallel": "BFCL_v3_parallel.json",
    "parallel_multiple": "BFCL_v3_parallel_multiple.json",
    "irrelevance": "BFCL_v3_irrelevance.json",
    "exec_simple": "BFCL_v3_exec_simple.json",
    "exec_multiple": "BFCL_v3_exec_multiple.json",
    "exec_parallel": "BFCL_v3_exec_parallel.json",
    "exec_parallel_multiple": "BFCL_v3_exec_parallel_multiple.json",
}


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


def expected_calls_from_answer(answer_row: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not answer_row:
        return []
    calls: list[dict[str, Any]] = []
    for call_spec in answer_row.get("ground_truth", []):
        if not isinstance(call_spec, dict):
            continue
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
    return calls


def source_fields_used(row: dict[str, Any], answer_row: dict[str, Any] | None) -> list[str]:
    fields = ["id", "question", "function"]
    if answer_row is not None:
        fields.append("possible_answer.ground_truth")
    return fields


def source_fields_excluded(row: dict[str, Any], answer_row: dict[str, Any] | None) -> list[str]:
    used = set(source_fields_used(row, answer_row))
    return sorted(key for key in row if key not in used)


def make_bfcl_case(category: str, row: dict[str, Any], answer_row: dict[str, Any] | None, index: int) -> BFCLCase:
    row_id = str(row["id"])
    source_row_hash = json_hash(row)
    expected_calls = expected_calls_from_answer(answer_row)
    functions = list(row.get("function") or [])
    messages = flatten_messages(row.get("question"))
    scorer_mode = "no_call_irrelevance" if not expected_calls else "expected_call_match"
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
        primary_eligibility_reason="pending_code_mode_full_visible_calibration",
        prefix_dependency_class="tool_schema_required_by_design_pending_negative_controls",
    )


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
        f"You are evaluating BFCL benchmark row {case.source_row['id']} under a {mode} harness.\n\n"
        "BENCHMARK:\n"
        "benchmark_id = BFCL\n"
        f"benchmark_checkpoint = {BFCL_LEADERBOARD_CHECKPOINT}\n"
        f"dataset_revision = {BFCL_DATASET_REVISION}\n"
        f"category = {case.category}\n\n"
        "TOOL/FUNCTION CATALOG:\n"
        f"{function_catalog_text(case.functions)}\n\n"
        "OUTPUT CONTRACT:\n"
        f"{contract}\n"
        "Do not invent functions. Do not call functions that are irrelevant to the user request. "
        "Return only the function call plan, not a natural-language answer."
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
    return {
        "benchmark_id": "BFCL",
        "benchmark_release": "BFCL_v3",
        "leaderboard_checkpoint": BFCL_LEADERBOARD_CHECKPOINT,
        "dataset_revision": BFCL_DATASET_REVISION,
        "dataset_url": f"https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard/tree/{BFCL_DATASET_REVISION}",
        "eval_package": BFCL_EVAL_PACKAGE,
        "license_id": "apache-2.0",
        "source_category": case.category,
        "source_file": INITIAL_CATEGORY_FILES[case.category],
        "source_answer_file": (
            f"possible_answer/{INITIAL_CATEGORY_FILES[case.category]}" if case.answer_row is not None else None
        ),
        "source_row_id": str(case.source_row["id"]),
        "source_row_index": case.source_row_index,
        "source_row_locator": f"{INITIAL_CATEGORY_FILES[case.category]}:{case.source_row_index}:{case.source_row['id']}",
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
                "row_id": case.source_row["id"],
            }
        ),
    }


def control_packet(case: BFCLCase, control_id: str) -> dict[str, Any]:
    if control_id not in CONTROL_IDS:
        raise ValueError(f"unsupported control: {control_id}")
    parts = prompt_parts(case, control_id)
    expected_calls = case.expected_calls
    expected_to_pass = control_id not in NEGATIVE_CONTROLS
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
        "catalog_id": f"bfcl:{case.category}:{case.source_row['id']}",
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
            "unsupported_scorer_features": [],
            "scorer_limitations": [
                "No model smoke may use categories whose BFCL-native semantics cannot be represented by this adapter.",
                "This adapter reconstructs expected function-call matching from BFCL possible_answer rows; it is not a substitute for BFCL executable/live environment scoring.",
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


def expected_options_allow_omission(expected_options: list[Any]) -> bool:
    return any(normalize_value(option) == "" for option in expected_options)


def optional_omitted_arguments(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    if actual_call_name(actual) != expected["name"]:
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
    if actual_name != expected["name"]:
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


def materialize_cases(
    *,
    source_dir: Path | None,
    categories: list[str],
    per_category: int,
    remote_base: str = REMOTE_BASE,
) -> list[BFCLCase]:
    cases: list[BFCLCase] = []
    for category in categories:
        if category not in INITIAL_CATEGORY_FILES:
            raise ValueError(f"unsupported initial BFCL category: {category}")
        file_name = INITIAL_CATEGORY_FILES[category]
        rows = load_jsonl(source_dir, file_name, remote_base=remote_base)
        answers = load_possible_answers(source_dir, file_name, remote_base=remote_base)
        for index, row in enumerate(rows[:per_category]):
            answer_row = answers.get(str(row["id"]))
            cases.append(make_bfcl_case(category, row, answer_row, index))
    return cases


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
        "status": "no_model_materialization_complete",
        "model_run_status": "not_started",
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize BFCL cases for the Code-mode KV control ladder.")
    parser.add_argument("--source-dir", type=Path, help="Local BFCL dataset directory. If omitted, raw HF URLs are used.")
    parser.add_argument(
        "--category",
        action="append",
        choices=sorted(INITIAL_CATEGORY_FILES),
        help="BFCL category to materialize. May be repeated.",
    )
    parser.add_argument("--per-category", type=int, default=1)
    parser.add_argument("--out", type=Path, required=True, help="Output control packet JSONL path.")
    parser.add_argument("--summary-out", type=Path, help="Optional summary JSON path.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    categories = args.category or ["simple", "multiple", "parallel", "parallel_multiple", "irrelevance"]
    cases = materialize_cases(source_dir=args.source_dir, categories=categories, per_category=args.per_category)
    packets = materialize_control_packets(cases)
    write_jsonl(args.out, packets)
    if args.summary_out:
        write_json(args.summary_out, summarize_packets(packets))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
