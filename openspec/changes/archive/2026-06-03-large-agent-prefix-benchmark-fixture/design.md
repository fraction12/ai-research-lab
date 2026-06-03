## Context

Post-merge DushyantPC runs show a repeated pattern: direct llama.cpp slot restore is flat/noisy on the 5.5 KB Printy fixture, while the Flashcache wrapper saves about 11-13% prompt-processing time. That is useful, but too small to support the bigger thesis that SSD-backed reusable prefix state can make regular local agent loops practical.

Real local agents carry much larger stable context: system/developer instructions, tool schemas, repo maps, active specs, prior task memory, safety rules, and benchmark instructions. This change creates a controlled ladder of larger reusable prefixes while preserving the same volatile changed-tail turns.

## Goals / Non-Goals

**Goals:**
- Produce deterministic fixture variants with target reusable-prefix byte sizes.
- Preserve a clear cache boundary: generated stable/semi-stable prefix first, volatile tails last.
- Check fixtures for obvious secret leakage and context-budget mistakes before model runs.
- Make PC benchmark commands repeatable for direct slot and Flashcache wrapper comparisons.

**Non-Goals:**
- Do not change llama.cpp, Ollama, or Flashcache timing semantics.
- Do not claim answer quality improvements from prompt-processing timing alone.
- Do not scrape private transcripts, secrets, raw Telegram IDs, private keys, or local personal context.
- Do not hand-author separate large fixtures when a deterministic generator can avoid drift.

## Decisions

- Generate fixtures from an allowlisted safe corpus plus synthetic-but-realistic agent context. This keeps the benchmark realistic enough for prefix behavior without risking private data.
- Use byte targets rather than token targets. The existing fixture and summary tooling already report prefix bytes, and tokenization differs across backends.
- Emit a metadata block with target bytes, actual prefix bytes, expansion source names, context-budget notes, and safety-check results.
- Keep scenario volatile tails inherited from the Printy fixture. This isolates the variable under test: reusable prefix size.
- Start with 16 KB, 32 KB, and 64 KB target prefixes. The PC run matrix can skip a size if the model/context budget or runtime becomes impractical.

## Risks / Trade-offs

- Larger prefixes may exceed the chosen context size -> compute prompt byte/token proxy and require an explicit context-size recommendation per generated fixture.
- Synthetic context may not represent real repo entropy -> include safe excerpts from repo docs/specs and label generated material clearly.
- Secret scanning can miss unusual private data -> use an allowlist corpus and common deny patterns; do not read arbitrary home directories.
- Full live ladder can be slow -> run dry-run and summary checks first, then execute PC benchmarks from smallest to largest with progress logs.
