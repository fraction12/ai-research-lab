# Harness Prep Notes

## Current Harness Location

The executable native C API runners for the latest Family 1 and Family 2 gates live under ignored Track 01 raw benchmark paths. They are intentionally not committed because those raw paths can contain prompt-bearing records, responses, token details, and state/cache artifacts.

No committed durable profile layer was found during repo prep. Therefore this change documents the needed patch shape rather than committing ignored raw runner code.

## Required Patch Shape For Orchestration

Add an explicit model profile mechanism to the ignored runner before Gemma model execution. The profile mechanism should preserve the GPT-OSS default and make Gemma selection deliberate.

Suggested profile fields:

```json
{
  "profile_id": "gemma4-12b",
  "model_family": "gemma",
  "model_name": "Gemma 4 12B",
  "model_path": "<orchestration-provided local GGUF path>",
  "expected_architecture": "<recorded from model metadata after load>",
  "tokenizer_or_template_notes": "<recorded before evidence>",
  "ctx_size": 32768,
  "predict": 48,
  "state_route": "auto",
  "expected_effective_route": "seq_file",
  "raw_dir": "research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-gemma4-12b-replication-2026-06-04/raw",
  "cache_dir": "research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-gemma4-12b-replication-2026-06-04/cache"
}
```

Suggested CLI shape:

```text
--model-profile {gpt-oss-20b,gemma4-12b}
--model-profile-file <optional-json>
--model <explicit override>
--out-dir <profile default or explicit override>
--cache-dir <profile default or explicit override>
--state-route {auto,seq-file,seq-memory,whole-context}
```

Rules:

- Selecting `gemma4-12b` must change raw/cache defaults away from the GPT-OSS paths.
- Raw/cache paths must be ignored before any DushyantPC execution.
- The run metadata must include the selected profile and all resolved fields.
- If Gemma-specific tokenization/template behavior differs, it must be recorded before evidence and not silently patched mid-gate.
- `whole-context` remains diagnostic fallback only.

## Smoke Ladder For Orchestration

1. Local syntax/help/stale-grep on the patched ignored runner.
2. Remote syntax/help/stale-grep and export probe.
3. Family 1 smoke with Gemma profile.
4. Family 1 primary if smoke passes.
5. Family 2 smoke if Family 1 primary passes.
6. Family 2 primary if Family 2 smoke passes.

No Family 3, GraphWalks, broad retrieval, noiseless evidence, or agent-context work should run in this replication change.
