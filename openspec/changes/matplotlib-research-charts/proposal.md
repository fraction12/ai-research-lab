## Why

The current benchmark graphs are useful, but they are hand-authored SVGs. For research-quality reporting, figures should be generated from data with a standard plotting tool, export vector formats, and be reproducible from raw benchmark JSON.

## What Changes

- Replace the hand-written SVG chart generator with a Matplotlib-based pipeline.
- Generate the existing benchmark chart set as publication-oriented SVG and PDF assets.
- Keep PNG preview output for browser/README use.
- Preserve `chart-data.json` as the compact computed-data artifact.
- Generate a single gains/projection figure that distinguishes measured values, trend projection, and future target.
- Document the Matplotlib dependency and regeneration command.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `benchmark-result-summary`: add reproducible research-chart generation from benchmark result JSON files.

## Impact

- `benchmarks/plot_benchmark_graphs.py`: switch to Matplotlib and generate SVG/PDF/PNG outputs.
- `requirements-dev.txt`: add Matplotlib as a dev dependency for chart generation.
- `docs/benchmark-graphs.md` and `docs/benchmark-graphs.html`: continue referencing regenerated chart assets.
- `docs/assets/benchmark-graphs/`: regenerated figure outputs.
