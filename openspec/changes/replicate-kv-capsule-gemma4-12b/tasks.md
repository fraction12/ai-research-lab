## 1. Change Setup

- [x] 1.1 Create proposal, design, tasks, and spec delta for `replicate-kv-capsule-gemma4-12b`.
- [x] 1.2 Validate `openspec validate replicate-kv-capsule-gemma4-12b --type change --strict`.

## 2. Harness Prep Boundary

- [x] 2.1 Inspect whether a committed durable harness/profile layer exists outside ignored raw runners.
- [x] 2.2 If durable harness exists, add a scoped explicit Gemma 4 12B profile without changing GPT-OSS defaults.
- [x] 2.3 If only ignored raw runners exist, document the needed patch shape instead of committing ignored prompt-bearing runner code.
- [x] 2.4 Define raw/cache path expectations for Gemma replication artifacts.
- [x] 2.5 Incorporate DushyantPC Gemma runtime facts: Ollama blob path, b9512 runtime, `llama.dll` name, sequence exports, GPU health, smoke caveat, and cleanup status.

## 3. Local Validation

- [x] 3.1 Run syntax/help checks for any committed harness/profile files changed. No committed harness/profile file was changed; executable raw runner changes remain ignored and under orchestration control.
- [x] 3.2 Run stale-path/profile checks to confirm GPT-OSS and Gemma selection are explicit.
- [x] 3.3 Run leak/control-byte scans for committed docs/artifacts.
- [x] 3.4 Re-run OpenSpec validations after DushyantPC runtime facts are added.

## 4. Execution Handoff

- [x] 4.1 Provide orchestration with the exact prepared profile/patch shape and smoke ladder.
- [x] 4.2 Do not SSH to DushyantPC or launch model-bearing commands unless orchestration explicitly hands execution back.
