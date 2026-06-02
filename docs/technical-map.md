# Technical Map

## Core Mental Model

Inference is a memory hierarchy problem:

1. Compute wants dense, fast access.
2. Model weights, KV cache, and context state get huge.
3. Moving data is often more expensive than doing math.
4. SSDs are useful only when access is predictable, chunked, compressed, and reusable.

## Memory Tiers

- GPU / accelerator / unified memory: hot weights, current layer activations, hot KV
- RAM: warm KV, prompt blocks, routing metadata, staging buffers
- SSD: persistent prefix cache, cold KV blocks, cold experts, prompt block store
- Network: optional remote cache later, not part of the first local prototype

## Objects Worth Storing

### Prefix Cache

Stable prompt prefixes:

- system prompt
- tool schemas
- repo context
- skill instructions
- memory bundles

This is the best first target because agent prompts repeat.

### KV Cache

Attention keys and values from prior context.

This can avoid prefill cost, but it needs careful compatibility:

- same model
- same tokenizer
- same quantization mode
- same prompt bytes or stable block hashing
- compatible position encoding assumptions

### MoE Experts

Sparse models may only activate a subset of experts per token.

Possible strategy:

- keep router and hot experts in memory
- store cold experts on SSD
- prefetch likely experts layer-ahead
- measure routing locality before betting the project on it

## I/O Rules

- Avoid tiny random reads.
- Read large aligned chunks.
- Use async prefetch.
- Stage reads one or more layers ahead.
- Store data in model-aware block layout.
- Track read amplification.

## Compression Rules

Compress before deciding to offload:

- quantized KV cache
- compressed prompt block store
- quantized cold experts
- optional transform-coded KV if worth the complexity

## Benchmark Rules

Track:

- time to first token
- cold tokens/sec
- warm tokens/sec
- repeated-agent-loop tokens/sec
- prefill time
- decode time
- cache hit rate
- SSD read bytes
- read amplification
- I/O wait
- memory pressure
- watts if easy to capture
- quality drift against baseline

