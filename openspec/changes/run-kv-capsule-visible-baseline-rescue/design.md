## Context

Current base:

```text
commit: bfd02be Record calibrated KV capsule A-to-E campaign
prior positives: Family 1 restored capsule 3/3, Family 2 restored capsule 5/5
prior boundary: calibrated A-to-E campaign stopped at Phase A, six 10-row full-visible retrieval variants failed promotion
native route: Python ctypes direct libllama C API against pinned b9493/GPT-OSS bundle on DushyantPC CUDA backend
canonical route: full prompt/prefix prefill add_special=true; appended tail add_special=false
```

The previous result is a benchmarkability boundary, not a capsule failure. This campaign starts smaller and adds route controls so a visible-baseline failure can be attributed more precisely.

## Goals / Non-Goals

**Goals:**

- Find the smallest reliable full-visible retrieval unit on the pinned native route.
- Distinguish task/prompt/model weakness from native-route/protocol weakness.
- Run restored capsule controls only after full-visible and live append pass on a frozen unit.
- Report quality, timing, state size, and amortization for passing restored-capsule units.
- Preserve raw evidence under ignored Track 01 paths and commit only sanitized summaries.

**Non-Goals:**

- Do not claim KV cache makes the model smarter.
- Do not interpret restored capsule results unless full-visible and live append pass.
- Do not run GraphWalks, broad benchmarks, noiseless-evidence repair, or new model downloads.
- Do not mutate prompts/scorers inside evidence after promotion.

## Phases

### Phase A: Visible-Baseline Rescue

Phase A runs full-visible calibration only. It tries 1, 3, 5, and 10 rows, querying every row. It may attempt 15 and 25 rows only after a smaller scale passes. The campaign tries:

- prior Family 2 positive-control style
- ultra-simple codebook lines such as `K03 -> VALUE03`
- XML/tagged records
- short TSV/two-column records
- natural sentence needles
- explicit single-record and three-record sanity cases

Prompt/output protocols include value-only, `VALUE=<value>` answer-channel output, first-line parsing, and deterministic decode budgets 4, 8, 16, and 32 where useful. A unit promotes only when full-visible answer-contained is 100% and exact or normalized scoring is 100%, or an explicitly fixed answer-channel parser is rerun to 100%.

### Phase B: Route-Control Audit

Route controls run for the best prompt families and for known positives when cheap:

- native ctypes full-visible route
- Family 1 simple codeword positive control
- Family 2 small structured-retrieval positive control, as close to the prior passed shape as possible
- installed llama.cpp alternate route, such as llama-cli or llama-server completion, only if already available and practical

If Family 1/2 positives pass but rescue units fail, the likely boundary is task/prompt/model retrieval weakness. If an alternate route passes the exact same prompt while ctypes fails, suspect native runner/protocol/ABI issue. If all routes fail, suspect model/task mismatch.

### Phase C: Capsule Evidence Ladder

For each promoted unit, controls run in order:

1. `native_full_visible_prefix_plus_tail`
2. `native_fresh_tail_only`
3. `native_live_append_tail_only`
4. `native_restored_capsule_append_tail_only`

The 1-row or 3-row promoted unit runs first if available. Larger scales are attempted only after the smaller promoted scale works.

### Phase D: Minimal Amortization

For restored-capsule-passing units, the runner builds one reusable prefix capsule and restores it across tail queries. It reports one-time capsule build/save cost, per-query restore/tail/decode cost, capsule bytes, state bytes, and break-even N = 1, 2, 5, 10, 20, 50, 100.

## Runner Requirements

- One model-bearing CLI mode, for example `campaign`.
- Raw-only `smoke` and `token-smoke` modes may exist.
- No executable bridge, Family 1/2/3 benchmark mode, GraphWalks, broad benchmark, or noiseless-evidence path.
- Route-control helpers are allowed only inside the focused campaign or explicit diagnostics and must be documented.
- Use foreground held SSH or a proven launcher on DushyantPC.
- Report local and remote CLI, path, py_compile, help, stale-grep, and ignored raw-path sanity before model-bearing execution.

## Metrics

Sanitized committed summaries retain:

- phase, variant id, scale, query count, task family, control, case id
- prompt/prefix/tail/expected/response hashes
- answer-contained, exact-only, normalized exact, output status, failure class
- prefix, tail, full prompt, and generated token counts
- prompt/prefix prefill ms, tail prefill ms, decode ms, total wall ms
- capsule build/save/restore ms, capsule bytes, state bytes requested/restored
- `n_past_before_tail_append`, `generation_start_pos`, final position
- route-control status and alternate-route availability
- break-even curves for passing restored-capsule units

## Stop Rules

- Stop before model-bearing work if OpenSpec validation fails, raw path is not ignored, stale CLI paths exist, or GPU/native route is unavailable.
- Do not stop at the first failed prompt format.
- If single-record and three-record full-visible sanity both fail under the native route, run route controls and package a native/model promptability blocker.
- If no variant reaches promotion by 5 rows but 1/3 rows pass, run capsule controls on the smaller promoted unit and package the scale boundary.
- If no variant reaches promotion at any scale including 1 and 3 rows, package model/route benchmarkability failure and do not run restored capsule.

## Artifact Layout

Prompt-bearing raw artifacts:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-visible-baseline-rescue-2026-06-04/raw/
```

Committed Track 02 summaries:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-visible-baseline-rescue-2026-06-04/
```

Required committed files:

```text
README.md
summary.json
phase-results.json
calibration-results.json
case-metrics.json
route-controls.json
amortization.json
failure-classifications.json
commands.md
model-info.json
artifact-manifest.json
capsule-contract.md or capsule-contracts.json only if restored capsule runs
```
