#!/usr/bin/env python3
"""Generate size-targeted large-prefix workflow fixtures."""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import llama_cpp_prompt_cache_benchmark as lcb  # noqa: E402
import ollama_workflow_benchmark as owb  # noqa: E402


DEFAULT_SOURCE = ROOT / "benchmarks" / "fixtures" / "printtestbot_printing_press_workflow.json"
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "fixtures"
DEFAULT_TARGETS = [16 * 1024, 32 * 1024, 64 * 1024]
CTX_BUCKETS = [4096, 8192, 16384, 32768, 65536]
APPROX_BYTES_PER_TOKEN = 3.5
CONTEXT_HEADROOM_RATIO = 1.25
CONTEXT_HEADROOM_TOKENS = 512

SAFE_CONTEXT_FILES = [
    "AGENTS.md",
    "MISSION.md",
    "README.md",
    "GLOSSARY.md",
    "RESOURCES.md",
    "benchmarks/README.md",
    "benchmarks/datasets/printtestbot-printing-press-2026-06-02/README.md",
    "openspec/specs/ollama-workflow-benchmark/spec.md",
    "openspec/specs/llama-cpp-prompt-cache-benchmark/spec.md",
    "openspec/specs/llama-cpp-agent-cache-wrapper/spec.md",
    "openspec/specs/benchmark-result-summary/spec.md",
    "openspec/specs/prefix-block-store/spec.md",
    "openspec/specs/research-positioning-doc/spec.md",
]

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"\bbot\d{4,}:[A-Za-z0-9_-]{20,}\b"),
    re.compile(r'"chat_id"\s*:\s*-?\d{5,}'),
    re.compile(r"\b[A-Za-z0-9+/]{80,}={0,2}\b"),
]


class FixtureGenerationError(Exception):
    """Raised for expected fixture generation failures."""


@dataclass
class FixtureMetrics:
    prefix_block_names: list[str]
    prefix_prompt_bytes: int
    largest_prompt_bytes: int
    estimated_largest_prompt_tokens: int
    recommended_ctx_size: int


@dataclass
class GeneratedFixture:
    target_prefix_bytes: int
    path: Path
    fixture: dict[str, Any]
    metrics: FixtureMetrics
    safety_status: str


def parse_size(value: str) -> int:
    normalized = value.strip().lower()
    multiplier = 1
    if normalized.endswith("kb"):
        multiplier = 1024
        normalized = normalized[:-2]
    elif normalized.endswith("k"):
        multiplier = 1024
        normalized = normalized[:-1]
    elif normalized.endswith("mb"):
        multiplier = 1024 * 1024
        normalized = normalized[:-2]
    try:
        amount = float(normalized)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid size: {value}") from exc
    if amount <= 0:
        raise argparse.ArgumentTypeError("size must be positive")
    return int(amount * multiplier)


def block_name_for_target(target_prefix_bytes: int) -> str:
    return f"large-agent-context-{target_prefix_bytes // 1024}kb"


def target_slug(target_prefix_bytes: int) -> str:
    return f"{target_prefix_bytes // 1024}kb"


def read_fixture(path: Path) -> dict[str, Any]:
    return owb.read_fixture(path)


def block_text(block: dict[str, Any]) -> str:
    return owb.block_text(block)


def reusable_prefix_metrics(fixture: dict[str, Any], max_ctx_size: int) -> FixtureMetrics:
    blocks_by_name = owb.index_blocks(fixture)
    scenarios = owb.selected_scenarios(fixture, None)
    prefix_block_names = owb.common_reusable_block_names(scenarios, blocks_by_name)
    prefix_prompt, _ = lcb.build_common_prefix_text(fixture, blocks_by_name, prefix_block_names)
    largest_prompt_bytes = 0
    for scenario in scenarios:
        prompt, _ = owb.build_prompt(fixture, blocks_by_name, scenario)
        largest_prompt_bytes = max(largest_prompt_bytes, len(prompt.encode("utf-8")))
    estimated_tokens = math.ceil(largest_prompt_bytes / APPROX_BYTES_PER_TOKEN)
    needed_tokens = math.ceil(estimated_tokens * CONTEXT_HEADROOM_RATIO) + CONTEXT_HEADROOM_TOKENS
    recommended_ctx = next((bucket for bucket in CTX_BUCKETS if bucket >= needed_tokens), CTX_BUCKETS[-1])
    if recommended_ctx > max_ctx_size:
        raise FixtureGenerationError(
            f"largest prompt needs approximately {needed_tokens} context tokens; "
            f"recommended ctx {recommended_ctx} exceeds max ctx {max_ctx_size}"
        )
    return FixtureMetrics(
        prefix_block_names=prefix_block_names,
        prefix_prompt_bytes=len(prefix_prompt.encode("utf-8")),
        largest_prompt_bytes=largest_prompt_bytes,
        estimated_largest_prompt_tokens=estimated_tokens,
        recommended_ctx_size=recommended_ctx,
    )


