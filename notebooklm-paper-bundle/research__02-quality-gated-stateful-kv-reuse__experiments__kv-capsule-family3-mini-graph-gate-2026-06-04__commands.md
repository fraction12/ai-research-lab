# KV Capsule Family 3 Mini-Graph Gate Commands

## OpenSpec

```bash
openspec validate run-kv-capsule-family3-mini-graph-gate --type change --strict
openspec validate --all --strict
```

## Local Runner Sanity

```bash
python3 -m py_compile research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/kv_capsule_family3_gate.py
grep -n 'ap.add_argument("--mode"' -A12 research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/kv_capsule_family3_gate.py
rg -n 'args\.mode == "(server|bridge|family1|family2)"|return run_(server|bridge|family1|family2)|choices=\["smoke", "token-smoke", "family[12]"\]|kv-capsule-family[12]|family[12]-records|family[12]-run-info|run_family[12]_gate|GraphWalks|broad-benchmark|Family 2|family2' research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/kv_capsule_family3_gate.py || true
```

## Sync DushyantPC

```bash
git bundle create /tmp/track02-family3-gate.bundle 3036c39..HEAD
scp /tmp/track02-family3-gate.bundle DushyantPC:C:/Users/Dushyant/Projects/track02-family3-gate.bundle
ssh DushyantPC 'powershell -NoProfile -Command "cd C:/Users/Dushyant/Projects/ai-research-lab; git fetch C:/Users/Dushyant/Projects/track02-family3-gate.bundle HEAD:refs/remotes/bundle/family3-gate; git merge --ff-only refs/remotes/bundle/family3-gate"'
scp research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/kv_capsule_family3_gate.py DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/kv_capsule_family3_gate.py
```

## Remote Runner Sanity

```powershell
cd C:/Users/Dushyant/Projects/ai-research-lab
python -m py_compile research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/kv_capsule_family3_gate.py
python research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/kv_capsule_family3_gate.py --help
```

`--help` exposed only `--mode {smoke,token-smoke,family3}`. A stale-string grep script returned false for reachable `bridge`, `family1`, `family2`, old Family 2 raw path/output filenames, `GraphWalks`, and `broad-benchmark` strings.

## Model-Bearing Run

The ignored raw runner was executed once in `--mode family3`:

```powershell
cd C:/Users/Dushyant/Projects/ai-research-lab
python research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/kv_capsule_family3_gate.py `
  --mode family3 `
  --cases 5 `
  --predict 48 `
  --temperature 0.0 `
  --ctx-size 32768 `
  --n-gpu-layers -1 `
  --backend cuda_v13
```

The runner stopped after the Stage A full-visible guard failed and did not run fresh-tail, live-append, restored-capsule, Stage B, GraphWalks, or broad benchmark work.

## Copyback

```bash
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/family3-records.jsonl research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/family3-run-info.json research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/family3-console.txt research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/kv_capsule_family3_gate.py research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/
```
