#!/usr/bin/env python3
"""Benchmark-agnostic Code-mode tool-call surface utilities.

This module normalizes messy model-authored tool-call dialects into a small
canonical structure that benchmark adapters can score without owning parser
quirks. It deliberately does not know benchmark expected answers.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any


WRAPPER_KEYS = {
    "action",
    "action_input",
    "arguments",
    "args",
    "calls",
    "function",
    "function_call",
    "function_name",
    "input",
    "name",
    "parameters",
    "plan",
    "tool",
    "tool_calls",
    "tool_id",
}
FENCED_JSON_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
GEMMA_NATIVE_CALL_RE = re.compile(r"call\s*:\s*(?P<name>[A-Za-z0-9_:\-.]+)\s*(?P<tail>\{)?", re.IGNORECASE)
JSON_FRAGMENT_CALL_NAME_RE = re.compile(r'"(?:function_name|name)"\s*:\s*"(?P<name>[^"]+)"')
JSON_FRAGMENT_ARGUMENTS_RE = re.compile(r'"arguments"\s*:\s*(?P<brace>\{)')
DOUBLED_JSON_KEY_QUOTE_REPAIRS = (
    (re.compile(r'""([A-Za-z_][A-Za-z0-9_\-. ]*)""(\s*:)'), r'"\1"\2'),
    (re.compile(r'"([A-Za-z_][A-Za-z0-9_\-. ]*)""(\s*:)'), r'"\1"\2'),
    (re.compile(r'""([A-Za-z_][A-Za-z0-9_\-. ]*)"(\s*:)'), r'"\1"\2'),
)


@dataclass(frozen=True)
class CanonicalToolCall:
    name: str
    arguments: dict[str, Any]
    source_format: str
    parse_status: str
    raw: Any

    def as_call_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arguments": self.arguments,
            "_tool_surface": {
                "source_format": self.source_format,
                "parse_status": self.parse_status,
            },
        }


@dataclass(frozen=True)
class ToolSurfaceParseResult:
    calls: list[CanonicalToolCall]
    parse_status: str
    source_format: str | None
    candidate_count: int


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalize_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): normalize_value(item) for key, item in value.items()}
    return value


def normalize_wrapper_keys(value: Any) -> Any:
    if isinstance(value, list):
        return [normalize_wrapper_keys(item) for item in value]
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            stripped = str(key).strip()
            canonical_key = stripped.lower() if stripped.lower() in WRAPPER_KEYS else stripped
            normalized[canonical_key] = normalize_wrapper_keys(item)
        return normalized
    return value


def extract_first_json_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def repair_common_model_json_text(text: str) -> str:
    """Repair narrow JSON-key quote glitches seen in model-authored tool calls."""
    repaired = text
    for pattern, replacement in DOUBLED_JSON_KEY_QUOTE_REPAIRS:
        repaired = pattern.sub(replacement, repaired)
    return repaired


def json_loads_with_repairs(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as original_error:
        repaired = repair_common_model_json_text(text)
        if repaired == text:
            raise original_error
        return json.loads(repaired)


def parse_json_or_relaxed_object(text: str) -> dict[str, Any] | None:
    text = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", lambda m: json.dumps(m.group(1)), text)
    try:
        value = json_loads_with_repairs(text)
    except json.JSONDecodeError:
        relaxed = re.sub(r"([,{]\s*)([A-Za-z_][A-Za-z0-9_-]*)\s*:", r'\1"\2":', text)
        try:
            value = json_loads_with_repairs(relaxed)
        except json.JSONDecodeError:
            return None
    return value if isinstance(value, dict) else None


def actual_call_name(actual: dict[str, Any] | CanonicalToolCall) -> str:
    if isinstance(actual, CanonicalToolCall):
        return actual.name
    actual = normalize_wrapper_keys(actual)
    function = actual.get("function")
    if isinstance(function, dict):
        value = function.get("name")
    else:
        value = function
    actual_name = str(
        actual.get("name")
        or actual.get("function_name")
        or value
        or actual.get("tool")
        or actual.get("tool_id")
        or ""
    ).strip()
    if actual_name.startswith("bfcl:function:"):
        actual_name = actual_name.removeprefix("bfcl:function:")
    return actual_name


def actual_call_arguments(actual: dict[str, Any] | CanonicalToolCall) -> dict[str, Any]:
    if isinstance(actual, CanonicalToolCall):
        return dict(actual.arguments)
    actual = normalize_wrapper_keys(actual)
    arguments = (
        actual.get("arguments")
        or actual.get("args")
        or actual.get("input")
        or actual.get("parameters")
        or actual.get("action_input")
    )
    function = actual.get("function")
    if arguments is None and isinstance(function, dict):
        arguments = function.get("arguments") or function.get("args") or function.get("parameters")
    if isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)
        except json.JSONDecodeError:
            parsed = {}
        arguments = parsed
    arguments = normalize_wrapper_keys(arguments or {})
    if not isinstance(arguments, dict):
        return {}
    return dict(arguments)


def _canonical_call(value: Any, *, source_format: str, parse_status: str) -> CanonicalToolCall | None:
    if isinstance(value, CanonicalToolCall):
        return value
    if not isinstance(value, dict):
        return None
    name = actual_call_name(value)
    if not name:
        return None
    return CanonicalToolCall(
        name=name,
        arguments=actual_call_arguments(value),
        source_format=source_format,
        parse_status=parse_status,
        raw=value,
    )


def coerce_call_object(value: Any, *, source_format: str = "json") -> list[CanonicalToolCall]:
    value = normalize_wrapper_keys(value)
    if isinstance(value, list):
        calls: list[CanonicalToolCall] = []
        for item in value:
            calls.extend(coerce_call_object(item, source_format=source_format))
        return calls
    if not isinstance(value, dict):
        return []
    if "tool_calls" in value:
        return coerce_call_object(value["tool_calls"], source_format="tool_calls")
    if "calls" in value:
        return coerce_call_object(value["calls"], source_format="calls")
    if "plan" in value:
        return coerce_call_object(value["plan"], source_format="plan")
    if "function_call" in value:
        return coerce_call_object(value["function_call"], source_format="function_call")
    if "action" in value:
        arguments = value.get("action_input") or value.get("parameters") or value.get("arguments") or value.get("args")
        call = _canonical_call(
            {"name": str(value["action"]).strip(), "arguments": normalize_wrapper_keys(arguments or {})},
            source_format="action",
            parse_status="canonical_tool_call",
        )
        return [call] if call else []
    if any(key in value for key in ("name", "function_name", "function", "tool", "tool_id")):
        call = _canonical_call(value, source_format=source_format, parse_status="canonical_tool_call")
        return [call] if call else []
    calls = []
    for name, args in value.items():
        if isinstance(args, dict):
            call = _canonical_call(
                {"name": str(name), "arguments": args},
                source_format="dict_mapping",
                parse_status="canonical_tool_call",
            )
            if call:
                calls.append(call)
    return calls


def parse_calls_from_json_text(text: str) -> list[CanonicalToolCall]:
    return coerce_call_object(json_loads_with_repairs(text), source_format="json")


def _json_candidates_from_text(text: str) -> list[Any]:
    candidates: list[Any] = []
    fenced_spans: list[tuple[int, int]] = []
    decoder = json.JSONDecoder()
    for match in FENCED_JSON_RE.finditer(text):
        fenced_spans.append(match.span())
        body = match.group(1).strip()
        if not body:
            continue
        try:
            candidates.append(json_loads_with_repairs(body))
        except json.JSONDecodeError:
            pass
    for index, char in enumerate(text):
        if char not in "{[":
            continue
        if any(start <= index < end for start, end in fenced_spans):
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        candidates.append(parsed)
    return candidates


def _is_call_collection(value: Any) -> bool:
    value = normalize_wrapper_keys(value)
    return isinstance(value, dict) and any(key in value for key in ("tool_calls", "calls", "plan"))


def _gemma_native_call_candidates(text: str) -> list[CanonicalToolCall]:
    calls: list[CanonicalToolCall] = []
    for match in GEMMA_NATIVE_CALL_RE.finditer(text):
        name = match.group("name").strip()
        if not name:
            continue
        arguments: dict[str, Any] = {}
        tail_start = match.start("tail") if match.group("tail") else -1
        if tail_start >= 0:
            json_object = extract_first_json_object(text[tail_start:])
            if json_object:
                parsed = parse_json_or_relaxed_object(json_object)
                if isinstance(parsed, dict):
                    arguments = normalize_wrapper_keys(parsed)
        if arguments:
            calls.append(
                CanonicalToolCall(
                    name=name,
                    arguments=arguments,
                    source_format="gemma_native_call",
                    parse_status="canonical_tool_call",
                    raw={"name": name, "arguments": arguments},
                )
            )
    return calls


def _json_tool_call_fragment_candidates(text: str) -> list[CanonicalToolCall]:
    text = repair_common_model_json_text(text)
    calls: list[CanonicalToolCall] = []
    seen: set[str] = set()
    for name_match in JSON_FRAGMENT_CALL_NAME_RE.finditer(text):
        name = name_match.group("name").strip()
        if not name:
            continue

        tail = text[name_match.end() :]
        arguments_match = JSON_FRAGMENT_ARGUMENTS_RE.search(tail)
        arguments_start: int | None = None
        if arguments_match:
            arguments_start = name_match.end() + arguments_match.start("brace")
        else:
            prefix = text[: name_match.start()]
            previous_arguments = list(JSON_FRAGMENT_ARGUMENTS_RE.finditer(prefix))
            if previous_arguments:
                arguments_start = previous_arguments[-1].start("brace")
        if arguments_start is None:
            continue

        json_object = extract_first_json_object(text[arguments_start:])
        if not json_object:
            continue
        arguments = parse_json_or_relaxed_object(json_object)
        if not isinstance(arguments, dict):
            continue

        raw = {"name": name, "arguments": normalize_wrapper_keys(arguments)}
        call = CanonicalToolCall(
            name=name,
            arguments=dict(raw["arguments"]),
            source_format="json_fragment",
            parse_status="canonical_tool_call",
            raw=raw,
        )
        identity = call_identity(call)
        if identity in seen:
            continue
        seen.add(identity)
        calls.append(call)
    return calls


def parse_tool_calls_from_text(text: str) -> ToolSurfaceParseResult:
    native_calls = _gemma_native_call_candidates(text)
    if native_calls:
        return ToolSurfaceParseResult(
            calls=native_calls,
            parse_status="parsed_tool_calls",
            source_format="gemma_native_call",
            candidate_count=len(native_calls),
        )

    fragment_calls = _json_tool_call_fragment_candidates(text)
    collected: list[CanonicalToolCall] = []
    candidate_count = 0
    source_format: str | None = None
    for candidate in _json_candidates_from_text(text):
        candidate_count += 1
        calls = coerce_call_object(candidate, source_format="json")
        if not calls:
            continue
        if fragment_calls and all(call.source_format == "dict_mapping" for call in calls):
            continue
        source_format = calls[0].source_format
        if _is_call_collection(candidate) or len(calls) > 1:
            return ToolSurfaceParseResult(
                calls=calls,
                parse_status="parsed_tool_calls",
                source_format=source_format,
                candidate_count=candidate_count,
            )
        collected.extend(calls)
    if not collected:
        if fragment_calls:
            return ToolSurfaceParseResult(
                calls=fragment_calls,
                parse_status="parsed_tool_calls",
                source_format="json_fragment",
                candidate_count=len(fragment_calls),
            )
    return ToolSurfaceParseResult(
        calls=collected,
        parse_status="parsed_tool_calls" if collected else "no_tool_calls",
        source_format=source_format,
        candidate_count=candidate_count,
    )


def parse_calls_from_generated_text(text: str) -> list[dict[str, Any]]:
    return [call.as_call_dict() for call in parse_tool_calls_from_text(text).calls]


def call_identity(call: dict[str, Any] | CanonicalToolCall) -> str:
    return canonical_json(
        {
            "name": actual_call_name(call),
            "arguments": normalize_value(actual_call_arguments(call)),
        }
    )


def merge_call_candidates(
    existing: list[dict[str, Any] | CanonicalToolCall],
    new_calls: list[dict[str, Any] | CanonicalToolCall],
) -> list[dict[str, Any]]:
    merged = [call.as_call_dict() if isinstance(call, CanonicalToolCall) else dict(call) for call in existing]
    seen = {call_identity(call) for call in merged}
    for call in new_calls:
        key = call_identity(call)
        if key in seen:
            continue
        seen.add(key)
        merged.append(call.as_call_dict() if isinstance(call, CanonicalToolCall) else dict(call))
    return merged


def telemetry_for_calls(calls: list[dict[str, Any] | CanonicalToolCall]) -> list[dict[str, Any]]:
    telemetry = []
    for call in calls:
        if isinstance(call, CanonicalToolCall):
            telemetry.append(asdict(call))
        else:
            surface = call.get("_tool_surface") if isinstance(call, dict) else {}
            telemetry.append(
                {
                    "name": actual_call_name(call),
                    "arguments": actual_call_arguments(call),
                    "source_format": surface.get("source_format") if isinstance(surface, dict) else None,
                    "parse_status": surface.get("parse_status") if isinstance(surface, dict) else None,
                    "raw": call,
                }
            )
    return telemetry
