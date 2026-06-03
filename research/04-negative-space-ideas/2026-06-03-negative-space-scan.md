# 2026-06-03 Negative-Space Scan

## Bottom Line

The speed story around SSD/KV/stateful agent inference is getting crowded. The best gaps are less about "can we cache state?" and more about correctness, role-aware context planning, model-specific safety envelopes, and local-machine constraints that cloud-serving papers often ignore.

## Marked Off

| Area | Status | Representative sources |
| --- | --- | --- |
| Generic SSD-backed KV offload | Crowded | Tutti, KVDrive, DUAL-BLADE, Swarm, LMCache, Dynamo |
| Stateful agent speedups | Now active | Stateful Inference for Low-Latency Multi-Agent Tool Calling, LayerScale |
| Agent memory benchmarks | Active | EvoMemBench, MemEvoBench, AgentMemoryBench |
| KV-cache security in shared serving | Active | Shadow in the Cache, SafeKV |
| Local inference efficiency and energy | Active | Bench360, Intelligence per Watt |

## Candidate Gaps

### 1. Correctness Contracts For Stateful KV Reuse

Question: When is stateful or delta KV reuse equivalent enough to full-prompt execution, especially for local non-frontier models?

Why it matters: speedups are not useful if restored state silently changes reasoning behavior.

### 2. Role-Aware Agent Context Compilation

Question: Can agent context be compiled into roles before inference, so the system knows what to restore, recompute, show visibly, or discard?

Why it matters: token position alone may be too weak for safe reuse policy.

### 3. Intentional Recompute As Quality Repair

Question: Can recomputing small anchor spans recover quality better than all-or-nothing cache reuse?

Why it matters: most cache work treats recompute as waste, but local agents may need selective recompute to stay reliable.

### 4. Model-Specific Safe-Reuse Envelopes

Question: Do smaller, quantized, local models need different cache/session policies than frontier hosted models?

Why it matters: model brittleness can look like cache failure unless it is measured directly.

### 5. Consumer SSD / AI-PC Agent Trace Co-Design

Question: What do real local-agent traces require from consumer SSDs: latency, IOPS, endurance, thermal behavior, artifact layout, and cleanup?

Why it matters: AI-PC SSD marketing is emerging, but open evidence for actual local-agent traces appears thin.

### 6. Local Persistent KV Privacy And Deletion

Question: What security model should local persistent KV artifacts have across projects, users, and repos?

Why it matters: cloud multi-tenant KV leakage has attention, but local persistent state creates deletion, forensic residue, and cross-project contamination questions.

## Source Anchors

- Stateful Inference for Low-Latency Multi-Agent Tool Calling: https://arxiv.org/abs/2605.26289
- Tutti: https://arxiv.org/abs/2605.03375
- KVDrive: https://arxiv.org/abs/2605.18071
- DUAL-BLADE: https://arxiv.org/abs/2604.26557
- Swarm: https://arxiv.org/abs/2603.17803
- EvoMemBench: https://arxiv.org/abs/2605.18421
- MemEvoBench: https://arxiv.org/abs/2604.15774
- Shadow in the Cache: https://arxiv.org/abs/2508.09442
- SafeKV: https://arxiv.org/abs/2508.08438
- Bench360: https://arxiv.org/abs/2511.16682
- Intelligence per Watt: https://arxiv.org/abs/2511.07885

## Evidence Harvest

- 2026-06-03 metadata harvest: `research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/negative-space-harvest-summary.md`
- Raw provider outputs: `research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/raw/`
- Method: exact arXiv DOI-form OpenAlex lookups through `openalex-pp-cli`, with arXiv HTML confirmation after arXiv Atom API rate limiting.
- Follow-up tooling: the workflow was printed as internal `paper-harvester-pp-cli` and exposed through `.codex/skills/pp-paper-harvester/SKILL.md`.
- Full-text/PDF status: no PDFs or full-text files downloaded.
