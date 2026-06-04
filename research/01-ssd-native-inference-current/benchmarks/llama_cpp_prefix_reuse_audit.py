#!/usr/bin/env python3
"""Audit llama.cpp prefix reuse behavior through direct /completion calls."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flashcache.cache import sha256_text  # noqa: E402
from flashcache.llama_cpp import LlamaServerConfig, ManagedLlamaServer, llama_server_version  # noqa: E402
from flashcache.wrapper import completion_text, timing_record  # noqa: E402


DEFAULT_MODEL = ROOT / "benchmarks" / "models" / "gpt-oss-20b-mxfp4.gguf"
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "lcpr-results"
DEFAULT_CACHE_DIR = ROOT / "benchmarks" / "lcpr-cache"

ANSWER_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {
            "type": "string",
            "description": "The exact secret token only.",
        }
    },
    "required": ["answer"],
    "additionalProperties": False,
}

ANSWER_INSTRUCTION = (
    'Return only a JSON object with this exact shape: {"answer": "<exact secret token>"}. '
    "Do not include reasoning, markdown, or any extra keys."
)


@dataclass(frozen=True)
class AuditCase:
    case_id: str
    secret_token: str
    prefix_repeat: int
    stable_prefix: str
    tail_prompt: str

    @property
    def full_prompt(self) -> str:
        return f"{self.stable_prefix.rstrip()}\n\n{self.tail_prompt.lstrip()}"


class AuditError(Exception):
    """Raised for expected audit setup failures."""


def build_default_case(prefix_repeat: int) -> AuditCase:
    token = "LCPR-7319-SIGNAL"
    blocks = [
        "# Synthetic Long Prefix",
        "",
        "This prefix is deterministic filler for a llama.cpp prefix reuse audit.",
        "Every block is intentionally stable, visible, and semantically irrelevant except the final token declaration.",
        "",
    ]
    for index in range(prefix_repeat):
        blocks.append(
            "Block {index:04d}: alpha beta gamma delta epsilon zeta eta theta. "
            "The audit marker stays stable and the answer is not in this filler sentence.".format(index=index)
        )
    blocks.extend(
        [
            "",
            "Critical fact for the answer task:",
            f"The exact secret token is {token}.",
            "Do not transform the token.",
        ]
    )
    tail = f"What is the exact secret token from the prefix?\n\n{ANSWER_INSTRUCTION}"
    return AuditCase(
        case_id=f"long-prefix-{prefix_repeat}",
        secret_token=token,
        prefix_repeat=prefix_repeat,
        stable_prefix="\n".join(blocks),
        tail_prompt=tail,
    )


def parse_cases(path: Path | None, prefix_repeat: int) -> list[AuditCase]:
    if path is None:
        return [build_default_case(prefix_repeat)]
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise AuditError(f"{path}:{line_number} is not valid JSON") from exc
            rows.append(
                AuditCase(
                    case_id=str(row["case_id"]),
                    secret_token=str(row["secret_token"]),
                    prefix_repeat=int(row.get("prefix_repeat", 0)),
                    stable_prefix=str(row["stable_prefix"]),
                    tail_prompt=str(row["tail_prompt"]),
                )
            )
    if not rows:
        raise AuditError(f"No prefix-reuse audit cases in {path}")
    for row in rows:
        validate_case(row)
    return rows


def validate_case(case: AuditCase) -> None:
    if case.secret_token not in case.stable_prefix:
        raise AuditError(f"{case.case_id}: stable_prefix must contain secret_token")
    if case.secret_token in case.tail_prompt:
        raise AuditError(f"{case.case_id}: tail_prompt must not contain secret_token")


def extract_answer(raw_response: str) -> tuple[str, str | None]:
    stripped = raw_response.strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        return stripped, f"invalid JSON answer object: {exc}"
    if not isinstance(parsed, dict):
        return stripped, "JSON answer is not an object"
    answer = parsed.get("answer")
    if not isinstance(answer, str):
        return stripped, "JSON answer object is missing string key 'answer'"
    return answer.strip(), None


def score_answer(answer: str, expected_token: str, parse_error: str | None = None) -> dict[str, Any]:
    normalized = answer.strip()
    passed = parse_error is None and normalized == expected_token
    return {
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "answer": answer,
        "expected_token": expected_token,
        "expected_token_sha256": sha256_text(expected_token),
        "answer_equals_expected": normalized == expected_token,
        "answer_contains_expected": expected_token in normalized,
        "parse_error": parse_error,
    }


def llama_config_from_args(args: argparse.Namespace, cache_dir: Path) -> LlamaServerConfig:
    return LlamaServerConfig(
        server_bin=args.server_bin,
        model_path=args.model,
        hf_repo=args.hf_repo,
        slot_cache_dir=cache_dir / "slot-cache",
        log_dir=cache_dir / "logs",
        ctx_size=args.ctx_size,
        timeout=args.timeout,
    )


def log_label(prefix: str, *parts: str) -> str:
    return f"lcpr-{prefix}-{sha256_text('|'.join(parts))[:12]}"


def slot_filename_for(case: AuditCase) -> str:
    return f"{case.case_id}-{sha256_text(case.stable_prefix)[:16]}-slot.bin"


def slot_response(response: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in response.items() if key != "_wall_ms"}


def prompt_hashes(case: AuditCase) -> dict[str, Any]:
    return {
        "stable_prefix_bytes": len(case.stable_prefix.encode("utf-8")),
        "stable_prefix_sha256": sha256_text(case.stable_prefix),
        "tail_prompt_bytes": len(case.tail_prompt.encode("utf-8")),
        "tail_prompt_sha256": sha256_text(case.tail_prompt),
        "full_prompt_bytes": len(case.full_prompt.encode("utf-8")),
        "full_prompt_sha256": sha256_text(case.full_prompt),
    }


def response_summary(response: dict[str, Any], expected_token: str) -> dict[str, Any]:
    raw_response = completion_text(response)
    answer, parse_error = extract_answer(raw_response)
    score = score_answer(answer, expected_token, parse_error)
    return {
        "response": answer,
        "raw_response": raw_response,
        "response_sha256": sha256_text(raw_response),
        "answer_parse_error": parse_error,
        "passed": score["passed"],
        "score": score["score"],
        "score_details": score,
        "timings": timing_record(response),
    }


def timing_value(row: dict[str, Any] | None, key: str) -> Any:
    if not isinstance(row, dict):
        return None
    timings = row.get("timings", {})
    if not isinstance(timings, dict):
        return None
    return timings.get(key)


def reduction_metrics(baseline: dict[str, Any] | None, measured: dict[str, Any] | None) -> dict[str, Any]:
    baseline_prompt_ms = timing_value(baseline, "prompt_ms")
    measured_prompt_ms = timing_value(measured, "prompt_ms")
    baseline_prompt_n = timing_value(baseline, "prompt_n")
    measured_prompt_n = timing_value(measured, "prompt_n")
    prompt_ms_delta = None
    prompt_ms_ratio = None
    prompt_n_delta = None
    if isinstance(baseline_prompt_ms, (int, float)) and isinstance(measured_prompt_ms, (int, float)):
        prompt_ms_delta = float(baseline_prompt_ms) - float(measured_prompt_ms)
        prompt_ms_ratio = float(measured_prompt_ms) / float(baseline_prompt_ms) if baseline_prompt_ms else None
    if isinstance(baseline_prompt_n, (int, float)) and isinstance(measured_prompt_n, (int, float)):
        prompt_n_delta = float(baseline_prompt_n) - float(measured_prompt_n)
    token_reduction = prompt_n_delta is not None and prompt_n_delta > 0
    timing_reduction = prompt_ms_ratio is not None and prompt_ms_ratio <= 0.8
    return {
        "baseline_prompt_ms": baseline_prompt_ms,
        "measured_prompt_ms": measured_prompt_ms,
        "baseline_prompt_n": baseline_prompt_n,
        "measured_prompt_n": measured_prompt_n,
        "prompt_ms_delta": prompt_ms_delta,
        "prompt_ms_ratio": prompt_ms_ratio,
        "prompt_n_delta": prompt_n_delta,
        "token_reduction": token_reduction,
        "timing_reduction": timing_reduction,
        "reuse_observed": token_reduction or timing_reduction,
    }


def classify_record(record: dict[str, Any]) -> str:
    if record.get("error"):
        return "runtime_storage_issue"
    if record.get("passed") is not True:
        return "correctness_failure"
    mode = record.get("mode")
    if mode == "cold-full":
        return "baseline_passed"
    reduction = record.get("reduction", {})
    reuse_observed = isinstance(reduction, dict) and reduction.get("reuse_observed") is True
    if mode == "same-server-exact-repeat":
        return "exact_repeat_reuse_observed" if reuse_observed else "exact_repeat_no_reuse"
    if mode in {"same-server-restore-full", "fresh-server-restore-full"}:
        return "restore_reuse_observed" if reuse_observed else "restore_no_reuse"
    return "unknown"


def record_base(args: argparse.Namespace, case: AuditCase, mode: str) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "mode": mode,
        "model": args.hf_repo or str(args.model),
        "ctx_size": args.ctx_size,
        "predict": args.predict,
        "prime_n_predict": args.prime_n_predict,
        "temperature": args.temperature,
        "expected_token_sha256": sha256_text(case.secret_token),
        "prefix_repeat": case.prefix_repeat,
        **prompt_hashes(case),
    }


def build_record(
    args: argparse.Namespace,
    case: AuditCase,
    mode: str,
    *,
    started_at: float,
    measured_response: dict[str, Any],
    baseline_response: dict[str, Any] | None = None,
    phases: list[dict[str, Any]] | None = None,
    session_setup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    measured = response_summary(measured_response, case.secret_token)
    baseline = response_summary(baseline_response, case.secret_token) if baseline_response is not None else None
    passed = measured["passed"] and (baseline is None or baseline["passed"])
    record = {
        **record_base(args, case, mode),
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "answer_parse_error": measured["answer_parse_error"] or (baseline or {}).get("answer_parse_error"),
        "response": measured["response"],
        "raw_response": measured["raw_response"],
        "response_sha256": measured["response_sha256"],
        "score_details": measured["score_details"],
        "timings": measured["timings"],
        "baseline_timings": (baseline or {}).get("timings"),
        "reduction": reduction_metrics(baseline, measured) if baseline is not None else {},
        "latency_ms": (time.perf_counter() - started_at) * 1000,
        "phases": phases or [],
        "session_setup": session_setup or {},
    }
    record["failure_classification"] = classify_record(record)
    return record


def build_error_record(args: argparse.Namespace, case: AuditCase, mode: str, exc: Exception, *, started_at: float) -> dict[str, Any]:
    record = {
        **record_base(args, case, mode),
        "passed": False,
        "score": 0.0,
        "answer_parse_error": None,
        "response": "",
        "raw_response": "",
        "response_sha256": sha256_text(""),
        "score_details": {"passed": False, "score": 0.0, "error": str(exc), "expected_token_sha256": sha256_text(case.secret_token)},
        "timings": {},
        "baseline_timings": None,
        "reduction": {},
        "latency_ms": (time.perf_counter() - started_at) * 1000,
        "phases": [],
        "session_setup": {},
        "error": str(exc),
    }
    record["failure_classification"] = classify_record(record)
    return record


def run_cold_full(args: argparse.Namespace, case: AuditCase, cache_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        server = ManagedLlamaServer(llama_config_from_args(args, cache_dir), label=log_label("cold", case.case_id))
        with server as client:
            response = client.completion(
                case.full_prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=False,
                json_schema=ANSWER_JSON_SCHEMA,
            )
        return build_record(
            args,
            case,
            "cold-full",
            started_at=started,
            measured_response=response,
            session_setup={"completion_log_path": str(server.log_path) if server.log_path else None},
        )
    except Exception as exc:
        return build_error_record(args, case, "cold-full", exc, started_at=started)


def run_same_server_exact_repeat(args: argparse.Namespace, case: AuditCase, cache_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        server = ManagedLlamaServer(llama_config_from_args(args, cache_dir), label=log_label("repeat", case.case_id))
        with server as client:
            first = client.completion(
                case.full_prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=True,
                json_schema=ANSWER_JSON_SCHEMA,
            )
            second = client.completion(
                case.full_prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=True,
                json_schema=ANSWER_JSON_SCHEMA,
            )
        return build_record(
            args,
            case,
            "same-server-exact-repeat",
            started_at=started,
            baseline_response=first,
            measured_response=second,
            phases=[
                {"phase": "first-full", "timings": timing_record(first)},
                {"phase": "second-full", "timings": timing_record(second)},
            ],
            session_setup={"completion_log_path": str(server.log_path) if server.log_path else None},
        )
    except Exception as exc:
        return build_error_record(args, case, "same-server-exact-repeat", exc, started_at=started)


def run_same_server_restore_full(args: argparse.Namespace, case: AuditCase, cold_record: dict[str, Any] | None, cache_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        slot_filename = slot_filename_for(case)
        config = llama_config_from_args(args, cache_dir)
        slot_path = config.slot_cache_dir / slot_filename
        server = ManagedLlamaServer(config, label=log_label("same-restore", case.case_id))
        with server as client:
            prime = client.completion(
                case.stable_prefix,
                n_predict=args.prime_n_predict,
                temperature=args.temperature,
                cache_prompt=False,
            )
            save = client.save_slot(slot_filename)
            restore = client.restore_slot(slot_filename)
            measured = client.completion(
                case.full_prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=True,
                json_schema=ANSWER_JSON_SCHEMA,
            )
        baseline = response_from_record(cold_record)
        setup = {
            "slot_filename": slot_filename,
            "slot_path": str(slot_path),
            "slot_file_bytes": slot_path.stat().st_size if slot_path.exists() else save.get("n_written"),
            "prime_timings": timing_record(prime),
            "prime_wall_ms": prime.get("_wall_ms"),
            "save_response": slot_response(save),
            "save_wall_ms": save.get("_wall_ms"),
            "restore_response": slot_response(restore),
            "restore_wall_ms": restore.get("_wall_ms"),
            "completion_log_path": str(server.log_path) if server.log_path else None,
        }
        return build_record(
            args,
            case,
            "same-server-restore-full",
            started_at=started,
            baseline_response=baseline,
            measured_response=measured,
            phases=[
                {"phase": "prime-prefix", "timings": timing_record(prime)},
                {"phase": "measured-full", "timings": timing_record(measured)},
            ],
            session_setup=setup,
        )
    except Exception as exc:
        return build_error_record(args, case, "same-server-restore-full", exc, started_at=started)


def run_fresh_server_restore_full(args: argparse.Namespace, case: AuditCase, cold_record: dict[str, Any] | None, cache_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        slot_filename = slot_filename_for(case)
        config = llama_config_from_args(args, cache_dir)
        slot_path = config.slot_cache_dir / slot_filename
        prime_server = ManagedLlamaServer(config, label=log_label("fresh-prime", case.case_id))
        with prime_server as client:
            prime = client.completion(
                case.stable_prefix,
                n_predict=args.prime_n_predict,
                temperature=args.temperature,
                cache_prompt=False,
            )
            save = client.save_slot(slot_filename)
        complete_server = ManagedLlamaServer(llama_config_from_args(args, cache_dir), label=log_label("fresh-restore", case.case_id))
        with complete_server as client:
            restore = client.restore_slot(slot_filename)
            measured = client.completion(
                case.full_prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=True,
                json_schema=ANSWER_JSON_SCHEMA,
            )
        baseline = response_from_record(cold_record)
        setup = {
            "slot_filename": slot_filename,
            "slot_path": str(slot_path),
            "slot_file_bytes": slot_path.stat().st_size if slot_path.exists() else save.get("n_written"),
            "prime_timings": timing_record(prime),
            "prime_wall_ms": prime.get("_wall_ms"),
            "save_response": slot_response(save),
            "save_wall_ms": save.get("_wall_ms"),
            "restore_response": slot_response(restore),
            "restore_wall_ms": restore.get("_wall_ms"),
            "prime_log_path": str(prime_server.log_path) if prime_server.log_path else None,
            "completion_log_path": str(complete_server.log_path) if complete_server.log_path else None,
        }
        return build_record(
            args,
            case,
            "fresh-server-restore-full",
            started_at=started,
            baseline_response=baseline,
            measured_response=measured,
            phases=[
                {"phase": "prime-prefix", "timings": timing_record(prime)},
                {"phase": "measured-full", "timings": timing_record(measured)},
            ],
            session_setup=setup,
        )
    except Exception as exc:
        return build_error_record(args, case, "fresh-server-restore-full", exc, started_at=started)


def response_from_record(record: dict[str, Any] | None) -> dict[str, Any] | None:
    if not record:
        return None
    raw = record.get("raw_response")
    timings = record.get("timings")
    if not isinstance(raw, str) or not isinstance(timings, dict):
        return None
    response = {"content": raw, "timings": {}}
    timing_map = {
        "prompt_ms": timings.get("prompt_ms"),
        "prompt_n": timings.get("prompt_n"),
        "prompt_per_token_ms": timings.get("prompt_per_token_ms"),
        "predicted_ms": timings.get("predicted_ms"),
        "predicted_n": timings.get("predicted_n"),
        "predicted_per_token_ms": timings.get("predicted_per_token_ms"),
    }
    response["timings"] = {key: value for key, value in timing_map.items() if value is not None}
    response["_wall_ms"] = timings.get("wall_ms")
    return response


def selected_modes(args: argparse.Namespace) -> list[str]:
    if args.mode == "all":
        return ["cold-full", "same-server-exact-repeat", "same-server-restore-full", "fresh-server-restore-full"]
    return [args.mode]


def dry_run_record(args: argparse.Namespace, case: AuditCase, mode: str, cold_record: dict[str, Any] | None = None) -> dict[str, Any]:
    base_response = {"content": json.dumps({"answer": case.secret_token}), "timings": {"prompt_ms": 1200.0, "prompt_n": 2048, "predicted_n": 12}}
    repeat_response = {"content": json.dumps({"answer": case.secret_token}), "timings": {"prompt_ms": 40.0, "prompt_n": 24, "predicted_n": 12}}
    restore_response = {"content": json.dumps({"answer": case.secret_token}), "timings": {"prompt_ms": 1180.0, "prompt_n": 2048, "predicted_n": 12}}
    if mode == "cold-full":
        return build_record(args, case, mode, started_at=time.perf_counter(), measured_response=base_response, session_setup={"dry_run": True})
    if mode == "same-server-exact-repeat":
        return build_record(args, case, mode, started_at=time.perf_counter(), baseline_response=base_response, measured_response=repeat_response, session_setup={"dry_run": True})
    measured = restore_response if mode in {"same-server-restore-full", "fresh-server-restore-full"} else base_response
    setup = {
        "dry_run": True,
        "slot_filename": slot_filename_for(case),
        "save_response": {"n_saved": 2000, "n_written": 1000},
        "restore_response": {"n_restored": 2000, "n_read": 1000},
    }
    return build_record(args, case, mode, started_at=time.perf_counter(), baseline_response=response_from_record(cold_record), measured_response=measured, session_setup=setup)


def run_case(args: argparse.Namespace, case: AuditCase) -> list[dict[str, Any]]:
    records = []
    cold_record = None
    for mode in selected_modes(args):
        print(f"[llama-cpp-prefix-reuse] {mode}: {case.case_id}", flush=True)
        cache_dir = args.cache_dir / mode / case.case_id
        if args.dry_run:
            record = dry_run_record(args, case, mode, cold_record)
        elif mode == "cold-full":
            record = run_cold_full(args, case, cache_dir)
        elif mode == "same-server-exact-repeat":
            record = run_same_server_exact_repeat(args, case, cache_dir)
        elif mode == "same-server-restore-full":
            record = run_same_server_restore_full(args, case, cold_record, cache_dir)
        elif mode == "fresh-server-restore-full":
            record = run_fresh_server_restore_full(args, case, cold_record, cache_dir)
        else:
            raise AuditError(f"Unsupported mode: {mode}")
        records.append(record)
        if mode == "cold-full":
            cold_record = record
    return records


def mean(values: list[Any]) -> float | None:
    numbers = [float(value) for value in values if isinstance(value, (int, float))]
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_mode: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_mode.setdefault(str(record["mode"]), []).append(record)

    mode_summary = {}
    for mode, rows in sorted(by_mode.items()):
        classifications: dict[str, int] = {}
        for row in rows:
            classification = str(row.get("failure_classification", "unknown"))
            classifications[classification] = classifications.get(classification, 0) + 1
        mode_summary[mode] = {
            "case_count": len(rows),
            "passed_count": sum(1 for row in rows if row.get("passed") is True),
            "pass_rate": sum(1 for row in rows if row.get("passed") is True) / len(rows) if rows else None,
            "mean_prompt_ms": mean([timing_value(row, "prompt_ms") for row in rows]),
            "mean_prompt_n": mean([timing_value(row, "prompt_n") for row in rows]),
            "mean_prompt_ms_delta": mean([(row.get("reduction") or {}).get("prompt_ms_delta") for row in rows]),
            "mean_prompt_n_delta": mean([(row.get("reduction") or {}).get("prompt_n_delta") for row in rows]),
            "reuse_observed_count": sum(1 for row in rows if (row.get("reduction") or {}).get("reuse_observed") is True),
            "response_error_count": sum(1 for row in rows if row.get("error")),
            "answer_parse_error_count": sum(1 for row in rows if row.get("answer_parse_error")),
            "failure_classifications": dict(sorted(classifications.items())),
        }

    exact_repeat_rows = by_mode.get("same-server-exact-repeat", [])
    same_restore_rows = by_mode.get("same-server-restore-full", [])
    fresh_restore_rows = by_mode.get("fresh-server-restore-full", [])
    exact_repeat_reuse = any((row.get("reduction") or {}).get("reuse_observed") is True for row in exact_repeat_rows)
    same_restore_reuse = any((row.get("reduction") or {}).get("reuse_observed") is True for row in same_restore_rows)
    fresh_restore_reuse = any((row.get("reduction") or {}).get("reuse_observed") is True for row in fresh_restore_rows)
    any_runtime_error = any(row.get("error") for row in records)
    all_passed = all(row.get("passed") is True for row in records)
    if any_runtime_error:
        overall = "runtime_storage_issue"
    elif not all_passed:
        overall = "correctness_failure"
    elif not exact_repeat_reuse:
        overall = "exact_repeat_no_reuse_backend_api_investigation"
    elif not same_restore_reuse and not fresh_restore_reuse:
        overall = "exact_repeat_reuse_but_restore_no_reuse"
    elif fresh_restore_reuse:
        overall = "fresh_server_restore_reuse_candidate"
    else:
        overall = "same_server_restore_reuse_only"

    return {
        "by_mode": mode_summary,
        "gate": {
            "all_scored_controls_passed": all_passed,
            "exact_repeat_reuse_observed": exact_repeat_reuse,
            "same_server_restore_reuse_observed": same_restore_reuse,
            "fresh_server_restore_reuse_observed": fresh_restore_reuse,
            "recommend_graphwalks_follow_up": fresh_restore_reuse,
            "overall_interpretation": overall,
        },
    }


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return args.output
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_slug = Path(str(args.hf_repo or args.model)).stem.replace(":", "-").replace("/", "-")
    return args.output_dir / f"{timestamp}-{model_slug}-llama-cpp-prefix-reuse-audit.json"


def command_metadata(args: argparse.Namespace) -> dict[str, Any]:
    version = None
    if not args.dry_run:
        try:
            version = llama_server_version(args.server_bin)
        except Exception as exc:
            version = f"unavailable: {exc}"
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "server_bin": args.server_bin,
        "server_version": version,
        "model": args.hf_repo or str(args.model),
        "model_bytes": None if args.hf_repo or not args.model.exists() else args.model.stat().st_size,
        "hf_repo": args.hf_repo,
        "ctx_size": args.ctx_size,
        "predict": args.predict,
        "prime_n_predict": args.prime_n_predict,
        "prefix_repeat": args.prefix_repeat,
        "temperature": args.temperature,
        "timeout": args.timeout,
        "mode": args.mode,
        "dry_run": args.dry_run,
        "machine": {
            "node": platform.node(),
            "platform": platform.platform(),
            "python": sys.version,
        },
        "artifact_paths": {
            "output_dir": str(args.output_dir),
            "cache_dir": str(args.cache_dir),
            "output": str(output_path(args)),
        },
    }


def run_audit(args: argparse.Namespace) -> dict[str, Any]:
    cases = parse_cases(args.cases, args.prefix_repeat)
    for case in cases:
        validate_case(case)
    records: list[dict[str, Any]] = []
    for case in cases:
        records.extend(run_case(args, case))
    return {
        "metadata": command_metadata(args),
        "cases": [asdict(case) for case in cases],
        "records": records,
        "summary": summarize(records),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit direct llama.cpp prefix reuse behavior.")
    parser.add_argument("--server-bin", default="llama-server", help="llama.cpp server binary.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="Path to a GGUF model.")
    parser.add_argument("--hf-repo", help="Hugging Face GGUF repo for llama.cpp -hf loading.")
    parser.add_argument("--cases", type=Path, help="Optional JSONL audit cases.")
    parser.add_argument(
        "--mode",
        choices=["all", "cold-full", "same-server-exact-repeat", "same-server-restore-full", "fresh-server-restore-full"],
        default="all",
        help="Audit mode to run.",
    )
    parser.add_argument("--prefix-repeat", type=int, default=256, help="Synthetic prefix block repetitions.")
    parser.add_argument("--ctx-size", type=int, default=32768, help="llama.cpp context size.")
    parser.add_argument("--predict", type=int, default=32, help="Generated tokens per answer.")
    parser.add_argument("--prime-n-predict", type=int, default=0, help="Generated tokens while priming stable prefix.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    parser.add_argument("--timeout", type=float, default=240.0, help="HTTP/server timeout in seconds.")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Directory for slot/log artifacts.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for audit JSON output.")
    parser.add_argument("--output", type=Path, help="Explicit output JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Write record skeletons without starting llama.cpp.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.prefix_repeat < 1:
        print("--prefix-repeat must be >= 1", file=sys.stderr)
        return 2
    if not args.dry_run and not args.hf_repo and not args.model.exists():
        print(f"Model file not found: {args.model}", file=sys.stderr)
        return 2
    try:
        result = run_audit(args)
    except AuditError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote llama.cpp prefix reuse audit result: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
