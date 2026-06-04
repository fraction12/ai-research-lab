## Why

The latest GPT-OSS edge-evidence control passed all six focused GraphWalks cases after the model was given tiny verified incoming-edge slices, while the pinned lower-level full-prompt baseline still missed two cases. Track 02 now needs the next focused test: whether hidden-prefix/session-tail can be repaired by adding a small visible evidence slice extracted from the hidden prefix.

## What Changes

- Import the latest GPT-OSS verified incoming-edge evidence result into Track 02 artifacts as a focused control, not a general benchmark.
- Define a visible-evidence-slice repair experiment for the six fixed GraphWalks cases: `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`.
- Compare hidden-prefix/session-tail against hidden-prefix plus a small visible extracted evidence slice.
- Require metrics for correctness, prompt tokens, prompt time, visible evidence edge count, visible evidence bytes, and visible evidence tokens where tokenizer data is available.
- Frame the result as role-aware context compilation / selective recompute rather than pure KV cache reuse.
- Keep prompt-bearing raw outputs local/ignored and commit only summaries, commands, hashes, model/runtime metadata, and classifications.
- Do not run broad benchmarks and do not modify Track 01 harness code unless the visible-evidence-slice control cannot be expressed with current commands or local case composition.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `flashcache-correctness-eval-suite`: Add the visible-evidence-slice repair control, artifact contract, and required metrics.
- `research-positioning-doc`: Add framing requirements that distinguish selective visible evidence repair from pure persistent KV reuse.

## Impact

- Affected specs: `openspec/specs/flashcache-correctness-eval-suite/spec.md` and `openspec/specs/research-positioning-doc/spec.md`.
- Imported Track 02 evidence: `research/02-quality-gated-stateful-kv-reuse/experiments/gptoss-edge-evidence-2026-06-04/`.
- Planned Track 02 repair artifact directory: `research/02-quality-gated-stateful-kv-reuse/experiments/visible-evidence-slice-repair-2026-06-04/`.
- Planned local prompt-bearing Track 01 input/output/cache directories:
  - `research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/visible-evidence-slice-repair-2026-06-04/`
  - `research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/visible-evidence-slice-repair-2026-06-04/raw/`
  - `research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/visible-evidence-slice-repair-2026-06-04/`
- Likely execution machine: DushyantPC, using the pinned GPT-OSS-compatible llama.cpp runner and GPT-OSS model recorded in the imported edge-evidence artifacts.
- No broad benchmark execution is in scope for this change.
