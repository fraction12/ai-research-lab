## Context

Fixed source-of-truth base:

```text
commit: 1a35780 Record KV capsule Family 3 gate
family1 decision: family1_restored_capsule_semantic_passed
family2 decision: family2_restored_capsule_structured_retrieval_passed
family3 decision: family3_stage_a_full_visible_guard_failed
native route: python ctypes direct libllama C API against pinned b9493/GPT-OSS bundle
canonical route: full prompt/prefix prefill add_special=true; appended tail add_special=false
```

Family 1 proved native restored capsule continuation for three simple codeword cases. Family 2 proved it for five small fabricated structured-retrieval cases, with mean prefix length around 148 tokens and restored capsule size around 7.29 MB. Family 3 did not test capsule semantics because native full-visible mini-graph retrieval failed 2/3 in Stage A.

This campaign tests the actual Track 02 research goal: whether persistent state capsules can preserve useful reusable context while reducing repeated prompt-token and prompt-time cost under explicit quality gates and fallback boundaries.

## Goals / Non-Goals

**Goals:**

- Measure quality retained versus full visible prompts for reusable prefixes.
- Measure fresh-tail leakage, native live append sanity, and restored capsule continuation before interpreting any capsule result.
- Measure prefix tokens avoided, one-time prefix prefill/save cost, per-query restore/tail/decode cost, capsule size, and amortized break-even query counts.
- Package complete, sanitized summaries even when a stop rule fires early.
- Preserve exact model, runner, backend, command, timing, token-count, state-byte, hash, and raw artifact metadata.

**Non-Goals:**

- Do not frame the result as KV cache making the model inherently smarter.
- Do not run GraphWalks, noiseless evidence repair, broad mixed benchmarks, or a 500-row stress run in this change.
- Do not modify tracked Track 01 harness code unless the campaign cannot proceed without a documented OpenSpec update.
- Do not commit raw prompts, responses, expected answer strings, token ID arrays, generated token arrays, top-k arrays, or state bytes.
- Do not mutate prompts mid-run to rescue a failing phase except inside the explicit Phase 2 full-visible calibration step.

## Research Questions

1. For structured retrieval over reusable prefixes, at what prefix size and query count does restored capsule reuse become economically interesting while retaining full-visible quality?
2. Does restored capsule quality remain comparable to native live append when the same prefix is reused across multiple independent tail queries?
3. Does the measured break-even depend on prefix size, capsule size, or restore overhead?
4. Can any simple reasoning prompt format reach a reliable full-visible baseline before capsule reasoning is attempted?
5. If Phase 1 passes, can a small agent-context prefix from this repo be reused by a restored capsule while retaining quality?

## Decisions

### Decision: Phase 1 is the primary campaign evidence

Phase 1 scales Family 2 rather than increasing reasoning complexity. It uses deterministic synthetic structured prefixes with row counts 25, 100, and 250, one reusable prefix per size, and 10 tail queries per prefix.

Alternatives considered: jump directly to mini graphs or GraphWalks. Rejected because Family 3 already showed graph prompts can fail the full-visible guard, making restored capsule interpretation invalid.

### Decision: One capsule build per prefix size

For restored multi-query Phase 1 runs, the runner builds one prefix capsule for the reusable prefix and restores that same capsule for each query. It records one-time capsule-build cost separately from per-query restore/tail/decode cost.

Alternatives considered: rebuild the capsule per query. Rejected for the main result because it would measure non-amortized setup rather than reusable context economics. If a rebuild diagnostic is ever needed, it must be clearly labeled and excluded from the main amortization result.

### Decision: Ordered controls gate every phase and size

Each unit runs controls in this order:

1. `native_full_visible_prefix_plus_tail`
2. `native_fresh_tail_only`
3. `native_live_append_tail_only`
4. `native_restored_capsule_append_tail_only`

Restored capsule semantics are interpreted only when full visible passes, fresh tail misses, and live append passes for the same unit.

### Decision: Phase 2 is calibration-first reasoning

Phase 2 first runs full-visible-only calibration across tiny one-hop graph/reasoning prompt formats: adjacency table, edge triples table, simple sentence facts, and JSON-ish object/list. A template must reach 100% answer-contained before capsule controls run.

Alternatives considered: rerun Family 3 directly. Rejected because the prior failure suggests prompt format calibration is the mechanism gate before any capsule reasoning claim.

