# Discovery Research Playbook

Date: 2026-06-03

## Purpose

This repo is not only trying to optimize a known cache path. It is trying to find a solution that may sit outside the obvious shape of the field.

That means the project should make room for strange ideas:

- using SSD state in ways that do not look like normal KV offload
- testing prompt/session layouts that look inefficient but preserve quality
- intentionally breaking prefix assumptions to learn where the model depends on full context
- mixing recompute, restore, compression, and fallback in non-standard ways
- treating weak local-model failures as signals about system design rather than only model limitations

The rule is not "be weird." The rule is:

> Challenge a mainstream assumption, make a measurable prediction, and design the fastest honest test that could prove the idea wrong.

## Discovery Posture

Good discovery research in this repo should feel a little uncomfortable. If an experiment obviously follows from prior art, it may still be useful, but it is probably not the route to a new result.

Prefer hypotheses that challenge one of these assumptions:

- cached state must preserve exact prefix bytes
- restored KV must aim for full equivalence on every task
- full-prompt fallback is only a safety net, not part of the core algorithm
- recompute is always the expensive thing to avoid
- SSD is useful only for cold KV capacity
- local non-frontier model brittleness is noise rather than a design constraint
- agent context should be assembled as text first and optimized later
- quality gates should happen after generation rather than during session planning

Do not confuse this with permission to make unsupported claims. The stranger the idea, the stronger the controls need to be.

## Hypothesis Template

Use this shape before running high-risk experiments:

```text
Hypothesis:
Mainstream assumption challenged:
Why this might work:
Why this might fail:
Smallest falsifying test:
Baseline:
Controls:
Metrics:
Confounders:
Expected artifact:
Stop rule:
```

The stop rule matters. If an idea cannot say what result would make us stop pursuing it, it is not yet a research hypothesis.

## High-Risk Experiment Lanes

### Lane 1: Quality-Gated Partial Reuse

Assumption challenged: cache reuse should either be equivalent or rejected.

Question: Can the system reuse only the parts of state that are safe for a task family, while routing the rest to recompute or full prompt?

Possible tests:

- classify IFEval versus GraphWalks before inference
- reuse stable system/tool state but recompute reasoning substrate
- compare full prompt, session-tail, partial visible-prefix, and fallback modes

Why it could be new: the contribution is not another cache hit rate; it is a correctness-aware reuse policy for local agents.

### Lane 2: Intentional Inefficiency For Quality

Assumption challenged: the best cache is the one that minimizes prefill.

Question: Are there small, deliberately recomputed anchor spans that recover most full-prompt quality while keeping most cache savings?

Possible tests:

- recompute task instructions and final constraint blocks while restoring tool/repo context
- recompute graph/task schema tokens but restore stable agent scaffolding
- sweep anchor span sizes and measure quality recovery per millisecond

Why it could be new: it treats recompute as a quality repair tool, not a failure of caching.

### Lane 3: Failure-First Cache Design

Assumption challenged: benchmark success cases should drive cache design.

Question: If we design around the cases where session-tail fails, do we get a better cache policy than if we optimize the average case?

Possible tests:

- start from the six GraphWalks failures
- create controls that isolate model weakness, prompt protocol, scorer brittleness, and cache/session semantics
- derive reuse rules from failure taxonomy before broad benchmarking

Why it could be new: it turns negative results into the primary design signal.

### Lane 4: Agent Context Compilation

Assumption challenged: agent context should be optimized only after it is written as normal text.

Question: Can an agent session be compiled into storage-aware state roles before inference: immutable rules, tool schemas, repo facts, reasoning anchors, volatile tails, and discardable logs?

Possible tests:

- annotate prompt spans with role metadata
- compare naive prefix caching with role-aware restore/recompute/fallback
- measure whether role labels predict safe reuse better than token position alone

Why it could be new: it moves the optimization boundary from runtime cache mechanics to agent-context design.

### Lane 5: Local-Model-Aware Cache Policy

Assumption challenged: cache policy is mostly model-independent.

Question: Do smaller or weaker local models need different reuse rules than frontier hosted models because they are less robust to prompt/session perturbations?

Possible tests:

- run the same parity set across model sizes and quantization levels
- measure whether fragile models require more visible anchors or more fallback
- report model-specific safe-reuse envelopes

Why it could be new: it treats non-frontier brittleness as a first-class systems variable.

### Lane 6: SSD As Experiment Memory

Assumption challenged: SSD value is only serving-time KV capacity.

Question: Can persisted session state, failure traces, and reusable evaluation artifacts make local research loops faster even when the final serving system still falls back often?

Possible tests:

- cache and replay prefix states for benchmark controls
- persist failed-case state for exact debugging
- measure researcher iteration time, not just inference latency

Why it could be new: it broadens "SSD-native inference" into a research and agent-loop infrastructure problem.

## Evidence Rules

Every discovery experiment should produce:

- raw run directory
- README with hypothesis and stop rule
- exact commands
- model and backend identifiers
- prompt or fixture hashes
- result table split by task family
- failure notes
- next decision: abandon, narrow, repeat, or promote

Never promote an idea because it is exciting. Promote it because it survived a test designed to kill it.

## Review Questions

Before accepting a discovery result, ask:

1. What assumption did this challenge?
2. What would prior art predict?
3. What did we measure that prior art probably would not?
4. Could model weakness explain the result?
5. Could prompt formatting explain the result?
6. Could scorer brittleness explain the result?
7. Did we learn a mechanism or only observe a number?
8. What is the next smallest test?

## Relationship To The Paper

The paper roadmap remains the disciplined path to publication. This playbook supplies the discovery engine.

The ideal loop is:

```text
strange hypothesis
-> smallest falsifying test
-> failure taxonomy
-> reproducible result
-> paper-roadmap promotion or abandonment
```

If a surprising result cannot be reproduced, it stays a lab note. If it survives controls and explains a mechanism, it can become the paper's contribution.
