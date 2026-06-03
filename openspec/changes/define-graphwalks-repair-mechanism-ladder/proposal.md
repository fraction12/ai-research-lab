## Why

The first Track 02 GraphWalks ladder showed stable full-prompt success and stable session-tail failure on six selected cases, but it did not yet identify the mechanism or test any repair path. The next step is a focused repair-and-attribution ladder before broad benchmarks or lower-level storage work.

## What Changes

- Define a GraphWalks repair/mechanism ladder for the same fixed cases: `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`.
- Add controls that separate live session continuation, disk save/restore, prompt visibility, anchor-span recompute, position compatibility, and conservative fallback behavior.
- Require exact artifact paths for commands, raw outputs, summaries, model/runtime metadata, prompts, repair outcomes, and prior-art mapping.
- Keep the ladder focused: no broad benchmark runs and no claims about overall GraphWalks or local-agent prevalence from the six-case cohort.
- Require the experiment record to map relevant new papers and systems to the novelty boundary before interpreting results.

## Capabilities

### New Capabilities

### Modified Capabilities

- `flashcache-correctness-eval-suite`: Add requirements for the focused six-case GraphWalks repair/mechanism ladder, including live no-restore control, anchor-span recompute controls, prompt visibility controls, position compatibility probes, fallback classification, and paper-facing prior-art mapping.

## Impact

- Affected OpenSpec capability: `flashcache-correctness-eval-suite`.
- Planned Track 02 research artifacts: `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-repair-mechanism-ladder-2026-06-03/`.
- Planned ignored Track 01 raw input, output, and cache artifact paths:
  - `research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/`
  - `research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/graphwalks-repair-mechanism-ladder-2026-06-03/raw/`
  - `research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/graphwalks-repair-mechanism-ladder-2026-06-03/`
- Track 01 harness code should remain unchanged unless a required runtime-boundary control cannot be expressed by existing commands and local case composition.
