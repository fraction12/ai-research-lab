#!/usr/bin/env python3
"""Build and score Flashcache correctness eval cases."""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DEFAULT_CASE_DIR = ROOT / "benchmarks" / "correctness-eval-inputs"
DEFAULT_RESULT_DIR = ROOT / "benchmarks" / "correctness-eval-results"
DEFAULT_RUN_CACHE_DIR = ROOT / "benchmarks" / "correctness-eval-cache"
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from flashcache.cache import sha256_text  # noqa: E402
from flashcache.llama_cpp import LlamaServerConfig, ManagedLlamaServer  # noqa: E402
from flashcache.wrapper import completion_text, timing_record  # noqa: E402

IFEVAL_STABLE_PREFIX = (
    "You are an instruction-following assistant. Answer the user's request exactly, "
    "including all formatting, wording, and constraint details."
)

ANSWER_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {
            "type": "string",
            "description": "The final answer only. No reasoning, analysis, or extra wrapper text.",
        }
    },
    "required": ["answer"],
    "additionalProperties": False,
}

JSON_ANSWER_INSTRUCTIONS = (
    "Return only a JSON object with this exact shape: {\"answer\": \"...\"}. "
    "Put the final answer in the answer string. Do not include reasoning, markdown, or extra keys."
)

IFEVAL_EASY_INSTRUCTION_IDS = {
    "detectable_content:number_placeholders",
    "detectable_format:json_format",
    "detectable_format:number_bullet_lists",
    "keywords:forbidden_words",
    "keywords:frequency",
    "length_constraints:number_words",
    "punctuation:no_comma",
    "punctuation:no_period",
    "startend:end_checker",
}


@dataclass(frozen=True)
class EvalDataset:
    id: str
    hf_repo: str
    split: str
    license: str
    task_family: str
    scoring: str
    url: str
    description: str


@dataclass
class ScoreResult:
    score: float | None
    passed: bool | None
    metrics: dict[str, Any]
    unsupported_checks: list[str]


@dataclass(frozen=True)
class CandidateDatasetSpec:
    dataset_id: str
    limit: int


DATASETS: dict[str, EvalDataset] = {
    "ifeval": EvalDataset(
        id="ifeval",
        hf_repo="google/IFEval",
        split="train",
        license="apache-2.0",
        task_family="instruction-following",
        scoring="supported deterministic IFEval instruction checks",
        url="https://huggingface.co/datasets/google/IFEval",
        description="Instruction-following prompts with verifiable constraint metadata.",
    ),
    "mrcr": EvalDataset(
        id="mrcr",
        hf_repo="openai/mrcr",
        split="train",
        license="mit",
        task_family="long-context multi-turn retrieval",
        scoring="sequence similarity against reference answer",
        url="https://huggingface.co/datasets/openai/mrcr",
        description="Long synthetic conversations with hidden repeated asks and a reference response.",
    ),
    "graphwalks": EvalDataset(
        id="graphwalks",
        hf_repo="openai/graphwalks",
        split="train",
        license="mit",
        task_family="long-context graph reasoning",
        scoring="node-set precision/recall/F1",
        url="https://huggingface.co/datasets/openai/graphwalks",
        description="Directed graph prompts with exact node-set answers.",
    ),
}


class CorrectnessEvalError(Exception):
    """Raised for expected correctness-eval failures."""


def combine_prompt(stable_prefix: str, tail_prompt: str) -> str:
    stable = stable_prefix.rstrip()
    tail = tail_prompt.lstrip()
    if not stable:
        return tail
    if not tail:
        return stable
    return f"{stable}\n\n{tail}"


def messages_to_text(messages: list[dict[str, Any]]) -> str:
    parts = []
    for message in messages:
        role = str(message.get("role", "message")).upper()
        content = str(message.get("content", ""))
        parts.append(f"{role}:\n{content}")
    return "\n\n".join(parts)


def case_id(dataset_id: str, source_id: str | int) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(source_id)).strip("-")
    return f"{dataset_id}-{cleaned or 'row'}"


def build_ifeval_case(row: dict[str, Any], index: int) -> dict[str, Any]:
    source_id = row.get("key", index)
    tail_prompt = str(row["prompt"])
    stable_prefix = IFEVAL_STABLE_PREFIX
    instruction_ids = row.get("instruction_id_list") or []
    kwargs = row.get("kwargs") or []
    return {
        "case_id": case_id("ifeval", source_id),
        "dataset_id": "ifeval",
        "source_dataset": DATASETS["ifeval"].hf_repo,
        "source_id": source_id,
        "stable_prefix": stable_prefix,
        "tail_prompt": tail_prompt,
        "full_prompt": combine_prompt(stable_prefix, tail_prompt),
        "scoring": {"type": "ifeval"},
        "reference": {
            "instruction_id_list": list(instruction_ids),
            "kwargs": list(kwargs),
        },
    }


def build_mrcr_case(row: dict[str, Any], index: int) -> dict[str, Any]:
    source_id = row.get("id", index)
    try:
        messages = json.loads(str(row["prompt"]))
    except json.JSONDecodeError as exc:
        raise CorrectnessEvalError(f"MRCR row {source_id} prompt is not valid JSON messages") from exc
    if not isinstance(messages, list) or not messages:
        raise CorrectnessEvalError(f"MRCR row {source_id} does not contain chat messages")

    stable_prefix = messages_to_text(messages[:-1])
    tail_prompt = messages_to_text(messages[-1:])
    return {
        "case_id": case_id("mrcr", source_id),
        "dataset_id": "mrcr",
        "source_dataset": DATASETS["mrcr"].hf_repo,
        "source_id": source_id,
        "stable_prefix": stable_prefix,
        "tail_prompt": tail_prompt,
        "full_prompt": combine_prompt(stable_prefix, tail_prompt),
        "scoring": {"type": "mrcr"},
        "reference": {
            "answer": str(row.get("answer", "")),
            "random_string_to_prepend": str(row.get("random_string_to_prepend", "")),
            "n_needles": row.get("n_needles"),
            "desired_msg_index": row.get("desired_msg_index"),
            "total_messages": row.get("total_messages"),
        },
    }


