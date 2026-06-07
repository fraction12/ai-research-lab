# Commands

Date: 2026-06-03

## macOS Local Tests

```bash
cd /Users/dushyantgarg/Documents/Projects/ai-research-lab/research/01-ssd-native-inference-current
python3 -m unittest tests.test_session_continuation_litmus
python3 benchmarks/flashcache_session_continuation_litmus.py --dry-run --output /tmp/session-litmus-dry.json
jq '.summary' /tmp/session-litmus-dry.json
```

## Sync Litmus Files To DushyantPC

```bash
cd /Users/dushyantgarg/Documents/Projects/ai-research-lab
COPYFILE_DISABLE=1 tar -czf /tmp/session-continuation-litmus-files.tgz .gitignore openspec/changes/define-session-continuation-litmus research/01-ssd-native-inference-current/benchmarks/flashcache_session_continuation_litmus.py research/01-ssd-native-inference-current/tests/test_session_continuation_litmus.py
scp /tmp/session-continuation-litmus-files.tgz dushyantpc:C:/Users/Dushyant/Projects/session-continuation-litmus-files.tgz
ssh dushyantpc "powershell -NoProfile -Command \"cd C:\\Users\\Dushyant\\Projects\\ai-research-lab; tar -xzf C:\\Users\\Dushyant\\Projects\\session-continuation-litmus-files.tgz; Remove-Item C:\\Users\\Dushyant\\Projects\\session-continuation-litmus-files.tgz\""
```

## DushyantPC Focused Test

```bat
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current
python -m unittest tests.test_session_continuation_litmus
```

## DushyantPC Model And Backend Probes

```bat
C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --version
```

```powershell
Get-Item C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\models\gpt-oss-20b-mxfp4.gguf | Select-Object FullName,Length,LastWriteTime | ConvertTo-Json
```

## DushyantPC Live Litmus

Run from:

```bat
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current
```

Command:

```bat
python benchmarks\flashcache_session_continuation_litmus.py --server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --ctx-size 32768 --predict 32 --prime-n-predict 0 --temperature 0.0 --timeout 240 --cache-dir benchmarks\session-continuation-litmus-cache\session-continuation-litmus-2026-06-03 --output benchmarks\session-continuation-litmus-results\session-continuation-litmus-2026-06-03\gpt-oss-20b-mxfp4-session-continuation-litmus.json
```

## Copy Raw Artifacts Back To macOS

```bash
cd /Users/dushyantgarg/Documents/Projects/ai-research-lab
mkdir -p research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results/session-continuation-litmus-2026-06-03 research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results/
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache/session-continuation-litmus-2026-06-03 research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache/
```

## Parse Result

```bash
cd /Users/dushyantgarg/Documents/Projects/ai-research-lab
jq '.summary' research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results/session-continuation-litmus-2026-06-03/gpt-oss-20b-mxfp4-session-continuation-litmus.json
jq -r '.records[] | [.case_id,.mode,.passed,.response,(.answer_parse_error // ""),(.error // "")] | @tsv' research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results/session-continuation-litmus-2026-06-03/gpt-oss-20b-mxfp4-session-continuation-litmus.json
```
