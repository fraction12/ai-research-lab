## 1. Evidence Import

- [x] 1.1 Import latest GPT-OSS verified incoming-edge evidence result into `research/02-quality-gated-stateful-kv-reuse/experiments/gptoss-edge-evidence-2026-06-04/`.
- [x] 1.2 Record raw DushyantPC artifact paths, hashes, model metadata, runner metadata, command metadata, per-case metrics, and focused failure classifications.

## 2. Repair Input Preparation

- [x] 2.1 Materialize or verify the six selected GraphWalks cases under `research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/visible-evidence-slice-repair-2026-06-04/`.
- [x] 2.2 Build `graphwalks-six-visible-evidence-slice-cases.jsonl` by extracting incoming edge lines from each stable graph prefix using the requested target node, not the reference answer set.
- [x] 2.3 Record `evidence-slices.json` with target node, evidence lines, evidence hash, evidence edge count, evidence bytes, evidence tokens when available, and extraction method.

## 3. Focused DushyantPC Runs

- [x] 3.1 Run `hidden_prefix_session_tail` on the six cases using the pinned GPT-OSS-compatible llama.cpp runner.
- [x] 3.2 Run `hidden_prefix_visible_evidence_tail` on the six cases using the same model, runner, context, temperature, and predict settings.
- [x] 3.3 Run or reference `full_visible_reference` and `verified_edge_evidence_control` as comparison anchors.
- [x] 3.4 Preserve prompt-bearing raw responses, prompts, scores, command files, and slot/cache telemetry under ignored Track 01 benchmark paths.

## 4. Summary And Classification

- [x] 4.1 Write committed Track 02 `README.md`, `summary.json`, `artifact-manifest.json`, `model-info.json`, `commands.md`, `failure-classifications.json`, and `evidence-slices.json` under `research/02-quality-gated-stateful-kv-reuse/experiments/visible-evidence-slice-repair-2026-06-04/`.
- [x] 4.2 Compare correctness, prompt tokens, prompt time, and visible evidence size between hidden-prefix/session-tail and hidden-prefix plus visible evidence slice.
- [x] 4.3 Classify each case using the failure taxonomy and separate cache/session semantics from model weakness, prompt protocol, scorer/parser, position/compatibility, and runtime/storage issues.

## 5. Validation

- [x] 5.1 If Track 01 harness code changes are necessary, add focused tests and run the relevant unit tests.
- [x] 5.2 Run `openspec validate --changes visible-evidence-slice-repair --strict`.
- [x] 5.3 Run `openspec validate --all --strict` and record any pre-existing unrelated active-change failures separately.

## 6. Compact Two-Case Repair

- [x] 6.1 Prepare `graphwalks-two-compact-visible-evidence-cases.jsonl` for only `graphwalks-16` and `graphwalks-19`, preserving the same extracted evidence lines and changing only the tail answer protocol.
- [x] 6.2 Run `hidden_prefix_compact_visible_evidence_tail` on DushyantPC with the same pinned GPT-OSS model, runner, context size, temperature, predict count, and GPT-OSS llama.cpp flags.
- [x] 6.3 If needed after the compact-answer main test, run an `increase_predict` diagnostic and label it separately.
- [x] 6.4 Preserve prompt-bearing raw inputs, raw outputs, scores, commands, and telemetry under ignored Track 01 benchmark paths.
- [x] 6.5 Write committed Track 02 `README.md`, `summary.json`, `commands.md`, `artifact-manifest.json`, `model-info.json`, and `failure-classifications.json` under `research/02-quality-gated-stateful-kv-reuse/experiments/compact-visible-evidence-repair-2026-06-04/`.
- [x] 6.6 Interpret the focused chain and classify remaining failures, if any.
- [x] 6.7 Run `openspec validate --changes visible-evidence-slice-repair --strict`.
- [x] 6.8 Run `openspec validate --all --strict`.
