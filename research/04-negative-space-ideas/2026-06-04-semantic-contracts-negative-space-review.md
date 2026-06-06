# 2026-06-04 Semantic Contracts Negative-Space Review

## Bottom Line

The strongest pivot is not "we invented KV caching" or "we can hide context in a cache." Those areas are crowded. The surviving research direction is:

> Local agents need semantic contracts for state reuse: a way to decide when hidden KV, documented prefix cache reuse, visible evidence, recompute, summaries, or full replay are valid representations of the same task state.

This review is based on live OpenAlex/paper-harvester and web checks on 2026-06-04. The claims below are "plausibly net-new" hypotheses, not world-first guarantees.

## Claims Marked Off

| Claim | Status | Why |
| --- | --- | --- |
| New KV/prefix caching | Not novel | Prompt Cache, vLLM prefix caching, SGLang, llama.cpp, LMCache, and related serving systems already cover this space. |
| New persistent KV for agents | Not novel | Stateful Inference and Agent Memory Below the Prompt directly target persistent agent KV/state. |
| New SSD/offloaded KV tier | Not novel | LMCache, Tutti, KVDrive, DUAL-BLADE, Mooncake-style serving, and edge persistent KV papers are active. |
| New role-aware context routing | Not novel as stated | RCR-Router explicitly frames role-aware context routing with structured memory. |
| New selective recompute | Not novel as stated | CacheBlend, StepCache, Cache-Craft/related work, ProphetKV-style methods, and SCBench-adjacent work cover quality-preserving recompute. |
| New RAG evidence sufficiency | Crowded | SURE-RAG, ReflectiveRAG, S2G-RAG, and other sufficiency/gap-judging systems are active. |
| New KV privacy/security | Crowded | SafeKV, cache salting, cache-side channels, and cache corruption work already occupy this area. |

## Five Surviving Hypotheses

### 1. Semantic Continuation Conformance For KV Restore

Hypothesis: LLM serving runtimes need black-box conformance tests proving that a restored/session KV state behaves semantically like `full visible prefix + tail`, because telemetry can report slot save/restore while the model behaves like `tail only`.

Closest prior art:

- Resident KV Claims defines a future-reuse/residency contract, not full-prompt semantic equivalence.
- Fail-Closed Lowering handles runtime claim lowering and failure semantics, not hidden-prefix continuation behavior.
- When KV Cache Reuse Fails studies quality failures in judge-centric multi-agent inference, not endpoint restore semantics.

Smallest falsifying test:

- Across llama.cpp, vLLM/SGLang-style APIs, LMCache, and at least one hosted-like prefix cache abstraction, run codeword, key-value, structured graph, and tool-schema probes.
- Kill the claim if existing documented APIs already define and pass full-prompt semantic parity for restored hidden prefix plus tail-only continuation.

### 2. Architecture-Specific Safe-Reuse Envelopes

Hypothesis: cache/session reuse safety is architecture-specific. Full attention, sliding-window attention, hybrid attention, MLA, Mamba/SSM, recurrent state, and quantized KV do not share one safe reuse rule.

Closest prior art:

- SCBench evaluates long-context and KV-centric methods across model families.
- LMCache documents hybrid attention support.
- Runtime issue trackers show active friction around sliding-window, SSM/Mamba, and hybrid cache reuse.

Smallest falsifying test:

- Run the same semantic reuse suite across one full-attention model, one sliding-window/full hybrid, one MLA-style model, and one SSM/recurrent hybrid.
- Kill or narrow the claim if failures are backend-specific bugs rather than model-architecture-dependent reuse boundaries.

### 3. Prompt ABI For Cache-Safe Agents

Hypothesis: agent runtimes need a prompt ABI that marks stable, volatile, tool-schema, policy, evidence, secret, and freshness-sensitive spans so cache reuse is guided by contracts instead of accidental prefix layout.

Closest prior art:

- Prompt Cache defines reusable prompt modules and positional accuracy for attention reuse.
- RCR-Router routes role-relevant memory subsets under token budgets.
- Production prompt-caching guides recommend stable-prefix ordering, but do not appear to formalize agent-level correctness and cache contracts.

Smallest falsifying test:

