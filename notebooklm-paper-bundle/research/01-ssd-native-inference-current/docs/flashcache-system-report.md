# Flashcache System Report

Date: 2026-06-03

## Bottom Line

Flashcache is worth continuing, but the product bar has changed.

The repo now has good evidence that SSD-backed reusable inference state can reduce local prompt-processing cost for repeated agent loops. The strongest timing result is session-tail mode on large Printy-style prefixes: restore stable context once, send only changed tails, and recover about 79.8% prompt-processing savings on the 64 KB fixture.

The repo also now has good evidence that speed alone is not enough. The correctness parity run selected 42 cases where the full prompt passed, then tested session-tail on those same cases. Session-tail passed 31/42 overall, 31/36 IFEval, and 0/6 GraphWalks. That means the current path is promising for simple instruction following but not quality-safe for reasoning tasks that depend deeply on restored prefix context.

So the current thesis is:

> SSD-backed local-agent inference state can make repeated local model workflows faster, but it needs explicit session semantics and quality gates before it can be trusted as a general replacement for full prompts.

## What We Built

The current system is not yet a custom SSD-native KV engine. It is an evidence harness around existing backend primitives:

- stable agent context is separated from changed tails
- llama.cpp slots are saved to local storage
- later requests restore that state
- benchmark modes compare full-prompt recompute, hot cache, session restore, and session-tail execution
- correctness tools compare full-prompt answers against session-tail answers only after the full prompt passes

This matters because the long-term target is lower-level than prompt text:

```text
agent prompt text
-> tokens
-> prefill compute
-> KV cache tensors
-> RAM / VRAM movement
-> SSD serialization
-> SSD read pattern
-> restore into runtime
-> continue generation
```

The current wrapper proves enough to shape the next layer, but it should not be confused with the final architecture.

## Why SSD Helps

Local agent loops repeatedly carry large stable context:

- system and developer instructions
- tool schemas
- repo summaries
- memory blocks
- workflow rules
- long-lived session state

The volatile tail changes every turn:

- command output
- diffs
- CI results
- review comments
- user corrections
- next action state

Plain Markdown and retrieval solve knowledge availability. Flashcache targets compute cost: if the same stable context must stay present for quality, the local runtime should avoid redoing the same prefill work on every turn.

SSD is useful when three things are true:

1. the reusable prefix is large enough to be expensive
2. the workflow has repeated changed-tail turns
3. restoring cached state is cheaper than recomputing the prefix

SSD is not magic VRAM. Whole-slot files already get large quickly, so the future design needs block layout, partial restore, cache eviction, compatibility keys, and I/O telemetry.

## Evidence Summary

| Evidence | Result | Meaning |
| --- | ---: | --- |
| Warm vs restarted Ollama Printy workflow | restarted prompt eval was 2.36x warm | There is a persistence gap worth targeting. |
| GPT-OSS 20B small-prefix direct slot restore | -0.35% reduction on 5.5 KB prefix | Whole-slot restore is not automatically useful at small prefix sizes. |
| GPT-OSS 20B small-prefix Flashcache wrapper | about 12.2% prompt-processing savings | Product-shaped wrapper can help even when direct slot restore is flat. |
| Persistent server 64 KB large-prefix wrapper | 81.5% prompt-processing reduction | Cache value scales when process lifecycle noise is removed. |
| Hot cache 64 KB large-prefix wrapper | 82.0% prompt-processing reduction | Already-persisted stable context gives large steady-state wins. |
| Session-tail 64 KB large-prefix wrapper | 79.8% prompt-processing reduction | Restore-once plus tail-only turns matches the desired local-agent shape. |
| Correctness parity, 42 selected full-passing cases | session-tail passed 31/42 | Current speed path is not quality-safe yet. |

Primary evidence paths:

- `docs/benchmark-graphs.md`
- `benchmarks/datasets/printtestbot-persistent-server-2026-06-03/README.md`
- `benchmarks/datasets/printtestbot-hot-cache-2026-06-03/README.md`
- `benchmarks/datasets/printtestbot-session-tail-2026-06-03/README.md`
- `benchmarks/datasets/flashcache-correctness-parity-2026-06-03/README.md`
- `benchmarks/datasets/flashcache-correctness-parity-2026-06-03/summary.json`

## Correctness Read

The latest correctness result is the most important evidence because it tests whether speed preserves answer quality.

Setup:

- model: `gpt-oss-20b-mxfp4.gguf`
- machine: DushyantPC
- candidate builder: `ifeval:100,graphwalks:20`
- candidate cases: 107
- full-prompt gate selected: 42
- selected set: 36 IFEval, 6 GraphWalks

Result:

