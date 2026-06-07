# Prototype Plan

## Prototype Name

Working name: `flashcache`.

## Phase 0: Benchmark Harness

Build this before building the cache.

Scenarios:

- short chat baseline
- long prompt cold prefill
- same long prompt repeated
- agent loop with stable system prompt and changing user/tool messages
- repo-context prompt with repeated file summaries

Metrics:

- time to first token
- prefill milliseconds
- decode tokens/sec
- warm tokens/sec
- cache hit rate
- SSD read bytes
- process RSS

## Phase 1: Prefix Block Store

Build a content-addressed prompt block store:

- split stable prompt sections into named blocks
- hash exact bytes plus tokenizer/model metadata
- persist block metadata on SSD
- mark attention-sink candidates at the start of the reusable prefix
- mark stable prefix, rolling-tail, and volatile-tail roles separately
- expose cache hit/miss telemetry

First version can cache prompt assembly and metadata before attempting raw KV reuse.

## Phase 2: Persistent KV Cache

Add KV persistence for exact-prefix reuse:

- only exact model/tokenizer/config matches
- start with full-prefix reuse, not arbitrary partial reuse
- keep attention-sink KV hot while experimenting with rolling or offloaded KV
- store blocks in large contiguous files
- implement LRU and size caps
- validate output equality against uncached baseline where possible

## Phase 3: Backend Wrapper

Wrap one local backend first:

- llama.cpp first, because slot save/restore already reduced cold changed-tail prefill in the feasibility benchmark
- compare MLX or oMLX next if Apple Silicon-specific performance becomes the primary target

Expose an OpenAI-compatible local API:

- `/v1/chat/completions`
- cache metadata in response headers or debug JSON
- benchmark endpoint or CLI

## Phase 4: SSD-Aware Prefetch

Add a prefetcher:

- predict needed cache blocks from prompt manifest
- load sequential blocks before decode
- keep hot blocks in RAM
- log misses and late reads

## Phase 5: MoE Investigation

Only after KV/prefix cache has numbers:

- choose a sparse model
- measure expert routing locality
- test hot expert residency
- test cold expert paging
- compare against simply using a smaller dense model

## First Milestone

Prove one claim:

Repeated OpenClaw-style agent prompts get meaningfully faster on the second and later run without quality drift.

Suggested target:

- 2x faster repeated long-context prefill
- no material decode slowdown
- cache telemetry explains the win
