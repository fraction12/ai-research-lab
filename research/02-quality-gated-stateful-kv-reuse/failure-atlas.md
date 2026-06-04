# Track 02 Failure Atlas

Date: 2026-06-04

This atlas is the working map for failed or inconclusive attempts in the quality-gated persistent KV reuse lane. Its job is to keep the research honest: what failed, what the evidence actually says, what it does not prove yet, and what control should come next.

The atlas is intentionally failure-first. Positive speed results matter, but Track 02 only becomes paper-worthy if the repo can explain when reused state preserves full-prompt quality, when it silently drifts, and how a local runtime should respond.

## Scope

Track 02 uses Track 01 as the evidence harness. The current implementation surface is:

| Surface | Path | What it contributes | Current limitation |
| --- | --- | --- | --- |
| Flashcache wrapper | `research/01-ssd-native-inference-current/flashcache/wrapper.py` | Cache-aware local-agent request path, cache miss/hit telemetry, full-prompt fallback on cache errors. | Quality routing is not implemented; fallback is runtime-error based, not answer-risk based. |
| Cache identity and manifests | `research/01-ssd-native-inference-current/flashcache/cache.py` | Compatibility key over namespace, model identity, server version, context size, settings, stable-prefix hash, and block hashes. | No semantic compatibility key for prompt-template position, task family, or answer contract. |
| llama.cpp slot helper | `research/01-ssd-native-inference-current/flashcache/llama_cpp.py` | Starts `llama-server`, calls `/completion`, saves/restores slots. | Uses backend slot semantics as an evidence tool; not a custom KV layout. |
| Correctness runner | `research/01-ssd-native-inference-current/benchmarks/flashcache_correctness_eval.py` | Runs full prompt vs session-tail, records raw responses/timings, scores IFEval/MRCR/GraphWalks, supports baseline-pass selection. | Only exposes `full` and `session-tail`; visible-prefix and stronger-hint controls currently require derived local case files. |
| Track 02 experiment record | `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/` | Setup manifest, command shapes, and control feasibility for the six GraphWalks cases. | Recorded in this checkout as setup only; live control summaries/classifications are not present here yet. |

## Taxonomy

Use these labels for every failed or inconclusive result. Prefer `ambiguous` when controls are missing.

| Failure class | Meaning | Confirming evidence | Next action |
| --- | --- | --- | --- |
| `model_weakness` | The model cannot reliably solve the task even with the full prompt. | Full-prompt replay fails, or a stronger model succeeds where the current model is unstable. | Do not use this model/task pair for cache semantics claims. |
| `prompt_protocol_issue` | The prompt shape, chat template, answer contract, or tail wording changes the task. | Visible-prefix/session-formatted control fails like session-tail, or stronger task hints repair the answer. | Fix protocol before judging cache semantics. |
| `scorer_parser_brittleness` | The raw answer is acceptable but extraction/scoring rejects it. | Raw response contains the right answer; parsed node set/check result is wrong due to format assumptions. | Fix scorer/parser or add a scoring-specific control. |
| `session_cache_semantic_issue` | Hidden/restored prefix state is not equivalent enough to visible full prompt for the task. | Full replay and visible-prefix controls pass, but restored session-tail fails with stable restore telemetry. | Add fallback, visible anchors, or partial recompute for this task family. |
| `position_compatibility_issue` | Position, template, tokenizer, context length, or cache key compatibility invalidates reuse. | Prompt hashes/positions/template differ, restore token counts are inconsistent, or context settings differ. | Strengthen compatibility keys or rebuild prefix state. |
| `runtime_storage_issue` | The backend, slot file, server, model loader, or storage path fails independently of semantics. | Server load failure, save/restore error, corrupted slot, path-length issue, missing model, or telemetry anomaly. | Treat as infrastructure; rerun only after runtime is repaired. |
| `performance_non_result` | Speed evidence is absent, negative, or not yet meaningful at this prefix size/mode. | Restore cost cancels savings, prompt size is too small, or no quality gate was run. | Change workload scale or report as a boundary, not a failure of the idea. |
| `ambiguous` | The evidence does not isolate cause. | One or more required controls are missing. | Run the smallest discriminating control. |

## Current Evidence Ledger

