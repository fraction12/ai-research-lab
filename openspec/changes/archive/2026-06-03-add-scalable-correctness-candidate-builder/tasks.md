## 1. Candidate Builder

- [x] 1.1 Add candidate-build parsing, metadata helpers, and IFEval easy-profile filters.
- [x] 1.2 Implement a `build-candidates` CLI command that writes combined case JSONL files.

## 2. Answer Guidance

- [x] 2.1 Add dataset-specific JSON answer hints without changing raw protocol behavior.
- [x] 2.2 Record the answer hint id in response and dry-run records.

## 3. Tests And Docs

- [x] 3.1 Add unit coverage for candidate specs, easy filtering, candidate writing, and answer hints.
- [x] 3.2 Update benchmark docs with the scalable candidate-builder and ladder workflow.

## 4. Validation And Benchmark

- [x] 4.1 Run local tests, OpenSpec validation, and diff hygiene checks.
- [x] 4.2 Build a larger local candidate set and run a PC baseline-pass ladder.
- [x] 4.3 Record the benchmark dataset artifacts and summarize whether the selected set is large enough.
