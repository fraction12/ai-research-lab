## 1. Implement Prefix-Reuse Audit Probe

- [x] 1.1 Add a focused Track 01 direct llama.cpp prefix-reuse audit runner.
- [x] 1.2 Include synthetic long-prefix exact-token cases and controls for cold-full, same-server exact repeat, same-server restore/full-resend, and fresh-server restore/full-resend.
- [x] 1.3 Record raw outputs, parsed answers, prompt hashes, timing/token telemetry, slot save/restore telemetry, log paths, and mechanism classifications.
- [x] 1.4 Add focused unit tests with fake llama.cpp clients for sequencing, telemetry extraction, and classification.

## 2. Run Audit On DushyantPC

- [x] 2.1 Sync the probe tooling to the DushyantPC checkout.
- [x] 2.2 Run the tiny audit with `gpt-oss-20b-mxfp4.gguf` and the portable llama.cpp backend.
- [x] 2.3 Copy raw audit outputs and cache/log artifacts back to the Mac checkout.

## 3. Record Track 02 Artifacts

- [x] 3.1 Write `commands.md` with exact commands.
- [x] 3.2 Write `model-info.json` with exact model, quantization, backend, command-line, machine, and run metadata.
- [x] 3.3 Write `summary.json` with mode-level, timing, token, slot, and classification results.
- [x] 3.4 Write `mechanism-decision.md` with the decision for exact-repeat and restored-slot reuse.
- [x] 3.5 Write `artifact-manifest.json` and `failure-classifications.json`.
- [x] 3.6 Write `README.md` for the experiment directory.

## 4. Gate Next Mechanism Step

- [x] 4.1 Record that exact-repeat reuse passed, so backend/API/cache-prompt is not the primary stop rule.
- [x] 4.2 Record that fresh-server restore reuse failed, so the next stop rule is slot restore/persistent session investigation.
- [x] 4.3 Record that GraphWalks remain deferred because fresh-server restored-prefix reuse did not pass.

## 5. Validate And Land

- [x] 5.1 Run relevant Track 01 tests.
- [x] 5.2 Run `npx --yes @fission-ai/openspec@latest validate --all --strict`.
- [x] 5.3 Confirm no broad benchmarks, no GraphWalks, and no excluded model use.
- [x] 5.4 Commit, push, and sync DushyantPC to the resulting `main` commit when implementation artifacts are complete.
