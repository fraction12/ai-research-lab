# Prior-Art Mechanism Map

Date: 2026-06-03

This map uses repo-local harvested metadata and abstracts. The current harvest did not download PDFs or full-text files, so this is a positioning map rather than a detailed algorithmic literature review.

## Mechanism Implications

| Source | Repo evidence path | Mechanism relevance | Boundary for this ladder |
| --- | --- | --- | --- |
| CacheBlend | `research/04-negative-space-ideas/evidence/2026-06-03-research-radar-harvest/raw/openalex-2405.16444.json` | Selective recomputation can preserve quality when reused KV chunks miss cross-attention context. | Our anchor-span controls are prompt-level repair proxies, not KV fusion or true CacheBlend implementation. |
| EPIC | `research/04-negative-space-ideas/evidence/2026-06-03-research-radar-harvest/raw/openalex-2410.15332.json` | Position-independent caching and attention-sink mitigation are directly relevant to non-prefix reuse and positional assumptions. | This ladder only probes prompt/position symptoms; it does not implement position-independent KV reuse. |
| CachedAttention | `research/04-negative-space-ideas/evidence/2026-06-03-research-radar-harvest/raw/openalex-2403.19708.json` | Multi-turn KV reuse with hierarchy and positional validity is close to session reuse. | Live-tail failure here suggests the issue is not only disk restore; multi-turn semantics need quality checks. |
| DroidSpeak | `research/04-negative-space-ideas/evidence/2026-06-03-research-radar-harvest/raw/openalex-2411.02820.json` | Selective layer recomputation is another repair pattern for reused KV. | This experiment does not perform layer-wise repair, but motivates a future lower-level control if prompt anchors fail. |
| SCBench | `research/04-negative-space-ideas/evidence/2026-06-03-research-radar-harvest/raw/openalex-2412.10319.json` | KV lifecycle quality should be evaluated across generation, compression, retrieval, and loading. | This ladder contributes a local six-case quality lifecycle probe, not a comprehensive long-context benchmark. |
| Resident KV Claims | `research/04-negative-space-ideas/evidence/2026-06-03-research-radar-harvest/raw/openalex-2605.24259.json` | Conformance contracts and telemetry for future reuse align with Track 02's correctness-contract framing. | Our contract is answer-quality/fallback oriented, not allocator-residency arbitration. |
| Stateful Inference | `research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/raw/openalex-cli-2605.26289.json` | Delta-only agent turns are active prior art. | This ladder shows delta-only/tail-only quality can fail on reasoning-over-prefix tasks for local non-frontier models. |
| KVFlow | `research/04-negative-space-ideas/evidence/2026-06-03-research-radar-harvest/raw/openalex-2507.07400.json` | Workflow-aware agent KV policy is active prior art. | The novelty boundary is not agent KV scheduling; it is correctness-gated fallback and failure attribution. |
| Tutti | `research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/raw/openalex-cli-2605.03375.json` | SSD-backed KV movement can be made faster and more practical. | Faster storage would not solve this ladder's live-tail failure by itself. |
| KVDrive | `research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/raw/openalex-cli-2605.18071.json` | Multi-tier KV placement and scheduling address long-context systems bottlenecks. | Storage-tier optimization remains background; this ladder is a correctness mechanism test. |
| DUAL-BLADE | `research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/raw/openalex-cli-2604.26557.json` | NVMe-direct offload is relevant to edge inference. | This ladder's main failure appears before restore/offload, so NVMe path changes are not the immediate repair. |
| Swarm | `research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/raw/openalex-cli-2603.17803.json` | Multi-SSD co-activation-aware placement addresses bandwidth. | Bandwidth and placement are not implicated by live-tail 0/6. |

## Interpretation Boundary

Do not claim novelty for generic prefix caching, KV reuse, SSD-backed KV storage, or agent workflow cache policy. The defensible contribution remains narrower: correctness contracts, failure attribution, prompt/visibility repair probes, and fallback policy for persistent/session KV reuse on local non-frontier agent-style workloads.
