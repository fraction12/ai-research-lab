#!/usr/bin/env python3
"""Run the repeated-work speed comparison smoke/benchmark.

The controller intentionally wraps the existing model-bearing KV runner
instead of reimplementing the KV path. That keeps the KV+Code Mode arm on
the same harness used for the selected 100-case cohort result.
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


BENCHMARKS_DIR = Path(__file__).resolve().parent
if str(BENCHMARKS_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARKS_DIR))

import bfcl_code_mode_kv_adapter as bfcl_adapter  # noqa: E402
import code_mode_tool_surface as tool_surface  # noqa: E402

REPO_ROOT = BENCHMARKS_DIR.parents[2]
DEFAULT_EXPERIMENT_ID = "paper-grade-code-mode-kv-capsule-evaluation-2026-06-05"
DEFAULT_TRACK01_ROOT = BENCHMARKS_DIR / DEFAULT_EXPERIMENT_ID
DEFAULT_RAW_DIR = DEFAULT_TRACK01_ROOT / "raw"
DEFAULT_CACHE_DIR = DEFAULT_TRACK01_ROOT / "cache"
DEFAULT_PACKET = DEFAULT_RAW_DIR / "bfcl-paper-selected-cohort-v1-control-packet.jsonl"
DEFAULT_OUT_DIR = DEFAULT_RAW_DIR / "repeated-work-speed"
DEFAULT_KV_CONTROLS = "code_mode_native_live_append,code_mode_restored_kv_capsule"
CONTROL_ORDER = [
    "direct_full_visible_tools",
    "code_mode_full_visible",
    "code_mode_fresh_tail_only",
    "code_mode_native_live_append",
    "code_mode_restored_kv_capsule",
    "code_mode_wrong_capsule_negative",
    "compact_visible_evidence_code_mode",
]


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


def safe_label(value: str) -> str:
    label = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in value).strip(".-_")
    return label or "repeated-work-speed"


def packet_case_order(rows: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for row in rows:
        case_id = str(row.get("case_id") or "")
        if case_id and case_id not in seen:
            seen.add(case_id)
            ordered.append(case_id)
    return ordered


def rows_by_case_control(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        case_id = str(row.get("case_id") or "")
        control_id = str(row.get("control_id") or "")
        if case_id and control_id:
            grouped.setdefault(case_id, {})[control_id] = row
    return grouped


def select_cases(packet_rows: list[dict[str, Any]], case_limit: int | None) -> list[str]:
    ordered = sorted(packet_case_order(packet_rows))
    if case_limit is not None:
        if case_limit < 1:
            raise SystemExit("--case-limit must be >= 1")
        ordered = ordered[:case_limit]
    return ordered


def selected_rows(packet_rows: list[dict[str, Any]], case_ids: list[str], control_id: str) -> list[dict[str, Any]]:
    wanted = set(case_ids)
    rows = [row for row in packet_rows if row.get("case_id") in wanted and row.get("control_id") == control_id]
    by_case = {row["case_id"]: row for row in rows}
    missing = [case_id for case_id in case_ids if case_id not in by_case]
    if missing:
        raise SystemExit(f"packet missing {control_id} rows for cases: {missing}")
    return [by_case[case_id] for case_id in case_ids]


def build_codex_prompt(row: dict[str, Any], *, task_index: int, task_count: int) -> str:
    visible_prompt = str(row.get("visible_prompt") or "")
    expected_shape = (
        '{"case_id":"'
        + str(row["case_id"])
        + '","tool_calls":[{"function_name":"...","arguments":{}}],"final_answer":"..."}'
    )
    return (
        "You are the Codex/Ollama real-compaction baseline for a controlled BFCL repeated-work benchmark.\n"
        "Use the regular visible tool schemas and user request below. Do not use hidden KV capsule state or Code Mode.\n"
        "Return only one compact JSON object, no markdown, no prose.\n"
        f"Task {task_index + 1} of {task_count}.\n"
        f"Required JSON shape: {expected_shape}\n\n"
        "VISIBLE REGULAR TOOL TASK:\n"
        f"{visible_prompt}\n"
    )


def build_kv_runner_command(args: argparse.Namespace, *, run_label: str) -> list[str]:
    return [
        sys.executable,
        str(BENCHMARKS_DIR / "code_mode_kv_capsule_model_loop_runner.py"),
        "--packet",
        str(args.packet),
        "--out-dir",
        str(args.out_dir),
        "--cache-dir",
        str(args.cache_dir),
        "--run-label",
        run_label,
        "--controls",
        args.kv_controls,
        "--model-profile",
        args.model_profile,
        "--case-limit",
        str(args.case_limit),
    ]


def run_subprocess(command: list[str], *, cwd: Path, stdin_text: str | None = None) -> tuple[int, str, str, float]:
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        input=stdin_text,
        text=True,
        cwd=str(cwd),
        capture_output=True,
        check=False,
    )
    wall_ms = (time.perf_counter() - started) * 1000
    return proc.returncode, proc.stdout, proc.stderr, wall_ms


def values_for_key(value: Any, key_names: set[str]) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key) in key_names:
                found.append(child)
            found.extend(values_for_key(child, key_names))
    elif isinstance(value, list):
        for child in value:
            found.extend(values_for_key(child, key_names))
    return found


def first_number(value: Any, keys: set[str]) -> float | None:
    for candidate in values_for_key(value, keys):
        if isinstance(candidate, (int, float)):
            return float(candidate)
    return None


def text_values(value: Any) -> list[str]:
    values: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"message", "content", "text", "last_message"} and isinstance(child, str):
                values.append(child)
            values.extend(text_values(child))
    elif isinstance(value, list):
        for child in value:
            values.extend(text_values(child))
    return values


def parse_codex_json_events(stdout: str, stderr: str = "") -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            events.append(parsed)

    text = stdout + "\n" + stderr
    compaction_markers = re.findall(r"context_compacted|ContextCompacted|thread/compacted", text)
    last_message = ""
    for event in reversed(events):
        candidates = [value for value in text_values(event) if value.strip()]
        if candidates:
            last_message = candidates[-1]
            break

    input_tokens = first_number(
        events,
        {"input_tokens", "prompt_tokens", "prompt_eval_count", "inputTokenCount", "total_input_tokens"},
    )
    output_tokens = first_number(
        events,
        {"output_tokens", "completion_tokens", "eval_count", "outputTokenCount", "total_output_tokens"},
    )
    codex_duration_ms = first_number(events, {"duration_ms", "wall_ms", "elapsed_ms", "codex_duration_ms"})
    codex_ttft_ms = first_number(events, {"ttft_ms", "time_to_first_token_ms", "timeToFirstTokenMs"})
    return {
        "event_count": len(events),
        "compaction_events_seen": len(compaction_markers),
        "last_compaction_marker": compaction_markers[-1] if compaction_markers else None,
        "visible_input_tokens": int(input_tokens) if input_tokens is not None else None,
        "output_tokens": int(output_tokens) if output_tokens is not None else None,
        "codex_duration_ms": codex_duration_ms,
        "codex_ttft_ms": codex_ttft_ms,
        "last_message": last_message,
    }


def score_codex_response(row: dict[str, Any], response_text: str) -> dict[str, Any]:
    parsed_calls = tool_surface.parse_calls_from_generated_text(response_text)
    expected_calls = list(row.get("expected_calls") or [])
    scorer = bfcl_adapter.score_calls(expected_calls, parsed_calls)
    answer_contained = str(row.get("expected_answer") or "") in response_text
    return {
        "passed": bool(scorer.get("passed")) or answer_contained,
        "answer_contained": answer_contained,
        "parsed_calls": parsed_calls,
        "scorer": scorer,
    }


def codex_command(args: argparse.Namespace, *, resume: bool) -> list[str]:
    codex_bin = str(args.codex_bin)
    if codex_bin.lower().endswith(".ps1"):
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            codex_bin,
            "--profile",
            args.codex_profile,
            "exec",
        ]
    elif codex_bin.lower().endswith(".js"):
        command = [str(args.node_bin), codex_bin, "--profile", args.codex_profile, "exec"]
    else:
        command = [codex_bin, "--profile", args.codex_profile, "exec"]
    if resume:
        command.extend(["resume", "--last"])
    command.extend(["--json", "-"])
    return command


def run_codex_arm(args: argparse.Namespace, packet_rows: list[dict[str, Any]], case_ids: list[str]) -> list[dict[str, Any]]:
    direct_rows = selected_rows(packet_rows, case_ids, "direct_full_visible_tools")
    records: list[dict[str, Any]] = []
    prompt_dir = args.out_dir / f"{args.run_label}-codex-prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    for task_index, row in enumerate(direct_rows):
        prompt = build_codex_prompt(row, task_index=task_index, task_count=len(direct_rows))
        prompt_path = prompt_dir / f"{task_index:04d}-{safe_label(row['case_id'])}.txt"
        prompt_path.write_text(prompt, encoding="utf-8")
        if args.dry_run:
            telemetry = {
                "event_count": 0,
                "compaction_events_seen": 0,
                "last_compaction_marker": None,
                "visible_input_tokens": None,
                "output_tokens": None,
                "codex_duration_ms": None,
                "codex_ttft_ms": None,
                "last_message": "",
            }
            returncode = 0
            stdout = ""
            stderr = ""
            wall_ms = 0.0
        else:
            returncode, stdout, stderr, wall_ms = run_subprocess(
                codex_command(args, resume=task_index > 0),
                cwd=args.repo_root,
                stdin_text=prompt,
            )
            telemetry = parse_codex_json_events(stdout, stderr)
        response_text = telemetry.get("last_message") or stdout
        score = score_codex_response(row, response_text)
        records.append(
            {
                "run_label": args.run_label,
                "system": "codex_ollama_regular_tools_compaction",
                "case_id": row["case_id"],
                "task_index": task_index,
                "wall_ms": wall_ms,
                "prompt_eval_ms": None,
                "generation_ms": None,
                "capsule_build_ms": 0,
                "capsule_restore_ms": 0,
                "codex_duration_ms": telemetry["codex_duration_ms"],
                "codex_ttft_ms": telemetry["codex_ttft_ms"],
                "codex_compaction_events_seen": telemetry["compaction_events_seen"],
                "codex_last_compaction_marker": telemetry["last_compaction_marker"],
                "codex_profile": args.codex_profile,
                "visible_input_tokens": telemetry["visible_input_tokens"],
                "output_tokens": telemetry["output_tokens"],
                "stable_context_tokens": 0,
                "passed": score["passed"],
                "repair_count": 0,
                "model_profile": "gemma4:12b",
                "model_provider": "ollama",
                "runtime": "codex-cli+ollama",
                "returncode": returncode,
                "metadata": {
                    "prompt_path": str(prompt_path),
                    "event_count": telemetry["event_count"],
                    "answer_contained": score["answer_contained"],
                    "parsed_calls": score["parsed_calls"],
                    "scorer": score["scorer"],
                    "stdout_path": None,
                    "stderr_path": None,
                },
            }
        )
        if stdout or stderr:
            stdout_path = args.out_dir / f"{args.run_label}-codex-{task_index:04d}.stdout.jsonl"
            stderr_path = args.out_dir / f"{args.run_label}-codex-{task_index:04d}.stderr.txt"
            stdout_path.write_text(stdout, encoding="utf-8")
            stderr_path.write_text(stderr, encoding="utf-8")
            records[-1]["metadata"]["stdout_path"] = str(stdout_path)
            records[-1]["metadata"]["stderr_path"] = str(stderr_path)
    return records


def kv_speed_record(row: dict[str, Any], *, task_index: int, run_label: str) -> dict[str, Any]:
    timing = row.get("timing") if isinstance(row.get("timing"), dict) else {}
    quality = row.get("quality") if isinstance(row.get("quality"), dict) else {}
    positions = row.get("positions") if isinstance(row.get("positions"), dict) else {}
    return {
        "run_label": run_label,
        "system": "kv_capsule_code_mode",
        "case_id": row["case_id"],
        "task_index": task_index,
        "wall_ms": timing.get("total_ms") or timing.get("prompt_eval_ms"),
        "prompt_eval_ms": timing.get("prompt_eval_ms"),
        "generation_ms": timing.get("decode_ms"),
        "capsule_build_ms": timing.get("capsule_build_ms") or 0,
        "capsule_restore_ms": timing.get("capsule_restore_ms") or 0,
        "codex_duration_ms": None,
        "codex_ttft_ms": None,
        "codex_compaction_events_seen": 0,
        "codex_last_compaction_marker": None,
        "codex_profile": None,
        "visible_input_tokens": positions.get("tail_token_count"),
        "output_tokens": quality.get("generated_token_count"),
        "stable_context_tokens": positions.get("prefix_token_count"),
        "passed": bool(row.get("control_gate_passed")),
        "repair_count": quality.get("repair_count") or 0,
        "model_profile": "gemma4-12b",
        "model_provider": "llama.cpp",
        "runtime": "llama.cpp-sequence-state+code-mode",
        "returncode": 0,
        "metadata": {
            "control_id": row.get("control_id"),
            "final_source": quality.get("final_source"),
            "failure_class": row.get("failure_class"),
        },
    }


def run_kv_arm(args: argparse.Namespace) -> list[dict[str, Any]]:
    kv_label = f"{args.run_label}-kv"
    if args.dry_run:
        return []
    command = build_kv_runner_command(args, run_label=kv_label)
    returncode, stdout, stderr, _wall_ms = run_subprocess(command, cwd=args.repo_root)
    stdout_path = args.out_dir / f"{kv_label}.stdout.txt"
    stderr_path = args.out_dir / f"{kv_label}.stderr.txt"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    if returncode != 0:
        raise SystemExit(f"KV runner failed with {returncode}; see {stdout_path} and {stderr_path}")
    records_path = args.out_dir / f"{kv_label}-model-loop-records.jsonl"
    kv_rows = [
        row
        for row in read_jsonl(records_path)
        if row.get("control_id") == "code_mode_restored_kv_capsule"
    ]
    return [kv_speed_record(row, task_index=index, run_label=args.run_label) for index, row in enumerate(kv_rows)]


def summarize_speed_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_system: dict[str, dict[str, Any]] = {}
    for system in sorted({row["system"] for row in records}):
        rows = [row for row in records if row["system"] == system]
        cumulative_wall = 0.0
        break_even_at = None
        for row in rows:
            cumulative_wall += float(row.get("wall_ms") or 0)
        by_system[system] = {
            "record_count": len(rows),
            "pass_count": sum(1 for row in rows if row.get("passed")),
            "cumulative_wall_ms": cumulative_wall,
            "visible_input_tokens": sum(int(row.get("visible_input_tokens") or 0) for row in rows),
            "output_tokens": sum(int(row.get("output_tokens") or 0) for row in rows),
            "compaction_events_seen": sum(int(row.get("codex_compaction_events_seen") or 0) for row in rows),
            "break_even_at_task": break_even_at,
        }
    return {
        "generated_utc": now_utc(),
        "record_count": len(records),
        "case_count": len({row["case_id"] for row in records}),
        "systems": by_system,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run repeated-work speed comparison arms.")
    ap.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--run-label", default="bfcl-repeated-work-speed-smoke-v1")
    ap.add_argument("--case-limit", type=int, default=2)
    ap.add_argument("--systems", default="codex,kv", help="Comma-separated: codex,kv")
    ap.add_argument("--codex-bin", default="codex", help="Codex executable or Windows codex.ps1 shim path.")
    ap.add_argument("--node-bin", default="node", help="Node executable when --codex-bin points at codex.js.")
    ap.add_argument("--codex-profile", default="gemma4-ollama-compact")
    ap.add_argument("--model-profile", default="gemma4-12b")
    ap.add_argument("--kv-controls", default=DEFAULT_KV_CONTROLS)
    ap.add_argument("--dry-run", action="store_true")
    return ap.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.run_label = safe_label(args.run_label)
    systems = {system.strip() for system in args.systems.split(",") if system.strip()}
    unsupported = systems - {"codex", "kv"}
    if unsupported:
        raise SystemExit(f"unsupported --systems values: {sorted(unsupported)}")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    packet_rows = read_jsonl(args.packet)
    case_ids = select_cases(packet_rows, args.case_limit)
    records: list[dict[str, Any]] = []
    if "codex" in systems:
        records.extend(run_codex_arm(args, packet_rows, case_ids))
    if "kv" in systems:
        records.extend(run_kv_arm(args))
    records_path = args.out_dir / f"{args.run_label}-speed-records.jsonl"
    summary_path = args.out_dir / f"{args.run_label}-speed-summary.json"
    run_info_path = args.out_dir / f"{args.run_label}-run-info.json"
    write_jsonl(records_path, records)
    summary = summarize_speed_records(records)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    run_info_path.write_text(
        json.dumps(
            {
                "started_utc": now_utc(),
                "host": platform.node(),
                "platform": platform.platform(),
                "packet": str(args.packet),
                "packet_case_count": len(packet_case_order(packet_rows)),
                "selected_case_ids": case_ids,
                "systems": sorted(systems),
                "dry_run": args.dry_run,
                "records_path": str(records_path),
                "summary_path": str(summary_path),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
