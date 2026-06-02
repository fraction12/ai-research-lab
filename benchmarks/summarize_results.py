#!/usr/bin/env python3
"""Summarize benchmark result JSON files for quick local-run comparison."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass
class SummaryRow:
    kind: str
    path: Path
    model: str
    fixture: str
    started_at: str
    prefix_bytes: Any = None
    before_ms: Any = None
    after_ms: Any = None
    delta_ms: Any = None
    ratio: Any = None
    hit_rate: Any = None
    cache_states: str | None = None
    slot_file_bytes: Any = None
    unsupported_reason: str | None = None


def value(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def summarize_data(data: dict[str, Any], path: Path) -> SummaryRow:
    metadata = data.get("metadata", {})
    prompt_set = data.get("prompt_set", {})
    comparison = data.get("comparison", {})
    common = {
        "path": path,
        "model": str(metadata.get("model", "n/a")),
        "fixture": str(metadata.get("fixture", "n/a")),
        "started_at": str(metadata.get("started_at", "n/a")),
        "prefix_bytes": prompt_set.get("prefix_prompt_bytes"),
    }

    if "baseline_prompt_ms_sum" in comparison or "restored_prompt_ms_sum" in comparison:
        return SummaryRow(
            kind="llama-cpp-prompt-cache",
            before_ms=comparison.get("baseline_prompt_ms_sum"),
            after_ms=comparison.get("restored_prompt_ms_sum"),
            delta_ms=comparison.get("baseline_minus_restored_prompt_ms"),
            ratio=comparison.get("baseline_minus_restored_prompt_ratio"),
            slot_file_bytes=value(data, "slot_cache", "file_bytes"),
            **common,
        )

    if "direct_prompt_ms_sum" in comparison or "wrapper_prompt_ms_sum" in comparison:
        states = [str(run.get("cache_state", "n/a")) for run in data.get("wrapper_cache_aware", [])]
        return SummaryRow(
            kind="flashcache-wrapper",
            before_ms=comparison.get("direct_prompt_ms_sum"),
            after_ms=comparison.get("wrapper_prompt_ms_sum"),
            delta_ms=comparison.get("direct_minus_wrapper_prompt_ms"),
            ratio=comparison.get("direct_minus_wrapper_prompt_ratio"),
            hit_rate=comparison.get("wrapper_cache_hit_rate"),
            cache_states=",".join(states) if states else None,
            **common,
        )

    return SummaryRow(
        kind="unsupported",
        path=path,
        model=str(metadata.get("model", "n/a")),
        fixture=str(metadata.get("fixture", "n/a")),
        started_at=str(metadata.get("started_at", "n/a")),
        unsupported_reason="unrecognized benchmark result schema",
    )


def summarize_path(path: Path) -> SummaryRow:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return SummaryRow(
            kind="unsupported",
            path=path,
            model="n/a",
            fixture="n/a",
            started_at="n/a",
            unsupported_reason=str(exc),
        )
    if not isinstance(data, dict):
        return SummaryRow(
            kind="unsupported",
            path=path,
            model="n/a",
            fixture="n/a",
            started_at="n/a",
            unsupported_reason="top-level JSON is not an object",
        )
    return summarize_data(data, path)


def expand_inputs(inputs: Iterable[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            paths.extend(sorted(path.rglob("*.json")))
        else:
            matches = sorted(Path().glob(raw)) if any(char in raw for char in "*?[]") else []
            paths.extend(matches or [path])
    return paths


def format_value(item: Any) -> str:
    if item is None:
        return "n/a"
    if isinstance(item, float):
        return f"{item:.3f}"
    return str(item)


def render(rows: list[SummaryRow]) -> str:
    headers = [
        "kind",
        "started",
        "model",
        "fixture",
        "prefix_bytes",
        "before_ms",
        "after_ms",
        "delta_ms",
        "ratio",
        "hit_rate",
        "slot_bytes",
        "cache_states",
        "path",
    ]
    table = ["\t".join(headers)]
    for row in rows:
        table.append(
            "\t".join(
                [
                    row.kind,
                    row.started_at,
                    row.model,
                    row.fixture,
                    format_value(row.prefix_bytes),
                    format_value(row.before_ms),
                    format_value(row.after_ms),
                    format_value(row.delta_ms),
                    format_value(row.ratio),
                    format_value(row.hit_rate),
                    format_value(row.slot_file_bytes),
                    row.cache_states or "n/a",
                    str(row.path),
                ]
            )
        )
        if row.unsupported_reason:
            table.append(f"# unsupported {row.path}: {row.unsupported_reason}")
    return "\n".join(table)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize benchmark result JSON files.")
    parser.add_argument("paths", nargs="+", help="Result JSON files, glob patterns, or directories.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = [summarize_path(path) for path in expand_inputs(args.paths)]
    print(render(rows))
    return 0 if all(row.kind != "unsupported" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
