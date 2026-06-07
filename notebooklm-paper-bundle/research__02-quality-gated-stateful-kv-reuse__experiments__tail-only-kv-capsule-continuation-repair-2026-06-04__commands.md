# Commands

## Local runner checks

```bash
PYTHONPYCACHEPREFIX=/private/tmp/codex-pycache python3 -m py_compile research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-continuation-repair-2026-06-04/raw/tail_only_kv_capsule_repair.py
python3 research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-continuation-repair-2026-06-04/raw/tail_only_kv_capsule_repair.py --help
git check-ignore -v research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-continuation-repair-2026-06-04/raw research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-continuation-repair-2026-06-04/cache
```

## Remote sanity

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\Dushyant\Temp\remote_repair_sanity.ps1
```

Sanity outcome: remote compile/help/stale grep passed; raw/cache were ignored; sequence-file and sequence-memory exports were available.

## Preliminary smoke gate

```powershell
python C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\tail-only-kv-capsule-continuation-repair-2026-06-04\raw\tail_only_kv_capsule_repair.py --mode family1-smoke --state-route auto --out-dir C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\tail-only-kv-capsule-continuation-repair-2026-06-04\raw --cache-dir C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\tail-only-kv-capsule-continuation-repair-2026-06-04\cache
```

Exit code: `0`.

## Primary 30-case gate

```powershell
python C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\tail-only-kv-capsule-continuation-repair-2026-06-04\raw\tail_only_kv_capsule_repair.py --mode family1-30 --state-route auto --out-dir C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\tail-only-kv-capsule-continuation-repair-2026-06-04\raw --cache-dir C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\tail-only-kv-capsule-continuation-repair-2026-06-04\cache
```

Exit code: `0`.

## Validation commands

```bash
openspec validate repair-tail-only-kv-capsule-continuation --type change --strict
openspec validate --all --strict
```
