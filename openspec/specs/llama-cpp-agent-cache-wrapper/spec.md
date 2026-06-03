# llama-cpp-agent-cache-wrapper Specification

## Purpose
Provide an agent-aware local wrapper around llama.cpp slot save/restore so OpenAI-style chat clients can reuse stable prompt state while receiving explicit cache telemetry.
## Requirements
### Requirement: Expose local chat completions endpoint
The system SHALL provide a local HTTP endpoint for non-streaming OpenAI-style chat completion requests.

#### Scenario: Standard chat request
- **WHEN** a client sends `POST /v1/chat/completions` with `model`, `messages`, and non-streaming generation options
- **THEN** the wrapper sends an equivalent prompt to llama.cpp
- **AND** the wrapper returns a chat completion response with assistant text and usage or timing metadata where available

#### Scenario: Unsupported streaming request
- **WHEN** a client sends a chat completion request with `stream: true`
- **THEN** the wrapper rejects the request with a clear error that streaming is not supported in the first implementation

### Requirement: Accept cache-aware agent metadata
The system SHALL accept optional wrapper-specific cache metadata that identifies reusable and volatile prompt material.

#### Scenario: Cache metadata is present
- **WHEN** a chat completion request includes `ssd_cache` metadata with a namespace and stable prefix content or block references
- **THEN** the wrapper uses that metadata to build the reusable prefix and cache manifest
- **AND** the wrapper treats non-prefix messages as changed-tail prompt content

#### Scenario: Cache metadata is absent
- **WHEN** a chat completion request does not include cache metadata
- **THEN** the wrapper runs a direct llama.cpp completion without saving or restoring a slot cache
- **AND** the response telemetry records that cache mode was bypassed

### Requirement: Derive exact-match cache keys
The wrapper SHALL derive deterministic exact-match cache keys for reusable prefix slot caches.

#### Scenario: Build cache key
- **WHEN** the wrapper prepares a cache-aware request
- **THEN** the cache key includes cache namespace, model identity, llama.cpp server version, context size, relevant llama.cpp settings, stable prefix bytes or block hashes, and cache policy version
- **AND** the wrapper may reuse a previously observed server-version identity within the same wrapper instance

#### Scenario: Compatibility input changes
- **WHEN** any cache-key input differs from an existing manifest
- **THEN** the wrapper treats the request as a cache miss and does not restore the old slot cache

### Requirement: Persist cache manifest and slot cache
The wrapper SHALL persist local cache artifacts for reusable prefixes.

#### Scenario: Cache miss is primed
- **WHEN** a cache-aware request misses the prefix cache
- **THEN** the wrapper primes llama.cpp with the reusable prefix
- **AND** saves the llama.cpp slot cache to a local file
- **AND** writes a manifest that records cache key, model identity, prefix hashes, saved token count, slot file bytes, and save timing

#### Scenario: Generated artifacts are local
- **WHEN** the wrapper writes manifests, slot caches, logs, prompt debug files, or smoke benchmark results
- **THEN** those paths are covered by git ignore rules

### Requirement: Restore cached prefix for changed-tail requests
The wrapper SHALL restore matching prefix slot caches before running changed-tail prompts.

#### Scenario: Cache hit is restored
- **WHEN** a cache-aware request matches an existing manifest and slot cache file
- **THEN** the wrapper restores the llama.cpp slot before sending the full changed-tail prompt
- **AND** records restored token count, restore timing, and prompt processing timing

#### Scenario: Restore fails
- **WHEN** a matching manifest exists but slot restore fails
- **THEN** the wrapper falls back to direct completion or cache rebuild according to configured policy
- **AND** the response telemetry records the fallback reason

### Requirement: Protect volatile prompt content
The wrapper SHALL avoid persisting raw volatile prompt content by default.

#### Scenario: Volatile tail is processed
- **WHEN** a cache-aware request includes changed-tail messages or blocks
- **THEN** the wrapper records hashes, byte counts, and role labels for volatile tail content
- **AND** does not persist raw volatile text unless an explicit debug option is enabled

### Requirement: Emit cache telemetry
The wrapper SHALL expose cache behavior and timing telemetry to callers.

#### Scenario: Completion returns telemetry
- **WHEN** the wrapper returns a completion response
- **THEN** the response includes cache state, cache key, prompt processing timing, save or restore timing where applicable, and fallback reason where applicable
- **AND** the response telemetry includes wrapper-visible boundary timings for request parsing or prompt assembly, server-version lookup or reuse, cache lookup, server context enter and exit, prefix priming, slot save, slot restore, direct or tail completion, and total wrapper time where each phase is applicable

#### Scenario: Debug telemetry requested
- **WHEN** a request enables debug telemetry
- **THEN** the response body includes a machine-readable cache debug object in addition to normal response fields
- **AND** the debug object includes a `boundary_timings` object with phase durations in milliseconds where available

#### Scenario: Boundary phase is not observable
- **WHEN** a lower-level phase such as SSD read throughput, tensor serialization, or accelerator upload is not observable from the wrapper
- **THEN** the wrapper does not invent a value for that phase

### Requirement: Manage llama.cpp server lifecycle
The wrapper SHALL manage or connect to a local llama.cpp server safely.

#### Scenario: Managed server starts
- **WHEN** the wrapper is configured to manage llama.cpp
- **THEN** it starts `llama-server` with configured model path, host, port, context size, slot save path, and cache prompt options
- **AND** waits for health before serving cache-aware completions

#### Scenario: Existing server is used
- **WHEN** the wrapper is configured with an existing llama.cpp base URL
- **THEN** it verifies health and uses that server without starting a new process

### Requirement: Compare wrapper cache value
The system SHALL provide a smoke benchmark for the wrapper cache path.

#### Scenario: Run wrapper smoke benchmark
- **WHEN** the user runs the wrapper benchmark against a workflow fixture
- **THEN** the benchmark compares direct llama.cpp full-prompt calls with wrapper cache-aware calls
- **AND** writes a result JSON that reports cache hit rate, prompt timing, save/restore overhead, net delta, boundary timing telemetry where available, and selected server mode

#### Scenario: Run wrapper benchmark with persistent server mode
- **WHEN** the user runs the wrapper benchmark with persistent server mode
- **THEN** the benchmark keeps a llama.cpp server alive across direct full-prompt scenarios
- **AND** keeps a separate llama.cpp server alive across wrapper cache-aware scenarios
- **AND** records the selected server mode in result metadata

### Requirement: Emit wrapper benchmark progress
The Flashcache wrapper benchmark SHALL emit progress output before long-running direct and cache-aware model phases.

#### Scenario: Progress before direct scenario
- **WHEN** the wrapper benchmark is about to run a direct full-prompt scenario
- **THEN** it prints a progress line identifying the direct phase and scenario name

#### Scenario: Progress before cache-aware scenario
- **WHEN** the wrapper benchmark is about to run a cache-aware scenario through the wrapper
- **THEN** it prints a progress line identifying the cache-aware phase and scenario name
