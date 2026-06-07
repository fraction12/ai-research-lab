# Repeated Work Speed Experiment Design

Date: 2026-06-06

This document defines the follow-up benchmark for testing whether KV capsules plus Code Mode create practical speed and token-efficiency value during repeated local-agent work.

The completed selected-cohort run established semantic viability: restored KV matched native live append on `100 / 100` selected BFCL-derived cases, with zero fresh-tail leaks and zero wrong-capsule leaks. It did not establish a speed win. This experiment is specifically about amortized repeated-work performance.

## Question

When a local model repeatedly performs work against the same stable tool/runtime context, does a restored KV capsule plus Code Mode reduce cumulative wall-clock time and repeated visible-token burden compared with a normal compacted-prompt/tool-call baseline?

## Primary Claim Under Test

KV capsules are not expected to win on every isolated single call. The product claim is amortized:

> For repeated local-agent work over a stable context, a one-time capsule build plus repeated restored tail calls should reduce cumulative repeated context cost versus repeatedly sending compacted context and visible tool descriptions.

This experiment must not be written as "KV capsules are faster" unless the measured cumulative wall-clock result supports that statement at matched quality. The backable claim is a ladder:

1. Semantic claim: restored KV preserves behavior under controls. Already supported by the selected cohort.
2. Token-burden claim: restored KV reduces repeated visible context burden over repeated work.
3. Latency claim: restored KV reduces cumulative wall-clock time after a measured break-even point.

The speed paper can use only the rungs actually supported by the data.

## Pre-Registered Decision Rules

Before running the benchmark, freeze these thresholds:

- Quality floor: each compared system must pass at least `95 / 100` selected tasks, or the comparison is reported as quality-limited.
- Matched-quality speed claim: the KV system can claim a latency win only if its success count is within `2` cases of the baseline and its cumulative wall-clock time including capsule build is lower by task `100`.
- Break-even claim: report the first task index where cumulative KV time including capsule build becomes lower than cumulative baseline time. If no crossing occurs by task `100`, report "no latency break-even by N=100."
- Token claim: report cumulative visible input tokens and visible characters. The KV system can claim a token-burden win if cumulative visible input tokens or visible characters are lower by at least `25%` by task `100`.
- No hidden retries: retries/repairs count toward wall-clock time and token burden.
- No discarded failures: failed tasks stay in the denominator. Do not remove tasks after seeing results unless a pre-run materialization/scoring bug is documented and applied to every system.
- No post-hoc baseline weakening: the compaction baseline configuration, compaction trigger, and prompt/tool templates must be versioned before the run and reused unchanged.

## Systems Compared

### Baseline A: Codex CLI + Ollama/Gemma 4 Compaction Harness + Regular Tool Calls

This is the practical regular local-agent baseline. It must use Codex CLI as the real agent/context-management harness, Ollama as the local model backend, and Gemma 4 as the model. It must use real Codex context compaction, not a hand-written or manually frozen "compact summary."

- Model is loaded through Ollama as `gemma4:12b`.
- Codex CLI maintains the repeated-work session, tool prompt, and compacted thread state.
- Codex CLI decides when to compact according to the pre-registered auto-compaction threshold.
- Compaction is performed through the same Ollama/Gemma 4 route unless the run is explicitly labeled as a hybrid compactor comparison.
- Each task request includes the current Codex-managed live/compacted session state, visible tool descriptions, task-specific user request, and regular tool-call / JSON instruction format.
- The stable context is managed as visible prompt/thread state and is re-sent/re-evaluated as required by the Codex compaction system.
- No hidden prefix state is restored between tasks.

Use the verified DushyantPC Codex profile as the baseline starting point:

- Config path: `C:\Users\Dushyant\.codex\gemma4-ollama-compact.config.toml`
- Codex CLI: `codex-cli 0.137.0` or the exact installed version recorded at run time.
- Model: `gemma4:12b`
- Model provider: `ollama`
- Model context window: `24000`
- Auto-compaction threshold: `18000`
- Local thread store compression: enabled
- Compact prompt: versioned before the benchmark and designed to preserve exact facts, tool names, arguments, and routing rules.

The baseline has already passed a compaction viability smoke test: Codex emitted `context_compacted`, retained `BLUE-CAPSULE-77`, retained the allowed `weather.lookup` tool, retained the `finance.quote` prohibition, and answered correctly from compacted context across subsequent turns. The speed benchmark must rerun and log this kind of compaction evidence for the actual BFCL workload; the smoke test alone is not paper evidence.

