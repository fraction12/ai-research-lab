## Context

Track 02 is investigating quality-gated persistent KV/session reuse for local agent loops. The completed `graphwalks-six-case-ladder-2026-06-03` experiment fixed six GraphWalks cases where full prompt passed and session-tail failed:

```text
graphwalks-6
graphwalks-9
graphwalks-11
graphwalks-13
graphwalks-16
graphwalks-19
```

The first ladder established:

- full-prompt replay passed 18/18 attempts
- session-tail replay failed 0/18 attempts
- visible-prefix/session-formatted control passed 3/6
- stronger tail hints passed 0/6 and worsened JSON compliance
- save/restore telemetry was stable enough that runtime/storage failure is not the first explanation

The key split is that `graphwalks-13`, `graphwalks-16`, and `graphwalks-19` are high-confidence `session_cache_semantic_issue` cases, while `graphwalks-6`, `graphwalks-9`, and `graphwalks-11` also show prompt-protocol sensitivity.

The repo's paper harvest changes the research emphasis. SSD/NVMe KV movement is active and crowded through systems such as Tutti, KVDrive, DUAL-BLADE, Swarm, LMCache, and related work. Agent workflow cache policy is also active through Stateful Inference, KVFlow, PBKV, and policy-runtime work. The papers most useful for the next experiment are CacheBlend, EPIC, CachedAttention, DroidSpeak, SCBench, and Resident KV Claims because they suggest mechanism tests around selective recompute, position-independent reuse, positional assumptions, quality lifecycle, and conformance contracts.

## Goals / Non-Goals

**Goals:**

- Identify whether the six-case collapse is caused by live session semantics, disk save/restore, prompt visibility, position compatibility, or missing visible reasoning anchors.
- Test whether selective visible recompute of suffix or semantic anchor spans repairs any high-confidence session/cache semantic cases.
- Preserve exact model, quantization, hardware, backend version, commands, prompt hashes, raw outputs, timing, cache telemetry, summaries, and classifications.
- Update the paper-facing prior-art boundary for this ladder before interpreting results.
- Produce a conservative fallback policy for GraphWalks-style reasoning-over-prefix tasks.

**Non-Goals:**

- No broad benchmark suites.
- No new task families.
- No prevalence claim beyond the fixed six-case cohort.
- No new SSD storage layout, KV tensor format, compression scheme, or backend integration in this change.
- No Track 01 harness refactor unless a required runtime-boundary control cannot be expressed otherwise.

## Decisions

### Decision 1: Keep the fixed six cases

The repair ladder uses only `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`.

Rationale: the first ladder already proved this cohort is stable enough for mechanism work. Expanding the dataset now would trade a clean causal question for noisy prevalence measurement.

Alternative considered: immediately expand to all GraphWalks full-prompt pass cases. Rejected until at least one repair or attribution mechanism is tested.

### Decision 2: Separate live session continuation from disk save/restore

The ladder must include a `live_session_no_restore` control:

```text
prime stable_prefix -> continue with tail_prompt in the same live llama.cpp slot
```

This is distinct from the existing `session-tail` path:

```text
prime stable_prefix -> save slot -> restore slot -> continue with tail_prompt
```

Rationale: if live no-restore passes while save/restore fails, the mechanism points toward restore or position compatibility. If live no-restore also fails, the mechanism points toward tail-only/session semantics even before storage.

Current harness status: `flashcache_correctness_eval.py run` supports `full`, `session-tail`, and `both`. A true live no-restore control likely requires a minimal new mode, for example `--mode live-tail`, unless a lower-level existing wrapper already exposes it.

### Decision 3: Use anchor-span recompute as the first repair mechanism

The ladder should test a CacheBlend-inspired repair family:

```text
restore reusable prefix state
visibly replay or recompute a bounded anchor span
then ask the original tail question
```

Recommended first spans:

| Control id | Anchor |
| --- | --- |
| `anchor_recompute_64` | last 64 stable-prefix tokens before the operation |
| `anchor_recompute_128` | last 128 stable-prefix tokens before the operation |
| `anchor_recompute_256` | last 256 stable-prefix tokens before the operation |
| `anchor_recompute_semantic_operation_context` | the nearest graph/task instructions and operation-relevant text, if extractable without hand-editing per case |

Rationale: CacheBlend-style selective recompute is the most plausible path from "reuse is fast but semantically fragile" to "reuse can be quality-gated and repaired." The first test should be small and falsifiable: if all anchor spans still fail, GraphWalks may need full visible context or full fallback.

Alternative considered: jump directly to a new lower-level KV fusion implementation. Rejected because a visible recompute proxy can test the quality hypothesis first.

### Decision 4: Decompose prompt visibility

The ladder should include prompt visibility controls that make the failure mechanism less mysterious:

| Control id | Purpose |
| --- | --- |
| `query_visible_graph_hidden` | Test whether the original operation/question visible in the tail is enough when graph evidence remains only restored/session state. |
| `graph_visible_query_session_tail` | Test whether making graph/task evidence visible while keeping session-tail framing changes the outcome. |
| `graph_and_query_visible_session_format` | Confirm the first ladder's visible-prefix/session-formatted result shape under the new artifact directory if needed. |

Rationale: the first ladder proved prompt-format sensitivity for half the cases. This ladder should identify which visible span matters.

### Decision 5: Treat fallback as an algorithm output

The ladder must produce a fallback-policy artifact, not just a pass/fail table. The artifact should decide for each case and control family whether the safe policy is:

- `allow_session_tail`
- `allow_live_tail_only`
- `allow_restore_with_anchor_recompute`
- `require_full_prompt`
- `ambiguous_needs_lower_level_probe`

