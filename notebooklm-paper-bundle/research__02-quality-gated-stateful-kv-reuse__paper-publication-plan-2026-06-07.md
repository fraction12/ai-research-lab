# Paper Publication Plan: KV Capsules + Code Mode

Date: 2026-06-07

## End Goal

Write and publish a credible research paper about quality-gated hidden-state reuse for local tool-using agents.

The target paper should make a narrow, defensible claim:

> A KV capsule + Code Mode runtime can replace repeatedly visible stable tool/context prompts with restored hidden state while preserving tool-use behavior under strict controls, and compares favorably against a real Codex/Ollama text-compaction baseline on the tested repeated-work stream.

Do not claim:

- We invented KV caching.
- KV capsules universally beat text compaction.
- The repeated-work lane is a prompt-identical comparison.
- The current implementation proves a broad speed theorem.

## Current Best Title Candidates

- KV Capsules for Local Tool-Using Agents
- Hidden-State Reuse for Local Tool-Using Agents
- Quality-Gated Hidden-State Reuse for Local Tool-Using Agents
- Hidden State Is Not A Summary: KV Capsules for Tool-Using Local Agents

Working title recommendation:

> Quality-Gated Hidden-State Reuse for Local Tool-Using Agents

## Publication Path

### Primary Path

1. Write a complete technical paper in repo.
2. Release an arXiv preprint once references, figures, source package, and claims are verified.
3. Submit to a relevant ML/NLP/systems venue or workshop after the preprint is stable.

### Venue Options To Track

- NeurIPS-style ML/systems evaluation track if the paper becomes strong enough on evaluation breadth. NeurIPS 2026 listed a full paper deadline of May 6, 2026 AOE, so the next comparable cycle must be checked when dates are posted.
- ICLR-style ML venue if the story becomes a clean learning-systems contribution. ICLR allows arXiv papers under its dual-submission policy, but exact dates and policies must be checked for the target year.
- ACL/ARR or an ACL systems/evaluation workshop if the framing is local language-agent tool use and evaluation. ACL 2026 used ARR submission/commitment, so future ACL-family submissions should be planned around ARR cycles.
- arXiv first if we want priority and open feedback before peer review. The paper must be an original empirical/technical contribution, not a survey or position-only article.

Online checks used for this plan:

- NeurIPS 2026 call listed full paper deadline and submission materials expectations: https://nips.cc/Conferences/2026/CallForPapers
- ICLR 2026 call noted arXiv is allowed under its dual-submission policy: https://iclr.cc/Conferences/2026/CallForPapers
- ACL 2026 main conference used ARR submission/commitment flow: https://2026.aclweb.org/calls/main_conference_papers/
- ACL 2026 Industry Track focused on practical deployment issues for language technologies: https://2026.aclweb.org/calls/industry_track/
- arXiv submission docs describe LaTeX/source package and announcement process: https://arxiv.github.io/arxiv-submission-core/announcement_process.html

## Paper Spine

### 1. Problem

Local agent runtimes repeatedly resend stable context: tool schemas, runtime contracts, system/developer rules, and long environment descriptions. Text compaction reduces visible length but changes the information into a generated summary. KV capsules preserve a different object: the model's hidden state after reading the stable prefix.

### 2. Mechanism

Build a stable prefix, evaluate it once, save the llama.cpp sequence/KV state, restore it later, and append only the task tail. Compare restored state against native live append, full visible prompt, fresh tail, wrong capsule, compact visible evidence, and direct visible tools.

### 3. Code Mode

Code Mode is not decoration. It is the compact tool-use contract that makes hidden-state reuse usable. It gives the model a small structured interface instead of relying on repeated raw tool-schema text.

### 4. Controls

The paper lives or dies on controls:

- Native live append: same prefix and tail without save/restore.
- Restored KV capsule: saved prefix state plus task tail.
- Fresh tail: task tail without stable prefix state.
- Wrong capsule: task tail with irrelevant hidden state.
- Compact visible evidence: visible summary instead of restored hidden state.
- Direct visible tools: regular tool schema prompt without Code Mode.

### 5. Practical Baseline

Codex/Ollama with regular visible tool prompts and natural text-summary compaction is a practical runtime baseline. It is not a prompt-identical mechanism baseline. Label it as:

`codex_ollama_regular_tools_natural_text_compaction`

