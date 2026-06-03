## Context

The correctness suite currently has three pieces: dataset registry, case materialization, and response scoring. The missing piece is response generation. We need a runner that can take sampled cases, produce full-prompt and session-tail outputs with llama.cpp, and write response JSONL that the scorer already understands.

## Goals / Non-Goals

**Goals:**
- Add a `run` subcommand to the correctness eval benchmark.
- Support `full`, `session-tail`, and `both` modes.
- Record enough timing and prompt metadata to debug quality/speed tradeoffs.
- Optionally score the generated responses immediately after model runs.

**Non-Goals:**
- Do not implement the public Flashcache session API.
- Do not optimize batch throughput yet.
- Do not run large PC benchmarks automatically from local validation.

## Decisions

1. Use llama.cpp HTTP helpers directly.

   The runner needs low-level slot control: complete stable prefix, save slot, restore slot, then complete the tail. The existing `LlamaClient` and `ManagedLlamaServer` already expose those operations, so the runner can avoid adding API surface to the wrapper.

2. Isolate by case and mode by default.

   Correctness is more important than throughput for this first quality gate. A fresh managed server per case/mode avoids accidental state carryover across unrelated eval rows. Later we can add a faster batch mode after we trust reset semantics.

3. Use response JSONL as the integration boundary.

   The scorer already consumes records with `case_id`, `mode`, `response`, and optional latency. Keeping response generation separate from scoring makes it easy to copy outputs from the Windows PC back to the Mac and score them deterministically.

4. Score optionally in the same command.

   The runner can write responses only, or it can immediately call the existing scorer and write a score JSON. This keeps PC runs simple without forcing a long model run into every local test.

## Risks / Trade-offs

- [Risk] Per-case server lifecycle is slow. -> Mitigation: start with small samples and add a faster batch mode only after correctness semantics are clear.
- [Risk] Session-tail may produce malformed answers because the backend treats tail-only prompts differently than true chat continuation. -> Mitigation: preserve prompt hashes, setup telemetry, and raw response text for inspection.
- [Risk] Slot save/restore can fail for some llama.cpp builds. -> Mitigation: fail the case with a clear error record rather than silently scoring missing output as quality loss.
