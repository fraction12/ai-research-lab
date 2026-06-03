## 1. Implement Litmus Tooling

- [x] 1.1 Add a tiny session-continuation litmus runner under Track 01 benchmarks.
- [x] 1.2 Include full-prompt, live-tail, restored-tail, and fresh-tail modes.
- [x] 1.3 Score exact secret-token recall and record raw outputs, parsed answers, prompt hashes, timings, and setup telemetry.
- [x] 1.4 Add focused unit tests with fake llama.cpp clients.

## 2. Run Focused Litmus On DushyantPC

- [x] 2.1 Sync the litmus tooling to the DushyantPC checkout.
- [x] 2.2 Run the litmus with `gpt-oss-20b-mxfp4.gguf` and the portable llama.cpp backend.
- [x] 2.3 Copy raw litmus outputs back to the Mac checkout.

## 3. Record Track 02 Artifacts

- [x] 3.1 Write `commands.md` with exact commands.
- [x] 3.2 Write `model-info.json` with exact model, quantization, backend, command-line, and machine metadata.
- [x] 3.3 Write `summary.json` with mode-level and case-level pass/fail results.
- [x] 3.4 Write `continuation-interpretation.md` with the decision for whether session-tail is a valid semantic primitive.
- [x] 3.5 Write `README.md` for the experiment directory.

## 4. Validate And Land

- [x] 4.1 Run relevant Track 01 tests.
- [x] 4.2 Run `npx --yes @fission-ai/openspec@latest validate --all --strict`.
- [x] 4.3 Confirm no broad benchmarks or GraphWalks reruns were run.
- [x] 4.4 Commit, push, and sync DushyantPC to the resulting `main` commit.
