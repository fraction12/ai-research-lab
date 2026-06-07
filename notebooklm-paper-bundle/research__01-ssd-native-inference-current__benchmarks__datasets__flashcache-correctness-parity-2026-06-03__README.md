# Flashcache Correctness Parity - 2026-06-03

This records a DushyantPC GPT-OSS 20B correctness ladder using the JSON answer protocol with dataset-specific answer hints.

## Setup

- Model: `gpt-oss-20b-mxfp4.gguf`
- Runtime: llama.cpp server on DushyantPC
- Candidate builder: `ifeval:100,graphwalks:20`, `--profile easy`, `--max-prompt-chars 5000`
- Candidate cases built: 107
- Prompt-bearing candidate and selected-case JSONL files are intentionally not recorded.

## Result

- Full-prompt gate selected 42/107 cases.
- Full selected set by dataset: 36 IFEval, 6 GraphWalks.
- Session-tail passed 31/42 selected cases overall.
- IFEval session-tail pass rate: 31/36.
- GraphWalks session-tail pass rate: 0/6.
- Mean selected-case prompt-time saving: 533.355 ms.

## Interpretation

This is enough data to judge quality for the current protocol. Session-tail is promising for simple instruction-following cases, but it is not correctness-safe yet for reasoning tasks that depend heavily on stable-prefix context. The next step should focus on why restored-prefix tail-only decoding loses GraphWalks semantics despite full-prompt passing the same cases.

## Files

- `summary.json`: compact result summary and interpretation.
- `raw/*full-responses.jsonl`: full-prompt responses for all candidates.
- `raw/*full-scores.json`: full-prompt score gate.
- `raw/*session-tail-responses.jsonl`: resumed tail-only responses for selected cases.
- `raw/*parity-responses.jsonl`: selected full responses plus session-tail responses.
- `raw/*parity-scores.json`: full versus session-tail correctness comparison.
- `raw/*ladder-report.json`: reconstructed ladder report with prompt timing deltas.
