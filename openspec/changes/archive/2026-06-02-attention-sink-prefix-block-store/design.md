## Context

The current benchmark proved a persistence gap: aligned prompts get cheaper while Ollama stays warm, but stopping the model before each changed-tail prompt removes much of that benefit. StreamingLLM adds a second design constraint: simple sliding-window cache eviction can fail if the initial attention-sink tokens are discarded.

The immediate next step is therefore a metadata store that labels block roles before any backend-specific KV implementation. This lets future MLX or llama.cpp work ask better questions: which blocks are attention anchors, which are stable workflow context, and which are rolling or volatile tail state?

## Goals / Non-Goals

**Goals:**

- Create content-addressed prompt block metadata from existing fixtures.
- Mark attention-sink candidates from the beginning of the common reusable prefix.
- Mark stable prefix, rolling-tail, and volatile-tail roles.
- Recommend memory/storage tier treatment per block role.
- Produce manifest JSON that future KV-cache code can reuse as cache-key scaffolding.

**Non-Goals:**

- Persist real KV tensors.
- Tokenize prompts or identify exact first-token KV positions.
- Implement SSD reads, prefetch, eviction, or LRU.
- Prove model quality under attention-sink eviction.

## Decisions

- **Use block-level attention-sink candidates.** The fixture does not tokenize prompts, so the first one or more reusable blocks are only candidates for later token-level sink handling.
- **Keep generated store artifacts ignored.** They are local run outputs and can be regenerated from fixtures.
- **Reuse benchmark fixture parsing.** The store builder imports the existing benchmark module to avoid divergent hashing and prompt assembly rules.
- **Store metadata, not raw prompt text.** The first store records hashes, byte counts, roles, and source names so it is safe to use as cache scaffolding.

## Risks / Trade-offs

- **Block-level sink candidates are coarse.** -> Mitigation: label them as candidates and defer token-level sink handling to a backend that exposes tokenizer/KV details.
- **Metadata-only storage does not speed up inference.** -> Mitigation: this is Phase 1 scaffolding for cache keys and storage layout, not the performance layer.
- **Fixture roles may be wrong for real transcripts.** -> Mitigation: keep the CLI configurable with selected scenarios and sink block count.
