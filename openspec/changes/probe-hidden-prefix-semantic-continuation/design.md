## Context

Track 02 has a stronger mechanism signal than it had at kickoff, but also a sharper ambiguity. The 50-case GraphWalks parents pilot found:

```text
hidden_prefix_session_tail:                    0/50
hidden_prefix_compact_tail_no_evidence:        0/50
hidden_prefix_compact_visible_evidence_tail:  27/50
fresh_compact_visible_evidence_only:          27/50
```

The hidden-plus-evidence and fresh evidence-only controls matched by exact response string and score across all 50 cases. Meanwhile, llama.cpp slot telemetry reported mechanical save/restore activity, including saved/restored tokens and slot bytes read/written. The next question is therefore not whether evidence scheduling helps GraphWalks. It is whether the current pinned low-level GPT-OSS path gives a later tail request semantically usable hidden prefix state at all.

Pinned lower-level path:

```text
runner: C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe
model:  C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb
```

## Goals / Non-Goals

**Goals:**

- Test whether restored hidden prefix state can answer trivial later tail questions without visible prefix text.
- Separate "slot restore happened" from "semantic continuation worked".
- Use deterministic, prompt-simple cases before any noiseless GraphWalks evidence rerun.
- Preserve exact command lines, runner/model hashes, flags, prompts, prompt hashes, raw outputs, slot telemetry, and timing telemetry.
- Produce a failure classification that guides the next Track 02 branch.

**Non-Goals:**

- No broad benchmark run.
- No mixed task-family benchmark.
- No noiseless GraphWalks evidence rerun in this change.
- No claim that passing this probe proves GraphWalks-safe hidden KV reuse.
- No interpretation of failure as evidence against hidden KV in general; failure only speaks to this protocol/backend usage.

## Test Ladder

### Step 1: Codeword sanity test

Generate at least 10 deterministic nonce variants. Each case has:

```text
prefix: The secret codeword is <NONCE>. Remember it.
tail:   What is the secret codeword? Answer with only the codeword.
```

Controls per variant:

| Control id | Visible prefix | Restored hidden prefix | Purpose |
| --- | --- | --- | --- |
| `full_visible_prefix_plus_tail` | yes | no | Positive control. |
| `fresh_tail_only` | no | no | Negative control; expected miss. |
| `restored_hidden_prefix_plus_tail` | no | yes | Main semantic-restore test. |

Expected result if the restore path is semantically valid: full visible passes, fresh tail-only misses, restored hidden-prefix passes.

### Step 2: Simple key/value retrieval test

Generate at least 20 deterministic variants with a fixed seed. Each prefix contains 20 random key/value pairs such as:

```text
k01=VORLAN-72QK
...
k20=NIMBRA-11AZ
```

The tail asks one exact query:

```text
What is the value for k17? Answer only the value.
```

Use the same three controls. This distinguishes basic hidden-prefix retrieval from GraphWalks structured graph retrieval.

### Step 3: Tiny structured probe

Run this only if Step 1 and Step 2 both pass restored hidden-prefix controls. Use a miniature deterministic `parents` graph with 5-10 edges and the same three controls. If Step 1 or Step 2 fails, skip this step and record the skip reason.

## Metrics

Every case/control record must include:

- pass/fail exact match
- answer-contained / extractable-answer pass, where the expected nonce/value appears exactly as a standalone substring in the raw or normalized response
- exact response string
- normalized response string
- prompt hash and prompt-bearing raw artifact path
- prompt tokens
- predicted tokens
- prompt processing milliseconds
- decode/predicted milliseconds
- total latency milliseconds
- slot save/restore success
- `n_saved`, `n_restored`, `n_written`, `n_read`
- setup wall milliseconds, save milliseconds, restore milliseconds, and prime prompt milliseconds when applicable
- failure type from the taxonomy

## Failure Taxonomy

| Failure type | Meaning |
| --- | --- |
| `passed` | Expected answer was recovered by exact normalized match. |
| `prompt_protocol_issue_contains_answer` | The response contains the expected answer as a standalone substring but includes extra text, so semantic recovery succeeded while exact-output discipline failed. |
| `fresh_tail_expected_miss` | Fresh tail-only cannot know the hidden value and does not pass. |
| `semantic_restore_failure` | Full visible passes but restored hidden-prefix fails or matches fresh tail-only on codeword retrieval. |
| `simple_retrieval_failure` | Codeword restored-prefix passes, but key/value restored-prefix retrieval fails. |
| `prompt_protocol_issue` | Full visible fails or output format violates the compact answer protocol despite visible evidence. |
| `parse_failure` | The response may contain the answer, but normalization/scoring cannot reliably parse it. |
| `runtime_or_slot_failure` | Server, slot save, slot restore, cache file, or telemetry failure prevents a valid control result. |

## Interpretation Rules

- If restored hidden prefix fails the codeword test while full visible contains/extracts the expected answer, conclude that the current protocol/backend usage is not a valid semantic continuation mechanism. Do not interpret prior GraphWalks hidden-prefix failures as evidence against hidden KV in general.
- If restored hidden prefix matches fresh tail-only on codeword or key/value controls, call out that the restored state is not contributing semantically under this protocol.
- If codeword restored-prefix passes but key/value restored-prefix fails, conclude hidden state may be present but weak for exact retrieval over hidden prefix.
- If codeword and key/value restored-prefix controls pass but GraphWalks remains failed in earlier results, conclude the observed limitation is structured graph retrieval/reasoning, not basic semantic continuation.
- If full visible fails on these simple controls, classify prompt/model/protocol before interpreting hidden restore.
- Preserve strict exact match as an output-compliance metric, but do not let verbose full-visible answers invalidate the semantic-continuation check when the expected answer is extractable.

## Artifact Layout

Prompt-bearing local artifacts stay under ignored Track 01 benchmark paths:

```text
research/01-ssd-native-inference-current/benchmarks/hidden-prefix-semantic-continuation-2026-06-04/raw/
research/01-ssd-native-inference-current/benchmarks/hidden-prefix-semantic-continuation-2026-06-04/cache/
```

Committed Track 02 summaries live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/hidden-prefix-semantic-continuation-2026-06-04/
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
```

## Stop Rules

- Stop before any noiseless GraphWalks evidence rerun.
- If DushyantPC cannot start the pinned GPT-OSS llama.cpp server, record the hard blocker and do not substitute the vault mind model.
- If full visible fails broadly on the simple controls, stop and classify prompt/model/protocol rather than interpreting hidden restore.
- If codeword restored-prefix fails, do not run the optional tiny structured probe.
- If the 10-codeword gate is decisive because full visible contains the answer in all cases, fresh tail-only contains it in none, and restored hidden-prefix contains it in none while matching fresh, stop before the key/value ladder and package the codeword gate only.
- If repeated runtime/slot failures prevent valid restored-prefix controls, preserve logs and classify `runtime_or_slot_failure`.

## Migration Plan

No migration is required. Add the OpenSpec change, run the focused probe through ignored local benchmark artifacts, import committed Track 02 summaries, validate OpenSpec, and commit locally if the artifact set is coherent.
