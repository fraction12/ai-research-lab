# 2026-06-05 Local-Agent Runtime Harness Synthesis

## Idea

The bigger research direction is not only KV cache reuse or Code mode. It is a local-agent runtime harness that helps non-frontier local models behave like stronger long-horizon agents by compiling context, tools, state, and evidence into separate execution surfaces.

Working framing:

> Local-agent runtime harness for non-frontier models: compile context and tools into the right execution surfaces so small/local models can run longer, call more tools, and waste fewer tokens.

## Components

- KV capsules: reusable hidden model state for stable prefixes when semantic continuation passes quality gates.
- Code mode / hidden tool catalog: compress large tool schemas into a small visible contract such as `exec` and `wait`, with policy-filtered tool discovery inside the runtime.
- SSD task trace: persistent record of tool calls, command outputs, file edits, failures, checkpoints, summaries, and evidence.
- Context scheduler: decides what to restore as hidden state, what to replay visibly, what to summarize, what to recompute, what to drop, and when to fall back to full prompt.
- Quality gates: validate cache identity, tool availability, denied-tool absence, answer quality, and task-family risk before trusting hidden state or hidden capability surfaces.

## Hypothesis

A local model such as Gemma 4 can perform longer-horizon, tool-heavy agent work if the runtime stops flattening everything into the active prompt. The model should see the current task, compact evidence, and a small orchestration contract; the runtime should manage tool catalogs, stable instructions, traces, summaries, and reusable KV state.

## What This Is Not

- Not model training.
- Not claiming SSD is infinite context.
- Not claiming hidden KV is always quality-equivalent to full prompt.
- Not claiming Code mode makes tool use safe by itself.

## Research Question

What correctness, audit, fallback, and scheduling contracts are required for a local runtime to safely hide large parts of agent state from the prompt while preserving or improving task success?

## Smallest Useful Test

Compare a local model across direct tools, tool search, and Code mode while also varying stable-prefix execution:

- full visible prompt with direct tool schemas
- full visible prompt with Code mode
- KV capsule stable prefix plus Code mode
- KV capsule plus compact visible evidence and SSD trace retrieval

Measure task success, prompt tokens, wrong-tool rate, tool-call count, approval misses, latency, recovery from failed tools, and whether the model can maintain task progress across many turns.
