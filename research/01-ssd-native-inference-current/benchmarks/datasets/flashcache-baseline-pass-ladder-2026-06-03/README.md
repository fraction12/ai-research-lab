# Flashcache Baseline-Pass Correctness Ladder - 2026-06-03

## Purpose

Record the first baseline-pass GPT-OSS 20B correctness ladder. This run first scored full-prompt outputs, selected only cases where full-prompt passed, then tested session-tail on that selected set.

This is the first result that can fairly ask whether session-tail preserved quality, because the comparison set only includes cases where the normal full prompt succeeded.

## Setup

- Machine: DushyantPC
- Model: `gpt-oss-20b-mxfp4.gguf`
- llama.cpp server: `llama-b9482-vulkan`
- Context: `32768`
- Predict: `192`
- Temperature: `0`
- Answer protocol: `json-answer`
- Candidate cases: 12
- Selection threshold: full score >= `1.0`

The candidate and selected case prompt JSONL files are not stored in this recorded dataset because they include sampled prompt text. The recorded raw artifacts preserve responses, scores, timings, and the ladder report.

## Artifacts

- `raw/baseline-pass-candidates-12-gpt-oss-20b-json-answer-full-responses.jsonl`
- `raw/baseline-pass-candidates-12-gpt-oss-20b-json-answer-full-scores.json`
- `raw/baseline-pass-candidates-12-gpt-oss-20b-json-answer-session-tail-responses.jsonl`
- `raw/baseline-pass-candidates-12-gpt-oss-20b-json-answer-parity-responses.jsonl`
- `raw/baseline-pass-candidates-12-gpt-oss-20b-json-answer-parity-scores.json`
- `raw/baseline-pass-candidates-12-gpt-oss-20b-json-answer-ladder-report.json`
- `summary.json`

## Result

Full-prompt baseline:

| Candidate Cases | Full Pass Rate | Full Mean Score |
|---:|---:|---:|
| 12 | 0.250 | 0.278 |

Selected full-passing cases:

| Case | Dataset | Full Prompt ms | Session-Tail Prompt ms | Prompt ms Saved | Score Delta |
|---|---|---:|---:|---:|---:|
| `ifeval-1147` | IFEval | 744.986 | 465.970 | 279.016 | 0.000 |
| `ifeval-1162` | IFEval | 700.717 | 218.131 | 482.586 | 0.000 |
| `ifeval-1580` | IFEval | 719.822 | 250.112 | 469.710 | 0.000 |

Parity set:

| Selected Cases | Full Pass Rate | Session-Tail Pass Rate | Full Mean Score | Session-Tail Mean Score |
|---:|---:|---:|---:|---:|
| 3 | 1.000 | 1.000 | 1.000 | 1.000 |

## Interpretation

This is the strongest positive quality signal so far, but it is narrow. On three IFEval cases where GPT-OSS 20B full-prompt mode passed, session-tail also passed with zero score delta while saving prompt processing time.

This does not prove broad quality parity. GraphWalks and MRCR did not enter the parity set because full-prompt baseline did not pass them. The next run should expand the candidate pool and improve long-context answer quality until at least some GraphWalks or MRCR cases pass the full baseline.
