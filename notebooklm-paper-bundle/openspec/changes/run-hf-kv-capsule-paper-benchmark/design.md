## Context

Track 02 is investigating whether a persisted inference state can be restored and continued with only volatile tail tokens while preserving the behavior of `full visible prefix + tail`.

The latest useful state is:

- GPT-OSS llama.cpp server slot restore moved cache bytes but tail-only semantics behaved like fresh tail-only on simple hidden-prefix probes.
- Gemma 4 12B on DushyantPC passed the synthetic KV capsule gates through the llama.cpp sequence-file route: full visible, native live append, and restored capsule append all passed; fresh tail-only failed.
- Those Gemma gates were synthetic codeword and structured key-value tasks. They prove the route can work mechanically, but they are not enough for a paper-facing benchmark claim.
- The correctness harness already knows `google/IFEval` and `openai/graphwalks`; these must become the paper benchmark sources.

This design treats synthetic tasks as preflight only. Paper evidence must come from HF-backed rows with preserved provenance.

## Goals / Non-Goals

**Goals:**

- Test whether restored tail-only KV capsules preserve full-visible quality on real HF benchmark rows.
- Separate runtime/capsule semantics from model weakness, prompt protocol, scorer brittleness, and context-compilation effects.
- Measure whether capsule reuse produces meaningful amortized speed or token savings once capsule creation cost is separated from repeated tail queries.
- Preserve enough metadata for a research paper methods section: source datasets, model, quantization, runtime, hardware, runner hashes, prompt hashes, raw output hashes, scoring versions, capsule metadata, commands, and telemetry.
- Produce task-family split results for IFEval and GraphWalks rather than a single blended score.

**Non-Goals:**

- No handmade benchmark cases beyond a small synthetic runner preflight.
- No broad claim that KV capsules make the model smarter.
- No claim of pure KV benefit if fresh visible evidence-only matches hidden-prefix plus evidence.
- No comparison across model families unless each model has its own fully separated table.
- No PDF/full-text dataset collection.

## Decisions

### Decision 1: Use a staged ladder

Run the experiment in this order:

1. Synthetic runner preflight: 3 codeword and 3 key-value cases. This validates the lower-level route only.
2. HF IFEval calibration: deterministic candidate sample from `google/IFEval`, with easy-profile supported deterministic checks first.
3. HF GraphWalks calibration: deterministic candidate sample from `openai/graphwalks`, starting with `parents` rows.
4. Primary selected benchmark: per-family full-visible-pass cohorts.
5. Amortization benchmark: repeated tails over the same prefix/capsule to measure when persisted state pays off.
6. Secondary GraphWalks context-compilation analysis: compact evidence controls, analyzed separately from pure KV capsule results.

Rationale: a failed synthetic preflight is a runner problem, a failed full-visible baseline is a model/task problem, and a restored-vs-live mismatch is a capsule problem. The ladder prevents those from being collapsed.

### Decision 2: Use HF source rows and baseline-pass gating

Candidate pools should target:

- IFEval: at least 100 deterministic candidates from `google/IFEval`, easy deterministic checks first.
- GraphWalks: at least 100 deterministic candidates from `openai/graphwalks`, `parents` first, with optional BFS after the parents result is understood.

Primary selected cohorts should target:

- 50 full-visible-passing IFEval cases.
- 50 full-visible-passing GraphWalks `parents` cases.

If a family cannot produce 50 full-visible-passing cases on Gemma 4 12B, record the number available and run the selected subset only as a diagnostic. Do not claim family-level parity if the selected set is too small.

Rationale: KV reuse can only be quality-preserving when the full prompt itself is a valid quality baseline.

### Decision 3: Run paired controls for every selected case

Each selected case should run these controls:

| Control id | Prefix visible to request | Tail only | Persistence | Purpose |
| --- | --- | --- | --- | --- |
| `full_visible` | yes | no | no | Positive quality baseline. |
| `fresh_tail_only` | no | yes | no | Negative leakage/control baseline. |
| `native_live_append` | hidden prefilled state | yes | no | Proves append semantics before persistence. |
| `native_restored_capsule_append` | restored hidden state | yes | yes | Main KV capsule result. |
| `wrong_capsule_negative` | mismatched hidden state | yes | yes | Ensures capsule identity matters and fails closed. |
| `documented_full_prompt_cache_resend` | yes | no | server/cache reuse | Efficiency comparison, not a capsule result. |

GraphWalks secondary controls:

| Control id | Purpose |
| --- | --- |
| `fresh_compact_evidence_only` | Measures role-aware evidence scheduling without hidden KV. |
| `capsule_plus_compact_evidence_tail` | Tests whether capsule state plus visible evidence beats evidence-only. |
| `compact_tail_no_evidence` | Detects prompt-protocol-only repair. |

Rationale: `native_live_append` is the semantic ceiling for restored capsules. If restored fails while live append passes, the persistence layer is broken. If both fail while full visible passes, the append protocol is broken. If fresh evidence-only equals capsule plus evidence, the benefit is context compilation, not hidden KV.

### Decision 4: Record paper-grade data per case and per control

Each record must include:

