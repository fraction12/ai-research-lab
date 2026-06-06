#!/usr/bin/env python3
"""Preflight readiness checks for the paper-grade Code-mode KV campaign."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


BENCHMARKS_DIR = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARKS_DIR.parents[2]
if str(BENCHMARKS_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARKS_DIR))

import bfcl_code_mode_kv_adapter as bfcl_adapter  # noqa: E402
import kv_capsule_profiles  # noqa: E402


DEFAULT_EXPERIMENT_ID = "paper-grade-code-mode-kv-capsule-evaluation-2026-06-05"
DEFAULT_TRACK01_ROOT = BENCHMARKS_DIR / DEFAULT_EXPERIMENT_ID
DEFAULT_TRACK02_ROOT = (
    REPO_ROOT
    / "research"
    / "02-quality-gated-stateful-kv-reuse"
    / "experiments"
    / DEFAULT_EXPERIMENT_ID
)
PROCESS_NAMES = ("python", "python.exe", "llama-cli", "llama-cli.exe", "llama-completion", "llama-completion.exe", "llama-server", "llama-server.exe")


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_command(args: list[str], *, cwd: Path | None = None, timeout: int = 30) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        proc = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)
        return {
            "command": args,
            "cwd": str(cwd) if cwd else None,
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-8000:],
            "stderr": proc.stderr[-8000:],
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        }
    except FileNotFoundError as exc:
        return {"command": args, "cwd": str(cwd) if cwd else None, "exit_code": 127, "error": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {
            "command": args,
            "cwd": str(cwd) if cwd else None,
            "exit_code": 124,
            "stdout": (exc.stdout or "")[-8000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-8000:] if isinstance(exc.stderr, str) else "",
            "error": "timeout",
        }


def git_info() -> dict[str, Any]:
    return {
        "head": run_command(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT),
        "status": run_command(["git", "status", "--short", "--branch"], cwd=REPO_ROOT),
        "ignored_raw_probe": run_command(
            [
                "git",
                "check-ignore",
                "-v",
                str(DEFAULT_TRACK01_ROOT.relative_to(REPO_ROOT) / "raw" / "probe.jsonl"),
                str(DEFAULT_TRACK01_ROOT.relative_to(REPO_ROOT) / "cache" / "probe.bin"),
            ],
            cwd=REPO_ROOT,
        ),
    }


def process_check() -> dict[str, Any]:
    system = platform.system().lower()
    if system == "windows":
        script = (
            "Get-Process python,llama-cli,llama-completion,llama-server -ErrorAction SilentlyContinue "
            "| Select-Object ProcessName,Id,CPU,StartTime "
            "| ConvertTo-Json -Compress"
        )
        result = run_command(["powershell", "-NoProfile", "-Command", script])
        return {"method": "powershell_get_process", "result": result, "active_processes": parse_json_output(result)}
    result = run_command(["ps", "-axo", "pid=,comm=,etime="])
    active: list[dict[str, str]] = []
    for line in result.get("stdout", "").splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) < 2:
            continue
        name = Path(parts[1]).name
        if name in PROCESS_NAMES:
            active.append({"pid": parts[0], "name": name, "etime": parts[2] if len(parts) > 2 else ""})
    return {"method": "ps", "result": result, "active_processes": active}


def parse_json_output(result: dict[str, Any]) -> Any:
    text = (result.get("stdout") or "").strip()
    if not text:
        return []
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return {"parse_error": True, "raw": text[-2000:]}
    if isinstance(value, list):
        return value
    return [value]


def gpu_check() -> dict[str, Any]:
    if not shutil.which("nvidia-smi"):
        return {"available": False, "reason": "nvidia-smi_not_found"}
    result = run_command(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu",
            "--format=csv,noheader",
        ],
        timeout=20,
    )
    return {"available": result["exit_code"] == 0, "result": result}


def profile_check(profile: str) -> dict[str, Any]:
    resolved = kv_capsule_profiles.resolve_profile(profile)
    paths = {
        "model_path": Path(resolved.model_path),
        "bundle": Path(resolved.bundle),
        "llama_dll": Path(resolved.llama_dll),
        "raw_dir": Path(resolved.raw_dir),
        "cache_dir": Path(resolved.cache_dir),
    }
    status = {
        key: {
            "path": str(path),
            "exists": path.exists(),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
        }
        for key, path in paths.items()
    }
    return {
        "profile_id": resolved.profile_id,
        "model_family": resolved.model_family,
        "model_name": resolved.model_name,
        "backend": resolved.backend,
        "state_route": resolved.state_route,
        "path_status": status,
    }


def py_compile_check() -> dict[str, Any]:
    files = [
        BENCHMARKS_DIR / "bfcl_code_mode_kv_adapter.py",
        BENCHMARKS_DIR / "code_mode_kv_capsule_model_loop_runner.py",
        BENCHMARKS_DIR / "code_mode_tool_surface.py",
        BENCHMARKS_DIR / "kv_capsule_profiles.py",
        BENCHMARKS_DIR / "paper_campaign_readiness.py",
        BENCHMARKS_DIR / "paper_campaign_checkup.py",
    ]
    return run_command([sys.executable, "-m", "py_compile", *[str(path) for path in files]], cwd=REPO_ROOT)


def bfcl_no_model_dry_run(out_dir: Path, per_category: int) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    packet = out_dir / "bfcl-readiness-control-packet.jsonl"
    summary = out_dir / "bfcl-readiness-summary.json"
    argv = [
        "--category",
        "simple",
        "--category",
        "multiple",
        "--category",
        "parallel",
        "--per-category",
        str(per_category),
        "--out",
        str(packet),
        "--summary-out",
        str(summary),
    ]
    started = time.perf_counter()
    try:
        bfcl_adapter.main(argv)
        summary_data = json.loads(summary.read_text(encoding="utf-8"))
        return {
            "status": "passed",
            "packet": str(packet),
            "summary": str(summary),
            "summary_data": summary_data,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        }
    except Exception as exc:  # pragma: no cover - defensive readiness reporting.
        return {"status": "failed", "error": repr(exc), "elapsed_ms": round((time.perf_counter() - started) * 1000, 3)}


def evaluate(report: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if report["git"]["head"]["exit_code"] != 0:
        blockers.append("git_head_unavailable")
    if report["git"]["ignored_raw_probe"]["exit_code"] != 0:
        blockers.append("paper_campaign_raw_cache_paths_not_ignored")
    if report["py_compile"]["exit_code"] != 0:
        blockers.append("python_compile_failed")
    if report["bfcl_no_model_dry_run"]["status"] != "passed":
        blockers.append("bfcl_no_model_dry_run_failed")

    active = report["processes"].get("active_processes") or []
    if active:
        blockers.append("duplicate_python_or_llama_processes_active")

    profile_paths = report["model_profile"]["path_status"]
    for key in ("model_path", "bundle", "llama_dll"):
        if not profile_paths[key]["exists"]:
            blockers.append(f"model_profile_missing_{key}")

    if not report["gpu"].get("available"):
        warnings.append("gpu_status_unavailable")

    if report["git"]["status"]["exit_code"] == 0 and (report["git"]["status"]["stdout"] or "").strip().splitlines()[1:]:
        warnings.append("worktree_has_changes")

    return {
        "ready": not blockers,
        "blockers": blockers,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check paper campaign execution readiness.")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_TRACK02_ROOT)
    ap.add_argument("--profile", default="gemma4-12b")
    ap.add_argument("--bfcl-per-category", type=int, default=2)
    args = ap.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "schema_version": 1,
        "checked_utc": now_utc(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "repo_root": str(REPO_ROOT),
        "track01_root": str(DEFAULT_TRACK01_ROOT),
        "track02_root": str(args.out_dir),
        "git": git_info(),
        "gpu": gpu_check(),
        "processes": process_check(),
        "model_profile": profile_check(args.profile),
        "py_compile": py_compile_check(),
        "bfcl_no_model_dry_run": bfcl_no_model_dry_run(args.out_dir / "readiness-raw", args.bfcl_per_category),
    }
    report["evaluation"] = evaluate(report)
    output = args.out_dir / "execution-readiness.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"ready": report["evaluation"]["ready"], "output": str(output), **report["evaluation"]}, indent=2))
    return 0 if report["evaluation"]["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
