#!/usr/bin/env python3
"""Probe restored llama.cpp prefix slots while resending the full prompt."""

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


DEFAULT_GEMMA4_HF_REPO = "ggml-org/gemma-4-12B-it-GGUF:Q4_K_M"
DEFAULT_MODEL = ROOT / "benchmarks" / "models" / "gemma-4-12B-it-Q4_K_M.gguf"
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "rpfr-results"
DEFAULT_CACHE_DIR = ROOT / "benchmarks" / "rpfr-cache"

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
class ProbeCase:
    case_id: str
    secret_token: str
    perturbed_token: str
    stable_prefix: str
    perturbed_prefix: str
    tail_prompt: str

    @property
    def full_prompt(self) -> str:
        return f"{self.stable_prefix.rstrip()}\n\n{self.tail_prompt.lstrip()}"

    @property
    def perturbed_full_prompt(self) -> str:
        return f"{self.perturbed_prefix.rstrip()}\n\n{self.tail_prompt.lstrip()}"


class ProbeError(Exception):
    """Raised for expected probe setup failures."""


def default_cases() -> list[ProbeCase]:
    rows = [
        ("prefix-alpha", "RPF-1047-ALPHA", "RPF-2047-ALPHA"),
        ("prefix-bravo", "RPF-3186-BRAVO", "RPF-4186-BRAVO"),
        ("prefix-charlie", "RPF-5293-CHARLIE", "RPF-6293-CHARLIE"),
    ]
    cases = []
    for case_id, token, perturbed_token in rows:
        stable = (
            "You are a precise memory assistant. Memorize this exact secret token for the next turn. "
            f"The exact secret token is {token}. Do not transform it."
        )
        perturbed = (
            "You are a precise memory assistant. Memorize this exact secret token for the next turn. "
            f"The exact secret token is {perturbed_token}. Do not transform it."
        )
        tail = f"What is the exact secret token from the previous turn?\n\n{ANSWER_INSTRUCTION}"
        cases.append(
            ProbeCase(
                case_id=case_id,
                secret_token=token,
                perturbed_token=perturbed_token,
                stable_prefix=stable,
                perturbed_prefix=perturbed,
                tail_prompt=tail,
            )
        )
    return cases


def parse_cases(path: Path | None) -> list[ProbeCase]:
    if path is None:
        return default_cases()
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ProbeError(f"{path}:{line_number} is not valid JSON") from exc
            stable_prefix = str(row["stable_prefix"])
            secret_token = str(row["secret_token"])
            perturbed_token = str(row.get("perturbed_token", f"{secret_token}-PERTURBED"))
            perturbed_prefix = str(row.get("perturbed_prefix", stable_prefix.replace(secret_token, perturbed_token)))
            rows.append(
                ProbeCase(
                    case_id=str(row["case_id"]),
                    secret_token=secret_token,
                    perturbed_token=perturbed_token,
                    stable_prefix=stable_prefix,
                    perturbed_prefix=perturbed_prefix,
                    tail_prompt=str(row["tail_prompt"]),
                )
            )
    if not rows:
        raise ProbeError(f"No restored-prefix probe cases in {path}")
    for row in rows:
        validate_case(row)
    return rows


def validate_case(case: ProbeCase) -> None:
    if case.secret_token == case.perturbed_token:
        raise ProbeError(f"{case.case_id}: secret_token and perturbed_token must differ")
    if case.secret_token not in case.stable_prefix:
        raise ProbeError(f"{case.case_id}: stable_prefix must contain secret_token")
    if case.perturbed_token not in case.perturbed_prefix:
        raise ProbeError(f"{case.case_id}: perturbed_prefix must contain perturbed_token")
    if case.secret_token in case.perturbed_prefix:
        raise ProbeError(f"{case.case_id}: perturbed_prefix must not contain original secret_token")


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


