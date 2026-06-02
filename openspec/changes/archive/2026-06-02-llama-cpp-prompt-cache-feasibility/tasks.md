## 1. Environment

- [x] 1.1 Install or locate llama.cpp server binary.
- [x] 1.2 Obtain a small GGUF model for local benchmarking.

## 2. Benchmark

- [x] 2.1 Add llama.cpp prompt-cache benchmark script.
- [x] 2.2 Build reusable prefix and changed-tail prompts from existing fixtures.
- [x] 2.3 Implement server start/health/stop handling.
- [x] 2.4 Implement baseline, slot save, slot restore, and restored-prefix runs.
- [x] 2.5 Persist result JSON and ignore generated artifacts.

## 3. Results

- [x] 3.1 Run the benchmark against the LightningITB fixture.
- [x] 3.2 Document result and interpretation.

## 4. Validation

- [x] 4.1 Validate the OpenSpec change.
- [x] 4.2 Run Python compile checks.
- [x] 4.3 Validate all OpenSpec specs after archive.