## Frozen Evidence Set

### Paper-Grade Selected Cohort

Source files:

- `experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/selected-cohort-findings.md`
- `experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/selected-cohort-summary.json`

Key facts:

- Cases: `100 / 100`
- Control records: `700 / 700`
- Code Mode full visible: `100 / 100`
- Native live append: `100 / 100`
- Restored KV capsule: `100 / 100`
- Native/restored hash parity: `100 / 100`
- Fresh-tail leaks: `0`
- Wrong-capsule leaks: `0`
- Direct visible tools: `91 / 100`
- Compact visible evidence Code Mode: `19 / 100`

Claim supported:

> Restored KV state matched native live-append behavior on the selected BFCL-derived cohort under strict negative controls.

Claim not supported:

> Restored KV is faster in this implementation.

### Repeated-Work Runtime Result

Source files:

- `experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/repeated-work-speed-findings.md`
- `experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/repeated-work-speed-summary.json`
- `experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/repeated-work-speed-run-info.json`

KV + Code Mode:

- Pass: `100 / 100`
- Cumulative wall: `853,499 ms`
- Visible input tokens: `3,900`

Natural Codex/Ollama text compaction:

- Run label: `bfcl-repeated-work-codex-natural-chained-v1`
- Pass: `86 / 100`
- Cumulative wall: `11,813,816 ms`
- Reported visible input tokens: `245,774,883`
- Codex session compaction events: `89`
- Exact `context_compacted` hits in `.codex/sessions`: `89`
- Summary-text hits: `180`

Claim supported:

> The KV capsule + Code Mode system compared favorably against the tested practical Codex/Ollama regular-tool text-compaction route on pass rate, wall time, and visible prompt burden.

Claim not supported:

> KV capsules beat Codex compaction under prompt-identical conditions.

### Supporting BFCL Primary 50

Source:

- `experiments/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/summary.json`

Use as supporting evidence only. The headline should stay on the selected 100-case paper-grade cohort and repeated-work follow-up.

## Required Paper Artifacts

Create these files before drafting full prose:

1. `paper-data-ledger.md`
   - One row per result.
   - Source file.
   - Run label.
   - Metric.
   - Claim supported.
   - Claim explicitly not supported.

2. `paper-claims-ledger.md`
   - Main claim.
   - Mechanism claims.
   - Code Mode claims.
   - Runtime baseline claims.
   - Limitations.
   - Reviewer-risk notes.

3. `paper-results-tables.md`
   - Main selected-cohort table.
   - Negative controls table.
   - Code Mode ablation table.
   - Repeated-work runtime table.
   - Failure taxonomy table.

4. `paper-outline.md`
   - Abstract.
   - Introduction.
   - Background and related work.
   - Method.
   - Experimental design.
   - Results.
   - Limitations.
   - Reproducibility.
   - Conclusion.

5. `paper-related-work.md`
   - KV/session reuse.
   - Stateful inference.
   - Prompt/context compaction.
   - Tool-using agents.
   - Local inference systems.
   - BFCL/tool-call evaluation.

6. `paper-reproducibility-checklist.md`
   - Hardware.
   - Model.
   - Quantization/profile.
   - Runtime.
   - Scripts.
   - Prompts/artifacts.
   - Randomness/sampling.
   - Known non-identical prompt lanes.

## Data Organization Work

### Phase 1: Ledger

Create `paper-data-ledger.md` and freeze the following:

- selected cohort summary
- repeated-work speed summary
- natural Codex compaction audit
- BFCL primary 50 supporting result
- earlier handmade/mechanism runs as background only

Every row must answer:

- What did we run?
- Where is the source?
- What metric did it produce?
- What claim does it support?
- What claim would be overreach?

### Phase 2: Tables

Turn the ledgers into paper-ready tables:

- Table 1: selected-cohort controls
- Table 2: Code Mode vs direct visible vs compact visible evidence
- Table 3: repeated-work runtime comparison
- Table 4: natural Codex failure breakdown
- Table 5: claim-to-evidence mapping

### Phase 3: Codex Compaction Summary Audit

Inspect the `89` compaction events and classify:

- first task index affected
- summary length if available
- whether prior task outputs appear in the summary
- whether failed tasks occur after summary corruption
- whether summaries introduce bad argument strings, duplicates, or stale task facts