### Baseline A Follow-Up After First Run

The first 100-case repeated-work run did not satisfy the compaction-baseline contract:

- Run label: `bfcl-repeated-work-speed-v1`
- Codex/Ollama result: `87 / 100`
- Codex compaction events observed: `0`
- KV + Code Mode result: `100 / 100`

This invalidates the phrase "real Codex auto-compaction baseline" for that run. It remains a useful operational comparison against the tested Codex/Ollama regular-tool route, but it cannot support a claim against Codex compaction.

The primary follow-up Codex baseline must be run as a natural chained-session validation:

- Use a new run label, e.g. `bfcl-repeated-work-codex-natural-chained-v1`.
- Run Codex only; reuse the existing KV result for comparison unless the benchmark design changes.
- Keep the BFCL tasks in a continuing Codex thread through `resume --last` or an equivalent single-thread route.
- Use the normal verified Codex profile, `gemma4-ollama-compact`, with its pre-registered `18000` auto-compaction threshold.
- Accept the run as Baseline A only if the actual BFCL artifacts contain `context_compacted` or an equivalent Codex compaction marker.
- If the run still logs zero compaction events, report "Codex auto-compaction did not trigger under the tested BFCL stream" and do not use it as a compaction baseline.

A forced-threshold Codex run is allowed only as a separately labeled stress test. It must not replace the natural chained-session baseline in the main paper claim.

If Codex/Ollama cannot expose the exact Gemma 4 quantization and GPU-offload profile used by the KV harness, use the closest same-weight route available and label the run as an operational harness comparison, not a pure model-identical mechanism comparison. The preferred setup is same model family, same quantization, same GPU offload profile, same sampling parameters.

The compaction baseline must be strong enough that a reviewer would not call it a strawman. It must include:

- the complete callable tool inventory needed by the selected cohort
- concise but explicit argument schemas
- output contract and JSON/tool-call rules
- enough stable task context to solve the cases without hidden state

The baseline must log real compaction behavior:

- pre-compaction prompt token/character count
- compaction trigger reason
- compaction wall-clock time
- compaction input tokens/characters
- compacted output tokens/characters
- compacted state hash
- post-compaction prompt token/character count
- task indices affected by each compaction artifact

The fallback repo-local compaction harness is allowed only if Codex CLI cannot run the BFCL repeated-work stream reliably or cannot emit auditable compaction records. If used, the fallback must be labeled separately as `ollama_repo_compaction_regular_tools`, not as the Codex baseline.

Not acceptable: a human-authored compact summary, a frontier-model-authored compact summary, a one-off static summary that never changes during the repeated-work session, or any baseline where compaction events cannot be audited.

Run two Codex compaction baselines if feasible:

- `codex_ollama_regular_tools_generous`: Codex context window and compaction threshold set high enough to preserve as much useful context as the route can handle.
- `codex_ollama_regular_tools_budgeted`: threshold matched as closely as possible to the per-turn visible budget we would actually ship.

The paper headline should compare against the generous baseline if both are available. The budgeted baseline is useful product evidence, but the generous baseline is harder for reviewers to dismiss.

### System B: Restored KV Capsule + Code Mode

This is the system under test.

- The stable context/tool/runtime prefix is evaluated once.
- The resulting sequence/KV state is saved as a capsule.
- Each task restores that capsule and appends only the task tail.
- Tool use is expressed through the compact Code Mode contract.
- The one-time capsule build cost is included in cumulative time.

### Optional Ablations

Use these only after the two primary systems are working:

- `code_mode_full_visible`: Code Mode with full visible context each turn, to separate Code Mode from KV restoration.
- `compact_visible_code_mode`: compact visible evidence with Code Mode, to separate compaction from hidden-state reuse.
- `restored_kv_regular_tools`: restored KV with ordinary visible tool-call formatting, to isolate Code Mode's contribution.

## Workload

Use BFCL-derived tasks because they already provide tool-use ground truth and scoring.

Recommended first benchmark:

- Source: the same 100-case selected cohort used in `bfcl-paper-selected-cohort-v1`.
- Task ordering: preserve the cohort order for the first run.
- Chain model-facing execution as repeated work over the same stable tool/runtime context.
- Controls per task:
  - Codex CLI + Ollama/Gemma 4 compaction harness + regular tool call
  - restored KV + Code Mode
  - optional ablations only if budget allows

