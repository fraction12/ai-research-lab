# Paper Defense Memo: Quality-Gated KV/Session Reuse

Date: 2026-06-04

Purpose: frame the Track 02 paper direction without overclaiming novelty. This memo uses the repo-local `pp-paper-harvester` skill for metadata checks, the Track 02 GraphWalks experiment artifacts, and live source checks. It is intentionally adversarial: the point is to make the paper harder for a reviewer to dismiss.

## Bottom Line

Do not frame the paper as new KV caching, new agent caching, new RAG, or new selective recomputation. Those claims are crowded.

The defensible Track 02 framing is narrower:

> Local agent loops can save prefill work with persistent/session KV reuse, but hidden cached state is not automatically a quality-equivalent substitute for full-prompt execution. A useful local runtime needs task-family-aware correctness gates, failure attribution, and conservative fallback when reasoning-over-prefix tasks fail reuse.

The current GraphWalks repair ladder strengthens the negative side of the paper. For this model/protocol stack, visible-anchor prompt proxies did not produce correctness-safe repair. That does not kill the paper; it moves the strongest contribution toward failure taxonomy, parity protocol, and fallback policy.

## Zeroth-Principle Frame To Preserve

Conditional north-star framing:

> Local agents should stop treating context as text and start treating it as scheduled compute.

Paper-safe version:

> For local agent loops, the core bottleneck is not model size or context length alone. It is that current runtimes spend full transformer compute on context spans whose value differs by role, task, and turn. A faster or higher-quality local agent should come from a quality-gated context scheduler that decides, per span, whether to reuse hidden state, replay visible evidence, recompute anchors, compress, drop, or fall back to full prompt.

This is not yet a proven Track 02 result. Preserve it as the broader research frame if later experiments show that role-aware visible evidence, selective recompute, or fallback routing can recover full-prompt parity under a lower compute budget.

The useful hypothesis is:

> A local agent can outperform naive full-context replay under a fixed compute budget by reallocating transformer work from low-value repeated context to high-value visible or recomputed evidence.

This frame is broader than KV caching but still testable. It avoids crowded novelty claims by making cache reuse one execution option among several, not the whole contribution.

Possible span policy:

| Context span | Candidate execution policy |
| --- | --- |
| Stable system/developer rules | Prefix reuse or full resend if policy changes |
| Tool schemas | Prefix reuse, schema hashing, or cached prefill |
| Repo facts and memory summaries | Reuse, compression, or periodic refresh |
| Task evidence for reasoning | Visible replay or targeted recompute |
| Reasoning anchors | Visible replay when parity risk is high |
| Logs and low-value history | Summarize, drop, or keep outside prompt |
| Uncertain or high-risk cases | Full-prompt fallback |

If future evidence supports this, a stronger paper spine becomes:

> Quality-Gated Context Scheduling for Local Agent Inference.

If future evidence does not support repair, keep the narrower paper frame: hidden state is not prompt visibility, and full-prompt fallback is part of a correct local cache policy.

## Claim Ledger

### Safe Claims We Can Likely Defend

- Local agent workloads repeat large stable prefixes such as system/developer instructions, tool schemas, repo context, and memory summaries.
- Persistent/session reuse can reduce prompt-processing cost on repeated stable-prefix workloads.
- Stateful/session reuse is not automatically equivalent to full-prompt recomputation.
- Track 02 GraphWalks evidence shows a task-family split: full-prompt replay passed, while session-tail/live-tail paths failed on the fixed six reasoning-over-prefix cases.
- For the fixed six GraphWalks cases, the current evidence supports full-prompt fallback rather than hidden reuse or anchor-proxy repair.
- Correctness gates and fallback policy are part of the cache design, not an afterthought.

### Crowded Claims We Should Avoid

