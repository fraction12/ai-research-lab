# KV Capsule Visible Baseline Rescue Commands

## Scope

Campaign: `kv-capsule-visible-baseline-rescue-2026-06-04`
PC checkout commit during run: `c02cde6`
Raw prompt-bearing artifacts stayed under the ignored Track 01 raw path.

## Local Gates

```bash
openspec validate run-kv-capsule-visible-baseline-rescue --type change --strict
PYTHONPYCACHEPREFIX=/private/tmp/codex-pycache python3 -m py_compile research/01-ssd-native-inference-current/benchmarks/kv-capsule-visible-baseline-rescue-2026-06-04/raw/kv_capsule_visible_baseline_rescue.py
python3 research/01-ssd-native-inference-current/benchmarks/kv-capsule-visible-baseline-rescue-2026-06-04/raw/kv_capsule_visible_baseline_rescue.py --help
```

## Remote Campaign Command

```powershell
python C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-visible-baseline-rescue-2026-06-04/raw/kv_capsule_visible_baseline_rescue.py --mode campaign --ctx-size 32768 --required-scales 1,3,5,10 --stretch-scales 15,25 --stretch-queries 10
```

## Copyback

```bash
scp -r DushyantPC:'C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-visible-baseline-rescue-2026-06-04/raw/*' research/01-ssd-native-inference-current/benchmarks/kv-capsule-visible-baseline-rescue-2026-06-04/raw/
```

## Validation After Packaging

```bash
openspec validate run-kv-capsule-visible-baseline-rescue --type change --strict
openspec validate --all --strict
```
