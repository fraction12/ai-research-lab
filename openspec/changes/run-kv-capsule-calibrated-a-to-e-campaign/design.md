## Context

Fixed source-of-truth base:

```text
commit: f3862b9 Record scaled KV capsule benchmark campaign
family1 decision: family1_restored_capsule_semantic_passed
family2 decision: family2_restored_capsule_structured_retrieval_passed
family3 decision: family3_stage_a_full_visible_guard_failed
scaled campaign decision: campaign_completed_without_interpretable_capsule_pass
native route: python ctypes direct libllama C API against pinned b9493/GPT-OSS bundle
canonical route: full prompt/prefix prefill add_special=true; appended tail add_special=false
runner fix required: chunk long prompt prefill/decode around n_batch=512
```

Family 1 and Family 2 showed that restored native state capsules can preserve simple and small structured hidden context. Family 3 and the first scaled campaign stopped at full-visible failures, so they did not test restored-capsule semantics at scale. This change treats those failures as benchmark-instrument feedback and adds a calibration phase before evidence collection.

## Goals / Non-Goals

**Goals:**

- Find capsule-ready benchmark units where full-visible behavior is reliable enough to serve as a quality baseline.
- Freeze promoted units before capsule evidence runs.
- Measure full-visible quality, fresh-tail leakage, native live append sanity, restored-capsule semantic continuation, prompt tokens avoided, state/capsule bytes, and amortized wall-time economics.
- Exercise retrieval scales, then agent-context tasks if retrieval passes.
- Preserve exact model, runner, backend, command, timing, token-count, state-byte, hash, and raw artifact metadata.

**Non-Goals:**

- Do not claim KV cache makes the model inherently smarter.
- Do not run GraphWalks, noiseless-evidence repair, broad mixed benchmarks, or unapproved 500-row stress runs in this change.
- Do not mutate prompts once a unit is promoted into evidence.
- Do not commit raw prompts, raw responses, expected answer strings, token ID arrays, generated token arrays, top-k arrays, or state bytes.
- Do not change tracked Track 01 harness code unless a later OpenSpec update explains why the ignored raw runner is insufficient.

## Research Questions

1. Which prompt/data/output/scoring variants produce reliable full-visible structured retrieval under the pinned native route?
2. For promoted retrieval units, does restored capsule continuation retain full-visible quality and match native live append?
3. What is the highest reliable scale for full-visible, live append, and restored capsule controls?
4. At passing scales, does restored capsule reuse reduce repeated prompt-token/time cost, and where is the break-even query count?
5. After retrieval passes, can a small repo-local agent-context prefix be reused by a restored capsule while retaining quality?

## Campaign Phases

### Phase A: Visible-Baseline Calibration Harness

The campaign tries variants systematically before giving up. Variant axes include:

- Prefix formats: compact key/value blocks, JSONL objects, delimiter records, TSV/CSV-like lines, and compact natural-language facts.
- Query styles: direct lookup, `Return only VALUE`, answer-channel style such as `ANSWER=<value>`, and short no-explanation instructions.
- Decode/scoring settings: deterministic greedy/temp 0, short generation budgets, optional newline stop when available, first-line parsing, answer-contained, exact match, and normalized exact match.
- Scales: 10, 25, 50, 100, and 250 rows, with 250 skipped only for documented runtime/context reasons after lower scales produce interpretable data.
- Query positions: early, middle, late, and seeded random targets where feasible.

Promotion requires full-visible answer-contained 10/10 and strong exact/normalized scoring. If answer-contained is 10/10 but exact is low due harmless formatting, the scorer or output protocol is fixed inside calibration and rerun before promotion. A cheap fresh-tail leakage smoke should be 0/10 before promotion when practical; otherwise it runs immediately after promotion.

Failed calibration attempts are kept as sanitized summaries: variant id, hashes, scale, pass counts, stop/failure class, and notes. Raw prompts and responses remain ignored.

### Phase B: Semantic Capsule Ladder

For each promoted retrieval unit/scale, controls run in order:

1. `native_full_visible_prefix_plus_tail`
2. `native_fresh_tail_only`
3. `native_live_append_tail_only`
4. `native_restored_capsule_append_tail_only`

If an evidence unit fails a gate unexpectedly, it is classified and retained. The campaign may return to Phase A to promote another variant/scale rather than stopping the whole campaign at the first failure.

### Phase C: Scale Ladder and Boundary Search

After a smaller promoted scale works, the campaign pushes upward through 10, 25, 50, and 100 rows if feasible. A 250-row stretch is allowed only if runtime/context behavior remains practical. The campaign reports the highest reliable full-visible scale, highest reliable live-append scale, and highest reliable restored-capsule scale.

### Phase D: Amortization and Economics

