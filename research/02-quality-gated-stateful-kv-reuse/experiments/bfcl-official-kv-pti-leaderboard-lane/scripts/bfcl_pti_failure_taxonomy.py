#!/usr/bin/env python3
"""Summarize BFCL PTI smoke failures without exposing answer keys to inference.

This is a post-hoc audit tool. It reads model-loop records and classifies likely
failure owners from parser, schema-validator, repair-trace, and evaluator
pass/fail metadata already written after generation.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def category_of(record: dict[str, Any]) -> str:
    provenance = record.get("source_provenance")
    if isinstance(provenance, dict) and provenance.get("source_category"):
        return str(provenance["source_category"])
    case_id = str(record.get("case_id", ""))
    parts = case_id.split(":")
    return parts[1] if len(parts) > 2 else "unknown"


def record_passed(record: dict[str, Any]) -> bool:
    quality = record.get("quality") if isinstance(record.get("quality"), dict) else {}
    score = quality.get("bfcl_score") if isinstance(quality.get("bfcl_score"), dict) else {}
    return bool(score.get("passed"))


def schema_codes(record: dict[str, Any]) -> set[str]:
    codes: set[str] = set()
    for step in record.get("steps", []) if isinstance(record.get("steps"), list) else []:
        validation = step.get("bfcl_schema_validation") if isinstance(step, dict) else None
        if not isinstance(validation, dict):
            continue
        for error in validation.get("errors", []):
            if isinstance(error, dict) and error.get("code"):
                codes.add(str(error["code"]))
    return codes


def repair_damaged(record: dict[str, Any]) -> bool:
    for step in record.get("steps", []) if isinstance(record.get("steps"), list) else []:
        audit = step.get("repair_damage_audit") if isinstance(step, dict) else None
        if isinstance(audit, dict) and audit.get("run_readiness_blocking"):
            return True
    return False


def classify_owner(record: dict[str, Any]) -> str:
    if repair_damaged(record):
        return "harness_repair_damage"
    codes = schema_codes(record)
    if codes & {"unknown_function", "ambiguous_function", "function_choice_low_request_support"}:
        return "model_semantic_function_choice"
    if codes & {"likely_call_count_mismatch", "likely_extra_call_count"}:
        return "model_call_count"
    if codes & {"enum_literal_mismatch", "literal_preservation_suspect"}:
        return "model_literal_copy"
    if codes & {
        "missing_required_argument",
        "nested_type_mismatch",
        "type_mismatch",
        "type_normalization_required",
        "unexpected_argument",
    }:
        return "model_argument_shape"
    parse_statuses = [
        str(step.get("parse_status", ""))
        for step in record.get("steps", []) if isinstance(step, dict)
    ]
    if parse_statuses and all(status in {"invalid", "empty", "none"} or "parse" in status for status in parse_statuses):
        return "harness_parsing_or_model_format"
    return "unknown"


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_category: dict[str, Counter[str]] = defaultdict(Counter)
    owner_counts: Counter[str] = Counter()
    failures = []
    for record in records:
        category = category_of(record)
        passed = record_passed(record)
        by_category[category]["total"] += 1
        by_category[category]["passed" if passed else "failed"] += 1
        if passed:
            continue
        owner = classify_owner(record)
        owner_counts[owner] += 1
        failures.append(
            {
                "case_id": record.get("case_id"),
                "category": category,
                "likely_owner": owner,
                "schema_codes": sorted(schema_codes(record)),
                "repair_damaged_preserved_call": repair_damaged(record),
            }
        )
    return {
        "taxonomy_version": "bfcl_pti_no_cheat_failure_taxonomy_v1",
        "record_count": len(records),
        "passed": sum(1 for record in records if record_passed(record)),
        "failed": sum(1 for record in records if not record_passed(record)),
        "by_category": {key: dict(value) for key, value in sorted(by_category.items())},
        "likely_owner_counts": dict(owner_counts),
        "failures": failures,
        "no_cheat_boundary": {
            "post_hoc_only": True,
            "not_model_facing": True,
            "does_not_read_possible_answer": True,
            "does_not_emit_expected_calls": True,
        },
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# BFCL PTI Failure Taxonomy",
        "",
        "Post-hoc only. This artifact must not be fed into model prompts, repair prompts, or export transformations.",
        "",
        f"- Records: `{summary['record_count']}`",
        f"- Passed: `{summary['passed']}`",
        f"- Failed: `{summary['failed']}`",
        "",
        "## Category Counts",
        "",
    ]
    for category, counts in summary["by_category"].items():
        lines.append(
            f"- `{category}`: `{counts.get('passed', 0)}/{counts.get('total', 0)}` passed"
        )
    lines.extend(["", "## Likely Owner Counts", ""])
    for owner, count in sorted(summary["likely_owner_counts"].items()):
        lines.append(f"- `{owner}`: `{count}`")
    lines.extend(["", "## Failures", ""])
    for failure in summary["failures"]:
        codes = ", ".join(failure["schema_codes"]) or "none"
        lines.append(
            f"- `{failure['case_id']}`: `{failure['likely_owner']}`; schema codes: `{codes}`"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args(argv)

    summary = summarize(read_jsonl(args.records))
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(summary), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