Rationale: the Track 02 thesis is quality-gated reuse. A failed repair result is still useful if it makes the fallback policy sharper.

### Decision 6: Write committed summaries in Track 02 and keep raw prompt/model outputs ignored

Committed summaries should live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-repair-mechanism-ladder-2026-06-03/
```

Expected committed files:

```text
README.md
commands.md
artifact-manifest.json
model-info.json
prior-art-mechanism-map.md
summary.json
repair-outcomes.json
failure-classifications.json
fallback-policy.md
control-feasibility.md
```

Prompt-bearing inputs, raw model outputs, and cache files should remain under ignored Track 01 benchmark paths:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/
research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/graphwalks-repair-mechanism-ladder-2026-06-03/raw/
research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/graphwalks-repair-mechanism-ladder-2026-06-03/
```

Rationale: this preserves the privacy/source-control posture from the first ladder while keeping reproducibility through hashes, commands, and summaries.

### Decision 7: Use the repo harvest as prior-art context, not as full-text evidence

The prior-art map should cite repo-local harvested metadata and abstracts, and it must state that PDFs/full text were not downloaded in the harvest if relying only on the current repo artifacts.

Relevant repo anchors:

```text
research/04-negative-space-ideas/2026-06-03-negative-space-scan.md
research/04-negative-space-ideas/evidence/2026-06-03-research-radar-harvest/harvest-summary.md
research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/negative-space-harvest-summary.md
research/01-ssd-native-inference-current/docs/research-paper-roadmap.md
research/01-ssd-native-inference-current/docs/research-positioning.md
research/01-ssd-native-inference-current/docs/references.md
```

Rationale: the current harvest is useful for positioning but not enough for detailed algorithmic claims.

## Proposed Command Shapes

These command shapes are design targets. They should not be run until the implementation phase is approved and any missing control surface is implemented.

Live no-restore control, if implemented as a minimal new mode:

```bash
cd research/01-ssd-native-inference-current

python3 benchmarks/flashcache_correctness_eval.py run \
  --cases benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/graphwalks-six-selected-cases.jsonl \
  --mode live-tail \
  --answer-protocol json-answer \
  --server-bin %USERPROFILE%\\Tools\\llama-b9482-vulkan\\llama-server.exe \
  --model benchmarks\\models\\gpt-oss-20b-mxfp4.gguf \
  --ctx-size 32768 \
  --predict 192 \
  --temperature 0.0 \
  --cache-dir benchmarks/correctness-eval-cache/graphwalks-repair-mechanism-ladder-2026-06-03/live-tail \
  --output-dir benchmarks/correctness-eval-results/graphwalks-repair-mechanism-ladder-2026-06-03/raw \
  --output benchmarks/correctness-eval-results/graphwalks-repair-mechanism-ladder-2026-06-03/raw/live-tail-responses.jsonl \
  --score \
  --score-output benchmarks/correctness-eval-results/graphwalks-repair-mechanism-ladder-2026-06-03/raw/live-tail-scores.json
```

Anchor recompute controls, if represented by derived local case JSONL files:

```bash
cd research/01-ssd-native-inference-current

for span in 64 128 256; do
  python3 benchmarks/flashcache_correctness_eval.py run \
    --cases benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/graphwalks-six-anchor-recompute-${span}-cases.jsonl \
    --mode session-tail \
    --answer-protocol json-answer \
    --server-bin %USERPROFILE%\\Tools\\llama-b9482-vulkan\\llama-server.exe \
    --model benchmarks\\models\\gpt-oss-20b-mxfp4.gguf \
    --ctx-size 32768 \
    --predict 192 \
    --temperature 0.0 \
    --cache-dir benchmarks/correctness-eval-cache/graphwalks-repair-mechanism-ladder-2026-06-03/anchor-recompute-${span} \
    --output-dir benchmarks/correctness-eval-results/graphwalks-repair-mechanism-ladder-2026-06-03/raw \
    --output benchmarks/correctness-eval-results/graphwalks-repair-mechanism-ladder-2026-06-03/raw/anchor-recompute-${span}-responses.jsonl \
    --score \
    --score-output benchmarks/correctness-eval-results/graphwalks-repair-mechanism-ladder-2026-06-03/raw/anchor-recompute-${span}-scores.json
done
```

The implementation may adjust command details after checking the actual DushyantPC shell, but `commands.md` must preserve the exact commands that were run.

## Risks / Trade-offs

- Live no-restore may require a Track 01 harness change -> keep it tiny, mode-scoped, and covered by focused tests.
- Anchor recompute through visible prompt composition is not the same as true KV-layer selective recompute -> label it as a proxy repair test and do not claim lower-level KV fusion.
- Token-span slicing can break prompt semantics -> record token counts, prompt hashes, and derived-case construction rules.
- Semantic anchor extraction may be hand-wavy -> prefer mechanical span controls first; if semantic anchors are used, record deterministic extraction rules.
- Six cases are not prevalence evidence -> report them as mechanism probes only.
- Prior-art harvest has metadata/abstracts but no PDFs -> avoid detailed novelty claims until full-text notes are added.

## Migration Plan

No migration is required. This change defines a focused research ladder. Implementation should create local derived-case inputs, add only minimal harness support if required, run the approved controls on DushyantPC, write Track 02 summaries, and validate with root OpenSpec plus relevant Track 01 tests if code changes are made.

## Open Questions

- Can live no-restore be expressed through an existing lower-level wrapper, or does it require a new correctness runner mode?
- Should anchor recompute spans be token-count based only, or should the first implementation include one deterministic semantic-anchor control?
- Is a compatible stronger GGUF model available later for cases that remain ambiguous after repair controls?