def collect_context(files: Iterable[str] = SAFE_CONTEXT_FILES) -> list[dict[str, str]]:
    entries = []
    for raw_path in files:
        path = ROOT / raw_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        entries.append({"path": raw_path, "text": sanitize_context_text(text)})
    if not entries:
        raise FixtureGenerationError("no allowlisted context files were available")
    return entries


def sanitize_context_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.rstrip()
        if not stripped:
            lines.append("")
            continue
        if stripped.startswith("ssh ") or "tailscale" in stripped.lower():
            continue
        lines.append(stripped)
    return "\n".join(lines).strip()


def context_stream(entries: list[dict[str, str]]) -> list[str]:
    chunks = []
    for entry in entries:
        chunks.append(f"### Allowlisted context source: {entry['path']}\n{entry['text']}")
    chunks.append(
        "\n".join(
            [
                "### Synthetic local-agent memory notes",
                "Stable agent memory usually repeats project goals, command constraints, tool policies, repo layout, validation rituals, and prior decisions.",
                "The benchmark intentionally makes this block reusable. Current command output, diffs, CI failures, and review comments remain volatile tails.",
                "A local model should use the stable prefix to understand the agent workflow while answering only the current turn.",
            ]
        )
    )
    return chunks


def expansion_text(seed_chunks: list[str], minimum_bytes: int) -> str:
    parts = []
    index = 0
    while len("\n\n".join(parts).encode("utf-8")) < minimum_bytes:
        chunk = seed_chunks[index % len(seed_chunks)]
        cycle = index // len(seed_chunks) + 1
        parts.append(f"### Reusable context pass {cycle}\n{chunk}")
        index += 1
    return "\n\n".join(parts)


def trim_utf8(text: str, byte_count: int) -> str:
    encoded = text.encode("utf-8")[:byte_count]
    return encoded.decode("utf-8", errors="ignore").rstrip()


def find_insert_index(block_names: list[str], blocks_by_name: dict[str, dict[str, Any]]) -> int:
    for index, block_name in enumerate(block_names):
        block = blocks_by_name.get(block_name, {})
        if block.get("tier") == "volatile":
            return index
    return len(block_names)


def add_or_replace_expansion_block(
    fixture: dict[str, Any],
    target_prefix_bytes: int,
    text: str,
    source_names: list[str],
) -> None:
    name = block_name_for_target(target_prefix_bytes)
    fixture["blocks"] = [block for block in fixture["blocks"] if block.get("name") != name]
    insert_at = next(
        (index + 1 for index, block in enumerate(fixture["blocks"]) if block.get("name") == "benchmark-instructions"),
        len(fixture["blocks"]),
    )
    fixture["blocks"].insert(
        insert_at,
        {
            "name": name,
            "tier": "stable",
            "cache_policy": "prefix-kv-candidate",
            "text": text,
            "metadata": {
                "generated": True,
                "target_prefix_bytes": target_prefix_bytes,
                "source_names": source_names,
            },
        },
    )
    blocks_by_name = owb.index_blocks(fixture)
    for scenario in fixture["scenarios"]:
        block_names = [block_name for block_name in owb.scenario_block_names(scenario) if block_name != name]
        insert_index = find_insert_index(block_names, blocks_by_name)
        block_names.insert(insert_index, name)
        scenario["blocks"] = block_names


