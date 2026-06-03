#!/usr/bin/env python3
"""Benchmark Flashcache wrapper cache-aware calls against direct llama.cpp calls."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "benchmarks"))

import llama_cpp_prompt_cache_benchmark as lcb  # noqa: E402
import ollama_workflow_benchmark as owb  # noqa: E402
from flashcache.cache import build_cache_key, parse_chat_request  # noqa: E402
from flashcache.llama_cpp import ManagedLlamaServer, llama_server_version  # noqa: E402
from flashcache.wrapper import BoundaryTimings, FlashcacheConfig, FlashcacheWrapper, timing_record  # noqa: E402


DEFAULT_MODEL = ROOT / "benchmarks" / "models" / "gemma-3-270m-it-Q8_0.gguf"
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "flashcache-results"
DEFAULT_CACHE_DIR = ROOT / "benchmarks" / "flashcache"


def progress(message: str) -> None:
    print(f"[flashcache-wrapper-benchmark] {message}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare direct llama.cpp prompts with Flashcache wrapper calls.")
    parser.add_argument("--server-bin", default="llama-server", help="llama.cpp server binary.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="Path to a GGUF model.")
    parser.add_argument("--hf-repo", help="Hugging Face GGUF repo for llama.cpp -hf loading.")
    parser.add_argument("--fixture", type=Path, default=owb.DEFAULT_FIXTURE, help="Workflow fixture JSON path.")
    parser.add_argument("--scenario", action="append", help="Use only the named scenario. Can be repeated.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for result JSON.")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Flashcache artifact directory.")
    parser.add_argument("--ctx-size", type=int, default=4096, help="llama.cpp context size.")
    parser.add_argument("--predict", type=int, default=8, help="Generated tokens per completion request.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    parser.add_argument("--timeout", type=float, default=120.0, help="HTTP/server timeout in seconds.")
    parser.add_argument("--prime-n-predict", type=int, default=1, help="Generated tokens while priming prefix slot.")
    parser.add_argument(
        "--cache-mode",
        choices=["cold", "hot", "session"],
        default="cold",
        help="Measure miss-plus-hit, restore-every-turn hot cache, or restore-once session-resident cache behavior.",
    )
    parser.add_argument(
        "--server-mode",
        choices=["per-request", "persistent"],
        default="per-request",
        help="Run each request with a fresh llama.cpp server or keep a server alive for each benchmark phase.",
    )
    args = parser.parse_args()
    validate_args(args)
    return args


def validate_args(args: argparse.Namespace) -> None:
    if args.cache_mode == "session" and args.server_mode != "persistent":
        raise SystemExit("--cache-mode session requires --server-mode persistent")


def sum_prompt_ms(runs: list[dict[str, Any]], timing_key: str = "timings") -> float | None:
    values = []
    for run in runs:
        value = run.get(timing_key, {}).get("prompt_ms")
        if isinstance(value, (int, float)):
            values.append(float(value))
    return sum(values) if values else None


def direct_boundary_timings(response: dict[str, Any]) -> dict[str, float]:
    timing = timing_record(response)
    wall_ms = timing.get("wall_ms")
    return {"direct_completion_ms": float(wall_ms)} if isinstance(wall_ms, (int, float)) else {}


def config_from_args(args: argparse.Namespace, *, existing_base_url: str | None = None) -> FlashcacheConfig:
    return FlashcacheConfig(
        model_path=args.model,
        hf_repo=args.hf_repo,
        server_bin=args.server_bin,
        ctx_size=args.ctx_size,
        timeout=args.timeout,
        cache_dir=args.cache_dir,
        prime_n_predict=args.prime_n_predict,
        existing_base_url=existing_base_url,
    )


def direct_run(args: argparse.Namespace, scenario: dict[str, Any], client: Any) -> dict[str, Any]:
    response = client.completion(
        scenario["prompt"],
        n_predict=args.predict,
        temperature=args.temperature,
    )
    return {
        "scenario": scenario["name"],
        "prompt_bytes": scenario["prompt_bytes"],
        "prompt_sha256": scenario["prompt_sha256"],
        "timings": timing_record(response),
        "boundary_timings": direct_boundary_timings(response),
        "content_excerpt": str(response.get("content", ""))[:300],
    }


def direct_baseline(args: argparse.Namespace, prompt_set: dict[str, Any]) -> list[dict[str, Any]]:
    runs = []
    config = config_from_args(args)
    if args.server_mode == "persistent":
        server_config = config.server_config()
        with ManagedLlamaServer(server_config, label="flashcache-direct-persistent") as client:
            for scenario in prompt_set["scenarios"]:
                progress(f"direct-full: {scenario['name']}")
                runs.append(direct_run(args, scenario, client))
        return runs

    for scenario in prompt_set["scenarios"]:
        progress(f"direct-full: {scenario['name']}")
        with ManagedLlamaServer(config.server_config(), label=f"flashcache-direct-{scenario['name']}") as client:
            runs.append(direct_run(args, scenario, client))
    return runs


def wrapper_payload(args: argparse.Namespace, prompt_set: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    block_hashes = [block["sha256"] for block in prompt_set["prefix_manifest"]]
    namespace = f"{prompt_set['fixture_name']}:{prompt_set['prefix_prompt_sha256'][:16]}"
    tail_prompt = scenario["prompt"][len(prompt_set["prefix_prompt"]) :].strip()
    return {
        "model": args.hf_repo or str(args.model),
        "messages": [{"role": "user", "content": tail_prompt}],
        "max_tokens": args.predict,
        "temperature": args.temperature,
        "ssd_cache": {
            "namespace": namespace,
            "stable_prefix_text": prompt_set["prefix_prompt"],
            "block_hashes": block_hashes,
            "debug": True,
        },
    }


def wrapper_run_scenario(
    args: argparse.Namespace,
    prompt_set: dict[str, Any],
    wrapper: FlashcacheWrapper,
    scenario: dict[str, Any],
    *,
    progress_label: str,
) -> dict[str, Any]:
    progress(f"{progress_label}: {scenario['name']}")
    response, headers = wrapper.complete(wrapper_payload(args, prompt_set, scenario))
    telemetry = response.get("flashcache", {})
    return {
        "scenario": scenario["name"],
        "cache_state": telemetry.get("cache_state"),
        "headers": headers,
        "telemetry": telemetry,
        "boundary_timings": telemetry.get("boundary_timings", {}),
        "assistant_excerpt": response["choices"][0]["message"]["content"][:300],
    }


def wrapper_runs_with_client(
    args: argparse.Namespace,
    prompt_set: dict[str, Any],
    wrapper: FlashcacheWrapper,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    prewarm = []
    if args.cache_mode == "hot" and prompt_set["scenarios"]:
        prewarm.append(
            wrapper_run_scenario(
                args,
                prompt_set,
                wrapper,
                prompt_set["scenarios"][0],
                progress_label="cache-prewarm",
            )
        )

    runs = []
    for scenario in prompt_set["scenarios"]:
        runs.append(wrapper_run_scenario(args, prompt_set, wrapper, scenario, progress_label="cache-aware"))
    return prewarm, runs


def cache_hit_count(runs: list[dict[str, Any]]) -> int:
    return sum(1 for run in runs if run.get("cache_state") in {"hit", "session-hit"})


def cache_key_for_payload(
    wrapper: FlashcacheWrapper,
    payload: dict[str, Any],
    boundary: BoundaryTimings | None = None,
) -> tuple[str, Any, Any]:
    with (boundary.phase("request_parse_ms") if boundary else nullcontext()):
        parsed = parse_chat_request(payload)
    with (boundary.phase("server_version_ms") if boundary else nullcontext()):
        server_version = wrapper.server_version()
    with (boundary.phase("cache_key_ms") if boundary else nullcontext()):
        cache_key, _key_material = build_cache_key(
            namespace=parsed.namespace,
            model_identity=wrapper.config.model_identity(),
            server_version=server_version,
            ctx_size=wrapper.config.ctx_size,
            llama_settings=wrapper.config.llama_settings(),
            stable_prefix_prompt=parsed.stable_prefix_prompt,
            block_hashes=parsed.block_hashes,
        )
    return cache_key, parsed, server_version


def session_run_scenario(
    args: argparse.Namespace,
    prompt_set: dict[str, Any],
    wrapper: FlashcacheWrapper,
    client: Any,
    scenario: dict[str, Any],
    cache_key: str,
    server_version: str,
    slot_file_bytes: int | None,
) -> dict[str, Any]:
    progress(f"cache-session: {scenario['name']}")
    boundary = BoundaryTimings()
    with boundary.phase("request_parse_ms"):
        parsed = parse_chat_request(wrapper_payload(args, prompt_set, scenario))
    with boundary.phase("tail_completion_ms"):
        llama_response = client.completion(
            parsed.full_prompt,
            n_predict=parsed.max_tokens,
            temperature=parsed.temperature,
        )
    timings = timing_record(llama_response)
    telemetry = {
        "cache_state": "session-hit",
        "cache_key": cache_key,
        "fallback_reason": None,
        "server_version": server_version,
        "slot_file_bytes": slot_file_bytes,
        "prompt_ms": timings.get("prompt_ms"),
        "prompt_n": timings.get("prompt_n"),
        "timings": timings,
        "boundary_timings": boundary.finish(),
    }
    return {
        "scenario": scenario["name"],
        "cache_state": "session-hit",
        "headers": {
            "X-Flashcache-Cache": "session-hit",
            "X-Flashcache-Key": cache_key,
        },
        "telemetry": telemetry,
        "boundary_timings": telemetry["boundary_timings"],
        "assistant_excerpt": str(llama_response.get("content", ""))[:300],
    }


def session_wrapper_runs(args: argparse.Namespace, prompt_set: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    if not prompt_set["scenarios"]:
        return [], {}, []

    prewarm_config = config_from_args(args)
    prewarm_wrapper = FlashcacheWrapper(prewarm_config)
    prewarm = [
        wrapper_run_scenario(
            args,
            prompt_set,
            prewarm_wrapper,
            prompt_set["scenarios"][0],
            progress_label="cache-prewarm",
        )
    ]

    server_config = config_from_args(args).server_config()
    server = ManagedLlamaServer(server_config, label="flashcache-wrapper-session")
    setup_boundary = BoundaryTimings()
    with setup_boundary.phase("server_enter_ms"):
        client = server.__enter__()
    try:
        wrapper = FlashcacheWrapper(config_from_args(args, existing_base_url=server_config.base_url))
        cache_key, _parsed, server_version = cache_key_for_payload(
            wrapper,
            wrapper_payload(args, prompt_set, prompt_set["scenarios"][0]),
            setup_boundary,
        )
        with setup_boundary.phase("cache_lookup_ms"):
            manifest = wrapper.store.load(cache_key)
        if manifest is None or not wrapper.store.slot_path(manifest.slot_filename).exists():
            raise SystemExit(f"Session cache prewarm did not create a restorable slot for cache key {cache_key}")

        with setup_boundary.phase("slot_restore_ms"):
            restore_response = client.restore_slot(manifest.slot_filename)
        restore_ms = restore_response.get("timings", {}).get("restore_ms") or restore_response.get("_wall_ms")
        setup = {
            "cache_state": "session-restored",
            "cache_key": cache_key,
            "slot_filename": manifest.slot_filename,
            "slot_file_bytes": manifest.slot_file_bytes,
            "restored_tokens": restore_response.get("n_restored"),
            "restore_ms": restore_ms,
            "boundary_timings": setup_boundary.finish(),
        }
        runs = [
            session_run_scenario(
                args,
                prompt_set,
                wrapper,
                client,
                scenario,
                cache_key,
                server_version,
                manifest.slot_file_bytes,
            )
            for scenario in prompt_set["scenarios"]
        ]
        return prewarm, setup, runs
    finally:
        server.stop()


def wrapper_runs(args: argparse.Namespace, prompt_set: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any] | None, list[dict[str, Any]]]:
    if args.cache_mode == "session":
        return session_wrapper_runs(args, prompt_set)

    config = config_from_args(args)
    if args.server_mode == "persistent":
        server_config = config.server_config()
        with ManagedLlamaServer(server_config, label="flashcache-wrapper-persistent"):
            wrapper = FlashcacheWrapper(config_from_args(args, existing_base_url=server_config.base_url))
            prewarm, runs = wrapper_runs_with_client(args, prompt_set, wrapper)
            return prewarm, None, runs

    wrapper = FlashcacheWrapper(config)
    prewarm, runs = wrapper_runs_with_client(args, prompt_set, wrapper)
    return prewarm, None, runs


def write_result(result: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_slug = Path(str(result["metadata"]["model"])).stem
    model_slug = model_slug.replace("/", "-").replace(":", "-")
    fixture_slug = Path(str(result["metadata"]["fixture"])).stem
    path = output_dir / f"{timestamp}-{model_slug}-{fixture_slug}-flashcache-wrapper.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def main() -> int:
    args = parse_args()
    if not args.hf_repo and not args.model.exists():
        print(f"Model file not found: {args.model}")
        return 2
    prompt_set = lcb.build_prompt_set(SimpleNamespace(fixture=args.fixture, scenario=args.scenario))
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    direct = direct_baseline(args, prompt_set)
    prewarm, session_setup, cached = wrapper_runs(args, prompt_set)

    direct_sum = sum_prompt_ms(direct)
    wrapper_values = []
    for run in cached:
        value = run.get("telemetry", {}).get("timings", {}).get("prompt_ms")
        if isinstance(value, (int, float)):
            wrapper_values.append(float(value))
    wrapper_sum = sum(wrapper_values) if wrapper_values else None
    delta = None
    ratio = None
    if direct_sum is not None and wrapper_sum is not None:
        delta = direct_sum - wrapper_sum
        ratio = delta / direct_sum if direct_sum else None
    hits = cache_hit_count(cached)

    result = {
        "metadata": {
            "started_at": started_at,
            "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "server_bin": args.server_bin,
            "server_version": llama_server_version(args.server_bin),
            "model": args.hf_repo or str(args.model),
            "model_bytes": None if args.hf_repo else args.model.stat().st_size,
            "fixture": str(args.fixture),
            "fixture_hash": prompt_set["fixture_hash"],
            "ctx_size": args.ctx_size,
            "predict": args.predict,
            "temperature": args.temperature,
            "prime_n_predict": args.prime_n_predict,
            "server_mode": args.server_mode,
            "cache_mode": args.cache_mode,
            "cache_dir": str(args.cache_dir),
        },
        "prompt_set": {
            "fixture_name": prompt_set["fixture_name"],
            "prefix_block_names": prompt_set["prefix_block_names"],
            "prefix_prompt_bytes": prompt_set["prefix_prompt_bytes"],
            "prefix_prompt_sha256": prompt_set["prefix_prompt_sha256"],
        },
        "direct_full_prompt": direct,
        "wrapper_prewarm": prewarm,
        "wrapper_session_setup": session_setup,
        "wrapper_cache_aware": cached,
        "comparison": {
            "direct_prompt_ms_sum": direct_sum,
            "wrapper_prompt_ms_sum": wrapper_sum,
            "direct_minus_wrapper_prompt_ms": delta,
            "direct_minus_wrapper_prompt_ratio": ratio,
            "wrapper_cache_hit_rate": hits / len(cached) if cached else None,
            "interpretation": "Positive delta means Flashcache wrapper reduced prompt processing time versus direct full-prompt llama.cpp calls.",
        },
    }
    output_path = write_result(result, args.output_dir)
    print(f"Direct prompt ms sum: {direct_sum}")
    print(f"Wrapper prompt ms sum: {wrapper_sum}")
    print(f"Direct minus wrapper: {delta}")
    print(f"Wrapper cache hit rate: {result['comparison']['wrapper_cache_hit_rate']}")
    print(f"Result JSON: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
