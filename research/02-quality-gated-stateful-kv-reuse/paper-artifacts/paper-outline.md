# Paper Outline

Date: 2026-06-07

Working title: Quality-Gated Hidden-State Reuse for Local Tool-Using Agents

Grounding files:

- `paper-data-ledger.md`
- `paper-claims-ledger.md`
- `paper-results-tables.md`
- `research/02-quality-gated-stateful-kv-reuse/paper-publication-plan-2026-06-07.md`

## Abstract

Draft target:

Local agent runtimes often repeatedly carry stable context as text: tool schemas, runtime rules, environment instructions, and task protocols. Text compaction summarizes this context but changes its representation. We study an alternative: evaluate a stable prefix once, persist the model's KV/sequence state as a capsule, and restore that hidden state before appending new task tails. We pair this with a compact programmatic tool interface and evaluate under a control ladder that compares full visible prompts, native live append, restored KV, fresh-tail negatives, wrong-capsule negatives, compact visible evidence, and direct visible tools. On a selected 100-case BFCL-derived cohort, restored KV matched native live append at 100/100 with zero fresh-tail or wrong-capsule leaks. On a repeated-work stream using the same local Gemma 4 model, the KV-capsule harness achieved 100/100 with 3,900 visible input tokens and 853,499 ms cumulative wall time, while a Codex/Ollama regular-tool natural text-compaction harness achieved 86/100 with 89 audited compaction events, 245,774,883 reported cumulative visible input tokens, and 11,813,816 ms cumulative wall time. The results support a narrow systems claim: quality-gated KV capsules can preserve stable tool/context knowledge as hidden state for repeated local-agent workloads. They do not establish prompt-identical superiority over all compaction methods or a general coding-agent benchmark win.

## 1. Introduction

Goal: explain the problem and the contribution without hype.

Key points:

- Local agents repeatedly resend stable tool and context information.
- Text-threaded harnesses rely on context windows and generated compaction summaries.
- KV capsules preserve hidden prefix state rather than generating a text summary.
- The paper asks when this is safe enough to use for local tool agents.

Main contributions:

1. A control ladder for evaluating hidden-state reuse in tool-use settings.
2. A programmatic tool-interface harness that keeps the visible task tail small while preserving a stable callable contract in prefix state.
3. A 100-case selected BFCL-derived evaluation where restored KV matches native live append under negative controls.
4. A repeated-work harness comparison against Codex/Ollama natural text compaction using the same Gemma 4 model.

Evidence to cite: E1, E5, E6.

## 2. Background And Related Work

Planned subsections:

- KV cache and sequence-state reuse.
- Prompt caching versus hidden-state restoration.
- Context compression and text-summary compaction.
- Tool-use and function-calling benchmarks, including BFCL.
- Programmatic tool calling / programmatic tool interfaces.
- Local agent harnesses and text-threaded CLI runtimes.

Must be checked/cited before final draft:

- llama.cpp sequence/KV state behavior and APIs used by the harness.
- BFCL v3 benchmark and scoring expectations.
- Programmatic tool calling terminology from current vendor/docs/literature.
- Any academic work on KV cache reuse, prompt caching, recurrent memory, context distillation, or long-context compression.

Evidence to cite from repo: E9, E10, E11, E12 for internal background; external citations still needed.

## 3. Method

### 3.1 Stable Prefix And KV Capsule

Describe:

- Construct stable prefix containing tool/function catalog, output contract, interface rules, and stable task protocol.
- Run the local model over that prefix.
- Save llama.cpp sequence/KV state.
- Restore it later.
- Append only the volatile task tail.

Evidence to cite: E1, E11, E12.

### 3.2 Programmatic Tool Interface

Describe carefully:

- Internal code uses `code_mode` labels, but paper calls it a programmatic tool interface.
- The model emits structured `EXEC`/function-call-style plans rather than seeing every tool schema every time.
- The host/harness compiles or records those calls for deterministic evaluation.
- This is related to, but not identical with, full arbitrary programmatic tool calling.

Evidence to cite: E1, E2, E3, E9, E10.

### 3.3 Control Ladder

Define each lane:

- Full visible.
- Native live append.
- Restored KV capsule.
- Fresh tail.
- Wrong capsule.
- Compact visible evidence.
- Direct visible tools.

Evidence to cite: E1, E9, E10.

## 4. Experimental Design

### 4.1 Selected 100-Case BFCL-Derived Cohort

Describe:

- Run label `bfcl-paper-selected-cohort-v1`.
- 100 cases, 700 records, 7 controls per case.
- Category mix: simple 26, multiple 25, parallel_multiple 17, java 17, parallel 14, javascript 1.
- Quality-gated selected cohort, not an official BFCL leaderboard submission.

Evidence to cite: E1.

### 4.2 Repeated-Work Runtime Comparison

Describe:

- Same Gemma 4 model family in both runtime lanes.
- KV-capsule harness with programmatic tool interface and restored hidden state.
- Codex/Ollama regular visible tools with natural text-summary compaction.
- Natural Codex compaction evidence came from Codex session JSONL, not per-task stdout.
- This is a practical harness comparison, not a prompt-identical mechanism comparison.

