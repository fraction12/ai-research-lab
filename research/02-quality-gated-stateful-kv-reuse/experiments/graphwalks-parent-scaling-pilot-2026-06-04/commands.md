# Commands

## Build deterministic 50-case cohort

```powershell
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current
python benchmarks\correctness-eval-results\graphwalks-parent-scaling-pilot-2026-06-04\raw\run_graphwalks_parent_scaling_pilot.py build-cases `
  --case-count 50 `
  --cases-output benchmarks\correctness-eval-inputs\graphwalks-parent-scaling-pilot-2026-06-04\graphwalks-parents-50-cases.jsonl `
  --evidence-output benchmarks\correctness-eval-inputs\graphwalks-parent-scaling-pilot-2026-06-04\evidence-slices.json `
  --build-manifest benchmarks\correctness-eval-inputs\graphwalks-parent-scaling-pilot-2026-06-04\build-manifest.json
```

## Run deterministic first-10 stop-rule slice

```powershell
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current
python benchmarks\correctness-eval-results\graphwalks-parent-scaling-pilot-2026-06-04\raw\run_graphwalks_parent_scaling_pilot.py run-matrix `
  --cases benchmarks\correctness-eval-inputs\graphwalks-parent-scaling-pilot-2026-06-04\graphwalks-parents-50-cases.jsonl `
  --case-limit 10 `
  --stop-rule "full 50x5 matrix estimated multi-hour from prior GPT-OSS runs; executing deterministic first-10 slice across all five controls" `
  --server-bin C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe `
  --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb `
  --ctx-size 32768 `
  --predict 192 `
  --prime-n-predict 0 `
  --temperature 0.0 `
  --timeout 300 `
  --cache-dir benchmarks\correctness-eval-cache\graphwalks-parent-scaling-pilot-2026-06-04 `
  --responses benchmarks\correctness-eval-results\graphwalks-parent-scaling-pilot-2026-06-04\raw\pilot-first10-five-control-responses.jsonl `
  --scores benchmarks\correctness-eval-results\graphwalks-parent-scaling-pilot-2026-06-04\raw\pilot-first10-five-control-scores.json `
  --command-output benchmarks\correctness-eval-results\graphwalks-parent-scaling-pilot-2026-06-04\raw\pilot-first10-five-control-command.json
```
