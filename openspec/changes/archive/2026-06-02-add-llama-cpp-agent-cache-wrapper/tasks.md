## 1. Package Structure

- [x] 1.1 Create the wrapper package/module layout for service, cache, llama.cpp client, and CLI entry points.
- [x] 1.2 Add ignored local artifact paths for wrapper manifests, slot caches, logs, prompt debug files, and smoke benchmark results.

## 2. Cache Model

- [x] 2.1 Implement request parsing for optional `ssd_cache` metadata.
- [x] 2.2 Implement deterministic cache-key derivation from namespace, model identity, llama.cpp version/settings, stable prefix bytes, block hashes, and policy version.
- [x] 2.3 Implement cache manifest read/write with stable prefix hashes, volatile tail hashes, saved/restored token counts, timings, slot file bytes, and fallback reason fields.
- [x] 2.4 Implement size-cap and least-recently-used cleanup for local cache artifacts.

## 3. llama.cpp Integration

- [x] 3.1 Implement llama.cpp HTTP client calls for health, completion, slot save, and slot restore.
- [x] 3.2 Implement managed `llama-server` startup, health wait, shutdown, and existing-server mode.
- [x] 3.3 Implement cache miss flow: prime reusable prefix, save slot cache, write manifest, then complete changed-tail request.
- [x] 3.4 Implement cache hit flow: restore matching slot cache, complete changed-tail request, and record restore telemetry.
- [x] 3.5 Implement fallback behavior when manifest lookup, slot file validation, server health, or restore fails.

## 4. HTTP API

- [x] 4.1 Implement `POST /v1/chat/completions` for non-streaming OpenAI-style requests.
- [x] 4.2 Reject unsupported streaming requests with a clear structured error.
- [x] 4.3 Return cache telemetry headers and optional debug JSON in completion responses.
- [x] 4.4 Avoid persisting raw volatile tail text unless explicit debug mode is enabled.

## 5. Smoke Benchmark and Docs

- [x] 5.1 Add a wrapper smoke benchmark for the LightningITB fixture comparing direct llama.cpp full-prompt calls with wrapper cache-aware calls.
- [x] 5.2 Persist wrapper benchmark results as ignored JSON artifacts.
- [x] 5.3 Document how to run the wrapper service, send a cache-aware request, and interpret cache telemetry.
- [x] 5.4 Update benchmark results with the first wrapper smoke benchmark interpretation.

## 6. Tests and Validation

- [x] 6.1 Add unit tests for cache-key derivation and manifest persistence.
- [x] 6.2 Add unit tests for request parsing, unsupported streaming rejection, and telemetry shape.
- [x] 6.3 Add integration or smoke tests for cache miss, cache hit, and restore fallback paths using the local small GGUF model when available.
- [x] 6.4 Run Python compile checks.
- [x] 6.5 Run wrapper tests and smoke benchmark where local prerequisites are available.
- [x] 6.6 Validate the OpenSpec change.
- [x] 6.7 Validate all OpenSpec specs after archive.
