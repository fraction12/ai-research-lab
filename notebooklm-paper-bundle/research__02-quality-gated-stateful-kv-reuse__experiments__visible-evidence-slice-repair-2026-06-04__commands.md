# Commands

Commands run on DushyantPC from:

```text
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current
```

## Input Artifacts

```text
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\correctness-eval-inputs\visible-evidence-slice-repair-2026-06-04\graphwalks-six-selected-cases.jsonl
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\correctness-eval-inputs\visible-evidence-slice-repair-2026-06-04\graphwalks-six-visible-evidence-slice-cases.jsonl
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\correctness-eval-inputs\visible-evidence-slice-repair-2026-06-04\evidence-slices.json
```

## Hidden Prefix Session Tail

```powershell
python benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\run_visible_evidence_repair.py `
  --cases benchmarks\correctness-eval-inputs\visible-evidence-slice-repair-2026-06-04\graphwalks-six-selected-cases.jsonl `
  --control hidden-prefix-session-tail `
  --server-bin C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe `
  --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb `
  --ctx-size 32768 `
  --predict 192 `
  --prime-n-predict 0 `
  --temperature 0.0 `
  --timeout 300 `
  --cache-dir benchmarks\correctness-eval-cache\visible-evidence-slice-repair-2026-06-04 `
  --responses benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\hidden-prefix-session-tail-responses.jsonl `
  --scores benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\hidden-prefix-session-tail-scores.json `
  --command-output benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\hidden-prefix-session-tail-command.json
```

Result: `0/6`, mean score `0.0`.

## Hidden Prefix With Visible Evidence Tail

```powershell
python benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\run_visible_evidence_repair.py `
  --cases benchmarks\correctness-eval-inputs\visible-evidence-slice-repair-2026-06-04\graphwalks-six-visible-evidence-slice-cases.jsonl `
  --control hidden-prefix-visible-evidence-tail `
  --server-bin C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe `
  --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb `
  --ctx-size 32768 `
  --predict 192 `
  --prime-n-predict 0 `
  --temperature 0.0 `
  --timeout 300 `
  --cache-dir benchmarks\correctness-eval-cache\visible-evidence-slice-repair-2026-06-04 `
  --responses benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\hidden-prefix-visible-evidence-tail-responses.jsonl `
  --scores benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\hidden-prefix-visible-evidence-tail-scores.json `
  --command-output benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\hidden-prefix-visible-evidence-tail-command.json
```

Result: `4/6`, mean score `0.6666666666666666`.

## Notes

The raw runner used GPT-OSS-specific llama.cpp flags: `--jinja`, `--reasoning off`, `--reasoning-budget 0`, `--no-mmap`, and `--flash-attn auto`. No Track 01 harness code was modified.