def split_graphwalks_prompt(prompt: str) -> tuple[str, str]:
    marker = "\nOperation:"
    index = prompt.rfind(marker)
    if index == -1:
        return "", prompt
    return prompt[:index].rstrip(), prompt[index + 1 :].lstrip()


def build_graphwalks_case(row: dict[str, Any], index: int) -> dict[str, Any]:
    source_id = row.get("id", index)
    stable_prefix, tail_prompt = split_graphwalks_prompt(str(row["prompt"]))
    return {
        "case_id": case_id("graphwalks", source_id),
        "dataset_id": "graphwalks",
        "source_dataset": DATASETS["graphwalks"].hf_repo,
        "source_id": source_id,
        "stable_prefix": stable_prefix,
        "tail_prompt": tail_prompt,
        "full_prompt": combine_prompt(stable_prefix, tail_prompt),
        "scoring": {"type": "graphwalks"},
        "reference": {
            "answer_nodes": list(row.get("answer_nodes", [])),
            "problem_type": row.get("problem_type"),
            "prompt_chars": row.get("prompt_chars"),
        },
    }


def build_case(dataset_id: str, row: dict[str, Any], index: int = 0) -> dict[str, Any]:
    if dataset_id == "ifeval":
        return build_ifeval_case(row, index)
    if dataset_id == "mrcr":
        return build_mrcr_case(row, index)
    if dataset_id == "graphwalks":
        return build_graphwalks_case(row, index)
    raise CorrectnessEvalError(f"Unsupported dataset id: {dataset_id}")


def prompt_chars(dataset_id: str, row: dict[str, Any]) -> int:
    if dataset_id in {"ifeval", "mrcr", "graphwalks"}:
        return len(str(row.get("prompt", "")).encode("utf-8"))
    return 0


def first_kwargs(kwargs: Any) -> dict[str, Any]:
    if isinstance(kwargs, list) and kwargs and isinstance(kwargs[0], dict):
        return kwargs[0]
    return {}


def is_easy_ifeval_row(row: dict[str, Any]) -> bool:
    instruction_ids = list(row.get("instruction_id_list") or [])
    if len(instruction_ids) != 1 or str(instruction_ids[0]) not in IFEVAL_EASY_INSTRUCTION_IDS:
        return False

    instruction_id = str(instruction_ids[0])
    params = first_kwargs(row.get("kwargs"))
    if instruction_id == "length_constraints:number_words":
        expected = params.get("num_words")
        return isinstance(expected, int) and expected <= 80

    if instruction_id == "detectable_format:number_bullet_lists":
        expected = params.get("num_bullets")
        return isinstance(expected, int) and expected <= 5

    if instruction_id == "keywords:forbidden_words":
        forbidden_words = params.get("forbidden_words")
        return isinstance(forbidden_words, list) and len(forbidden_words) <= 5

    if instruction_id == "keywords:frequency":
        keyword = params.get("keyword")
        expected = params.get("frequency")
        return isinstance(keyword, str) and isinstance(expected, int) and expected <= 5

    if instruction_id == "detectable_content:number_placeholders":
        expected = params.get("num_placeholders")
        return isinstance(expected, int) and expected <= 5

    if instruction_id == "startend:end_checker":
        end_phrase = params.get("end_phrase")
        return isinstance(end_phrase, str) and len(end_phrase) <= 80

    return True


def candidate_row_filter(dataset_id: str, profile: str) -> Callable[[dict[str, Any]], bool] | None:
    if profile == "default":
        return None
    if profile == "easy" and dataset_id == "ifeval":
        return is_easy_ifeval_row
    if profile == "easy":
        return None
    raise CorrectnessEvalError(f"Unsupported candidate profile: {profile}")


def load_remote_rows(
    dataset_id: str,
    *,
    limit: int,
    offset: int = 0,
    max_prompt_chars: int | None = None,
    streaming: bool = True,
    row_filter: Callable[[dict[str, Any]], bool] | None = None,
) -> list[dict[str, Any]]:
    dataset = DATASETS[dataset_id]
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise CorrectnessEvalError(
            "Sampling Hugging Face rows requires the optional 'datasets' package. "
            "Install requirements-dev.txt or run: python3 -m pip install datasets"
        ) from exc

    loaded = load_dataset(dataset.hf_repo, split=dataset.split, streaming=streaming)
    rows = []
    seen = 0
    for row in loaded:
        row_dict = dict(row)
        if max_prompt_chars is not None and prompt_chars(dataset_id, row_dict) > max_prompt_chars:
            continue
        if row_filter is not None and not row_filter(row_dict):
            continue
        if seen < offset:
            seen += 1
            continue
        rows.append(row_dict)
        if len(rows) >= limit:
            break
    return rows


def parse_candidate_mix(raw_mix: str) -> list[CandidateDatasetSpec]:
    specs = []
    seen = set()
    for raw_part in raw_mix.split(","):
        part = raw_part.strip()
        if not part:
            continue
        if ":" not in part:
            raise CorrectnessEvalError(f"Candidate mix item must use DATASET:COUNT format: {part}")
        dataset_id, raw_limit = [value.strip() for value in part.split(":", 1)]
        if dataset_id not in DATASETS:
            raise CorrectnessEvalError(f"Unsupported dataset in candidate mix: {dataset_id}")
        if dataset_id in seen:
            raise CorrectnessEvalError(f"Duplicate dataset in candidate mix: {dataset_id}")
        try:
            limit = int(raw_limit)
        except ValueError as exc:
            raise CorrectnessEvalError(f"Candidate count must be an integer for {dataset_id}: {raw_limit}") from exc
        if limit <= 0:
            raise CorrectnessEvalError(f"Candidate count must be positive for {dataset_id}: {limit}")
        specs.append(CandidateDatasetSpec(dataset_id=dataset_id, limit=limit))
        seen.add(dataset_id)
    if not specs:
        raise CorrectnessEvalError("Candidate mix must include at least one DATASET:COUNT item")
    return specs


def candidate_mix_slug(specs: list[CandidateDatasetSpec], profile: str) -> str:
    parts = [f"{spec.dataset_id}-{spec.limit}" for spec in specs]
    return f"{profile}-" + "-".join(parts)


