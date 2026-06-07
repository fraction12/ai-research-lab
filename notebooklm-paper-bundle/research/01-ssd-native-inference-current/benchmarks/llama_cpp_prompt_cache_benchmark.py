#!/usr/bin/env python3
"""Benchmark llama.cpp server slot save/restore for reusable agent prefixes."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import ollama_workflow_benchmark as owb


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = ROOT / "benchmarks" / "models" / "gemma-3-270m-it-Q8_0.gguf"
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "llama-cpp-results"
DEFAULT_SLOT_CACHE_DIR = ROOT / "benchmarks" / "llama-cpp-slot-cache"
DEFAULT_PROMPT_DIR = ROOT / "benchmarks" / "llama-cpp-prompts"
DEFAULT_LOG_DIR = ROOT / "benchmarks" / "llama-cpp-logs"


class LlamaBenchmarkError(Exception):
    """Raised for expected benchmark failures."""


def progress(message: str) -> None:
    print(f"[llama-cpp-benchmark] {message}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure llama.cpp prompt cache save/restore for changed-tail workflow prompts."
    )
    parser.add_argument("--server-bin", default="llama-server", help="llama.cpp server binary.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="Path to a GGUF model.")
    parser.add_argument("--hf-repo", help="Hugging Face GGUF repo for llama.cpp -hf loading.")
    parser.add_argument("--fixture", type=Path, default=owb.DEFAULT_FIXTURE, help="Workflow fixture JSON path.")
    parser.add_argument("--scenario", action="append", help="Use only the named scenario. Can be repeated.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for JSON results.")
    parser.add_argument("--slot-cache-dir", type=Path, default=DEFAULT_SLOT_CACHE_DIR, help="Directory for slot cache files.")
    parser.add_argument("--prompt-dir", type=Path, default=DEFAULT_PROMPT_DIR, help="Directory for prompt text artifacts.")
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR, help="Directory for server logs.")
    parser.add_argument("--host", default="127.0.0.1", help="Server host.")
    parser.add_argument("--port", type=int, default=0, help="Server port. 0 chooses a free port.")
    parser.add_argument("--ctx-size", type=int, default=4096, help="llama.cpp context size.")
    parser.add_argument("--predict", type=int, default=8, help="Generated tokens per completion request.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    parser.add_argument("--slot-id", type=int, default=0, help="llama.cpp slot id to use.")
    parser.add_argument("--timeout", type=float, default=120.0, help="HTTP/server timeout in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Build prompts and result metadata without starting llama.cpp.")
    return parser.parse_args()


def free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def http_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 60.0) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = str(exc)
        raise LlamaBenchmarkError(f"HTTP {exc.code} from {url}: {body[:500]}") from exc
    except urllib.error.URLError as exc:
        raise LlamaBenchmarkError(f"Could not reach {url}: {exc}") from exc

    try:
        return json.loads(body) if body else {}
    except json.JSONDecodeError as exc:
        raise LlamaBenchmarkError(f"Non-JSON response from {url}: {body[:500]}") from exc


def wait_for_health(base_url: str, timeout: float) -> None:
    deadline = time.time() + timeout
    last_error = ""
    while time.time() < deadline:
        try:
            response = http_json("GET", base_url + "/health", timeout=3)
            if response.get("status") == "ok":
                return
            last_error = json.dumps(response)
        except LlamaBenchmarkError as exc:
            last_error = str(exc)
        time.sleep(0.25)
    raise LlamaBenchmarkError(f"llama.cpp server did not become healthy: {last_error}")


def server_command(args: argparse.Namespace, port: int) -> list[str]:
    command = [
        args.server_bin,
        "--host",
        args.host,
        "--port",
        str(port),
        "--ctx-size",
        str(args.ctx_size),
        "--parallel",
        "1",
        "--slot-save-path",
        str(args.slot_cache_dir),
        "--cache-prompt",
        "--slots",
        "--no-ui",
        "--no-warmup",
        "--log-disable",
    ]
    if args.hf_repo:
        command[1:1] = ["-hf", args.hf_repo]
    else:
        command[1:1] = ["--model", str(args.model)]
    return command


def model_identity(args: argparse.Namespace) -> str:
    return args.hf_repo or str(args.model)


def model_bytes(args: argparse.Namespace) -> int | None:
    if args.hf_repo:
        return None
    return args.model.stat().st_size


def llama_server_version(server_bin: str) -> str:
    try:
        version = subprocess.run([server_bin, "--version"], capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise LlamaBenchmarkError(f"llama.cpp server binary not found: {server_bin}") from exc
    return "\n".join(part for part in [version.stdout.strip(), version.stderr.strip()] if part)


def start_server(args: argparse.Namespace, label: str, port: int) -> tuple[subprocess.Popen[bytes], Path, float]:
    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.slot_cache_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.log_dir / f"{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{label}.log"
    command = server_command(args, port)
    started = time.perf_counter()
    log_handle = log_path.open("wb")
    process = subprocess.Popen(command, stdout=log_handle, stderr=subprocess.STDOUT)
    log_handle.close()
    try:
        wait_for_health(f"http://{args.host}:{port}", args.timeout)
    except Exception:
        process.terminate()
        raise
    return process, log_path, (time.perf_counter() - started) * 1000


def stop_server(process: subprocess.Popen[bytes]) -> float:
    started = time.perf_counter()
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=15)
    return (time.perf_counter() - started) * 1000


def build_common_prefix_text(
    fixture: dict[str, Any],
    blocks_by_name: dict[str, dict[str, Any]],
    prefix_block_names: list[str],
) -> tuple[str, list[dict[str, Any]]]:
    prompt_parts = [
        "# Local Agent Workflow Benchmark",
        "",
        f"Fixture: {fixture.get('name', 'unnamed')}",
        "",
    ]
    manifest = []
    for block_name in prefix_block_names:
        block = blocks_by_name[block_name]
        text = owb.block_text(block)
        prompt_parts.extend(
            [
                f"## Block: {block_name}",
                f"Tier: {block.get('tier', 'unknown')}",
                f"Cache-Policy: {block.get('cache_policy', 'unknown')}",
                text,
                "",
            ]
        )
        manifest.append(
            {
                "name": block_name,
                "tier": block.get("tier", "unknown"),
                "cache_policy": block.get("cache_policy", "unknown"),
                "bytes": len(text.encode("utf-8")),
                "sha256": owb.sha256_text(text),
            }
        )
    return "\n".join(prompt_parts), manifest


def build_prompt_set(args: argparse.Namespace) -> dict[str, Any]:
    fixture = owb.read_fixture(args.fixture)
    blocks_by_name = owb.index_blocks(fixture)
    scenarios = owb.selected_scenarios(fixture, args.scenario)
    prefix_block_names = owb.common_reusable_block_names(scenarios, blocks_by_name)
    prefix_prompt, prefix_manifest = build_common_prefix_text(fixture, blocks_by_name, prefix_block_names)
    scenario_prompts = []
    for scenario in scenarios:
        prompt, manifest = owb.build_prompt(fixture, blocks_by_name, scenario)
        if not prompt.startswith(prefix_prompt):
            raise LlamaBenchmarkError(f"Scenario {scenario.get('name')} does not start with the reusable prefix.")
        scenario_prompts.append(
            {
                "name": scenario.get("name", "unnamed"),
                "description": scenario.get("description"),
                "prompt": prompt,
                "prompt_bytes": len(prompt.encode("utf-8")),
                "prompt_sha256": owb.sha256_text(prompt),
                "block_manifest": manifest,
            }
        )
    return {
        "fixture_hash": owb.fixture_hash(fixture),
        "fixture_name": fixture.get("name", args.fixture.stem),
        "prefix_block_names": prefix_block_names,
        "prefix_prompt": prefix_prompt,
        "prefix_prompt_bytes": len(prefix_prompt.encode("utf-8")),
        "prefix_prompt_sha256": owb.sha256_text(prefix_prompt),
        "prefix_manifest": prefix_manifest,
        "scenarios": scenario_prompts,
    }


def write_prompts(args: argparse.Namespace, prompt_set: dict[str, Any]) -> list[Path]:
    args.prompt_dir.mkdir(parents=True, exist_ok=True)
    written = []
    prefix_path = args.prompt_dir / "llama-cpp-reusable-prefix.txt"
    prefix_path.write_text(prompt_set["prefix_prompt"], encoding="utf-8")
    written.append(prefix_path)
    for scenario in prompt_set["scenarios"]:
        path = args.prompt_dir / f"llama-cpp-{scenario['name']}.txt"
        path.write_text(scenario["prompt"], encoding="utf-8")
        written.append(path)
    return written


def completion_request(base_url: str, args: argparse.Namespace, prompt: str) -> dict[str, Any]:
    payload = {
        "prompt": prompt,
        "id_slot": args.slot_id,
        "n_predict": args.predict,
        "temperature": args.temperature,
        "cache_prompt": True,
        "timings_per_token": True,
        "stream": False,
    }
    started = time.perf_counter()
    response = http_json("POST", base_url + "/completion", payload, timeout=args.timeout)
    response["_wall_ms"] = (time.perf_counter() - started) * 1000
    return response


def timing_record(response: dict[str, Any]) -> dict[str, Any]:
    timings = response.get("timings", {})
    return {
        "wall_ms": response.get("_wall_ms"),
        "prompt_ms": timings.get("prompt_ms"),
        "prompt_n": timings.get("prompt_n"),
        "prompt_per_token_ms": timings.get("prompt_per_token_ms"),
        "predicted_ms": timings.get("predicted_ms"),
        "predicted_n": timings.get("predicted_n"),
        "predicted_per_token_ms": timings.get("predicted_per_token_ms"),
        "timings": timings,
        "content_excerpt": str(response.get("content", ""))[:400],
    }


def save_slot(base_url: str, args: argparse.Namespace, filename: str) -> dict[str, Any]:
    started = time.perf_counter()
    response = http_json(
        "POST",
        f"{base_url}/slots/{args.slot_id}?action=save",
        {"filename": filename},
        timeout=args.timeout,
    )
    response["_wall_ms"] = (time.perf_counter() - started) * 1000
    return response


def restore_slot(base_url: str, args: argparse.Namespace, filename: str) -> dict[str, Any]:
    started = time.perf_counter()
    response = http_json(
        "POST",
        f"{base_url}/slots/{args.slot_id}?action=restore",
        {"filename": filename},
        timeout=args.timeout,
    )
    response["_wall_ms"] = (time.perf_counter() - started) * 1000
    return response


def run_single_completion_server(
    args: argparse.Namespace,
    label: str,
    prompt: str,
    port: int,
) -> dict[str, Any]:
    process, log_path, startup_ms = start_server(args, label, port)
    base_url = f"http://{args.host}:{port}"
    try:
        response = completion_request(base_url, args, prompt)
    finally:
        shutdown_ms = stop_server(process)
    return {
        "server_startup_ms": startup_ms,
        "server_shutdown_ms": shutdown_ms,
        "server_log": str(log_path),
        "completion": timing_record(response),
    }


def sum_prompt_ms(runs: list[dict[str, Any]]) -> float | None:
    values = [run.get("completion", {}).get("prompt_ms") for run in runs]
    numeric = [float(value) for value in values if isinstance(value, (int, float))]
    return sum(numeric) if numeric else None


def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    if not args.hf_repo and not args.model.exists():
        raise LlamaBenchmarkError(f"Model file not found: {args.model}")
    prompt_set = build_prompt_set(args)
    prompt_paths = write_prompts(args, prompt_set)
    port = args.port or free_port(args.host)
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    slot_filename = f"{owb.sha256_text(prompt_set['prefix_prompt'])[:16]}-slot.bin"
    version = llama_server_version(args.server_bin)

    result: dict[str, Any] = {
        "metadata": {
            "started_at": started_at,
            "server_bin": args.server_bin,
            "server_version": version,
            "server_command": server_command(args, port),
            "model": model_identity(args),
            "model_bytes": model_bytes(args),
            "fixture": str(args.fixture),
            "fixture_hash": prompt_set["fixture_hash"],
            "ctx_size": args.ctx_size,
            "predict": args.predict,
            "temperature": args.temperature,
            "slot_id": args.slot_id,
            "slot_cache_dir": str(args.slot_cache_dir),
            "prompt_paths": [str(path) for path in prompt_paths],
            "dry_run": args.dry_run,
        },
        "prompt_set": {
            "fixture_name": prompt_set["fixture_name"],
            "prefix_block_names": prompt_set["prefix_block_names"],
            "prefix_prompt_bytes": prompt_set["prefix_prompt_bytes"],
            "prefix_prompt_sha256": prompt_set["prefix_prompt_sha256"],
            "prefix_manifest": prompt_set["prefix_manifest"],
            "scenarios": [
                {
                    "name": scenario["name"],
                    "description": scenario["description"],
                    "prompt_bytes": scenario["prompt_bytes"],
                    "prompt_sha256": scenario["prompt_sha256"],
                    "block_manifest": scenario["block_manifest"],
                }
                for scenario in prompt_set["scenarios"]
            ],
        },
        "slot_cache": {"filename": slot_filename},
        "baseline_full": [],
        "restored_prefix": [],
    }

    if args.dry_run:
        result["metadata"]["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        return result

    progress("prime-prefix: creating reusable prefix slot cache")
    process, log_path, startup_ms = start_server(args, "prime-prefix", port)
    base_url = f"http://{args.host}:{port}"
    try:
        prefix_response = completion_request(base_url, args, prompt_set["prefix_prompt"])
        save_response = save_slot(base_url, args, slot_filename)
    finally:
        shutdown_ms = stop_server(process)

    slot_path = args.slot_cache_dir / slot_filename
    result["prime_prefix"] = {
        "server_startup_ms": startup_ms,
        "server_shutdown_ms": shutdown_ms,
        "server_log": str(log_path),
        "completion": timing_record(prefix_response),
    }
    result["slot_cache"].update(
        {
            "path": str(slot_path),
            "exists": slot_path.exists(),
            "file_bytes": slot_path.stat().st_size if slot_path.exists() else None,
            "save_response": save_response,
        }
    )

    for scenario in prompt_set["scenarios"]:
        progress(f"baseline-full: {scenario['name']}")
        run = run_single_completion_server(args, f"baseline-{scenario['name']}", scenario["prompt"], port)
        run["scenario"] = scenario["name"]
        result["baseline_full"].append(run)

    for scenario in prompt_set["scenarios"]:
        progress(f"restored-prefix: {scenario['name']}")
        process, log_path, startup_ms = start_server(args, f"restore-{scenario['name']}", port)
        base_url = f"http://{args.host}:{port}"
        try:
            restore_response = restore_slot(base_url, args, slot_filename)
            completion_response = completion_request(base_url, args, scenario["prompt"])
        finally:
            shutdown_ms = stop_server(process)
        result["restored_prefix"].append(
            {
                "scenario": scenario["name"],
                "server_startup_ms": startup_ms,
                "server_shutdown_ms": shutdown_ms,
                "server_log": str(log_path),
                "restore_response": restore_response,
                "completion": timing_record(completion_response),
            }
        )

    baseline_sum = sum_prompt_ms(result["baseline_full"])
    restored_sum = sum_prompt_ms(result["restored_prefix"])
    delta = None
    ratio = None
    if baseline_sum is not None and restored_sum is not None:
        delta = baseline_sum - restored_sum
        ratio = delta / baseline_sum if baseline_sum else None
    result["comparison"] = {
        "baseline_prompt_ms_sum": baseline_sum,
        "restored_prompt_ms_sum": restored_sum,
        "baseline_minus_restored_prompt_ms": delta,
        "baseline_minus_restored_prompt_ratio": ratio,
        "interpretation": "Positive delta means slot restore reduced prompt processing time.",
    }
    result["metadata"]["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    return result


def write_result(result: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_slug = Path(str(result["metadata"]["model"])).stem
    model_slug = model_slug.replace("/", "-").replace(":", "-")
    fixture_slug = Path(str(result["metadata"]["fixture"])).stem
    path = output_dir / f"{timestamp}-{model_slug}-{fixture_slug}-llama-cpp-prompt-cache.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    return path


def print_summary(result: dict[str, Any]) -> None:
    print(f"Model: {result['metadata']['model']}")
    print(f"Fixture: {result['metadata']['fixture']}")
    print(f"Reusable prefix bytes: {result['prompt_set']['prefix_prompt_bytes']:,}")
    if result["metadata"]["dry_run"]:
        print("Dry run: no llama.cpp server calls executed")
        return
    print(f"Slot cache bytes: {result['slot_cache'].get('file_bytes')}")
    for run in result["baseline_full"]:
        print(
            "Baseline {scenario}: prompt_ms={prompt_ms}, prompt_n={prompt_n}".format(
                scenario=run["scenario"],
                prompt_ms=run["completion"].get("prompt_ms"),
                prompt_n=run["completion"].get("prompt_n"),
            )
        )
    for run in result["restored_prefix"]:
        print(
            "Restored {scenario}: prompt_ms={prompt_ms}, prompt_n={prompt_n}, restore_ms={restore_ms}".format(
                scenario=run["scenario"],
                prompt_ms=run["completion"].get("prompt_ms"),
                prompt_n=run["completion"].get("prompt_n"),
                restore_ms=run.get("restore_response", {}).get("timings", {}).get("restore_ms"),
            )
        )
    comparison = result.get("comparison", {})
    print(f"Baseline prompt ms sum: {comparison.get('baseline_prompt_ms_sum')}")
    print(f"Restored prompt ms sum: {comparison.get('restored_prompt_ms_sum')}")
    print(f"Baseline minus restored: {comparison.get('baseline_minus_restored_prompt_ms')}")


def main() -> int:
    args = parse_args()
    try:
        result = run_benchmark(args)
        output_path = write_result(result, args.output_dir)
    except LlamaBenchmarkError as exc:
        print(f"llama.cpp benchmark error: {exc}")
        return 2

    print_summary(result)
    print(f"Result JSON: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
