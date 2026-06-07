# SSD State Layers And Context Scheduling

Date: 2026-06-04

## Purpose

This note records a working distinction that matters for Track 02: "storing context on SSD" can mean several different things, and only one of them is actual model-internal KV/session state.

The paper should avoid treating SSD as magic context or VRAM. The cleaner framing is:

> local agent runtimes should keep an unbounded task trace on disk while maintaining a bounded active context for the model, with quality gates deciding what to replay, reuse, summarize, drop, or recompute.

## Four Storage Layers

### 1. Research and benchmark artifacts

These are normal files: datasets, prompts, raw responses, scores, commands, model metadata, evidence slices, manifests, and experiment summaries.

They are on SSD because the repo and worktrees live on disk, but they are not model memory. The model only benefits from these files when the runtime explicitly loads their content and puts it back into a prompt or uses it to decide which prompt to build.

Current Track 02 examples:

- `research/02-quality-gated-stateful-kv-reuse/experiments/`
- ignored Track 01 benchmark input/result/cache paths used by Track 02 experiments
- OpenSpec change folders under `openspec/changes/`

### 2. Human-readable context artifacts

These are semantic artifacts that a future local-agent runtime could store and selectively reintroduce:

- task traces: tool calls, decisions, command outputs, file edits, errors, and checkpoints
- evidence slices: source snippets, graph edges, retrieved passages, code spans, or other facts needed for a future answer
- prompt summaries: compressed summaries of prior turns or work phases
- manifests: hashes, source pointers, model/backend metadata, and validity boundaries

These artifacts are useful because they can be inspected, indexed, filtered, summarized, and inserted visibly into the model's active context window.

Current Track 02 has started using this layer experimentally through compact visible evidence slices. The model sees the small evidence slice directly in the prompt, so the mechanism is visible context scheduling rather than hidden model-state reuse.

### 3. Backend KV/session cache files

This is the actual model-internal state layer.

When a backend such as llama.cpp saves a slot or session cache, it is storing opaque tensors derived from a prior prefill. In simple terms, this is the already-computed key/value attention state for a specific token sequence under a specific model, tokenizer, backend, position layout, and runtime configuration.

These files are not human-readable evidence. They are only valid if the backend can restore them under the same semantic contract the model would have had if the prefix had just been computed live.

Current Track 02 has tested this layer through session-tail, live-tail, slot save/restore, and prefix reuse audits. So far, the safe conclusion is conservative:

- same-server exact-prefix reuse can reduce repeated prompt processing
- fresh-server restore/full-resend did not show useful prefix-token reuse in the audited stack
- hidden prefix/session-tail behavior is not quality-equivalent to full prompt on the GraphWalks reasoning-over-prefix cases tested so far

### 4. Process-local runtime state

Some reuse may happen inside a live model server without becoming a durable SSD artifact. For example, a same-server exact repeat can reuse an in-memory prefix cache even if the result is not a portable long-lived cache file.

This matters because a speedup from a warm live server is not the same claim as persistent SSD-backed reuse across sessions. Track 02 should keep those mechanisms separated in reports and tables.

## What Track 02 Is Storing Today

Track 02 currently stores:

1. Experiment summaries and paper-facing notes in the Track 02 folder.
2. Prompt-bearing raw inputs, responses, scores, and scripts under ignored Track 01 benchmark paths.
3. Evidence slices derived from stable graph prefixes, currently used as visible prompt content.
4. Backend slot/session/cache artifacts in ignored benchmark cache paths when running session or restore probes.

It does not yet implement a full SSD-backed local-agent memory tier. There is not yet a scheduler that indexes task traces, chooses evidence, maintains summaries, validates cache state, and routes between visible replay, hidden reuse, recompute, or full fallback.

## Current Interpretation

The strongest current Track 02 signal is not "KV cache makes the model smarter."

The stronger signal is:

> visible, compact, task-relevant evidence can restore quality where hidden/session state alone fails.

That suggests the paper should treat KV/session reuse as one possible execution mode inside a larger quality-gated context scheduler.

For the GraphWalks evidence chain, the key distinction is:

- hidden prefix/session-tail tests whether opaque cached state can replace visible prefix reasoning
- compact visible evidence tests whether the runtime can surface only the relevant facts
- fresh compact visible evidence-only tests whether hidden KV contributes anything beyond the evidence slice itself

If hidden-plus-evidence and fresh-evidence-only match, the mechanism is evidence scheduling/token-efficient context compilation, not hidden KV contribution.

## Future SSD-Tier Shape

A future local-agent system could store an SSD-backed trace with records like:

- stable prefix manifests: prompt spans, hashes, model/backend compatibility, token counts
- evidence index: source spans, graph edges, code ranges, retrieval keys, and provenance
- summary chain: compact turn/work summaries with invalidation boundaries
- KV/session registry: opaque cache files with strict compatibility metadata
- quality gate log: when reuse was allowed, when visible replay was required, and when full fallback was triggered

The model's attention window would remain finite. The unbounded part would be the external trace and evidence library, not the active transformer context.

## Paper-Framing Guardrails

Do say:

- bounded active context over an unbounded task trace
- quality-gated context scheduling
- visible evidence replay and fallback as first-class runtime choices
- SSD as a trace/evidence/cache tier with explicit validity contracts

Do not say:

- SSD is infinite context
- SSD acts like VRAM
- stored files are automatically model memory
- hidden KV/session state is quality-equivalent to full prompt without controls

