# Execution Runbook

This is the operator handoff for the paper-grade Code-mode + KV capsule campaign.

## Source Of Truth

- Mac checkout: `/Volumes/MacSSD/Projects/ai-research-lab`
- DushyantPC execution checkout: `C:\ai\paper`
- Current prepared commit: `a0dd5069`
- OpenSpec change: `design-paper-grade-code-mode-kv-capsule-evaluation`

Use `C:\ai\paper` for campaign execution. The older DushyantPC checkout at `C:\Users\Dushyant\Projects\ai-research-lab` is dirty/detached historical state and should not be used for this campaign unless it is deliberately cleaned.

## Stage 0 Readiness

Run on DushyantPC:

```powershell
cd C:\ai\paper
python research/01-ssd-native-inference-current/benchmarks/paper_campaign_readiness.py
```

Expected:

- `ready: true`
- no blockers
- `execution-readiness.json` written under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/
```

Prompt-bearing BFCL readiness packets are written under ignored Track 01:

```text
research/01-ssd-native-inference-current/benchmarks/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/readiness-raw/
```

## Checkup

Run on DushyantPC:

```powershell
cd C:\ai\paper
python research/01-ssd-native-inference-current/benchmarks/paper_campaign_checkup.py
```

Expected:

- appends `periodic-checkups.jsonl`
- reports GPU status, active process state, latest model-loop record file if present, row/control counts, and stop-rule indicators
- does not mutate or restart the run

Before model execution starts, `no_model_loop_records_found` is expected.

## BFCL Candidate Packet

Initial paper-campaign candidate materialization should use supported BFCL categories first:

```powershell
cd C:\ai\paper
$raw = "research/01-ssd-native-inference-current/benchmarks/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/raw"
New-Item -ItemType Directory -Force $raw | Out-Null
python research/01-ssd-native-inference-current/benchmarks/bfcl_code_mode_kv_adapter.py `
  --category simple `
  --category multiple `
  --category parallel `
  --category parallel_multiple `
  --category irrelevance `
  --per-category 100 `
  --out "$raw\bfcl-candidate-control-packet.jsonl" `
  --summary-out "$raw\bfcl-candidate-materialization-summary.json"
```

This creates up to 500 BFCL cases and 3500 control records. The model run may be reduced before execution if the materialized source count is lower or if a smaller staged run is chosen.

## BFCL Model Run

Start with a bounded calibration run, not the full paper run, unless Sir explicitly asks for the full run immediately.

Example 10-row smoke:

```powershell
cd C:\ai\paper
$raw = "research/01-ssd-native-inference-current/benchmarks/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/raw"
$cache = "research/01-ssd-native-inference-current/benchmarks/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/cache"
python research/01-ssd-native-inference-current/benchmarks/bfcl_code_mode_kv_adapter.py `
  --category simple `
  --category multiple `
  --category parallel `
  --per-category 2 `
  --out "$raw\bfcl-smoke-control-packet.jsonl" `
  --summary-out "$raw\bfcl-smoke-materialization-summary.json"
python research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_model_loop_runner.py `
  --packet "$raw\bfcl-smoke-control-packet.jsonl" `
  --out-dir "$raw" `
  --cache-dir "$cache" `
  --run-label bfcl-paper-smoke `
  --model-profile gemma4-12b `
  --state-route auto `
  --predict 128 `
  --max-steps 3 `
  --max-repairs 1
```

After the smoke, run:

```powershell
python research/01-ssd-native-inference-current/benchmarks/paper_campaign_checkup.py --raw-dir "$raw"
```

## Stop Rules

Stop before broad execution if:

- readiness reports any blocker
- GPU is unavailable or saturated before launch
- duplicate Python/llama processes are active before launch
- BFCL materialization cannot produce all seven controls
- fresh-tail or wrong-capsule negative controls pass unexpectedly in a staged run
- native live append passes but restored capsule fails repeatedly
- parser/scorer repair dominates the run
- JSONL output stops advancing while a process remains active

## Current Known Caveats

- Windows does not currently have `openspec` or `pytest`; those validations are Mac-side.
- Gemma 4 emits thought/channel markers in simple `llama-completion` smoke. The scoring plan already treats this as calibration/protocol behavior, not as paper evidence.
- The full paper campaign is intentionally staged. Do not jump directly to a 500-row all-control run unless Sir explicitly asks for it.
