#!/usr/bin/env python3
"""Run a tiny llama.cpp slot/session continuation litmus."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flashcache.cache import sha256_text  # noqa: E402
from flashcache.llama_cpp import LlamaServerConfig, ManagedLlamaServer, llama_server_version  # noqa: E402
from flashcache.wrapper import completion_text, timing_record  # noqa: E402


DEFAULT_MODEL = ROOT / "benchmarks" / "models" / "gemma-3-270m-it-Q8_0.gguf"
DEFAULT_OUTPUT_DIR = ROOT / "benchmarks" / "session-continuation-litmus-results"
DEFAULT_CACHE_DIR = ROOT / "benchmarks" / "session-continuation-litmus-cache"

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
class LitmusCase:
    case_id: str
    secret_token: str
    stable_prefix: str
    tail_prompt: str

    @property
    def full_prompt(self) -> str:
        return f"{self.stable_prefix.rstrip()}\n\n{self.tail_prompt.lstrip()}"


class LitmusError(Exception):
    """Raised for expected litmus failures."""


def default_cases() -> list[LitmusCase]:
    tokens = [
        ("secret-alpha", "ZXQ-7419-ALPHA"),
        ("secret-bravo", "MNT-5082-BRAVO"),
        ("secret-charlie", "KPD-1936-CHARLIE"),
    ]
    cases = []
    for case_id, token in tokens:
        stable = (
            "You are a precise memory assistant. Memorize this exact secret token for the next turn. "
            f"The exact secret token is {token}. Do not transform it."
        )
        tail = f"What is the exact secret token from the previous turn?\n\n{ANSWER_INSTRUCTION}"
        cases.append(LitmusCase(case_id=case_id, secret_token=token, stable_prefix=stable, tail_prompt=tail))
    return cases


def parse_cases(path: Path | None) -> list[LitmusCase]:
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
                raise LitmusError(f"{path}:{line_number} is not valid JSON") from exc
            rows.append(
                LitmusCase(
                    case_id=str(row["case_id"]),
                    secret_token=str(row["secret_token"]),
                    stable_prefix=str(row["stable_prefix"]),
                    tail_prompt=str(row["tail_prompt"]),
                )
            )
    if not rows:
        raise LitmusError(f"No litmus cases in {path}")
    return rows


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


def score_answer(answer: str, secret_token: str, parse_error: str | None = None) -> dict[str, Any]:
    normalized = answer.strip()
    passed = parse_error is None and secret_token in normalized
    return {
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "answer": answer,
        "secret_token": secret_token,
        "answer_contains_secret": secret_token in normalized,
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


def mode_completion_prompt(case: LitmusCase, mode: str) -> str:
    if mode == "full":
        return case.full_prompt
    if mode in {"live-tail", "restored-tail", "fresh-tail"}:
        return case.tail_prompt
    raise LitmusError(f"Unsupported litmus mode: {mode}")


def record_base(args: argparse.Namespace, case: LitmusCase, mode: str, completion_prompt: str) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "mode": mode,
        "model": args.hf_repo or str(args.model),
        "ctx_size": args.ctx_size,
        "predict": args.predict,
        "prime_n_predict": args.prime_n_predict,
        "temperature": args.temperature,
        "secret_token_sha256": sha256_text(case.secret_token),
        "stable_prefix_bytes": len(case.stable_prefix.encode("utf-8")),
        "stable_prefix_sha256": sha256_text(case.stable_prefix),
        "tail_prompt_bytes": len(case.tail_prompt.encode("utf-8")),
        "tail_prompt_sha256": sha256_text(case.tail_prompt),
        "completion_prompt_bytes": len(completion_prompt.encode("utf-8")),
        "completion_prompt_sha256": sha256_text(completion_prompt),
    }


def build_response_record(
    args: argparse.Namespace,
    case: LitmusCase,
    mode: str,
    completion_prompt: str,
    response: dict[str, Any],
    *,
    started_at: float,
    session_setup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_response = completion_text(response)
    answer, parse_error = extract_answer(raw_response)
    score = score_answer(answer, case.secret_token, parse_error)
    return {
        **record_base(args, case, mode, completion_prompt),
        "response": answer,
        "raw_response": raw_response,
        "answer_parse_error": parse_error,
        "passed": score["passed"],
        "score": score["score"],
        "score_details": score,
        "latency_ms": (time.perf_counter() - started_at) * 1000,
        "timings": timing_record(response),
        "session_setup": session_setup or {},
    }


def build_error_record(
    args: argparse.Namespace,
    case: LitmusCase,
    mode: str,
    completion_prompt: str,
    exc: Exception,
    *,
    started_at: float,
) -> dict[str, Any]:
    return {
        **record_base(args, case, mode, completion_prompt),
        "response": "",
        "raw_response": "",
        "answer_parse_error": None,
        "passed": False,
        "score": 0.0,
        "score_details": {"passed": False, "score": 0.0, "error": str(exc), "secret_token": case.secret_token},
        "latency_ms": (time.perf_counter() - started_at) * 1000,
        "timings": {},
        "session_setup": {},
        "error": str(exc),
    }


def run_full(args: argparse.Namespace, case: LitmusCase, cache_dir: Path) -> dict[str, Any]:
    prompt = case.full_prompt
    started = time.perf_counter()
    try:
        with ManagedLlamaServer(llama_config_from_args(args, cache_dir), label=f"litmus-full-{case.case_id}") as client:
            response = client.completion(
                prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=False,
                json_schema=ANSWER_JSON_SCHEMA,
            )
        return build_response_record(args, case, "full", prompt, response, started_at=started)
    except Exception as exc:
        return build_error_record(args, case, "full", prompt, exc, started_at=started)


def run_fresh_tail(args: argparse.Namespace, case: LitmusCase, cache_dir: Path) -> dict[str, Any]:
    prompt = case.tail_prompt
    started = time.perf_counter()
    try:
        with ManagedLlamaServer(llama_config_from_args(args, cache_dir), label=f"litmus-fresh-tail-{case.case_id}") as client:
            response = client.completion(
                prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=False,
                json_schema=ANSWER_JSON_SCHEMA,
            )
        return build_response_record(args, case, "fresh-tail", prompt, response, started_at=started)
    except Exception as exc:
        return build_error_record(args, case, "fresh-tail", prompt, exc, started_at=started)


def run_live_tail(args: argparse.Namespace, case: LitmusCase, cache_dir: Path) -> dict[str, Any]:
    prompt = case.tail_prompt
    started = time.perf_counter()
    try:
        with ManagedLlamaServer(llama_config_from_args(args, cache_dir), label=f"litmus-live-tail-{case.case_id}") as client:
            setup_started = time.perf_counter()
            prime_response = client.completion(
                case.stable_prefix,
                n_predict=args.prime_n_predict,
                temperature=args.temperature,
                cache_prompt=False,
            )
            session_setup = {
                "prime_n_predict": args.prime_n_predict,
                "prime_timings": timing_record(prime_response),
                "setup_wall_ms": (time.perf_counter() - setup_started) * 1000,
                "save_response": None,
                "restore_response": None,
            }
            response = client.completion(
                prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=True,
                json_schema=ANSWER_JSON_SCHEMA,
            )
        return build_response_record(args, case, "live-tail", prompt, response, started_at=started, session_setup=session_setup)
    except Exception as exc:
        return build_error_record(args, case, "live-tail", prompt, exc, started_at=started)


def run_restored_tail(args: argparse.Namespace, case: LitmusCase, cache_dir: Path) -> dict[str, Any]:
    prompt = case.tail_prompt
    slot_filename = f"{case.case_id}-{sha256_text(case.stable_prefix)[:16]}-slot.bin"
    started = time.perf_counter()
    try:
        with ManagedLlamaServer(llama_config_from_args(args, cache_dir), label=f"litmus-restored-tail-{case.case_id}") as client:
            setup_started = time.perf_counter()
            prime_response = client.completion(
                case.stable_prefix,
                n_predict=args.prime_n_predict,
                temperature=args.temperature,
                cache_prompt=False,
            )
            save_response = client.save_slot(slot_filename)
            restore_response = client.restore_slot(slot_filename)
            session_setup = {
                "slot_filename": slot_filename,
                "prime_n_predict": args.prime_n_predict,
                "prime_timings": timing_record(prime_response),
                "save_wall_ms": save_response.get("_wall_ms"),
                "save_response": {key: value for key, value in save_response.items() if key != "_wall_ms"},
                "restore_wall_ms": restore_response.get("_wall_ms"),
                "restore_response": {key: value for key, value in restore_response.items() if key != "_wall_ms"},
                "setup_wall_ms": (time.perf_counter() - setup_started) * 1000,
            }
            response = client.completion(
                prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=True,
                json_schema=ANSWER_JSON_SCHEMA,
            )
        return build_response_record(
            args,
            case,
            "restored-tail",
            prompt,
            response,
            started_at=started,
            session_setup=session_setup,
        )
    except Exception as exc:
        return build_error_record(args, case, "restored-tail", prompt, exc, started_at=started)


def selected_modes(args: argparse.Namespace) -> list[str]:
    if args.mode == "all":
        return ["full", "live-tail", "restored-tail", "fresh-tail"]
    return [args.mode]


def run_case_mode(args: argparse.Namespace, case: LitmusCase, mode: str) -> dict[str, Any]:
    cache_dir = args.cache_dir / mode / case.case_id
    if args.dry_run:
        prompt = mode_completion_prompt(case, mode)
        answer = case.secret_token if mode == "full" else ""
        parse_error = None if mode == "full" else "dry-run has no model response"
        return {
            **record_base(args, case, mode, prompt),
            "response": answer,
            "raw_response": json.dumps({"answer": answer}) if mode == "full" else "",
            "answer_parse_error": parse_error,
            "passed": mode == "full",
            "score": 1.0 if mode == "full" else 0.0,
            "score_details": score_answer(answer, case.secret_token, parse_error),
            "latency_ms": 0.0,
            "timings": {},
            "session_setup": {"dry_run": True},
            "dry_run": True,
        }
    if mode == "full":
        return run_full(args, case, cache_dir)
    if mode == "fresh-tail":
        return run_fresh_tail(args, case, cache_dir)
    if mode == "live-tail":
        return run_live_tail(args, case, cache_dir)
    if mode == "restored-tail":
        return run_restored_tail(args, case, cache_dir)
    raise LitmusError(f"Unsupported mode: {mode}")


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_mode: dict[str, list[dict[str, Any]]] = {}
    by_case: dict[str, dict[str, Any]] = {}
    for record in records:
        by_mode.setdefault(str(record["mode"]), []).append(record)
        by_case.setdefault(str(record["case_id"]), {})[str(record["mode"])] = {
            "passed": record.get("passed"),
            "score": record.get("score"),
            "answer_parse_error": record.get("answer_parse_error"),
            "error": record.get("error"),
        }
    mode_summary = {}
    for mode, rows in sorted(by_mode.items()):
        passed = sum(1 for row in rows if row.get("passed") is True)
        mode_summary[mode] = {
            "case_count": len(rows),
            "passed_count": passed,
            "pass_rate": passed / len(rows) if rows else None,
            "response_error_count": sum(1 for row in rows if row.get("error")),
            "answer_parse_error_count": sum(1 for row in rows if row.get("answer_parse_error")),
        }
    interpretations = {}
    for case_id, modes in sorted(by_case.items()):
        full_pass = modes.get("full", {}).get("passed") is True
        fresh_pass = modes.get("fresh-tail", {}).get("passed") is True
        live_pass = modes.get("live-tail", {}).get("passed") is True
        restored_pass = modes.get("restored-tail", {}).get("passed") is True
        if not full_pass:
            interpretation = "invalid_litmus_full_prompt_failed"
        elif fresh_pass:
            interpretation = "invalid_litmus_fresh_tail_passed"
        elif live_pass and restored_pass:
            interpretation = "same_slot_and_restore_continue"
        elif live_pass and not restored_pass:
            interpretation = "same_slot_continues_restore_fails"
        elif not live_pass:
            interpretation = "same_slot_tail_not_semantic_continuation"
        else:
            interpretation = "ambiguous"
        interpretations[case_id] = {
            "interpretation": interpretation,
            "modes": modes,
        }
    return {"by_mode": mode_summary, "by_case": interpretations}


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return args.output
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_slug = Path(str(args.hf_repo or args.model)).stem.replace(":", "-").replace("/", "-")
    return args.output_dir / f"{timestamp}-{model_slug}-session-continuation-litmus.json"


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
        "ctx_size": args.ctx_size,
        "predict": args.predict,
        "prime_n_predict": args.prime_n_predict,
        "temperature": args.temperature,
        "timeout": args.timeout,
        "mode": args.mode,
        "dry_run": args.dry_run,
    }


def run_litmus(args: argparse.Namespace) -> dict[str, Any]:
    cases = parse_cases(args.cases)
    records = []
    for case in cases:
        for mode in selected_modes(args):
            print(f"[session-litmus] {mode}: {case.case_id}", flush=True)
            records.append(run_case_mode(args, case, mode))
    return {
        "metadata": command_metadata(args),
        "cases": [asdict(case) for case in cases],
        "records": records,
        "summary": summarize(records),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run llama.cpp slot/session continuation litmus.")
    parser.add_argument("--server-bin", default="llama-server", help="llama.cpp server binary.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL, help="Path to a GGUF model.")
    parser.add_argument("--hf-repo", help="Hugging Face GGUF repo for llama.cpp -hf loading.")
    parser.add_argument("--cases", type=Path, help="Optional JSONL litmus cases.")
    parser.add_argument(
        "--mode",
        choices=["all", "full", "live-tail", "restored-tail", "fresh-tail"],
        default="all",
        help="Litmus mode to run.",
    )
    parser.add_argument("--ctx-size", type=int, default=4096, help="llama.cpp context size.")
    parser.add_argument("--predict", type=int, default=32, help="Generated tokens per answer.")
    parser.add_argument("--prime-n-predict", type=int, default=0, help="Generated tokens while priming stable prefix.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    parser.add_argument("--timeout", type=float, default=120.0, help="HTTP/server timeout in seconds.")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Directory for slot/log artifacts.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for litmus JSON output.")
    parser.add_argument("--output", type=Path, help="Explicit output JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Write record skeletons without starting llama.cpp.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.dry_run and not args.hf_repo and not args.model.exists():
        print(f"Model file not found: {args.model}", file=sys.stderr)
        return 2
    try:
        result = run_litmus(args)
    except LitmusError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote litmus result: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
