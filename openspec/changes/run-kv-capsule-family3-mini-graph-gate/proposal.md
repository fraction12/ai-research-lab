## Why

Family 1 and Family 2 showed restored native state capsules can preserve simple codewords and compact structured key-value/table prefixes. The next smallest meaningful bridge toward the known GraphWalks boundary is a fabricated mini-graph gate that tests one-hop and two-hop relation retrieval without importing GraphWalks or broad benchmark cases.

## What Changes

- Add a focused 5-case Family 3 mini-graph capsule gate.
- Split the task into Stage A with 3 one-hop relation edge retrieval cases and Stage B with 2 two-hop path cases.
- Run Stage B only if Stage A restored capsule passes.
- Reuse the established canonical native route: full prompt and prefix prefill with `add_special=true`, appended tail with `add_special=false`.
- Run controls in strict order per stage: full-visible guard, fresh-tail leakage control, live append, and restored capsule only after live append passes.
- Stop and package the first hard stop condition instead of changing prompts or expanding task families.
- Preserve prompt-bearing raw artifacts under ignored Track 01 benchmark paths and commit only sanitized Track 02 summaries.

## Capabilities

### New Capabilities

- `kv-capsule-family3-mini-graph-gate`: Defines the 5-case mini-graph capsule gate, staged controls, metrics, stop rules, artifact layout, and interpretation boundary.

### Modified Capabilities

- `kv-capsule-semantic-continuation`: Adds the post-Family-2 mini-graph gate as the next allowable step after structured retrieval passes.

## Impact

- Affected OpenSpec artifacts: new change under `openspec/changes/run-kv-capsule-family3-mini-graph-gate/`.
- Affected committed experiment summaries: `research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-family3-mini-graph-gate-2026-06-04/`.
- Affected ignored raw artifacts: prompt-bearing runner records, responses, logs, and state bytes under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/`.
- No tracked Track 01 harness changes are expected; any runner remains in the ignored raw benchmark path.
- No push is part of this change.
