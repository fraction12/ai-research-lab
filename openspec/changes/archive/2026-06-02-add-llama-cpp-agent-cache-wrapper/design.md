## Context

The repo now has three important facts:

- Ollama benchmarks showed a cross-session persistence gap for changed-tail agent prompts.
- The prefix block store can describe stable prefix, attention-sink, rolling-tail, and volatile-tail prompt roles.
- The llama.cpp feasibility benchmark showed that `llama-server` slot save/restore can persist reusable prefix state across fresh local server processes.

The product opportunity is a local-agent cache wrapper: tools should call one OpenAI-style local endpoint while the wrapper handles cache keys, slot files, restore decisions, and telemetry. llama.cpp already exposes OpenAI-compatible routes and native slot save/restore endpoints, so the first build should wrap those mechanisms instead of reimplementing transformer internals.

Primary user: a local agent operator running repeated repo/workflow prompts on a personal machine.

Primary job: make repeated local-agent runs faster and more explainable without requiring the user to manually manage prompt cache files.

## Goals / Non-Goals

**Goals:**

- Expose a local `/v1/chat/completions` endpoint compatible with the common OpenAI chat request shape for non-streaming text responses.
- Support optional cache metadata so agents can identify reusable prefix blocks and volatile tail content.
- Derive exact-match cache keys from model identity, llama.cpp settings, stable prefix bytes, and prompt block hashes.
- Manage llama.cpp server startup, health checks, slot save, slot restore, and fallback direct completion.
- Persist machine-readable cache manifests alongside llama.cpp slot cache files.
- Return cache telemetry in response headers and a debug JSON field when requested.
- Provide a smoke benchmark that compares direct llama.cpp full-prompt calls against wrapper cached calls for the LightningITB fixture.

**Non-Goals:**

- Full OpenAI API compatibility.
- Streaming responses in the first implementation.
- Arbitrary partial KV reuse inside a changed prompt.
- Editing llama.cpp internals.
- Multi-user production auth, tenancy, or network exposure.
- Caching volatile prompt tails by default.

## Decisions

### Build a thin Python wrapper first

Use a small Python package for the service, cache manifest logic, llama.cpp client, and CLI. The existing benchmark code is already Python standard-library based, and a thin wrapper keeps the first prototype easy to inspect and test.

Alternative considered: build a Rust or Go service. That may be better later for daemon ergonomics, but it adds compilation and packaging friction before the cache policy is proven.

### Wrap llama.cpp instead of replacing it

The wrapper SHALL call llama.cpp `/completion` and slot save/restore endpoints for cache operations. It may expose `/v1/chat/completions` to callers, but internally it can use llama.cpp's lower-level prompt endpoint so slot ids and timing behavior remain explicit.

Alternative considered: proxy llama.cpp's existing `/v1/chat/completions` endpoint directly. That is simpler, but it hides the prompt string and cache split unless the wrapper controls prompt assembly.

### Use cache-aware request metadata as an opt-in

Standard chat requests SHALL still run without cache metadata. Cache acceleration SHALL require an optional wrapper-specific object, tentatively named `ssd_cache`, that includes stable prefix messages or block references, cache namespace, and debug preference.

Alternative considered: infer stable prefix automatically from all chat messages. This is attractive for ease of use but risky for correctness; volatile state could be persisted accidentally.

### Cache exact stable prefixes only

Cache keys SHALL include model path or model id, llama.cpp version/settings, context size, slot cache policy version, stable prefix bytes, and block hashes where available. If any compatibility input changes, the wrapper SHALL miss the cache and rebuild it.

Alternative considered: fuzzy or partial prefix matching. That is a later optimization; exact matching is easier to validate and safer for the first layer.

### Keep volatile tails out of persisted manifests by default

The manifest SHALL record hashes and byte counts for volatile tail material, but it SHALL NOT persist raw volatile tail text unless a debug flag is enabled. Stable prefix text may be persisted only in local ignored artifacts or represented by hashes when possible.

Alternative considered: persist every prompt for debuggability. That is convenient but bad hygiene for repo context, user messages, and secrets.

### Return explicit telemetry

The wrapper SHALL return cache state in headers such as `X-Flashcache-Cache` and `X-Flashcache-Key`, plus optional debug JSON with prompt timing, restored tokens, slot bytes, and fallback reason.

Alternative considered: only log telemetry to files. That makes benchmark analysis harder and prevents client-side cache assertions.

## Risks / Trade-offs

- **llama.cpp server APIs may change.** -> Keep endpoint paths isolated in a client module and record server version in manifests.
- **OpenAI compatibility can sprawl.** -> Start with a documented non-streaming subset and reject unsupported fields clearly.
- **Cache restore can produce wrong behavior if compatibility is under-keyed.** -> Over-key first; include model, version, settings, and exact bytes.
- **Prompt assembly can diverge from client expectations.** -> Store assembled prompt hash and expose debug prompt artifact only when explicitly enabled.
- **Slot files may grow quickly.** -> Add size caps and least-recently-used eviction in the first implementation, even if simple.
- **Local network exposure could leak prompts.** -> Bind to `127.0.0.1` by default and avoid auth claims in this change.

## Migration Plan

1. Add the wrapper as an opt-in local service; existing benchmarks continue to work unchanged.
2. Add ignored local cache directories for wrapper manifests, slot files, logs, and smoke results.
3. Run the wrapper smoke benchmark against the existing LightningITB fixture.
4. Document how to run the service and how to inspect telemetry.
5. Keep direct llama.cpp benchmark results as the comparison baseline.

Rollback is deleting the wrapper cache artifacts and using the existing direct llama.cpp benchmark path.

## Open Questions

- Should the public name stay `flashcache`, or should the repo use a more literal `ssd-native-cache` name?
- Should cache-aware metadata be carried in a request body field, a header, or both?
- Should the first implementation expose a true daemon mode, or should it start `llama-server` per request for clearer measurement?