| ID | Test / implementation | Evidence path | Question asked | Outcome | Current classification |
| --- | --- | --- | --- | --- | --- |
| F-001 | Early mixed correctness smoke, raw `/completion` | `research/01-ssd-native-inference-current/benchmarks/datasets/flashcache-correctness-smoke-2026-06-03/` | Can the runner produce paired full/session-tail responses and score them? | Pipeline worked, but raw answers were not a fair quality harness: full-prompt pass rate was 0/3 and GraphWalks/MRCR were semantically weak. | `prompt_protocol_issue` plus `model_weakness`, not cache evidence. |
| F-002 | Early mixed correctness smoke, JSON answer protocol | Same as F-001 | Does constrained JSON answer improve answer hygiene? | JSON protocol improved IFEval session-tail on one case, but full-prompt baseline was still 0/3 overall; GraphWalks session-tail had malformed/truncated JSON. | `prompt_protocol_issue`; GraphWalks/MRCR remain `ambiguous`. |
| F-003 | First baseline-pass ladder, 12 candidates | `research/01-ssd-native-inference-current/benchmarks/datasets/flashcache-baseline-pass-ladder-2026-06-03/` | If we only test cases full prompt can solve, does session-tail preserve quality? | Only 3/12 candidates passed full prompt; all selected cases were IFEval and session-tail passed 3/3 with prompt-time savings. GraphWalks and MRCR did not enter the parity set. | Positive but narrow; GraphWalks/MRCR full-baseline failures are `model_weakness` or `prompt_protocol_issue`. |
| F-004 | Large-prefix speed ladders | `research/01-ssd-native-inference-current/docs/flashcache-system-report.md`; `research/01-ssd-native-inference-current/docs/benchmark-graphs.md` | Can persistent local state reduce prompt-processing time on large stable-prefix agent fixtures? | Strong speed signal: session-tail on 64 KB Printy-style fixture recovered about 79.8% prompt-processing savings. | Speed evidence only; quality remains `ambiguous` until paired correctness passes. |
| F-005 | Correctness parity, 107 candidates, JSON answer hints | `research/01-ssd-native-inference-current/benchmarks/datasets/flashcache-correctness-parity-2026-06-03/` | On a larger full-passing selected set, does session-tail preserve full-prompt quality? | Full gate selected 42/107 cases. Session-tail passed 31/42 overall, 31/36 IFEval, and 0/6 selected GraphWalks. | Central Track 02 failure: GraphWalks are `ambiguous` between prompt protocol, session/cache semantics, and position compatibility until controls run. |
| F-006 | Six-case GraphWalks ladder setup | `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/` | Can we isolate the six full-passing/session-tail-failing GraphWalks cases for focused attribution? | Prompt-bearing six-case inputs were re-materialized locally; dry-run command plumbing worked; no live model answers are recorded in this checkout for the focused controls. | Setup complete; failure classes remain `ambiguous`. |
| F-007 | Control-surface feasibility | `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/control-feasibility.md` | Do we need Track 01 harness changes before running focused controls? | Existing CLI covers full replay, session-tail replay, reset/restore telemetry, and scorer/parser checks. Visible-prefix and stronger-tail controls can be expressed with derived local case files. | No harness change needed for first attribution pass. |

## Case-Level Failure Map

### Correctness parity selected failures

Source: `research/01-ssd-native-inference-current/benchmarks/datasets/flashcache-correctness-parity-2026-06-03/summary.json` and `raw/easy-mixed-candidates-107-gpt-oss-20b-json-answer-hints-parity-scores.json`.

| Case | Family | Full score | Session-tail score | Observed failure | Current class | Needed control |
| --- | --- | ---: | ---: | --- | --- | --- |
| `ifeval-1675` | instruction following | 1.0 | 0.0 | Session-tail included forbidden word `heute`. | `prompt_protocol_issue` or `session_cache_semantic_issue` | Visible-prefix/session-formatted IFEval control. |
| `ifeval-2028` | instruction following | 1.0 | 0.0 | Session-tail included forbidden word `yes`. | `prompt_protocol_issue` or `session_cache_semantic_issue` | Visible-prefix/session-formatted IFEval control. |
| `ifeval-2324` | instruction following | 1.0 | 0.0 | Session-tail violated no-comma constraint. | `prompt_protocol_issue` or `session_cache_semantic_issue` | Visible-prefix/session-formatted IFEval control. |
| `ifeval-2811` | instruction following | 1.0 | 0.0 | Session-tail included forbidden word `yo`. | `prompt_protocol_issue` or `session_cache_semantic_issue` | Visible-prefix/session-formatted IFEval control. |
| `ifeval-3401` | instruction following | 1.0 | 0.0 | Session-tail JSON parse error. | `scorer_parser_brittleness` or `prompt_protocol_issue` | Inspect raw output; retry with output-budget/template control. |
| `graphwalks-6` | reasoning over prefix | 1.0 | 0.0 | Session-tail produced prose/noisy token set instead of the parent node set. | `ambiguous` | Six-case full replay, visible-prefix control, stronger hints, reset/restore sanity. |
| `graphwalks-9` | reasoning over prefix | 1.0 | 0.0 | Session-tail produced prose/noisy token set instead of the parent node set. | `ambiguous` | Same six-case ladder. |
| `graphwalks-11` | reasoning over prefix | 1.0 | 0.0 | Session-tail predicted `0a4d55a8`/`node` instead of `d3d9446802`. | `ambiguous` | Same six-case ladder. |
| `graphwalks-13` | reasoning over prefix | 1.0 | 0.0 | Session-tail predicted `0a4d55a8`/`node` instead of `1679091c5a`. | `ambiguous` | Same six-case ladder. |
| `graphwalks-16` | reasoning over prefix | 1.0 | 0.0 | Session-tail predicted `0a4d55a8`/`node` instead of the five-node parent set. | `ambiguous` | Same six-case ladder. |
| `graphwalks-19` | reasoning over prefix | 1.0 | 0.0 | Session-tail produced prose/noisy token set instead of the parent node set. | `ambiguous` | Same six-case ladder. |

