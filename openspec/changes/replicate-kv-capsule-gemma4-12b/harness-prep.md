# Harness Prep Notes

## Current Harness Location

The executable native C API runners for the latest Family 1 and Family 2 gates live under ignored Track 01 raw benchmark paths. They are intentionally not committed because those raw paths can contain prompt-bearing records, responses, token details, and state/cache artifacts.

This change adds a committed non-inference profile resolver at `research/01-ssd-native-inference-current/benchmarks/kv_capsule_profiles.py`. It prepares profile metadata and command arguments, but it does not itself run or patch model-bearing benchmarks.

The ignored raw Family 1/2 runners still need orchestration's runtime-only patch so their actual load/export/hash paths consume `--model-profile` / `--llama-dll`. In particular, b9512 ships `llama.dll`, not `libllama.dll`; any runner that still hashes or loads `bundle / "libllama.dll"` is not Gemma-ready.

## Required Patch Shape For Orchestration

Add an explicit model profile mechanism to the ignored runner before Gemma model execution. The profile mechanism should preserve the GPT-OSS default and make Gemma selection deliberate.

Suggested profile fields:

```json
{
  "profile_id": "gemma4-12b",
  "model_family": "gemma",
  "model_name": "Gemma 4 12B",
  "ollama_manifest_path": "C:\\Users\\Dushyant\\.ollama\\models\\manifests\\registry.ollama.ai\\library\\gemma4\\12b",
  "model_path": "C:\\Users\\Dushyant\\.ollama\\models\\blobs\\sha256-5cf8a1f2fc4268b3fd628743675910cf1d8137c4742d0be401c3e885f605023a",
  "model_size_bytes": 7381382048,
  "mmproj_layer_present": true,
  "mmproj_layer_note": "Ollama manifest has an mmproj layer beginning sha256:a18399bf; initial text-only smoke did not require it.",
  "expected_architecture": "<recorded from model metadata after load>",
  "tokenizer_or_template_notes": "Gemma smoke emitted thinking/channel markers; calibrate scoring or disable thinking through a supported route before evidence.",
  "llama_bundle": "C:\\Users\\Dushyant\\Tools\\llama-b9512-cuda13",
  "llama_version": "9512 (0dbfa66a1)",
  "llama_dll_path": "C:\\Users\\Dushyant\\Tools\\llama-b9512-cuda13\\llama.dll",
  "llama_dll_name": "llama.dll",
  "ctx_size": 32768,
  "predict": 48,
  "state_route": "auto",
  "expected_effective_route": "seq_file",
  "raw_dir": "research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-gemma4-12b-replication-2026-06-04/raw",
  "cache_dir": "research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-gemma4-12b-replication-2026-06-04/cache"
}
```

Suggested CLI shape:

```text
--model-profile {gpt-oss-20b,gemma4-12b}
--model-profile-file <optional-json>
--model <explicit override>
--llama-dll <explicit llama.dll/libllama.dll path>
--out-dir <profile default or explicit override>
--cache-dir <profile default or explicit override>
--state-route {auto,seq-file,seq-memory,whole-context}
```

Committed resolver examples:

```text
python research/01-ssd-native-inference-current/benchmarks/kv_capsule_profiles.py --profile gemma4-12b --check-paths
python research/01-ssd-native-inference-current/benchmarks/kv_capsule_profiles.py --profile gemma4-12b --runner-args
python research/01-ssd-native-inference-current/benchmarks/kv_capsule_profiles.py --profile gemma4-12b --completion-smoke-command
```

Rules:

- Selecting `gemma4-12b` must change raw/cache defaults away from the GPT-OSS paths.
- Selecting `gemma4-12b` must load b9512's `llama.dll` or another explicit compatible DLL path. Do not assume the DLL is named `libllama.dll`.
- Runner metadata and export scans must use the resolved DLL path, not a hardcoded `bundle / "libllama.dll"`.
- Raw/cache paths must be ignored before any DushyantPC execution.
- The run metadata must include the selected profile and all resolved fields.
- If Gemma-specific tokenization/template behavior differs, it must be recorded before evidence and not silently patched mid-gate.
- Gemma scoring must handle or suppress thinking/channel markers before Family 1/2 evidence. The initial one-shot smoke loaded successfully but produced such markers in raw output.
- The Gemma `llama-completion` smoke command should include `--reasoning off` when supported. That flag is a CLI/template calibration aid and does not replace the raw C API Family 1/2 semantic gates.
- `whole-context` remains diagnostic fallback only.

## Confirmed Runtime Facts

- Gemma 4 12B is installed through Ollama as the text model blob listed in the profile above.
- No final duplicate Hugging Face GGUF remains in the repo cache after orchestration cleanup.
- b9512 CUDA 13 runtime is installed and version-checked.
- b9512 exports required sequence-state symbols from `llama.dll`.
- RTX 3060 12GB had about 11.8GB free before smoke.
- `llama-cli` is conversation-oriented for this runtime; use `llama-completion` for one-shot load smoke instead.
- Orchestration confirmed no stale model/download/harness processes remained after cleanup.

## Smoke Ladder For Orchestration

1. Local syntax/help/stale-grep on the patched ignored runner.
2. Remote syntax/help/stale-grep and export probe.
3. Optional one-shot `llama-completion` load smoke using the Gemma text blob.
4. Family 1 smoke with Gemma profile.
5. Family 1 primary if smoke passes.
6. Family 2 smoke if Family 1 primary passes.
7. Family 2 primary if Family 2 smoke passes.

No Family 3, GraphWalks, broad retrieval, noiseless evidence, or agent-context work should run in this replication change.
