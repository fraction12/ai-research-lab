# KV Capsule Family 1 Semantic Gate Commands

## OpenSpec

```bash
openspec validate run-kv-capsule-family1-semantic-gate --type change --strict
openspec validate --all --strict
```

## Sync DushyantPC

```bash
git bundle create /tmp/track02-family1-gate.bundle 0bb44f5..HEAD
scp /tmp/track02-family1-gate.bundle DushyantPC:C:/Users/Dushyant/Projects/track02-family1-gate.bundle
ssh DushyantPC 'powershell -NoProfile -Command "cd C:\Users\Dushyant\Projects\ai-research-lab; git fetch C:\Users\Dushyant\Projects\track02-family1-gate.bundle HEAD:refs/remotes/bundle/family1-gate; git merge --ff-only refs/remotes/bundle/family1-gate"'
```

## Runner

The ignored raw runner was copied to DushyantPC and executed only in `--mode family1`:

```powershell
python research\01-ssd-native-inference-current\benchmarks\kv-capsule-family1-semantic-gate-2026-06-04\raw\kv_capsule_family1_gate.py `
  --mode family1 `
  --cases 3 `
  --predict 48 `
  --temperature 0.0 `
  --ctx-size 32768 `
  --n-gpu-layers -1 `
  --backend cuda_v13
```

## Copyback

```bash
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/family1-records.jsonl research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/family1-run-info.json research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/family1-console.txt research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/kv_capsule_family1_gate.py research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/
```