Deliverable:

`codex-compaction-summary-audit.md`

### Phase 4: Related Work Refresh

Use online search and paper harvest notes to refresh:

- stateful inference / session KV reuse
- KV cache sharing/reuse systems
- local/on-device LLM inference
- prompt compaction / context compression
- tool-use benchmark baselines
- BFCL and function-calling evaluation

Deliverable:

`paper-related-work.md`

Rule: every cited paper must be manually checked for title/authors/claim. No hallucinated citations.

### Phase 5: Draft

Write the paper from evidence, not vibes.

Suggested draft order:

1. Results tables.
2. Method.
3. Experimental design.
4. Limitations.
5. Related work.
6. Introduction.
7. Abstract last.

## Tooling And Skills To Use

### Repo Tools

- `rg`: find result references, run labels, and stale claims.
- `python3 -m json.tool`: validate JSON summaries.
- small Python scripts: extract tables from JSON/JSONL records.
- `git diff`, `git status`, `git log`: keep paper prep auditable.

### Existing Repo Scripts

Use the benchmark scripts under:

- `research/01-ssd-native-inference-current/benchmarks/`

Key script families:

- selected-cohort control packet generation
- model-loop record analysis
- repeated-work controller/finalizer/watchdog
- BFCL materialization summaries

Do not hand-transcribe raw metrics if a summary JSON can be parsed.

### OpenClaw/Codex Skills

Useful skills:

- `data-analytics:build-report`: turn validated metrics into a polished analytical report or dashboard if needed.
- `data-analytics:visualize-data`: create clean charts for pass rate, wall time, and visible-token burden.
- `github:github` / `github:yeet`: publish branches, PRs, or release-ready repo changes.
- `openai-docs`: only if the paper references OpenAI/Codex product behavior and needs official doc checks.
- `substack-human-voice`: not for the paper, but useful later for writing a public layperson announcement.
- `knowledge-os`: useful if saving a durable Second Brain research note outside the repo.

Online tools:

- official conference websites for submission rules and dates
- arXiv submission docs for source package readiness
- arXiv/Semantic Scholar/OpenReview for related-work verification

### Data Hygiene Rules

- Keep raw prompt-bearing artifacts ignored unless explicitly approved.
- Keep paper-facing summaries and ledgers committed.
- Do not expose private machine paths in the public paper except as reproducibility notes sanitized for publication.
- Separate Mac repo paths from DushyantPC execution paths.
- Label every non-identical-prompt comparison as a systems/runtime comparison.

## Paper Skeleton

### Abstract

One paragraph:

- local agents repeat stable context
- KV capsules reuse hidden prefix state
- Code Mode provides compact tool-use interface
- restored KV matched native append under controls
- repeated-work comparison against Codex/Ollama text compaction
- limitations

### Introduction

- local tool agents are context-heavy
- text compaction is lossy and changes the representation
- hidden-state reuse is appealing but risky
- our contribution is a quality-gated runtime and evaluation protocol

### Method

- stable prefix
- capsule save/restore
- task tail
- Code Mode contract
- controls and gates

### Experiments

1. Selected 100-case BFCL-derived cohort.
2. Controls and negative controls.
3. Code Mode ablation.
4. Repeated-work practical runtime baseline.

### Results

Use the paper-ready tables. Keep claims strict.

### Limitations

- selected cohort, not entire BFCL
- Gemma 4 12B local model
- implementation-specific timing
- Codex baseline not prompt-identical
- token telemetry is route-reported cumulative burden
- raw session compaction logs need careful handling

### Reproducibility

- repo commit
- scripts
- run labels
- model profile
- hardware
- output summaries
- artifact policy

## First Execution Checklist

1. Create `paper-data-ledger.md`.
2. Create `paper-claims-ledger.md`.
3. Create `paper-results-tables.md`.
4. Audit Codex compaction summaries.
5. Refresh related work with verified citations.
6. Update defense memo with BFCL evidence.
7. Draft `paper-outline.md`.
8. Review for overclaims.
9. Generate LaTeX skeleton.
10. Prepare arXiv-safe source package.

## Immediate Next Action

Start with `paper-data-ledger.md`.

Reason: the paper can only be as strong as its evidence ledger. Once the ledger is clean, the draft becomes much easier and safer.
