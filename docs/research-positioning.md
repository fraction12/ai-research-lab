# Research Positioning

Date: 2026-06-03

## Bottom Line

SSD-native local-agent inference sits in a fast-moving research space, but the base ideas are not new.

Do not claim that this project invented KV caching, prefix caching, prompt-state reuse, or SSD-backed KV storage. Those are already active and partially proven areas.

The defensible wedge is narrower and more interesting: whether persistent, storage-aware KV/prefix reuse can make local agent loops reliably fast across realistic changed-tail workflows and cold or restarted sessions without silently degrading answer quality.

## What Is Already Proven

KV and prefix caching are mainstream inference optimizations. vLLM's automatic prefix caching and PagedAttention show that block-based KV memory management can avoid redundant prompt computation and improve serving throughput.

Reusable attention state has direct research support. Prompt Cache stores attention states for repeated text modules such as system prompts, templates, and documents. CachedAttention extends the same direction to multi-turn conversations with hierarchical storage.

Multi-tier KV cache systems are active infrastructure work. LMCache, NVIDIA Dynamo, Mooncake, AdaptCache, Tutti, DUAL-BLADE, and Swarm all point to a world where KV state moves across GPU memory, CPU RAM, SSD, and sometimes remote stores.

Local systems are already close to this project's shape. llama.cpp supports prompt/cache reuse and slot save/restore paths. oMLX claims Apple Silicon serving with hot RAM plus cold SSD KV cache restored across requests and server restarts.

Agentic prompt caching is now explicitly studied. "Don't Break the Cache" evaluates prompt-caching strategies for long-horizon agent tasks across hosted providers, and KVFlow studies workflow-aware KV cache management for multi-agent workflows. That means "agents repeat system prompts and tool context" is not enough, by itself, to be a novel claim.

Quality-aware KV reuse is also partially covered in adjacent areas. CacheBlend, CacheClip, SCBench, and semantic-integrity work show that KV reuse, fusion, compression, and loading can affect answer quality and should be evaluated with more than latency. These papers are especially important because they make it harder to claim that this repo is the first to notice a speed-quality tradeoff.

## 2026-06-03 Negative-Space Scan

The current online scan marks these areas as already covered:

| Area | Status | Representative anchors |
| --- | --- | --- |
| Prefix and KV reuse | Established | vLLM automatic prefix caching, PagedAttention, Prompt Cache |
| Multi-turn KV persistence | Established | CachedAttention |
| Multi-tier KV storage | Established | LMCache, Mooncake, Dynamo, AdaptCache |
| SSD/NVMe KV offload | Active research | Tutti, DUAL-BLADE, Swarm |
| Agentic prompt caching | Active research | Don't Break the Cache |
| Workflow-aware agent KV policy | Active research | KVFlow |
| Quality impact of KV reuse/compression | Active research | CacheBlend, CacheClip, SCBench, Semantic Integrity Matters |

The underexplored area appears to be narrower:

> Quality-gated persistent/session KV reuse for local, non-frontier agent loops, with explicit tests for when restored-prefix or tail-only execution remains equivalent enough to full-prompt execution.

As of this scan, the repo does not have strong evidence that public work has already covered the exact combination of:

- local non-frontier models on ordinary machines
- stable agent prefixes plus volatile tool/output tails
- persisted state across calls or restarted sessions
- full-prompt versus restored-prefix/session-tail correctness parity
- task-family-specific failure analysis
- fallback policy that trades speed for quality when reuse becomes unsafe

That combination is this repo's best candidate for net-new research.

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
- failure attribution that separates model weakness, prompt protocol weakness, scorer brittleness, and cache/session semantics
- routing or fallback policies that preserve quality by choosing full-prompt execution when reuse is risky

## Public Claim Guidance

Avoid:

- "We invented SSD-native inference."
- "This is a completely new frontier."
- "KV caching gives local models a significant token-efficiency gain" without a number and baseline.
- "This project is the first agent prompt-caching study."
- "SSD-backed state preserves quality" before parity and fallback experiments support that claim.

Prefer:

- "We are exploring a fast-moving edge of local inference: quality-gated persistent KV/prefix reuse for local agent workloads."
- "The open question is whether local agent loops can preserve useful inference state across changing context and cold restarts without unacceptable quality drift."
- "The novelty, if any, is in the correctness contract, local-agent benchmark design, persistence boundary, failure taxonomy, and storage-aware fallback policy."

## Paper-Worthy Bar

The work becomes paper-worthy only if it shows something beyond existing prefix/KV cache systems:

- reproducible benchmark fixtures for realistic local agent loops
- clear ablations for prompt layout, prefix alignment, cache persistence, SSD tiering, and compression
- direct comparison against existing systems and settings
- evidence that latency improves without unacceptable quality drift
- an explanation of when SSD-backed state helps and when it does not
- a correctness-parity protocol that identifies unsafe reuse cases before they become user-visible failures
- an evidence-backed fallback policy that preserves most speed benefit while recovering full-prompt quality on risky tasks

Until then, treat this as a rigorous prototype and positioning investigation, not a novelty claim. See `docs/research-paper-roadmap.md` for the paper-oriented plan.
