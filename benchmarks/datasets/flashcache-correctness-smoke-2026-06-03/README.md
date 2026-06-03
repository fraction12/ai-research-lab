# Flashcache Correctness Smoke - 2026-06-03

## Purpose

Record the first GPT-OSS 20B full-prompt versus session-tail correctness smoke run across the selected Hugging Face eval families.

This is a quality-pipeline smoke, not a passing quality benchmark. The goal was to prove that the runner can generate paired responses and score them after the earlier session-tail latency result.

## Setup

- Machine: DushyantPC
- Model: `gpt-oss-20b-mxfp4.gguf`
- llama.cpp server: `llama-b9482-vulkan`
- Context: `32768`
- Predict: `96`
- Temperature: `0`
- Cases:
  - `ifeval-1001`
  - `graphwalks-0`
  - `mrcr-0`

The sampled case prompts are not stored in this recorded dataset. The raw outputs preserve model responses, timing metadata, and scores.

## Artifacts

- `raw/mixed-quality-smoke-3-gpt-oss-20b-responses.jsonl`: paired full/session-tail response records.
- `raw/mixed-quality-smoke-3-gpt-oss-20b-scores.json`: scorer output.
- `raw/mixed-quality-smoke-3-gpt-oss-20b-json-answer-responses.jsonl`: paired response records using the constrained JSON answer protocol.
- `raw/mixed-quality-smoke-3-gpt-oss-20b-json-answer-scores.json`: scorer output for the constrained JSON answer protocol.
- `summary.json`: compact case-level scores and prompt timing.

## Raw Completion Result

| Case | Dataset | Full Score | Session-Tail Score | Delta |
|---|---:|---:|---:|---:|
| `ifeval-1001` | IFEval | 0.000 | 0.000 | 0.000 |
| `graphwalks-0` | GraphWalks | 0.071 | 0.000 | -0.071 |
| `mrcr-0` | MRCR | 0.022 | 0.016 | -0.005 |

Prompt processing still showed the expected speed signal:

| Case | Full Prompt ms | Session-Tail Prompt ms |
|---|---:|---:|
| `ifeval-1001` | 1044.942 | 350.665 |
| `graphwalks-0` | 1409.950 | 381.516 |
| `mrcr-0` | 4617.299 | 222.602 |

## JSON Answer Result

The JSON answer protocol was added after checking llama.cpp's current server guidance. It keeps the raw `/completion` slot path but constrains output to a JSON object with an `answer` field, then scores the extracted answer.

| Case | Dataset | Full Score | Session-Tail Score | Delta |
|---|---:|---:|---:|---:|
| `ifeval-1001` | IFEval | 0.000 | 1.000 | 1.000 |
| `graphwalks-0` | GraphWalks | 0.333 | 0.000 | -0.333 |
| `mrcr-0` | MRCR | 0.002 | 0.000 | -0.002 |

Prompt processing still favored session-tail:

| Case | Full Prompt ms | Session-Tail Prompt ms |
|---|---:|---:|
| `ifeval-1001` | 703.929 | 359.571 |
| `graphwalks-0` | 1499.832 | 419.818 |
| `mrcr-0` | 4712.410 | 240.252 |

## Interpretation

The response pipeline works end to end: it generated paired responses, produced score JSON, and copied results back from the PC.

The raw run showed that unconstrained `/completion` emits reasoning or incomplete text, so it is not a fair quality harness. The JSON answer run improved answer hygiene, but still does not prove session-tail quality parity. Full-prompt baseline quality is also weak on this tiny smoke, and session-tail failed GraphWalks because the model produced truncated malformed JSON.

The next benchmark should use the JSON answer protocol, raise output budget for GraphWalks/MRCR, and sample cases where the full-prompt baseline passes before evaluating parity.
