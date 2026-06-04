## Why

The restored-prefix full-resend probe showed correctness safety but no useful prompt-processing reduction. The next question is whether llama.cpp prefix reuse is working at all in this backend/API shape, or whether slot restore plus full resend is the wrong layer to expect acceleration.

## What Changes

- Add a focused llama.cpp prefix-reuse audit that sends direct `/completion` requests against `llama-server`.
- Compare exact repeat, same-server restore/full-resend, fresh-server restore/full-resend, and longer-prefix variants.
- Preserve command lines, prompts, hashes, raw responses, timing/token telemetry, slot save/restore telemetry, server logs, and a mechanism classification.
- Use only `gpt-oss-20b-mxfp4.gguf` on DushyantPC for model-backed runs.
- Keep GraphWalks and broad benchmarks out of scope until the audit proves useful prompt-work reduction.

## Capabilities

### New Capabilities

### Modified Capabilities

- `llama-cpp-prompt-cache-benchmark`: Add a lower-level prefix-reuse audit requirement for direct llama.cpp `/completion` controls.

## Impact

- Affected code: a small Track 01 benchmark/probe runner and focused tests.
- Affected artifacts: a new Track 02 experiment directory under `research/02-quality-gated-stateful-kv-reuse/experiments/llama-cpp-prefix-reuse-audit-2026-06-04/`.
- Affected raw outputs: ignored Track 01 benchmark result/cache paths for prompt-bearing JSON, logs, and slot files.
- Explicitly excluded: GraphWalks, broad correctness benchmarks, and any alternate or experimental fine-tuned model.
