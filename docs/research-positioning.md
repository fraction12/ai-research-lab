# Research Positioning

Date: 2026-06-02

## Bottom Line

SSD-native local-agent inference is a real research frontier, but the base ideas are not new.

Do not claim that this project invented KV caching, prefix caching, prompt-state reuse, or SSD-backed KV storage. Those are already active and partially proven areas.

The defensible wedge is narrower and more interesting: whether persistent, storage-aware KV/prefix reuse can make local agent loops reliably fast across realistic changed-tail workflows and cold or restarted sessions.

## What Is Already Proven

KV and prefix caching are mainstream inference optimizations. vLLM's automatic prefix caching and PagedAttention show that block-based KV memory management can avoid redundant prompt computation and improve serving throughput.

Reusable attention state has direct research support. Prompt Cache stores attention states for repeated text modules such as system prompts, templates, and documents. CachedAttention extends the same direction to multi-turn conversations with hierarchical storage.

Multi-tier KV cache systems are active infrastructure work. LMCache, NVIDIA Dynamo, Mooncake, AdaptCache, and Tutti all point to a world where KV state moves across GPU memory, CPU RAM, SSD, and sometimes remote stores.

Local systems are already close to this project's shape. llama.cpp supports prompt/cache reuse and slot save/restore paths. oMLX claims Apple Silicon serving with hot RAM plus cold SSD KV cache restored across requests and server restarts.

## Where This Project Can Still Be Useful

Local coding and agent workloads are not clean repeated prompts. They repeatedly include stable context such as system prompts, tool schemas, repo summaries, memory blocks, and workflow scaffolds, but they also mutate volatile tails through tool calls, command output, diffs, and planner state.

The current project signal is the warm-vs-restarted persistence gap: aligned stable-prefix prompts get cheaper while Ollama stays warm, but restarted runs pay the prefix cost again. That creates a concrete target for persistent prefix/KV state.

The project can still contribute if it produces evidence for:

- realistic local-agent benchmark fixtures instead of toy repeated prompts
- cold, warm, exact-replay, partial-prefix, and restarted-session measurements
- comparisons against close baselines such as Ollama, llama.cpp, vLLM with LMCache, and oMLX
- cache-key and block-role design for stable prefixes, attention-sink candidates, rolling tails, and volatile tails
- quality and correctness checks, not only latency numbers
- I/O telemetry that shows whether SSD reads help or merely move the bottleneck

## Public Claim Guidance

Avoid:

- "We invented SSD-native inference."
- "This is a completely new frontier."
- "KV caching gives local models a significant token-efficiency gain" without a number and baseline.

Prefer:

- "We are exploring a fast-moving edge of local inference: persistent KV/prefix reuse for agent workloads."
- "The open question is whether local agent loops can preserve useful inference state across changing context and cold restarts."
- "The novelty, if any, is in the workload framing, persistence boundary, benchmark design, and storage-aware cache policy."

## Paper-Worthy Bar

The work becomes paper-worthy only if it shows something beyond existing prefix/KV cache systems:

- reproducible benchmark fixtures for realistic local agent loops
- clear ablations for prompt layout, prefix alignment, cache persistence, SSD tiering, and compression
- direct comparison against existing systems and settings
- evidence that latency improves without unacceptable quality drift
- an explanation of when SSD-backed state helps and when it does not

Until then, treat this as a rigorous prototype and positioning investigation, not a novelty claim.
