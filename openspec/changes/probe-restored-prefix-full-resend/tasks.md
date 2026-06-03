## 1. Implement Tiny Restored-Prefix Probe

- [x] 1.1 Add a focused Track 01 restored-prefix full-resend runner or minimally extend the correctness evaluator with a `restored-full` mode.
- [x] 1.2 Include synthetic exact-token cases with cold full, prime/save, restored full-resend, perturbed full-resend, and wrong-slot full-resend controls.
- [x] 1.3 Record raw outputs, parsed answers, prompt hashes, timing/token telemetry, slot save/restore telemetry, and failure classifications.
- [x] 1.4 Add focused unit tests with fake llama.cpp clients for mode sequencing and safety classification.

## 2. Run Tiny Probe On DushyantPC

- [x] 2.1 Sync the probe tooling to the DushyantPC checkout.
- [x] 2.2 Run the tiny synthetic probe with `gpt-oss-20b-mxfp4.gguf` and the portable llama.cpp backend.
- [x] 2.3 Copy raw probe outputs and cache artifacts back to the Mac checkout.

## 3. Record Tiny-Probe Artifacts

- [x] 3.1 Write `commands.md` with exact commands.
- [x] 3.2 Write `model-info.json` with exact model, quantization, backend, command-line, machine, and run metadata.
- [x] 3.3 Write `summary.json` with mode-level, case-level, timing, and safety-control results.
- [x] 3.4 Write `mechanism-decision.md` with the decision for whether restored-prefix full-resend works.
- [x] 3.5 Write `failure-classifications.json` and `artifact-manifest.json`.
- [x] 3.6 Write `README.md` for the experiment directory.

## 4. Gate GraphWalks Follow-Up

- [x] 4.1 Assess the six selected GraphWalks restored-full follow-up gate after the tiny probe.
- [x] 4.2 Record the stop rule and do not run GraphWalks because useful-acceleration evidence did not pass.
- [x] 4.3 Record that GraphWalks were not run; no six-case cold-full versus restored-full artifacts were collected.

## 5. Validate And Land

- [x] 5.1 Run relevant Track 01 tests.
- [x] 5.2 Run `npx --yes @fission-ai/openspec@latest validate --all --strict`.
- [x] 5.3 Confirm no broad benchmarks and no vault-mind model use.
- [x] 5.4 Commit, push, and sync DushyantPC to the resulting `main` commit when implementation artifacts are complete.
