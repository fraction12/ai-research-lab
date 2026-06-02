## Why

The llama.cpp feasibility benchmark proved that local prompt/KV state can be saved to disk and restored across fresh server processes, reducing changed-tail prompt evaluation for a real agent workflow fixture. The next opportunity is to turn that raw backend mechanism into an agent-aware local API that regular tools can call without manually managing slot files.

## What Changes

- Add a local wrapper service for llama.cpp that exposes an OpenAI-style chat completions endpoint.
- Accept agent cache metadata that identifies stable prefix blocks, attention-sink blocks, rolling tail, and volatile tail.
- Derive deterministic cache keys from model identity, server settings, tokenizer-relevant metadata, and exact stable prefix bytes.
- On cache miss, prime llama.cpp with the reusable prefix, save the slot cache, and persist a manifest.
- On cache hit, start or reuse llama.cpp, restore the matching slot cache, and send the full changed-tail prompt.
- Return response metadata that reports cache hit/miss state, restored token count, prompt timing, save/restore timing, and slot cache file bytes.
- Add a CLI smoke benchmark that compares wrapper cached runs against direct llama.cpp full-prompt baselines.

## Capabilities

### New Capabilities

- `llama-cpp-agent-cache-wrapper`: Provides an OpenAI-style local API wrapper around llama.cpp slot save/restore with agent-aware cache manifests, cache policy, and telemetry.

### Modified Capabilities

None.

## Impact

- Adds wrapper service code under a new local package or script path.
- Adds tests for cache-key derivation, manifest persistence, hit/miss behavior, and telemetry shape.
- Adds generated artifact ignore rules for wrapper cache manifests, slot cache files, logs, and smoke benchmark outputs.
- Depends on a local `llama-server` binary and a GGUF model path, both configurable.
- Does not replace llama.cpp internals, implement arbitrary partial KV reuse, or claim compatibility with every OpenAI API feature.
