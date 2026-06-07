# Mechanism Decision

Decision: `correctness_safe_without_useful_acceleration_evidence`

## What Passed

The full visible prompt controls passed:

- `cold-full`: 3/3
- `restored-full`: 3/3
- `perturbed-full`: 3/3
- `wrong-slot-full`: 3/3

The parser was not the problem: all scored answers were valid JSON and exact-token correct. The perturbation and wrong-slot controls did not show leakage from restored state into the visible prompt answer.

## What Did Not Pass

The acceleration gate did not pass.

`restored-full` reported the same mean prompt token count as `cold-full`:

```text
cold-full prompt_n mean: 79.667
restored-full prompt_n mean: 79.667
```

It was also slower on mean prompt time:

```text
cold-full prompt_ms mean: 659.674
restored-full prompt_ms mean: 687.327
cold minus restored prompt_ms: -27.653
```

Only one of three cases had a small prompt-ms reduction, so this is not enough to claim useful prefix reuse.

## Stop Rule

Do not run the six selected GraphWalks restored-full control yet.

The tiny synthetic probe only supports a correctness claim for visible full-resend under exact-token controls. It does not yet show that restoring the slot reduces prompt processing. GraphWalks would spend model time without answering the mechanism question.

## Next Mechanism Work

Move closer to the implementation boundary:

- inspect llama.cpp slot restore plus `cache_prompt` prefix matching behavior under full resend;
- compare same-process restore, fresh-process restore, and persistent-server restore with verbose token accounting;
- test a longer synthetic prefix where prompt-processing savings should be large if reuse is active;
- add a lower-level compatibility check for tokenized prefix identity before claiming state reuse.

The fallback policy remains full visible prompt execution for reasoning-over-prefix tasks until a lower-level reuse path shows both correctness and prompt-work reduction.
