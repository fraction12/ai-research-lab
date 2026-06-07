# Commands

Run from:

```bat
cd /d C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks
```

Profile/path check:

```bat
py -3 kv_capsule_profiles.py --profile gemma4-12b --check-paths
```

Remote syntax check:

```bat
py -3 -m py_compile kv_capsule_profiles.py tail-only-kv-capsule-continuation-repair-2026-06-04\raw\tail_only_kv_capsule_repair.py tail-only-kv-capsule-family2-structured-retrieval-scale-2026-06-04\raw\tail_only_kv_capsule_family2_scale.py
```

Family 1 smoke:

```bat
py -3 tail-only-kv-capsule-continuation-repair-2026-06-04\raw\tail_only_kv_capsule_repair.py --mode family1-smoke --model-profile gemma4-12b --ctx-size 4096 --predict 96 --state-route auto
```

Family 2 smoke:

```bat
py -3 tail-only-kv-capsule-family2-structured-retrieval-scale-2026-06-04\raw\tail_only_kv_capsule_family2_scale.py --mode family2-smoke --model-profile gemma4-12b --ctx-size 4096 --predict 96 --state-route auto --cases 3
```

Family 2 primary:

```bat
py -3 tail-only-kv-capsule-family2-structured-retrieval-scale-2026-06-04\raw\tail_only_kv_capsule_family2_scale.py --mode family2-30 --model-profile gemma4-12b --ctx-size 4096 --predict 96 --state-route auto > C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\tail-only-kv-capsule-gemma4-12b-replication-2026-06-04\raw\family2-30-console.log 2>&1
```

Local validations after committed profile update:

```bash
PYTHONPYCACHEPREFIX=/tmp/ai-research-lab-pycache python3 -m py_compile research/01-ssd-native-inference-current/benchmarks/kv_capsule_profiles.py
python3 -m unittest research/01-ssd-native-inference-current/tests/test_kv_capsule_profiles.py
openspec validate replicate-kv-capsule-gemma4-12b --type change --strict
```
