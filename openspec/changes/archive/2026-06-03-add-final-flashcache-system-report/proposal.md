## Why

The repo now has enough benchmark evidence to explain the Flashcache direction clearly: SSD-backed/session-backed reuse can reduce local prompt work, but the last correctness run exposed quality drift. We need a final system report that turns the measurements into an honest architecture and product readout.

## What Changes

- Add a decision-oriented final report for the SSD-backed Flashcache approach.
- Summarize what the system is, what the benchmarks prove, what they do not prove, and what must improve before this becomes safe for regular local-agent users.
- Ground claims in recorded repo artifacts and avoid overstating novelty or quality.
- Link the report from the benchmark docs.

## Capabilities

### New Capabilities
- `flashcache-system-report`: Maintains a final report that synthesizes Flashcache system evidence, quality risks, and next-step architecture direction.

### Modified Capabilities
- None.

## Impact

- Adds documentation under `docs/`.
- Adds an OpenSpec capability for maintaining the report.
- Does not change runtime behavior, benchmark execution, or recorded dataset artifacts.