## What We Have Tried

### Prompt and answer protocol

- Raw `/completion` responses were too unconstrained for a reliable quality harness.
- JSON answer protocol improved answer hygiene but did not solve GraphWalks or MRCR in the early smoke.
- Dataset-specific answer hints improved the larger full-prompt gate enough to select 42 passing cases, including six GraphWalks cases.
- Tail-only/session-tail still failed all selected GraphWalks cases, so answer formatting alone is not enough.

### Baseline-pass gating

- The baseline-pass ladder is the right evaluation shape: run session-tail only after full prompt passes.
- The first 12-case ladder produced only IFEval selected cases, which was useful but too narrow.
- The 107-candidate parity run produced enough selected cases to expose task-family split: IFEval mostly survived; GraphWalks collapsed.

### Session and cache mechanics

- The current session-tail runner primes the stable prefix, saves a llama.cpp slot, restores it, and then calls `/completion` on only the tail prompt.
- Response records preserve prompt hashes, timing, slot filenames, save/restore responses, raw output, extracted answer, and parse errors.
- This is enough to investigate failure attribution, but not enough to claim semantic equivalence.

### Track 02 focused ladder

- The six GraphWalks cases are fixed: `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`.
- The current Track 02 folder records setup and control feasibility only.
- If future live-control artifacts exist only on DushyantPC or in ignored paths, import their summaries, commands, hashes, and classifications before updating this atlas.

## Controls That Must Fill The Gaps

Run these in order. Stop broad benchmark work until this table is populated.

| Control | What it decides | Required artifact | Classification rule |
| --- | --- | --- | --- |
| Full-prompt replay variance | Whether the local model still solves the six cases reliably. | `full-replay-*-responses.jsonl`, `full-replay-*-scores.json` | Failure here means `model_weakness`; do not test cache semantics on that case. |
| Visible-prefix/session-formatted control | Whether session-style wording breaks the task even when the prefix is visible. | Derived visible-prefix case JSONL plus full-mode responses/scores. | Failure like session-tail means `prompt_protocol_issue`. Passing here keeps cache semantics in play. |
| Stronger tail instructions / answer hints | Whether the tail lacks enough task-specific guidance. | Derived stronger-tail case JSONL plus session-tail responses/scores. | Repair here means `prompt_protocol_issue`; no repair keeps semantic/position suspects alive. |
| Reset/restore sanity | Whether save/restore telemetry is stable and compatible. | Session setup telemetry, save/restore responses, slot filenames, cache dirs. | Errors or inconsistent restore metadata mean `runtime_storage_issue` or `position_compatibility_issue`. |
| Scorer/parser brittleness check | Whether raw output is actually correct but rejected. | Joined raw response, extracted answer, parsed node set, truth, precision/recall/F1. | Correct raw answer with parse failure means `scorer_parser_brittleness`. |
| Stronger-model control | Whether failures are local-model brittleness rather than reuse semantics. | Model info, command, raw responses, scores. | Stronger model full-prompt success with local failure means `model_weakness`; stronger session-tail failure after full/visible controls pass strengthens `session_cache_semantic_issue`. |

## Research Implications So Far

1. Speed is real but insufficient. The 64 KB session-tail result is encouraging, but the 0/6 GraphWalks parity result is the paper-critical failure.
2. Task-family split is not optional. IFEval and GraphWalks cannot be averaged into one comforting score.
3. Full-prompt gating is mandatory. Without it, model weakness and cache drift collapse into the same bucket.
4. Prompt protocol is a first-class system boundary. Raw completions, JSON answer constraints, chat templates, and tail wording can all change the result.
5. The likely paper contribution is not "we cache KV on SSD." It is a methodology and runtime policy for deciding when persistent local state reuse is safe, when to repair it, and when to fall back.

## Update Rules

When adding a new result:

1. Add an evidence-led row to the Current Evidence Ledger.
2. Link exact artifact paths for raw responses, scores, commands, prompt hashes, model info, and summaries.
3. Record model name, quantization, backend, hardware, context size, predict budget, temperature, and command line.
4. Fill the Case-Level Failure Map if the result changes a specific case classification.
5. Leave the class as `ambiguous` unless a control actually rules out competing causes.
6. Mark unrecorded side-run notes as `not atlas-grade` until their artifacts are copied into a stable result path.

