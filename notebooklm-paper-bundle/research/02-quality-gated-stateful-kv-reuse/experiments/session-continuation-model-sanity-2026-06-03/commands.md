# Commands

Date: 2026-06-03

## Discover Alternate Local GGUFs

```bat
dir /s /b C:\Users\Dushyant\*.gguf
```

Relevant discovered models:

```text
C:\Users\Dushyant\Documents\vault-mind\vault-mind-q5_k_m.gguf
C:\Users\Dushyant\My Documents\vault-mind\vault-mind-q5_k_m.gguf
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\models\gpt-oss-20b-mxfp4.gguf
C:\Users\Dushyant\Projects\ssd-native-inference\benchmarks\models\gemma-3-270m-it-Q8_0.gguf
C:\Users\Dushyant\Projects\ssd-native-inference\benchmarks\models\gpt-oss-20b-mxfp4.gguf
```

## Model File Probe

```powershell
Get-Item C:\Users\Dushyant\Documents\vault-mind\vault-mind-q5_k_m.gguf | Select-Object FullName,Length,LastWriteTime | ConvertTo-Json
```

Observed:

```json
{
  "FullName": "C:\\Users\\Dushyant\\Documents\\vault-mind\\vault-mind-q5_k_m.gguf",
  "Length": 5444831136,
  "LastWriteTime": "/Date(1774404285191)/"
}
```

## Transcript Case Sync

```bash
cd /Users/dushyantgarg/Documents/Projects/ai-research-lab
ssh dushyantpc "powershell -NoProfile -Command \"New-Item -ItemType Directory -Force C:\\Users\\Dushyant\\Projects\\ai-research-lab\\research\\02-quality-gated-stateful-kv-reuse\\experiments\\session-continuation-model-sanity-2026-06-03 | Out-Null\""
scp research/02-quality-gated-stateful-kv-reuse/experiments/session-continuation-model-sanity-2026-06-03/transcript-format-cases.jsonl dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/02-quality-gated-stateful-kv-reuse/experiments/session-continuation-model-sanity-2026-06-03/transcript-format-cases.jsonl
```

## Bounded Full-Mode Probe

Run from DushyantPC:

```bat
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current
```

```bat
python benchmarks\flashcache_session_continuation_litmus.py --mode full --server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --model C:\Users\Dushyant\Documents\vault-mind\vault-mind-q5_k_m.gguf --ctx-size 32768 --predict 32 --prime-n-predict 0 --temperature 0.0 --timeout 90 --cache-dir benchmarks\session-continuation-litmus-cache\session-continuation-model-sanity-2026-06-03\vault-probe --output benchmarks\session-continuation-litmus-results\session-continuation-model-sanity-2026-06-03\vault-mind-default-full-probe.json
```

## Default Litmus

First attempt used a long cache path and preserved the failed raw JSON:

```bat
python benchmarks\flashcache_session_continuation_litmus.py --server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --model C:\Users\Dushyant\Documents\vault-mind\vault-mind-q5_k_m.gguf --ctx-size 32768 --predict 32 --prime-n-predict 0 --temperature 0.0 --timeout 120 --cache-dir benchmarks\session-continuation-litmus-cache\session-continuation-model-sanity-2026-06-03\vault-default --output benchmarks\session-continuation-litmus-results\session-continuation-model-sanity-2026-06-03\vault-mind-default-litmus.json
```

It produced Windows log-file path errors, so the output was renamed:

```bat
Move-Item -Force benchmarks\session-continuation-litmus-results\session-continuation-model-sanity-2026-06-03\vault-mind-default-litmus.json benchmarks\session-continuation-litmus-results\session-continuation-model-sanity-2026-06-03\vault-mind-default-litmus-long-cache-failed.json
```

Valid rerun with short cache path:

```bat
python benchmarks\flashcache_session_continuation_litmus.py --server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --model C:\Users\Dushyant\Documents\vault-mind\vault-mind-q5_k_m.gguf --ctx-size 32768 --predict 32 --prime-n-predict 0 --temperature 0.0 --timeout 120 --cache-dir benchmarks\session-continuation-litmus-cache\scms-vd --output benchmarks\session-continuation-litmus-results\session-continuation-model-sanity-2026-06-03\vault-mind-default-litmus.json
```

## Transcript-Format Litmus

```bat
python benchmarks\flashcache_session_continuation_litmus.py --cases ..\02-quality-gated-stateful-kv-reuse\experiments\session-continuation-model-sanity-2026-06-03\transcript-format-cases.jsonl --server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --model C:\Users\Dushyant\Documents\vault-mind\vault-mind-q5_k_m.gguf --ctx-size 32768 --predict 32 --prime-n-predict 0 --temperature 0.0 --timeout 120 --cache-dir benchmarks\session-continuation-litmus-cache\scms-vt --output benchmarks\session-continuation-litmus-results\session-continuation-model-sanity-2026-06-03\vault-mind-transcript-format-litmus.json
```

## Copy Raw Artifacts Back To macOS

```bash
cd /Users/dushyantgarg/Documents/Projects/ai-research-lab
mkdir -p research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results/session-continuation-model-sanity-2026-06-03 research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results/
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache/scms-vd research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache/
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache/scms-vt research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache/
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache/session-continuation-model-sanity-2026-06-03 research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache/
```

## Parse Results

```bash
cd /Users/dushyantgarg/Documents/Projects/ai-research-lab
for f in research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results/session-continuation-model-sanity-2026-06-03/*.json; do
  echo "== $f"
  jq '.summary.by_mode' "$f"
done
```
