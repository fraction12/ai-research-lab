## Context

Track 02 is investigating quality-gated persistent KV/session reuse for local agent loops. The six-case GraphWalks lane exists because the original 2026-06-03 parity run found selected cases where full prompt passed and session-tail failed. Since then, the lower-level GPT-OSS path has produced a sharper signal: a pinned Harmony full-prompt baseline passed 4/6, final-only repair failed on the two misses, and a verified incoming-edge evidence control passed 6/6.

The next question is not whether GraphWalks is broadly solved. It is whether the hidden-prefix/session-tail path can recover correctness when a small visible evidence slice is recomputed or extracted from the hidden prefix and supplied with the tail.

The first visible-evidence repair run repaired four of the six cases. The two remaining failures, `graphwalks-16` and `graphwalks-19`, saw the correct extracted evidence but generated verbose truncated JSON at the `--predict 192` cap. The next focused follow-up tests whether those failures are only prompt-protocol / verbosity failures.

## Goals / Non-Goals

**Goals:**

- Run the next focused repair test only on the six fixed GraphWalks cases.
- Compare hidden-prefix/session-tail against hidden-prefix plus a small visible extracted evidence slice.
- Preserve exact model, quantization, runner, hardware, backend version, commands, prompts, hashes, raw outputs, timing, token counts, evidence-size metrics, and failure classifications.
- Measure correctness, prompt tokens, prompt time, visible evidence bytes, visible evidence edge count, and visible evidence tokens where practical.
- Interpret the control as role-aware context compilation / selective recompute.
- Run a two-case compact-answer follow-up for `graphwalks-16` and `graphwalks-19` with the same extracted evidence content and the same hidden-prefix mechanics.

**Non-Goals:**

- No broad GraphWalks, IFEval, MRCR, or mixed benchmark runs.
- No paper-facing prevalence claim from this six-case result.
- No use of the vault mind experimental model.
- No Track 01 harness modification unless current commands and local case composition cannot express the repair control.
- No claim that a visible evidence slice is pure KV reuse.
- No evidence extraction change in the compact-answer follow-up.

## Decisions

### Decision 1: Use the imported edge-evidence result as the positive control

The starting control is:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/gptoss-edge-evidence-2026-06-04/
```

It records the verified incoming-edge evidence control that passed 6/6 and the immediate lower-level GPT-OSS baseline context. This should be referenced, not rerun, unless the next execution requires a fresh same-day sanity check.

Alternative considered: treat the 6/6 result as a new benchmark. Rejected because the control is oracle-like and task-specific; it only proves that small visible evidence is sufficient for these cases.

### Decision 2: Keep the repair comparison paired by case

Each case should produce at least these control records:

| Control id | Prompt state | Visible evidence | Purpose |
| --- | --- | --- | --- |
| `hidden_prefix_session_tail` | Restored hidden stable prefix plus tail-only request | none | Measures current lower-level session-tail correctness and prompt cost. |
| `hidden_prefix_visible_evidence_tail` | Same restored hidden stable prefix plus tail request | extracted incoming-edge slice | Tests whether a small visible slice repairs hidden-prefix correctness. |
| `full_visible_reference` | Full visible graph prompt | full graph | Reference correctness and prompt-cost anchor; can reuse pinned baseline if compatible. |
| `verified_edge_evidence_control` | Small visible evidence prompt | verified incoming-edge slice | Imported positive control, not a general benchmark. |

The primary comparison is `hidden_prefix_visible_evidence_tail` minus `hidden_prefix_session_tail` for correctness, prompt tokens, and prompt time.

### Decision 3: Extract evidence from the stable prefix and operation, not from the answer label

For GraphWalks `parents` cases, the repair slice should be the incoming edge lines matching the operation target, extracted from the stable graph prefix. The extraction input is the hidden graph text plus the requested target node. The implementation must not read the reference answer nodes to build the repair slice, except in a separately labeled oracle-control path.

Alternative considered: keep using verified answer-derived edges. Rejected for the repair test because it would be a positive oracle, not a plausible repair mechanism.

### Decision 4: Track evidence-size metrics separately from total prompt metrics

The repair summary must record:

- `prompt_n`, `prompt_ms`, `predicted_n`, `predicted_ms`, and `latency_ms` for each generated response.
- `visible_evidence_edge_count`, `visible_evidence_bytes`, and `visible_evidence_tokens` for the extracted slice.
- `hidden_prefix_bytes`, `tail_bytes`, `tail_hash`, `visible_evidence_hash`, and `composed_prompt_hash`.
- Slot setup and restore telemetry when the control uses hidden session state.

Rationale: a correctness repair that adds too much visible context may erase the benefit of hidden-prefix/session reuse.

### Decision 5: Store prompt-bearing artifacts locally and summaries in Track 02

Prompt-bearing local artifacts should live under ignored Track 01 benchmark paths:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/visible-evidence-slice-repair-2026-06-04/
research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/visible-evidence-slice-repair-2026-06-04/raw/
research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/visible-evidence-slice-repair-2026-06-04/
```