For each restored-capsule-passing unit, the runner builds one reusable prefix capsule and restores it for multiple tail queries. It records one-time prefix prefill/save/build cost separately from per-query restore/tail/decode cost.

Break-even curves are calculated for N = 1, 2, 5, 10, 20, 50, and 100:

```text
full_resend_total_ms = N * mean_full_visible_per_query_wall_ms
capsule_total_ms = one_time_prefix_prefill_save_build_ms + N * mean_restored_query_wall_ms
prompt_tokens_avoided = N * prefix_tokens
```

Quality-passing but latency-negative results are valid and must be reported directly.

### Phase E: Small Agent-Context Capsule Benchmark

Phase E runs only after at least one retrieval restored-capsule ladder passes. It uses repo/workspace context such as Track 02 README, relevant experiment summaries, AGENTS/handoff constraints, and compact synthetic task-policy/tool-schema blocks.

Agent-context tasks calibrate full-visible first. If the first design fails, the campaign may revise task format, wording, source subset, answer protocol, or scoring inside calibration. Once an agent-context unit is promoted, it freezes and runs the same ordered controls.

## Runner Requirements

- The only model-bearing CLI mode is an explicit calibrated campaign mode, such as `calibrated-campaign`.
- Raw-only `smoke` and `token-smoke` modes may remain.
- The CLI must not expose server, bridge, Family 1, Family 2, Family 3, GraphWalks, noiseless-evidence, or broad-benchmark execution paths.
- The runner must chunk long prefill/decode calls so prompt batches do not exceed `n_batch=512`.
- Remote PowerShell work should use script files instead of fragile inline command quoting.
- Before DushyantPC sync, the thread reports mode choices, default raw path, output filenames, `py_compile`, help output, stale executable-path grep, and ignored raw-path status.

## Metrics

Raw records may contain audit evidence. Sanitized committed summaries retain:

- phase, variant id, scale, query count, task family, control/stage, case id, and promoted/fail status
- prompt, prefix, tail, expected, response, and raw artifact hashes
- answer-contained, exact-only, and normalized exact booleans
- failure class and output status
- prefix tokens, tail tokens, full prompt tokens, generated token count, and decode budget
- prompt/prefix prefill ms, tail prefill ms where separable, decode ms, and total wall ms
- capsule build/prefix-prefill ms, save ms, restore ms, state bytes requested/restored, capsule byte count
- `n_past_before_tail_append`, `generation_start_pos`, and final position where available
- amortized full-resend and capsule totals for N = 1, 2, 5, 10, 20, 50, 100
- prompt tokens avoided and break-even query count
- highest reliable scale by control
- model, runner, lib, backend, hardware, source, hashes, and command metadata

## Stop / Fallback Rules

- If OpenSpec validation fails, stop and fix before model-bearing work.
- If the raw path is not ignored, stop before sync/model execution.
- If the runner CLI exposes stale execution paths, stop before sync/model execution.
- Calibration may iterate prompt/data/output/scoring variants. Evidence runs may not mutate promoted units.
- If all reasonable calibration variants fail at 10 rows, package that as a model/protocol benchmarkability result and wait.
- For evidence units, if full-visible fails, classify and return to calibration or a different promoted unit.
- If fresh-tail contains any expected answer, quarantine the unit as leakage or scorer issue.
- If live append fails, do not interpret restored capsule for that unit.
- If restored capsule fails after full-visible and live append pass, classify restored-capsule semantic/scale failure for that unit.
- Do not run GraphWalks, broad benchmarks, or 500-row stress tests in this campaign.

## Artifact Layout

Prompt-bearing raw artifacts stay under ignored Track 01 paths:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/
```

Committed Track 02 summaries live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/
```

Required committed files:

```text
README.md
summary.json
phase-results.json
calibration-results.json
case-metrics.json
amortization.json
failure-classifications.json
commands.md
model-info.json
artifact-manifest.json
capsule-contract.md or capsule-contracts.json only for units where restored capsule actually runs
```

If restored capsule does not run, the manifest and summary must say why rather than creating a synthetic capsule contract.

## Risks / Trade-offs

- Calibration can overfit if it keeps mutating after promotion. The freeze rule prevents this.
- Exact-only output can fail even when semantic retrieval works. Promotion prefers exact 10/10, but answer-contained remains the semantic metric and normalized exact is tracked separately.
- Restore overhead can erase wall-time wins even when token savings are real. Economics are reported separately from quality.
- The pinned GPT-OSS/b9493 `ctypes` route remains ABI-risk. Prior parity and Family 1/2 gates justify continuing, but backend metadata must stay explicit.
- Agent-context tasks can leak answers if source names or task phrasing include expected strings. Fresh-tail and sanitation checks guard this.
