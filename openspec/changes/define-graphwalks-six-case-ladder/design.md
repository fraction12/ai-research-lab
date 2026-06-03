## Context

Track 02 is the main paper candidate: quality-gated persistent KV reuse for local agent loops. The source evidence is the 2026-06-03 Flashcache correctness parity run in Track 01, where full prompt selected 42 passing cases and session-tail passed 31/42 overall but 0/6 selected GraphWalks cases.

The six focused cases are:

| Case | Dataset | Source evidence |
| --- | --- | --- |
| `graphwalks-6` | `openai/graphwalks` | `flashcache-correctness-parity-2026-06-03` |
| `graphwalks-9` | `openai/graphwalks` | `flashcache-correctness-parity-2026-06-03` |
| `graphwalks-11` | `openai/graphwalks` | `flashcache-correctness-parity-2026-06-03` |
| `graphwalks-13` | `openai/graphwalks` | `flashcache-correctness-parity-2026-06-03` |
| `graphwalks-16` | `openai/graphwalks` | `flashcache-correctness-parity-2026-06-03` |
| `graphwalks-19` | `openai/graphwalks` | `flashcache-correctness-parity-2026-06-03` |

The prior prompt-bearing selected-case JSONL was intentionally not recorded, so the first implementation step must re-materialize the six prompt-bearing cases locally from `openai/graphwalks` rather than depending on missing selected-case input.

## Goals / Non-Goals

**Goals:**

- Define the experiment ladder before running it.
- Keep the scope fixed to the six known GraphWalks failures.
- Preserve exact commands, model/runtime metadata, prompt hashes, raw outputs, timing, scores, and classifications.
- Separate model weakness, prompt-protocol issues, scorer/parser brittleness, session/cache semantics, position/compatibility issues, and runtime/storage issues.
- Identify the smallest Track 01 harness changes only if an existing command cannot express a requested control.

**Non-Goals:**

- No broad benchmark runs.
- No generalization from these six cases to all GraphWalks, all reasoning tasks, or all local-agent workloads.
- No lower-level SSD/KV storage design in this change.
- No Track 01 harness refactor unless a missing control surface blocks the focused ladder.

## Decisions

### Decision 1: Treat Track 02 as the committed experiment record

Committed experiment summaries will live in:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/
```

Expected committed files:

```text
README.md
commands.md
artifact-manifest.json
model-info.json
summary.json
failure-taxonomy.md
failure-classifications.json
```

Rationale: Track 02 owns the paper-candidate research lane. Track 01 remains the source harness and prior evidence path.

Alternative considered: store everything under the existing Track 01 dataset directory. That would blur evidence-harness ownership with the new failure-attribution research lane.

### Decision 2: Keep prompt-bearing raw inputs and execution artifacts local

Prompt-bearing input artifacts should be written under ignored benchmark paths:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/
research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/
research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/graphwalks-six-case-ladder-2026-06-03/
```

Rationale: previous prompt-bearing candidate and selected-case JSONL files were intentionally not recorded. The committed Track 02 files should preserve hashes, paths, metadata, commands, and summaries without forcing prompt text into source control.

Alternative considered: commit raw prompt JSONL to Track 02. Rejected because it changes the privacy/source-control posture from the prior correctness run.

### Decision 3: Use the current correctness CLI first

The existing CLI already provides `sample`, `build-candidates`, `run`, `score`, and `baseline-ladder`. Implementation should first try to express the ladder through existing commands plus local six-case filtering.

Proposed setup command shape:

```bash
cd research/01-ssd-native-inference-current

python3 benchmarks/flashcache_correctness_eval.py sample \
  --dataset graphwalks \
  --limit 20 \
  --max-prompt-chars 5000 \
  --output benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/graphwalks-20-candidates.jsonl

python3 - <<'PY'
import json
from pathlib import Path

root = Path("benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03")
selected = {"graphwalks-6", "graphwalks-9", "graphwalks-11", "graphwalks-13", "graphwalks-16", "graphwalks-19"}
rows = [json.loads(line) for line in (root / "graphwalks-20-candidates.jsonl").read_text().splitlines()]
picked = [row for row in rows if row["case_id"] in selected]
if {row["case_id"] for row in picked} != selected:
    raise SystemExit("missing one or more selected GraphWalks cases")
(root / "graphwalks-six-selected-cases.jsonl").write_text(
    "".join(json.dumps(row, sort_keys=True) + "\n" for row in picked),
    encoding="utf-8",
)
PY
```

If this cannot reproduce the exact cases due to remote dataset ordering or streaming behavior, add the smallest explicit case-id/source-id selection support needed and test it.

### Decision 4: Name each control as a separate mode in the artifact manifest

Use these control identifiers:

| Control id | Purpose | First implementation path |
| --- | --- | --- |
| `full_replay_variance` | Check whether full prompt still passes repeatedly at temperature `0.0` | Run full mode N times on the six selected cases |
| `visible_prefix_session_formatted` | Test prompt-protocol formatting without hidden/restored prefix semantics | Compose visible prefix plus session-tail framing in a full prompt, then score |
| `stronger_tail_hints` | Test whether tail-only failures are due to weak answer instructions | Run session-tail with stricter GraphWalks answer hint |
| `reset_restore_sanity` | Test restore determinism and clean-prefix reset behavior | Repeat prime/save/restore/tail and compare slot telemetry and answers |
| `scorer_parser_brittleness` | Test whether failures are scorer/parser artifacts | Re-score raw outputs and record raw/extracted/parsed/reference node sets |
| `stronger_model_control` | Test whether local GPT-OSS 20B brittleness is the main confounder | Run same cases on a stronger available local or hosted model if practical |