Committed Track 02 summaries should live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/visible-evidence-slice-repair-2026-06-04/
```

Expected committed files:

```text
README.md
summary.json
artifact-manifest.json
model-info.json
commands.md
failure-classifications.json
evidence-slices.json
```

### Decision 6: Use GPT-OSS lower-level path only

The next test should use the pinned GPT-OSS-compatible llama.cpp path on DushyantPC:

```text
C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe
C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb
```

The model hash, runner hash, and command line must be preserved exactly in the output artifacts.

### Decision 7: Test compact answer protocol before increasing predict

For `graphwalks-16` and `graphwalks-19`, the next main repair condition is `hidden_prefix_compact_visible_evidence_tail`: the same hidden prefix, the same extracted edge lines, and a tail that strongly instructs GPT-OSS to output only the compact final node list in the JSON `answer` string with no explanation.

Rationale: the previous visible-evidence failures contained the right evidence but failed by verbose truncated output. A compact prompt-only repair is the smallest test of whether the remaining error is prompt protocol rather than model weakness or evidence extraction.

An `increase_predict` condition may run only after the compact-answer condition and must be labeled diagnostic. It is not the main repair result because it changes the token budget rather than the prompt protocol.

## Proposed Commands

These are the proposed command shapes for the repair execution. They are not run by this OpenSpec creation step.

Prepare or verify the six-case input bundle on DushyantPC:

```powershell
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current

python benchmarks\flashcache_correctness_eval.py sample `
  --dataset graphwalks `
  --limit 20 `
  --max-prompt-chars 5000 `
  --output benchmarks\correctness-eval-inputs\visible-evidence-slice-repair-2026-06-04\graphwalks-20-candidates.jsonl
```

Run or reuse hidden-prefix/session-tail baseline:

```powershell
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current

python benchmarks\flashcache_correctness_eval.py run `
  --cases benchmarks\correctness-eval-inputs\visible-evidence-slice-repair-2026-06-04\graphwalks-six-selected-cases.jsonl `
  --mode session-tail `
  --answer-protocol json-answer `
  --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb `
  --server-bin C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe `
  --ctx-size 32768 `
  --predict 192 `
  --temperature 0.0 `
  --cache-dir benchmarks\correctness-eval-cache\visible-evidence-slice-repair-2026-06-04\hidden-prefix-session-tail `
  --output benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\hidden-prefix-session-tail-responses.jsonl `
  --score `
  --score-output benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\hidden-prefix-session-tail-scores.json
```

Run hidden-prefix plus visible extracted evidence slice:

```powershell
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current

python benchmarks\flashcache_correctness_eval.py run `
  --cases benchmarks\correctness-eval-inputs\visible-evidence-slice-repair-2026-06-04\graphwalks-six-visible-evidence-slice-cases.jsonl `
  --mode session-tail `
  --answer-protocol json-answer `
  --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb `
  --server-bin C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe `
  --ctx-size 32768 `
  --predict 192 `
  --temperature 0.0 `
  --cache-dir benchmarks\correctness-eval-cache\visible-evidence-slice-repair-2026-06-04\hidden-prefix-visible-evidence-tail `
  --output benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\hidden-prefix-visible-evidence-tail-responses.jsonl `
  --score `
  --score-output benchmarks\correctness-eval-results\visible-evidence-slice-repair-2026-06-04\raw\hidden-prefix-visible-evidence-tail-scores.json
```

If the current runner cannot compose `graphwalks-six-visible-evidence-slice-cases.jsonl` without changing Track 01 code, first record the gap in the Track 02 experiment notes, then make the smallest harness change necessary under a follow-on approval.

Run compact-answer visible evidence repair on the two remaining failures:

```powershell
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current

python benchmarks\correctness-eval-results\compact-visible-evidence-repair-2026-06-04\raw\run_compact_visible_evidence_repair.py `
  --cases benchmarks\correctness-eval-inputs\compact-visible-evidence-repair-2026-06-04\graphwalks-two-compact-visible-evidence-cases.jsonl `
  --control hidden-prefix-compact-visible-evidence-tail `
  --server-bin C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe `
  --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb `
  --ctx-size 32768 `
  --predict 192 `
  --prime-n-predict 0 `
  --temperature 0.0 `
  --timeout 300 `
  --cache-dir benchmarks\correctness-eval-cache\compact-visible-evidence-repair-2026-06-04 `
  --responses benchmarks\correctness-eval-results\compact-visible-evidence-repair-2026-06-04\raw\hidden-prefix-compact-visible-evidence-tail-responses.jsonl `
  --scores benchmarks\correctness-eval-results\compact-visible-evidence-repair-2026-06-04\raw\hidden-prefix-compact-visible-evidence-tail-scores.json `
  --command-output benchmarks\correctness-eval-results\compact-visible-evidence-repair-2026-06-04\raw\hidden-prefix-compact-visible-evidence-tail-command.json
```

## Risks / Trade-offs

- Evidence extraction accidentally uses answer labels -> require extraction from graph prefix and requested target; label any oracle control separately.
- Visible evidence repairs correctness but erases prompt savings -> report token/time overhead and do not call it a cache win.
- Hidden-prefix/session-tail does not reproduce the earlier failure on the pinned lower-level path -> classify the result as backend/protocol drift and use it as the new baseline rather than forcing old labels.
- Current harness cannot express the exact prompt state -> avoid broad edits; add only a small case-composition or run-mode surface if needed.
- Six cases pass -> still no general benchmark claim.
- Compact-answer follow-up passes both remaining cases -> report the chain as `hidden-prefix 0/6 -> visible evidence 4/6 -> compact visible evidence 6/6` for the focused six-case cohort only.
- Compact-answer follow-up does not pass both remaining cases -> classify the remaining issue without broadening to a benchmark.

## Migration Plan

No migration is required. This change defines and prepares a focused experiment. After approval, execute the DushyantPC commands, import summaries into the planned Track 02 directory, classify failures, and validate any harness changes with focused tests plus root OpenSpec validation.

## Open Questions

- Can the visible evidence slice be expressed entirely through local case composition, or does the runner need a minimal mode for tail evidence while preserving hidden prefix state?
- Should the imported `verified_edge_evidence_control` be rerun after the repair test for same-session timing comparability, or is the recorded 6/6 control enough?
- How should evidence extraction be generalized beyond GraphWalks `parents` without turning this six-case repair into a broad benchmark?
