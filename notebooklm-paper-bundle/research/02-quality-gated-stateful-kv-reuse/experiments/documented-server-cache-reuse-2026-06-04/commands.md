# Commands

## OpenSpec

```bash
openspec validate probe-documented-server-cache-reuse --type change --strict
openspec validate --all --strict
```

## DushyantPC Run

Run from `C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current`:

```powershell
python benchmarks\documented-server-cache-reuse-2026-06-04\raw\run_documented_server_cache_reuse.py `
  --server-bin C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe `
  --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb `
  --ctx-size 32768 `
  --predict 32 `
  --prime-n-predict 0 `
  --temperature 0.0 `
  --timeout 300 `
  --seed 20260604 `
  --case-count 10 `
  --raw-dir benchmarks\documented-server-cache-reuse-2026-06-04\raw `
  --cache-dir benchmarks\documented-server-cache-reuse-2026-06-04\cache `
  --cases benchmarks\documented-server-cache-reuse-2026-06-04\raw\documented-cache-cases.jsonl `
  --responses benchmarks\documented-server-cache-reuse-2026-06-04\raw\documented-cache-responses.jsonl `
  --summary benchmarks\documented-server-cache-reuse-2026-06-04\raw\documented-cache-summary.json `
  --command-output benchmarks\documented-server-cache-reuse-2026-06-04\raw\documented-cache-command.json
```
