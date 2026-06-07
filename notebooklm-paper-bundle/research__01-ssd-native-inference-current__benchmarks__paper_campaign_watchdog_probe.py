#!/usr/bin/env python3
"""Single-command watchdog probe for the BFCL paper campaign."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


BENCHMARKS_DIR = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARKS_DIR.parents[2]
EXPERIMENT_ID = "paper-grade-code-mode-kv-capsule-evaluation-2026-06-05"
RAW_DIR = BENCHMARKS_DIR / EXPERIMENT_ID / "raw"
CACHE_DIR = BENCHMARKS_DIR / EXPERIMENT_ID / "cache"
SUMMARY_DIR = REPO_ROOT / "research" / "02-quality-gated-stateful-kv-reuse" / "experiments" / EXPERIMENT_ID
MARKER_PATH = SUMMARY_DIR / "calibration-job.json"
CALIBRATION_LABEL = "bfcl-paper-calibration-detached-v2"
CALIBRATION_TASK = "BFCLCalibrationDetachedV2"
PAPER_LABEL = "bfcl-paper-selected-cohort-v1"
PAPER_TASK = "BFCLPaperSelectedCohortV1"
EXPECTED_CALIBRATION_RECORDS = 3514
STALE_SECONDS = 30 * 60


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


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": repr(exc)}


def jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def file_info(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False}
    stat = path.stat()
    age = time.time() - stat.st_mtime
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_mtime)),
        "age_seconds": round(age, 3),
    }


def task_status(task_name: str) -> dict[str, Any]:
    if platform.system().lower() != "windows":
        return {"available": False, "reason": "not_windows"}
    result = run_command(["schtasks", "/Query", "/TN", task_name, "/V", "/FO", "LIST"])
    status = "unknown"
    for line in str(result.get("stdout", "")).splitlines():
        if line.startswith("Status:"):
            status = line.split(":", 1)[1].strip()
            break
    result["status"] = status
    return result


def process_status() -> dict[str, Any]:
    if platform.system().lower() == "windows":
        return run_command(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process python,py,llama-completion,llama-server -ErrorAction SilentlyContinue "
                "| Select-Object ProcessName,Id,CPU,StartTime | ConvertTo-Json -Compress",
            ]
        )
    return run_command(["ps", "-axo", "pid=,comm=,etime="])


def run_info_path(label: str) -> Path:
    return RAW_DIR / f"{label}-model-loop-run-info.json"


def records_path(label: str) -> Path:
    return RAW_DIR / f"{label}-model-loop-records.jsonl"


def stdout_path(label: str) -> Path:
    return RAW_DIR / f"{label}-stdout.log"


def stderr_path(label: str) -> Path:
    return RAW_DIR / f"{label}-stderr.log"


def active_from_marker(marker: dict[str, Any]) -> tuple[str, str, str]:
    if marker.get("status") == "paper_test_started" or marker.get("paper_run_label"):
        return PAPER_LABEL, PAPER_TASK, "paper"
    return CALIBRATION_LABEL, CALIBRATION_TASK, "calibration"


def selector_command() -> list[str]:
    return [
        sys.executable,
        str(BENCHMARKS_DIR / "paper_campaign_selected_cohort.py"),
        "--calibration-run-label",
        CALIBRATION_LABEL,
        "--paper-run-label",
        PAPER_LABEL,
        "--raw-dir",
        str(RAW_DIR),
        "--cache-dir",
        str(CACHE_DIR),
        "--summary-dir",
        str(SUMMARY_DIR),
        "--target-rows",
        "200",
        "--min-clean-rows",
        "100",
        "--launch-detached",
        "--task-name",
        PAPER_TASK,
    ]


def maybe_launch_paper_after_calibration(calibration_info: dict[str, Any]) -> dict[str, Any]:
    if int(calibration_info.get("exit_code", -1)) != 0:
        return {
            "action": "alert",
            "status": "calibration_failed",
            "message": "BFCL calibration finished with non-zero exit; paper test not launched.",
        }
    result = run_command(selector_command(), timeout=120)
    status = "paper_launch_attempted"
    message = "BFCL calibration completed; selected-cohort launcher ran."
    if result.get("exit_code") == 0:
        status = "paper_test_started"
        message = "BFCL calibration completed and selected-cohort paper test started."
    elif result.get("exit_code") == 3:
        status = "below_minimum_clean_rows"
        message = "BFCL calibration completed but clean cohort is below 100 rows; paper test not launched."
    elif result.get("exit_code") == 4:
        status = "below_target_clean_rows"
        message = "BFCL calibration completed with 100-199 clean rows; waiting before minimum-cohort test."
    elif result.get("exit_code") == 5:
        status = "paper_launch_failed"
        message = "BFCL calibration completed but selected-cohort paper-test launch failed."
    return {"action": "alert", "status": status, "message": message, "selector_result": result}


def main() -> int:
    marker = read_json(MARKER_PATH)
    label, task_name, stage = active_from_marker(marker)
    records = records_path(label)
    run_info = run_info_path(label)
    records_info = file_info(records)
    run_info_data = read_json(run_info)
    count = jsonl_count(records)
    task = task_status(task_name)
    processes = process_status()
    status = {
        "checked_utc": now_utc(),
        "stage": stage,
        "run_label": label,
        "task_name": task_name,
        "marker_path": str(MARKER_PATH),
        "marker_status": marker.get("status"),
        "records": records_info,
        "record_count": count,
        "run_info": file_info(run_info),
        "run_info_decision": run_info_data.get("decision"),
        "run_info_exit_code": run_info_data.get("exit_code"),
        "stdout": file_info(stdout_path(label)),
        "stderr": file_info(stderr_path(label)),
        "task": {"status": task.get("status"), "exit_code": task.get("exit_code")},
        "processes_exit_code": processes.get("exit_code"),
    }

    if stage == "calibration" and run_info.exists():
        launched = maybe_launch_paper_after_calibration(run_info_data)
        print(json.dumps({**status, **launched}, indent=2))
        return 0
    if stage == "paper" and run_info.exists():
        print(
            json.dumps(
                {
                    **status,
                    "action": "alert",
                    "status": "paper_test_completed",
                    "message": "BFCL selected-cohort paper test completed.",
                },
                indent=2,
            )
        )
        return 0

    if task.get("status") == "Running" and records_info.get("exists") and records_info.get("age_seconds", STALE_SECONDS + 1) < STALE_SECONDS:
        print(json.dumps({**status, "action": "none", "status": "healthy_running"}, indent=2))
        return 0
    if task.get("status") == "Running" and not records_info.get("exists"):
        print(json.dumps({**status, "action": "none", "status": "healthy_starting"}, indent=2))
        return 0

    expected = EXPECTED_CALIBRATION_RECORDS if stage == "calibration" else None
    reason = "stalled_or_stopped"
    if expected and count >= expected:
        reason = "records_complete_but_run_info_missing"
    print(
        json.dumps(
            {
                **status,
                "action": "alert",
                "status": reason,
                "message": f"BFCL {stage} run may be stalled or stopped; inspect logs and run-info.",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
