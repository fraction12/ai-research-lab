# Agent Handoff

Date: 2026-06-03

This document is for a fresh Codex agent opened on this repo. It captures the current project state, research framing, and next useful moves.

## Repo Identity

- Local path: `/Users/dushyantgarg/Documents/Projects/ai-research-lab`
- GitHub remote: `https://github.com/fraction12/ai-research-lab.git`
- Current branch: `main`
- Previous repo name/path: `ssd-native-inference`
- Current framing: this is now an AI research lab repo with multiple research tracks.

The original SSD-native inference work was not deleted. It was moved into `research/01-ssd-native-inference-current/` and should be treated as track 01 of the lab.

## First Files To Read

1. `AGENTS.md`
2. `README.md`
3. `research/README.md`
4. The relevant research track README.

For the current main paper direction, read:

1. `research/02-quality-gated-stateful-kv-reuse/README.md`
2. `research/01-ssd-native-inference-current/docs/flashcache-system-report.md`
3. `research/01-ssd-native-inference-current/docs/research-paper-roadmap.md`
4. `research/04-negative-space-ideas/README.md`
5. `research/04-negative-space-ideas/2026-06-03-negative-space-scan.md`

## Operating Posture

- Use root OpenSpec for meaningful changes.
- Keep changes small, reviewable, and evidence-backed.
- Do not claim novelty without refreshing prior art online.
- Preserve exact commands, model names, hardware, quantization, prompts, raw outputs, data paths, and source links.
- Treat negative results as research evidence.
- Keep source notes in the relevant track references file or negative-space note.
- Separate model weakness, prompt-protocol weakness, scorer brittleness, and cache/session semantics when interpreting failures.

## Current Research Tracks

| Track | Folder | Status |
| --- | --- | --- |
| SSD-native inference current track | `research/01-ssd-native-inference-current/` | Existing Flashcache harness, benchmarks, docs, and tests. |
| Quality-gated stateful KV reuse | `research/02-quality-gated-stateful-kv-reuse/` | Main next paper candidate. |
| Role-aware context compilation | `research/03-role-aware-context-compilation/` | Higher-risk discovery track. |
| Negative-space research ideas | `research/04-negative-space-ideas/` | Living idea archive and prior-art boundary notes. |

## What We Know So Far

The strongest current evidence is from the Flashcache harness in track 01.

- SSD-backed reusable local-agent inference state can reduce prompt-processing cost on repeated stable-prefix workloads.
- Session-tail mode on a large 64 KB Printy-style fixture showed about 79.8% prompt-processing savings.
- The current implementation is an evidence harness around existing backend primitives, not a final custom SSD-native KV engine.
- Speed alone is not sufficient. The latest correctness-parity run selected 42 cases where full prompt passed, then tested session-tail on those same cases.
- Session-tail passed 31/42 overall, 31/36 IFEval, and 0/6 GraphWalks.
- That means the current session-tail path looks promising for simpler instruction-following tasks but is not quality-safe for reasoning-over-prefix tasks.

Important caveat: the model used in the latest correctness run was a local GPT-OSS 20B GGUF model, not a frontier model. Some failures may come from model capability or brittleness rather than cache semantics alone. Do not over-interpret failures as "Flashcache breaks reasoning" until controls isolate the cause.

## Current Paper Framing

The broad topic "SSD-native inference" is too broad and too close to existing prior art. The sharper candidate topic is:

> Quality-Gated Persistent KV Reuse for Local Agent Loops

The paper should investigate whether persistent reusable inference state can accelerate local agent loops while preserving full-prompt quality through explicit correctness contracts, failure attribution, and fallback policy.

This is probably a methodology-and-systems paper unless the implementation later adds a clearly new storage/runtime mechanism.

Marked-off prior art areas include:

- prefix and KV caching
- multi-turn KV reuse
- multi-tier and SSD-backed KV storage
- hosted-provider prompt caching for agents
- workflow-aware agent cache policy
- quality impact of KV reuse or compression

The underexplored wedge is local, non-frontier, ordinary-machine agent loops where stable prefixes, tool schemas, repo context, and memory blocks repeat across turns, but quality drift must be measured against full-prompt controls.

## Main Next Experiment

Do not run another broad benchmark first. Start with the six selected GraphWalks cases where full prompt passed and session-tail failed.

Recommended ladder:

1. Rerun full prompt on the six GraphWalks cases to measure variance.
2. Run a visible-prefix but session-formatted control.
3. Run tail-only with stronger answer hints.
4. Run reset/restore sanity checks.
5. Check scorer/parser brittleness.
6. If practical, run stronger-model controls.
7. Classify each failure as model weakness, prompt protocol, scorer brittleness, cache/session semantics, compatibility/position issue, or runtime/storage issue.

Only after that should the repo design a new lower-level SSD/KV layer.

## Research Rules For New Ideas

This lab is intentionally looking for negative space: ideas that may feel against the grain but can be tested cleanly.

For every unconventional idea, write:

- the mainstream assumption it challenges
- why it might work
- why it might fail
- the smallest falsifying test
- the expected artifact
- the stop rule

Current promising high-risk directions:

- quality-gated stateful KV reuse
- role-aware context compilation
- intentional recompute as a quality repair tool
- model-specific safe-reuse envelopes for local non-frontier models
- consumer SSD and AI-PC co-design for local agent traces
- privacy, deletion, and cross-project isolation for persistent local KV state

## Validation Snapshot

Last known clean validation before this handoff:

```bash
openspec validate --all --strict
```

Result: 9 specs passed.

```bash
cd research/01-ssd-native-inference-current
python3 -m unittest discover -s tests
```

Result: 45 tests ran OK, 1 skipped.

For future code changes, rerun the relevant track tests from the track folder because several benchmark paths are relative.

## Practical First Hour For A New Agent

1. Confirm `pwd` is `/Users/dushyantgarg/Documents/Projects/ai-research-lab`.
2. Confirm `git remote -v` points to `fraction12/ai-research-lab`.
3. Read `AGENTS.md`, this file, and `research/README.md`.
4. If making meaningful changes, use root OpenSpec.
5. If making paper-facing claims, refresh prior art online first.
6. If continuing the main research, work in `research/02-quality-gated-stateful-kv-reuse/` and use track 01 evidence as the source dataset.
7. If touching Flashcache itself, first read `research/01-ssd-native-inference-current/docs/flashcache-metal-direction.md`.

## Things Not To Assume

- Do not assume SSD can act like VRAM.
- Do not assume restored/session-tail execution is equivalent to full-prompt execution.
- Do not assume a failure is caused by caching until model, prompt, scorer, and runtime controls are checked.
- Do not blend instruction-following and reasoning-over-prefix quality into one aggregate without task-family splits.
- Do not optimize only for latency; quality and fallback behavior are part of the system.
- Do not treat local non-frontier model behavior as representative of stronger frontier models without controls.