- "We introduce KV cache reuse for agents."
  - Marked off by [Stateful Inference for Low-Latency Multi-Agent Tool Calling](https://arxiv.org/abs/2605.26289), [KVFlow](https://arxiv.org/abs/2507.07400), and [Don't Break the Cache](https://arxiv.org/abs/2601.06007).
- "We introduce selective recomputation over reused KV state."
  - Marked off by [ProphetKV](https://arxiv.org/abs/2602.02579), [QCFuse](https://arxiv.org/abs/2604.08585), [Cache-Craft](https://arxiv.org/abs/2502.15734), and [CacheBlend](https://arxiv.org/abs/2405.16444).
- "We introduce semantic anchors or visible evidence slices."
  - Marked off by [QCFuse](https://arxiv.org/abs/2604.08585), [Self-RAG](https://arxiv.org/abs/2310.11511), [LongLLMLingua](https://arxiv.org/abs/2310.06839), and long-context evidence placement work such as [Lost in the Middle](https://arxiv.org/abs/2307.03172).
- "SSD-backed KV/offload is the main novelty."
  - Marked off by systems such as [Tutti](https://arxiv.org/abs/2605.03375), KVDrive, DUAL-BLADE, Swarm, LMCache, and adjacent multi-tier KV work.

### Speculative Claims That Need More Evidence

- Role-aware anchors beat generic retrieval, prompt compression, or query-similarity selection at the same token budget.
- A lower-level KV/layer selective recompute mechanism can repair GraphWalks failures where prompt-level anchors did not.
- Local non-frontier models need stricter reuse contracts than frontier hosted models.
- A simple quality-risk router can preserve most speed benefit while recovering full-prompt quality.
- The observed GraphWalks collapse generalizes to coding-agent, tool-use, RAG, or longer local-agent workloads.

### Rejected Claims Contradicted By Current Experiments

- "Session-tail is quality-safe for reasoning-over-prefix."
  - Rejected by the six-case GraphWalks ladder: full-prompt replay passed `18/18`, session-tail replay/reset-restore passed `0/18`.
- "Disk save/restore or SSD behavior is the primary cause."
  - The repair ladder's `live_tail` no-restore control also passed `0/6`, so the failure appears before disk restore.
- "Visible-anchor prompt proxies repair the current GraphWalks cohort."
  - All live repair controls passed `0/6`; the 256-token anchor proxy raised mean score to about `0.4202` but did not produce correctness-safe repair.
- "Stronger tail instructions are enough."
  - The six-case ladder's stronger tail hints passed `0/6` and produced malformed JSON/prose outputs.

## Related-Work Matrix

| Bucket | Major sources | What reviewers may say | Boundary for this paper |
| --- | --- | --- | --- |
| Persistent/session KV reuse | [CachedAttention](https://arxiv.org/abs/2403.19708), [Stateful Inference](https://arxiv.org/abs/2605.26289), HCache, LMCache | "Multi-turn/session KV reuse is already studied." | We are not claiming the reuse primitive. We study full-prompt parity, failure classes, and fallback for local reasoning-over-prefix cases. |
| Query-conditioned or selective recomputation | [ProphetKV](https://arxiv.org/abs/2602.02579), [QCFuse](https://arxiv.org/abs/2604.08585), [Cache-Craft](https://arxiv.org/abs/2502.15734), [CacheBlend](https://arxiv.org/abs/2405.16444) | "Anchor recompute is just RAG-cache selective recompute." | Current Track 02 prompt-level anchor proxies failed; future lower-level recompute must be framed as a repair control, not as the core novelty unless it clearly differs. |
| Semantic anchors / visible evidence slices | [QCFuse](https://arxiv.org/abs/2604.08585), [Self-RAG](https://arxiv.org/abs/2310.11511), [LongLLMLingua](https://arxiv.org/abs/2310.06839) | "Evidence selection and semantic anchors are not new." | Our angle is not evidence selection itself; it is whether prompt visibility/recompute can restore parity after hidden session state fails. Current evidence says not yet. |
| KV cache correctness failures | [When KV Cache Reuse Fails](https://arxiv.org/abs/2601.08343), [SCBench](https://arxiv.org/abs/2412.10319), [CacheBlend](https://arxiv.org/abs/2405.16444) | "Quality effects of cache reuse are known." | Track 02 contributes a local-agent parity protocol and failure taxonomy for restored/session-tail execution, not a broad cache-quality benchmark yet. |
| Long-context retrieval failures | [Lost in the Middle](https://arxiv.org/abs/2307.03172), [LongLLMLingua](https://arxiv.org/abs/2310.06839), [Found in the Middle](https://arxiv.org/abs/2403.04797) | "This is position bias or context compression under another name." | Position and evidence visibility are likely confounders; Track 02 should report them explicitly rather than claim they are new. |
| Quality gates and fallback policies | [METIS](https://www.microsoft.com/en-us/research/publication/metis-fast-quality-aware-rag-systems-with-configuration-adaptation-tr/), [Self-RAG](https://arxiv.org/abs/2310.11511), [SCBench](https://arxiv.org/abs/2412.10319) | "Quality-aware routing already exists in RAG." | The narrower gap is quality gating for persistent local inference state, with full-prompt parity as the control. |
| Agent context compression and compaction | [ACON](https://arxiv.org/abs/2510.00615), [Parallel Context Compaction](https://arxiv.org/abs/2605.23296), [LongLLMLingua](https://arxiv.org/abs/2310.06839) | "Scheduling context spans is just context compression with another name." | The broader frame must measure quality per execution policy: hidden reuse, visible replay, recompute, compression, drop, and fallback. Do not claim compression novelty. |
| Local agent-loop inference | [Don't Break the Cache](https://arxiv.org/abs/2601.06007), [KVFlow](https://arxiv.org/abs/2507.07400), [Stateful Inference](https://arxiv.org/abs/2605.26289), [On-Device Language Models](https://arxiv.org/abs/2409.00088) | "Agent caching is an active area." | Our paper should emphasize local non-frontier models, ordinary-machine constraints, and correctness drift by task family. |
| SSD/multi-tier KV storage | [Tutti](https://arxiv.org/abs/2605.03375), KVDrive, DUAL-BLADE, Swarm, LMCache | "SSD-backed KV is already a systems topic." | Storage is background motivation unless this repo later adds a distinct storage/runtime mechanism. Current Track 02 failures are semantic/protocol failures, not SSD bandwidth failures. |

## Novelty Wedge Recommendation

### If The Anchor Experiment Succeeds

Strongest framing:

> Parity-Gated KV Reuse for Local Agent Loops with Minimal Visible Anchors.

Defensible contribution:

- A failure-driven benchmark and protocol for full-prompt parity.
- Evidence that small role-selected visible/recomputed anchors can recover reasoning-over-prefix quality for local agent loops.
- A speed/quality/fallback tradeoff that compares hidden reuse, anchor repair, and full fallback.

Reviewer risk:

- Must compare against generic retrieval/compression and selective recomputation prior art. Otherwise reviewers will say this is QCFuse/ProphetKV under a local-agent name.

### If The Anchor Experiment Partially Succeeds

Strongest framing:

> A Failure Taxonomy and Fallback Protocol for Stateful KV Reuse in Local Agent Loops.

Defensible contribution:

- Show which failures are repairable by visibility and which are not.
- Define a conservative quality-risk router.
- Preserve negative results as design evidence.

Reviewer risk:

- Needs enough cases and task families beyond six GraphWalks to avoid reading as an anecdote.

### If The Anchor Experiment Fails

Strongest current framing:

> Hidden State Is Not Prompt Visibility: A Parity Study of Stateful KV Reuse for Local Reasoning Loops.

Defensible contribution:

- A precise negative result: full prompt passes, live-tail/session-tail fails, prompt-level anchor proxies do not restore exact correctness.
- A practical fallback policy: GraphWalks-style reasoning-over-prefix should require full-prompt execution for this model/protocol stack.
- A warning against treating cached/session state as a drop-in replacement for full prompt on local non-frontier models.

Reviewer risk:

- Must avoid implying universal failure of KV reuse. The evidence is a fixed six-case local-model cohort. The paper needs either more task families or a deliberately narrow technical-report scope.

## Current Track 02 Evidence Boundary

Current committed evidence:

- Six fixed GraphWalks cases: `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, `graphwalks-19`.
- Full-prompt replay variance: `18/18` attempts passed.
- Session-tail replay/reset-restore: `0/18` attempts passed.
- Visible-prefix/session-formatted control: `3/6` cases passed in the first ladder.
- Repair mechanism ladder: every live control passed `0/6`.
- `live_tail` no-restore also passed `0/6`, weakening the hypothesis that disk restore is the primary cause.
- `anchor_recompute_256` raised mean score to about `0.4202`, but no case reached correctness parity.

Paper implication:

> The current evidence supports conservative fallback for GraphWalks-style reasoning-over-prefix tasks. It does not support anchor repair as a safe policy yet.

## Reviewer-Adversarial Questions

1. Is this just RAG/context compression?
   - It will look that way unless the paper is centered on hidden-session-state parity and fallback, not evidence selection.
2. Is this just KV cache reuse?
   - Yes, if we claim speed. No, if we show task-family-specific quality drift and a correctness protocol.
3. Are six GraphWalks cases enough?
   - Not for a broad paper. They are enough for a mechanism note or a first technical-report section that motivates broader evaluation.
4. Does anchor failure weaken the paper?
   - It weakens the repair story, but strengthens the fallback story.
5. Can we claim local-model specificity?
   - Only as a hypothesis until the same protocol runs on another local model or a stronger-model control.

## Specific Source Links

- Persistent / session reuse: [CachedAttention](https://arxiv.org/abs/2403.19708), [Stateful Inference](https://arxiv.org/abs/2605.26289), [HCache](https://arxiv.org/abs/2410.05004)
- Agent/workflow caching: [Don't Break the Cache](https://arxiv.org/abs/2601.06007), [KVFlow](https://arxiv.org/abs/2507.07400)
- Selective recompute / cache fusion: [CacheBlend](https://arxiv.org/abs/2405.16444), [Cache-Craft](https://arxiv.org/abs/2502.15734), [ProphetKV](https://arxiv.org/abs/2602.02579), [QCFuse](https://arxiv.org/abs/2604.08585), [EPIC](https://arxiv.org/abs/2410.15332), [KVShare](https://arxiv.org/abs/2503.16525)
- Correctness and quality: [When KV Cache Reuse Fails](https://arxiv.org/abs/2601.08343), [SCBench](https://arxiv.org/abs/2412.10319)
- Evidence placement and compression: [Lost in the Middle](https://arxiv.org/abs/2307.03172), [LongLLMLingua](https://arxiv.org/abs/2310.06839), [Self-RAG](https://arxiv.org/abs/2310.11511), [Found in the Middle](https://arxiv.org/abs/2403.04797)
- Quality-aware RAG routing: [METIS](https://www.microsoft.com/en-us/research/publication/metis-fast-quality-aware-rag-systems-with-configuration-adaptation-tr/)
- Agent context compression and compaction: [ACON](https://arxiv.org/abs/2510.00615), [Parallel Context Compaction](https://arxiv.org/abs/2605.23296)
- Context-independent or packetized cache reuse: [KV Packet](https://arxiv.org/abs/2604.13226)
- Local/on-device background: [On-Device Language Models](https://arxiv.org/abs/2409.00088)

## Recommended Paper Posture

Use this as a first technical report framing:

> We do not propose that KV/session reuse is always safe. We show why it needs a correctness contract. In local reasoning-over-prefix cases, hidden cached state can fail even when full prompt is stable and correct; prompt-level anchor repair may improve partial scores but still fail parity. Therefore a local agent runtime should treat full-prompt fallback as part of the cache policy.

Do not make public novelty claims until the paper either:

1. Expands task-family evidence beyond six GraphWalks cases, or
2. Adds a genuinely lower-level recompute/restore mechanism that prior art does not already cover, or
3. Explicitly publishes as a narrow negative-results technical report.