- Compare naive stable-prefix ordering against an ABI-annotated context compiler on dynamic tool/schema/repo tasks.
- Kill the claim if ABI metadata does not improve correctness, cache hit rate, or failure attribution over simple prefix ordering.

### 4. Proof-Carrying Context Compilation For Structured Agent Workspaces

Hypothesis: for structured tasks such as repo graphs, dependency chains, parent walks, and tool traces, a deterministic context compiler can emit a small visible evidence slice plus a machine-checkable sufficiency certificate.

Closest prior art:

- SURE-RAG and related systems verify evidence sufficiency for RAG.
- GraphRAG and technical-literature RAG systems organize evidence, but generally rely on probabilistic/LLM judging rather than deterministic workspace certificates.
- Track 02 evidence controls suggest local GPT-OSS can answer correctly when exact incoming-edge evidence is surfaced.

Smallest falsifying test:

- On GraphWalks-style parent queries, compile minimal edge evidence plus a certificate such as "all incoming edges for target node are included."
- Kill or narrow the claim if perfect certificates and exact visible evidence do not improve local-model correctness beyond generic retrieval/compression.

### 5. Project-Scoped Erasure And Isolation For Persistent Local Agent State

Hypothesis: local agents need project-scoped erasure and isolation contracts across text traces, vector memory, prompt caches, KV snapshots, SSD artifacts, and scheduler state.

Closest prior art:

- SafeKV and vLLM cache salting address shared-serving privacy and timing leakage.
- Cache-side vulnerability work treats KV as an attack surface.
- The underexplored local angle is verifiable deletion/isolation across all persistent agent state tiers on one developer machine.

Smallest falsifying test:

- Create cross-project codeword and timing probes, delete one project, restart runtime according to documented procedure, and test for semantic or timing leakage into another project.
- Kill the claim if ordinary process restart plus cache-directory deletion fully eliminates observable leakage across tested local stacks.

## Strongest Paper Umbrella

Working title:

> Semantic Contracts for Local Agent State Reuse

The paper would not claim that KV caching is new. It would claim that local-agent systems need a correctness layer above caching: a representation router that chooses hidden KV, documented visible-prefix cache reuse, visible evidence, recompute, summary, or full replay based on semantic risk.

## Immediate Fit With Track 02

Track 02 currently has a concrete mechanism collapse:

- Hidden-prefix tail-only restore failed semantic continuation gates.
- Visible evidence repair worked on GraphWalks-style failures.
- Documented llama.cpp full-prompt resend with `cache_prompt: true` is being tested as the supported cache path.

If the documented cache path works, the paper framing becomes:

> State reuse is valid when the runtime can prove semantic and computational equivalence to full visible prompt execution.

If it fails, the paper framing becomes:

> Local agents need fallback state representations and conformance tests because backend cache telemetry alone is not a correctness contract.

## Source Anchors

- Prompt Cache: https://arxiv.org/abs/2311.04934
- CacheBlend: https://arxiv.org/abs/2405.16444
- SCBench: https://arxiv.org/abs/2412.10319
- RCR-Router: https://arxiv.org/abs/2508.04903
- When KV Cache Reuse Fails in Multi-Agent Systems: https://arxiv.org/abs/2601.08343
- StepCache: https://arxiv.org/abs/2603.28795
- Agent Memory Below the Prompt: https://arxiv.org/abs/2603.04428
- SURE-RAG: https://arxiv.org/abs/2605.03534
- Stateful Inference for Low-Latency Multi-Agent Tool Calling: https://arxiv.org/abs/2605.26289
- Resident KV Claims: https://arxiv.org/abs/2605.24259
- Fail-Closed Lowering of Resident KV Claims onto LLM Serving Runtimes: https://arxiv.org/abs/2606.01387
- vLLM prefix caching: https://docs.vllm.ai/en/v0.11.1/design/prefix_caching/
- LMCache hybrid attention models: https://docs.lmcache.ai/zh_CN/mp/hybrid_models.html
- MLX hybrid cache issue: https://github.com/ml-explore/mlx-lm/issues/980
- Can Transformer Memory Be Corrupted?: https://arxiv.org/abs/2510.17098
- SafeKV: https://openreview.net/pdf?id=jhDsbd5eXL

