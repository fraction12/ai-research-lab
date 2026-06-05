# Gemma 4 12B Replication Prep Design

## Research Question

Can the same official llama.cpp sequence-file state route preserve tail-only semantic continuation for Gemma 4 12B on the already-gated Family 1 and Family 2 tasks?

## Baseline And Controls

For each approved gate, run controls in order:

1. `native_full_visible_prefix_plus_tail`
2. `native_fresh_tail_only`
3. `native_live_append_tail_only`
4. `native_restored_capsule_append_tail_only`

The restored control is interpretable only if full-visible passes, fresh-tail does not leak, and live append passes.

## Model Profile Requirements

Gemma 4 12B must be selected through an explicit profile/config rather than implicit CLI edits. The profile must record:

- model family/name and local model path,
- GGUF/hash/size metadata,
- tokenizer/template assumptions,
- context size and decode budget,
- llama.cpp bundle/backend and the exact llama DLL path/name,
- sequence-state export availability,
- route requested/effective/internal labels,
- any model-specific sampler/template notes.

The GPT-OSS profile must remain available and unchanged.

## Committed Profile Resolver

This change adds a non-inference profile resolver at `research/01-ssd-native-inference-current/benchmarks/kv_capsule_profiles.py`.

The resolver is intentionally small and repo-safe:

- `gpt-oss-20b` preserves the existing GPT-OSS runtime defaults, including the old `libllama.dll` name.
- `gemma4-12b` resolves the Ollama Gemma text blob, b9512 CUDA runtime, `llama.dll`, raw/cache defaults, context/decode knobs, and output-calibration notes.
- `--llama-dll` is emitted in generated runner arguments so a raw runner does not need to pretend b9512's `llama.dll` is named `libllama.dll`.
- `--check-paths` reports path availability without loading a model.
- `--completion-smoke-command` prints the Gemma `llama-completion` one-shot command for orchestration.

The ignored raw Family 1/2 runners still need a runtime-only patch to consume `--model-profile` / `--llama-dll` and hash/export-probe the resolved DLL path. Orchestration owns that ignored-runner patch and DushyantPC execution. The committed resolver alone is not evidence that Gemma capsule runs are executable.

## DushyantPC Runtime Inventory

Orchestration verified the following concrete Gemma runtime facts on DushyantPC:

- Gemma 4 12B is already installed through Ollama as a hash-named blob, not as a visible `gemma-4-12B-it-Q4_K_M.gguf` file.
- Ollama manifest path: `C:\Users\Dushyant\.ollama\models\manifests\registry.ollama.ai\library\gemma4\12b`.
- Text model blob path: `C:\Users\Dushyant\.ollama\models\blobs\sha256-5cf8a1f2fc4268b3fd628743675910cf1d8137c4742d0be401c3e885f605023a`.
- Text model blob size: `7,381,382,048` bytes.
- Ollama also has an mmproj layer digest beginning `sha256:a18399bf`; the initial one-shot smoke used the text model blob directly and did not require mmproj.
- A duplicate Hugging Face download was accidentally started into the ignored repo model cache, then stopped and cleaned by orchestration; no final duplicate GGUF remains.
- The separate llama.cpp CUDA 13 runtime is installed at `C:\Users\Dushyant\Tools\llama-b9512-cuda13`.
- `llama-cli --version` and `llama-server --version` both reported `version: 9512 (0dbfa66a1)`, Clang 19.1.5 Windows x86_64.
- DLL compatibility requirement: b9512 ships `llama.dll`, not `libllama.dll`; the harness profile must support configurable llama DLL name/path rather than assuming `libllama.dll`.
- The b9512 `llama.dll` exports `llama_state_seq_save_file`, `llama_state_seq_load_file`, `llama_state_seq_get_size`, `llama_state_seq_get_data`, `llama_state_seq_set_data`, `llama_model_load_from_file`, and `llama_tokenize`.
- RTX 3060 12GB was healthy; `nvidia-smi` reported about 11.8GB free before smoke.
- `llama-cli` on b9512 is conversation-oriented; `-no-cnv` is not supported there and it directs operators to `llama-completion` instead.
- A one-shot `llama-completion` smoke against the text model blob exited `0`.
- Smoke output caveat: raw output included Gemma thinking/channel tokens such as thought/channel markers, so the Gemma profile must calibrate prompt/scoring behavior or use a supported route to disable thinking before Family 1/2 evidence.
- For `llama-completion` / CLI load smokes, the profile exposes `--reasoning off` when supported. This is a CLI/template calibration knob only; it is not proof that the raw C API sequence-state runner suppresses thinking/channel output unless that runner path uses the same machinery and passes the empirical gate.
- After orchestration cleanup, no leftover `llama-cli`, `llama-completion`, Hugging Face download, Python harness, or benchmark process remained; only Ollama app/service processes were present.

## Runtime Assumptions

- Orchestration owns DushyantPC SSH and model execution.
- Repo work may prepare docs or profile scaffolding only.
- No Gemma run is evidence until raw/cache paths are ignored and local/remote syntax/help/stale-grep checks pass.
- `--state-route auto` should resolve to `seq_file` when sequence file exports are available; `whole-context` may only be labeled fallback/diagnostic and cannot count as success.

## Smoke Ladder

1. Gemma profile dry-run/help check.
2. Raw-only smoke or token-smoke if orchestration approves.
3. One-shot runtime smoke via `llama-completion` if needed to verify model load; include `--reasoning off` when supported and do not use interactive `llama-cli` as the harness route.
4. Family 1 3-case smoke.
5. Family 1 30-case gate if smoke passes.
6. Family 2 smoke only after Family 1 passes.
7. Family 2 primary only after Family 2 smoke passes.

Do not run beyond these gates without new orchestration clearance.

## Metrics

Record the same metrics as GPT-OSS:

- answer-contained and exact match,
- response/normalized/generated hashes,
- full-vs-live and live-vs-restored hash parity,
- prefix/tail/full token counts and hashes,
- capsule byte counts and save/restore timings,
- sequence positions and sequence id,
- model/backend/build metadata,
- process cleanup status.

## Artifact Boundary

Prompt-bearing raw artifacts must remain ignored under Track 01 benchmark paths. Committed Track 02 artifacts may include hashes, counts, booleans, routes, timings, failure classes, and model metadata. Do not commit raw prompts, raw responses, expected answer strings, token arrays/slices, generated token arrays/slices, top-k arrays, token piece previews, or state bytes.

## Stop Rules

- Stop before model work if OpenSpec validation fails, raw/cache paths are not ignored, stale GPT-OSS-only assumptions are reachable, or DushyantPC sanity fails.
- If Gemma full-visible fails, classify model/task/template/scorer difficulty and do not interpret capsule.
- If fresh tail passes, classify leakage/benchmark flaw.
- If live append fails, classify harness/tokenization/position/template route blocker.
- If restored capsule fails after full/live pass, inspect sequence route telemetry and package the narrowest route/model blocker.
- If semantic pass occurs but hash parity differs, package semantic pass with deterministic-parity warning.