The benchmark must report both per-task and cumulative metrics. The cumulative view is the important one.

Do not concatenate all 100 tasks into one giant prompt. The repeated-work claim is about repeated requests over the same stable context. Each task should be a separate request so the benchmark measures per-request overhead, context reprocessing, capsule restore cost, and cumulative repeated burden.

Use the selected 100 cases because they already passed the semantic filters:

- Code Mode full visible passed.
- Native live append passed.
- Restored KV passed.
- Fresh-tail and wrong-capsule controls stayed closed.

This makes the speed test a performance comparison over cases where the mechanism is already known to be semantically valid. It is not a new broad BFCL coverage claim.

## Metrics

### Timing

Record all available timing fields:

- wall-clock start/end timestamp per task
- total request latency
- Codex task duration for the baseline, if exposed
- Codex time-to-first-token for the baseline, if exposed
- prompt/prefill evaluation time
- generation/decode time
- capsule build time
- capsule save time
- capsule restore time
- tool-call parse/validation time
- retry/repair time

If a route cannot expose internal timing, still record end-to-end wall-clock time and mark internal fields as unavailable.

Use monotonic timers around the full request path. For paper-facing wall-clock time, include:

- prompt construction
- request dispatch
- model runtime
- capsule build/save/restore when applicable
- output parsing
- scoring
- repairs/retries

Also report a model-runtime-only timing slice when available, but do not use that as the primary user-value metric.

### Tokens

Record:

- visible input tokens per task
- Codex/Ollama reported input tokens per task for the baseline
- output tokens per task
- stable-context tokens repeated per task
- compaction input/output tokens per compaction event
- compaction event count
- total visible input tokens over the full run
- generated tokens over the full run
- amortized capsule prefix tokens over `N` tasks

The key token metric is not just per-call input length. It is cumulative repeated visible-token burden.

### Quality

Record:

- exact tool-call pass/fail
- argument correctness
- invalid JSON/tool-call rate
- hallucinated tool/function names
- repair attempts
- final task success after repair

The speed comparison is paper-usable only at matched quality. If one system is faster because it fails more often, report that as a quality-speed tradeoff, not a speed win.

### Amortization

For each prefix length and task count, compute:

- one-time capsule build cost
- per-task restored cost
- cumulative baseline cost
- cumulative KV system cost including build
- break-even task count
- speedup after break-even
- token reduction after break-even

Compute two cumulative KV curves:

- `kv_including_build`: includes capsule build and save cost. This is the honest from-scratch cost.
- `kv_prebuilt_capsule`: excludes build cost. This represents a long-lived assistant/runtime where the capsule already exists.

The paper must label these separately. The from-scratch curve is the primary scientific comparison; the prebuilt curve is product/runtime analysis.

## Statistical Treatment

Because the same tasks are run under each system, use paired comparisons:

- per-task wall-clock deltas
- per-task visible input token deltas
- per-task success deltas

Report:

- mean, median, p95, and total cumulative time
- bootstrap confidence intervals for cumulative wall-clock delta where practical
- paired win/loss counts by task
- category-level breakdowns, but do not overinterpret small categories

If only one full pass is run, call the result a benchmark run, not a statistically stable estimate. For paper confidence, prefer at least two primary passes with alternated order.

## Reporting Shape

The final benchmark summary should include:

- per-system success rate
- per-system mean/median/p95 wall-clock latency
- per-system cumulative wall-clock time at task counts `1`, `5`, `10`, `25`, `50`, `100`
- visible input tokens at the same checkpoints
- compaction event counts and costs for the baseline
- break-even task count
- failure taxonomy
- route/model/GPU profile metadata
- raw JSONL provenance paths

The most important figure is:

- x-axis: repeated task count
- y-axis: cumulative wall-clock time
- lines:
  - Codex/Ollama compaction baseline
  - KV capsule + Code Mode including capsule build
  - KV capsule + Code Mode after one-time build

## Experimental Controls

The benchmark must control for:

- same selected task set
- same model or explicitly labelled model route difference
- same quantization/offload profile when possible
- same max generated tokens
- same temperature and sampling settings
- same repair budget
- same scoring logic
- same machine state where practical
- warmed model before measured tasks, unless cold-start behavior is explicitly being measured

Run order should be alternated or repeated to reduce heat/load/order bias:

1. Warm-up tasks, excluded from reported timing.
2. Baseline first pass.
3. KV first pass.
4. KV second pass.
5. Baseline second pass.

