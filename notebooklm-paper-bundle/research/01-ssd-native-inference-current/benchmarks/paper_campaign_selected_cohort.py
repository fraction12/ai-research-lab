#!/usr/bin/env python3
"""Select a calibrated BFCL cohort and optionally launch the paper test."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BENCHMARKS_DIR = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARKS_DIR.parents[2]
DEFAULT_EXPERIMENT_ID = "paper-grade-code-mode-kv-capsule-evaluation-2026-06-05"
DEFAULT_TRACK01_ROOT = BENCHMARKS_DIR / DEFAULT_EXPERIMENT_ID
DEFAULT_TRACK02_ROOT = (
    REPO_ROOT
    / "research"
    / "02-quality-gated-stateful-kv-reuse"
    / "experiments"
    / DEFAULT_EXPERIMENT_ID
)
CONTROL_ORDER = [
    "direct_full_visible_tools",
    "code_mode_full_visible",
    "code_mode_fresh_tail_only",
    "code_mode_native_live_append",
    "code_mode_restored_kv_capsule",
    "code_mode_wrong_capsule_negative",
    "compact_visible_evidence_code_mode",
]
PRIMARY_POSITIVE_CONTROLS = {
    "code_mode_full_visible",
    "code_mode_native_live_append",
    "code_mode_restored_kv_capsule",
}
PRIMARY_NEGATIVE_CONTROLS = {
    "code_mode_fresh_tail_only",
    "code_mode_wrong_capsule_negative",
}
NO_CALL_CATEGORIES = {"irrelevance", "live_irrelevance"}


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"missing JSONL file: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def source_category(row: dict[str, Any]) -> str:
    provenance = row.get("source_provenance")
    if isinstance(provenance, dict):
        return str(provenance.get("source_category") or "")
    task_bucket = str(row.get("task_bucket") or "")
    return task_bucket.removeprefix("bfcl_")


def gate_passed(row: dict[str, Any] | None) -> bool:
    return bool(row and row.get("control_gate_passed") is True)


def answer_contained(row: dict[str, Any] | None) -> bool:
    quality = row.get("quality") if isinstance(row, dict) else None
    return bool(isinstance(quality, dict) and quality.get("answer_contained") is True)


def response_hash(row: dict[str, Any] | None) -> str | None:
    quality = row.get("quality") if isinstance(row, dict) else None
    if not isinstance(quality, dict):
        return None
    value = quality.get("normalized_response_hash") or quality.get("response_hash")
    return str(value) if value else None


def by_case_and_control(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        case_id = str(row.get("case_id") or "")
        control_id = str(row.get("control_id") or "")
        if case_id and control_id:
            grouped.setdefault(case_id, {})[control_id] = row
    return grouped


def packet_case_order(packet_rows: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    order: list[str] = []
    for row in packet_rows:
        case_id = str(row.get("case_id") or "")
        if case_id and case_id not in seen:
            seen.add(case_id)
            order.append(case_id)
    return order


@dataclass(frozen=True)
class CaseDecision:
    case_id: str
    category: str
    clean_primary_eligible: bool
    rejection_reasons: tuple[str, ...]
    restored_only_failure: bool
    direct_tool_gap: bool
    compact_visible_passed: bool
    live_restored_hash_match: bool


def decide_case(case_id: str, controls: dict[str, dict[str, Any]]) -> CaseDecision:
    representative = next(iter(controls.values()), {})
    category = source_category(representative)
    reasons: list[str] = []
    missing = [control for control in CONTROL_ORDER if control not in controls]
    if missing:
        reasons.append("missing_controls:" + ",".join(missing))
    if category in NO_CALL_CATEGORIES:
        reasons.append("no_call_category")
    for control in PRIMARY_POSITIVE_CONTROLS:
        if not gate_passed(controls.get(control)):
            reasons.append(f"{control}_failed")
    for control in PRIMARY_NEGATIVE_CONTROLS:
        row = controls.get(control)
        if not gate_passed(row) or answer_contained(row):
            reasons.append(f"{control}_leaked")

    full = controls.get("code_mode_full_visible")
    native = controls.get("code_mode_native_live_append")
    restored = controls.get("code_mode_restored_kv_capsule")
    direct = controls.get("direct_full_visible_tools")
    compact = controls.get("compact_visible_evidence_code_mode")
    live_restored_hash_match = bool(response_hash(native) and response_hash(native) == response_hash(restored))
    restored_only_failure = bool(gate_passed(full) and gate_passed(native) and not gate_passed(restored))
    direct_tool_gap = bool(gate_passed(full) and not gate_passed(direct))
    compact_visible_passed = gate_passed(compact)
    return CaseDecision(
        case_id=case_id,
        category=category,
        clean_primary_eligible=not reasons,
        rejection_reasons=tuple(reasons),
        restored_only_failure=restored_only_failure,
        direct_tool_gap=direct_tool_gap,
        compact_visible_passed=compact_visible_passed,
        live_restored_hash_match=live_restored_hash_match,
    )


def summarize_and_select(
    *,
    calibration_records: list[dict[str, Any]],
    source_packet_rows: list[dict[str, Any]],
    target_rows: int,
) -> tuple[dict[str, Any], list[str]]:
    grouped = by_case_and_control(calibration_records)
    source_order = packet_case_order(source_packet_rows)
    decisions = [decide_case(case_id, grouped.get(case_id, {})) for case_id in source_order if case_id in grouped]
    selected = [decision.case_id for decision in decisions if decision.clean_primary_eligible][:target_rows]

    counts_by_category: dict[str, dict[str, int]] = {}
    rejection_counts: dict[str, int] = {}
    for decision in decisions:
        bucket = counts_by_category.setdefault(
            decision.category or "unknown",
            {"cases": 0, "clean_primary_eligible": 0, "restored_only_failures": 0, "direct_tool_gaps": 0},
        )
        bucket["cases"] += 1
        if decision.clean_primary_eligible:
            bucket["clean_primary_eligible"] += 1
        if decision.restored_only_failure:
            bucket["restored_only_failures"] += 1
        if decision.direct_tool_gap:
            bucket["direct_tool_gaps"] += 1
        for reason in decision.rejection_reasons:
            rejection_counts[reason] = rejection_counts.get(reason, 0) + 1

    control_counts: dict[str, dict[str, int]] = {}
    for row in calibration_records:
        control = str(row.get("control_id") or "unknown")
        stats = control_counts.setdefault(control, {"records": 0, "gate_passed": 0, "answer_contained": 0})
        stats["records"] += 1
        if gate_passed(row):
            stats["gate_passed"] += 1
        if answer_contained(row):
            stats["answer_contained"] += 1

    clean_count = sum(1 for decision in decisions if decision.clean_primary_eligible)
    summary = {
        "schema_version": 1,
        "created_utc": now_utc(),
        "candidate_case_count": len(decisions),
        "record_count": len(calibration_records),
        "target_rows": target_rows,
        "clean_primary_eligible_count": clean_count,
        "selected_case_count": len(selected),
        "selected_case_ids": selected,
        "thresholds": {"minimum_clean_rows": 100, "target_clean_rows": 200},
        "threshold_decision": "paper_test_ready" if clean_count >= target_rows else "below_target",
        "counts_by_category": counts_by_category,
        "counts_by_control": control_counts,
        "rejection_counts": rejection_counts,
        "restored_only_failure_count": sum(1 for decision in decisions if decision.restored_only_failure),
        "direct_tool_gap_count": sum(1 for decision in decisions if decision.direct_tool_gap),
        "compact_visible_pass_count": sum(1 for decision in decisions if decision.compact_visible_passed),
        "live_restored_hash_match_count": sum(1 for decision in decisions if decision.live_restored_hash_match),
    }
    return summary, selected


def selected_packet_rows(source_packet_rows: list[dict[str, Any]], selected_case_ids: list[str]) -> list[dict[str, Any]]:
    selected = set(selected_case_ids)
    rows = [row for row in source_packet_rows if row.get("case_id") in selected]
    expected = len(selected_case_ids) * len(CONTROL_ORDER)
    if len(rows) != expected:
        raise SystemExit(f"selected packet has {len(rows)} rows, expected {expected}")
    return rows


def quote_cmd(value: str | Path) -> str:
    text = str(value)
    return '"' + text.replace('"', '\\"') + '"'


def write_windows_launcher(
    *,
    repo_root: Path,
    runner: Path,
    packet: Path,
    raw_dir: Path,
    cache_dir: Path,
    run_label: str,
    stdout: Path,
    stderr: Path,
    exit_code: Path,
    cmd_path: Path,
) -> None:
    runner_line = " ".join(
        [
            "py",
            "-3",
            quote_cmd(runner),
            "--packet",
            quote_cmd(packet),
            "--out-dir",
            quote_cmd(raw_dir),
            "--cache-dir",
            quote_cmd(cache_dir),
            "--run-label",
            run_label,
            "--model-profile",
            "gemma4-12b",
            "--state-route",
            "auto",
            "--predict",
            "128",
            "--max-steps",
            "3",
            "--max-repairs",
            "1",
        ]
    )
    cmd_path.write_text(
        "\n".join(
            [
                "@echo off",
                "setlocal",
                f"cd /d {quote_cmd(repo_root)}",
                f"echo START %DATE% %TIME% > {quote_cmd(stdout)}",
                f"echo RUNNER {runner_line} >> {quote_cmd(stdout)}",
                f"{runner_line} >> {quote_cmd(stdout)} 2>> {quote_cmd(stderr)}",
                "set EXITCODE=%ERRORLEVEL%",
                f"echo %EXITCODE% > {quote_cmd(exit_code)}",
                f"echo END %DATE% %TIME% EXIT %EXITCODE% >> {quote_cmd(stdout)}",
                "exit /b %EXITCODE%",
                "",
            ]
        ),
        encoding="utf-8",
    )


def launch_windows_task(task_name: str, cmd_path: Path) -> dict[str, Any]:
    if platform.system().lower() != "windows":
        raise SystemExit("--launch-detached is only supported on Windows")
    subprocess.run(["schtasks", "/Delete", "/TN", task_name, "/F"], text=True, capture_output=True)
    create = subprocess.run(
        ["schtasks", "/Create", "/TN", task_name, "/TR", str(cmd_path), "/SC", "ONCE", "/ST", time.strftime("%H:%M"), "/F"],
        text=True,
        capture_output=True,
        check=False,
    )
    if create.returncode:
        return {"ok": False, "stage": "create", "exit_code": create.returncode, "stdout": create.stdout, "stderr": create.stderr}
    run = subprocess.run(["schtasks", "/Run", "/TN", task_name], text=True, capture_output=True, check=False)
    return {
        "ok": run.returncode == 0,
        "stage": "run",
        "exit_code": run.returncode,
        "create_stdout": create.stdout,
        "stdout": run.stdout,
        "stderr": run.stderr,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Select calibrated BFCL cohort and optionally launch paper test.")
    ap.add_argument("--calibration-run-label", default="bfcl-paper-calibration-detached-v2")
    ap.add_argument("--paper-run-label", default="bfcl-paper-selected-cohort-v1")
    ap.add_argument("--raw-dir", type=Path, default=DEFAULT_TRACK01_ROOT / "raw")
    ap.add_argument("--cache-dir", type=Path, default=DEFAULT_TRACK01_ROOT / "cache")
    ap.add_argument("--summary-dir", type=Path, default=DEFAULT_TRACK02_ROOT)
    ap.add_argument("--target-rows", type=int, default=200)
    ap.add_argument("--min-clean-rows", type=int, default=100)
    ap.add_argument("--launch-detached", action="store_true")
    ap.add_argument("--task-name", default="BFCLPaperSelectedCohortV1")
    args = ap.parse_args(argv)

    args.summary_dir.mkdir(parents=True, exist_ok=True)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    calibration_records_path = args.raw_dir / f"{args.calibration_run_label}-model-loop-records.jsonl"
    source_packet_path = args.raw_dir / f"{args.calibration_run_label}-control-packet.jsonl"
    calibration_records = read_jsonl(calibration_records_path)
    source_packet = read_jsonl(source_packet_path)
    summary, selected_case_ids = summarize_and_select(
        calibration_records=calibration_records,
        source_packet_rows=source_packet,
        target_rows=args.target_rows,
    )
    summary.update(
        {
            "calibration_run_label": args.calibration_run_label,
            "paper_run_label": args.paper_run_label,
            "calibration_records_path": str(calibration_records_path),
            "source_packet_path": str(source_packet_path),
        }
    )
    summary_path = args.summary_dir / f"{args.calibration_run_label}-calibration-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if summary["clean_primary_eligible_count"] < args.min_clean_rows:
        print(json.dumps({"decision": "below_minimum_clean_rows", "summary": str(summary_path)}, indent=2))
        return 3
    if summary["clean_primary_eligible_count"] < args.target_rows:
        print(json.dumps({"decision": "below_target_clean_rows", "summary": str(summary_path)}, indent=2))
        return 4

    paper_packet = args.raw_dir / f"{args.paper_run_label}-control-packet.jsonl"
    packet_rows = selected_packet_rows(source_packet, selected_case_ids)
    write_jsonl(paper_packet, packet_rows)
    summary["paper_packet_path"] = str(paper_packet)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    result: dict[str, Any] = {"decision": "selected_cohort_packet_written", "summary": str(summary_path), "packet": str(paper_packet)}
    if args.launch_detached:
        runner = BENCHMARKS_DIR / "code_mode_kv_capsule_model_loop_runner.py"
        stdout = args.raw_dir / f"{args.paper_run_label}-stdout.log"
        stderr = args.raw_dir / f"{args.paper_run_label}-stderr.log"
        exit_code = args.raw_dir / f"{args.paper_run_label}-exit-code.txt"
        cmd_path = args.raw_dir / f"{args.paper_run_label}.cmd"
        write_windows_launcher(
            repo_root=REPO_ROOT,
            runner=runner,
            packet=paper_packet,
            raw_dir=args.raw_dir,
            cache_dir=args.cache_dir,
            run_label=args.paper_run_label,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            cmd_path=cmd_path,
        )
        launch = launch_windows_task(args.task_name, cmd_path)
        marker = args.summary_dir / "calibration-job.json"
        marker_data: dict[str, Any] = {}
        if marker.exists():
            marker_data = json.loads(marker.read_text(encoding="utf-8"))
        marker_data.update(
            {
                "status": "paper_test_started" if launch.get("ok") else "paper_test_launch_failed",
                "paper_run_label": args.paper_run_label,
                "paper_task_name": args.task_name,
                "paper_packet": str(paper_packet),
                "paper_cmdfile": str(cmd_path),
                "paper_stdout": str(stdout),
                "paper_stderr": str(stderr),
                "paper_exit_code": str(exit_code),
                "paper_selected_case_count": len(selected_case_ids),
                "paper_launch_result": launch,
                "paper_started_utc": now_utc(),
            }
        )
        marker.write_text(json.dumps(marker_data, indent=2), encoding="utf-8")
        result.update({"decision": "paper_test_started" if launch.get("ok") else "paper_test_launch_failed", "launch": launch})
        if not launch.get("ok"):
            print(json.dumps(result, indent=2))
            return 5

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
