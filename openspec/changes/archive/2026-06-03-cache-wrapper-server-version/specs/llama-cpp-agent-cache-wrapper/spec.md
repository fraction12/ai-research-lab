## MODIFIED Requirements

### Requirement: Derive exact-match cache keys
The wrapper SHALL derive deterministic exact-match cache keys for reusable prefix slot caches.

#### Scenario: Build cache key
- **WHEN** the wrapper prepares a cache-aware request
- **THEN** the cache key includes cache namespace, model identity, llama.cpp server version, context size, relevant llama.cpp settings, stable prefix bytes or block hashes, and cache policy version
- **AND** the wrapper may reuse a previously observed server-version identity within the same wrapper instance

### Requirement: Emit cache telemetry
The wrapper SHALL expose cache behavior and timing telemetry to callers.

#### Scenario: Completion returns telemetry
- **WHEN** the wrapper returns a completion response
- **THEN** the response includes cache state, cache key, prompt processing timing, save or restore timing where applicable, and fallback reason where applicable
- **AND** the response telemetry includes wrapper-visible boundary timings for request parsing or prompt assembly, server-version lookup or reuse, cache lookup, server context enter and exit, prefix priming, slot save, slot restore, direct or tail completion, and total wrapper time where each phase is applicable
