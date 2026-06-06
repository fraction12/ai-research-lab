# Gemma 4 KV Capsule Replication

## Result

Gemma 4 12B replicated the tail-only sequence-state KV capsule gates on DushyantPC.

- Family 1 smoke: full visible `3/3`, fresh tail `0/3`, live append `3/3`, restored capsule append `3/3`.
- Family 2 smoke: full visible `3/3`, fresh tail `0/3`, live append `3/3`, restored capsule append `3/3`.
- Family 2 primary: full visible `30/30`, fresh tail `0/30`, live append `30/30`, restored capsule append `30/30`.

The primary 30-case Family 2 run also produced deterministic live-vs-restored parity: response hash, normalized response hash, and generated-token hash matched for `30/30` paired cases.

## Interpretation

This is a go for the narrow KV capsule mechanism on Gemma 4 12B: persisted llama.cpp sequence-file state can be restored and appended with only the volatile tail while preserving semantic access to the hidden structured prefix. It directly answers the earlier worry that saved/restored state might move bytes without behaving like attention-visible prefix state for the next run.

This is not yet a broad quality claim. The tested tasks are synthetic codeword and structured key-value retrieval gates. The next research gate should test harder task families such as graph/relational reasoning and agent-like repo context, plus amortization on larger and repeated stable prefixes.

## Route

- Requested route: `auto`
- Effective route: `seq_file`
- Internal route: `seq-file`
- Backend: llama.cpp b9512 CUDA 13 runtime on DushyantPC
- DLL: `C:\Users\Dushyant\Tools\llama-b9512-cuda13\llama.dll`
- DLL SHA-256: `8A08D3221F375116E4C0AF6263E625A1CAC8552D3FADB38FC3279D9F30EE4EBC`
- Model blob: `C:\Users\Dushyant\.ollama\models\blobs\sha256-5cf8a1f2fc4268b3fd628743675910cf1d8137c4742d0be401c3e885f605023a`
- Model size: `7,381,382,048` bytes
- GPU: NVIDIA GeForce RTX 3060, 12 GB VRAM

## Scoring Calibration

Gemma 4 raw C API output includes channel/thinking markers. The runtime-only runner calibration therefore scores answer containment case-insensitively while preserving exact-match, exact-case containment, raw response hashes, normalized response hashes, and generated-token hashes as separate evidence fields.

In the primary Family 2 run, all four semantic controls used exact-case containment for all positive answers: full visible `30/30`, live append `30/30`, and restored capsule append `30/30`. Fresh tail remained `0/30`.

## Artifact Boundary

Raw prompt/response records and console logs are local ignored artifacts under:

`research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-gemma4-12b-replication-2026-06-04/raw/`

The distilled files in this experiment folder contain only summary statistics, commands, and artifact pointers.

## Go/No-Go

Go for the next controlled phase:

- run Gemma Family 3/graph-style gates;
- run a larger-prefix amortization variant that separates one-time capsule creation from repeated tail-only reuse;
- add a stricter channel-aware scorer if future tasks need final-answer-only semantics;
- compare against GPT-OSS results without blending model families.
