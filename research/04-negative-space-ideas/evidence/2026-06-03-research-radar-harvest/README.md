# 2026-06-03 Research Radar Paper Harvest

Purpose: collect a focused paper set for the lab's research direction around quality-gated persistent KV reuse, agentic workflow caching, role-aware context compilation, and intentional recompute.

Generated with `paper-harvester-pp-cli 1.0.0` on 2026-06-03. No PDFs or full-text files were downloaded.

## Commands

Search outputs were saved under `searches/` with bounded OpenAlex queries for:

- `stateful inference multi-agent tool calling KV cache`
- `KV cache quality reuse compression LLM inference correctness`
- `prompt caching agents LLM tool use cache`
- `CacheBlend KV cache reuse quality LLM`
- `CacheClip KV cache compression semantic integrity LLM`
- `SCBench KV cache compression long context quality`
- `CachedAttention multi turn KV cache conversations`
- `LMCache KV cache storage LLM serving SSD`
- `KVFlow workflow aware KV cache agent LLM`
- `Tutti KV cache SSD offload LLM inference`
- `role aware context compilation LLM agents context engineering recompute`

Exact arXiv-backed metadata and arXiv confirmation pages were then harvested with:

```bash
paper-harvester-pp-cli harvest anchors --id 2405.16444,2410.15332,2411.02820,2412.19442,2412.10319,2403.19708,2405.12981,2407.12391,2410.03065,2409.13761,2507.07400,2605.24259,2603.16104,2603.04428,2605.06472,2605.07238,2604.24971,2605.27744 --output-dir research/04-negative-space-ideas/evidence/2026-06-03-research-radar-harvest --delay 1s --agent --deliver file:research/04-negative-space-ideas/evidence/2026-06-03-research-radar-harvest/harvest-result.json
```

## Artifact Index

- `harvest-summary.md`: compact table of the 18 exact harvested papers.
- `harvest-summary.json`: structured metadata summary.
- `harvest-result.json`: full harvester command output.
- `raw/openalex-<id>.json`: raw OpenAlex metadata per paper.
- `raw/arxiv-html-<id>.html`: raw arXiv confirmation page per paper.
- `searches/*.json`: raw bounded OpenAlex search results.

## Read First

1. `2403.19708` - CachedAttention. Multi-turn KV reuse is already directly studied.
2. `2507.07400` - KVFlow. Workflow-aware prefix caching for multi-agent systems is already active.
3. `2603.16104` - Helium / data-systems view of agentic workflows. This crowds generic "agent workflows have reusable state" claims.
4. `2605.06472` - Prediction-based KV management for dynamic agent workflows. This crowds static workflow policy claims.
5. `2605.24259` - Resident KV Claims. Very close to correctness/contract language; review before claiming novelty around reuse contracts.
6. `2412.10319` - SCBench. Useful for quality and lifecycle-oriented KV evaluation framing.
7. `2410.03065` - Compute Or Load KV Cache? Why Not Both? Important for intentional recompute, but from a throughput/resource-overlap angle rather than quality repair.

## Crowded Boundaries

- Generic KV/prefix reuse: CachedAttention, CacheBlend, EPIC, DroidSpeak.
- Workflow-aware agent caching: KVFlow, dynamic prediction-based KV management, FATE, Helium.
- SSD/offload or load-vs-compute systems: Tutti search result plus Cake (`Compute Or Load KV Cache? Why Not Both?`).
- KV compression and shared pools: Cross-Layer Attention, PolyKV, SCBench, the KV-cache management survey.

## Still Interesting Gaps

- Quality-gated persistent reuse for local non-frontier agent loops remains promising, but needs careful comparison against Resident KV Claims, SCBench, and workflow-aware cache papers.
- Intentional recompute remains plausible if framed as quality repair or semantic parity restoration, not merely overlapping compute with KV loads.
- Role-aware context compilation still looks underexplored as a mechanism for deciding visible replay, restore, recompute, discard, or fallback. The search results were noisy, which is weak evidence that the exact phrase is not yet a crowded systems term.
- Local persistent KV privacy, deletion, and cross-project isolation were not deeply covered in this harvest; use the previous negative-space security anchors before making claims.

## Suggested Next Pass

Read the abstracts and methods for the seven "Read First" papers, then update the negative-space scan with:

- what each paper already covers
- which claims the lab should avoid
- one falsifiable hypothesis per remaining gap
- whether each gap should be promoted, parked, or abandoned