Evidence to cite: E5, E6, E7, E8.

### 4.3 Supporting Runs

Describe:

- BFCL primary-50 V5 as nonhandmade supporting evidence.
- 30-case custom harness as earlier controlled fixture evidence.
- Family 2 gates as low-level mechanism background.

Evidence to cite: E9, E10, E11, E12.

## 5. Results

### 5.1 Restored KV Matches Native Live Append

Use Table 1.

Main sentence:

On the selected 100-case cohort, full visible, native live append, and restored KV all passed 100/100; fresh-tail and wrong-capsule controls had zero leaks; native/restored hash parity was 100/100.

Evidence: E1.

### 5.2 Compact Visible Evidence Does Not Explain The Result

Use Table 1.

Main sentence:

Compact visible evidence passed only 19/100, far below restored KV at 100/100, supporting the claim that the restored hidden prefix carried useful information beyond a compact visible baseline.

Evidence: E3.

### 5.3 Programmatic Interface Versus Direct Visible Tools

Use Table 1.

Main sentence:

The programmatic full-visible lane passed 100/100 compared with 91/100 for direct visible tools on the selected cohort.

Evidence: E2.

### 5.4 Timing Boundary

Use Table 2.

Main sentence:

The selected-cohort mechanism run does not support an intrinsic restore-speed claim: restored KV mean latency was 8513.8 ms versus 6766.7 ms for full visible and 6782.7 ms for native live append.

Evidence: E4.

### 5.5 Repeated-Work Runtime Comparison

Use Table 3.

Main sentence:

On the repeated-work stream, the KV-capsule harness achieved 100/100 with 853,499 ms cumulative wall time and 3,900 visible input tokens, while the natural Codex/Ollama text-compaction lane achieved 86/100 with 11,813,816 ms cumulative wall time, 245,774,883 reported visible input tokens, and 89 audited compaction events.

Evidence: E5, E6.

### 5.6 Failure Analysis

Use Table 4.

Main sentence:

The 14 Codex failures mostly looked like tool-call accuracy misses rather than parser collapse, but the current evidence does not prove compaction summaries caused those failures.

Evidence: E8.

## 6. Discussion

Points:

- Hidden state is not a text summary; it preserves the model's internal representation of the stable prefix.
- Quality gates matter: fresh-tail and wrong-capsule controls are what make the result credible.
- The programmatic interface matters because it reduces the repeated visible contract and stabilizes how tools are represented.
- The repeated-work result is the operational result; the selected-cohort ladder is the mechanism defense.

Claims to avoid:

- "KV beats compaction" without qualifiers.
- "This is full programmatic tool calling."
- "This beats Codex on coding."
- "Restored KV is inherently faster."

Evidence: C1 through C12.

## 7. Limitations

Must include:

- Practical harness comparison, not prompt-identical mechanism comparison.
- Selected cohort is quality-gated and BFCL-derived, not a full official leaderboard run.
- Programmatic interface is not full arbitrary PTC.
- Codex token telemetry is route-reported cumulative burden.
- Codex compaction-summary contamination/help/harm remains to be audited.
- Restored KV was slower in the selected-cohort mechanism run.

Evidence: L1 through L6 in `paper-claims-ledger.md`.

## 8. Reproducibility

Include:

- Source repo paths and run labels.
- Model profile and backend where available.
- Raw artifact hashes where available, especially BFCL primary-50.
- Scripts:
  - `research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_agent_harness.py`
  - `research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_model_loop_runner.py`
  - `research/01-ssd-native-inference-current/benchmarks/bfcl_code_mode_kv_adapter.py`
  - `research/01-ssd-native-inference-current/benchmarks/paper_campaign_selected_cohort.py`
  - `research/01-ssd-native-inference-current/benchmarks/paper_campaign_repeated_work_speed.py`
- NotebookLM flat bundle:
  - `notebooklm-paper-bundle/README.md`
  - `notebooklm-paper-bundle/FILE_INDEX.txt`

Evidence: E1, E5, E6, E9, E14.

## 9. Conclusion

Draft target:

This paper shows that quality-gated hidden-state reuse can support local tool-using agents on repeated stable-context workloads. Restoring a KV capsule allowed the same local model to use stable tool/context knowledge without repeatedly carrying that stable context as visible text. Under strict controls, restored KV matched native live append on a selected 100-case BFCL-derived cohort, and in a repeated-work systems comparison it outperformed a Codex/Ollama text-compaction harness using the same model on pass rate, wall time, and visible-context burden. The result is narrow but useful: KV capsules are not a universal memory solution, but they are a credible runtime primitive for local agents when the stable prefix is quality-gated, the tail is small, and negative controls verify that hidden state is doing real work.

## Outline Review

- Every result sentence has an evidence ID.
- The main paper should be built from Tables 1 through 4.
- Related work still needs external citation filling before a full draft.
- The paper should use "programmatic tool interface" externally and reserve `code_mode` for internal run labels.