### Decision: Phase 3 depends on Phase 1 restored-capsule quality

Phase 3 runs a small local-agent-like context benchmark only if Phase 1 produces at least one restored capsule pass at a scaled size. It may include source files such as Track 02 README, relevant experiment summaries, AGENTS/handoff constraints, and a compact synthetic policy/tool-schema block.

Alternatives considered: always run Phase 3. Rejected because a failure to scale structured retrieval would make agent-context interpretation premature.

## Metrics

Raw records may contain full evidence needed for audit. Sanitized committed summaries retain:

- phase, unit, size, query count, control, stage, case id, and task family
- prompt/prefix/tail/expected/response hashes
- answer-contained and exact-only booleans
- output status and failure class
- prefix token count, tail token count, full prompt token count, generated token count
- prompt/prefix prefill ms, tail prefill ms, decode ms, and total wall ms
- one-time capsule build/prefix-prefill ms and save ms
- per-query capsule restore ms
- state bytes requested/restored and capsule byte count
- `n_past_before_tail_append`, `generation_start_pos`, and final position where available
- full-resend and capsule amortized totals for N = 1, 2, 5, 10, 20, 50
- prompt tokens avoided and measured break-even query count
- model, runner, lib, backend, hardware, source, hashes, and command metadata

## Stop Rules

- If OpenSpec validation fails, stop and fix before model-bearing work.
- If the runner CLI exposes stale Family 1/2/3, bridge, server, GraphWalks, or broad-benchmark execution modes, stop before sync.
- For any phase, size, template, or task family, if full-visible fails, do not interpret restored capsule for that unit.
- If fresh-tail contains any expected answer, quarantine the unit as leakage or scorer issue.
- If live append fails, do not interpret restored capsule for that unit.
- If restored capsule fails after full-visible and live-append pass, classify restored capsule semantic/scale failure for that unit.
- If Phase 1 reaches 250 rows and runtime/context cost is too high, stop at 100 or the last completed size and package the blocker with exact timing and context evidence.
- Do not run 500 rows, GraphWalks, noiseless evidence repair, or broad benchmarks in this campaign.

## Artifact Layout

Prompt-bearing raw artifacts stay under ignored Track 01 paths:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/
```

Committed Track 02 summaries live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/
```

Required committed files:

```text
README.md
summary.json
phase-results.json
case-metrics.json
amortization.json
failure-classifications.json
commands.md
model-info.json
artifact-manifest.json
capsule-contract.md or capsule-contracts.json only for phases where restored capsule actually runs
```

If restored capsule does not run in a phase, the manifest and summary must say why rather than creating a synthetic capsule contract.

## Risks / Trade-offs

- Scaled structured prompts may expose model or prompt-protocol weakness. Full-visible guards stop those units before capsule interpretation.
- Fresh-tail outputs may accidentally contain a fabricated value. The fresh-tail control quarantines that unit.
- Exact-only output may fail even when the semantic answer is present. Answer-contained is the semantic metric; exact-only remains output-discipline evidence.
- Restored capsule may retain quality but lose time after restore overhead. That is a valid economics result and must be reported without hiding behind token savings.
- The pinned GPT-OSS/b9493 `ctypes` route remains ABI-risk. The campaign relies on prior token smoke, native/server parity, and Family 1/2 gates, but still reports backend metadata and hashes.
- Phase 2 calibration can fail. That is a useful boundary and should not be rescued by changing tasks during capsule evidence collection.

## Migration Plan

Create and validate this OpenSpec change, add ignore coverage for the raw campaign path, build a campaign-only ignored native runner with explicit CLI mode and no stale execution paths, run local syntax and grep sanity checks, report local runner evidence before DushyantPC sync, sync the minimal ignored runner/state, run the campaign on DushyantPC, copy raw artifacts back, package sanitized Track 02 summaries, run sanitation scans and OpenSpec validation, confirm raw ignored status, and commit locally without pushing.

## Open Questions

- Whether 250 rows will remain practical under the pinned GPT-OSS CUDA route; if not, the campaign stops after the last completed size and records the blocker.
- Whether any Phase 2 reasoning template can reach 100% full-visible answer-contained after Family 3's mini-graph full-visible miss.
- Whether Phase 3 agent-context tasks will be valid enough to interpret if Phase 1 passes but Phase 2 calibration fails.
