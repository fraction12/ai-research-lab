# Commands

## OpenSpec

```bash
openspec validate probe-hidden-prefix-semantic-continuation --type change --strict
openspec validate --all --strict
```

## DushyantPC Run

Run from `C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current`:

```powershell
python benchmarks\hidden-prefix-semantic-continuation-2026-06-04\raw\run_hidden_prefix_semantic_continuation.py `
  --server-bin C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe `
  --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb `
  --ctx-size 32768 `
  --predict 32 `
  --prime-n-predict 0 `
  --temperature 0.0 `
  --timeout 300 `
  --seed 20260604 `
  --codeword-count 10 `
  --kv-count 20 `
  --cache-dir benchmarks\hidden-prefix-semantic-continuation-2026-06-04\cache `
  --cases benchmarks\hidden-prefix-semantic-continuation-2026-06-04\raw\semantic-continuation-cases.jsonl `
  --responses benchmarks\hidden-prefix-semantic-continuation-2026-06-04\raw\semantic-continuation-responses.jsonl `
  --summary benchmarks\hidden-prefix-semantic-continuation-2026-06-04\raw\semantic-continuation-summary.json `
  --failure-classifications benchmarks\hidden-prefix-semantic-continuation-2026-06-04\raw\semantic-continuation-failure-classifications.json `
  --command-output benchmarks\hidden-prefix-semantic-continuation-2026-06-04\raw\semantic-continuation-command.json
```

The runner was manually stopped after the 10-codeword gate. The raw response file contains 31 lines; the one `kv-01` full-visible stray record is excluded from this analysis.

## Import

```bash
scp 'DushyantPC:/C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/hidden-prefix-semantic-continuation-2026-06-04/raw/semantic-continuation-*' research/01-ssd-native-inference-current/benchmarks/hidden-prefix-semantic-continuation-2026-06-04/raw/
```
