## Context

The BFCL reliability run exposed a general local-model behavior: useful tool-call intent appears in several dialects. The previous BFCL fix handled these cases inside `bfcl_code_mode_kv_adapter.py`, which would force every future benchmark to rediscover the same parsing issues.

OpenClaw's Code mode model is the right north star: the model-facing surface should stay narrow (`exec`/`wait`), normal tools should live in a hidden run-scoped catalog, nested calls should preserve policy/audit, and telemetry should record the orchestration path. This repo is not implementing OpenClaw itself, but the harness should mirror that separation.

## Goals

- Create a reusable tool-surface parser/IR for model-authored tool calls.
- Keep benchmark adapters responsible for tool definitions, scoring, row metadata, and benchmark-specific execution semantics.
- Preserve the BFCL 10-row reliability result while making the implementation less BFCL-specific.
- Make future benchmark onboarding a matter of writing an adapter, not a parser.

## Non-Goals

- Do not implement a full QuickJS runtime or OpenClaw guest VM.
- Do not expose a broad direct tool schema surface as the default model contract.
- Do not infer missing required arguments from expected benchmark answers.
- Do not claim larger benchmark reliability or KV-capsule value from this refactor alone.

## Architecture

Add `code_mode_tool_surface.py` under the benchmark harness package. It owns:

- `CanonicalToolCall`: name, arguments, source format, parse status, raw object.
- dialect extraction from raw model text;
- wrapper-key normalization for known tool-call schema keys;
- value normalization for scorer-safe comparison;
- conversion to benchmark-compatible call dictionaries;
- duplicate merge by normalized call identity.

BFCL becomes a consumer:

- `parse_calls_from_generated_text` delegates to the common runtime;
- `actual_call_name`, `actual_call_arguments`, and duplicate merge use the common runtime;
- BFCL scoring remains in the BFCL adapter.

The model loop runner uses common parsing to decide whether generation can stop on a complete model-authored call payload. BFCL-specific branches remain only for BFCL execution/scoring and prompt repair language.

## Parser Policy

The parser may normalize syntax and wrapper shape:

- `Function_name` -> `function_name`
- leading-space wrapper keys -> trimmed wrapper keys
- native `call:function.name{arg: value}` -> canonical call
- OpenAI-style `function.arguments` string -> parsed arguments

The parser must not:

- fill required missing arguments;
- map ambiguous partial prefixes to expected functions;
- add calls that are not present in model output;
- use benchmark expected answers to repair output.

## Testing Strategy

- Unit-test every supported dialect through the common tool-surface module.
- Keep BFCL adapter tests as compatibility tests.
- Add runner-level tests for generation stop and duplicate retry merge through the common module.
- Run local py_compile, unit tests, and OpenSpec validation.

## Risks

- Over-normalization could hide model errors. Mitigation: restrict canonical key casing to known wrapper keys, preserve argument key casing unless explicitly trimmed, and report parse source/status.
- Migration could break BFCL compatibility. Mitigation: keep BFCL adapter facade functions and run existing BFCL tests.
- Future benchmarks may need stricter dialect allowlists. Mitigation: make benchmark adapters consume canonical calls but retain scorer-level validation.
