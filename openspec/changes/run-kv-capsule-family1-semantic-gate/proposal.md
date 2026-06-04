## Why

The native/server parity bridge at commit `c8a96d9` proved that the native direct C API full-visible path is semantically usable for the simple codeword prompt shape. It did not run capsule controls. Track 02 can now run the first real KV capsule semantic-continuation gate under a trustworthy native prompt/token/generation route.

The question is narrow: can a native direct C API session save/restore prefix state so that appending only the visible tail behaves semantically like full visible `prefix + tail`, without resending prefix text?

## What Changes

- Add a focused 3-case Family 1 simple codeword capsule gate.
- Use the parity-proven `prior_known_good_simple_codeword` prompt shape.
- Use one canonical native tokenization route and record why.
- Run controls in strict order: full-visible guard, fresh-tail negative, live append, restored capsule only if live append passes.
- Stop immediately on the first hard stop rule.
- Preserve prompt-bearing raw artifacts under ignored Track 01 benchmark paths and commit only sanitized Track 02 summaries.

## Capabilities

### New Capabilities
- `kv-capsule-family1-semantic-gate`: Defines the 3-case parity-proven codeword capsule gate, controls, metrics, stop rules, artifact layout, and interpretation.

### Modified Capabilities
- `kv-capsule-semantic-continuation`: Adds the post-parity Family 1 capsule gate as the next allowable step after native/server full-visible parity passes.

## Impact

- Affected experiment artifacts: new Track 02 summaries under `research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-family1-semantic-gate-2026-06-04/`.
- Affected raw artifacts: prompt-bearing native runner records, responses, logs, and state bytes under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/`.
- Prior evidence preserved: the native/server parity bridge and previous KV-capsule blocker remain unchanged.
- No Track 01 tracked harness changes are expected; the runner remains ignored under the raw benchmark path.
