## Context

The benchmark harness now runs realistic local-agent fixtures on large local models, including a Windows PC over SSH. Those runs are long enough that quiet stdout makes it hard to distinguish a healthy model call from a stuck harness. The repo also has multiple raw JSON result files for the same model/fixture, so manual comparison is getting noisy.

## Goals / Non-Goals

**Goals:**
- Print concise progress before each long phase and scenario-level model call.
- Keep progress output useful on both macOS and Windows shells.
- Provide a small JSON summarizer for comparing result files without reading raw artifacts by hand.
- Preserve existing benchmark result JSON schemas.

**Non-Goals:**
- Do not change benchmark timing semantics.
- Do not add a daemon, dashboard, dependency, or remote execution system.
- Do not persist model files, slot caches, logs, or generated prompts in source control.

## Decisions

- Use plain `print(..., flush=True)` progress lines in the benchmark scripts. This is portable, low-risk, and works over SSH where buffering made the PC runs feel silent.
- Print before each long action rather than after. The important operator signal is what the harness is about to spend time on: priming, baseline scenario, direct wrapper scenario, and cache-aware scenario.
- Add a standalone summary script instead of baking comparison logic into every benchmark. This keeps raw result generation unchanged and lets us compare old and new JSON files together.
- Make the summarizer tolerant of the two current result schemas. It should classify direct llama.cpp prompt-cache results and Flashcache wrapper results by keys already present in `comparison`.

## Risks / Trade-offs

- More stdout could clutter short dry runs -> keep messages one line and phase-oriented.
- Result schemas may evolve -> use defensive field lookup and emit `n/a` for missing metrics.
- Multiple runs can have different warm/cold model state -> summarizer reports evidence, but interpretation still needs run context.
