## Context

The prior codeword gate established that:

```text
full_visible_prefix_plus_tail contained answer:      10/10
fresh_tail_only contained answer:                    0/10
restored_hidden_prefix_plus_tail contained answer:   0/10
restored exact response equaled fresh tail-only:     10/10
```

That means slot save/restore can be mechanically true while hidden tail-only completion is not a semantic continuation primitive for this pinned GPT-OSS path. The likely supported llama.cpp server path is different: restore the slot and resend the same full prompt with `cache_prompt: true` and an explicit `id_slot`, allowing the server to prefix-match restored tokens and only evaluate the suffix.

Pinned lower-level path:

```text
runner: C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe
model:  C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb
```

## Goals / Non-Goals

**Goals:**

- Test whether documented full-prompt resend cache reuse is semantically correct for the pinned GPT-OSS llama.cpp path.
- Test whether it avoids recomputing the restored prefix by comparing prompt-eval tokens/timing and server-log cache evidence.
- Preserve exact request payloads, commands, prompt hashes, raw output hashes, server log hashes, slot telemetry, model hash, runner hash, and timing telemetry.
- Keep the previous restored tail-only failure as an expected negative control.

**Non-Goals:**

- No GraphWalks run.
- No noiseless evidence rerun.
- No broad benchmark claim.
- No claim that this proves hidden invisible context.
- No use of the vault mind model.

## Controls

Run 10 deterministic codeword variants with the same nonce style as the prior gate.

| Control id | Slot setup | Prompt sent to `/completion` | Purpose |
| --- | --- | --- | --- |
| `full_visible_no_cache` | clean server/slot | full `prefix + tail`, `cache_prompt: false` | Semantic positive control without restored-slot dependence. |
| `fresh_tail_only` | clean server/slot | tail only, `cache_prompt: false` | Semantic negative control. |
| `restored_tail_only` | prime/save/restore prefix | tail only, `cache_prompt: true` | Preserve the known failing negative control. |
| `restored_full_prompt_cache_prompt` | prime/save/restore prefix | full `prefix + tail`, `cache_prompt: true` | Main documented server reuse route. |
| `full_prompt_cache_prompt_without_restore` | clean server/slot | full `prefix + tail`, `cache_prompt: true` | Optional comparison for ordinary full prompt behavior with cache_prompt enabled. |

Every request must force `id_slot: 0` to avoid automatic slot-selection ambiguity.

## Metrics

Every case/control record must include:

- strict exact match
- answer-contained / extractable-answer match
- output status: `exact_only`, `contains_with_extra_text`, `missing`, or `malformed`
- exact response string and normalized response string in raw artifacts
- response hash and normalized response hash in committed summaries
- prompt hash, prompt bytes, stable-prefix hash, tail hash
- request payload hash and raw request artifact path
- prompt tokens, predicted tokens, prompt milliseconds, decode milliseconds, total milliseconds, wall latency
- slot save/restore telemetry: `n_saved`, `n_restored`, `n_written`, `n_read`, save ms, restore ms, setup wall ms, prime prompt ms
- server log hash and selected non-prompt-bearing log evidence
- cache evidence fields if visible: slot id, `n_past`, evaluated prompt token counts, cache erase/truncate/prefix mismatch messages, and prompt-eval timing

## Log Evidence

Raw server logs are prompt-bearing and stay under ignored Track 01 benchmark paths. Committed summaries may include only:

- log path and hash
- selected sanitized lines that do not reveal prompt text
- counts for cache-related patterns such as `n_past`, `slot`, `cache`, `erase`, `truncate`, `prefix`, `prompt eval`, and `prompt tokens`
- whether the log evidence clearly indicates suffix-only evaluation, full-prefix recomputation, or ambiguity

## Decision Tree

- If `restored_full_prompt_cache_prompt` contains the codeword and prompt eval/log evidence shows only the tail/suffix was evaluated, conclude documented server cache reuse works semantically and computationally, but requires resending the prefix for matching. This is reusable visible-prefix context, not invisible hidden context.
- If `restored_full_prompt_cache_prompt` contains the codeword but prompt eval/log evidence shows the whole prefix was recomputed, conclude semantic correctness works but cache reuse did not produce the intended speed win.
- If `restored_full_prompt_cache_prompt` fails like `fresh_tail_only`, conclude the pinned GPT-OSS/server path is broken or incompatible for this documented cache-reuse route; recommend a stable non-SWA/non-hybrid model control before general claims.
- If `restored_tail_only` still fails, treat it as an expected negative control.
- If server logs are ambiguous, preserve the ambiguity and avoid overclaiming computational cache reuse.

## Artifact Layout

Prompt-bearing raw artifacts stay under ignored Track 01 paths:

```text
research/01-ssd-native-inference-current/benchmarks/documented-server-cache-reuse-2026-06-04/raw/
research/01-ssd-native-inference-current/benchmarks/documented-server-cache-reuse-2026-06-04/cache/
```

Committed Track 02 summaries live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/documented-server-cache-reuse-2026-06-04/
```

Required committed files:

```text
README.md
summary.json
case-metrics.json
failure-classifications.json
commands.md
model-info.json
artifact-manifest.json
server-log-index.json
```

## Stop Rules

- Stop before any GraphWalks or noiseless-evidence work.
- If DushyantPC cannot start the pinned server/model, record the hard blocker and do not substitute a different model.
- If full visible controls do not contain the answer, stop and classify prompt/model/protocol before interpreting cache reuse.
- If the main documented control fails like fresh tail-only across the codeword gate, stop after the 10-codeword set; do not expand the benchmark.
- If raw server logs are unavailable or ambiguous, continue semantic scoring but mark computational cache reuse as ambiguous.

## Migration Plan

No migration is required. Add the OpenSpec change, run the focused probe through ignored raw benchmark paths, import committed Track 02 summaries, validate OpenSpec, and commit locally if coherent.
