#!/usr/bin/env python3
"""Benchmark repeated agent workflow prompt cost through Ollama."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "benchmarks" / "fixtures" / "codex_deepclean_workflow.json"
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "results"
DEFAULT_MANIFEST_DIR = ROOT / "benchmarks" / "prefix-manifests"
DEFAULT_OLLAMA_MODEL = "gemma4:12b"


class BenchmarkError(Exception):
    """Raised for expected benchmark failures."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure local Ollama prompt evaluation cost for repeated agent workflow prompts."
    )
    parser.add_argument("--model", default=DEFAULT_OLLAMA_MODEL, help="Ollama model name.")
    parser.add_argument("--host", default="http://localhost:11434", help="Ollama host URL.")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE, help="Workflow fixture JSON path.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for JSON results.")
    parser.add_argument("--manifest-dir", type=Path, default=DEFAULT_MANIFEST_DIR, help="Directory for prefix manifests.")
    parser.add_argument("--runs", type=int, default=1, help="Runs per scenario.")
    parser.add_argument("--num-predict", type=int, default=16, help="Generated tokens per run.")
    parser.add_argument("--prime-num-predict", type=int, default=1, help="Generated tokens for prefix priming.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Generation temperature.")
    parser.add_argument("--num-ctx", type=int, default=None, help="Optional Ollama context window.")
    parser.add_argument("--scenario", action="append", help="Run only the named scenario. Can be repeated.")
    parser.add_argument(
        "--strategy",
        choices=["full", "prefix-context", "compare", "restart-compare"],
        default="full",
        help="Benchmark strategy to run.",
    )
    parser.add_argument(
        "--write-prefix-manifest",
        action="store_true",
        help="Write a standalone prefix manifest JSON artifact.",
    )
    parser.add_argument(
        "--restart-delay",
        type=float,
        default=0.5,
        help="Seconds to wait after 'ollama stop <model>' during restart comparison.",
    )
    parser.add_argument(
        "--vary-runs",
        action="store_true",
        help="Append a benchmark-only marker so repeated samples do not become exact prompt replay.",
    )
    parser.add_argument("--timeout", type=float, default=300.0, help="HTTP timeout in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Build prompts and write metadata without calling Ollama.")
    return parser.parse_args()


def read_fixture(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            fixture = json.load(handle)
    except FileNotFoundError as exc:
        raise BenchmarkError(f"Fixture not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BenchmarkError(f"Fixture is not valid JSON: {path}: {exc}") from exc

    if not isinstance(fixture.get("blocks"), list) or not isinstance(fixture.get("scenarios"), list):
        raise BenchmarkError("Fixture must include 'blocks' and 'scenarios' arrays.")
    return fixture


def block_text(block: dict[str, Any]) -> str:
    if "text" in block:
        text = block["text"]
        if not isinstance(text, str):
            raise BenchmarkError(f"Block {block.get('name')} has non-string text.")
        return text
    lines = block.get("lines")
    if isinstance(lines, list) and all(isinstance(line, str) for line in lines):
        return "\n".join(lines)
    raise BenchmarkError(f"Block {block.get('name')} must include text or string lines.")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fixture_hash(fixture: dict[str, Any]) -> str:
    stable = json.dumps(fixture, sort_keys=True, separators=(",", ":"))
    return sha256_text(stable)


def index_blocks(fixture: dict[str, Any]) -> dict[str, dict[str, Any]]:
    blocks: dict[str, dict[str, Any]] = {}
    for block in fixture["blocks"]:
        name = block.get("name")
        if not isinstance(name, str) or not name:
            raise BenchmarkError("Each block must have a non-empty name.")
        if name in blocks:
            raise BenchmarkError(f"Duplicate block name: {name}")
        blocks[name] = block
    return blocks


def scenario_block_names(scenario: dict[str, Any]) -> list[str]:
    scenario_blocks = scenario.get("blocks")
    if not isinstance(scenario_blocks, list) or not all(isinstance(name, str) for name in scenario_blocks):
        raise BenchmarkError(f"Scenario {scenario.get('name')} must include a blocks array.")
    return scenario_blocks


def is_reusable_block(block: dict[str, Any]) -> bool:
    return block.get("tier") in {"stable", "semi-stable"}


def build_prompt_from_blocks(
    fixture: dict[str, Any],
    blocks_by_name: dict[str, dict[str, Any]],
    scenario_name: str,
    block_names: list[str],
    task: str | None,
    title: str,
    final_instruction: str,
) -> tuple[str, list[dict[str, Any]]]:
    prompt_parts = [
        title,
        "",
        f"Fixture: {fixture.get('name', 'unnamed')}",
        "",
    ]
    manifest = []
    for block_name in block_names:
        block = blocks_by_name.get(block_name)
        if block is None:
            raise BenchmarkError(f"Scenario {scenario_name} references missing block: {block_name}")
        text = block_text(block)
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
                "sha256": sha256_text(text),
            }
        )

    prompt_parts.extend(
        [
            "## Scenario",
            scenario_name,
            "",
        ]
    )
    if task is not None:
        prompt_parts.extend(
            [
                "## Current Task",
                task,
                "",
            ]
        )
    prompt_parts.append(final_instruction)
    return "\n".join(prompt_parts), manifest


