# KV Capsule HF Paper Benchmark Experiment

Date: 2026-06-05

## Purpose

This experiment tests whether a persisted KV capsule can be restored and continued with only volatile tail tokens while preserving the behavior of a full visible prompt on real benchmark rows.

The claim under test is not "the model has memory" and not "SSD makes the model smarter." The claim under test is narrower:

```text
restore(capsule(prefix)) + append(tail)
```

can behave like:

```text
full_prompt = prefix + tail
```

while reducing repeated-prefix computation after capsule creation is amortized.

## Source Datasets

Paper-facing benchmark cases must come from Hugging Face datasets already supported by the correctness harness:

| Family | HF repo | Split | Task role |
| --- | --- | --- | --- |
| IFEval | `google/IFEval` | `train` | Instruction-following constraints with deterministic checks. |
| GraphWalks | `openai/graphwalks` | `train` | Long-context graph reasoning, starting with `parents` rows. |

Synthetic codeword and key-value cases are allowed only as runner preflight. They must not be included in benchmark tables or task-family quality claims.

## Hypotheses

### H1: Semantic Continuation

For full-visible-passing HF cases, `native_restored_capsule_append` will match `native_live_append` and remain non-inferior to `full_visible` quality.

Evidence required:

- restored capsule quality within the declared non-inferiority margin versus full visible
- restored capsule matching native live append on quality, and on response/token hashes where deterministic hashes are available
- fresh tail-only underperforming on prefix-dependent cases

### H2: Amortized Efficiency

Once capsule creation is separated from repeated tail requests, restored capsule append will reduce prompt eval tokens and prompt eval time versus full visible resend without violating H1.

Evidence required:

- one-shot and amortized cost tables
- break-even repeated-tail count
- prompt eval token reduction
- prompt eval time and total wall-time speedup

### H3: Task-Family Boundary

IFEval and GraphWalks will behave differently. IFEval may be easier to preserve because constraints are often short and instruction-local; GraphWalks stresses reasoning over prefix structure.

Evidence required:

- separate IFEval and GraphWalks tables
- no blended headline score without family splits
- failure classifications by family

### H4: Context Compilation Confounder

For GraphWalks, compact visible evidence may repair failures independently of hidden KV. If fresh compact evidence-only matches capsule plus evidence, the finding supports role-aware context compilation, not pure KV capsule reuse.

Evidence required:

- fresh evidence-only versus capsule plus evidence paired comparison
- compact tail no-evidence control
- explicit interpretation separating hidden KV from visible evidence scheduling

## Cohorts

### Candidate Pools

Build deterministic candidate pools:

- IFEval: at least 100 candidates from `google/IFEval`, easy deterministic supported checks first.
- GraphWalks: at least 100 candidates from `openai/graphwalks`, `parents` rows first.

Each candidate must record:

- HF repo, split, revision or snapshot timestamp
- source row key or row offset
- source row hash
- license
- task family
- stable prefix hash
- tail prompt hash
- full prompt hash
- transform version
- prompt protocol version
- scorer version

### Selected Paper Cohorts

Run full-visible calibration first. Select up to:

- 50 full-visible-passing IFEval cases
- 50 full-visible-passing GraphWalks `parents` cases

If fewer than 50 full-visible-passing cases exist for a family, continue only as diagnostic evidence and do not claim family-level capsule parity.

## Control Matrix

### Primary KV Capsule Controls

| Control | Description | Research role |
| --- | --- | --- |
| `full_visible` | Send full prompt normally. | Positive quality baseline. |
| `fresh_tail_only` | Send tail with no prefix state. | Negative leakage baseline. |
| `native_live_append` | Prefill prefix, append tail in same native sequence. | Tests append semantics without persistence. |
| `native_restored_capsule_append` | Prefill prefix, save capsule, restore capsule, append tail only. | Main KV capsule result. |
| `wrong_capsule_negative` | Restore mismatched capsule or fail closed. | Validates capsule identity and leakage resistance. |
| `documented_full_prompt_cache_resend` | Resend full prompt with documented prompt-cache reuse. | Efficiency comparator, not capsule evidence. |

### GraphWalks Secondary Controls

| Control | Description | Research role |
| --- | --- | --- |
| `fresh_compact_evidence_only` | Tail contains only extracted incoming-edge evidence, no hidden prefix. | Measures context compilation alone. |
| `capsule_plus_compact_evidence_tail` | Restored capsule plus compact visible evidence tail. | Tests whether hidden state adds value beyond evidence. |
| `compact_tail_no_evidence` | Compact answer protocol but no evidence. | Detects prompt-protocol-only repair. |

Evidence extraction for GraphWalks may use the graph prefix and requested target node. It must not use reference answer nodes.

## Required Data Points

### Provenance

- HF repo, split, revision or snapshot timestamp
- source row key or offset
- source row hash
- materialized candidate file hash
- case transform version
- scorer version
- prompt protocol version

### Model And Runtime

- model name, path, size, SHA-256, quantization
- tokenizer or chat template hash where available
- llama.cpp version/hash
- runner script path/hash
- backend route: sequence-file, C API, server cache, or other
- hardware: CPU, GPU, VRAM, driver/CUDA where available
- context size, batch settings, temperature, seed, prediction cap

