#!/usr/bin/env python3
"""Benchmark repeated agent workflow prompts through Codex frontier models."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from ollama_workflow_benchmark import (
    DEFAULT_FIXTURE,
    BenchmarkError,
    build_prompt,
    fixture_hash,
    index_blocks,
    read_fixture,
    selected_scenarios,
    sha256_text,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "results"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure Codex frontier model token usage for repeated agent workflow prompts."
    )
    parser.add_argument("--model", default="gpt-5.5", help="Codex model name.")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE, help="Workflow fixture JSON path.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for JSON results.")
    parser.add_argument("--runs", type=int, default=1, help="Runs per scenario.")
    parser.add_argument("--scenario", action="append", help="Run only the named scenario. Can be repeated.")
    parser.add_argument(
        "--reasoning-effort",
        default="xhigh",
        help="Codex model_reasoning_effort config value. Use 'none' to omit the override.",
    )
    parser.add_argument(
        "--sandbox",
        default="read-only",
        choices=["read-only", "workspace-write", "danger-full-access"],
        help="Codex sandbox mode.",
    )
    parser.add_argument("--timeout", type=float, default=600.0, help="Codex process timeout in seconds.")
    parser.add_argument(
        "--persist-session",
        action="store_true",
        help="Do not pass --ephemeral. Off by default so benchmark sessions do not pollute history.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build prompts and write metadata without calling Codex.",
    )
    return parser.parse_args()


def make_codex_prompt(prompt: str, scenario_name: str, run_index: int) -> str:
    return "\n".join(
        [
            "Offline benchmark task. Do not inspect files, run tools, edit files, or ask questions.",
            "Use only the benchmark fixture content below.",
            "Return only a compact JSON object with keys: action, reason, next_command, cache_boundary_note, quality_risk.",
            f"Scenario: {scenario_name}",
            f"Run: {run_index}",
            "",
            prompt,
        ]
    )


def parse_jsonl(stdout: str) -> tuple[list[dict[str, Any]], dict[str, Any], str | None]:
    events: list[dict[str, Any]] = []
    usage: dict[str, Any] = {}
    final_message: str | None = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            events.append({"type": "unparsed", "text": line[:500]})
            continue
        events.append(event)
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
        item = event.get("item")
        if event.get("type") == "item.completed" and isinstance(item, dict) and item.get("type") == "agent_message":
            final_message = str(item.get("text", ""))
    return events, usage, final_message


def call_codex(args: argparse.Namespace, prompt: str) -> dict[str, Any]:
    command = [
        "codex",
        "exec",
        "--json",
        "-m",
        args.model,
        "-s",
        args.sandbox,
    ]
    if not args.persist_session:
        command.append("--ephemeral")
    if args.reasoning_effort != "none":
        command.extend(["-c", f"model_reasoning_effort={json.dumps(args.reasoning_effort)}"])
    command.append("-")

    started = time.perf_counter()
    completed = subprocess.run(
        command,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=args.timeout,
        check=False,
    )
    wall_ms = (time.perf_counter() - started) * 1000
    events, usage, final_message = parse_jsonl(completed.stdout)
    return {
        "command": command[:-1] + ["<stdin>"],
        "returncode": completed.returncode,
        "wall_duration_ms": wall_ms,
        "stdout_events": events,
        "stderr_excerpt": completed.stderr.strip()[:1000],
        "usage": usage,
        "final_message": final_message,
    }


def numeric_usage(records: list[dict[str, Any]], field: str) -> list[int]:
    values = []
    for record in records:
        value = record.get("usage", {}).get(field)
        if isinstance(value, int):
            values.append(value)
    return values


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"run_count": len(records)}
    wall_values = [float(record["wall_duration_ms"]) for record in records if isinstance(record.get("wall_duration_ms"), (int, float))]
    if wall_values:
        summary["wall_duration_ms_mean"] = statistics.mean(wall_values)
        summary["wall_duration_ms_sum"] = sum(wall_values)
    for field in ["input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"]:
        values = numeric_usage(records, field)
        if values:
            summary[field + "_sum"] = sum(values)
            summary[field + "_mean"] = statistics.mean(values)
    input_sum = summary.get("input_tokens_sum")
    cached_sum = summary.get("cached_input_tokens_sum", 0)
    if isinstance(input_sum, int) and isinstance(cached_sum, int):
        summary["uncached_input_tokens_sum"] = input_sum - cached_sum
        summary["cached_input_ratio"] = cached_sum / input_sum if input_sum else None
    return summary


def main() -> int:
    args = parse_args()
    if args.runs < 1:
        raise BenchmarkError("--runs must be at least 1.")

    fixture = read_fixture(args.fixture)
    blocks_by_name = index_blocks(fixture)
    scenarios = selected_scenarios(fixture, args.scenario)
    result: dict[str, Any] = {
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "benchmark": "codex-frontier-workflow",
        "model": args.model,
        "reasoning_effort": None if args.reasoning_effort == "none" else args.reasoning_effort,
        "sandbox": args.sandbox,
        "fixture_path": str(args.fixture),
        "fixture_hash": fixture_hash(fixture),
        "fixture_name": fixture.get("name"),
        "dry_run": args.dry_run,
        "notes": [
            "Codex CLI usage is agent-runtime usage, not raw Chat Completions API usage.",
            "input_tokens includes Codex harness, user/project instructions, and benchmark prompt.",
            "Codex CLI does not expose a per-run dollar cost in this result.",
        ],
        "scenarios": [],
    }

    all_records: list[dict[str, Any]] = []
    for scenario in scenarios:
        scenario_name = str(scenario.get("name", "unnamed"))
        prompt, manifest = build_prompt(fixture, blocks_by_name, scenario)
        scenario_result: dict[str, Any] = {
            "name": scenario_name,
            "description": scenario.get("description"),
            "prompt_bytes": len(prompt.encode("utf-8")),
            "prompt_sha256": sha256_text(prompt),
            "blocks": manifest,
            "runs": [],
        }
        for run_index in range(1, args.runs + 1):
            codex_prompt = make_codex_prompt(prompt, scenario_name, run_index)
            if args.dry_run:
                record = {
                    "run_index": run_index,
                    "codex_prompt_bytes": len(codex_prompt.encode("utf-8")),
                    "codex_prompt_sha256": sha256_text(codex_prompt),
                    "wall_duration_ms": 0.0,
                    "usage": {},
                    "final_message": None,
                    "returncode": None,
                }
            else:
                record = call_codex(args, codex_prompt)
                record["run_index"] = run_index
                record["codex_prompt_bytes"] = len(codex_prompt.encode("utf-8"))
                record["codex_prompt_sha256"] = sha256_text(codex_prompt)
                if record["returncode"] != 0:
                    raise BenchmarkError(
                        f"Codex failed for {scenario_name} run {run_index} with exit code {record['returncode']}: "
                        f"{record.get('stderr_excerpt', '')}"
                    )
            scenario_result["runs"].append(record)
            all_records.append(record)
            usage = record.get("usage", {})
            print(
                f"{scenario_name} run {run_index}: wall={record['wall_duration_ms']:,.1f} ms "
                f"input={usage.get('input_tokens', 'n/a')} cached={usage.get('cached_input_tokens', 'n/a')} "
                f"output={usage.get('output_tokens', 'n/a')}"
            )
        scenario_result["summary"] = summarize_records(scenario_result["runs"])
        result["scenarios"].append(scenario_result)

    result["summary"] = summarize_records(all_records)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fixture_stem = args.fixture.stem.replace("_", "-")
    model_slug = args.model.replace(":", "-").replace("/", "-")
    output_path = args.output_dir / f"{timestamp}-{model_slug}-{fixture_stem}-codex-frontier.json"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BenchmarkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
