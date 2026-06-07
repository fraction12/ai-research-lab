# BFCL 10-Row Smoke Commands

## Materialize 10-row smoke packet

```bash
python3 research/01-ssd-native-inference-current/benchmarks/bfcl_code_mode_kv_adapter.py --category simple --category multiple --category parallel --category parallel_multiple --category irrelevance --per-category 2 --out research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw/bfcl-10row-smoke-control-packet.jsonl --summary-out research/02-quality-gated-stateful-kv-reuse/experiments/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/bfcl-10row-smoke-materialization-summary.json
```

## Run model smoke on DushyantPC

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 DushyantPC "cd C:\Users\Dushyant\Projects\ai-research-lab && python research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_model_loop_runner.py --packet research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw/bfcl-10row-smoke-control-packet.jsonl --out-dir research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw --cache-dir research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/cache --run-label bfcl-10row-smoke --state-route auto --predict 128 --max-steps 3 --max-repairs 1"
```

## Copy raw artifacts back

```bash
scp DushyantPC:"C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw/bfcl-10row-smoke-model-loop-records.jsonl" research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw/
scp DushyantPC:"C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw/bfcl-10row-smoke-model-loop-run-info.json" research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw/
```

## Validate local implementation

```bash
python3 -m py_compile research/01-ssd-native-inference-current/benchmarks/bfcl_code_mode_kv_adapter.py research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_model_loop_runner.py
python3 -m unittest research/01-ssd-native-inference-current/tests/test_code_mode_kv_capsule_agent_harness.py research/01-ssd-native-inference-current/tests/test_bfcl_code_mode_kv_adapter.py
openspec validate run-nonhandmade-code-mode-kv-agent-benchmark --type change --strict
openspec validate --all --strict
```

## Raw artifact hashes

- `records_sha256`: `1d3bbe3449855f0157f5509910a3871ff5860dfa3d2e03756d54d505debafd41`
- `run_info_sha256`: `3238518dacd699efd5801012e5b84f606458c2381663f2655672f45e487f0d98`
- `packet_sha256`: `0ED761508EEA4859FB893B1366C549373B5704E8E2EB47DF41F7D8086196E41D`