def build_generated_fixture(
    source_fixture: dict[str, Any],
    source_path: Path,
    target_prefix_bytes: int,
    context_entries: list[dict[str, str]],
    max_ctx_size: int,
) -> tuple[dict[str, Any], FixtureMetrics]:
    fixture = copy.deepcopy(source_fixture)
    seed_chunks = context_stream(context_entries)
    source_names = [entry["path"] for entry in context_entries]
    current_metrics = reusable_prefix_metrics(fixture, max_ctx_size)
    extra_needed = max(target_prefix_bytes - current_metrics.prefix_prompt_bytes, 0)
    text = expansion_text(seed_chunks, extra_needed + 4096)
    add_or_replace_expansion_block(fixture, target_prefix_bytes, text, source_names)
    metrics = reusable_prefix_metrics(fixture, max_ctx_size)
    if metrics.prefix_prompt_bytes > target_prefix_bytes:
        block_name = block_name_for_target(target_prefix_bytes)
        blocks_by_name = owb.index_blocks(fixture)
        block = blocks_by_name[block_name]
        excess = metrics.prefix_prompt_bytes - target_prefix_bytes
        trimmed = trim_utf8(block_text(block), max(0, len(block_text(block).encode("utf-8")) - excess))
        block["text"] = trimmed
        metrics = reusable_prefix_metrics(fixture, max_ctx_size)

    if metrics.prefix_prompt_bytes < target_prefix_bytes:
        block_name = block_name_for_target(target_prefix_bytes)
        blocks_by_name = owb.index_blocks(fixture)
        deficit = target_prefix_bytes - metrics.prefix_prompt_bytes
        blocks_by_name[block_name]["text"] = block_text(blocks_by_name[block_name]) + "\n" + ("x" * deficit)
        metrics = reusable_prefix_metrics(fixture, max_ctx_size)

    metadata = fixture.setdefault("metadata", {})
    metadata["generated_large_prefix"] = {
        "generator": "benchmarks/generate_large_prefix_fixtures.py",
        "source_fixture": str(source_path),
        "target_prefix_bytes": target_prefix_bytes,
        "actual_prefix_bytes": metrics.prefix_prompt_bytes,
        "largest_prompt_bytes": metrics.largest_prompt_bytes,
        "estimated_largest_prompt_tokens": metrics.estimated_largest_prompt_tokens,
        "recommended_ctx_size": metrics.recommended_ctx_size,
        "expansion_block_names": [block_name_for_target(target_prefix_bytes)],
        "allowlisted_context_sources": source_names,
        "safety_status": "passed",
    }
    fixture["name"] = f"{fixture.get('name', source_path.stem)}-large-prefix-{target_slug(target_prefix_bytes)}"
    fixture["description"] = (
        f"{fixture.get('description', '').rstrip()} Generated large-prefix variant with "
        f"{metrics.prefix_prompt_bytes:,} reusable prefix bytes."
    ).strip()
    return fixture, metrics


def scan_for_secrets(fixture: dict[str, Any]) -> list[str]:
    text = json.dumps(fixture, sort_keys=True)
    matches = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            matches.append(pattern.pattern)
    return matches


def output_path(output_dir: Path, fixture: dict[str, Any], target_prefix_bytes: int) -> Path:
    name = str(fixture.get("name", f"large-prefix-{target_slug(target_prefix_bytes)}"))
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")
    return output_dir / f"{safe_name}.json"


def generate(
    source_path: Path,
    output_dir: Path,
    targets: list[int],
    max_ctx_size: int,
    dry_run: bool,
) -> list[GeneratedFixture]:
    source_fixture = read_fixture(source_path)
    context_entries = collect_context()
    generated = []
    for target in targets:
        fixture, metrics = build_generated_fixture(source_fixture, source_path, target, context_entries, max_ctx_size)
        secret_matches = scan_for_secrets(fixture)
        if secret_matches and not dry_run:
            raise FixtureGenerationError(
                f"secret-like pattern detected for target {target}: {', '.join(secret_matches)}"
            )
        path = output_path(output_dir, fixture, target)
        generated.append(
            GeneratedFixture(
                target_prefix_bytes=target,
                path=path,
                fixture=fixture,
                metrics=metrics,
                safety_status="failed" if secret_matches else "passed",
            )
        )
        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return generated


def print_summary(generated: list[GeneratedFixture], dry_run: bool) -> None:
    mode = "dry-run" if dry_run else "written"
    print(f"large-prefix fixture generation: {mode}")
    for item in generated:
        print(
            "target={target} actual_prefix={actual} largest_prompt={largest} "
            "estimated_tokens={tokens} recommended_ctx={ctx} safety={safety} path={path}".format(
                target=item.target_prefix_bytes,
                actual=item.metrics.prefix_prompt_bytes,
                largest=item.metrics.largest_prompt_bytes,
                tokens=item.metrics.estimated_largest_prompt_tokens,
                ctx=item.metrics.recommended_ctx_size,
                safety=item.safety_status,
                path=item.path,
            )
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate large reusable-prefix benchmark fixtures.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source workflow fixture JSON.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for generated fixtures.")
    parser.add_argument(
        "--target-prefix-bytes",
        type=parse_size,
        action="append",
        help="Target reusable prefix size. Accepts bytes, 16kb, 1mb. Can be repeated.",
    )
    parser.add_argument("--max-ctx-size", type=int, default=32768, help="Maximum context size to allow.")
    parser.add_argument("--dry-run", action="store_true", help="Report generated fixture metrics without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    targets = args.target_prefix_bytes or DEFAULT_TARGETS
    try:
        generated = generate(
            source_path=args.source,
            output_dir=args.output_dir,
            targets=targets,
            max_ctx_size=args.max_ctx_size,
            dry_run=args.dry_run,
        )
    except (FixtureGenerationError, owb.BenchmarkError, lcb.LlamaBenchmarkError) as exc:
        print(f"large-prefix fixture error: {exc}", file=sys.stderr)
        return 2
    print_summary(generated, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
