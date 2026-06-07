#!/usr/bin/env python3
"""Watchdog probe for the repeated-work speed comparison run."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from pathlib import Path
from typing import Any


BENCHMARKS_DIR = Path(__file__).resolve().parent
EXPERIMENT_ID = "paper-grade-code-mode-kv-capsule-evaluation-2026-06-05"
RAW_DIR = BENCHMARKS_DIR / EXPERIMENT_ID / "raw"
OUT_DIR = RAW_DIR / "repeated-work-speed"
DEFAULT_RUN_LABEL = "bfcl-repeated-work-speed-v1"
DEFAULT_TASK_NAME = "BFCLRepeatedWorkSpeedV1"
DEFAULT_EXPECTED_CASES = 100
DEFAULT_STALE_SECONDS = 30 * 60


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_command(args: list[str], timeout: int = 30) -> dict[str, Any]:
    try:
        proc = subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=False)
        return {
            "args": args,
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
        }
    except Exception as exc:
        return {"args": args, "exit_code": 1, "error": repr(exc)}


def file_info(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False}
    stat = path.stat()
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_mtime)),
        "age_seconds": round(time.time() - stat.st_mtime, 3),
    }


def jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": repr(exc)}


def task_status(task_name: str) -> dict[str, Any]:
    if platform.system().lower() != "windows":
        return {"available": False, "reason": "not_windows"}
    result = run_command(["schtasks", "/Query", "/TN", task_name, "/V", "/FO", "LIST"])
    status = "unknown"
    last_result = None
    for line in str(result.get("stdout", "")).splitlines():
        if line.startswith("Status:"):
            status = line.split(":", 1)[1].strip()
        elif line.startswith("Last Result:"):
            last_result = line.split(":", 1)[1].strip()
    result["status"] = status
    result["last_result"] = last_result
    return result


def process_status() -> dict[str, Any]:
    if platform.system().lower() == "windows":
        return run_command(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process python,py,node,codex,llama-completion,llama-server -ErrorAction SilentlyContinue "
                "| Select-Object ProcessName,Id,CPU,StartTime | ConvertTo-Json -Compress",
            ]
        )
    return {"available": False, "reason": "not_windows"}


def gpu_status() -> dict[str, Any]:
    result = run_command(
        [
            "nvidia-smi",
            "--query-gpu=utilization.gpu,memory.used,memory.total",
            "--format=csv,noheader,nounits",
        ],
        timeout=15,
    )
    if result.get("exit_code") == 0:
        parts = [part.strip() for part in str(result.get("stdout", "")).split(",", 2)]
        if len(parts) == 3:
            result["parsed"] = {
                "utilization_gpu_pct": int(parts[0]),
                "memory_used_mib": int(parts[1]),
                "memory_total_mib": int(parts[2]),
            }
    return result


def newest(paths: list[Path]) -> dict[str, Any]:
    existing = [path for path in paths if path.exists()]
    if not existing:
        return {"exists": False}
    latest = max(existing, key=lambda path: path.stat().st_mtime)
    info = file_info(latest)
    info["candidate_count"] = len(existing)
    return info


def kv_record_paths(out_dir: Path, run_label: str) -> list[Path]:
    """Return KV model-loop record files for original and resumed KV arms."""
    return sorted(out_dir.glob(f"{run_label}-kv*-model-loop-records.jsonl"))


def speed_record_paths(out_dir: Path, run_label: str) -> list[Path]:
    """Return speed record files for original and resumed controller runs."""
    return sorted(out_dir.glob(f"{run_label}*-speed-records.jsonl"))


def speed_summary_paths(out_dir: Path, run_label: str) -> list[Path]:
    """Return speed summary files for original and resumed controller runs."""
    return sorted(out_dir.glob(f"{run_label}*-speed-summary.json"))


def preferred_summary_path(out_dir: Path, run_label: str) -> Path:
    """Prefer the newest completed summary, including resume-only continuations."""
    summaries = speed_summary_paths(out_dir, run_label)
    if not summaries:
        return out_dir / f"{run_label}-speed-summary.json"
    return max(summaries, key=lambda path: path.stat().st_mtime)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Probe a repeated-work speed run.")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--run-label", default=DEFAULT_RUN_LABEL)
    ap.add_argument("--task-name", default=DEFAULT_TASK_NAME)
    ap.add_argument("--expected-cases", type=int, default=DEFAULT_EXPECTED_CASES)
    ap.add_argument("--stale-seconds", type=int, default=DEFAULT_STALE_SECONDS)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    record_paths = speed_record_paths(args.out_dir, args.run_label)
    summary_path = preferred_summary_path(args.out_dir, args.run_label)
    run_info_path = args.out_dir / f"{args.run_label}-run-info.json"
    kv_paths = kv_record_paths(args.out_dir, args.run_label)
    task = task_status(args.task_name)
    codex_stdout_paths = sorted(args.out_dir.glob(f"{args.run_label}-codex-*.stdout.jsonl"))
    codex_stderr_paths = sorted(args.out_dir.glob(f"{args.run_label}-codex-*.stderr.txt"))
    prompt_paths = sorted((args.out_dir / f"{args.run_label}-codex-prompts").glob("*.txt"))
    activity = newest(codex_stdout_paths + codex_stderr_paths + kv_paths + record_paths + [summary_path, run_info_path])
    summary = read_json(summary_path)
    status: dict[str, Any] = {
        "checked_utc": now_utc(),
        "run_label": args.run_label,
        "task_name": args.task_name,
        "out_dir": str(args.out_dir),
        "expected_cases": args.expected_cases,
        "task": {"status": task.get("status"), "last_result": task.get("last_result"), "exit_code": task.get("exit_code")},
        "gpu": gpu_status().get("parsed"),
        "processes_exit_code": process_status().get("exit_code"),
        "codex_prompt_count": len(prompt_paths),
        "codex_stdout_count": len(codex_stdout_paths),
        "codex_stderr_count": len(codex_stderr_paths),
        "kv_record_count": sum(jsonl_count(path) for path in kv_paths),
        "kv_record_files": [str(path) for path in kv_paths],
        "speed_record_count": sum(jsonl_count(path) for path in record_paths),
        "speed_record_files": [str(path) for path in record_paths],
        "summary": file_info(summary_path),
        "run_info": file_info(run_info_path),
        "latest_activity": activity,
    }

    if summary_path.exists():
        systems = summary.get("systems") if isinstance(summary.get("systems"), dict) else {}
        codex = systems.get("codex_ollama_regular_tools_compaction", {})
        kv = systems.get("kv_capsule_code_mode", {})
        codex_pass = int(codex.get("pass_count") or 0)
        kv_pass = int(kv.get("pass_count") or 0)
        status.update(
            {
                "action": "alert",
                "status": "completed",
                "message": "BFCL repeated-work speed run completed.",
                "codex_pass_count": codex_pass,
                "kv_pass_count": kv_pass,
                "codex_compaction_events_seen": int(codex.get("compaction_events_seen") or 0),
            }
        )
        if not codex and len(codex_stdout_paths) >= args.expected_cases and kv_pass >= args.expected_cases:
            status["status"] = "completed_resume_summary_only"
            status["message"] = (
                "BFCL repeated-work speed run completed after a KV-only resume; "
                "write a combined summary before making final comparative claims."
            )
            print(json.dumps(status, indent=2))
            return 0
        if codex_pass < args.expected_cases or kv_pass < args.expected_cases:
            status["status"] = "completed_with_quality_gap"
            status["message"] = "BFCL repeated-work speed run completed but at least one arm missed the pass-count target."
        print(json.dumps(status, indent=2))
        return 0

    task_running = task.get("status") == "Running"
    fresh = bool(activity.get("exists")) and float(activity.get("age_seconds", args.stale_seconds + 1)) < args.stale_seconds
    if task_running and fresh:
        status.update({"action": "none", "status": "healthy_running"})
        print(json.dumps(status, indent=2))
        return 0
    if task_running and not activity.get("exists"):
        status.update({"action": "none", "status": "healthy_starting"})
        print(json.dumps(status, indent=2))
        return 0

    status.update(
        {
            "action": "alert",
            "status": "stalled_or_stopped",
            "message": "BFCL repeated-work speed run may be stalled or stopped; inspect task state, Codex stderr, KV stderr, and GPU/process status.",
        }
    )
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
