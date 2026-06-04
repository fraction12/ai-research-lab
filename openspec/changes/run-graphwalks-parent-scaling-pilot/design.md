## Context

Track 02 is investigating quality-gated persistent KV/session reuse for local agent loops. The focused six-case GraphWalks chain is now:

```text
hidden-prefix/session-tail:          0/6
visible evidence tail:               4/6
compact visible evidence tail:       6/6
```

That chain is a mechanism result, not a benchmark claim. It says the model can solve the six selected `parents` failures when the relevant incoming-edge evidence is made visible and the answer protocol is compact enough to avoid verbose truncation. The next question is whether the same pattern survives a larger, still-controlled GraphWalks `parents` cohort.

The pinned lower-level path remains the DushyantPC GPT-OSS llama.cpp runner:

```text
C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe
C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb
```

The pilot should preserve `--ctx-size 32768`, `--temperature 0.0`, `--predict 192`, and the GPT-OSS llama.cpp flags unless a hard blocker is recorded.

## Goals / Non-Goals

**Goals:**

- Test whether the six-case mechanism chain generalizes to a deterministic 50-case GraphWalks `parents` pilot.
- Measure when hidden cached context fails and when compact visible evidence repairs it.
- Separate hidden-KV contribution from token-efficient evidence scheduling using a fresh evidence-only honesty control.
- Preserve exact model, quantization, runner path, runner hash, backend flags, commands, prompt hashes, raw response hashes, and timing telemetry.
- Classify failures by model weakness, prompt protocol, scorer/parser brittleness, session/cache semantics, position/compatibility issue, runtime/storage issue, or ambiguity.

**Non-Goals:**

- No broad mixed benchmark run.
- No claim of general GraphWalks quality from this pilot.
- No use of the vault mind experimental model.
- No Track 01 harness edits unless current local scripts cannot express the control matrix.
- No use of reference answer sets to construct evidence slices.
- No claim that compact visible evidence is pure KV reuse.

## Decisions

### Decision 1: Use a deterministic 50-case `parents` cohort

Build the pilot from GraphWalks `parents` rows only. Prefer deterministic sampling over expensive perfect stratification. After sampling, annotate each case into buckets for answer size, evidence edge count/bytes, duplicate edge presence, relevant edge position, prefix length, and full-visible pass/fail. If the deterministic sample includes an empty parent set, record it as a separate `0 parents` bucket rather than folding it into `1 parent`.

Rationale: deterministic sampling makes the pilot reproducible. Bucket annotation keeps it interpretable even if perfect pre-stratification is not practical.

### Decision 2: Run five paired controls per case

Each sampled case should produce these control records:

| Control id | Hidden prefix | Visible graph/evidence | Purpose |
| --- | --- | --- | --- |
| `full_visible_compact_prompt` | no | full graph visible | Full-context quality baseline with compact answer protocol. |
| `hidden_prefix_session_tail` | yes | none | Tests hidden cached context alone with the original or existing tail path. |
| `hidden_prefix_compact_tail_no_evidence` | yes | none | Tests whether compact protocol alone repairs hidden-prefix failures. |
| `hidden_prefix_compact_visible_evidence_tail` | yes | extracted incoming-edge slice | Main repair condition. |
| `fresh_compact_visible_evidence_only` | no | extracted incoming-edge slice only | Honesty control for evidence scheduling versus hidden-KV contribution. |

The primary comparisons are:

- `hidden_prefix_compact_visible_evidence_tail` versus `hidden_prefix_session_tail`
- `hidden_prefix_compact_visible_evidence_tail` versus `hidden_prefix_compact_tail_no_evidence`
- `hidden_prefix_compact_visible_evidence_tail` versus `fresh_compact_visible_evidence_only`

### Decision 3: Extract evidence from prefix text and target only

For each `parents` case, extract incoming edge lines whose destination is the requested target node from the stable graph prefix. The extractor may use the question target and graph text, but not the reference answer set. Store the evidence lines, evidence hash, edge count, evidence bytes, token count if available, and duplicate-edge metadata.

Rationale: this models role-aware context compilation from available context. Answer-derived evidence would be an oracle control and must not be mixed with the main repair result.

### Decision 4: Preserve prompt-bearing artifacts locally

Prompt-bearing raw inputs and outputs stay under ignored Track 01 paths:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-parent-scaling-pilot-2026-06-04/
research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/graphwalks-parent-scaling-pilot-2026-06-04/raw/
research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/graphwalks-parent-scaling-pilot-2026-06-04/
```

Committed summaries belong under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-parent-scaling-pilot-2026-06-04/
```

Expected committed files:

```text
README.md
summary.json
case-metrics.json
bucket-analysis.json
failure-classifications.json
evidence-slices.json
commands.md
model-info.json
artifact-manifest.json
```

### Decision 5: Analyze the pilot through subset views

The summary must include:

- All 50 sampled cases.
- Full-visible-pass subset.
- Hidden-prefix-fail subset.
- Repairable hidden-prefix failures.
- Cases where fresh evidence-only equals hidden-prefix plus evidence.
- Cases where compact no-evidence repairs hidden-prefix failure.

This prevents a single aggregate from hiding prompt-protocol or evidence-only confounders.

### Decision 6: Use explicit stop rules

If the full five-control 50-case matrix is too slow or hits repeated runtime blockers, stop after a deterministic smaller slice such as 10 or 20 cases. Record the exact blocker, completed controls, elapsed time, estimated full runtime, and whether the partial result is enough to choose the next test.

Do not silently change the study design or drop controls.

## Risks / Trade-offs

- Evidence-only equals hidden-prefix plus evidence -> report that hidden KV may not contribute materially for this task family; the useful mechanism may be context/evidence scheduling.
- Compact no-evidence repairs many cases -> classify prompt protocol as a major confounder.
- Full visible compact underperforms compact evidence -> treat as pilot signal for retrieval-burden reduction, not a general claim.
- Full visible compact fails many sampled cases -> analyze the full-visible-pass subset before interpreting hidden-prefix repair rates.
- Runtime exceeds the turn budget -> stop at a deterministic partial slice and preserve raw artifacts rather than changing controls.
- Current harness cannot express one or more controls -> use a prompt-composition runner under ignored benchmark artifacts first; modify Track 01 harness only if a spec-level need is proven.

## Migration Plan

No migration is required. This change defines and runs a focused experiment. After the run, import summaries into Track 02, validate OpenSpec, and leave prompt-bearing raw artifacts in ignored Track 01 benchmark paths.

## Open Questions

- Can the 50-case full matrix complete within one DushyantPC run window with `--predict 192`, or should the stop rule trigger a 10/20-case partial pilot?
- Does the current GraphWalks case materializer expose enough source-row metadata to derive target node and edge position buckets cleanly?
- Should future pilots add a second task family only after this `parents`-only result is understood?
