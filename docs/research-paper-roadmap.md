# Research Paper Roadmap

Date: 2026-06-03

## Verdict

This is a good research topic if the paper is framed narrowly.

The paper should not be "SSD-native inference" or "KV caching for agents." Those areas already have strong prior art. The better paper topic is:

> Quality-Gated Persistent KV Reuse for Local Agent Loops

The core claim to investigate is that local agents can gain large prompt-processing speedups from persistent reusable inference state, but only if the system treats correctness parity and fallback as first-class parts of the cache design.

## Candidate Thesis

Local agent workloads repeatedly combine a stable prefix with a volatile tail. Persisting reusable prefix or KV state can reduce prompt-processing cost on ordinary machines, but restored-prefix or session-tail execution is not automatically equivalent to full-prompt execution. A practical local-agent cache must therefore include:

- a workload model for stable prefixes and volatile tails
- a correctness-parity protocol against full-prompt execution
- failure attribution across model capability, prompt protocol, scorer brittleness, and cache/session semantics
- a routing or fallback policy that chooses full-prompt execution when reuse is unsafe
- latency, I/O, and quality measurements reported together

## Prior-Art Boundary

Already covered:

| Topic | Why it is marked off |
| --- | --- |
| Prefix and KV caching | vLLM, PagedAttention, Prompt Cache, and provider prompt caching already establish this primitive. |
| Multi-turn KV reuse | CachedAttention targets repeated historical-token KV work in conversations. |
| Multi-tier and SSD-backed KV storage | LMCache, Mooncake, Tutti, DUAL-BLADE, Swarm, and related systems already make KV storage a GPU/CPU/DRAM/SSD systems problem. |
| Agentic prompt caching | Don't Break the Cache studies long-horizon hosted-provider prompt caching for agent tasks. |
| Workflow-aware agent cache policy | KVFlow studies agent workflow scheduling and KV cache eviction/prefetch. |
| Quality impact of KV reuse/compression | CacheBlend, CacheClip, SCBench, and semantic-integrity work show that cache reuse and compression must be evaluated for answer quality. |

Still underexplored enough to pursue:

- local non-frontier models rather than hosted frontier APIs
- local coding-agent and tool-loop workloads rather than only chat, RAG, or cloud serving traces
- persisted session state across calls or restarts on ordinary machines
- full-prompt versus restored-prefix/session-tail parity by task family
- failure taxonomy for cache-related quality drift
- quality-gated fallback policy for local inference state reuse

This is a methodology-and-systems paper unless the later implementation adds a clearly new storage or runtime mechanism.

## Research Questions

RQ1: How much prompt-processing cost can persistent prefix/KV reuse save for realistic local agent loops?

RQ2: Under what task families does restored-prefix or session-tail execution diverge from full-prompt execution?

RQ3: Can divergence be attributed to model weakness, prompt protocol, scorer brittleness, or cache/session semantics?

RQ4: Can a quality-aware routing policy keep most of the speed benefit while recovering full-prompt quality on risky tasks?

RQ5: Which storage and session boundaries matter most: whole-slot restore, prefix blocks, tail-only turns, partial recompute, SSD tiering, or compression?

## Hypotheses

H1: Large stable-prefix agent loops can recover meaningful prompt-processing savings from persisted reusable state.

H2: Quality drift is task-family dependent; simple instruction-following tasks are safer than reasoning-over-prefix tasks.

H3: A visible-prefix/session-formatted control can separate prompt-protocol failures from cache/session semantic failures.

H4: A conservative fallback policy can preserve much of the latency win while avoiding the worst correctness failures.

H5: Non-frontier local models will need stricter quality gates than frontier hosted models because model brittleness can look like cache failure.

## Required Baselines

Every serious result should compare against:

- full-prompt recompute
- repeated full-prompt replay for variance
- visible-prefix but session-formatted control
- restored-prefix/session-tail path
- backend-native prompt or slot cache when available
- at least one close systems baseline such as llama.cpp slot restore, vLLM/LMCache, or oMLX when practical
- a stronger-model control when quality failures are ambiguous

## Metrics

Report speed, storage, and quality together:

- prompt eval or prefill time
- time to first token
- wall-clock task time
- cache save, restore, and tail timing
- SSD read/write bytes and cache artifact size
- cache hit/miss state
- answer correctness or task success
- task-family split
- variance across reruns
- fallback rate and fallback reason

Do not average IFEval-style instruction following and GraphWalks-style reasoning into one comforting number without reporting the split.

## Experiment Ladder

1. Reproduce the current correctness result and rerun the six GraphWalks failures.
2. Add visible-prefix/session-formatted controls for those failures.
3. Add stronger tail instructions and scorer-brittleness checks.
4. Run stronger-model controls for ambiguous cases.
5. Expand the selected-case set across IFEval, GraphWalks, tool-use, RAG, and local coding tasks.
6. Add close systems baselines and report comparable metrics.
7. Implement a simple quality-aware fallback policy.
8. Measure end-to-end local-agent task success, not only prompt eval.

## Failure Taxonomy

Every failed parity case should be classified as one of:

- model cannot solve the task reliably
- model is too brittle under constrained output
- prompt protocol changes the task
- scorer or parser rejects an otherwise acceptable answer
- restored-prefix/session-tail semantics are not equivalent enough
- cache compatibility or position assumptions are wrong
- storage or runtime behavior caused a non-semantic failure

Ambiguous cases should stay ambiguous until a control resolves them.

## Paper Contributions

A credible first paper could contribute:

1. A local-agent cache-fragility benchmark with stable-prefix and volatile-tail fixtures.
2. A correctness-parity protocol for persistent/session KV reuse.
3. An empirical study of speed-quality tradeoffs on local non-frontier models.
4. A failure taxonomy for restored-prefix/session-tail divergence.
5. A quality-aware fallback policy and ablation.

A stronger systems paper would also need:

- a new storage layout, partial-restore scheme, or backend integration
- comparison against existing SSD/KV systems
- I/O-level explanation of where time is saved or lost
- reproducible implementation and raw datasets

## Paper Outline

1. Introduction: local agents repeat expensive stable context, but cache reuse can drift.
2. Background: prefill, KV cache, prefix caching, SSD/NVMe tiers, local-agent loops.
3. Related work: prefix caching, prompt-state reuse, multi-tier KV stores, SSD offload, agent prompt caching, quality-aware KV reuse.
4. Problem definition: stable-prefix/volatile-tail session reuse and full-prompt parity.
5. Methodology: workloads, baselines, controls, metrics, failure taxonomy.
6. System or harness: Flashcache and session-tail evaluation path.
7. Results: speed, quality, failures, fallback.
8. Discussion: model caveats, local-hardware limits, when not to cache.
9. Limitations and future work.
10. Conclusion.

## Working Rules

- Refresh the prior-art scan before public claims or paper drafts.
- Preserve raw data, scripts, model hashes, prompts, hardware notes, and command lines.
- Record negative results as evidence, not embarrassment.
- Treat model weakness as a first-class confounder.
- Keep `docs/references.md` current with every paper or system used for positioning.
- Prefer one clean, reproducible figure over five vague benchmark claims.

## Publication Path

Phase 1: arXiv-style technical report from the current harness once the correctness controls are credible.

Phase 2: workshop submission if the main contribution is the benchmark and methodology.

Phase 3: systems conference submission only if the project adds a stronger storage/runtime mechanism with competitive baselines.

The fastest honest path is a rigorous technical report first. It lets the research mature in public without pretending the systems contribution is finished.