def build_prompt(
    fixture: dict[str, Any],
    blocks_by_name: dict[str, dict[str, Any]],
    scenario: dict[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    task = scenario.get("task", "Return a compact JSON object with the next action.")
    if not isinstance(task, str):
        raise BenchmarkError(f"Scenario {scenario.get('name')} task must be a string.")
    return build_prompt_from_blocks(
        fixture=fixture,
        blocks_by_name=blocks_by_name,
        scenario_name=str(scenario.get("name", "unnamed")),
        block_names=scenario_block_names(scenario),
        task=task,
        title="# Local Agent Workflow Benchmark",
        final_instruction="Respond with only the compact JSON object.",
    )


def common_reusable_block_names(
    scenarios: list[dict[str, Any]],
    blocks_by_name: dict[str, dict[str, Any]],
) -> list[str]:
    common_names: set[str] | None = None
    for scenario in scenarios:
        reusable_names = set()
        for block_name in scenario_block_names(scenario):
            block = blocks_by_name.get(block_name)
            if block is None:
                raise BenchmarkError(f"Scenario {scenario.get('name')} references missing block: {block_name}")
            if is_reusable_block(block):
                reusable_names.add(block_name)
        common_names = reusable_names if common_names is None else common_names.intersection(reusable_names)

    if not common_names:
        raise BenchmarkError("Prefix-context comparison requires stable or semi-stable blocks shared by the selected scenarios.")

    ordered_names = [
        block_name
        for block_name in scenario_block_names(scenarios[0])
        if block_name in common_names and is_reusable_block(blocks_by_name[block_name])
    ]
    if not ordered_names:
        raise BenchmarkError("Prefix-context comparison found no ordered reusable prefix blocks.")
    return ordered_names


def build_reusable_prefix_prompt(
    fixture: dict[str, Any],
    blocks_by_name: dict[str, dict[str, Any]],
    prefix_block_names: list[str],
) -> tuple[str, list[dict[str, Any]]]:
    return build_prompt_from_blocks(
        fixture=fixture,
        blocks_by_name=blocks_by_name,
        scenario_name="reusable-prefix-prime",
        block_names=prefix_block_names,
        task="Prime the reusable workflow context for later changed-tail tasks.",
        title="# Reusable Agent Workflow Prefix",
        final_instruction="Respond with only OK.",
    )


def build_tail_prompt(
    fixture: dict[str, Any],
    blocks_by_name: dict[str, dict[str, Any]],
    scenario: dict[str, Any],
    prefix_block_names: list[str],
) -> tuple[str, list[dict[str, Any]]]:
    prefix_set = set(prefix_block_names)
    tail_block_names = [block_name for block_name in scenario_block_names(scenario) if block_name not in prefix_set]
    task = scenario.get("task", "Return a compact JSON object with the next action.")
    if not isinstance(task, str):
        raise BenchmarkError(f"Scenario {scenario.get('name')} task must be a string.")
    return build_prompt_from_blocks(
        fixture=fixture,
        blocks_by_name=blocks_by_name,
        scenario_name=str(scenario.get("name", "unnamed")),
        block_names=tail_block_names,
        task=task,
        title="# Changed Tail For Primed Agent Workflow",
        final_instruction="Use the prior reusable workflow context. Respond with only the compact JSON object.",
    )


def build_prefix_manifest(
    args: argparse.Namespace,
    fixture: dict[str, Any],
    blocks_by_name: dict[str, dict[str, Any]],
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    prefix_block_names = common_reusable_block_names(scenarios, blocks_by_name)
    prefix_prompt, prefix_manifest = build_reusable_prefix_prompt(fixture, blocks_by_name, prefix_block_names)
    scenario_tails = []
    for scenario in scenarios:
        tail_prompt, tail_manifest = build_tail_prompt(fixture, blocks_by_name, scenario, prefix_block_names)
        full_prompt, full_manifest = build_prompt(fixture, blocks_by_name, scenario)
        scenario_tails.append(
            {
                "name": scenario.get("name", "unnamed"),
                "description": scenario.get("description"),
                "tail_prompt_bytes": len(tail_prompt.encode("utf-8")),
                "tail_prompt_sha256": sha256_text(tail_prompt),
                "tail_blocks": tail_manifest,
                "full_prompt_bytes": len(full_prompt.encode("utf-8")),
                "full_prompt_sha256": sha256_text(full_prompt),
                "full_blocks": full_manifest,
            }
        )

    cache_key_material = {
        "model": args.model,
        "fixture_hash": fixture_hash(fixture),
        "prefix_prompt_sha256": sha256_text(prefix_prompt),
        "prefix_block_hashes": [block["sha256"] for block in prefix_manifest],
        "num_ctx": args.num_ctx,
        "prompt_layout": "stable blocks before scenario metadata and volatile task",
    }
    return {
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "manifest_version": 1,
        "model": args.model,
        "fixture_path": str(args.fixture),
        "fixture_hash": fixture_hash(fixture),
        "selected_scenarios": [scenario.get("name", "unnamed") for scenario in scenarios],
        "prefix_block_names": prefix_block_names,
        "prefix_prompt_bytes": len(prefix_prompt.encode("utf-8")),
        "prefix_prompt_sha256": sha256_text(prefix_prompt),
        "prefix_blocks": prefix_manifest,
        "scenario_tails": scenario_tails,
        "cache_key_material": cache_key_material,
        "cache_key_sha256": sha256_text(json.dumps(cache_key_material, sort_keys=True, separators=(",", ":"))),
        "note": "Metadata scaffold only. This does not persist KV tensors.",
    }


def selected_scenarios(fixture: dict[str, Any], requested: list[str] | None) -> list[dict[str, Any]]:
    scenarios = fixture["scenarios"]
    if not requested:
        return scenarios
    requested_set = set(requested)
    matches = [scenario for scenario in scenarios if scenario.get("name") in requested_set]
    missing = requested_set.difference(str(scenario.get("name")) for scenario in matches)
    if missing:
        raise BenchmarkError(f"Unknown scenario(s): {', '.join(sorted(missing))}")
    return matches


def call_ollama(
    host: str,
    model: str,
    prompt: str,
    num_predict: int,
    temperature: float,
    num_ctx: int | None,
    timeout: float,
    context: list[int] | None = None,
) -> dict[str, Any]:
    options: dict[str, Any] = {
        "num_predict": num_predict,
        "temperature": temperature,
    }
    if num_ctx is not None:
        options["num_ctx"] = num_ctx

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": options,
    }
    if context is not None:
        payload["context"] = context
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        host.rstrip("/") + "/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise BenchmarkError(
            "Could not reach Ollama. Start it with 'ollama serve' or set --host to the running Ollama API."
        ) from exc
    except TimeoutError as exc:
        raise BenchmarkError(f"Ollama request timed out after {timeout}s.") from exc

    try:
        result = json.loads(body)
    except json.JSONDecodeError as exc:
        raise BenchmarkError(f"Ollama returned non-JSON response: {body[:200]}") from exc

    if "error" in result:
        raise BenchmarkError(f"Ollama error: {result['error']}")
    return result


def ns_to_ms(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return value / 1_000_000
    return None


def tokens_per_second(count: Any, duration_ns: Any) -> float | None:
    if not isinstance(count, (int, float)) or not isinstance(duration_ns, (int, float)) or duration_ns <= 0:
        return None
    return count / duration_ns * 1_000_000_000


def summarize_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    def values(field: str) -> list[float]:
        return [float(run[field]) for run in runs if isinstance(run.get(field), (int, float))]

    summary: dict[str, Any] = {"run_count": len(runs)}
    for field in [
        "total_duration",
        "load_duration",
        "prompt_eval_duration",
        "eval_duration",
        "prompt_eval_count",
        "eval_count",
    ]:
        field_values = values(field)
        if field_values:
            summary[field + "_mean"] = statistics.mean(field_values)
            summary[field + "_min"] = min(field_values)
            summary[field + "_max"] = max(field_values)
    return summary


def format_ms(value: Any) -> str:
    ms = ns_to_ms(value)
    return "n/a" if ms is None else f"{ms:,.1f} ms"


def format_tps(value: float | None) -> str:
    return "n/a" if value is None else f"{value:,.1f} tok/s"


def prompt_for_run(prompt: str, run_index: int, vary_runs: bool) -> str:
    if not vary_runs:
        return prompt
    return (
        prompt
        + "\n\n## Benchmark Run Marker\n"
        + f"This marker prevents exact prompt replay in repeated samples. Run: {run_index}."
    )


def make_run_record(run_index: int, wall_duration: float, ollama_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_index": run_index,
        "wall_duration_ms": wall_duration * 1000,
        "total_duration": ollama_result.get("total_duration"),
        "load_duration": ollama_result.get("load_duration"),
        "prompt_eval_count": ollama_result.get("prompt_eval_count"),
        "prompt_eval_duration": ollama_result.get("prompt_eval_duration"),
        "eval_count": ollama_result.get("eval_count"),
        "eval_duration": ollama_result.get("eval_duration"),
        "prompt_eval_tokens_per_second": tokens_per_second(
            ollama_result.get("prompt_eval_count"),
            ollama_result.get("prompt_eval_duration"),
        ),
        "eval_tokens_per_second": tokens_per_second(
            ollama_result.get("eval_count"),
            ollama_result.get("eval_duration"),
        ),
        "response_excerpt": str(ollama_result.get("response", ""))[:400],
        "context_length": len(ollama_result.get("context", [])) if isinstance(ollama_result.get("context"), list) else None,
    }


def print_run(prefix: str, run: dict[str, Any]) -> None:
    print(
        "{prefix}run {run}: total={total}, load={load}, prompt_eval={prompt_eval}, "
        "prompt_tokens={prompt_tokens}, prompt_tps={prompt_tps}".format(
            prefix=prefix,
            run=run["run_index"],
            total=format_ms(run["total_duration"]),
            load=format_ms(run["load_duration"]),
            prompt_eval=format_ms(run["prompt_eval_duration"]),
            prompt_tokens=run["prompt_eval_count"] or "n/a",
            prompt_tps=format_tps(run["prompt_eval_tokens_per_second"]),
        )
    )


def duration_sum(runs: list[dict[str, Any]], field: str) -> int | float | None:
    values = [run.get(field) for run in runs]
    numeric = [value for value in values if isinstance(value, (int, float))]
    if not numeric:
        return None
    return sum(numeric)


def summarize_strategy(strategy: dict[str, Any]) -> dict[str, Any]:
    if strategy["name"] == "full":
        runs = [run for scenario in strategy["scenarios"] for run in scenario["runs"]]
        return {
            "run_count": len(runs),
            "prompt_eval_duration_sum": duration_sum(runs, "prompt_eval_duration"),
            "total_duration_sum": duration_sum(runs, "total_duration"),
            "load_duration_sum": duration_sum(runs, "load_duration"),
        }

    if strategy["name"] == "prefix-context":
        tail_runs = [run for scenario in strategy["scenarios"] for run in scenario["runs"]]
        prime_run = strategy.get("prime", {}).get("run", {})
        prime_prompt_eval = prime_run.get("prompt_eval_duration")
        tail_prompt_eval = duration_sum(tail_runs, "prompt_eval_duration")
        prompt_eval_total = None
        if isinstance(prime_prompt_eval, (int, float)) and isinstance(tail_prompt_eval, (int, float)):
            prompt_eval_total = prime_prompt_eval + tail_prompt_eval
        tail_call_count = len(tail_runs)
        amortized_prompt_eval = None
        if isinstance(prompt_eval_total, (int, float)) and tail_call_count:
            amortized_prompt_eval = prompt_eval_total / tail_call_count
        return {
            "tail_run_count": tail_call_count,
            "prime_prompt_eval_duration": prime_prompt_eval,
            "tail_prompt_eval_duration_sum": tail_prompt_eval,
            "prompt_eval_duration_sum": prompt_eval_total,
            "amortized_prompt_eval_duration": amortized_prompt_eval,
            "proxy_note": "Ollama generate context reuse is deprecated API behavior and is not persistent SSD-backed KV cache.",
        }

    return {}


def summarize_comparison(strategies: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {strategy["name"]: strategy for strategy in strategies}
    full = by_name.get("full")
    prefix = by_name.get("prefix-context")
    if full is None or prefix is None:
        return {}

    full_prompt_eval = full.get("summary", {}).get("prompt_eval_duration_sum")
    prefix_prompt_eval = prefix.get("summary", {}).get("prompt_eval_duration_sum")
    delta = None
    delta_ratio = None
    if isinstance(full_prompt_eval, (int, float)) and isinstance(prefix_prompt_eval, (int, float)):
        delta = full_prompt_eval - prefix_prompt_eval
        if full_prompt_eval:
            delta_ratio = delta / full_prompt_eval
    return {
        "baseline_prompt_eval_duration": full_prompt_eval,
        "prefix_context_prompt_eval_duration": prefix_prompt_eval,
        "baseline_minus_prefix_context_prompt_eval_duration": delta,
        "baseline_minus_prefix_context_prompt_eval_ratio": delta_ratio,
        "interpretation": "Positive delta means prefix-context was faster for prompt eval; negative delta means it was slower.",
    }


def summarize_sequence(sequence: dict[str, Any]) -> dict[str, Any]:
    runs = [run for scenario in sequence["scenarios"] for run in scenario["runs"]]
    first_run = runs[0] if runs else {}
    remaining_runs = runs[1:]
    return {
        "run_count": len(runs),
        "prompt_eval_duration_sum": duration_sum(runs, "prompt_eval_duration"),
        "total_duration_sum": duration_sum(runs, "total_duration"),
        "load_duration_sum": duration_sum(runs, "load_duration"),
        "first_prompt_eval_duration": first_run.get("prompt_eval_duration"),
        "remaining_prompt_eval_duration_sum": duration_sum(remaining_runs, "prompt_eval_duration"),
    }


def summarize_restart_comparison(strategy: dict[str, Any]) -> dict[str, Any]:
    sequences = {sequence["name"]: sequence for sequence in strategy.get("sequences", [])}
    warm = sequences.get("warm-sequence", {}).get("summary", {})
    restarted = sequences.get("restarted-sequence", {}).get("summary", {})
    warm_prompt_eval = warm.get("prompt_eval_duration_sum")
    restarted_prompt_eval = restarted.get("prompt_eval_duration_sum")
    delta = None
    ratio = None
    if isinstance(warm_prompt_eval, (int, float)) and isinstance(restarted_prompt_eval, (int, float)):
        delta = restarted_prompt_eval - warm_prompt_eval
        if warm_prompt_eval:
            ratio = delta / warm_prompt_eval
    return {
        "warm_prompt_eval_duration": warm_prompt_eval,
        "restarted_prompt_eval_duration": restarted_prompt_eval,
        "restarted_minus_warm_prompt_eval_duration": delta,
        "restarted_minus_warm_prompt_eval_ratio": ratio,
        "interpretation": "Positive delta means restarts remove warm-prefix benefit and create a persistence gap.",
    }


def clean_output_excerpt(value: str, limit: int = 500) -> str:
    printable = "".join(ch for ch in value if ch.isprintable() or ch in "\n\t")
    return printable.strip()[:limit]


def stop_ollama_model(model: str, reason: str, delay: float, dry_run: bool) -> dict[str, Any]:
    started = time.perf_counter()
    record: dict[str, Any] = {
        "model": model,
        "reason": reason,
        "command": ["ollama", "stop", model],
        "dry_run": dry_run,
    }
    if dry_run:
        record["elapsed_ms"] = 0.0
        return record
    try:
        completed = subprocess.run(
            ["ollama", "stop", model],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError as exc:
        raise BenchmarkError("Could not find the 'ollama' command needed for restart comparison.") from exc
    except subprocess.TimeoutExpired as exc:
        raise BenchmarkError("Timed out while running 'ollama stop'.") from exc

    record.update(
        {
            "returncode": completed.returncode,
            "stdout": clean_output_excerpt(completed.stdout),
            "stderr": clean_output_excerpt(completed.stderr),
            "elapsed_ms": (time.perf_counter() - started) * 1000,
        }
    )
    if completed.returncode != 0:
        raise BenchmarkError(f"'ollama stop {model}' failed with exit code {completed.returncode}.")
    if delay > 0:
        time.sleep(delay)
    return record


def run_full_strategy(
    args: argparse.Namespace,
    fixture: dict[str, Any],
    blocks_by_name: dict[str, dict[str, Any]],
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    strategy: dict[str, Any] = {"name": "full", "description": "Full prompt per scenario.", "scenarios": []}

    print("Strategy: full")
    for scenario in scenarios:
        scenario_name = str(scenario.get("name", "unnamed"))
        prompt, manifest = build_prompt(fixture, blocks_by_name, scenario)
        prompt_bytes = len(prompt.encode("utf-8"))
        reusable_bytes = sum(
            block["bytes"] for block in manifest if block.get("tier") in {"stable", "semi-stable"}
        )
        scenario_result: dict[str, Any] = {
            "name": scenario_name,
            "description": scenario.get("description"),
            "prompt_bytes": prompt_bytes,
            "reusable_prefix_bytes": reusable_bytes,
            "prompt_sha256": sha256_text(prompt),
            "block_manifest": manifest,
            "runs": [],
        }

        print(f"  Scenario: {scenario_name}")
        print(f"    prompt bytes: {prompt_bytes:,}")
        print(f"    stable/semi-stable bytes: {reusable_bytes:,}")

        for run_index in range(1, args.runs + 1):
            wall_start = time.perf_counter()
            if args.dry_run:
                ollama_result: dict[str, Any] = {}
            else:
                ollama_result = call_ollama(
                    host=args.host,
                    model=args.model,
                    prompt=prompt_for_run(prompt, run_index, args.vary_runs),
                    num_predict=args.num_predict,
                    temperature=args.temperature,
                    num_ctx=args.num_ctx,
                    timeout=args.timeout,
                )
            wall_duration = time.perf_counter() - wall_start
            run = make_run_record(run_index, wall_duration, ollama_result)
            scenario_result["runs"].append(run)
            print_run("    ", run)

        scenario_result["summary"] = summarize_runs(scenario_result["runs"])
        strategy["scenarios"].append(scenario_result)
        print()

    strategy["summary"] = summarize_strategy(strategy)
    return strategy


def run_full_sequence(
    args: argparse.Namespace,
    fixture: dict[str, Any],
    blocks_by_name: dict[str, dict[str, Any]],
    scenarios: list[dict[str, Any]],
    sequence_name: str,
    stop_before_sequence: bool,
    stop_before_each_call: bool,
) -> dict[str, Any]:
    sequence: dict[str, Any] = {
        "name": sequence_name,
        "stop_before_sequence": stop_before_sequence,
        "stop_before_each_call": stop_before_each_call,
        "restart_actions": [],
        "scenarios": [],
    }
    print(f"  Sequence: {sequence_name}")
    if stop_before_sequence:
        action = stop_ollama_model(args.model, f"{sequence_name}:before-sequence", args.restart_delay, args.dry_run)
        sequence["restart_actions"].append(action)
        print(f"    stopped model before sequence: {args.model}")

    for scenario in scenarios:
        scenario_name = str(scenario.get("name", "unnamed"))
        prompt, manifest = build_prompt(fixture, blocks_by_name, scenario)
        scenario_result: dict[str, Any] = {
            "name": scenario_name,
            "description": scenario.get("description"),
            "prompt_bytes": len(prompt.encode("utf-8")),
            "prompt_sha256": sha256_text(prompt),
            "block_manifest": manifest,
            "runs": [],
        }
        print(f"    Scenario: {scenario_name}")

        for run_index in range(1, args.runs + 1):
            if stop_before_each_call:
                action = stop_ollama_model(
                    args.model,
                    f"{sequence_name}:{scenario_name}:run-{run_index}",
                    args.restart_delay,
                    args.dry_run,
                )
                sequence["restart_actions"].append(action)
                print(f"      stopped model before run {run_index}: {args.model}")

            wall_start = time.perf_counter()
            if args.dry_run:
                ollama_result: dict[str, Any] = {}
            else:
                ollama_result = call_ollama(
                    host=args.host,
                    model=args.model,
                    prompt=prompt_for_run(prompt, run_index, args.vary_runs),
                    num_predict=args.num_predict,
                    temperature=args.temperature,
                    num_ctx=args.num_ctx,
                    timeout=args.timeout,
                )
            wall_duration = time.perf_counter() - wall_start
            run = make_run_record(run_index, wall_duration, ollama_result)
            scenario_result["runs"].append(run)
            print_run("      ", run)

        scenario_result["summary"] = summarize_runs(scenario_result["runs"])
        sequence["scenarios"].append(scenario_result)
        print()

    sequence["summary"] = summarize_sequence(sequence)
    return sequence


def run_restart_compare_strategy(
    args: argparse.Namespace,
    fixture: dict[str, Any],
    blocks_by_name: dict[str, dict[str, Any]],
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    strategy: dict[str, Any] = {
        "name": "restart-compare",
        "description": "Compare warm aligned full-prompt sequence against stopping Ollama before each prompt.",
        "sequences": [],
    }
    print("Strategy: restart-compare")
    warm = run_full_sequence(
        args=args,
        fixture=fixture,
        blocks_by_name=blocks_by_name,
        scenarios=scenarios,
        sequence_name="warm-sequence",
        stop_before_sequence=True,
        stop_before_each_call=False,
    )
    strategy["sequences"].append(warm)

    restarted = run_full_sequence(
        args=args,
        fixture=fixture,
        blocks_by_name=blocks_by_name,
        scenarios=scenarios,
        sequence_name="restarted-sequence",
        stop_before_sequence=False,
        stop_before_each_call=True,
    )
    strategy["sequences"].append(restarted)
    strategy["summary"] = summarize_restart_comparison(strategy)
    return strategy


def run_prefix_context_strategy(
    args: argparse.Namespace,
    fixture: dict[str, Any],
    blocks_by_name: dict[str, dict[str, Any]],
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    prefix_block_names = common_reusable_block_names(scenarios, blocks_by_name)
    prefix_prompt, prefix_manifest = build_reusable_prefix_prompt(fixture, blocks_by_name, prefix_block_names)
    prefix_bytes = len(prefix_prompt.encode("utf-8"))
    strategy: dict[str, Any] = {
        "name": "prefix-context",
        "description": "Prime common reusable blocks once, then run changed tails with Ollama context.",
        "proxy_note": "Ollama generate context reuse is deprecated API behavior and is not persistent SSD-backed KV cache.",
        "prefix_block_names": prefix_block_names,
        "prefix_prompt_bytes": prefix_bytes,
        "prefix_prompt_sha256": sha256_text(prefix_prompt),
        "prefix_block_manifest": prefix_manifest,
        "prime": {},
        "scenarios": [],
    }

    print("Strategy: prefix-context")
    print(f"  prefix blocks: {', '.join(prefix_block_names)}")
    print(f"  prefix prompt bytes: {prefix_bytes:,}")

    wall_start = time.perf_counter()
    if args.dry_run:
        prime_result: dict[str, Any] = {}
        prime_context: list[int] | None = None
    else:
        prime_result = call_ollama(
            host=args.host,
            model=args.model,
            prompt=prefix_prompt,
            num_predict=args.prime_num_predict,
            temperature=args.temperature,
            num_ctx=args.num_ctx,
            timeout=args.timeout,
        )
        context_value = prime_result.get("context")
        if not isinstance(context_value, list):
            raise BenchmarkError("Ollama did not return a context array for prefix-context strategy.")
        prime_context = context_value
    wall_duration = time.perf_counter() - wall_start
    prime_run = make_run_record(1, wall_duration, prime_result)
    strategy["prime"] = {
        "prompt_bytes": prefix_bytes,
        "run": prime_run,
    }
    print_run("  prime ", prime_run)

    for scenario in scenarios:
        scenario_name = str(scenario.get("name", "unnamed"))
        tail_prompt, manifest = build_tail_prompt(fixture, blocks_by_name, scenario, prefix_block_names)
        tail_bytes = len(tail_prompt.encode("utf-8"))
        scenario_result = {
            "name": scenario_name,
            "description": scenario.get("description"),
            "tail_prompt_bytes": tail_bytes,
            "tail_prompt_sha256": sha256_text(tail_prompt),
            "tail_block_manifest": manifest,
            "runs": [],
        }
        print(f"  Scenario: {scenario_name}")
        print(f"    tail prompt bytes: {tail_bytes:,}")

        for run_index in range(1, args.runs + 1):
            wall_start = time.perf_counter()
            if args.dry_run:
                ollama_result = {}
            else:
                ollama_result = call_ollama(
                    host=args.host,
                    model=args.model,
                    prompt=prompt_for_run(tail_prompt, run_index, args.vary_runs),
                    num_predict=args.num_predict,
                    temperature=args.temperature,
                    num_ctx=args.num_ctx,
                    timeout=args.timeout,
                    context=prime_context,
                )
            wall_duration = time.perf_counter() - wall_start
            run = make_run_record(run_index, wall_duration, ollama_result)
            scenario_result["runs"].append(run)
            print_run("    ", run)

        scenario_result["summary"] = summarize_runs(scenario_result["runs"])
        strategy["scenarios"].append(scenario_result)
        print()

    strategy["summary"] = summarize_strategy(strategy)
    return strategy


def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    fixture = read_fixture(args.fixture)
    blocks_by_name = index_blocks(fixture)
    scenarios = selected_scenarios(fixture, args.scenario)
    if args.runs < 1:
        raise BenchmarkError("--runs must be at least 1.")
    if args.num_predict < 1:
        raise BenchmarkError("--num-predict must be at least 1.")
    if args.prime_num_predict < 1:
        raise BenchmarkError("--prime-num-predict must be at least 1.")

    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    result: dict[str, Any] = {
        "metadata": {
            "started_at": started_at,
            "model": args.model,
            "host": args.host,
            "fixture_path": str(args.fixture),
            "fixture_hash": fixture_hash(fixture),
            "runs_per_scenario": args.runs,
            "num_predict": args.num_predict,
            "prime_num_predict": args.prime_num_predict,
            "temperature": args.temperature,
            "num_ctx": args.num_ctx,
            "dry_run": args.dry_run,
            "strategy": args.strategy,
            "vary_runs": args.vary_runs,
            "restart_delay": args.restart_delay,
            "proxy_context_source": "Ollama /api/generate context parameter; official docs mark it deprecated.",
        },
        "prefix_manifest": build_prefix_manifest(args, fixture, blocks_by_name, scenarios),
        "strategies": [],
    }

    print(f"Benchmark fixture: {fixture.get('name', args.fixture.name)}")
    print(f"Model: {args.model}")
    print(f"Strategy: {args.strategy}")
    print(f"Runs per scenario: {args.runs}")
    print(f"Dry run: {args.dry_run}")
    print()

    if args.strategy in {"full", "compare"}:
        full_strategy = run_full_strategy(args, fixture, blocks_by_name, scenarios)
        result["strategies"].append(full_strategy)
        result["scenarios"] = full_strategy["scenarios"]

    if args.strategy in {"prefix-context", "compare"}:
        prefix_strategy = run_prefix_context_strategy(args, fixture, blocks_by_name, scenarios)
        result["strategies"].append(prefix_strategy)

    if args.strategy == "restart-compare":
        restart_strategy = run_restart_compare_strategy(args, fixture, blocks_by_name, scenarios)
        result["strategies"].append(restart_strategy)
        result["restart_comparison"] = restart_strategy["summary"]

    result["comparison"] = summarize_comparison(result["strategies"])
    if result["comparison"]:
        delta = result["comparison"].get("baseline_minus_prefix_context_prompt_eval_duration")
        ratio = result["comparison"].get("baseline_minus_prefix_context_prompt_eval_ratio")
        print("Comparison:")
        print(f"  baseline prompt eval sum: {format_ms(result['comparison'].get('baseline_prompt_eval_duration'))}")
        print(f"  prefix-context prompt eval sum: {format_ms(result['comparison'].get('prefix_context_prompt_eval_duration'))}")
        print(f"  baseline minus prefix-context: {format_ms(delta)}")
        if isinstance(ratio, (int, float)):
            print(f"  ratio: {ratio:.3f}")

    if result.get("restart_comparison"):
        delta = result["restart_comparison"].get("restarted_minus_warm_prompt_eval_duration")
        ratio = result["restart_comparison"].get("restarted_minus_warm_prompt_eval_ratio")
        print("Restart comparison:")
        print(f"  warm prompt eval sum: {format_ms(result['restart_comparison'].get('warm_prompt_eval_duration'))}")
        print(f"  restarted prompt eval sum: {format_ms(result['restart_comparison'].get('restarted_prompt_eval_duration'))}")
        print(f"  restarted minus warm: {format_ms(delta)}")
        if isinstance(ratio, (int, float)):
            print(f"  ratio: {ratio:.3f}")

    result["metadata"]["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    return result


def write_result(result: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_slug = str(result["metadata"]["model"]).replace(":", "-").replace("/", "-")
    fixture_slug = Path(str(result["metadata"]["fixture_path"])).stem
    path = output_dir / f"{timestamp}-{model_slug}-{fixture_slug}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    return path


def write_prefix_manifest(result: dict[str, Any], manifest_dir: Path) -> Path:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_slug = str(result["metadata"]["model"]).replace(":", "-").replace("/", "-")
    fixture_slug = Path(str(result["metadata"]["fixture_path"])).stem
    path = manifest_dir / f"{timestamp}-{model_slug}-{fixture_slug}-prefix-manifest.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result["prefix_manifest"], handle, indent=2)
        handle.write("\n")
    return path


def main() -> int:
    args = parse_args()
    try:
        result = run_benchmark(args)
        manifest_path = write_prefix_manifest(result, args.manifest_dir) if args.write_prefix_manifest else None
        output_path = write_result(result, args.output_dir)
    except BenchmarkError as exc:
        print(f"benchmark error: {exc}", file=sys.stderr)
        return 2

    if manifest_path is not None:
        print(f"Prefix manifest JSON: {manifest_path}")
    print(f"Result JSON: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
