## Why

The first workflow benchmark used a synthetic fixture. The user provided a sanitized real DeepClean campaign prompt from LightningITB, backed by archived OpenSpec design and testing artifacts, which gives the benchmark a more realistic repeated-agent workload.

## What Changes

- Add a LightningITB DeepClean campaign workflow fixture.
- Record fixture provenance so future readers can trace why the prompt is shaped this way.
- Run and document the benchmark result for the real campaign fixture.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ollama-workflow-benchmark`: add provenance expectations for real workflow fixtures used by the benchmark.

## Impact

- Adds one benchmark fixture under `benchmarks/fixtures/`.
- Updates benchmark documentation and result notes.
- Does not change the benchmark CLI behavior or add dependencies.
