#!/usr/bin/env python3
"""Finalize a repeated-work speed run that completed through a resume arm."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path
from typing import Any


BENCHMARKS_DIR = Path(__file__).resolve().parent
if str(BENCHMARKS_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARKS_DIR))

import paper_campaign_repeated_work_speed as speed  # noqa: E402


def mtime_wall_ms(start: Path, end: Path) -> float | None:
    if not start.exists() or not end.exists():
        return None
    return max(0.0, (end.stat().st_mtime - start.stat().st_mtime) * 1000.0)


def reconstruct_codex_records(
    *,
    packet_rows: list[dict[str, Any]],
    out_dir: Path,
    run_label: str,
    expected_cases: int,
    codex_profile: str,
) -> list[dict[str, Any]]:
    case_ids = speed.select_cases(packet_rows, expected_cases)
    direct_rows = speed.selected_rows(packet_rows, case_ids, "direct_full_visible_tools")
    prompt_dir = out_dir / f"{run_label}-codex-prompts"
    records: list[dict[str, Any]] = []
    for task_index, row in enumerate(direct_rows):
        prompt_path = prompt_dir / f"{task_index:04d}-{speed.safe_label(row['case_id'])}.txt"
        stdout_path = out_dir / f"{run_label}-codex-{task_index:04d}.stdout.jsonl"
        stderr_path = out_dir / f"{run_label}-codex-{task_index:04d}.stderr.txt"
        stdout = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
        stderr = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
        telemetry = speed.parse_codex_json_events(stdout, stderr)
        response_text = telemetry.get("last_message") or stdout
        score = speed.score_codex_response(row, response_text)
        records.append(
            {
                "run_label": run_label,
                "system": "codex_ollama_regular_tools_compaction",
                "case_id": row["case_id"],
                "task_index": task_index,
                "wall_ms": mtime_wall_ms(prompt_path, stdout_path),
                "prompt_eval_ms": None,
                "generation_ms": None,
                "capsule_build_ms": 0,
                "capsule_restore_ms": 0,
                "codex_duration_ms": telemetry["codex_duration_ms"],
                "codex_ttft_ms": telemetry["codex_ttft_ms"],
                "codex_compaction_events_seen": telemetry["compaction_events_seen"],
                "codex_last_compaction_marker": telemetry["last_compaction_marker"],
                "codex_profile": codex_profile,
                "visible_input_tokens": telemetry["visible_input_tokens"],
                "output_tokens": telemetry["output_tokens"],
                "stable_context_tokens": 0,
                "passed": score["passed"],
                "repair_count": 0,
                "model_profile": "gemma4:12b",
                "model_provider": "ollama",
                "runtime": "codex-cli+ollama",
                "returncode": 0 if stdout_path.exists() else 1,
                "metadata": {
                    "prompt_path": str(prompt_path),
                    "event_count": telemetry["event_count"],
                    "answer_contained": score["answer_contained"],
                    "parsed_calls": score["parsed_calls"],
                    "scorer": score["scorer"],
                    "stdout_path": str(stdout_path) if stdout_path.exists() else None,
                    "stderr_path": str(stderr_path) if stderr_path.exists() else None,
                    "reconstructed_from_artifacts": True,
                    "wall_ms_source": "stdout_mtime_minus_prompt_mtime",
                },
            }
        )
    return records


def reconstruct_kv_records(*, out_dir: Path, source_label: str, run_label: str) -> list[dict[str, Any]]:
    records_path = out_dir / f"{source_label}-kv-model-loop-records.jsonl"
    kv_rows = [
        row
        for row in speed.read_jsonl(records_path)
        if row.get("control_id") == "code_mode_restored_kv_capsule"
    ]
    return [speed.kv_speed_record(row, task_index=index, run_label=run_label) for index, row in enumerate(kv_rows)]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Write a combined summary for a resumed repeated-work speed run.")
    ap.add_argument("--packet", type=Path, default=speed.DEFAULT_PACKET)
    ap.add_argument("--out-dir", type=Path, default=speed.DEFAULT_OUT_DIR)
    ap.add_argument("--run-label", default="bfcl-repeated-work-speed-v1")
    ap.add_argument("--kv-source-label", default="bfcl-repeated-work-speed-v1-kv-resume")
    ap.add_argument("--expected-cases", type=int, default=100)
    ap.add_argument("--codex-profile", default="gemma4-ollama-compact")
    return ap.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.run_label = speed.safe_label(args.run_label)
    packet_rows = speed.read_jsonl(args.packet)
    codex_records = reconstruct_codex_records(
        packet_rows=packet_rows,
        out_dir=args.out_dir,
        run_label=args.run_label,
        expected_cases=args.expected_cases,
        codex_profile=args.codex_profile,
    )
    kv_records = reconstruct_kv_records(
        out_dir=args.out_dir,
        source_label=speed.safe_label(args.kv_source_label),
        run_label=args.run_label,
    )
    records = codex_records + kv_records
    records_path = args.out_dir / f"{args.run_label}-speed-records.jsonl"
    summary_path = args.out_dir / f"{args.run_label}-speed-summary.json"
    run_info_path = args.out_dir / f"{args.run_label}-finalized-run-info.json"
    speed.write_jsonl(records_path, records)
    summary = speed.summarize_speed_records(records)
    summary["finalized_from_resume"] = True
    summary["source_labels"] = {
        "codex": args.run_label,
        "kv": speed.safe_label(args.kv_source_label),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    run_info_path.write_text(
        json.dumps(
            {
                "generated_utc": speed.now_utc(),
                "host": platform.node(),
                "platform": platform.platform(),
                "packet": str(args.packet),
                "records_path": str(records_path),
                "summary_path": str(summary_path),
                "reconstructed_codex_records": len(codex_records),
                "reconstructed_kv_records": len(kv_records),
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
