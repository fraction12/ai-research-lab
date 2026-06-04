# KV Capsule Family 2 Structured-Retrieval Gate Commands

## OpenSpec

```bash
openspec validate run-kv-capsule-family2-structured-retrieval-gate --type change --strict
openspec validate --all --strict
```

## Local Runner Sanity

```bash
python3 -m py_compile research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/kv_capsule_family2_gate.py
grep -n 'ap.add_argument("--mode"' -A12 research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/kv_capsule_family2_gate.py
rg -n 'args\.mode == "(bridge|family1)"|return run_bridge|return run_family1|choices=\["smoke", "token-smoke", "family1"\]|kv-capsule-family1-semantic-gate|family1-records|family1-run-info|GraphWalks|broad-benchmark' research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/kv_capsule_family2_gate.py || true
```

## Sync DushyantPC

```bash
git bundle create /tmp/track02-family2-gate.bundle 1081b82..HEAD
scp /tmp/track02-family2-gate.bundle DushyantPC:C:/Users/Dushyant/Projects/track02-family2-gate.bundle
ssh DushyantPC 'powershell -NoProfile -Command "cd C:/Users/Dushyant/Projects/ai-research-lab; git fetch C:/Users/Dushyant/Projects/track02-family2-gate.bundle HEAD:refs/remotes/bundle/family2-gate; git merge --ff-only refs/remotes/bundle/family2-gate"'
scp research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/kv_capsule_family2_gate.py DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/kv_capsule_family2_gate.py
```

## Remote Runner Sanity

```powershell
cd C:/Users/Dushyant/Projects/ai-research-lab
python -m py_compile research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/kv_capsule_family2_gate.py
python research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/kv_capsule_family2_gate.py --help
```

`--help` exposed only `--mode {smoke,token-smoke,family2}`. A stale-string grep script returned false for reachable `bridge`, `family1`, old Family 1 raw filenames, `GraphWalks`, and `broad-benchmark` strings.

## Model-Bearing Run

The ignored raw runner was executed once in `--mode family2`:

```powershell
cd C:/Users/Dushyant/Projects/ai-research-lab
python research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/kv_capsule_family2_gate.py `
  --mode family2 `
  --cases 5 `
  --predict 48 `
  --temperature 0.0 `
  --ctx-size 32768 `
  --n-gpu-layers -1 `
  --backend cuda_v13
```

A shell quoting mistake in the wrapper affected only console redirection setup, not the Python invocation. The runner wrote `family2-records.jsonl` and `family2-run-info.json` to its default Family 2 raw path; the console log was copied into that raw directory afterward.

## Copyback

```bash
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/family2-records.jsonl research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/family2-run-info.json research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/family2-console.txt research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/
scp DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/kv_capsule_family2_gate.py research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/
```