def attach_candidate_metadata(
    case: dict[str, Any],
    *,
    args: argparse.Namespace,
    spec: CandidateDatasetSpec,
    sample_index: int,
) -> dict[str, Any]:
    enriched = dict(case)
    enriched["candidate_builder"] = {
        "mix": args.mix,
        "dataset_id": spec.dataset_id,
        "requested_count": spec.limit,
        "profile": args.profile,
        "dataset_offset": args.offset,
        "sample_index": sample_index,
        "max_prompt_chars": args.max_prompt_chars,
        "streaming": not args.no_streaming,
    }
    return enriched


def default_candidate_output_path(output_dir: Path, specs: list[CandidateDatasetSpec], profile: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return output_dir / f"{candidate_mix_slug(specs, profile)}-candidates-{timestamp}.jsonl"


def write_jsonl(records: Iterable[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            json.dump(record, handle, sort_keys=True)
            handle.write("\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise CorrectnessEvalError(f"{path}:{line_number} is not valid JSON") from exc
            if not isinstance(record, dict):
                raise CorrectnessEvalError(f"{path}:{line_number} is not a JSON object")
            records.append(record)
    return records


def compare_relation(actual: int, expected: int, relation: str | None) -> bool:
    normalized = (relation or "exactly").replace("_", " ").lower()
    if normalized in {"at least", "minimum", "min"}:
        return actual >= expected
    if normalized in {"at most", "maximum", "max"}:
        return actual <= expected
    if normalized in {"less than"}:
        return actual < expected
    if normalized in {"more than", "greater than"}:
        return actual > expected
    return actual == expected


def count_words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def check_ifeval_instruction(instruction_id: str, params: dict[str, Any], response: str) -> tuple[bool | None, dict[str, Any]]:
    if instruction_id == "punctuation:no_comma":
        return "," not in response, {"comma_count": response.count(",")}

    if instruction_id == "punctuation:no_period":
        return "." not in response, {"period_count": response.count(".")}

    if instruction_id == "length_constraints:number_words":
        expected = params.get("num_words")
        if not isinstance(expected, int):
            return None, {"reason": "missing num_words"}
        actual = count_words(response)
        return compare_relation(actual, expected, params.get("relation")), {"word_count": actual, "expected": expected}

    if instruction_id == "detectable_content:number_placeholders":
        expected = params.get("num_placeholders")
        if not isinstance(expected, int):
            return None, {"reason": "missing num_placeholders"}
        actual = len(re.findall(r"\[[^\[\]]+\]", response))
        return compare_relation(actual, expected, params.get("relation")), {
            "placeholder_count": actual,
            "expected": expected,
        }

    if instruction_id == "keywords:forbidden_words":
        forbidden_words = params.get("forbidden_words")
        if not isinstance(forbidden_words, list):
            return None, {"reason": "missing forbidden_words"}
        lowered = response.lower()
        found = [str(word) for word in forbidden_words if str(word).lower() in lowered]
        return not found, {"found_forbidden_words": found}

    if instruction_id == "keywords:frequency":
        keyword = params.get("keyword")
        expected = params.get("frequency")
        if not isinstance(keyword, str) or not isinstance(expected, int):
            return None, {"reason": "missing keyword or frequency"}
        actual = len(re.findall(rf"\b{re.escape(keyword)}\b", response, flags=re.IGNORECASE))
        return compare_relation(actual, expected, params.get("relation")), {
            "keyword": keyword,
            "frequency": actual,
            "expected": expected,
        }

    if instruction_id == "startend:end_checker":
        end_phrase = params.get("end_phrase")
        if not isinstance(end_phrase, str):
            return None, {"reason": "missing end_phrase"}
        return response.rstrip().endswith(end_phrase), {"end_phrase": end_phrase}

    if instruction_id == "detectable_format:json_format":
        try:
            json.loads(response)
        except json.JSONDecodeError:
            return False, {"json_parseable": False}
        return True, {"json_parseable": True}

    if instruction_id == "detectable_format:number_bullet_lists":
        expected = params.get("num_bullets")
        if not isinstance(expected, int):
            return None, {"reason": "missing num_bullets"}
        actual = len(re.findall(r"(?m)^\s*[-*]\s+\S+", response))
        return compare_relation(actual, expected, params.get("relation")), {"bullet_count": actual, "expected": expected}

    return None, {"reason": "unsupported instruction"}


def score_ifeval(case: dict[str, Any], response: str) -> ScoreResult:
    reference = case.get("reference", {})
    instruction_ids = list(reference.get("instruction_id_list", []))
    kwargs = list(reference.get("kwargs", []))
    checks = []
    unsupported = []
    passed_count = 0
    supported_count = 0
    for index, instruction_id in enumerate(instruction_ids):
        params = kwargs[index] if index < len(kwargs) and isinstance(kwargs[index], dict) else {}
        passed, metrics = check_ifeval_instruction(str(instruction_id), params, response)
        checks.append({"instruction_id": instruction_id, "passed": passed, "metrics": metrics})
        if passed is None:
            unsupported.append(str(instruction_id))
            continue
        supported_count += 1
        passed_count += 1 if passed else 0

    score = passed_count / supported_count if supported_count else None
    return ScoreResult(
        score=score,
        passed=(score == 1.0) if score is not None else None,
        metrics={
            "supported_instruction_count": supported_count,
            "passed_instruction_count": passed_count,
            "total_instruction_count": len(instruction_ids),
            "checks": checks,
        },
        unsupported_checks=unsupported,
    )


def without_prefix(text: str, prefix: str) -> str:
    return text[len(prefix) :] if prefix and text.startswith(prefix) else text


def score_mrcr(case: dict[str, Any], response: str) -> ScoreResult:
    reference = case.get("reference", {})
    answer = str(reference.get("answer", ""))
    prefix = str(reference.get("random_string_to_prepend", ""))
    cleaned_response = without_prefix(response, prefix).strip()
    cleaned_answer = without_prefix(answer, prefix).strip()
    similarity = SequenceMatcher(None, cleaned_response, cleaned_answer).ratio()
    return ScoreResult(
        score=similarity,
        passed=similarity >= 0.8,
        metrics={"similarity": similarity},
        unsupported_checks=[],
    )


def parse_node_set(response: str) -> set[str]:
    bracket_match = re.search(r"\[[^\]]*\]", response, flags=re.DOTALL)
    text = bracket_match.group(0) if bracket_match else response.strip()
    try:
        parsed = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        parsed = None
    if isinstance(parsed, list):
        return {str(item) for item in parsed}
    if text.strip() == "[]":
        return set()
    inner = text.strip().strip("[]")
    if not inner:
        return set()
    return {token.strip().strip("\"'") for token in re.split(r"[, \n\t]+", inner) if token.strip().strip("\"'")}


def score_graphwalks(case: dict[str, Any], response: str) -> ScoreResult:
    truth = {str(item) for item in case.get("reference", {}).get("answer_nodes", [])}
    predicted = parse_node_set(response)
    overlap = truth & predicted
    precision = len(overlap) / len(predicted) if predicted else (1.0 if not truth else 0.0)
    recall = len(overlap) / len(truth) if truth else (1.0 if not predicted else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return ScoreResult(
        score=f1,
        passed=f1 == 1.0,
        metrics={
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "predicted_nodes": sorted(predicted),
            "answer_nodes": sorted(truth),
        },
        unsupported_checks=[],
    )


def score_response(case: dict[str, Any], response: str) -> ScoreResult:
    scoring_type = case.get("scoring", {}).get("type")
    if scoring_type == "ifeval":
        return score_ifeval(case, response)
    if scoring_type == "mrcr":
        return score_mrcr(case, response)
    if scoring_type == "graphwalks":
        return score_graphwalks(case, response)
    raise CorrectnessEvalError(f"Unsupported scoring type: {scoring_type}")


def score_response_record(case: dict[str, Any], response_record: dict[str, Any]) -> ScoreResult:
    parse_error = response_record.get("answer_parse_error")
    if parse_error:
        return ScoreResult(
            score=0.0,
            passed=False,
            metrics={"answer_parse_error": parse_error},
            unsupported_checks=[],
        )
    return score_response(case, str(response_record.get("response", "")))


def aggregate_numeric_scores(case_results: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    scores = []
    passed = 0
    present = 0
    for result in case_results:
        score = result.get("scores", {}).get(mode)
        if not isinstance(score, dict):
            continue
        present += 1
        if isinstance(score.get("score"), (int, float)):
            scores.append(float(score["score"]))
        if score.get("passed") is True:
            passed += 1
    return {
        "case_count": present,
        "numeric_score_count": len(scores),
        "mean_score": sum(scores) / len(scores) if scores else None,
        "pass_rate": passed / present if present else None,
    }


def score_response_pairs(cases: list[dict[str, Any]], responses: list[dict[str, Any]]) -> dict[str, Any]:
    responses_by_case: dict[str, dict[str, dict[str, Any]]] = {}
    for response in responses:
        case_key = str(response.get("case_id", ""))
        mode = str(response.get("mode", ""))
        if not case_key or not mode:
            continue
        responses_by_case.setdefault(case_key, {})[mode] = response

    case_results = []
    for case in cases:
        case_key = str(case["case_id"])
        mode_scores = {}
        mode_latency = {}
        unsupported = {}
        for mode, response_record in sorted(responses_by_case.get(case_key, {}).items()):
            scored = score_response_record(case, response_record)
            mode_scores[mode] = asdict(scored)
            if response_record.get("latency_ms") is not None:
                mode_latency[mode] = response_record.get("latency_ms")
            if scored.unsupported_checks:
                unsupported[mode] = scored.unsupported_checks

        full_score = mode_scores.get("full", {}).get("score")
        tail_score = mode_scores.get("session-tail", {}).get("score")
        score_delta = None
        if isinstance(full_score, (int, float)) and isinstance(tail_score, (int, float)):
            score_delta = float(tail_score) - float(full_score)

        case_results.append(
            {
                "case_id": case_key,
                "dataset_id": case["dataset_id"],
                "source_id": case.get("source_id"),
                "scores": mode_scores,
                "latency_ms": mode_latency,
                "session_tail_minus_full_score": score_delta,
                "unsupported_checks": unsupported,
            }
        )

    modes = sorted({mode for result in case_results for mode in result["scores"]})
    return {
        "metadata": {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "case_count": len(cases),
            "response_count": len(responses),
            "modes": modes,
        },
        "summary": {mode: aggregate_numeric_scores(case_results, mode) for mode in modes},
        "cases": case_results,
    }


def selected_run_modes(raw_mode: str) -> list[str]:
    if raw_mode == "both":
        return ["full", "session-tail"]
    if raw_mode in {"full", "session-tail"}:
        return [raw_mode]
    raise CorrectnessEvalError(f"Unsupported run mode: {raw_mode}")


def json_schema_for_protocol(protocol: str) -> dict[str, Any] | None:
    if protocol == "json-answer":
        return ANSWER_JSON_SCHEMA
    if protocol == "raw":
        return None
    raise CorrectnessEvalError(f"Unsupported answer protocol: {protocol}")


def protocol_prefix_text(protocol: str) -> str:
    if protocol == "json-answer":
        return JSON_ANSWER_INSTRUCTIONS
    if protocol == "raw":
        return ""
    raise CorrectnessEvalError(f"Unsupported answer protocol: {protocol}")


def answer_hint_for_case(case: dict[str, Any], protocol: str) -> tuple[str | None, str]:
    if protocol != "json-answer":
        return None, ""

    dataset_id = str(case.get("dataset_id", ""))
    if dataset_id == "graphwalks":
        return (
            "graphwalks-node-list",
            "For this GraphWalks task, the answer string must contain only a JSON-style list of node ids, "
            "for example [\"node_a\", \"node_b\"]. Do not include labels or explanation.",
        )

    if dataset_id == "mrcr":
        return (
            "mrcr-exact-text",
            "For this MRCR task, the answer string must contain only the exact requested text, including any "
            "required prefix if the prompt asks for one. Do not summarize or explain.",
        )

    if dataset_id == "ifeval":
        return (
            "ifeval-final-answer",
            "For this IFEval task, the answer string must contain only the final user-facing answer that obeys "
            "every requested constraint. If the user asks for JSON or bullets, put that format inside the string.",
        )

    return "generic-final-answer", "The answer string must contain only the final answer expected by the task."


def answer_hint_id_for_case(case: dict[str, Any], protocol: str) -> str | None:
    hint_id, _text = answer_hint_for_case(case, protocol)
    return hint_id


def apply_protocol_to_prompt(prompt: str, protocol: str, case: dict[str, Any] | None = None) -> str:
    instructions = protocol_prefix_text(protocol)
    if case is not None:
        _hint_id, hint_text = answer_hint_for_case(case, protocol)
        if hint_text:
            instructions = combine_prompt(instructions, hint_text)
    if not instructions:
        return prompt
    return combine_prompt(instructions, prompt)


def protocol_case_parts(case: dict[str, Any], protocol: str) -> tuple[str, str, str]:
    if protocol == "raw":
        stable_prefix = str(case.get("stable_prefix", ""))
        tail_prompt = str(case["tail_prompt"])
        return stable_prefix, tail_prompt, str(case["full_prompt"])
    stable_prefix = apply_protocol_to_prompt(str(case.get("stable_prefix", "")), protocol, case)
    tail_prompt = str(case["tail_prompt"])
    full_prompt = combine_prompt(stable_prefix, tail_prompt)
    return stable_prefix, tail_prompt, full_prompt


def extract_protocol_response(raw_response: str, protocol: str) -> tuple[str, str | None]:
    if protocol == "raw":
        return raw_response, None
    if protocol != "json-answer":
        raise CorrectnessEvalError(f"Unsupported answer protocol: {protocol}")
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        return raw_response, f"invalid JSON answer object: {exc}"
    if not isinstance(parsed, dict):
        return raw_response, "JSON answer output is not an object"
    answer = parsed.get("answer")
    if not isinstance(answer, str):
        return raw_response, "JSON answer output is missing string field 'answer'"
    return answer, None


def case_slug(case: dict[str, Any]) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", str(case.get("case_id", "case"))).strip("-") or "case"


def response_output_path(cases_path: Path, mode: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    mode_slug = mode.replace("-", "_")
    return output_dir / f"{cases_path.stem}-{mode_slug}-responses-{timestamp}.jsonl"


def default_score_output_path(responses_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{responses_path.stem}-scores.json"


def ladder_paths(output_dir: Path, label: str) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    return {
        "full_responses": output_dir / f"{label}-full-responses.jsonl",
        "full_scores": output_dir / f"{label}-full-scores.json",
        "selected_cases": output_dir / f"{label}-selected-cases.jsonl",
        "session_tail_responses": output_dir / f"{label}-session-tail-responses.jsonl",
        "parity_responses": output_dir / f"{label}-parity-responses.jsonl",
        "parity_scores": output_dir / f"{label}-parity-scores.json",
        "report": output_dir / f"{label}-ladder-report.json",
    }


def default_ladder_label(cases_path: Path) -> str:
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{cases_path.stem}-baseline-pass-{timestamp}"


def selected_case_ids(score_result: dict[str, Any], *, mode: str = "full", min_score: float = 1.0) -> list[str]:
    selected = []
    for case_result in score_result.get("cases", []):
        score = case_result.get("scores", {}).get(mode, {}).get("score")
        if isinstance(score, (int, float)) and float(score) >= min_score:
            selected.append(str(case_result["case_id"]))
    return selected


def filter_cases_by_id(cases: list[dict[str, Any]], case_ids: Iterable[str]) -> list[dict[str, Any]]:
    selected = set(case_ids)
    return [case for case in cases if str(case.get("case_id")) in selected]


def filter_responses_by_id(responses: list[dict[str, Any]], case_ids: Iterable[str], *, mode: str | None = None) -> list[dict[str, Any]]:
    selected = set(case_ids)
    return [
        response
        for response in responses
        if str(response.get("case_id")) in selected and (mode is None or response.get("mode") == mode)
    ]


def prompt_timing_index(responses: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(response.get("case_id")), str(response.get("mode"))): response
        for response in responses
    }


def build_ladder_report(
    *,
    args: argparse.Namespace,
    paths: dict[str, Path],
    cases: list[dict[str, Any]],
    selected_cases: list[dict[str, Any]],
    selected_full_responses: list[dict[str, Any]],
    session_tail_responses: list[dict[str, Any]],
    full_score: dict[str, Any],
    parity_score: dict[str, Any] | None,
) -> dict[str, Any]:
    timing = prompt_timing_index(selected_full_responses + session_tail_responses)
    selected_summaries = []
    parity_by_case = {case["case_id"]: case for case in (parity_score or {}).get("cases", [])}
    for case in selected_cases:
        case_key = str(case["case_id"])
        full = timing.get((case_key, "full"), {})
        tail = timing.get((case_key, "session-tail"), {})
        full_prompt_ms = full.get("timings", {}).get("prompt_ms") if isinstance(full.get("timings"), dict) else None
        tail_prompt_ms = tail.get("timings", {}).get("prompt_ms") if isinstance(tail.get("timings"), dict) else None
        selected_summaries.append(
            {
                "case_id": case_key,
                "dataset_id": case.get("dataset_id"),
                "full_prompt_ms": full_prompt_ms,
                "session_tail_prompt_ms": tail_prompt_ms,
                "prompt_ms_saved": (
                    float(full_prompt_ms) - float(tail_prompt_ms)
                    if isinstance(full_prompt_ms, (int, float)) and isinstance(tail_prompt_ms, (int, float))
                    else None
                ),
                "full_answer_parse_error": full.get("answer_parse_error"),
                "session_tail_answer_parse_error": tail.get("answer_parse_error"),
                "session_tail_minus_full_score": parity_by_case.get(case_key, {}).get("session_tail_minus_full_score"),
            }
        )

    return {
        "metadata": {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "candidate_case_count": len(cases),
            "selected_case_count": len(selected_cases),
            "answer_protocol": args.answer_protocol,
            "min_full_score": args.min_full_score,
            "model": args.hf_repo or str(args.model),
            "ctx_size": args.ctx_size,
            "predict": args.predict,
            "temperature": args.temperature,
            "dry_run": args.dry_run,
        },
        "paths": {name: str(path) for name, path in paths.items()},
        "full_summary": full_score.get("summary", {}),
        "parity_summary": (parity_score or {}).get("summary", {}),
        "selected_cases": selected_summaries,
        "interpretation": (
            "Session-tail quality parity is only meaningful for selected cases where full-prompt baseline met the configured score threshold."
        ),
    }


def llama_config_from_args(args: argparse.Namespace) -> LlamaServerConfig:
    return LlamaServerConfig(
        server_bin=args.server_bin,
        model_path=args.model,
        hf_repo=args.hf_repo,
        slot_cache_dir=args.cache_dir / "slot-cache",
        log_dir=args.cache_dir / "logs",
        ctx_size=args.ctx_size,
        timeout=args.timeout,
    )


def run_metadata(args: argparse.Namespace, case: dict[str, Any], mode: str, completion_prompt: str) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "dataset_id": case.get("dataset_id"),
        "source_id": case.get("source_id"),
        "mode": mode,
        "answer_protocol": args.answer_protocol,
        "answer_hint_id": answer_hint_id_for_case(case, args.answer_protocol),
        "model": args.hf_repo or str(args.model),
        "ctx_size": args.ctx_size,
        "predict": args.predict,
        "temperature": args.temperature,
        "completion_prompt_bytes": len(completion_prompt.encode("utf-8")),
        "completion_prompt_sha256": sha256_text(completion_prompt),
        "stable_prefix_bytes": len(str(case.get("stable_prefix", "")).encode("utf-8")),
        "stable_prefix_sha256": sha256_text(str(case.get("stable_prefix", ""))),
        "tail_prompt_bytes": len(str(case.get("tail_prompt", "")).encode("utf-8")),
        "tail_prompt_sha256": sha256_text(str(case.get("tail_prompt", ""))),
    }


def build_response_record(
    args: argparse.Namespace,
    case: dict[str, Any],
    mode: str,
    completion_prompt: str,
    llama_response: dict[str, Any],
    *,
    started_at: float,
    session_setup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_response = completion_text(llama_response)
    extracted_response, parse_error = extract_protocol_response(raw_response, args.answer_protocol)
    return {
        **run_metadata(args, case, mode, completion_prompt),
        "response": extracted_response,
        "raw_response": raw_response,
        "answer_parse_error": parse_error,
        "latency_ms": (time.perf_counter() - started_at) * 1000,
        "timings": timing_record(llama_response),
        "session_setup": session_setup or {},
    }


def build_error_record(
    args: argparse.Namespace,
    case: dict[str, Any],
    mode: str,
    completion_prompt: str,
    exc: Exception,
    *,
    started_at: float,
) -> dict[str, Any]:
    return {
        **run_metadata(args, case, mode, completion_prompt),
        "response": "",
        "raw_response": "",
        "answer_parse_error": None,
        "latency_ms": (time.perf_counter() - started_at) * 1000,
        "timings": {},
        "session_setup": {},
        "error": str(exc),
    }


def build_dry_run_record(args: argparse.Namespace, case: dict[str, Any], mode: str) -> dict[str, Any]:
    stable_prefix, tail_prompt, full_prompt = protocol_case_parts(case, args.answer_protocol)
    completion_prompt = full_prompt if mode == "full" else tail_prompt
    return {
        **run_metadata(args, case, mode, completion_prompt),
        "response": "",
        "raw_response": "",
        "answer_parse_error": "dry-run has no model response",
        "latency_ms": 0.0,
        "timings": {},
        "session_setup": {
            "dry_run": True,
            "stable_prefix_sha256": sha256_text(stable_prefix),
            "tail_prompt_sha256": sha256_text(tail_prompt),
        },
        "dry_run": True,
    }


def run_full_case(args: argparse.Namespace, case: dict[str, Any]) -> dict[str, Any]:
    _stable_prefix, _tail_prompt, prompt = protocol_case_parts(case, args.answer_protocol)
    started = time.perf_counter()
    try:
        with ManagedLlamaServer(llama_config_from_args(args), label=f"correctness-full-{case_slug(case)}") as client:
            response = client.completion(
                prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=False,
                json_schema=json_schema_for_protocol(args.answer_protocol),
            )
        return build_response_record(args, case, "full", prompt, response, started_at=started)
    except Exception as exc:
        return build_error_record(args, case, "full", prompt, exc, started_at=started)


def run_session_tail_case(args: argparse.Namespace, case: dict[str, Any]) -> dict[str, Any]:
    stable_prefix, tail_prompt, _full_prompt = protocol_case_parts(case, args.answer_protocol)
    slot_filename = f"{case_slug(case)}-{sha256_text(stable_prefix)[:16]}-slot.bin"
    started = time.perf_counter()
    try:
        with ManagedLlamaServer(llama_config_from_args(args), label=f"correctness-session-tail-{case_slug(case)}") as client:
            setup_started = time.perf_counter()
            prime_response = client.completion(
                stable_prefix,
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
                tail_prompt,
                n_predict=args.predict,
                temperature=args.temperature,
                cache_prompt=True,
                json_schema=json_schema_for_protocol(args.answer_protocol),
            )
        return build_response_record(
            args,
            case,
            "session-tail",
            tail_prompt,
            response,
            started_at=started,
            session_setup=session_setup,
        )
    except Exception as exc:
        return build_error_record(args, case, "session-tail", tail_prompt, exc, started_at=started)


def run_case(args: argparse.Namespace, case: dict[str, Any], mode: str) -> dict[str, Any]:
    if args.dry_run:
        return build_dry_run_record(args, case, mode)
    if mode == "full":
        return run_full_case(args, case)
    if mode == "session-tail":
        return run_session_tail_case(args, case)
    raise CorrectnessEvalError(f"Unsupported run mode: {mode}")


def write_score_result(cases: list[dict[str, Any]], responses: list[dict[str, Any]], output_path: Path) -> None:
    result = score_response_pairs(cases, responses)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def list_datasets() -> list[dict[str, Any]]:
    return [asdict(dataset) for dataset in DATASETS.values()]


def command_list_datasets(args: argparse.Namespace) -> int:
    payload = list_datasets()
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else render_dataset_table(payload))
    return 0


def render_dataset_table(rows: list[dict[str, Any]]) -> str:
    headers = ["id", "hf_repo", "split", "license", "task_family", "scoring"]
    lines = ["\t".join(headers)]
    for row in rows:
        lines.append("\t".join(str(row[key]) for key in headers))
    return "\n".join(lines)


def command_sample(args: argparse.Namespace) -> int:
    rows = load_remote_rows(
        args.dataset,
        limit=args.limit,
        offset=args.offset,
        max_prompt_chars=args.max_prompt_chars,
        streaming=not args.no_streaming,
    )
    cases = [build_case(args.dataset, row, index=args.offset + index) for index, row in enumerate(rows)]
    output_path = args.output or args.output_dir / f"{args.dataset}-sample-{len(cases)}.jsonl"
    write_jsonl(cases, output_path)
    print(f"Wrote {len(cases)} cases: {output_path}")
    return 0


def command_build_candidates(args: argparse.Namespace) -> int:
    specs = parse_candidate_mix(args.mix)
    cases = []
    dataset_counts = {}
    for spec in specs:
        rows = load_remote_rows(
            spec.dataset_id,
            limit=spec.limit,
            offset=args.offset,
            max_prompt_chars=args.max_prompt_chars,
            streaming=not args.no_streaming,
            row_filter=candidate_row_filter(spec.dataset_id, args.profile),
        )
        dataset_counts[spec.dataset_id] = len(rows)
        for index, row in enumerate(rows):
            case = build_case(spec.dataset_id, row, index=args.offset + index)
            cases.append(attach_candidate_metadata(case, args=args, spec=spec, sample_index=args.offset + index))

    output_path = args.output or default_candidate_output_path(args.output_dir, specs, args.profile)
    write_jsonl(cases, output_path)
    summary = {
        "candidate_count": len(cases),
        "dataset_counts": dataset_counts,
        "mix": args.mix,
        "output": str(output_path),
        "profile": args.profile,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def command_score(args: argparse.Namespace) -> int:
    cases = read_jsonl(args.cases)
    responses = read_jsonl(args.responses)
    result = score_response_pairs(cases, responses)
    output_path = args.output or DEFAULT_RESULT_DIR / f"correctness-score-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote score result: {output_path}")
    return 0


def command_run(args: argparse.Namespace) -> int:
    cases = read_jsonl(args.cases)
    modes = selected_run_modes(args.mode)
    output_path = args.output or response_output_path(args.cases, args.mode, args.output_dir)
    records = []
    for case in cases:
        for mode in modes:
            print(f"[correctness-eval] {mode}: {case['case_id']}", flush=True)
            records.append(run_case(args, case, mode))

    write_jsonl(records, output_path)
    print(f"Wrote {len(records)} response records: {output_path}")
    if args.score_output or args.score:
        score_output = args.score_output or default_score_output_path(output_path, args.output_dir)
        write_score_result(cases, records, score_output)
        print(f"Wrote score result: {score_output}")
    return 0


def command_baseline_ladder(args: argparse.Namespace) -> int:
    cases = read_jsonl(args.cases)
    label = args.label or default_ladder_label(args.cases)
    paths = ladder_paths(args.output_dir, label)

    full_responses = []
    for case in cases:
        print(f"[correctness-ladder] full: {case['case_id']}", flush=True)
        full_responses.append(run_case(args, case, "full"))
    write_jsonl(full_responses, paths["full_responses"])
    full_score = score_response_pairs(cases, full_responses)
    paths["full_scores"].write_text(json.dumps(full_score, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    passing_ids = selected_case_ids(full_score, min_score=args.min_full_score)
    selected_cases = filter_cases_by_id(cases, passing_ids)
    selected_full_responses = filter_responses_by_id(full_responses, passing_ids, mode="full")
    write_jsonl(selected_cases, paths["selected_cases"])

    session_tail_responses: list[dict[str, Any]] = []
    parity_score: dict[str, Any] | None = None
    if selected_cases:
        for case in selected_cases:
            print(f"[correctness-ladder] session-tail: {case['case_id']}", flush=True)
            session_tail_responses.append(run_case(args, case, "session-tail"))
        write_jsonl(session_tail_responses, paths["session_tail_responses"])
        parity_responses = selected_full_responses + session_tail_responses
        write_jsonl(parity_responses, paths["parity_responses"])
        parity_score = score_response_pairs(selected_cases, parity_responses)
        paths["parity_scores"].write_text(json.dumps(parity_score, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        write_jsonl([], paths["session_tail_responses"])
        write_jsonl([], paths["parity_responses"])
        empty_score = score_response_pairs([], [])
        paths["parity_scores"].write_text(json.dumps(empty_score, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        parity_score = empty_score

    report = build_ladder_report(
        args=args,
        paths=paths,
        cases=cases,
        selected_cases=selected_cases,
        selected_full_responses=selected_full_responses,
        session_tail_responses=session_tail_responses,
        full_score=full_score,
        parity_score=parity_score,
    )
    paths["report"].write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote ladder report: {paths['report']}")
    print(f"Candidate cases: {len(cases)}")
    print(f"Selected full-passing cases: {len(selected_cases)}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare and score Flashcache correctness eval cases.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-datasets", help="List supported correctness datasets.")
    list_parser.add_argument("--json", action="store_true", help="Emit JSON instead of a TSV table.")
    list_parser.set_defaults(func=command_list_datasets)

    sample_parser = subparsers.add_parser("sample", help="Materialize sampled Hugging Face rows as eval cases.")
    sample_parser.add_argument("--dataset", choices=sorted(DATASETS), required=True, help="Dataset id to sample.")
    sample_parser.add_argument("--limit", type=int, default=8, help="Maximum cases to write.")
    sample_parser.add_argument("--offset", type=int, default=0, help="Skip this many matching rows before sampling.")
    sample_parser.add_argument("--max-prompt-chars", type=int, help="Skip rows whose raw prompt exceeds this many bytes.")
    sample_parser.add_argument("--no-streaming", action="store_true", help="Disable Hugging Face streaming load.")
    sample_parser.add_argument("--output-dir", type=Path, default=DEFAULT_CASE_DIR, help="Directory for sampled case JSONL.")
    sample_parser.add_argument("--output", type=Path, help="Explicit output JSONL path.")
    sample_parser.set_defaults(func=command_sample)

    candidate_parser = subparsers.add_parser(
        "build-candidates",
        help="Materialize a mixed correctness candidate JSONL file for baseline-pass ladders.",
    )
    candidate_parser.add_argument(
        "--mix",
        required=True,
        help="Comma-separated DATASET:COUNT entries, e.g. ifeval:80,graphwalks:20.",
    )
    candidate_parser.add_argument(
        "--profile",
        choices=["default", "easy"],
        default="default",
        help="Sampling profile. 'easy' currently filters IFEval to simple supported checks.",
    )
    candidate_parser.add_argument("--offset", type=int, default=0, help="Skip this many matching rows per dataset.")
    candidate_parser.add_argument("--max-prompt-chars", type=int, help="Skip rows whose raw prompt exceeds this many bytes.")
    candidate_parser.add_argument("--no-streaming", action="store_true", help="Disable Hugging Face streaming load.")
    candidate_parser.add_argument("--output-dir", type=Path, default=DEFAULT_CASE_DIR, help="Directory for candidate case JSONL.")
    candidate_parser.add_argument("--output", type=Path, help="Explicit output JSONL path.")
    candidate_parser.set_defaults(func=command_build_candidates)

    score_parser = subparsers.add_parser("score", help="Score response JSONL records against eval cases.")
    score_parser.add_argument("--cases", type=Path, required=True, help="Eval case JSONL path.")
    score_parser.add_argument("--responses", type=Path, required=True, help="Response JSONL path.")
    score_parser.add_argument("--output", type=Path, help="Score result JSON path.")
    score_parser.set_defaults(func=command_score)

    run_parser = subparsers.add_parser("run", help="Generate full/session-tail model responses for eval cases.")
    run_parser.add_argument("--cases", type=Path, required=True, help="Eval case JSONL path.")
    run_parser.add_argument(
        "--mode",
        choices=["full", "session-tail", "both"],
        default="both",
        help="Which response mode to generate.",
    )
    run_parser.add_argument(
        "--answer-protocol",
        choices=["raw", "json-answer"],
        default="raw",
        help="How to format model answers before scoring.",
    )
    run_parser.add_argument("--server-bin", default="llama-server", help="llama.cpp server binary.")
    run_parser.add_argument(
        "--model",
        type=Path,
        default=ROOT / "benchmarks" / "models" / "gemma-3-270m-it-Q8_0.gguf",
        help="Path to a GGUF model.",
    )
    run_parser.add_argument("--hf-repo", help="Hugging Face GGUF repo for llama.cpp -hf loading.")
    run_parser.add_argument("--ctx-size", type=int, default=4096, help="llama.cpp context size.")
    run_parser.add_argument("--predict", type=int, default=64, help="Generated tokens per response.")
    run_parser.add_argument("--prime-n-predict", type=int, default=0, help="Generated tokens when priming stable prefix.")
    run_parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    run_parser.add_argument("--timeout", type=float, default=120.0, help="HTTP/server timeout in seconds.")
    run_parser.add_argument("--cache-dir", type=Path, default=DEFAULT_RUN_CACHE_DIR, help="Directory for slot/log artifacts.")
    run_parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULT_DIR, help="Directory for response and score outputs.")
    run_parser.add_argument("--output", type=Path, help="Explicit response JSONL output path.")
    run_parser.add_argument("--score", action="store_true", help="Score generated responses after writing response JSONL.")
    run_parser.add_argument("--score-output", type=Path, help="Explicit score JSON output path.")
    run_parser.add_argument("--dry-run", action="store_true", help="Write response record skeletons without starting llama.cpp.")
    run_parser.set_defaults(func=command_run)

    ladder_parser = subparsers.add_parser(
        "baseline-ladder",
        help="Run full baseline first, then compare session-tail only on full-passing cases.",
    )
    ladder_parser.add_argument("--cases", type=Path, required=True, help="Candidate eval case JSONL path.")
    ladder_parser.add_argument("--label", help="Output artifact label. Defaults to case stem plus timestamp.")
    ladder_parser.add_argument("--min-full-score", type=float, default=1.0, help="Minimum full-mode score to select a case.")
    ladder_parser.add_argument(
        "--answer-protocol",
        choices=["raw", "json-answer"],
        default="json-answer",
        help="How to format model answers before scoring.",
    )
    ladder_parser.add_argument("--server-bin", default="llama-server", help="llama.cpp server binary.")
    ladder_parser.add_argument(
        "--model",
        type=Path,
        default=ROOT / "benchmarks" / "models" / "gemma-3-270m-it-Q8_0.gguf",
        help="Path to a GGUF model.",
    )
    ladder_parser.add_argument("--hf-repo", help="Hugging Face GGUF repo for llama.cpp -hf loading.")
    ladder_parser.add_argument("--ctx-size", type=int, default=4096, help="llama.cpp context size.")
    ladder_parser.add_argument("--predict", type=int, default=128, help="Generated tokens per response.")
    ladder_parser.add_argument("--prime-n-predict", type=int, default=0, help="Generated tokens when priming stable prefix.")
    ladder_parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    ladder_parser.add_argument("--timeout", type=float, default=120.0, help="HTTP/server timeout in seconds.")
    ladder_parser.add_argument("--cache-dir", type=Path, default=DEFAULT_RUN_CACHE_DIR, help="Directory for slot/log artifacts.")
    ladder_parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULT_DIR, help="Directory for ladder outputs.")
    ladder_parser.add_argument("--dry-run", action="store_true", help="Write response record skeletons without starting llama.cpp.")
    ladder_parser.set_defaults(func=command_baseline_ladder)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return int(args.func(args))
    except CorrectnessEvalError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    exit_code = main()
    if len(sys.argv) > 1 and sys.argv[1] in {"sample", "build-candidates"}:
        # Hugging Face streaming can leave transfer worker threads alive after a bounded sample.
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(exit_code)
    raise SystemExit(exit_code)
