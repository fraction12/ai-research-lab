## Why

Track 02 needs a focused correctness investigation before any broader benchmark or lower-level KV design work. The current evidence shows six GraphWalks cases where full prompt passed and session-tail failed, but the repo has not yet specified the controls needed to attribute those failures.

## What Changes

- Define a six-case GraphWalks correctness ladder for `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`.
- Require the ladder to run focused controls in this order: full-prompt replay variance, visible-prefix/session-formatted control, stronger tail instructions or answer hints, reset/restore sanity checks, scorer/parser brittleness check, and stronger-model control if practical.
- Require exact artifact paths for raw responses, prompt-bearing local inputs, summaries, command logs, model/runtime metadata, and failure classifications.
- Add a failure taxonomy contract so each case can be classified without collapsing model weakness, prompt-protocol issues, scorer brittleness, session/cache semantics, position/compatibility issues, and runtime/storage issues into one bucket.
- Keep the work scoped to experiment design and focused execution; do not run broad benchmarks or modify Track 01 harness code unless a missing control surface is explicitly identified during implementation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `flashcache-correctness-eval-suite`: Add requirements for the focused six-case GraphWalks correctness ladder, artifact manifest, and failure classification taxonomy.

## Impact

- Affected specs: `openspec/specs/flashcache-correctness-eval-suite/spec.md`.
- Likely affected implementation only after approval: `research/01-ssd-native-inference-current/benchmarks/flashcache_correctness_eval.py` and related tests if existing commands cannot express one or more controls.
- Planned local/private artifacts: `research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/`, `research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/`, and `research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/graphwalks-six-case-ladder-2026-06-03/`.
- Planned Track 02 research artifacts: `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/`.
