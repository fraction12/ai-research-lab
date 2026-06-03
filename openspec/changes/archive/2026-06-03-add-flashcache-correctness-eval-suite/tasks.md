## 1. Eval Harness

- [x] 1.1 Add a Flashcache correctness eval benchmark module with dataset registry and CLI dataset listing.
- [x] 1.2 Implement sample materialization for IFEval, MRCR, and GraphWalks cases with stable-prefix, tail, and full-prompt fields.
- [x] 1.3 Implement deterministic scoring for MRCR, GraphWalks, and supported IFEval instruction checks.
- [x] 1.4 Implement response-pair scoring output with per-mode scores, deltas, unsupported checks, and summary aggregates.

## 2. Tests And Docs

- [x] 2.1 Add unit tests for dataset registry, case construction, and scorers.
- [x] 2.2 Update benchmark docs with dataset choices and local run commands.
- [x] 2.3 Ignore generated correctness eval inputs and results.

## 3. Validation

- [x] 3.1 Run Python compile checks and unit tests.
- [x] 3.2 Run OpenSpec strict validation.
