# Non-Handmade Code-Mode KV Agent Benchmark Plan 2026-06-05

## Purpose

Move the successful 30-case handmade Code-mode + KV capsule control ladder onto external benchmark-derived tool-use tasks. This is the bridge from "strong internal viability result" to "paper-grade evidence."

## Research Question

Can a local model using a Code-mode hidden-tool runtime plus restored KV capsules preserve full-visible tool-use quality on non-handmade benchmark tasks while reducing repeated visible prompt tokens and maintaining strict negative controls?

## Hypotheses

- H1: On rows where Code-mode full-visible passes, restored KV capsule append will match native live append quality within a predeclared non-inferiority margin.
- H2: Restored KV capsule append will reduce visible prompt tokens versus Code-mode full-visible resend because stable tool/policy/context material is not resent in the volatile tail.
- H3: Fresh tail-only and wrong-capsule negative controls will fail on prefix-dependent rows, showing the tail is not leaking the answer.
- H4: Direct full-visible tool exposure will remain weaker than Code-mode on some tool-selection or multi-step rows, supporting a runtime-harness value claim separate from the KV claim.
- H5: Compact visible evidence may repair some rows, but those gains must be reported as context compilation unless capsule-plus-tail beats evidence-only under controls.

## Benchmark Sources

First target: BFCL.

Reason: BFCL is the closest public benchmark to our control ladder. It stresses function/tool selection, arguments, multiple calls, parallel calls, irrelevance, executable/API-style tasks, and multi-turn categories. It is the correct first non-handmade suite before jumping into full stateful simulated-agent environments.

Follow-on targets:

- tau-bench/tau2-bench: harder customer-service agent tasks with tools, policies, simulated users, and state/database scoring.
- ToolSandbox: stateful conversational tool-use benchmark with state dependency, canonicalization, and insufficient-information stressors.

Primary source anchors:

- BFCL project: https://sky.cs.berkeley.edu/project/berkeley-function-calling-leaderboard/
- BFCL paper: https://openreview.net/pdf?id=2GmDdhBdDk
- BFCL leaderboard/package checkpoint: `f7cf735`, `bfcl-eval==2025.12.17`
- BFCL Hugging Face data head observed for direct JSONL materialization: `61fc0608cfd831fcfbbaa676ebdfef0ed963eeda`
- tau-bench paper: https://arxiv.org/abs/2406.12045
- tau2-bench repo: https://github.com/sierra-research/tau2-bench
- ToolSandbox paper: https://arxiv.org/abs/2408.04682
- OpenClaw Code mode reference: https://docs.openclaw.ai/reference/code-mode

Stage 1 BFCL scope:

- Start with non-live JSONL categories.
- Read JSONL directly; do not use Hugging Face `load_dataset`.
- Treat live/agentic categories as deferred until non-live scorer fidelity and prefix-dependence labeling are proven.

## Exact Control Ladder

Run every selected external case through:

1. `direct_full_visible_tools`
2. `code_mode_full_visible`
3. `code_mode_fresh_tail_only`
4. `code_mode_native_live_append`
5. `code_mode_restored_kv_capsule`
6. `code_mode_wrong_capsule_negative`
7. `compact_visible_evidence_code_mode`

The controls must not be renamed, dropped, or replaced without recording the reason.

## Stable Prefix And Tail Split

BFCL:

- Stable prefix: Code-mode bridge instructions, hidden catalog/search protocol, benchmark tool/function definitions, namespace metadata, output contract, and category notes.
- Volatile tail: source user query or current turn.
- Scorer: BFCL-native scorer where available, otherwise a deterministic adapter that preserves expected function names and argument constraints.

tau-bench/tau2:

- Stable prefix: domain policy, API/tool documentation, initial state reference, Code-mode bridge, and agent instructions.
- Volatile tail: current simulated user turn or task request.
- Scorer: benchmark state checker or task success signal.

ToolSandbox:

- Stable prefix: tool inventory, scenario state, constraints, Code-mode bridge, and state-checking instructions.
- Volatile tail: current conversational user turn.
- Scorer: ToolSandbox stateful evaluator.

## Metrics

Quality:

- Benchmark pass/fail per control.
- Expected and parsed tool/function calls.
- Argument correctness.
- Multi-call order/parallel handling where relevant.
- Irrelevance/no-call correctness.
- Unsupported scorer features.
- Parser/scorer status.
- Native scorer name/version/mode.
- Expected and parsed call/argument hashes.
- `primary_eligible`, `primary_eligibility_reason`, and `prefix_dependency_class`.
- `template`, `template_alias`, `alias_registry_version`, `host_filled_args`, and `final_source`.