- full prompt on selected set: 42/42
- session-tail overall: 31/42
- session-tail IFEval: 31/36
- session-tail GraphWalks: 0/6
- mean selected-case prompt-time saving: 533.355 ms

Interpretation:

- The selected set is large enough to judge this protocol.
- Session-tail can preserve many simple instruction-following answers.
- Session-tail failed every selected reasoning-over-prefix case.
- The quality risk is now concrete, not theoretical.

This does not prove that SSD-backed inference is fundamentally unsafe. It proves that this local model plus this prompt protocol plus this slot/session path is not yet equivalent to full-prompt inference for reasoning-heavy tasks.

## Model Caveat

The correctness run used a local GPT-OSS 20B GGUF model, not a frontier model. That matters.

Failures can come from at least three places:

- model capability: the model may be weak or brittle on GraphWalks and constrained output
- prompt protocol: the JSON-answer and tail-only prompts may under-specify how to use restored context
- cache/session semantics: restored-prefix tail-only decoding may not behave like full-prompt decoding for deep context reasoning

The right conclusion is not "Flashcache breaks reasoning." The right conclusion is:

> The current local-model/session-tail stack has measurable quality drift, and the system must include controls that can identify whether drift comes from model weakness, prompt protocol, or cache semantics.

## Product Shape

The best product shape is not "cache every prompt."

The best shape is an explicit local-agent session API:

1. open a session with stable prefix context
2. persist compatible prefix/KV state to local storage
3. append changed-tail turns
4. reset back to a clean prefix when needed
5. score or compare outputs against full-prompt baselines during evaluation
6. fall back to full prompt when quality risk is high

For regular people running local models, the product should hide the storage mechanics but expose enough telemetry to trust it:

- cache hit/miss state
- reusable prefix bytes
- prompt milliseconds saved
- restore and tail timing
- slot or KV storage bytes
- fallback reason
- quality/parity status in benchmark mode

## Architecture Direction

The current wrapper should evolve toward a lower-level SSD-aware memory tier.

Near-term architecture:

- explicit session object
- stable-prefix restore once per session
- tail append API
- clean-prefix reset
- compatibility keys for model, tokenizer, quantization, context size, runtime flags, prompt bytes, and position assumptions
- quality-aware routing: full prompt for risky tasks, session-tail for safe repeated turns

Medium-term architecture:

- block-based prefix/KV layout instead of whole-slot blobs
- partial restore for relevant prefix blocks
- block roles for system prompts, tool schemas, repo context, attention sinks, rolling tails, and volatile tails
- eviction policy that preserves high-value stable state
- I/O telemetry for SSD read/write bytes and throughput
- optional compression when decompression plus restore beats recompute

Long-term architecture:

- backend integration deep enough to reduce serialization, memory copy, and accelerator upload overhead
- persistent cache index shared across sessions
- automatic session-state planning for local coding agents
- benchmark harness that measures wall-clock task success, not only prompt time

## Quality Gates

Flashcache should not be considered safe for general local-agent use until these gates pass:

1. Full-prompt replay control passes the same selected cases repeatedly.
2. Session-tail answers match full-prompt answers on a larger selected set.
3. Results are split by task family, not only averaged.
4. Reasoning-over-prefix tasks like GraphWalks no longer collapse.
5. Stronger-model controls show whether failures are model-specific.
6. Prompt-protocol controls show whether the tail path needs different instructions.
7. The system can route unsafe tasks back to full-prompt mode.
8. End-to-end agent workflows are measured for task completion, not just prompt eval.

The current correctness result fails gate 4 and partially fails gate 2.

## What To Build Next

The next step is not another broad benchmark. It is a focused correctness investigation.

Recommended next experiment:

1. Use the six selected GraphWalks cases that full prompt passed and session-tail failed.
2. Rerun full prompt to check model variance.
3. Run a "visible prefix but session formatted" control.
4. Run tail-only with stronger answer hints.
5. Run tail-only after a reset/restore sanity check.
6. If possible, compare against a stronger local or frontier model on the same cases.

The goal is to classify each failure:

- model cannot do it reliably
- prompt protocol causes the failure
- restored-prefix state is not semantically equivalent enough
- scorer/output parsing is too brittle

Only after that should the repo design the next SSD/KV layer.

## Current Verdict

Flashcache has crossed the first threshold: the speed opportunity is real enough to justify deeper work.

It has not crossed the second threshold: the current session-tail path is not yet quality-safe.

The promising path is still clear. Treat SSD as a persistent memory tier for reusable local-agent state, not as magic model capacity. Use explicit sessions, measure restore and tail costs separately, keep full-prompt fallbacks, and make correctness parity a release gate.

If this works, the practical win is large: regular people could run more capable local agents on ordinary machines because stable context would become reusable local inference state instead of repeated prompt-processing work.
