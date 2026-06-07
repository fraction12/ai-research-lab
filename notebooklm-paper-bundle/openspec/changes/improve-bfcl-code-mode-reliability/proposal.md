## Why

The first non-handmade BFCL smoke showed that Gemma4's Code-mode path often emitted usable tool-call intent in shapes the current adapter does not accept. Before scaling the KV capsule benchmark, the runtime must handle realistic BFCL tool-call output and repair failures without using hidden benchmark answers.

## What Changes

- Extend the BFCL Code-mode adapter to parse common model-generated call shapes observed in the 10-row smoke: `action`/`action_input`, `action`/`parameters`, `plan`, nested `function_call`, OpenAI-style `function`, and keys with harmless surrounding whitespace.
- Treat BFCL expected argument options containing an empty string as optional slots during deterministic scoring, while recording the scorer behavior and avoiding host-filled answer synthesis.
- Add a BFCL-specific repair prompt for invalid BFCL rows so model retries request the exact `tool_calls` JSON schema instead of the generic local-agent action schema.
- Add tests covering the observed failure shapes and the scorer boundary between optional arguments and missing required arguments.
- Re-run the 10-row BFCL smoke on Gemma4 and report whether Code-mode full-visible reaches 100% before any larger benchmark run.

## Capabilities

### New Capabilities

- `bfcl-code-mode-reliability`: Code-mode BFCL runtime parsing, repair, scoring, and validation gates for benchmark-derived tool-use rows.

### Modified Capabilities

- None.

## Impact

- Affected code: `research/01-ssd-native-inference-current/benchmarks/bfcl_code_mode_kv_adapter.py`, `research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_model_loop_runner.py`, and BFCL adapter tests.
- Affected artifacts: the ignored BFCL raw smoke outputs and the Track 02 non-handmade benchmark summary artifacts.
- No new external dependencies are required.
