## Why

StreamingLLM's attention-sink result changes how this repo should think about KV/cache eviction: the first tokens can be stabilizing anchors, not merely old context. The next prototype should therefore classify reusable prompt blocks into attention-sink candidates, stable prefix blocks, and volatile tails before attempting real KV persistence.

## What Changes

- Add StreamingLLM / Attention Sinks to the research references and technical map.
- Update the prototype plan so Phase 1 prefix storage records attention-sink candidates and rolling-tail boundaries.
- Add a metadata-only prefix block store CLI that writes content-addressed block records and a manifest from existing benchmark fixtures.
- Ignore generated prefix block store artifacts.

## Capabilities

### New Capabilities

- `prefix-block-store`: Build a content-addressed metadata store for reusable prompt blocks, attention-sink candidates, and scenario tails.

### Modified Capabilities

None.

## Impact

- Adds `benchmarks/prefix_block_store.py`.
- Updates `docs/references.md`, `docs/technical-map.md`, `docs/prototype-plan.md`, `docs/decision-log.md`, and `GLOSSARY.md`.
- Adds generated artifact ignore rules under `benchmarks/prefix-store/`.
- Does not store real KV tensors or require backend runtime changes.
