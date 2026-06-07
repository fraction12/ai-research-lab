# Commands

Commands ran on DushyantPC from:

```text
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current
```

## Compact Answer Main Condition

```powershell
python benchmarks\correctness-eval-results\compact-visible-evidence-repair-2026-06-04\raw\run_compact_visible_evidence_repair.py `
  --cases benchmarks\correctness-eval-inputs\compact-visible-evidence-repair-2026-06-04\graphwalks-two-compact-visible-evidence-cases.jsonl `
  --control hidden-prefix-compact-visible-evidence-tail `
  --server-bin C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe `
  --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb `
  --ctx-size 32768 `
  --predict 192 `
  --prime-n-predict 0 `
  --temperature 0.0 `
  --timeout 300 `
  --cache-dir benchmarks\correctness-eval-cache\compact-visible-evidence-repair-2026-06-04 `
  --responses benchmarks\correctness-eval-results\compact-visible-evidence-repair-2026-06-04\raw\hidden-prefix-compact-visible-evidence-tail-responses.jsonl `
  --scores benchmarks\correctness-eval-results\compact-visible-evidence-repair-2026-06-04\raw\hidden-prefix-compact-visible-evidence-tail-scores.json `
  --command-output benchmarks\correctness-eval-results\compact-visible-evidence-repair-2026-06-04\raw\hidden-prefix-compact-visible-evidence-tail-command.json
```

Result: `2/2`, mean score `1.0`.

No `increase_predict` diagnostic was run because the compact-answer main condition repaired both cases at the original `--predict 192` cap.