- Dataset provenance: HF repo, split, revision or snapshot timestamp, source row key/offset, source row hash, license, task family.
- Case transform: stable prefix hash, tail prompt hash, full prompt hash, transform version, prompt protocol version, scorer version, source row fields used, source row fields excluded.
- Prompt sizes: prefix bytes/tokens, tail bytes/tokens, full prompt bytes/tokens, visible evidence bytes/tokens where applicable.
- Runtime: model path, model SHA-256, quantization, tokenizer/template identity or hash, llama.cpp version/hash, runner script hash, hardware, GPU, driver/CUDA where applicable, context size, batch settings, temperature, seed, prediction cap.
- Capsule: capsule route, sequence id, `n_past`, prefix token count, capsule path/hash/bytes, save time, restore time, position/RoPE state availability, cache metadata fields captured/missing.
- Response: raw response hash, normalized response hash, generated token ids hash where available, parsed answer, parse status, truncation flag, stop reason.
- Quality: pass/fail, exact match or constraint pass, GraphWalks precision/recall/F1, IFEval supported check pass/fail, unsupported checks.
- Performance: prompt eval tokens/ms, decode tokens/ms, total wall time, capsule creation amortized and unamortized costs, speedup versus full visible, prompt-token reduction versus full visible.
- Failure class: model weakness, prompt protocol issue, scorer/parser brittleness, session/cache semantic issue, position/compatibility issue, runtime/storage issue, transport issue, or ambiguous.

Rationale: the paper needs raw-enough evidence to support claims and to explain negative results without hand-waving.

### Decision 5: Define success thresholds before running

Use these gates:

- Preflight gate: synthetic restored capsule append must pass all preflight cases and beat fresh tail-only.
- Live append gate: on a 10-case HF slice per family, `native_live_append` must match or exceed full-visible quality on all full-visible-passing cases before running the full matrix.
- Restored capsule semantic gate: restored capsule must match native live append quality within a predeclared non-inferiority margin. Default margin: no more than one additional failure per 50-case family, plus no systematic response-hash divergence on deterministic tasks where token hashes are available.
- Fresh tail sanity gate: fresh tail-only should underperform on prefix-dependent cases. If it does not, the case family is not useful for testing hidden-prefix value.
- Efficiency gate: report both one-shot and amortized costs. A capsule speed claim requires amortized prompt eval time or total wall time improvement versus full visible over repeated tails without violating the semantic gate.

Rationale: success is not "some examples passed." Success is quality parity with a measurable efficiency story.

### Decision 6: Analyze by task family and subset

Required analyses:

- IFEval selected cohort.
- GraphWalks selected cohort.
- All candidate full-visible calibration results.
- Full-visible-pass subset.
- Fresh-tail-fail subset.
- Live-append-pass subset.
- Restored-vs-live mismatches.
- Restored-vs-full-visible mismatches.
- Wrong-capsule failures.
- GraphWalks evidence-only equals capsule-plus-evidence cases.
- Amortization curves for repeated tail counts: 1, 2, 5, 10, and 20 where runtime allows.

Rationale: blended averages would hide exactly the thing Track 02 is trying to study.

### Decision 7: Preserve artifacts with prompt-bearing boundaries

Prompt-bearing artifacts stay under ignored Track 01 benchmark paths. Track 02 commits summaries only:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/hf-kv-capsule-paper-benchmark-2026-06-05/
```

Expected committed files:

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

Rationale: this keeps the repo usable while preserving enough hashes and path pointers to audit raw local artifacts.

## Risks / Trade-offs

- [Risk] Full-visible baseline fails too many GraphWalks cases. -> Mitigation: treat this as model/task limitation, report selected count, and do not make capsule parity claims for that family.
- [Risk] Restored capsule passes synthetic gates but fails HF rows. -> Mitigation: compare against native live append to identify persistence failure versus append/protocol failure.
- [Risk] Fresh compact evidence-only matches capsule plus evidence. -> Mitigation: classify the finding as role-aware context compilation, not pure KV capsule benefit.
- [Risk] Runtime overloads DushyantPC again. -> Mitigation: use staged 10-case gates, monitor active processes, avoid duplicate runs, record partial results under stop rules.
- [Risk] Dataset rows change upstream. -> Mitigation: record HF revision or snapshot timestamp, row hashes, and materialized local candidate hashes.
- [Risk] IFEval unsupported checks distort scores. -> Mitigation: filter primary IFEval to supported deterministic checks and report unsupported checks separately.
- [Risk] Prompt formatting changes create false differences. -> Mitigation: hash prompt protocol/template and keep the transform version fixed across controls.

## Migration Plan

No migration is required. This is a new experiment design. The implementation phase should first add or verify the local runner and artifact schema, then run staged gates before launching the full selected benchmark.

## Open Questions

- Can Gemma 4 12B produce 50 full-visible-passing GraphWalks `parents` cases under the current compact answer protocol?
- Should the first paper run include GraphWalks BFS, or wait until the `parents` result is understood?
- What exact HF revision hash should be pinned once Track 2 materializes candidates?
- Should the amortization benchmark use repeated questions over one shared prefix, or repeated independent tails over multiple prefixes with identical capsule creation cost accounting?