If total runtime is too high, run one pass each but state that order effects remain a caveat.

Additional hardening controls:

- Run on AC power with no concurrent GPU-heavy jobs.
- Record CPU model, RAM, GPU, driver, VRAM, runtime versions, model hash, quantization, context length, GPU layers, batch size, and sampling parameters.
- Use deterministic decoding where possible: temperature `0` or equivalent greedy settings.
- Use a fixed max output token budget across systems.
- Pre-tokenize or at least pre-count prompts before execution so token reporting does not depend on successful model runs.
- Save every prompt template and generated prompt hash, but keep raw prompt-bearing artifacts in ignored/private paths if they contain benchmark material that should not be committed.

## Poke Holes

These are the ways the result could be misleading, and how to harden it.

### Hole: Codex/Ollama Is Not Model-Identical

If Codex/Ollama uses a different runtime, quantization, prompt template, or GPU offload path than the llama.cpp KV system, differences may reflect serving stack and harness behavior, not only KV capsules.

Hardening:

- Prefer the exact same GGUF/model profile where possible.
- Record model hash, quantization, context size, GPU layers, batch settings, runtime versions, Codex version, Ollama version, and prompt templates.
- If route-identical comparison is impossible, phrase the result as an operational harness comparison, not a pure mechanism comparison.
- Keep the headline baseline practical: do not cripple Codex/Ollama just to make the KV route look cleaner.

### Hole: KV Restore Is Slower Per Call

The selected-cohort run already showed restored KV was slower than native live append in mean latency. The speed claim may fail for `N=1`.

Hardening:

- Make amortization the main claim.
- Include capsule build and restore overhead honestly.
- Report the break-even point even if it is high or not reached.

### Hole: Compaction Baseline Is Too Weak

A fake or weak compaction baseline would make the KV system look better unfairly.

Hardening:

- Use Codex CLI's real automatic compaction system as the primary baseline, not a manually written static summary.
- Version the Codex profile, compaction trigger, and compact prompt before running.
- Require `context_compacted` or equivalent Codex session evidence during the actual BFCL benchmark.
- Log every compaction event and include compaction cost in the baseline wall-clock and token accounting.
- Include compacted context token count.
- If possible, test two Codex compaction sizes: budgeted and generous.
- Do not use frontier-model compaction in the baseline unless the paper explicitly labels it as a hybrid frontier/local baseline.
- If Codex fails and the fallback repo-local Ollama compactor is used, label that run separately and do not describe it as a native Codex-compaction baseline.

### Hole: Code Mode, Not KV, Explains The Win

If Code Mode alone is faster or more accurate, the advantage is not necessarily the capsule.

Hardening:

- Include `code_mode_full_visible` as an ablation if runtime allows.
- Attribute gains separately: Code Mode formatting, hidden-state reuse, or both.

### Hole: Repeated Workload Is Artificial

BFCL tasks are useful but may not represent a personal assistant harness.

Hardening:

- Use BFCL for paper-grade scoring first.
- Later repeat with a small personal-assistant workload: reminders, notes, file triage, log classification.
- Do not overclaim beyond tool-use tasks until that second workload exists.

### Hole: Cache/Warmth Contamination

One route may benefit from OS file cache, model warm state, thermal changes, or GPU state.

Hardening:

- Use warm-up tasks.
- Alternate run order.
- Record GPU utilization, VRAM, and temperature if available.
- Repeat at least two passes for the primary systems.

### Hole: Token Counts Are Not Comparable Across Tokenizers

If Ollama and llama.cpp use different tokenizers or templates, token counts may differ for reasons unrelated to the method.

Hardening:

- Use the model's tokenizer where possible.
- Report visible character counts alongside token counts.
- Keep token claims scoped to visible prompt burden and model route.

### Hole: Baseline Benefits From Codex/Ollama Caching Or Compaction Caching

Codex/Ollama may internally cache prompt prefixes, keep model state warm, keep compacted thread state, or reuse compaction artifacts, which could narrow or erase the apparent KV advantage.

Hardening:

- Record Codex resume/session settings and Ollama keep-alive/cache settings.
- Run a "baseline warm server" condition as the main practical baseline.
- If possible, run a "baseline no prefix cache" diagnostic only as a lower-bound comparison.
- Do not disable useful Ollama behavior in the headline baseline merely to make KV look better.
- Record whether compaction artifacts are reused, regenerated, or incrementally updated.

