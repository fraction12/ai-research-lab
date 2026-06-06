#!/usr/bin/env python3
"""Append a non-mutating checkup for a paper-campaign run."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
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


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_command(args: list[str], timeout: int = 20) -> dict[str, Any]:
    try:
        proc = subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=False)
        return {"command": args, "exit_code": proc.returncode, "stdout": proc.stdout[-6000:], "stderr": proc.stderr[-6000:]}
    except Exception as exc:  # pragma: no cover - checkup should report, not crash.
        return {"command": args, "exit_code": 1, "error": repr(exc)}


def active_processes() -> dict[str, Any]:
    if platform.system().lower() == "windows":
        return run_command(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process python,llama-cli,llama-completion,llama-server -ErrorAction SilentlyContinue "
                "| Select-Object ProcessName,Id,CPU,StartTime | ConvertTo-Json -Compress",
            ]
        )
    return run_command(["ps", "-axo", "pid=,comm=,etime="])


def gpu_status() -> dict[str, Any]:
    return run_command(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.used,memory.free,utilization.gpu,temperature.gpu",
            "--format=csv,noheader",
        ]
    )


def latest_file(root: Path, pattern: str) -> dict[str, Any] | None:
    files = sorted(root.glob(pattern), key=lambda path: path.stat().st_mtime if path.exists() else 0)
    if not files:
        return None
    path = files[-1]
    stat = path.stat()
    return {"path": str(path), "size_bytes": stat.st_size, "modified_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_mtime))}


def jsonl_count(path: Path | None) -> int | None:
    if path is None or not path.exists():
        return None
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def summarize_records(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    counts: dict[str, int] = {}
    failures: dict[str, int] = {}
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                failures["json_decode_error"] = failures.get("json_decode_error", 0) + 1
                continue
            control = str(row.get("control_id", "unknown"))
            counts[control] = counts.get(control, 0) + 1
            failure = row.get("failure_class")
            if failure:
                failures[str(failure)] = failures.get(str(failure), 0) + 1
    return {"counts_by_control": counts, "failure_counts": failures}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Record a paper campaign run checkup.")
    ap.add_argument("--raw-dir", type=Path, default=DEFAULT_TRACK01_ROOT / "raw")
    ap.add_argument("--summary-dir", type=Path, default=DEFAULT_TRACK02_ROOT)
    ap.add_argument("--run-label", default="")
    args = ap.parse_args(argv)

    records_info = latest_file(args.raw_dir, f"{args.run_label}*model-loop-records.jsonl" if args.run_label else "*model-loop-records.jsonl")
    run_info = latest_file(args.raw_dir, f"{args.run_label}*model-loop-run-info.json" if args.run_label else "*model-loop-run-info.json")
    records_path = Path(records_info["path"]) if records_info else None

    checkup = {
        "schema_version": 1,
        "checked_utc": now_utc(),
        "host": platform.node(),
        "raw_dir": str(args.raw_dir),
        "summary_dir": str(args.summary_dir),
        "gpu": gpu_status(),
        "processes": active_processes(),
        "latest_records": records_info,
        "latest_run_info": run_info,
        "record_count": jsonl_count(records_path),
        "record_summary": summarize_records(records_path),
        "stop_rule_indicators": [],
    }
    if checkup["gpu"].get("exit_code") != 0:
        checkup["stop_rule_indicators"].append("gpu_status_unavailable")
    if records_info is None:
        checkup["stop_rule_indicators"].append("no_model_loop_records_found")

    args.summary_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.summary_dir / "periodic-checkups.jsonl"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(checkup, sort_keys=True) + "\n")
    print(json.dumps({"appended": str(log_path), "record_count": checkup["record_count"], "stop_rule_indicators": checkup["stop_rule_indicators"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
