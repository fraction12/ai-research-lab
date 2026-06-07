# GPT-OSS Edge-Evidence Control

Date: 2026-06-04

Machine: DushyantPC

Scope: six selected GraphWalks `parents` cases only: `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`.

## Result

The verified incoming-edge evidence control passed all six cases. This is not a broad benchmark and not proof of pure KV reuse. It is a role-aware context compilation / selective recompute control: the model succeeds when a small visible slice of the relevant graph evidence is supplied.

| Control | Cases | Passes | Mean score | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Pinned lower-level Harmony full prompt | 6 | 4 | 0.9333333333333332 | Full visible graph scan still misses one parent on `graphwalks-6` and `graphwalks-19`. |
| Final-only exhaustive repair on the two misses | 2 | 0 | 0.8 | Stronger final wording alone did not recover the omitted parent. |
| Verified incoming-edge evidence control | 6 | 6 | 1.0 | Tiny visible edge slices are enough for GPT-OSS to emit exact parent sets. |

## Evidence Added

| Case | Target | Verified incoming sources | Verified edges | Evidence bytes | Prompt tokens | Prompt ms | Passed |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `graphwalks-6` | `e4da3b7fbb` | `c81e728d9d`, `eccbc87e4b`, `d3d9446802` | 3 | 74 | 149 | 2152.209 | yes |
| `graphwalks-9` | `1679091c5a` | `c81e728d9d`, `eccbc87e4b` | 3 | 74 | 146 | 2121.801 | yes |
| `graphwalks-11` | `a87ff679a2` | `d3d9446802` | 1 | 24 | 112 | 1675.878 | yes |
| `graphwalks-13` | `a87ff679a2` | `1679091c5a` | 1 | 24 | 112 | 1830.23 | yes |
| `graphwalks-16` | `a87ff679a2` | `cfcd208495`, `c81e728d9d`, `e4da3b7fbb`, `1679091c5a`, `8f14e45fce` | 6 | 149 | 186 | 3195.486 | yes |
| `graphwalks-19` | `c4ca4238a0` | `eccbc87e4b`, `a87ff679a2`, `1679091c5a` | 4 | 99 | 159 | 2769.843 | yes |

Aggregate verified incoming-edge control metrics:

- Prompt tokens: 864 total, 144.0 mean.
- Prompt time: 13745.447 ms total, 2290.907833333333 ms mean.
- Visible evidence: 18 edge lines total, 444 bytes total, 3.0 edge lines mean, 74.0 bytes mean.
- Visible evidence tokens were not separately recorded in this control; the next repair test must record them.

## Artifact Pointers

Prompt-bearing raw artifacts remain in the DushyantPC ignored Track 01 benchmark results path:

```text
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\gptoss-llcpp-2026-06-04\raw\
```

Committed Track 02 summaries for this import:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/gptoss-edge-evidence-2026-06-04/README.md
research/02-quality-gated-stateful-kv-reuse/experiments/gptoss-edge-evidence-2026-06-04/summary.json
research/02-quality-gated-stateful-kv-reuse/experiments/gptoss-edge-evidence-2026-06-04/artifact-manifest.json
research/02-quality-gated-stateful-kv-reuse/experiments/gptoss-edge-evidence-2026-06-04/model-info.json
research/02-quality-gated-stateful-kv-reuse/experiments/gptoss-edge-evidence-2026-06-04/commands.md
research/02-quality-gated-stateful-kv-reuse/experiments/gptoss-edge-evidence-2026-06-04/failure-classifications.json
```

## Failure Taxonomy

| Class | Meaning for this import | Current status |
| --- | --- | --- |
| `model_weakness` | Model omits a correct parent while the answer format and scorer are valid. | Primary attribution for the pinned full-prompt misses on `graphwalks-6` and `graphwalks-19`. |
| `prompt_protocol_issue` | Instructions fail to expose or privilege the right evidence. | Secondary attribution for the two misses; final-only wording did not fix them, but visible evidence did. |
| `scorer_parser_brittleness` | Raw output is acceptable but parser/scorer rejects it. | Ruled down: edge evidence outputs parse and score correctly; missed full-prompt nodes are real omissions. |
| `session_cache_semantic_issue` | Hidden restored prefix changes semantics versus visible prompt. | Not tested by this import; this is the next visible-evidence-slice repair question. |
| `position_compatibility_issue` | Token position, context, tokenizer, or slot compatibility metadata explain drift. | Not established by this import. |
| `runtime_storage_issue` | Save/restore, storage, server, or slot telemetry failure explains the result. | No evidence in this control. |

## Interpretation

The evidence control narrows the next experiment. We should compare hidden-prefix/session-tail against hidden-prefix plus a small visible extracted evidence slice. If the visible slice repairs correctness while preserving most hidden-prefix prompt savings, the research framing should shift from pure persistent KV reuse to quality-gated state reuse with role-aware context compilation and selective recompute.
