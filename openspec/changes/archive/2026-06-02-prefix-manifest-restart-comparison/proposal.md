## Why

The benchmark has shown that aligned stable prefixes can become cheaper while Ollama stays warm, but that does not prove the benefit survives model/session restarts. The next experiment must measure whether the apparent reuse disappears when Ollama is stopped between changed-tail prompts.

## What Changes

- Add a prefix manifest that records reusable block hashes, prompt hashes, model/config metadata, and scenario tail hashes.
- Add a restart comparison strategy that runs aligned full prompts in a warm sequence and a restarted-before-each-call sequence.
- Report the persistence gap: restarted prompt evaluation cost minus warm prompt evaluation cost.
- Document how to interpret this as a target for future persistent SSD-backed prefix/KV cache work.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ollama-workflow-benchmark`: add prefix manifest generation and cold/warm/restarted comparison support.

## Impact

- Updates `benchmarks/ollama_workflow_benchmark.py`.
- Adds optional local prefix manifest JSON output under `benchmarks/prefix-manifests/`.
- Updates benchmark documentation and result notes.
- Does not implement SSD-backed KV storage yet.
