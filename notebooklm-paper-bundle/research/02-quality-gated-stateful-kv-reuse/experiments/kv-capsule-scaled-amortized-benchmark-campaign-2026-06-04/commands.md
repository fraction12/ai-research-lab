# KV Capsule Scaled Amortized Campaign Commands

## Local OpenSpec Validation

```bash
openspec validate run-kv-capsule-scaled-amortized-benchmark-campaign --type change --strict
openspec validate --all --strict
```

## Local Runner Sanity

```bash
PYTHONPYCACHEPREFIX=/tmp/kv-capsule-pycache python3 -m py_compile research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/kv_capsule_scaled_campaign.py
PYTHONDONTWRITEBYTECODE=1 python3 research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/kv_capsule_scaled_campaign.py --help
```

## DushyantPC Base Update

The PC checkout was clean but behind the required base. Because non-interactive `git fetch origin` could not authenticate on DushyantPC, the exact `1a35780` commit object was packed from the Mac worktree and imported into the PC checkout, then main was fast-forwarded locally:

```bash
git pack-objects --revs --stdout > /tmp/track02-family3-record.pack
scp /tmp/track02-family3-record.pack DushyantPC:C:/Users/Dushyant/Temp/track02-family3-record.pack
ssh DushyantPC 'cmd /c "cd /d C:\Users\Dushyant\Projects\ai-research-lab && git unpack-objects < C:\Users\Dushyant\Temp\track02-family3-record.pack && git merge --ff-only 1a35780839f2e3277dafe569aa64852e1c614365"'
```

## Remote Sync And Sanity

```bash
scp research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/kv_capsule_scaled_campaign.py DushyantPC:C:/Users/Dushyant/Temp/kv_capsule_scaled_campaign.py
scp research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/remote_sync_sanity.ps1 DushyantPC:C:/Users/Dushyant/Temp/remote_sync_sanity.ps1
ssh DushyantPC "powershell -NoProfile -ExecutionPolicy Bypass -File C:/Users/Dushyant/Temp/remote_sync_sanity.ps1"
```

Remote sanity confirmed the PC checkout was at `1a35780`, the raw path was ignored, help exposed only `smoke`, `token-smoke`, and `campaign`, and Phase 2 templates each had exactly one reusable prefix hash.

## Model-Bearing Run

```bash
scp research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/remote_run_campaign.ps1 DushyantPC:C:/Users/Dushyant/Temp/remote_run_campaign.ps1
ssh DushyantPC "powershell -NoProfile -ExecutionPolicy Bypass -File C:/Users/Dushyant/Temp/remote_run_campaign.ps1"
```

The PowerShell script ran:

```powershell
python C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/kv_capsule_scaled_campaign.py --mode campaign --phase1-row-sizes 25,100,250 --phase1-queries 10 --phase2-calibration-cases 20 --phase3-tasks 8
```

## Raw Copyback

```bash
scp -r 'DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/*' research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/
```
