#!/usr/bin/env python3
"""Prepare and run the KV-capsule/PTI lane against official BFCL artifacts.

This wrapper keeps the leaderboard lane separate from the paper-selected
cohort. It stages BFCL package data, materializes our full control packet,
runs the existing model-bearing KV runner, and exports result files in the
directory shape expected by `bfcl-eval`.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


BENCHMARKS_DIR = Path(__file__).resolve().parent
if str(BENCHMARKS_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARKS_DIR))

import bfcl_code_mode_kv_adapter as adapter  # noqa: E402


TRACK_ROOT = BENCHMARKS_DIR.parents[1] / "02-quality-gated-stateful-kv-reuse"
DEFAULT_LANE_ROOT = TRACK_ROOT / "experiments" / "bfcl-official-kv-pti-leaderboard-lane"
DEFAULT_RUN_LABEL = "gemma4-kv-capsule-pti-bfcl-v4"
DEFAULT_MODEL_DIR = "gemma4-kv-capsule-pti"
DEFAULT_CONTROLS = "code_mode_restored_kv_capsule"
BFCL_PACKAGE = "bfcl-eval==2025.12.17"
BFCL_VERSION_PREFIX = "BFCL_v4"

OFFICIAL_SCORING_CATEGORIES = [
    "simple_python",
    "simple_java",
    "simple_javascript",
    "multiple",
    "parallel",
    "parallel_multiple",
    "irrelevance",
    "live_simple",
    "live_multiple",
    "live_parallel",
    "live_parallel_multiple",
    "live_irrelevance",
    "live_relevance",
    "multi_turn_base",
    "multi_turn_miss_func",
    "multi_turn_miss_param",
    "multi_turn_long_context",
    "web_search",
    "memory",
]

V4_TO_ADAPTER_ALIASES = {
    "multiple": "BFCL_v3_multiple.json",
    "parallel": "BFCL_v3_parallel.json",
    "parallel_multiple": "BFCL_v3_parallel_multiple.json",
    "irrelevance": "BFCL_v3_irrelevance.json",
    "live_simple": "BFCL_v3_live_simple.json",
    "live_multiple": "BFCL_v3_live_multiple.json",
    "live_parallel": "BFCL_v3_live_parallel.json",
    "live_parallel_multiple": "BFCL_v3_live_parallel_multiple.json",
    "live_irrelevance": "BFCL_v3_live_irrelevance.json",
    "live_relevance": "BFCL_v3_live_relevance.json",
    "multi_turn_base": "BFCL_v3_multi_turn_base.json",
    "multi_turn_miss_func": "BFCL_v3_multi_turn_miss_func.json",
    "multi_turn_miss_param": "BFCL_v3_multi_turn_miss_param.json",
    "multi_turn_long_context": "BFCL_v3_multi_turn_long_context.json",
}

GROUP_BY_CATEGORY = {
    "simple_python": "non_live",
    "simple_java": "non_live",
    "simple_javascript": "non_live",
    "multiple": "non_live",
    "parallel": "non_live",
    "parallel_multiple": "non_live",
    "irrelevance": "non_live",
    "live_simple": "live",
    "live_multiple": "live",
    "live_parallel": "live",
    "live_parallel_multiple": "live",
    "live_irrelevance": "live",
    "live_relevance": "live",
    "multi_turn_base": "multi_turn",
    "multi_turn_miss_func": "multi_turn",
    "multi_turn_miss_param": "multi_turn",
    "multi_turn_long_context": "multi_turn",
    "web_search": "agentic",
    "memory": "agentic",
}


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def bfcl_package_data_dir() -> Path:
    spec = importlib.util.find_spec("bfcl_eval")
    if spec is None or spec.origin is None:
        raise SystemExit(
            "missing BFCL package. Create a local venv and install it with: "
            f"python -m pip install '{BFCL_PACKAGE}'"
        )
    return Path(spec.origin).resolve().parent / "data"


def bfcl_package_version() -> str:
    try:
        return importlib.metadata.version("bfcl-eval")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def official_file(category: str) -> str:
    return f"{BFCL_VERSION_PREFIX}_{category}.json"


def copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def stage_official_data(source_data_dir: Path, staged_dir: Path, categories: list[str]) -> dict[str, Any]:
    staged_dir.mkdir(parents=True, exist_ok=True)
    (staged_dir / "possible_answer").mkdir(parents=True, exist_ok=True)
    staged = []
    missing = []
    for category in categories:
        src_name = official_file(category)
        adapter_name = V4_TO_ADAPTER_ALIASES.get(category, src_name)
        src = source_data_dir / src_name
        dst = staged_dir / adapter_name
        ok = copy_if_exists(src, dst)
        answer_ok = copy_if_exists(
            source_data_dir / "possible_answer" / src_name,
            staged_dir / "possible_answer" / adapter_name,
        )
        if not ok:
            missing.append(src_name)
            continue
        staged.append(
            {
                "category": category,
                "official_file": src_name,
                "adapter_file": adapter_name,
                "possible_answer_available": answer_ok,
            }
        )
    if missing:
        raise SystemExit(f"missing BFCL data files in {source_data_dir}: {missing}")
    return {"staged_dir": str(staged_dir), "categories": staged}


def py_value(value: Any) -> str:
    if isinstance(value, dict):
        return "{" + ", ".join(f"{key!r}: {py_value(child)}" for key, child in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ", ".join(py_value(child) for child in value) + "]"
    return repr(value)


def call_to_python(call: dict[str, Any]) -> str:
    name = str(adapter.actual_call_name(call))
    arguments = adapter.actual_call_arguments(call)
    args = ", ".join(f"{key}={py_value(value)}" for key, value in arguments.items())
    return f"{name}({args})"


def calls_to_bfcl_prompt_result(calls: list[dict[str, Any]]) -> str:
    if not calls:
        return "[]"
    return "[" + ", ".join(call_to_python(call) for call in calls) + "]"


def calls_from_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    response = record.get("raw", {}).get("response") or ""
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        return adapter.parse_calls_from_generated_text(str(response))
    return adapter.coerce_call_object(parsed)


def official_result_id(category: str, source_row_id: str) -> str:
    """Return the BFCL evaluator ID for rows materialized through adapter aliases."""
    simple_aliases = {
        "simple_python": "simple_",
        "simple_java": "java_",
        "simple_javascript": "javascript_",
    }
    alias = simple_aliases.get(category)
    if alias and source_row_id.startswith(alias) and not source_row_id.startswith(f"{category}_"):
        return f"{category}_{source_row_id[len(alias):]}"
    return source_row_id


def export_official_results(
    records_path: Path,
    export_root: Path,
    *,
    model_dir: str,
    control_id: str,
) -> dict[str, Any]:
    rows = [row for row in read_jsonl(records_path) if row.get("control_id") == control_id]
    by_category: dict[str, list[dict[str, Any]]] = {}
    sidecars: list[dict[str, Any]] = []
    for row in rows:
        provenance = row.get("source_provenance") or {}
        category = str(provenance.get("source_category") or row.get("task_bucket", "").removeprefix("bfcl_"))
        source_row_id = official_result_id(
            category,
            str(provenance.get("source_row_id") or row.get("case_id", "").split(":")[-1]),
        )
        calls = calls_from_record(row)
        official_entry = {
            "id": source_row_id,
            "result": calls_to_bfcl_prompt_result(calls),
            "input_token_count": row.get("positions", {}).get("tail_token_count"),
            "output_token_count": row.get("quality", {}).get("generated_token_count"),
            "latency": row.get("timing", {}).get("total_ms"),
            "kv_capsule_pti_metadata": {
                "control_id": control_id,
                "case_id": row.get("case_id"),
                "source_row_hash": provenance.get("source_row_hash"),
                "function_catalog_hash": row.get("catalog_hash"),
                "capsule": row.get("capsule", {}),
                "local_scorer_passed": row.get("quality", {}).get("bfcl_score", {}).get("passed"),
            },
        }
        by_category.setdefault(category, []).append(official_entry)
        sidecars.append(
            {
                "id": source_row_id,
                "category": category,
                "case_id": row.get("case_id"),
                "result": official_entry["result"],
                "raw_response_hash": row.get("quality", {}).get("response_hash"),
                "generated_text_hash": row.get("quality", {}).get("generated_text_hash"),
                "bfcl_score": row.get("quality", {}).get("bfcl_score"),
                "source_provenance": provenance,
            }
        )

    written = []
    for category, entries in sorted(by_category.items()):
        group = GROUP_BY_CATEGORY.get(category, "unknown")
        path = export_root / "result" / model_dir / group / f"{BFCL_VERSION_PREFIX}_{category}_result.json"
        write_jsonl(path, sorted(entries, key=lambda item: item["id"]))
        written.append({"category": category, "path": str(path), "entry_count": len(entries)})

    sidecar_path = export_root / "kv_pti_sidecar" / f"{model_dir}-{control_id}-trace.jsonl"
    write_jsonl(sidecar_path, sidecars)
    return {
        "record_count": len(rows),
        "category_count": len(by_category),
        "result_files": written,
        "sidecar_path": str(sidecar_path),
    }


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    source_data = args.bfcl_data_dir or bfcl_package_data_dir()
    source_data = source_data.resolve()
    staged = stage_official_data(source_data, args.lane_root / "staged-bfcl-data", args.categories)
    cases = adapter.materialize_cases(
        source_dir=args.lane_root / "staged-bfcl-data",
        categories=args.categories,
        per_category=args.per_category,
    )
    packets = adapter.materialize_control_packets(cases)
    packet_path = args.lane_root / "raw" / f"{args.run_label}-control-packet.jsonl"
    summary_path = args.lane_root / "raw" / f"{args.run_label}-materialization-summary.json"
    audit_path = args.lane_root / "raw" / f"{args.run_label}-compatibility-audit.json"
    adapter.write_jsonl(packet_path, packets)
    adapter.write_json(summary_path, adapter.summarize_packets(packets))
    adapter.write_json(audit_path, adapter.compatibility_audit(cases))
    return {
        "packet_path": str(packet_path),
        "summary_path": str(summary_path),
        "compatibility_audit_path": str(audit_path),
        "case_count": len(cases),
        "control_record_count": len(packets),
        "staged": staged,
    }


def run_model(args: argparse.Namespace, packet_path: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        str(BENCHMARKS_DIR / "code_mode_kv_capsule_model_loop_runner.py"),
        "--packet",
        str(packet_path),
        "--out-dir",
        str(args.lane_root / "raw"),
        "--cache-dir",
        str(args.lane_root / "cache"),
        "--run-label",
        args.run_label,
        "--controls",
        args.controls,
        "--model-profile",
        args.model_profile,
        "--predict",
        str(args.predict),
        "--max-steps",
        str(args.max_steps),
        "--max-repairs",
        str(args.max_repairs),
    ]
    if args.case_limit is not None:
        command.extend(["--case-limit", str(args.case_limit)])
    if args.state_route:
        command.extend(["--state-route", args.state_route])
    command_path = args.lane_root / "raw" / f"{args.run_label}-official-runner-command.txt"
    command_path.parent.mkdir(parents=True, exist_ok=True)
    command_path.write_text(" ".join(command) + "\n", encoding="utf-8")
    if args.dry_run:
        return {"skipped": True, "command": command, "command_path": str(command_path)}
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=str(BENCHMARKS_DIR), text=True, capture_output=True, check=False)
    stdout_path = args.lane_root / "raw" / f"{args.run_label}-official-runner-stdout.log"
    stderr_path = args.lane_root / "raw" / f"{args.run_label}-official-runner-stderr.log"
    stdout_path.write_text(proc.stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(proc.stderr, encoding="utf-8", errors="replace")
    return {
        "skipped": False,
        "exit_code": proc.returncode,
        "wall_ms": (time.perf_counter() - started) * 1000,
        "command": command,
        "command_path": str(command_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }


def build_manifest(args: argparse.Namespace, materialized: dict[str, Any], run_result: dict[str, Any], export: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "created_utc": now_utc(),
        "lane": "bfcl_official_kv_pti_leaderboard_lane",
        "goal": "Generate BFCL V4-compatible result artifacts for a disclosed KV-capsule + programmatic-tool-interface runtime.",
        "run_label": args.run_label,
        "model_dir": args.model_dir,
        "model_profile": args.model_profile,
        "bfcl_eval_package_required": BFCL_PACKAGE,
        "bfcl_eval_package_observed": bfcl_package_version(),
        "bfcl_version_prefix": BFCL_VERSION_PREFIX,
        "categories": args.categories,
        "controls": args.controls,
        "leaderboard_disclosure": {
            "runtime_is_standard_model_only": False,
            "runtime_description": "Gemma 4 local model with stable BFCL function catalog loaded into a saved/restored llama.cpp KV/sequence-state capsule; task tails are evaluated through a compact programmatic tool interface.",
            "submission_class": "custom inference harness / prompt-mode result files",
            "must_disclose_hidden_state": True,
            "must_disclose_pti_contract": True,
            "official_submission_status": "not_submitted",
        },
        "materialized": materialized,
        "run": run_result,
        "export": export,
        "official_evaluation_handoff": {
            "install": (
                "python3 -m venv .venv-bfcl && "
                ". .venv-bfcl/bin/activate && "
                f"python -m pip install '{BFCL_PACKAGE}'"
            ),
            "evaluate_from_export_root": (
                f"BFCL_PROJECT_ROOT={args.lane_root / 'official-export'} "
                f"bfcl evaluate --model {args.model_dir} --test-category {' '.join(args.categories)} --result-dir result"
            ),
            "note": "The BFCL package may require registering a custom model handler for this model key so its prompt-mode decoder is used for these pre-generated result files.",
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare/run/export the official BFCL KV/PTI lane.")
    parser.add_argument("command", choices=["prepare", "run", "export", "all"])
    parser.add_argument("--lane-root", type=Path, default=DEFAULT_LANE_ROOT)
    parser.add_argument("--bfcl-data-dir", type=Path, help="Optional bfcl_eval/data directory. Defaults to installed package data.")
    parser.add_argument("--run-label", default=DEFAULT_RUN_LABEL)
    parser.add_argument("--model-dir", default=DEFAULT_MODEL_DIR)
    parser.add_argument("--model-profile", default="gemma4-12b")
    parser.add_argument("--category", action="append", choices=OFFICIAL_SCORING_CATEGORIES)
    parser.add_argument("--per-category", type=int, default=1)
    parser.add_argument("--case-limit", type=int)
    parser.add_argument("--controls", default=DEFAULT_CONTROLS)
    parser.add_argument("--predict", type=int, default=128)
    parser.add_argument("--max-steps", type=int, default=5)
    parser.add_argument("--max-repairs", type=int, default=1)
    parser.add_argument("--state-route", choices=["auto", "seq-file", "seq-memory", "whole-context"])
    parser.add_argument("--records", type=Path, help="Model-loop records JSONL for export.")
    parser.add_argument("--dry-run", action="store_true", help="Prepare commands and manifest without running the model.")
    args = parser.parse_args(argv)
    args.categories = args.category or [
        "simple_python",
        "simple_java",
        "simple_javascript",
        "multiple",
        "parallel",
        "parallel_multiple",
        "irrelevance",
    ]
    args.lane_root = args.lane_root.resolve()
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.lane_root.mkdir(parents=True, exist_ok=True)
    materialized: dict[str, Any] | None = None
    run_result: dict[str, Any] | None = None
    export_result: dict[str, Any] | None = None

    if args.command in {"prepare", "run", "all"}:
        materialized = materialize(args)
    else:
        materialized = {"packet_path": str(args.lane_root / "raw" / f"{args.run_label}-control-packet.jsonl")}

    packet_path = Path(materialized["packet_path"])
    if args.command in {"run", "all"}:
        run_result = run_model(args, packet_path)
    else:
        run_result = {"skipped": True}

    records_path = args.records or (args.lane_root / "raw" / f"{args.run_label}-model-loop-records.jsonl")
    if args.command in {"export", "all"} and records_path.exists():
        export_result = export_official_results(
            records_path,
            args.lane_root / "official-export",
            model_dir=args.model_dir,
            control_id=args.controls.split(",")[0],
        )
    elif args.command in {"export", "all"}:
        export_result = {"skipped": True, "reason": f"records file not found: {records_path}"}

    manifest = build_manifest(args, materialized, run_result, export_result)
    manifest_path = args.lane_root / "BFCL_OFFICIAL_LANE_MANIFEST.json"
    write_json(manifest_path, manifest)
    print(json.dumps({"manifest_path": str(manifest_path), **manifest}, indent=2, sort_keys=True))
    if run_result and not run_result.get("skipped") and run_result.get("exit_code"):
        return int(run_result["exit_code"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
