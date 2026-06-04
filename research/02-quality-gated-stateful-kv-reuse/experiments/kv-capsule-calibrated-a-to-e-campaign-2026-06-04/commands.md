# Commands

## Local OpenSpec and Runner Checkpoint

```bash
openspec validate run-kv-capsule-calibrated-a-to-e-campaign --type change --strict
PYTHONPYCACHEPREFIX=/private/tmp/codex-pycache python3 -m py_compile research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/kv_capsule_calibrated_campaign.py
python3 research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/kv_capsule_calibrated_campaign.py --help
```

## PC Sync

```bash
git bundle create /private/tmp/track2-calibrated-a-to-e.bundle HEAD ^1a35780
scp /private/tmp/track2-calibrated-a-to-e.bundle DushyantPC:C:/Users/Dushyant/Temp/track2-calibrated-a-to-e.bundle
ssh DushyantPC 'powershell -NoProfile -Command "Set-Location ''C:/Users/Dushyant/Projects/ai-research-lab''; git fetch ''C:/Users/Dushyant/Temp/track2-calibrated-a-to-e.bundle'' HEAD; git merge --ff-only FETCH_HEAD"'
scp research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/kv_capsule_calibrated_campaign.py DushyantPC:C:/Users/Dushyant/Temp/kv_capsule_calibrated_campaign.py
```

## Remote Sanity

```powershell
python -m py_compile C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/kv_capsule_calibrated_campaign.py
python C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/kv_capsule_calibrated_campaign.py --help
git status --short --ignored -- research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw
```

## Model-Bearing Campaign

```powershell
python C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/kv_capsule_calibrated_campaign.py --mode campaign --predict 16 --retrieval-row-sizes 10,25,50,100,250 --retrieval-queries 10 --min-exact-or-normalized-for-promotion 10 --agent-context-tasks 8 --run-agent-context
```

Result: `ExitCode: 0`; campaign stopped after Phase A because all six 10-row full-visible calibration variants failed promotion.

## Copyback

```bash
scp -r DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/ research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/
```
