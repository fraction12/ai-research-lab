## Context

Track 02 now has a 30-case handmade viability result for a local-agent runtime pattern:

- Code-mode full-visible, native live append, and restored KV capsule all passed 30/30 on Gemma 4 12B.
- Fresh tail-only and wrong-capsule negatives stayed negative.
- Restored capsule used only the volatile tail in the visible request while matching live append hashes.
- Direct full-visible tools and compact visible evidence were weaker secondary controls.

That result is good enough to justify a broader test, but not good enough for a paper claim. The next experiment must move the exact same control ladder onto external benchmark-derived tasks and preserve benchmark provenance.

Primary source scan:

- BFCL is the first target because it is a broad function-calling benchmark with single, multiple, parallel, irrelevance, executable, REST/API, multilingual, and multi-turn categories. Sources: https://sky.cs.berkeley.edu/project/berkeley-function-calling-leaderboard/ and https://openreview.net/pdf?id=2GmDdhBdDk.
- BFCL Stage 1 should use the official leaderboard checkpoint reported as `f7cf735`, `bfcl-eval==2025.12.17`, and direct JSONL materialization from the Hugging Face dataset head observed at `61fc0608cfd831fcfbbaa676ebdfef0ed963eeda`. The BFCL dataset card says not to use Hugging Face `load_dataset` for this dataset.
- tau-bench/tau2-bench are harder stateful customer-service agent benchmarks with policies, tools, tasks, simulated users, and database-state scoring. Sources: https://arxiv.org/abs/2406.12045 and https://github.com/sierra-research/tau2-bench.
- ToolSandbox is a stateful conversational tool-use benchmark with explicit state dependency and insufficient-information stressors. Source: https://arxiv.org/abs/2408.04682.
- OpenClaw Code mode is a useful implementation reference for the model-facing shape: expose only `exec`/`wait`, hide the tool catalog, and route nested tool calls through a controlled host bridge. Source: https://docs.openclaw.ai/reference/code-mode.

This design keeps the experiment source-backed while accepting that an adapter is required. The benchmark rows provide the user queries, tool definitions, expected calls, state, and scoring semantics. Our adapter only maps those into the seven controls.

## Goals / Non-Goals

**Goals:**

- Run the exact seven-control Code-mode + KV capsule ladder on non-handmade benchmark-derived tool-use tasks.
- Use BFCL as the first external benchmark because it best matches the tool-catalog and function-calling mechanics of the current harness.
- Stage tau-bench/tau2-bench and ToolSandbox as harder follow-ons after BFCL source materialization, scoring, and smokes pass.
- Preserve benchmark provenance, source revision, license notes, row ids, row hashes, transform hashes, and scorer versions.
- Compare restored KV capsules against native live append and Code-mode full-visible behavior, not against weak or failed baselines.
- Keep negative controls strong enough to prove that visible tails are not leaking the answer.
- Produce artifact manifests and summary tables that can support a research-paper methods/results section.
- Delegate execution across Track 2 and subagents with clear ownership boundaries.

**Non-Goals:**

- Do not invent new benchmark cases for the primary result.
- Do not silently alter benchmark scoring semantics to make the harness pass.
- Do not claim broad model intelligence gains from a tool-use benchmark alone.
- Do not blend handmade viability results with non-handmade benchmark results.
- Do not run tau-bench/tau2/ToolSandbox at full scale until the BFCL adapter and control ladder pass smokes.
- Do not treat the full-prompt resend/cache-prompt route as a KV capsule result; it remains an efficiency comparison only.

## Decisions

### Decision 1: Preserve the seven-control ladder exactly

Every selected benchmark-derived case must run:

| Control id | Purpose |
| --- | --- |
| `direct_full_visible_tools` | Secondary baseline for direct tool-schema exposure. |
| `code_mode_full_visible` | Positive quality baseline for Code-mode with visible stable context. |
| `code_mode_fresh_tail_only` | Negative control for answer/tool leakage in the volatile tail. |
| `code_mode_native_live_append` | Semantic ceiling for tail-only append after a live hidden prefix prefill. |
| `code_mode_restored_kv_capsule` | Main persisted KV capsule condition. |
| `code_mode_wrong_capsule_negative` | Negative control proving capsule identity matters. |
| `compact_visible_evidence_code_mode` | Secondary context-compilation/evidence ablation. |

Rationale: the paper value is continuity from the 30-case handmade result to external tasks. Changing the ladder would make the comparison mushy.

Alternative considered: run only full-visible, fresh-tail, and restored capsule to save time. Rejected because it would collapse protocol failures, persistence failures, and benchmark/model failures into one ambiguous number.

### Decision 2: Use BFCL as the first source, then stage harder agent benchmarks

Stage order:

1. BFCL source audit and adapter dry run.
2. BFCL 10-case smoke across non-live JSONL simple, multiple, parallel, irrelevance, and executable/API buckets.
3. BFCL selected cohort of 50 to 100 full-visible-passing cases.
4. Selected BFCL multi-turn smoke once single-turn scorer fidelity and prefix-dependence labeling are proven.
5. tau-bench/tau2 small smoke once BFCL is clean.
6. ToolSandbox small smoke if its runner/stateful environment can be integrated without changing semantics.

Rationale: BFCL directly tests hidden catalog search, tool selection, function arguments, and distractor/irrelevance behavior. tau-bench and ToolSandbox add richer agent state but also introduce simulated users, mutable environments, and longer runtime.

Alternative considered: jump straight to tau-bench because it is more agentic. Rejected because it adds environment complexity before we have proven the benchmark adapter is honest.

### Decision 3: Treat benchmark adapter transforms as first-class artifacts

For every source row, materialization must record:

- benchmark id and upstream URL
- dataset/repo revision or local checkout commit
- license note
- split/category/domain/task family
- source row id or deterministic offset
- source row hash
- fields used and fields excluded
- stable prefix hash
- volatile tail hash
- full prompt hash
- transform version
- scorer version
- primary eligibility status and reason
- prefix dependency class
- expected and parsed call/argument hashes

Rationale: non-handmade does not mean no transform. It means the transform is deterministic, documented, and auditable.

Alternative considered: store only generated prompt files. Rejected because prompt files alone cannot prove source fidelity.

### Decision 4: Define stable prefix versus volatile tail per benchmark

BFCL mapping:

- Stable prefix: Code-mode instructions, hidden tool-catalog bridge, BFCL function/tool definitions, tool namespace metadata, benchmark category notes, and output contract.
- Volatile tail: the source user query and any per-turn current user message.
- Scorer: BFCL AST/execution/category scorer where available, or a narrow deterministic adapter that preserves expected function names and argument constraints.

tau-bench/tau2 mapping:

- Stable prefix: domain policy, tool list/API docs, initial database state reference, Code-mode bridge, and agent instructions.
- Volatile tail: current simulated user turn or task-specific user request.
- Scorer: benchmark state checker or task success signal.

ToolSandbox mapping:

- Stable prefix: sandbox tool inventory, initial state, scenario constraints, Code-mode bridge, and state-checking instructions.
- Volatile tail: current conversational user turn.
- Scorer: ToolSandbox stateful evaluation result.

Rationale: our claim is about reusable stable context plus volatile task tails. This split has to be explicit for each benchmark.

Alternative considered: put only tool schemas in the stable prefix. Rejected because policy/state/context are part of what a long-running local agent repeatedly carries.

### Decision 5: Gate primary claims on full-visible Code-mode pass

Candidate rows first run `code_mode_full_visible`. Primary comparison cohorts are selected from rows where full-visible Code-mode passes the benchmark scorer. Rows that fail full-visible are still useful diagnostics, but they cannot support a quality-preserving KV claim.

Rationale: a restored capsule cannot be blamed for failing a task the model cannot solve with the complete prompt.

Alternative considered: include all benchmark rows and compare aggregate rates. Rejected because it would mix model weakness with capsule semantics.

### Decision 6: Use predeclared success, failure, and stop rules

Required gates:

- Source gate: benchmark source, license, scorer, and transform are recorded before model runs.
- Adapter gate: non-model dry run verifies prompt/control generation and scoring on at least five rows.
- Smoke gate: 10 external rows pass through all controls before any larger run.
- Semantic gate: on full-visible-passing cases, `code_mode_restored_kv_capsule` must match `code_mode_native_live_append` within the predeclared margin.
- Negative gate: `code_mode_fresh_tail_only` and `code_mode_wrong_capsule_negative` must not pass on prefix-dependent cases.
- Efficiency gate: token and timing wins are reported separately from quality and must include capsule create/save/restore overhead.

Default non-inferiority margin for the first BFCL selected cohort: no more than one restored-only quality failure per 50 full-visible-passing cases, with all restored failures classified.

Stop rules:

- Stop and fix if full-visible Code-mode fails due to adapter/scorer bug.
- Stop before model smoke if native or faithful category-specific BFCL scoring is not proven for the sampled category.
- Stop and mark diagnostic-only if prefix dependency cannot be classified for a row or category.
- Stop and classify if native live append fails while full-visible passes.
- Stop and classify if restored fails while native live append passes.
- Stop and exclude a source bucket from primary claims if fresh tail-only passes because the tail leaks the answer.
- Stop broad scaling if alias normalization, host-filled arguments, or host answer finalization becomes the dominant success mechanism.
- Stop long runs if DushyantPC shows active duplicate Python/llama processes or thermal/crash instability.

Rationale: the result needs to tell us which layer failed, not just whether the final number is lower.

### Decision 7: Record paper-grade per-control data

