#!/usr/bin/env python3
"""Benchmark Flashcache wrapper cache-aware calls against direct llama.cpp calls."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "benchmarks"))

import llama_cpp_prompt_cache_benchmark as lcb  # noqa: E402
import ollama_workflow_benchmark as owb  # noqa: E402
from flashcache.llama_cpp import ManagedLlamaServer, llama_server_version  # noqa: E402
from flashcache.wrapper import FlashcacheConfig, FlashcacheWrapper, timing_record  # noqa: E402


DEFAULT_MODEL = ROOT / "benchmarks" / "models" / "gemma-3-270m-it-Q8_0.gguf"
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "flashcache-results"
DEFAULT_CACHE_DIR = ROOT / "benchmarks" / "flashcache"


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
    return parser.parse_args()


def sum_prompt_ms(runs: list[dict[str, Any]], timing_key: str = "timings") -> float | None:
    values = []
    for run in runs:
        value = run.get(timing_key, {}).get("prompt_ms")
        if isinstance(value, (int, float)):
            values.append(float(value))
    return sum(values) if values else None


def direct_baseline(args: argparse.Namespace, prompt_set: dict[str, Any]) -> list[dict[str, Any]]:
    runs = []
    config = FlashcacheConfig(
        model_path=args.model,
        hf_repo=args.hf_repo,
        server_bin=args.server_bin,
        ctx_size=args.ctx_size,
        timeout=args.timeout,
        cache_dir=args.cache_dir,
        prime_n_predict=args.prime_n_predict,
    )
    for scenario in prompt_set["scenarios"]:
        with ManagedLlamaServer(config.server_config(), label=f"flashcache-direct-{scenario['name']}") as client:
            response = client.completion(
                scenario["prompt"],
                n_predict=args.predict,
                temperature=args.temperature,
            )
        runs.append(
            {
                "scenario": scenario["name"],
                "prompt_bytes": scenario["prompt_bytes"],
                "prompt_sha256": scenario["prompt_sha256"],
                "timings": timing_record(response),
                "content_excerpt": str(response.get("content", ""))[:300],
            }
        )
    return runs


def wrapper_runs(args: argparse.Namespace, prompt_set: dict[str, Any]) -> list[dict[str, Any]]:
    config = FlashcacheConfig(
        model_path=args.model,
        hf_repo=args.hf_repo,
        server_bin=args.server_bin,
        ctx_size=args.ctx_size,
        timeout=args.timeout,
        cache_dir=args.cache_dir,
        prime_n_predict=args.prime_n_predict,
    )
    wrapper = FlashcacheWrapper(config)
    runs = []
    block_hashes = [block["sha256"] for block in prompt_set["prefix_manifest"]]
    namespace = f"{prompt_set['fixture_name']}:{prompt_set['prefix_prompt_sha256'][:16]}"
    for scenario in prompt_set["scenarios"]:
        tail_prompt = scenario["prompt"][len(prompt_set["prefix_prompt"]) :].strip()
        payload = {
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
        response, headers = wrapper.complete(payload)
        telemetry = response.get("flashcache", {})
        runs.append(
            {
                "scenario": scenario["name"],
                "cache_state": telemetry.get("cache_state"),
                "headers": headers,
                "telemetry": telemetry,
                "assistant_excerpt": response["choices"][0]["message"]["content"][:300],
            }
        )
    return runs


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
    cached = wrapper_runs(args, prompt_set)

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
    hits = sum(1 for run in cached if run.get("cache_state") == "hit")

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
            "cache_dir": str(args.cache_dir),
        },
        "prompt_set": {
            "fixture_name": prompt_set["fixture_name"],
            "prefix_block_names": prompt_set["prefix_block_names"],
            "prefix_prompt_bytes": prompt_set["prefix_prompt_bytes"],
            "prefix_prompt_sha256": prompt_set["prefix_prompt_sha256"],
        },
        "direct_full_prompt": direct,
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
