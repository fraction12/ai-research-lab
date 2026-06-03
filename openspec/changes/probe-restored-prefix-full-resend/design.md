## Context

The last two Track 02 experiments changed the problem shape:

- `gpt-oss-20b-mxfp4.gguf` passed full-prompt tiny secret-token controls, but failed `live-tail` and `restored-tail` 0/3.
- An alternate-model sanity check also failed tail-only continuation after passing full-prompt controls.
- Slot save/restore telemetry showed tokens were saved/restored, so the failure is not simply "no slot file exists."

That means the next useful question is not whether the model can use hidden primed context from a tail-only prompt. The useful question is whether we can keep the full prompt visible, restore a matching prefix slot, and observe real prompt-processing reduction without correctness drift.

The model for this experiment is only:

```text
research/01-ssd-native-inference-current/benchmarks/models/gpt-oss-20b-mxfp4.gguf
```

Do not use `vault-mind-q5_k_m.gguf`; it was a one-off sanity probe and is not a valid research-control model going forward.

## Goals / Non-Goals

**Goals:**

- Prove or falsify restored-prefix full-resend as a correctness-safe mechanism candidate.
- Measure whether restored slots reduce prompt processing when the full prompt begins with the exact saved prefix.
- Verify exact-prefix gating with perturbation and wrong-slot controls.
- Preserve raw outputs and enough telemetry to separate correctness, prompt protocol, prefix-match behavior, restore overhead, and runtime/path issues.
- Produce a clear next-step decision for the six selected GraphWalks cases.

**Non-Goals:**

- No tail-only semantic-memory rescue attempt.
- No vault-mind model.
- No broad benchmark suite.
- No GraphWalks run until the tiny mechanism probe passes.
- No paper claim that prefix reuse is solved unless correctness and perturbation controls both pass.

## Experiment Ladder

### Phase 1: Tiny Synthetic Mechanism Probe

Use three secret-token cases first. Each case has:

- `stable_prefix`: store an exact token.
- `tail_prompt`: ask for that exact token using the same JSON answer protocol.
- `full_prompt`: `stable_prefix + tail_prompt`.
- `perturbed_prefix`: one deliberate, recorded token/byte change that changes the stored token.
- `wrong_slot_prefix`: another case's stable prefix restored before this case's full prompt.

Run these modes:

| Mode | Prompt Sent To Completion | Slot State | Expected Correctness | Expected Timing Signal |
| --- | --- | --- | --- | --- |
| `cold-full` | full prompt | no saved slot | pass | baseline prompt cost |
| `prime-save` | stable prefix | saves slot | not scored as answer | records saved tokens/slot bytes |
| `restored-full` | same full prompt | restored matching prefix slot | pass | lower prompt work than cold full if prefix reuse is active |
| `perturbed-full` | full prompt with changed prefix | restored original slot | pass for perturbed visible token | no unsafe reuse/leak; prompt work should rise or cache should miss |
| `wrong-slot-full` | full prompt for case A | restored slot for case B | pass for visible case A token | no leakage from wrong restored slot |

`restored-full` is the candidate mechanism. `perturbed-full` and `wrong-slot-full` are the safety controls.

### Phase 2: Decision Gate

Only proceed beyond tiny synthetic cases if:

- `cold-full` passes all selected synthetic cases.
- `restored-full` matches `cold-full` correctness.
- `perturbed-full` answers the perturbed visible prompt, not the restored original token.
- `wrong-slot-full` answers the visible prompt, not the wrong restored slot.
- `restored-full` shows measurable prompt-processing reduction versus `cold-full`, or at minimum clear token-accounting evidence that the prefix was recognized.

### Phase 3: Six GraphWalks Mechanism Control

If Phase 1 passes, apply the same mode set to:

```text
graphwalks-6, graphwalks-9, graphwalks-11, graphwalks-13, graphwalks-16, graphwalks-19
```

For GraphWalks, the safety gate is stricter:

- `cold-full` must match the previously full-passing baseline or pass the scorer again.
- `restored-full` must match `cold-full` score and answer.
- Perturbation should be limited to synthetic controls unless we design a graph-safe perturbation that does not make the problem ill-posed.

## Data To Collect

For every run record:

- case id, mode, model path, model bytes, backend version, command line, machine, date
- stable prefix bytes/hash, tail prompt bytes/hash, full prompt bytes/hash, perturbed prompt hash where applicable
- raw response, parsed answer, parse error, score, pass/fail
- latency wall time
- llama.cpp timings: prompt ms, prompt tokens, prompt ms/token, predicted ms, predicted tokens
- slot telemetry: slot filename, slot path, slot bytes, `n_saved`, `n_written`, save ms, `n_restored`, `n_read`, restore ms
- cache/compatibility classification: exact match, perturbed match, wrong slot, fallback/error
- raw log paths and result hashes

Committed Track 02 artifacts:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/restored-prefix-full-resend-2026-06-03/
  README.md
  commands.md
  model-info.json
  summary.json
  mechanism-decision.md
  failure-classifications.json
  artifact-manifest.json
```

Ignored raw artifacts:

```text
research/01-ssd-native-inference-current/benchmarks/restored-prefix-full-resend-results/restored-prefix-full-resend-2026-06-03/
research/01-ssd-native-inference-current/benchmarks/restored-prefix-full-resend-cache/restored-prefix-full-resend-2026-06-03/
research/01-ssd-native-inference-current/benchmarks/rpfr-results/rpfr-2026-06-03/
research/01-ssd-native-inference-current/benchmarks/rpfr-cache/rpfr-2026-06-03/
```

## Success / Failure Interpretation

| Outcome | Meaning | Next Step |
| --- | --- | --- |
| Correctness parity plus prompt reduction | Best case: visible full-resend can be quality-safe and useful | Run six GraphWalks restored-full control |
| Correctness parity but no prompt reduction | Quality-safe but no useful acceleration at this layer | Inspect lower-level prefix matching/token accounting; do not run GraphWalks for speed |
| Correctness drift on restored-full | Restore/full-resend path is not safe yet | fallback full prompt; inspect llama.cpp prompt/slot compatibility |
| Perturbation or wrong-slot leakage | Unsafe cache semantic behavior | require strict hash gate/fallback before any reuse |
| Runtime/path failure | Infrastructure issue, not mechanism result | shorten paths, rerun tiny probe only |

## Risks / Trade-offs

- [Risk] llama.cpp timing fields may count cached tokens differently across versions. -> Mitigation: record both timing and token counts, plus slot telemetry and raw outputs.
- [Risk] Perturbation can create ambiguous prompts. -> Mitigation: use synthetic exact-token cases first where expected answer is unambiguous.
- [Risk] Full-resend correctness may pass even if no acceleration happens. -> Mitigation: require prompt-processing reduction or token-accounting evidence before moving to GraphWalks.
- [Risk] Cache paths on Windows can fail when too long. -> Mitigation: use intentionally short cache/result paths on DushyantPC.
