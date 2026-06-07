# Flashcache Metal Direction

Date: 2026-06-02

## Agent Note

Flashcache is not meant to stop at proving that prompt caching works. Prompt caching, prefix reuse, and KV-cache reuse are already proven primitives. Treat the current Flashcache prototype as a measurement harness and stepping stone toward a lower-level SSD-aware inference layer for local agent workloads.

The project direction is:

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

The deeper research question is whether we can make persistent prompt and KV state behave like a practical memory tier on ordinary machines, especially for repeated local-agent loops with stable prefixes and changing tails.

## What The Current Prototype Proves

Current Flashcache work wraps existing backend behavior, especially llama.cpp slot save and restore. This is useful because it gives the repo a real benchmark harness and evidence loop:

- stable context is processed once
- reusable state is written to SSD
- later runs restore that state
- changed-tail workflow latency is compared against direct recompute

Do not treat this as the final invention. Treat it as the first instrument.

## What We Are Working Toward

The target is closer to the metal than a wrapper:

- direct control over KV-cache storage layout
- partial restore of reusable prefix blocks instead of whole slot blobs
- memory-mapped or OS-page-cache-friendly reads where useful
- prefetching cache blocks while agents run tools
- block-role policies for system prompts, tool schemas, repo context, attention sinks, rolling tails, and volatile tails
- cache compatibility keys for model, tokenizer, quantization, context size, runtime flags, prompt bytes, and position assumptions
- eviction that preserves valuable repo/session/tool-schema state
- optional KV compression or quantization when loading compressed state beats recompute
- backend integration deep enough to measure and reduce copy, upload, and serialization overhead

## How To Use The Benchmarks

The benchmark question is not only "did caching help?" The better question is "where did the time go?"

Future benchmark work should separate:

- tokenization time
- cold prefill time
- slot or KV save time
- slot or KV file size
- SSD write throughput
- SSD read throughput
- restore time
- GPU or accelerator upload time, if observable
- tail prefill time
- decode time
- cache hit rate
- quality or output drift against baseline

If restore beats recompute by a meaningful margin, go deeper. If restore barely helps, use the measurements to identify the bottleneck before changing architecture.

## Guardrails

- Do not claim this repo invented prompt caching or KV caching.
- Do not describe SSD as magic VRAM.
- Do not optimize toy repeated prompts at the expense of realistic agent workflows.
- Do not add cache complexity without a benchmark that can show the win or isolate the loss.
- Prefer backend-aware improvements over generic file caching.

## Near-Term Path

1. Use Flashcache to collect evidence on realistic local-agent fixtures.
2. Add timing instrumentation around every cache boundary.
3. Compare full-slot restore, prefix-block reuse, and changed-tail recompute.
4. Identify whether the bottleneck is prefill compute, disk I/O, serialization, memory copy, GPU upload, or runtime scheduling.
5. Only then design the next lower-level storage format or backend patch.

The long-term win is not "prompt caching exists." The win is making SSD-backed inference state automatic, measurable, and useful enough that regular people can run capable local agents on normal machines.
