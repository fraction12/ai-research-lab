# Idea Brief

## One-Line Bet

Build an SSD-native local inference daemon for agents, where the SSD stores reusable inference state and cold model pieces while RAM, GPU, or unified memory holds the hot path.

## Why This Is Interesting

Local agents are memory hungry in a different way than chatbots. They repeat stable context:

- system prompts
- tool schemas
- repo summaries
- memory blocks
- long-lived session context
- common task scaffolds

That repetition creates cacheable structure. A storage-aware engine can avoid recomputing and reloading the same expensive context over and over.

## Taste Filter

Good taste:

- build around repeated agent workloads
- make the memory hierarchy explicit
- benchmark cold start, warm reuse, and cache-hit behavior separately
- use SSD for prefix/KV cache, local block store, and cold expert paging
- compress before offloading
- prefetch large aligned chunks instead of doing tiny random reads
- challenge obvious cache assumptions with small falsifying experiments
- treat failed correctness cases as design material

Bad taste:

- promising "any SSD runs any model fast"
- treating dense model weights on disk as a drop-in VRAM replacement
- optimizing a demo path that only works once
- ignoring latency, read amplification, and quality drift
- benchmarking only warm happy paths
- calling an idea novel before checking prior art
- pursuing strange ideas without controls, confounders, and stop rules

## Initial Product Shape

An OpenAI-compatible local server that wraps MLX or llama.cpp and adds:

- persistent prefix cache
- optional SSD-backed KV cache
- content-addressed context blocks
- cache-aware prompt assembly
- timing and I/O telemetry
- benchmark scripts for agent-style workloads

## Non-Goals

- Training models
- Beating hosted frontier models
- General cloud serving
- Supporting every model format on day one
- Building a new transformer runtime from scratch before proving the cache layer
