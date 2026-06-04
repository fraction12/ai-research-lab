## Why

Family 1 proved that the parity-validated native direct C API route can save and restore enough prefix state for a 3-case simple codeword gate. The next smallest meaningful question is whether the same capsule contract survives a small structured-retrieval prefix where the tail must retrieve one fabricated value from several hidden facts.

## What Changes

- Add a focused 5-case Family 2 structured-retrieval KV capsule gate.
- Use fabricated key-value/table prefixes where the requested answer appears only in prefix text, never in the tail.
- Reuse the Family 1 canonical native route: full prompt and prefix prefill with `add_special=true`, appended tail with `add_special=false`.
- Run controls in strict order: full-visible guard, fresh-tail leakage control, live append, and restored capsule only after live append passes.
- Stop and package the first hard stop condition instead of changing prompts, expanding task families, or running broad benchmarks.
- Preserve prompt-bearing raw artifacts under ignored Track 01 benchmark paths and commit only sanitized Track 02 summaries.

## Capabilities

### New Capabilities

- `kv-capsule-family2-structured-retrieval-gate`: Defines the 5-case structured-retrieval capsule gate, controls, metrics, stop rules, artifact layout, and interpretation boundary.

### Modified Capabilities

- `kv-capsule-semantic-continuation`: Adds the post-Family-1 structured-retrieval gate as the next allowable step after the simple codeword capsule gate passes.

## Impact

- Affected OpenSpec artifacts: new change under `openspec/changes/run-kv-capsule-family2-structured-retrieval-gate/`.
- Affected committed experiment summaries: `research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-family2-structured-retrieval-gate-2026-06-04/`.
- Affected ignored raw artifacts: prompt-bearing runner records, responses, logs, and state bytes under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/`.
- No tracked Track 01 harness changes are expected; any runner remains in the ignored raw benchmark path.
- The Family 1 OpenSpec task-ledger cleanup remains a tiny bookkeeping diff in the same local landing if not committed separately.