def score_answer(
    answer: str,
    expected_token: str,
    *,
    parse_error: str | None = None,
    forbidden_tokens: list[str] | None = None,
) -> dict[str, Any]:
    normalized = answer.strip()
    forbidden_tokens = [token for token in (forbidden_tokens or []) if token]
    forbidden_present = [token for token in forbidden_tokens if token in normalized]
    exact_match = parse_error is None and normalized == expected_token
    passed = exact_match and not forbidden_present
    return {
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "answer": answer,
        "expected_token": expected_token,
        "expected_token_sha256": sha256_text(expected_token),
        "answer_equals_expected": normalized == expected_token,
        "answer_contains_expected": expected_token in normalized,
        "forbidden_token_sha256": [sha256_text(token) for token in forbidden_tokens],
        "forbidden_token_present_sha256": [sha256_text(token) for token in forbidden_present],
        "leakage_detected": bool(forbidden_present),
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


def slot_filename_for(case: ProbeCase) -> str:
    return f"{case.case_id}-{sha256_text(case.stable_prefix)[:16]}-slot.bin"


def log_label(prefix: str, *parts: str) -> str:
    material = "|".join(parts)
    return f"rpfr-{prefix}-{sha256_text(material)[:12]}"


def mode_completion_prompt(case: ProbeCase, mode: str) -> str:
    if mode in {"cold-full", "restored-full", "wrong-slot-full"}:
        return case.full_prompt
    if mode == "perturbed-full":
        return case.perturbed_full_prompt
    if mode == "prime-save":
        return case.stable_prefix
    raise ProbeError(f"Unsupported restored-prefix probe mode: {mode}")


def expected_token_for_mode(case: ProbeCase, mode: str) -> str:
    if mode == "perturbed-full":
        return case.perturbed_token
    return case.secret_token


def prompt_hashes(case: ProbeCase, completion_prompt: str) -> dict[str, Any]:
    return {
        "stable_prefix_bytes": len(case.stable_prefix.encode("utf-8")),
        "stable_prefix_sha256": sha256_text(case.stable_prefix),
        "perturbed_prefix_bytes": len(case.perturbed_prefix.encode("utf-8")),
        "perturbed_prefix_sha256": sha256_text(case.perturbed_prefix),
        "tail_prompt_bytes": len(case.tail_prompt.encode("utf-8")),
        "tail_prompt_sha256": sha256_text(case.tail_prompt),
        "full_prompt_bytes": len(case.full_prompt.encode("utf-8")),
        "full_prompt_sha256": sha256_text(case.full_prompt),
        "perturbed_full_prompt_bytes": len(case.perturbed_full_prompt.encode("utf-8")),
        "perturbed_full_prompt_sha256": sha256_text(case.perturbed_full_prompt),
        "completion_prompt_bytes": len(completion_prompt.encode("utf-8")),
        "completion_prompt_sha256": sha256_text(completion_prompt),
    }


def record_base(
    args: argparse.Namespace,
    case: ProbeCase,
    mode: str,
    completion_prompt: str,
    expected_token: str,
    *,
    slot_source_case: ProbeCase | None = None,
) -> dict[str, Any]:
    base = {
        "case_id": case.case_id,
        "mode": mode,
        "model": args.hf_repo or str(args.model),
        "ctx_size": args.ctx_size,
        "predict": args.predict,
        "prime_n_predict": args.prime_n_predict,
        "temperature": args.temperature,
        "expected_token_sha256": sha256_text(expected_token),
        "secret_token_sha256": sha256_text(case.secret_token),
        "perturbed_token_sha256": sha256_text(case.perturbed_token),
        **prompt_hashes(case, completion_prompt),
    }
    if slot_source_case is not None:
        base.update(
            {
                "slot_source_case_id": slot_source_case.case_id,
                "slot_source_expected_token_sha256": sha256_text(slot_source_case.secret_token),
                "slot_source_stable_prefix_sha256": sha256_text(slot_source_case.stable_prefix),
            }
        )
    return base


def slot_response(response: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in response.items() if key != "_wall_ms"}


def classify_record(record: dict[str, Any]) -> str:
    if record.get("error"):
        return "runtime_storage_issue"
    if record.get("scored") is False:
        return "not_scored_prime_save"
    if record.get("answer_parse_error"):
        return "scorer_parser_brittleness"
    if record.get("passed") is True:
        return "passed"
    score_details = record.get("score_details", {})
    if isinstance(score_details, dict) and score_details.get("leakage_detected"):
        return "session_cache_semantic_issue"
    mode = record.get("mode")
    if mode == "cold-full":
        return "model_weakness"
    if mode in {"restored-full", "perturbed-full", "wrong-slot-full"}:
        return "session_cache_semantic_issue"
    return "prompt_protocol_issue"


def build_response_record(
    args: argparse.Namespace,
    case: ProbeCase,
    mode: str,
    completion_prompt: str,
    response: dict[str, Any],
    *,
    started_at: float,
    expected_token: str,
    forbidden_tokens: list[str] | None = None,
    slot_source_case: ProbeCase | None = None,
    session_setup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_response = completion_text(response)
    answer, parse_error = extract_answer(raw_response)
    score = score_answer(answer, expected_token, parse_error=parse_error, forbidden_tokens=forbidden_tokens)
    record = {
        **record_base(args, case, mode, completion_prompt, expected_token, slot_source_case=slot_source_case),
        "scored": True,
        "response": answer,
        "raw_response": raw_response,
        "response_sha256": sha256_text(raw_response),
        "answer_parse_error": parse_error,
        "passed": score["passed"],
        "score": score["score"],
        "score_details": score,
        "latency_ms": (time.perf_counter() - started_at) * 1000,
        "timings": timing_record(response),
        "session_setup": session_setup or {},
    }
    record["failure_classification"] = classify_record(record)
    return record


def build_error_record(
    args: argparse.Namespace,
    case: ProbeCase,
    mode: str,
    completion_prompt: str,
    exc: Exception,
    *,
    started_at: float,
    expected_token: str,
    slot_source_case: ProbeCase | None = None,
) -> dict[str, Any]:
    record = {
        **record_base(args, case, mode, completion_prompt, expected_token, slot_source_case=slot_source_case),
        "scored": True,
        "response": "",
        "raw_response": "",
        "response_sha256": sha256_text(""),
        "answer_parse_error": None,
        "passed": False,
        "score": 0.0,
        "score_details": {"passed": False, "score": 0.0, "error": str(exc), "expected_token_sha256": sha256_text(expected_token)},
        "latency_ms": (time.perf_counter() - started_at) * 1000,
        "timings": {},
        "session_setup": {},
        "error": str(exc),
    }
    record["failure_classification"] = classify_record(record)
    return record


def save_prefix_slot(args: argparse.Namespace, slot_case: ProbeCase, cache_dir: Path, label_suffix: str) -> dict[str, Any]:
    slot_filename = slot_filename_for(slot_case)
    config = llama_config_from_args(args, cache_dir)
    slot_path = config.slot_cache_dir / slot_filename
    setup_started = time.perf_counter()
    server = ManagedLlamaServer(config, label=log_label("p", slot_case.case_id, label_suffix))
    with server as client:
        prime_response = client.completion(
            slot_case.stable_prefix,
            n_predict=args.prime_n_predict,
            temperature=args.temperature,
            cache_prompt=False,
        )
        save_response = client.save_slot(slot_filename)
    return {
        "slot_filename": slot_filename,
        "slot_path": str(slot_path),
        "slot_file_bytes": slot_path.stat().st_size if slot_path.exists() else save_response.get("n_written"),
        "slot_source_case_id": slot_case.case_id,
        "slot_source_stable_prefix_sha256": sha256_text(slot_case.stable_prefix),
        "prime_n_predict": args.prime_n_predict,
        "prime_timings": timing_record(prime_response),
        "prime_wall_ms": prime_response.get("_wall_ms"),
        "save_wall_ms": save_response.get("_wall_ms"),
        "save_response": slot_response(save_response),
        "prime_log_path": str(server.log_path) if server.log_path else None,
        "setup_wall_ms": (time.perf_counter() - setup_started) * 1000,
    }


def restore_and_complete(
    args: argparse.Namespace,
    case: ProbeCase,
    mode: str,
    cache_dir: Path,
    *,
    slot_source_case: ProbeCase,
    completion_prompt: str,
    expected_token: str,
    forbidden_tokens: list[str] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        setup = save_prefix_slot(args, slot_source_case, cache_dir, f"{mode}-{case.case_id}")
        config = llama_config_from_args(args, cache_dir)
        server = ManagedLlamaServer(config, label=log_label("c", mode, case.case_id, slot_source_case.case_id))
        with server as client:
            restore_response = client.restore_slot(setup["slot_filename"])
            response = client.completion(
                completion_prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=True,
                json_schema=ANSWER_JSON_SCHEMA,
            )
        setup.update(
            {
                "restore_wall_ms": restore_response.get("_wall_ms"),
                "restore_response": slot_response(restore_response),
                "completion_log_path": str(server.log_path) if server.log_path else None,
            }
        )
        return build_response_record(
            args,
            case,
            mode,
            completion_prompt,
            response,
            started_at=started,
            expected_token=expected_token,
            forbidden_tokens=forbidden_tokens,
            slot_source_case=slot_source_case,
            session_setup=setup,
        )
    except Exception as exc:
        return build_error_record(
            args,
            case,
            mode,
            completion_prompt,
            exc,
            started_at=started,
            expected_token=expected_token,
            slot_source_case=slot_source_case,
        )


def run_cold_full(args: argparse.Namespace, case: ProbeCase, cache_dir: Path) -> dict[str, Any]:
    prompt = case.full_prompt
    started = time.perf_counter()
    try:
        server = ManagedLlamaServer(llama_config_from_args(args, cache_dir), label=log_label("cold", case.case_id))
        with server as client:
            response = client.completion(
                prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=False,
                json_schema=ANSWER_JSON_SCHEMA,
            )
        return build_response_record(
            args,
            case,
            "cold-full",
            prompt,
            response,
            started_at=started,
            expected_token=case.secret_token,
            session_setup={"completion_log_path": str(server.log_path) if server.log_path else None},
        )
    except Exception as exc:
        return build_error_record(args, case, "cold-full", prompt, exc, started_at=started, expected_token=case.secret_token)


def run_prime_save(args: argparse.Namespace, case: ProbeCase, cache_dir: Path) -> dict[str, Any]:
    prompt = case.stable_prefix
    started = time.perf_counter()
    try:
        setup = save_prefix_slot(args, case, cache_dir, "prime-save")
        record = {
            **record_base(args, case, "prime-save", prompt, case.secret_token, slot_source_case=case),
            "scored": False,
            "response": "",
            "raw_response": "",
            "response_sha256": sha256_text(""),
            "answer_parse_error": None,
            "passed": None,
            "score": None,
            "score_details": None,
            "latency_ms": (time.perf_counter() - started) * 1000,
            "timings": {},
            "session_setup": setup,
        }
        record["failure_classification"] = classify_record(record)
        return record
    except Exception as exc:
        return build_error_record(args, case, "prime-save", prompt, exc, started_at=started, expected_token=case.secret_token, slot_source_case=case)


def run_restored_full(args: argparse.Namespace, case: ProbeCase, cache_dir: Path) -> dict[str, Any]:
    return restore_and_complete(
        args,
        case,
        "restored-full",
        cache_dir,
        slot_source_case=case,
        completion_prompt=case.full_prompt,
        expected_token=case.secret_token,
        forbidden_tokens=[],
    )


def run_perturbed_full(args: argparse.Namespace, case: ProbeCase, cache_dir: Path) -> dict[str, Any]:
    return restore_and_complete(
        args,
        case,
        "perturbed-full",
        cache_dir,
        slot_source_case=case,
        completion_prompt=case.perturbed_full_prompt,
        expected_token=case.perturbed_token,
        forbidden_tokens=[case.secret_token],
    )


def run_wrong_slot_full(args: argparse.Namespace, case: ProbeCase, wrong_slot_case: ProbeCase, cache_dir: Path) -> dict[str, Any]:
    return restore_and_complete(
        args,
        case,
        "wrong-slot-full",
        cache_dir,
        slot_source_case=wrong_slot_case,
        completion_prompt=case.full_prompt,
        expected_token=case.secret_token,
        forbidden_tokens=[wrong_slot_case.secret_token],
    )


def selected_modes(args: argparse.Namespace) -> list[str]:
    if args.mode == "all":
        return ["cold-full", "prime-save", "restored-full", "perturbed-full", "wrong-slot-full"]
    return [args.mode]


def dry_run_record(
    args: argparse.Namespace,
    case: ProbeCase,
    mode: str,
    *,
    slot_source_case: ProbeCase | None = None,
) -> dict[str, Any]:
    prompt = mode_completion_prompt(case, mode)
    expected = expected_token_for_mode(case, mode)
    base = record_base(args, case, mode, prompt, expected, slot_source_case=slot_source_case)
    if mode == "prime-save":
        record = {
            **base,
            "scored": False,
            "response": "",
            "raw_response": "",
            "response_sha256": sha256_text(""),
            "answer_parse_error": None,
            "passed": None,
            "score": None,
            "score_details": None,
            "latency_ms": 0.0,
            "timings": {},
            "session_setup": {
                "dry_run": True,
                "slot_filename": slot_filename_for(case),
                "slot_path": str(args.cache_dir / "dry-run" / slot_filename_for(case)),
                "slot_file_bytes": 1024,
                "save_response": {"n_saved": 16, "n_written": 1024},
            },
            "dry_run": True,
        }
        record["failure_classification"] = classify_record(record)
        return record

    prompt_ms_by_mode = {
        "cold-full": 20.0,
        "restored-full": 8.0,
        "perturbed-full": 19.0,
        "wrong-slot-full": 20.0,
    }
    prompt_n_by_mode = {
        "cold-full": 120,
        "restored-full": 48,
        "perturbed-full": 118,
        "wrong-slot-full": 120,
    }
    response = {"content": json.dumps({"answer": expected}), "timings": {"prompt_ms": prompt_ms_by_mode[mode], "prompt_n": prompt_n_by_mode[mode]}}
    return build_response_record(
        args,
        case,
        mode,
        prompt,
        response,
        started_at=time.perf_counter(),
        expected_token=expected,
        forbidden_tokens=[],
        slot_source_case=slot_source_case,
        session_setup={"dry_run": True},
    )


def run_case_mode(args: argparse.Namespace, cases: list[ProbeCase], index: int, mode: str) -> dict[str, Any]:
    case = cases[index]
    cache_dir = args.cache_dir / mode / case.case_id
    wrong_slot_case = cases[(index + 1) % len(cases)] if len(cases) > 1 else None
    if mode == "wrong-slot-full" and wrong_slot_case is None:
        raise ProbeError("wrong-slot-full requires at least two probe cases")
    if args.dry_run:
        return dry_run_record(args, case, mode, slot_source_case=wrong_slot_case if mode == "wrong-slot-full" else case if mode != "cold-full" else None)
    if mode == "cold-full":
        return run_cold_full(args, case, cache_dir)
    if mode == "prime-save":
        return run_prime_save(args, case, cache_dir)
    if mode == "restored-full":
        return run_restored_full(args, case, cache_dir)
    if mode == "perturbed-full":
        return run_perturbed_full(args, case, cache_dir)
    if mode == "wrong-slot-full":
        assert wrong_slot_case is not None
        return run_wrong_slot_full(args, case, wrong_slot_case, cache_dir)
    raise ProbeError(f"Unsupported mode: {mode}")


def numeric_mean(values: list[Any]) -> float | None:
    numbers = [float(value) for value in values if isinstance(value, (int, float))]
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


def timing_value(record: dict[str, Any], key: str) -> Any:
    timings = record.get("timings", {})
    if not isinstance(timings, dict):
        return None
    return timings.get(key)


def classify_case(modes: dict[str, dict[str, Any]]) -> str:
    cold_pass = modes.get("cold-full", {}).get("passed") is True
    restored_pass = modes.get("restored-full", {}).get("passed") is True
    perturbed_pass = modes.get("perturbed-full", {}).get("passed") is True
    wrong_slot_pass = modes.get("wrong-slot-full", {}).get("passed") is True
    any_runtime_error = any(row.get("error") for row in modes.values())
    if any_runtime_error:
        return "runtime_storage_issue"
    if not cold_pass:
        return "invalid_probe_cold_full_failed"
    if not restored_pass:
        return "restored_full_correctness_drift"
    if not perturbed_pass:
        return "unsafe_cache_leakage_or_protocol_drift"
    if not wrong_slot_pass:
        return "unsafe_cache_leakage_or_protocol_drift"
    cold_prompt_ms = timing_value(modes["cold-full"], "prompt_ms")
    restored_prompt_ms = timing_value(modes["restored-full"], "prompt_ms")
    cold_prompt_n = timing_value(modes["cold-full"], "prompt_n")
    restored_prompt_n = timing_value(modes["restored-full"], "prompt_n")
    if isinstance(cold_prompt_ms, (int, float)) and isinstance(restored_prompt_ms, (int, float)) and restored_prompt_ms < cold_prompt_ms:
        return "correctness_safe_with_prompt_reduction"
    if isinstance(cold_prompt_n, (int, float)) and isinstance(restored_prompt_n, (int, float)) and restored_prompt_n < cold_prompt_n:
        return "correctness_safe_with_token_accounting_evidence"
    return "correctness_safe_without_clear_prompt_reduction"


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_mode: dict[str, list[dict[str, Any]]] = {}
    by_case_records: dict[str, dict[str, dict[str, Any]]] = {}
    for record in records:
        mode = str(record["mode"])
        case_id = str(record["case_id"])
        by_mode.setdefault(mode, []).append(record)
        by_case_records.setdefault(case_id, {})[mode] = record

    mode_summary = {}
    for mode, rows in sorted(by_mode.items()):
        scored_rows = [row for row in rows if row.get("scored") is not False]
        passed = sum(1 for row in scored_rows if row.get("passed") is True)
        classifications: dict[str, int] = {}
        for row in rows:
            classification = str(row.get("failure_classification", "unknown"))
            classifications[classification] = classifications.get(classification, 0) + 1
        mode_summary[mode] = {
            "case_count": len(rows),
            "scored_count": len(scored_rows),
            "passed_count": passed,
            "pass_rate": passed / len(scored_rows) if scored_rows else None,
            "response_error_count": sum(1 for row in rows if row.get("error")),
            "answer_parse_error_count": sum(1 for row in scored_rows if row.get("answer_parse_error")),
            "mean_latency_ms": numeric_mean([row.get("latency_ms") for row in rows]),
            "mean_prompt_ms": numeric_mean([timing_value(row, "prompt_ms") for row in scored_rows]),
            "mean_prompt_n": numeric_mean([timing_value(row, "prompt_n") for row in scored_rows]),
            "failure_classifications": dict(sorted(classifications.items())),
        }

    case_summary = {}
    prompt_reduction_cases = 0
    token_reduction_cases = 0
    for case_id, modes in sorted(by_case_records.items()):
        compact_modes = {
            mode: {
                "passed": record.get("passed"),
                "score": record.get("score"),
                "scored": record.get("scored"),
                "answer_parse_error": record.get("answer_parse_error"),
                "error": record.get("error"),
                "failure_classification": record.get("failure_classification"),
                "prompt_ms": timing_value(record, "prompt_ms"),
                "prompt_n": timing_value(record, "prompt_n"),
            }
            for mode, record in sorted(modes.items())
        }
        cold = modes.get("cold-full", {})
        restored = modes.get("restored-full", {})
        cold_prompt_ms = timing_value(cold, "prompt_ms")
        restored_prompt_ms = timing_value(restored, "prompt_ms")
        cold_prompt_n = timing_value(cold, "prompt_n")
        restored_prompt_n = timing_value(restored, "prompt_n")
        prompt_ms_delta = None
        prompt_n_delta = None
        if isinstance(cold_prompt_ms, (int, float)) and isinstance(restored_prompt_ms, (int, float)):
            prompt_ms_delta = float(cold_prompt_ms) - float(restored_prompt_ms)
            if prompt_ms_delta > 0:
                prompt_reduction_cases += 1
        if isinstance(cold_prompt_n, (int, float)) and isinstance(restored_prompt_n, (int, float)):
            prompt_n_delta = float(cold_prompt_n) - float(restored_prompt_n)
            if prompt_n_delta > 0:
                token_reduction_cases += 1
        case_summary[case_id] = {
            "interpretation": classify_case(modes),
            "modes": compact_modes,
            "timing_delta": {
                "cold_minus_restored_prompt_ms": prompt_ms_delta,
                "cold_minus_restored_prompt_n": prompt_n_delta,
            },
        }

    required_modes = ["cold-full", "restored-full", "perturbed-full", "wrong-slot-full"]
    mode_all_pass = {
        mode: mode in by_mode and all(row.get("passed") is True for row in by_mode[mode] if row.get("scored") is not False)
        for mode in required_modes
    }
    correctness_controls_pass = all(mode_all_pass.values())
    cold_mean_prompt_ms = mode_summary.get("cold-full", {}).get("mean_prompt_ms")
    restored_mean_prompt_ms = mode_summary.get("restored-full", {}).get("mean_prompt_ms")
    cold_mean_prompt_n = mode_summary.get("cold-full", {}).get("mean_prompt_n")
    restored_mean_prompt_n = mode_summary.get("restored-full", {}).get("mean_prompt_n")
    mean_prompt_ms_delta = None
    mean_prompt_n_delta = None
    if isinstance(cold_mean_prompt_ms, (int, float)) and isinstance(restored_mean_prompt_ms, (int, float)):
        mean_prompt_ms_delta = float(cold_mean_prompt_ms) - float(restored_mean_prompt_ms)
    if isinstance(cold_mean_prompt_n, (int, float)) and isinstance(restored_mean_prompt_n, (int, float)):
        mean_prompt_n_delta = float(cold_mean_prompt_n) - float(restored_mean_prompt_n)
    majority_prompt_reduction = prompt_reduction_cases > (len(by_case_records) / 2)
    useful_acceleration_evidence = (mean_prompt_n_delta is not None and mean_prompt_n_delta > 0) or (
        mean_prompt_ms_delta is not None and mean_prompt_ms_delta > 0 and majority_prompt_reduction
    )
    any_runtime_error = any(row.get("error") for row in records)
    if any_runtime_error:
        overall = "runtime_failure"
    elif not mode_all_pass["cold-full"]:
        overall = "invalid_probe_cold_full_failed"
    elif not mode_all_pass["restored-full"]:
        overall = "restored_full_correctness_drift"
    elif not mode_all_pass["perturbed-full"] or not mode_all_pass["wrong-slot-full"]:
        overall = "unsafe_cache_leakage_or_protocol_drift"
    elif useful_acceleration_evidence:
        overall = "correctness_safe_with_useful_acceleration_evidence"
    else:
        overall = "correctness_safe_without_useful_acceleration_evidence"

    return {
        "by_mode": mode_summary,
        "by_case": case_summary,
        "gate": {
            "mode_all_pass": mode_all_pass,
            "correctness_and_safety_controls_pass": correctness_controls_pass,
            "prompt_reduction_cases": prompt_reduction_cases,
            "token_reduction_cases": token_reduction_cases,
            "majority_prompt_reduction": majority_prompt_reduction,
            "mean_cold_minus_restored_prompt_ms": mean_prompt_ms_delta,
            "mean_cold_minus_restored_prompt_n": mean_prompt_n_delta,
            "useful_acceleration_evidence": useful_acceleration_evidence,
            "recommend_graphwalks_follow_up": correctness_controls_pass and useful_acceleration_evidence,
            "overall_interpretation": overall,
        },
    }


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return args.output
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_slug = Path(str(args.hf_repo or args.model)).stem.replace(":", "-").replace("/", "-")
    return args.output_dir / f"{timestamp}-{model_slug}-restored-prefix-full-resend.json"


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


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    cases = parse_cases(args.cases)
    for case in cases:
        validate_case(case)
    records = []
    modes = selected_modes(args)
    for index, case in enumerate(cases):
        for mode in modes:
            print(f"[restored-prefix-full-resend] {mode}: {case.case_id}", flush=True)
            records.append(run_case_mode(args, cases, index, mode))
    return {
        "metadata": command_metadata(args),
        "cases": [asdict(case) for case in cases],
        "records": records,
        "summary": summarize(records),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe restored llama.cpp prefix slots while resending full prompts.")
    parser.add_argument("--server-bin", default="llama-server", help="llama.cpp server binary.")
    parser.add_argument("--model", type=Path, help="Path to a GGUF model. Overrides the default Gemma 4 HF repo.")
    parser.add_argument("--hf-repo", help="Hugging Face GGUF repo for llama.cpp -hf loading.")
    parser.add_argument("--cases", type=Path, help="Optional JSONL restored-prefix probe cases.")
    parser.add_argument(
        "--mode",
        choices=["all", "cold-full", "prime-save", "restored-full", "perturbed-full", "wrong-slot-full"],
        default="all",
        help="Probe mode to run.",
    )
    parser.add_argument("--ctx-size", type=int, default=32768, help="llama.cpp context size.")
    parser.add_argument("--predict", type=int, default=32, help="Generated tokens per answer.")
    parser.add_argument("--prime-n-predict", type=int, default=0, help="Generated tokens while priming stable prefix.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    parser.add_argument("--timeout", type=float, default=240.0, help="HTTP/server timeout in seconds.")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Directory for slot/log artifacts.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for probe JSON output.")
    parser.add_argument("--output", type=Path, help="Explicit output JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Write record skeletons without starting llama.cpp.")
    args = parser.parse_args(argv)
    if args.model is None:
        args.model = DEFAULT_MODEL
        if not args.hf_repo:
            args.hf_repo = DEFAULT_GEMMA4_HF_REPO
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.dry_run and not args.hf_repo and not args.model.exists():
        print(f"Model file not found: {args.model}", file=sys.stderr)
        return 2
    try:
        result = run_probe(args)
    except ProbeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote restored-prefix full-resend probe result: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
