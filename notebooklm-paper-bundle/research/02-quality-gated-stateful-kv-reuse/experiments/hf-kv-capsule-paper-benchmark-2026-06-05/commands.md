# Commands

## OpenSpec Validation

```bash
openspec validate run-hf-kv-capsule-paper-benchmark --type change --strict
openspec validate --all --strict
```

## Candidate Materialization

```bash
python3 research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/hf-kv-capsule-paper-benchmark-2026-06-05/raw/hf_kv_capsule_materialize.py --output-dir research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/hf-kv-capsule-paper-benchmark-2026-06-05 --ifeval-limit 100 --graphwalks-limit 100 --max-prompt-chars 12000 --profile default
python3 research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/hf-kv-capsule-paper-benchmark-2026-06-05/raw/hf_kv_capsule_materialize.py --output-dir research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/hf-kv-capsule-paper-benchmark-2026-06-05/expanded-ifeval-250 --ifeval-limit 250 --graphwalks-limit 100 --max-prompt-chars 12000 --profile default
```

## DushyantPC Model-Bearing Gates

All model-bearing commands used foreground SSH, Gemma 4 12B profile, b9512 CUDA llama.dll, and `--state-route auto` resolving to `seq_file`.

```powershell
py -3 research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\hf-kv-capsule-paper-benchmark-2026-06-05\raw\hf_kv_capsule_runner.py --mode preflight --model-profile gemma4-12b --ctx-size 4096 --predict 128 --state-route auto --output-stem preflight
py -3 research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\hf-kv-capsule-paper-benchmark-2026-06-05\raw\hf_kv_capsule_runner.py --mode hf-live-gate --cases research\01-ssd-native-inference-current\benchmarks\correctness-eval-inputs\hf-kv-capsule-paper-benchmark-2026-06-05\ifeval-candidates.jsonl --dataset ifeval --limit 10 --model-profile gemma4-12b --ctx-size 4096 --predict 256 --state-route auto --output-stem ifeval-live-gate
py -3 research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\hf-kv-capsule-paper-benchmark-2026-06-05\raw\hf_kv_capsule_runner.py --mode hf-live-gate --cases research\01-ssd-native-inference-current\benchmarks\correctness-eval-inputs\hf-kv-capsule-paper-benchmark-2026-06-05\graphwalks-parents-candidates.jsonl --dataset graphwalks --limit 10 --model-profile gemma4-12b --ctx-size 4096 --predict 256 --state-route auto --output-stem graphwalks-live-gate
py -3 research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\hf-kv-capsule-paper-benchmark-2026-06-05\raw\hf_kv_capsule_runner.py --mode calibrate --cases research\01-ssd-native-inference-current\benchmarks\correctness-eval-inputs\hf-kv-capsule-paper-benchmark-2026-06-05\ifeval-candidates.jsonl --dataset ifeval --limit 100 --model-profile gemma4-12b --ctx-size 4096 --predict 256 --state-route auto --output-stem ifeval-calibration
py -3 research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\hf-kv-capsule-paper-benchmark-2026-06-05\raw\hf_kv_capsule_runner.py --mode calibrate --cases research\01-ssd-native-inference-current\benchmarks\correctness-eval-inputs\hf-kv-capsule-paper-benchmark-2026-06-05\expanded-ifeval-250\ifeval-candidates-extra-100-249.jsonl --dataset ifeval --limit 150 --model-profile gemma4-12b --ctx-size 4096 --predict 256 --state-route auto --output-stem ifeval-calibration-extra-100-249
py -3 research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\hf-kv-capsule-paper-benchmark-2026-06-05\raw\hf_kv_capsule_runner.py --mode matrix --cases research\01-ssd-native-inference-current\benchmarks\correctness-eval-inputs\hf-kv-capsule-paper-benchmark-2026-06-05\selected-ifeval-50\ifeval-selected-50-candidates.jsonl --dataset ifeval --limit 50 --model-profile gemma4-12b --ctx-size 4096 --predict 256 --state-route auto --output-stem ifeval-selected-50-matrix
py -3 research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\hf-kv-capsule-paper-benchmark-2026-06-05\raw\hf_kv_capsule_runner.py --mode calibrate --cases research\01-ssd-native-inference-current\benchmarks\correctness-eval-inputs\hf-kv-capsule-paper-benchmark-2026-06-05\graphwalks-parents-candidates.jsonl --dataset graphwalks --limit 100 --model-profile gemma4-12b --ctx-size 4096 --predict 256 --state-route auto --output-stem graphwalks-calibration
```

The IFEval matrix was intentionally stopped after fresh-tail leakage fired.
