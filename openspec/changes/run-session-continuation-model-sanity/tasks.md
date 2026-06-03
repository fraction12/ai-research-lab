## 1. Prepare Bounded Option 2 Inputs

- [x] 1.1 Create the Track 02 experiment directory.
- [x] 1.2 Add `transcript-format-cases.jsonl` with exact synthetic prompts.
- [x] 1.3 Sync the new case file to DushyantPC.

## 2. Run Alternate Model Sanity Check On DushyantPC

- [x] 2.1 Run a bounded full-mode probe with `vault-mind-q5_k_m.gguf`.
- [x] 2.2 If the probe passes, run the default litmus case set on `vault-mind-q5_k_m.gguf`.
- [x] 2.3 If the probe passes, run the transcript-format litmus case set on `vault-mind-q5_k_m.gguf`.
- [x] 2.4 Copy raw litmus outputs back to the Mac checkout.

## 3. Record Track 02 Artifacts

- [x] 3.1 Write `commands.md` with exact commands.
- [x] 3.2 Write `model-info.json` with exact model, quantization/file-name hint, backend, command-line, and machine metadata.
- [x] 3.3 Write `summary.json` with probe, mode-level, case-level, and taxonomy results.
- [x] 3.4 Write `continuation-model-sanity.md` with the Option 2 interpretation and Option 3 handoff.
- [x] 3.5 Write `README.md` for the experiment directory.

## 4. Validate And Land

- [x] 4.1 Run relevant Track 01 tests.
- [x] 4.2 Run `npx --yes @fission-ai/openspec@latest validate --all --strict`.
- [x] 4.3 Confirm no broad benchmarks or GraphWalks reruns were run.
- [x] 4.4 Commit, push, and sync DushyantPC to the resulting `main` commit.
