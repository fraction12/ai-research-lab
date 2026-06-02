## Overview

Add a compact research note under `docs/` rather than spreading the same judgment across multiple files. The note will be written for future retrieval: clear bottom line, known prior art, project-specific wedge, paper-worthy bar, and source links.

## Decisions

- Use `docs/research-positioning.md` as the canonical note for the novelty/prior-art question.
- Keep `docs/technical-map.md` focused on the technical mental model and link to the positioning note.
- Keep `docs/decision-log.md` concise by recording only the decision outcome.
- Keep `docs/references.md` as the source index with paper and system links.

## Risks

- The literature is moving quickly, so the note must state that the check is time-bounded.
- Claims about being "net new" remain provisional until benchmark comparisons are run against close baselines such as vLLM/LMCache, llama.cpp, and oMLX.

## Validation

- Validate the OpenSpec change.
- Run a lightweight docs sanity check by reading the edited files and searching for broken local references.
