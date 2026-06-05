# Replicate KV Capsule Gates With Gemma 4 12B

## Why

The GPT-OSS native sequence-state route now has narrow positives for Family 1 and Family 2, including the 30-case Family 2 semantic pass with deterministic hash-parity warning. The next useful prep step is to make the harness ready to rerun the same controlled gates with Gemma 4 12B without changing benchmark semantics or breaking the GPT-OSS path.

## What Changes

- Define a Gemma 4 12B replication plan for the same tail-only sequence-state contract.
- Require an explicit model/profile/config selection so Gemma runs cannot accidentally reuse GPT-OSS assumptions.
- Preserve the exact controls: full visible, fresh tail, live append, restored capsule.
- Keep DushyantPC execution out of this repo-prep lane until orchestration explicitly hands it back.

## Non-Goals

- No GraphWalks, Family 3, broad retrieval, noiseless evidence, or agent-context expansion.
- No model download, PC SSH, or model-bearing execution in this repo-prep task.
- No claim that Gemma will behave like GPT-OSS before the smoke ladder runs.