Mechanism:

- Full-visible pass count.
- Fresh-tail leak count.
- Wrong-capsule pass count.
- Native live append versus restored capsule pass parity.
- Native live append versus restored capsule response hash parity.
- Generated token hash parity where available.
- Restored-only failure count and failure class.

Efficiency:

- Stable prefix tokens.
- Volatile tail tokens.
- Full visible prompt tokens.
- Restored visible prompt tokens.
- Prompt eval time.
- Decode time.
- Total wall time.
- Capsule save/restore time.
- Capsule bytes.
- One-shot and amortized repeated-tail cost.

Provenance:

- Benchmark id.
- Source revision or checkout.
- License note.
- Source row id or deterministic offset.
- Source row hash.
- Category/domain/task family.
- Transform version.
- Source fields used and excluded.
- Scorer version.
- Unsupported scorer features.
- Prompt hashes.
- Runner commit/script hash where practical.
- Model path/hash, quantization, llama.cpp version, hardware, GPU/CUDA notes.

## Gates And Stop Rules

Source gate:

- Do not run models until source revision, row provenance, categories, license notes, and scorer status are recorded.

Adapter gate:

- Run a no-model materialization/scorer dry run on at least five rows.
- Stop if expected calls or scoring cannot be reconstructed from source metadata.
- Stop before model smoke if category-native or faithful category-specific scoring is not proven.
- Mark any partial-scorer category diagnostic-only.
- Mark rows diagnostic-only if prefix dependency cannot be classified.

BFCL smoke gate:

- Run 10 rows across available categories.
- Stop if Code-mode full-visible failures are caused by adapter/scorer bugs.
- Stop if native live append fails while full-visible passes.
- Stop if restored capsule fails while native live append passes.
- Stop if fresh tail-only or wrong capsule passes on prefix-dependent rows.
- Stop before broad scaling if alias normalization, host-filled arguments, or host answer finalization becomes the dominant success mechanism.

Primary BFCL cohort:

- Target 50 to 100 full-visible-passing BFCL rows.
- Default non-inferiority margin: no more than one restored-only failure per 50 full-visible-passing rows.
- Rows where fresh tail-only passes are excluded from hidden-prefix value claims.

Follow-on:

- tau-bench/tau2 or ToolSandbox may begin only after BFCL smoke and summary are clean enough to show the adapter is honest.

## Delegation Plan

Workspace Manager:

- Own the goal, stop rules, final decisions, and synthesis.

Track 2:

- Act as skeptical paper owner.
- Review the design, gates, and final claims.
- Reject overclaims.

Subagent A:

- Source/provenance audit for BFCL, tau-bench/tau2, and ToolSandbox.
- Identify exact dataset/repo revisions, licenses, categories, runner/scorer availability, and integration risks.

Subagent B:

- Build or specify the BFCL adapter.
- Map source rows into stable prefix/tail/control records.
- Preserve scorer semantics.

Subagent C:

- Runner operations and DushyantPC smokes.
- Verify no duplicate llama/Python processes.
- Run small dry runs before full cohorts.

Subagent D:

- Analysis artifacts, tables, failure taxonomy, and paper-methods notes.

## Expected Artifacts

Committed summary path:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/
```

Ignored raw path:

```text
research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/
```

Committed files:

- `README.md`
- `summary.json`
- `source-audit.json`
- `candidate-calibration.json`
- `case-metrics.json`
- `control-matrix.json`
- `failure-classifications.json`
- `amortization.json`
- `model-info.json`
- `commands.md`
- `artifact-manifest.json`
- `paper-methods-notes.md`
- `disallowed-claims.md`

## Claim Rules

Allowed if gates pass:

- "On selected BFCL rows where Code-mode full-visible passed, restored KV capsule append matched native live append within the predeclared margin."
- "The restored condition reduced visible prompt tokens by not resending stable benchmark/tool context in the volatile tail."
- "Fresh-tail and wrong-capsule negatives stayed negative on prefix-dependent selected rows."
- "Code-mode hidden-tool orchestration improved reliability over direct visible tool schemas on the measured subset."

Disallowed unless separately proven:

- "The model is generally smarter."
- "KV capsules improve all tool use."
- "This works for long-horizon agents."
- "This beats tau-bench or ToolSandbox."
- "Prompt caching/full-prompt resend proves the KV capsule claim."
- "Compact visible evidence proves hidden KV value."
