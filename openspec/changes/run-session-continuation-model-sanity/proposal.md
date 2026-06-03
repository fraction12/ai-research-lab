## Why

The first session-continuation litmus showed that `gpt-oss-20b-mxfp4.gguf` fails tail-only same-slot and restored-slot continuation even on a tiny secret-token task. Before moving to lower-level KV/session repair, run one narrow alternate-model/format sanity check so the Track 02 paper trail does not overfit to a single model artifact or plain prompt format.

## What Changes

- Run the existing session-continuation litmus on the alternate local GGUF found on DushyantPC: `C:\Users\Dushyant\Documents\vault-mind\vault-mind-q5_k_m.gguf`.
- Add an explicit conversation-transcript prompt-format case set for the same litmus if the alternate model can load.
- Record exact model path, model bytes, backend, command lines, prompts, raw outputs, parsed answers, prompt hashes, timings, and failure classification.
- Keep Option 3 as the intended next research lane regardless of this sanity result: tail-only `/completion` is not the mechanism path we want to rely on.

## Capabilities

### New Capabilities

### Modified Capabilities

- `llama-cpp-agent-cache-wrapper`: Add requirements for a bounded alternate-model/format session-continuation sanity check before moving to lower-level continuation/KV repair work.

## Impact

- Affected code: no Track 01 harness code unless the alternate-format cases expose a small, necessary CLI limitation.
- Affected artifacts: new Track 02 experiment directory under `research/02-quality-gated-stateful-kv-reuse/experiments/session-continuation-model-sanity-2026-06-03/`.
- Affected raw outputs: ignored Track 01 benchmark result/cache paths under `benchmarks/session-continuation-litmus-results/` and `benchmarks/session-continuation-litmus-cache/`.
- No broad benchmarks and no GraphWalks reruns.
