## Context

The Flashcache benchmark now has a fast `session-tail` path. The unresolved product risk is correctness: a local agent is only useful if tail-only continuations preserve the same instruction-following, long-context recall, and reasoning behavior as the full prompt.

The first correctness suite should use free datasets with scoreable references:

- `google/IFEval` for instruction-following checks.
- `openai/mrcr` for long multi-turn retrieval/co-reference.
- `openai/graphwalks` for exact long-context graph reasoning.

## Goals / Non-Goals

**Goals:**
- Add a small benchmark utility that can list supported datasets, materialize sampled eval cases, and score output pairs.
- Represent every case as `stable_prefix`, `tail_prompt`, and `full_prompt` so the same case can drive full-prompt and session-tail model runs.
- Keep remote dataset downloads and generated eval outputs local and ignored.
- Make deterministic scorers testable without downloading Hugging Face data.

**Non-Goals:**
- Do not run the large PC model as part of this change.
- Do not implement a full agent runner or public Flashcache session API.
- Do not claim complete official IFEval parity; unsupported instruction ids must be explicit.

## Decisions

1. Add a standalone benchmark module instead of extending the latency runner.

   The latency runner is already responsible for llama.cpp server lifecycle and cache telemetry. Correctness scoring has a different data model: cases, responses, references, and per-mode quality scores. A separate module keeps the latency path stable and lets us join quality and speed evidence later through result JSON.

2. Use dataset-specific case builders.

   IFEval, MRCR, and GraphWalks expose different row shapes. A small adapter per dataset is clearer than a generic prompt splitter. IFEval uses a reusable instruction-following prefix plus the row prompt as the tail. MRCR converts chat messages into prefix messages plus the final request tail. GraphWalks splits the graph/instructions from the final `Operation:` section when that marker is present.

3. Use deterministic first-pass scorers.

   MRCR uses sequence similarity after removing the random prefix, matching the dataset card's reference scorer. GraphWalks uses set precision/recall/F1. IFEval starts with deterministic checks for supported instruction ids and reports unsupported ids, because silently scoring every IFEval item as if fully supported would make the quality gate untrustworthy.

4. Keep Hugging Face loading optional at import time.

   Unit tests and local development should not require network access or a populated Hugging Face cache. The CLI imports `datasets.load_dataset` only when sampling remote rows and raises a clear dependency error if the package is missing.

## Risks / Trade-offs

- [Risk] IFEval coverage starts partial. → Mitigation: report unsupported instruction ids and aggregate only numeric supported checks.
- [Risk] Prompt splitting can change semantics. → Mitigation: store both prefix/tail and derived full prompt in every case for inspection and reproducibility.
- [Risk] Downloaded benchmark rows could bloat the repo. → Mitigation: default output directories are ignored and docs call out that generated rows are local artifacts.
- [Risk] Correctness and latency results are separate files at first. → Mitigation: use stable `case_id` and `mode` fields so later benchmark steps can join them.
