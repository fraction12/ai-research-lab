# Commands

Local validation:

```bash
python3 -m py_compile research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_agent_harness.py research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_model_loop_runner.py
python3 -m unittest research/01-ssd-native-inference-current/tests/test_code_mode_kv_capsule_agent_harness.py
openspec validate probe-code-mode-kv-capsule-agent-harness --type change --strict
openspec validate --all --strict
```

Packet generation:

```bash
python3 research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_agent_harness.py --mode dry-run --stage twelve-case
python3 research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_agent_harness.py --mode dry-run --stage thirty-case
```

Remote 30-case Gemma 4 run on DushyantPC:

```powershell
py -3 research\01-ssd-native-inference-current\benchmarks\code_mode_kv_capsule_model_loop_runner.py `
  --packet C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\code-mode-kv-capsule-agent-harness-2026-06-05\raw\thirty-case-model-control-packet.jsonl `
  --out-dir C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\code-mode-kv-capsule-agent-harness-2026-06-05\raw `
  --cache-dir C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\code-mode-kv-capsule-agent-harness-2026-06-05\cache `
  --run-label thirty-case-v9 `
  --state-route auto
```

Raw outputs are intentionally under ignored Track 01 benchmark paths.
