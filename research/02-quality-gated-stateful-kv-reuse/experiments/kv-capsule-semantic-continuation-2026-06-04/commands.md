# KV Capsule Semantic Continuation Commands

## OpenSpec

```bash
openspec new change probe-kv-capsule-semantic-continuation
openspec validate probe-kv-capsule-semantic-continuation --type change --strict
```

## Sync Mac Worktree To DushyantPC

```bash
git bundle create /tmp/track02-kv-capsule.bundle be248f2..HEAD
scp /tmp/track02-kv-capsule.bundle DushyantPC:C:/Users/Dushyant/Projects/track02-kv-capsule.bundle
ssh DushyantPC "powershell -NoProfile -Command "cd C:\\Users\\Dushyant\\Projects\\ai-research-lab; git fetch C:\\Users\\Dushyant\\Projects\\track02-kv-capsule.bundle HEAD:refs/remotes/bundle/track02-kv-capsule; git merge --ff-only refs/remotes/bundle/track02-kv-capsule""
```

## Feasibility And Source Checks

```bash
ssh DushyantPC 'cmd /c "where /r C:\Users\Dushyant\Tools llama.h & where /r C:\Users\Dushyant\Projects llama.h & where /r C:\Users\Dushyant\Downloads llama.h"'
ssh DushyantPC 'cmd /c "git ls-remote https://github.com/ggml-org/llama.cpp.git HEAD"'
ssh DushyantPC 'cmd /c "if not exist C:\Users\Dushyant\Tools\llama.cpp-kv-capsule-src git clone --depth 1 https://github.com/ggml-org/llama.cpp.git C:\Users\Dushyant\Tools\llama.cpp-kv-capsule-src"'
git ls-remote https://github.com/ggml-org/llama.cpp.git | grep -i a731805ce
ssh DushyantPC 'cmd /c "cd /d C:\Users\Dushyant\Tools\llama.cpp-kv-capsule-src && git fetch --depth 1 origin tag b9493 && git show b9493:include/llama.h > C:\Users\Dushyant\Tools\llama.cpp-kv-capsule-src\llama-b9493.h"'
```

## Direct API Smoke And Token Smoke

```bash
scp research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/raw/kv_capsule_ctypes_runner.py DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/raw/kv_capsule_ctypes_runner.py
ssh DushyantPC 'cmd /c "cd /d C:\Users\Dushyant\Projects\ai-research-lab && python research\01-ssd-native-inference-current\benchmarks\kv-capsule-semantic-continuation-2026-06-04\raw\kv_capsule_ctypes_runner.py --mode smoke --backend cuda_v13 --ctx-size 32768 --n-gpu-layers -1"'
ssh DushyantPC 'cmd /c "cd /d C:\Users\Dushyant\Projects\ai-research-lab && python research\01-ssd-native-inference-current\benchmarks\kv-capsule-semantic-continuation-2026-06-04\raw\kv_capsule_ctypes_runner.py --mode token-smoke --backend cuda_v13 --ctx-size 32768 --n-gpu-layers -1"'
```

## GPU Backend Diagnosis

```bash
ssh DushyantPC 'cmd /c "nvidia-smi"'
scp research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/raw/gpu_backend_diag.py DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/raw/gpu_backend_diag.py
ssh DushyantPC 'cmd /c "cd /d C:\Users\Dushyant\Projects\ai-research-lab && python research\01-ssd-native-inference-current\benchmarks\kv-capsule-semantic-continuation-2026-06-04\raw\gpu_backend_diag.py"'
```

## Accepted Partial Family 1 Run

```bash
ssh DushyantPC 'cmd /c "cd /d C:\Users\Dushyant\Projects\ai-research-lab && del /q research\01-ssd-native-inference-current\benchmarks\kv-capsule-semantic-continuation-2026-06-04\raw\codeword-records.jsonl 2>NUL & del /q research\01-ssd-native-inference-current\benchmarks\kv-capsule-semantic-continuation-2026-06-04\raw\codeword-run-info.json 2>NUL & del /q research\01-ssd-native-inference-current\benchmarks\kv-capsule-semantic-continuation-2026-06-04\raw\codeword-console.txt 2>NUL & python research\01-ssd-native-inference-current\benchmarks\kv-capsule-semantic-continuation-2026-06-04\raw\kv_capsule_ctypes_runner.py --mode codeword --backend cuda_v13 --ctx-size 32768 --n-gpu-layers -1 --predict 48 --cases 10 > research\01-ssd-native-inference-current\benchmarks\kv-capsule-semantic-continuation-2026-06-04\raw\codeword-console.txt 2>&1"'
ssh DushyantPC "powershell -NoProfile -Command "Stop-Process -Id 36828 -Force""
scp -r 'DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/raw/*' research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/raw/
```

The run was stopped by orchestration stop rule after native full-visible positive control failed.

## Validation

```bash
openspec validate probe-kv-capsule-semantic-continuation --type change --strict
openspec validate --all --strict
```
