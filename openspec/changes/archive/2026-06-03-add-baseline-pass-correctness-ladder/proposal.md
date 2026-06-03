## Why

The correctness smoke still cannot prove session-tail quality parity because many full-prompt baselines fail. We need a workflow that first finds cases the model can answer correctly with the normal full prompt, then tests whether session-tail preserves those passing answers while saving prompt time.

## What Changes

- Add a baseline-pass correctness ladder command.
- Run full-prompt responses first for a candidate case file.
- Score the full responses and select only full-passing cases.
- Run session-tail only on the selected cases.
- Combine selected full responses with session-tail responses and write parity scores plus a compact report.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `flashcache-correctness-eval-suite`: Add baseline-pass workflow for fair full-prompt versus session-tail comparison.

## Impact

- Affects the correctness runner, tests, and benchmark docs.
- Uses existing ignored correctness input/output/cache directories.
- Does not change the Flashcache HTTP wrapper or latency benchmark schema.
