# BFCL Official KV/PTI Leaderboard Lane

Date: 2026-06-07

Goal: turn the KV-capsule + programmatic tool-interface harness into a BFCL V4-compatible run lane that can produce reproducible result artifacts for official evaluation and, if accepted by BFCL maintainers, leaderboard submission.

This lane is separate from the paper-selected 100-case cohort. Do not mix these artifacts into paper claims until an official-protocol run has completed and been evaluated.

## What This Lane Does

- Uses the pinned BFCL package path: `bfcl-eval==2025.12.17`.
- Stages official BFCL V4 data from the installed `bfcl_eval/data` directory.
- Materializes our full control packet shape with BFCL V4 cases.
- Runs the existing model-bearing KV/PTI harness through `code_mode_kv_capsule_model_loop_runner.py`.
- Exports prompt-mode BFCL result files under:
  `official-export/result/gemma4-kv-capsule-pti/.../BFCL_v4_<category>_result.json`
- Writes a sidecar trace under:
  `official-export/kv_pti_sidecar/`
- Writes `BFCL_OFFICIAL_LANE_MANIFEST.json` with the required disclosure that this is a custom hidden-state runtime, not a vanilla model invocation.

## Why This Is Not A Submission Yet

BFCL's evaluator expects known model keys and handlers. Our runtime is a custom inference harness: Gemma 4 with stable BFCL function catalogs loaded into restored llama.cpp KV/sequence state, plus a compact programmatic tool interface. For a public leaderboard entry, we must disclose that runtime and may need BFCL maintainer acceptance or a small custom handler overlay so the evaluator can decode our pre-generated prompt-mode outputs.

## Setup

```bash
python3 -m venv .venv-bfcl
. .venv-bfcl/bin/activate
python -m pip install 'bfcl-eval==2025.12.17'
```

The BFCL package currently exposes BFCL V4 data and writes results under a `result/` tree. The runner records the observed installed package version in `BFCL_OFFICIAL_LANE_MANIFEST.json`.

If the package has already been unpacked elsewhere, pass its data directory explicitly:

```bash
python3 research/01-ssd-native-inference-current/benchmarks/bfcl_official_runner.py prepare \
  --bfcl-data-dir /path/to/bfcl_eval/data \
  --per-category 1
```

## Prepare A Small Official Packet

Smoke materialization:

```bash
python3 research/01-ssd-native-inference-current/benchmarks/bfcl_official_runner.py prepare \
  --per-category 1
```

This writes:

- `raw/gemma4-kv-capsule-pti-bfcl-v4-control-packet.jsonl`
- `raw/gemma4-kv-capsule-pti-bfcl-v4-materialization-summary.json`
- `raw/gemma4-kv-capsule-pti-bfcl-v4-compatibility-audit.json`
- `BFCL_OFFICIAL_LANE_MANIFEST.json`

## Dry-Run The Model Command

```bash
python3 research/01-ssd-native-inference-current/benchmarks/bfcl_official_runner.py run \
  --per-category 1 \
  --case-limit 2 \
  --dry-run
```

## Run A Smoke

```bash
python3 research/01-ssd-native-inference-current/benchmarks/bfcl_official_runner.py run \
  --per-category 1 \
  --case-limit 2 \
  --controls code_mode_restored_kv_capsule \
  --model-profile gemma4-12b
```

## Export BFCL-Style Result Files

After a run creates `raw/gemma4-kv-capsule-pti-bfcl-v4-model-loop-records.jsonl`:

```bash
python3 research/01-ssd-native-inference-current/benchmarks/bfcl_official_runner.py export \
  --records research/02-quality-gated-stateful-kv-reuse/experiments/bfcl-official-kv-pti-leaderboard-lane/raw/gemma4-kv-capsule-pti-bfcl-v4-model-loop-records.jsonl
```

The exporter converts recorded BFCL calls into BFCL prompt-mode Python-call strings such as:

```text
[calculate_triangle_area(base=10, height=5)]
```

Raw JSON calls, hashes, source provenance, capsule metadata, and local scorer output remain in the sidecar trace.

## Full Candidate Run

Start with non-live categories:

```bash
python3 research/01-ssd-native-inference-current/benchmarks/bfcl_official_runner.py all \
  --category simple_python \
  --category simple_java \
  --category simple_javascript \
  --category multiple \
  --category parallel \
  --category parallel_multiple \
  --category irrelevance \
  --per-category 999999 \
  --controls code_mode_restored_kv_capsule \
  --model-profile gemma4-12b
```

Then extend to live, multi-turn, web-search, and memory categories only after the non-live lane passes local sanity checks.

## Official Evaluation Handoff

The manifest prints a suggested command, but the likely final path is:

1. Register `gemma4-kv-capsule-pti` as a prompt-mode custom model key or ask BFCL maintainers how they want custom pre-generated result files submitted.
2. Point BFCL at `official-export/result/`.
3. Run `bfcl evaluate` against the categories present.
4. Attach the manifest and sidecar trace when discussing leaderboard eligibility.

## Submission Disclosure

Any submission or paper mention must state:

- Same local Gemma 4 model.
- Non-standard runtime: restored llama.cpp KV/sequence-state capsule.
- Stable BFCL tool/function catalog loaded in the hidden prefix.
- Task tail evaluated through a programmatic tool interface.
- Official result files contain BFCL prompt-mode call strings exported from the recorded runtime calls.

This is a custom inference-system submission, not a vanilla Gemma 4 model result.