### Hole: The Systems Have Different Tool Interfaces

If baseline uses regular tool calls and KV uses Code Mode, a speed/quality difference could come from interface design rather than hidden-state reuse.

Hardening:

- Treat the primary comparison as product-system comparison: compacted prompt + regular tools versus KV capsule + Code Mode.
- Include `code_mode_full_visible` if feasible to isolate interface effects.
- In paper language, say "KV capsules plus Code Mode" unless ablations prove KV alone.

### Hole: Selected Cohort Was Filtered Using The KV System

The 100 cases were selected because they passed Code Mode and restored KV gates, so the workload may favor the system under test.

Hardening:

- Be explicit: this is a speed benchmark on the validated cohort, not a general BFCL benchmark.
- Keep quality metrics for the compact baseline; if it underperforms, report that as part of the product-system comparison.
- Later add a non-selected BFCL sample for external-validity checking if needed.

### Hole: "Repeated Work" Is Not Stateful Conversation

Running 100 independent BFCL tasks over one stable context is repeated work, but not the same as a true multi-turn assistant conversation.

Hardening:

- Phrase the workload as repeated independent tool-use requests over stable context.
- Do not claim conversational memory speedup until a separate assistant-style benchmark exists.

## Paper-Safe Outcomes

### Strong Positive

KV capsule + Code Mode reaches matched or better quality, crosses baseline cumulative wall-clock time before `N=100`, and reduces cumulative visible input burden by at least `25%`.

Paper phrasing:

> Restored KV capsules amortize stable context over repeated tool-use tasks, reducing cumulative visible prompt burden and improving repeated-work efficiency after a measured break-even point.

### Mixed Positive

KV capsule + Code Mode reduces visible tokens by at least `25%` but does not beat wall-clock time in this implementation.

Paper phrasing:

> The mechanism reduces repeated visible context and preserves behavior, but current restore overhead prevents a latency win. This identifies runtime restore optimization as the next systems target.

### Negative

KV capsule + Code Mode is slower and does not reduce quality-adjusted cost enough to matter.

Paper phrasing:

> The current implementation establishes semantic preservation but does not yet provide an amortized speed advantage against a strong Codex/Ollama real-compaction local baseline.

This is still useful because it keeps the paper honest and directs engineering work.

## Backable Paper Language

Use one of these, depending on outcome:

- Strong: "On the validated 100-case BFCL-derived repeated-work benchmark, restored KV capsules plus Code Mode preserved task success while reducing cumulative wall-clock time after a measured break-even point and reducing repeated visible prompt burden."
- Mixed: "The system reduced repeated visible prompt burden while preserving behavior, but the current llama.cpp sequence-state restore path did not produce a cumulative latency win by N=100 against a Codex/Ollama real-compaction local baseline."
- Negative: "The selected-cohort result establishes semantic preservation, but the repeated-work benchmark did not show a quality-adjusted speed or prompt-burden advantage over a strong Codex/Ollama real-compaction local baseline."

Avoid:

- "KV capsules are faster" without break-even evidence.
- "Ollama is slower" or "Codex is slower" unless the route-matched Codex/Ollama compaction baseline supports that.
- "General BFCL speedup" because this workload is the validated selected cohort.
- "Local models are better" because the result is about a harnessed local model under a constrained tool-use workload.

## First Implementation Target

Build a benchmark runner that consumes the existing selected-cohort packet and emits one JSONL record per task per system:

```json
{
  "run_label": "bfcl-repeated-work-speed-v1",
  "system": "codex_ollama_regular_tools_generous",
  "case_id": "bfcl:simple:simple_25",
  "task_index": 25,
  "wall_ms": 1234,
  "prompt_eval_ms": 456,
  "generation_ms": 789,
  "capsule_build_ms": 0,
  "capsule_restore_ms": 111,
  "codex_duration_ms": 1234,
  "codex_ttft_ms": 250,
  "codex_compaction_events_seen": 1,
  "codex_last_compaction_marker": "context_compacted",
  "codex_profile": "gemma4-ollama-compact",
  "visible_input_tokens": 321,
  "output_tokens": 42,
  "stable_context_tokens": 0,
  "passed": true,
  "repair_count": 0,
  "model_profile": "gemma4-12b",
  "model_provider": "ollama",
  "runtime": "codex-cli+ollama",
  "metadata": {}
}
```

Then write a summary JSON and Markdown report with cumulative curves and break-even analysis.
