## Why

Track 02 now has a narrow positive KV capsule mechanism signal on synthetic Gemma 4 12B codeword and key-value gates, but that is not enough for a research-paper claim. The next experiment must test whether tail-only persisted KV capsules preserve full-prompt quality and reduce repeated-prefix cost on real Hugging Face benchmark rows from `google/IFEval` and `openai/graphwalks`.

## What Changes

- Add a paper-facing HF-backed KV capsule benchmark design with no handmade benchmark cases except synthetic preflight gates.
- Build deterministic candidate pools from `google/IFEval` and `openai/graphwalks`, preserving source dataset id, split, row id or row offset, row hash, prompt hashes, and transform hashes.
- Gate paper-facing comparisons on full-visible baseline pass so capsule quality is compared only on cases the model can solve with the complete prompt.
- Run a paired control matrix per selected case: full visible, fresh tail only, native live append, native restored capsule append, wrong capsule negative, and documented full-prompt cache resend.
- Add GraphWalks-specific context-compilation controls as a separate secondary analysis, not as pure KV capsule evidence.
- Record semantic quality, speed, token, capsule, hardware, runtime, telemetry, and failure-classification data needed for paper methods and ablations.
- Define stop rules for runner failures, insufficient full-visible pass counts, hidden state mismatch, runtime instability, and transport failures.

## Capabilities

### New Capabilities

- `hf-kv-capsule-paper-benchmark`: Defines the HF-backed paper benchmark for KV capsule semantic continuation, including cohorts, hypotheses, controls, metrics, stop rules, artifacts, and interpretation rules.

### Modified Capabilities

- `flashcache-correctness-eval-suite`: Requires correctness workflows to preserve HF dataset provenance, deterministic candidate sampling, baseline-pass gating, and per-control scoring for the HF KV capsule benchmark.
- `llama-cpp-agent-cache-wrapper`: Requires lower-level KV capsule runs to expose native live append, restored capsule append, capsule metadata, and wrong-capsule negative controls when used for paper-facing claims.
- `research-positioning-doc`: Requires Track 02 paper summaries to distinguish synthetic mechanism gates, HF benchmark evidence, pure KV capsule effects, and role-aware context-compilation effects.

## Impact

- Adds a design artifact under `research/02-quality-gated-stateful-kv-reuse/docs/`.
- Adds OpenSpec artifacts under `openspec/changes/run-hf-kv-capsule-paper-benchmark/`.
- Future implementation will likely add or extend local benchmark scripts under `research/01-ssd-native-inference-current/benchmarks/`.
- Prompt-bearing candidate, raw response, and capsule artifacts must remain under ignored benchmark paths.
- Primary runtime target is Gemma 4 12B on DushyantPC through the working llama.cpp sequence-file route; GPT-OSS results may be retained as a comparison but must not be blended with Gemma results.