Rationale: explicit control ids make summaries, commands, and classifications stable across repeated runs.

### Decision 5: Use conservative failure classification

Failure taxonomy:

| Class | Confirming evidence | Ruling-out evidence | Fallback implication |
| --- | --- | --- | --- |
| `model_weakness` | Full-prompt replay fails or stronger model succeeds where local model is unstable | Full-prompt replay is stable and visible-prefix control passes | Use full prompt may not be sufficient; route by model/task capability |
| `prompt_protocol_issue` | Visible-prefix/session-formatted control fails like session-tail, or stronger tail hints repair the answer | Visible-prefix control passes while hidden session-tail fails | Change prompt protocol or use task-specific tail hints |
| `scorer_parser_brittleness` | Raw output contains acceptable answer but parser/scorer rejects it | Parsed node set is plainly wrong or prose-only | Improve scorer/parser before using as gate |
| `session_cache_semantic_issue` | Full replay and visible-prefix control pass, but restored session-tail fails | Reset/restore reveals compatibility or runtime issue instead | Fall back to full prompt for this task family or recompute anchor spans |
| `position_compatibility_issue` | Restore position, token count, context size, tokenizer, or prompt hash mismatch explains drift | Compatibility metadata matches and repeated restore is stable | Strengthen compatibility keys or reset/rebuild prefix |
| `runtime_storage_issue` | Save/restore errors, slot telemetry anomalies, corrupted files, or nondeterministic restore behavior appear | Slot telemetry is stable and failures are semantic | Treat as runtime bug; do not classify as model/prompt drift |

Ambiguous cases remain `ambiguous` until controls distinguish them.

## Proposed Commands

These commands are proposed for the eventual experiment run, not executed by this OpenSpec change.

Full-prompt replay variance:

```bash
cd research/01-ssd-native-inference-current

for run in 01 02 03; do
  python3 benchmarks/flashcache_correctness_eval.py run \
    --cases benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/graphwalks-six-selected-cases.jsonl \
    --mode full \
    --answer-protocol json-answer \
    --model benchmarks/models/gpt-oss-20b-mxfp4.gguf \
    --ctx-size 32768 \
    --predict 192 \
    --temperature 0.0 \
    --output-dir benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw \
    --output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/full-replay-${run}-responses.jsonl \
    --score \
    --score-output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/full-replay-${run}-scores.json
done
```

Session-tail replay / reset-restore sanity:

```bash
cd research/01-ssd-native-inference-current

for run in 01 02 03; do
  python3 benchmarks/flashcache_correctness_eval.py run \
    --cases benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/graphwalks-six-selected-cases.jsonl \
    --mode session-tail \
    --answer-protocol json-answer \
    --model benchmarks/models/gpt-oss-20b-mxfp4.gguf \
    --ctx-size 32768 \
    --predict 192 \
    --temperature 0.0 \
    --cache-dir benchmarks/correctness-eval-cache/graphwalks-six-case-ladder-2026-06-03/session-tail-${run} \
    --output-dir benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw \
    --output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/session-tail-${run}-responses.jsonl \
    --score \
    --score-output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/session-tail-${run}-scores.json
done
```

Visible-prefix/session-formatted control and stronger tail hints require either local case composition or a minimal CLI option if existing prompt construction cannot represent them. The implementation must record the chosen command in:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/commands.md
```

Stronger-model control command shape:

```bash
cd research/01-ssd-native-inference-current

python3 benchmarks/flashcache_correctness_eval.py run \
  --cases benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/graphwalks-six-selected-cases.jsonl \
  --mode full \
  --answer-protocol json-answer \
  --model <stronger-model-path-or-hf-repo> \
  --ctx-size <model-compatible-context-size> \
  --predict 192 \
  --temperature 0.0 \
  --output-dir benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw \
  --output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/stronger-model-full-responses.jsonl \
  --score \
  --score-output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/stronger-model-full-scores.json
```

## Risks / Trade-offs

- Dataset ordering drift could prevent exact source-id reconstruction from the remote GraphWalks stream. Mitigation: verify all six case ids after materialization; if missing, add a tiny source-id selection path and record the dependency.
- Prompt-bearing artifacts may contain dataset prompt text. Mitigation: keep them under ignored benchmark input paths and commit only hashes, metadata, summaries, and classifications.
- The existing CLI may not support visible-prefix/session-formatted and stronger-hint controls exactly. Mitigation: first try local case composition; only then add minimal tested harness support.
- Stronger-model control may be unavailable on the local machine. Mitigation: mark it `not_practical` with the reason, model availability check, and no paper-facing conclusion from that missing control.
- Six cases are useful for attribution, not prevalence. Mitigation: do not report them as a benchmark pass rate beyond the known failed-case cohort.

## Migration Plan

No migration is required. This change only defines the focused experiment contract. After approval, implementation should create the local artifact directories, run or add the focused controls, write Track 02 summaries, and validate any code changes with the Track 01 unit tests plus root OpenSpec validation.

## Open Questions

- Is `gpt-oss-20b-mxfp4.gguf` available in the expected local model path on the machine that will run the experiment?
- Which stronger model, if any, is practical for the stronger-model control?
- Can visible-prefix/session-formatted and stronger-tail-hint controls be represented by case composition alone, or is a minimal CLI option needed?
