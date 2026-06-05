## 1. Change Setup

- [x] 1.1 Create proposal, design, tasks, and spec delta for `replicate-kv-capsule-gemma4-12b`.
- [x] 1.2 Validate `openspec validate replicate-kv-capsule-gemma4-12b --type change --strict`.

## 2. Harness Prep Boundary

- [x] 2.1 Inspect whether a committed durable harness/profile layer exists outside ignored raw runners.
- [x] 2.2 Add a scoped committed profile resolver with `gpt-oss-20b` and `gemma4-12b` profiles without changing GPT-OSS defaults.
- [x] 2.3 Document that orchestration owns the runtime-only ignored raw-runner patch needed to consume `--llama-dll` / profile-resolved `llama.dll`.
- [x] 2.4 Define raw/cache path expectations for Gemma replication artifacts.
- [x] 2.5 Incorporate DushyantPC Gemma runtime facts: Ollama blob path, b9512 runtime, `llama.dll` name, sequence exports, GPU health, smoke caveat, and cleanup status.
- [x] 2.6 Add a non-inference profile CLI that emits JSON reports, runner arguments, path checks, and a Gemma `llama-completion` smoke command.
- [x] 2.7 Include `--reasoning off` in the Gemma CLI smoke command when supported, while keeping C API evidence gated on empirical Family 1/2 smokes.

## 3. Local Validation

- [x] 3.1 Run syntax/help checks for the committed profile resolver and unit tests.
- [x] 3.2 Run stale-path/profile checks to confirm GPT-OSS and Gemma selection are explicit.
- [x] 3.3 Run leak/control-byte scans for committed docs/artifacts.
- [x] 3.4 Re-run OpenSpec validations after profile resolver implementation and DushyantPC runtime facts are added.

## 4. Execution Handoff

- [x] 4.1 Provide orchestration with the exact prepared profile/patch shape and smoke ladder.
- [x] 4.2 Do not SSH to DushyantPC or launch model-bearing commands unless orchestration explicitly hands execution back.
- [x] 4.3 Record that orchestration owns ignored raw-runner patching and DushyantPC smoke execution for this step.