Each record must include:

- model path, model hash where practical, quantization, tokenizer/template identity, llama.cpp version/hash, runtime route, GPU/CUDA/driver notes, context size, seed, temperature, max prediction tokens
- per-control prompt bytes/tokens, stable prefix tokens, volatile tail tokens, visible prompt tokens, generated tokens
- capsule route, sequence id, n_past, capsule bytes, capsule path/hash, save time, restore time, restored token count, live/restored generated-token hash where available
- raw response hash, normalized response hash, parsed tool calls, executed tool path, final answer source, parser status, truncation/stop reason
- `template`, `template_alias`, `alias_registry_version`, `host_filled_args`, `primary_eligible`, `primary_eligibility_reason`, and `prefix_dependency_class`
- benchmark scorer result, pass/fail, expected tool calls/arguments as allowed by source scorer, unsupported scorer features, and failure class
- prompt eval time, decode time, total wall time, one-shot cost, amortized cost at repeated-tail counts

Rationale: Track 02 has repeatedly found that aggregate pass rates hide the real mechanism. The records need to make failures inspectable.

### Decision 8: Delegate execution through a hub-and-spoke plan

Execution ownership:

- Workspace Manager: owns the goal, stop rules, decisions, and final synthesis.
- Track 2: owns skeptical review, claim boundaries, and quality gates.
- Subagent A: benchmark source/provenance scout.
- Subagent B: BFCL adapter and scorer integration.
- Subagent C: runner/ops and DushyantPC dry runs.
- Subagent D: analysis, tables, figures, and paper-methods notes.

Rationale: this is large enough that one thread doing everything invites drift. The orchestration thread should keep the experiment shape stable while agents handle bounded pieces.

Alternative considered: send all work to Track 2. Rejected because Track 2 should remain the paper/research owner, not the only implementation worker.

### Decision 9: Preserve artifact boundaries

Committed Track 02 summary path:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/
```

Ignored raw benchmark path:

```text
research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/
```

Expected committed files:

```text
README.md
summary.json
source-audit.json
candidate-calibration.json
case-metrics.json
control-matrix.json
failure-classifications.json
amortization.json
model-info.json
commands.md
artifact-manifest.json
paper-methods-notes.md
disallowed-claims.md
```

Rationale: raw prompts and large outputs stay local; summaries carry enough hashes and metadata to audit.

## Risks / Trade-offs

- [Risk] BFCL adapter accidentally becomes a handmade benchmark. -> Mitigation: preserve source rows, row hashes, benchmark categories, expected calls, and scorer versions; document every transform.
- [Risk] BFCL is not long-horizon enough. -> Mitigation: use it as the first external tool-calling gate, then move to tau-bench/tau2 and ToolSandbox for stateful-agent stress.
- [Risk] External benchmark scorers are difficult to integrate with local Code-mode output. -> Mitigation: run a scorer-only dry run before model runs and record unsupported scorer features.
- [Risk] Fresh tail-only passes many cases because BFCL queries contain enough information without the stable prefix. -> Mitigation: mark those rows as non-prefix-dependent and exclude them from KV capsule primary claims.
- [Risk] Full-visible baseline pass count is too low on Gemma 4 12B. -> Mitigation: report the benchmark as diagnostic and do not claim restored capsule parity for that family.
- [Risk] DushyantPC crashes or duplicates long runs. -> Mitigation: stage smokes, poll active processes before launch, flush JSONL per row, and resume only from validated artifacts.
- [Risk] Host-side finalization or alias normalization overstates model ability. -> Mitigation: record final source, template alias, exact tool path, parser status, and bounded whitelist normalization.
- [Risk] Efficiency numbers look worse one-shot due to capsule save/restore overhead. -> Mitigation: report one-shot and amortized repeated-tail curves separately.

## Migration Plan

No migration is required. This is a new experiment lane. Implementation should:

1. Validate the OpenSpec plan.
2. Build source-audit and candidate-materialization commands.
3. Add BFCL adapter/scorer dry runs.
4. Run local no-model tests.
5. Run DushyantPC 10-case smoke.
6. Run selected BFCL cohort only after smoke gates pass.
7. Decide whether tau-bench/tau2 or ToolSandbox is the next source based on BFCL failure modes.

Rollback is simple: do not use nonhandmade benchmark summaries for claims if gates fail. Raw artifacts remain ignored and can be deleted without affecting source.

## Open Questions

- Which exact BFCL version/source checkout should be pinned for the first run?
- Should the first selected cohort target 50 or 100 full-visible-passing BFCL rows?
- Which BFCL categories are prefix-dependent enough for the KV capsule question, and which should be diagnostic only?
- Should tau-bench or ToolSandbox be the second benchmark after BFCL?
- How much alias normalization is acceptable before the result should be classified as host repair rather than model success?