### Capsule Metadata

- capsule route and serialization format
- sequence id
- prefix token count
- `n_past`
- capsule bytes
- capsule path and hash
- save time
- restore time
- position/RoPE state availability
- captured fields and unavailable fields

### Prompt And Response Metrics

- prefix bytes/tokens
- tail bytes/tokens
- full prompt bytes/tokens
- evidence bytes/tokens where applicable
- raw response hash
- normalized response hash
- generated token ids hash where available
- parsed answer
- parse status
- truncation flag
- stop reason

### Quality Metrics

- IFEval supported instruction pass/fail
- unsupported IFEval checks
- GraphWalks precision, recall, and F1
- exact set match for GraphWalks
- pass/fail by control
- restored versus live append mismatch
- restored versus full-visible mismatch
- wrong-capsule unexpected pass

### Performance Metrics

- prompt eval tokens
- prompt eval milliseconds
- decode tokens
- decode milliseconds
- total wall time
- capsule creation time
- save time
- restore time
- one-shot speedup versus full visible
- amortized speedup versus full visible at repeat counts 1, 2, 5, 10, and 20
- break-even repeat count

## Success Criteria

### Route Validity

Synthetic preflight must pass before HF rows run:

- full visible passes
- fresh tail-only fails on prefix-dependent cases
- native live append passes
- native restored capsule append passes

### Semantic Parity

For each selected HF family:

- `native_live_append` must match full-visible quality on a 10-case gate before full run.
- `native_restored_capsule_append` must stay within the declared non-inferiority margin against `full_visible`.
- Default margin: no more than one additional failure per 50-case family, and no systematic divergence from native live append.

### Efficiency

Efficiency claims require:

- semantic parity gate passed
- prompt-token reduction versus full visible
- amortized prompt eval or total wall-time improvement over repeated tails
- break-even count reported

## Failure Taxonomy

Use these labels:

- `model_weakness`
- `prompt_protocol_issue`
- `scorer_parser_brittleness`
- `session_cache_semantic_issue`
- `position_compatibility_issue`
- `runtime_storage_issue`
- `transport_issue`
- `context_compilation_effect`
- `ambiguous`

Every failed or ambiguous case-control pair should include a short evidence note.

## Stop Rules

Stop or downgrade claims when:

- synthetic preflight fails
- native live append fails on full-visible-passing HF cases
- restored capsule diverges from native live append beyond the margin
- wrong capsule unexpectedly passes in a way that suggests leakage or identity failure
- full-visible selected count is too small for a family-level claim
- DushyantPC shows repeated instability, duplicate model processes, or transport corruption
- raw artifacts are incomplete or hashes do not match imported summaries

Partial runs must report completed cases, completed controls, elapsed time, estimated full runtime, and exact deviation from the planned design.

## Analysis Plan

Report:

- candidate calibration by family
- selected cohort by family
- full control matrix by family
- restored capsule versus full visible
- restored capsule versus native live append
- fresh tail-only versus full visible
- wrong capsule negative outcomes
- GraphWalks evidence-only versus capsule plus evidence
- amortization curves
- failures by taxonomy

Use paired analysis wherever possible. For pass/fail deltas, report counts and confidence intervals rather than only averages. For latency, report mean, median, p95, and bootstrap confidence intervals when practical.

## Artifact Layout

Prompt-bearing raw artifacts stay under ignored Track 01 benchmark paths:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/hf-kv-capsule-paper-benchmark-2026-06-05/
research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/hf-kv-capsule-paper-benchmark-2026-06-05/raw/
research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/hf-kv-capsule-paper-benchmark-2026-06-05/
```

Committed Track 02 summaries belong under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/hf-kv-capsule-paper-benchmark-2026-06-05/
```

Expected summary files:

```text
README.md
summary.json
case-metrics.json
control-matrix.json
candidate-calibration.json
amortization.json
failure-classifications.json
model-info.json
commands.md
artifact-manifest.json
paper-methods-notes.md
```

## Claim Mapping

| Result pattern | Allowed claim | Disallowed claim |
| --- | --- | --- |
| Restored capsule matches live append and full visible, with amortized speedup | KV capsules can preserve quality on this family under this runtime/model while reducing repeated-prefix cost. | KV capsules make the model generally smarter. |
| Restored capsule matches live append but both trail full visible | Append protocol preserves state, but the tail protocol is not quality-equivalent for the task. | Persistence is the only issue. |
| Live append passes, restored capsule fails | Persistence/restore path is broken or incomplete. | KV capsules do not work in principle. |
| Evidence-only matches capsule plus evidence | Context compilation explains the repair more than hidden KV. | Hidden KV caused the repair. |
| IFEval passes, GraphWalks fails | Task-family boundary exists. | Overall quality is preserved. |

## Next Action After Approval

Send Track 2 to implement the runner/artifact updates and run only the staged gates first:

1. synthetic preflight
2. 10-case IFEval HF gate
3. 10-case GraphWalks HF gate
4. full selected benchmark only if gates pass
