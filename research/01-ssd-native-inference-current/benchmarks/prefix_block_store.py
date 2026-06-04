#!/usr/bin/env python3
"""Build a metadata-only prefix block store from workflow fixtures."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import ollama_workflow_benchmark as owb


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STORE_DIR = ROOT / "benchmarks" / "prefix-store"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create content-addressed prompt block metadata for future prefix/KV cache experiments."
    )
    parser.add_argument("--model", default=owb.DEFAULT_OLLAMA_MODEL, help="Model name used as cache-key material.")
    parser.add_argument("--fixture", type=Path, default=owb.DEFAULT_FIXTURE, help="Workflow fixture JSON path.")
    parser.add_argument("--store-dir", type=Path, default=DEFAULT_STORE_DIR, help="Prefix block store output directory.")
    parser.add_argument("--scenario", action="append", help="Use only the named scenario. Can be repeated.")
    parser.add_argument("--num-ctx", type=int, default=None, help="Optional context window metadata.")
    parser.add_argument(
        "--sink-block-count",
        type=int,
        default=1,
        help="Number of earliest reusable blocks to mark as attention-sink candidates.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the store summary without writing files.")
    return parser.parse_args()


def storage_tier_for_role(role: str) -> str:
    if role == "attention-sink-candidate":
        return "ram-hot"
    if role == "stable-prefix":
        return "ssd-persistent-candidate"
    if role == "rolling-tail-candidate":
        return "ram-or-ssd-warm"
    return "no-persist"


def block_role(
    block_name: str,
    block: dict[str, Any],
    prefix_block_names: list[str],
    sink_block_names: set[str],
) -> str:
    if block_name in sink_block_names:
        return "attention-sink-candidate"
    if block_name in prefix_block_names:
        return "stable-prefix"
    if block.get("tier") == "semi-stable":
        return "rolling-tail-candidate"
    return "volatile-tail"


def build_block_record(
    fixture_name: str,
    block_name: str,
    block: dict[str, Any],
    role: str,
) -> dict[str, Any]:
    text = owb.block_text(block)
    return {
        "name": block_name,
        "fixture": fixture_name,
        "sha256": owb.sha256_text(text),
        "bytes": len(text.encode("utf-8")),
        "tier": block.get("tier", "unknown"),
        "cache_policy": block.get("cache_policy", "unknown"),
        "cache_role": role,
        "storage_recommendation": storage_tier_for_role(role),
        "text_persisted": False,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def cache_key_for_manifest(parts: dict[str, Any]) -> str:
    stable = json.dumps(parts, sort_keys=True, separators=(",", ":"))
    return owb.sha256_text(stable)


def build_store(args: argparse.Namespace) -> dict[str, Any]:
    fixture = owb.read_fixture(args.fixture)
    blocks_by_name = owb.index_blocks(fixture)
    scenarios = owb.selected_scenarios(fixture, args.scenario)
    if args.sink_block_count < 0:
        raise owb.BenchmarkError("--sink-block-count must be zero or greater.")

    prefix_args = SimpleNamespace(
        model=args.model,
        fixture=args.fixture,
        num_ctx=args.num_ctx,
    )
    prefix_manifest = owb.build_prefix_manifest(prefix_args, fixture, blocks_by_name, scenarios)
    prefix_block_names = list(prefix_manifest["prefix_block_names"])
    sink_block_names = set(prefix_block_names[: args.sink_block_count])

    block_records_by_hash: dict[str, dict[str, Any]] = {}
    block_hits = 0
    scenario_block_roles = []
    fixture_name = str(fixture.get("name", args.fixture.stem))

    for scenario in scenarios:
        scenario_roles = {
            "name": scenario.get("name", "unnamed"),
            "blocks": [],
        }
        for block_name in owb.scenario_block_names(scenario):
            block = blocks_by_name[block_name]
            role = block_role(block_name, block, prefix_block_names, sink_block_names)
            record = build_block_record(fixture_name, block_name, block, role)
            if record["sha256"] in block_records_by_hash:
                block_hits += 1
            else:
                block_records_by_hash[record["sha256"]] = record
            scenario_roles["blocks"].append(
                {
                    "name": block_name,
                    "sha256": record["sha256"],
                    "cache_role": role,
                    "storage_recommendation": record["storage_recommendation"],
                }
            )
        scenario_block_roles.append(scenario_roles)

    block_records = sorted(block_records_by_hash.values(), key=lambda record: (record["cache_role"], record["name"]))
    role_counts: dict[str, int] = {}
    role_bytes: dict[str, int] = {}
    for record in block_records:
        role = str(record["cache_role"])
        role_counts[role] = role_counts.get(role, 0) + 1
        role_bytes[role] = role_bytes.get(role, 0) + int(record["bytes"])

    cache_key_material = {
        "model": args.model,
        "fixture_hash": prefix_manifest["fixture_hash"],
        "selected_scenarios": prefix_manifest["selected_scenarios"],
        "prefix_block_hashes": [record["sha256"] for record in block_records if record["name"] in prefix_block_names],
        "sink_block_hashes": [record["sha256"] for record in block_records if record["name"] in sink_block_names],
        "num_ctx": args.num_ctx,
        "sink_block_count": args.sink_block_count,
    }
    cache_key = cache_key_for_manifest(cache_key_material)

    return {
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "store_version": 1,
        "model": args.model,
        "fixture_path": str(args.fixture),
        "fixture_hash": prefix_manifest["fixture_hash"],
        "selected_scenarios": prefix_manifest["selected_scenarios"],
        "cache_key_material": cache_key_material,
        "cache_key_sha256": cache_key,
        "prefix_manifest": prefix_manifest,
        "attention_sink_candidate_blocks": list(prefix_block_names[: args.sink_block_count]),
        "prefix_block_names": prefix_block_names,
        "block_records": block_records,
        "scenario_block_roles": scenario_block_roles,
        "summary": {
            "unique_block_count": len(block_records),
            "block_reference_hits": block_hits,
            "role_counts": role_counts,
            "role_bytes": role_bytes,
        },
        "note": "Metadata-only prefix block store. No KV tensors are persisted.",
    }


def write_store(store: dict[str, Any], store_dir: Path) -> tuple[Path, list[Path]]:
    blocks_dir = store_dir / "blocks"
    manifests_dir = store_dir / "manifests"
    blocks_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)

    written_blocks = []
    for block in store["block_records"]:
        path = blocks_dir / f"{block['sha256']}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(block, handle, indent=2)
            handle.write("\n")
        written_blocks.append(path)

    manifest_path = manifests_dir / f"{store['cache_key_sha256']}.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(store, handle, indent=2)
        handle.write("\n")
    return manifest_path, written_blocks


def print_summary(store: dict[str, Any]) -> None:
    print(f"Prefix block store cache key: {store['cache_key_sha256']}")
    print(f"Fixture: {store['fixture_path']}")
    print(f"Model: {store['model']}")
    print(f"Selected scenarios: {', '.join(store['selected_scenarios'])}")
    print(f"Unique blocks: {store['summary']['unique_block_count']}")
    print(f"Block reference hits: {store['summary']['block_reference_hits']}")
    print("Roles:")
    for role, count in sorted(store["summary"]["role_counts"].items()):
        bytes_for_role = store["summary"]["role_bytes"].get(role, 0)
        print(f"  {role}: {count} blocks, {bytes_for_role:,} bytes")
    print("Attention-sink candidates:")
    for block_name in store["attention_sink_candidate_blocks"]:
        print(f"  {block_name}")


def main() -> int:
    args = parse_args()
    try:
        store = build_store(args)
        print_summary(store)
        if args.dry_run:
            return 0
        manifest_path, block_paths = write_store(store, args.store_dir)
    except owb.BenchmarkError as exc:
        print(f"prefix store error: {exc}")
        return 2

    print(f"Manifest: {manifest_path}")
    print(f"Block records: {len(block_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
