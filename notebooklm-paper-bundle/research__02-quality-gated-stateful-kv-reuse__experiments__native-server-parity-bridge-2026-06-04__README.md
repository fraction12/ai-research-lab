# Native Server Parity Bridge

Date: 2026-06-04

## Decision

`native_full_visible_parity_passed_family1_capsule_gate_not_run_in_this_script`

The native direct C API harness now reproduces the refreshed server full-visible codeword behavior on the 3-case simple prompt bridge. This is a parity result, not a KV capsule result. The run stopped by design before Family 1 capsule gates.

## What Passed

- Refreshed server full-visible baseline: `3/3` answer-contained.
- Server `/tokenize` with payload shape `content`: token counts matched native tokenization hashes for all 3 cases.
- Server `/tokenize` with payload shape `prompt`: returned 0 tokens, recorded as an endpoint-shape finding.
- Native full-visible with `add_special=true`: `3/3` answer-contained.
- Native full-visible with `add_special=false`: `3/3` answer-contained.

Exact-only output did not pass; responses contained extra explanatory text. For this sanity bridge, answer-contained is the semantic gate, matching prior probe scoring guidance.

## Important Correction

An earlier nonce-shaped bridge attempt produced repeated newlines and was discarded as a harness-mismatch diagnostic. The final accepted bridge uses the prior known-good simple codeword prompt shape and GPT-OSS server flags: `--no-mmap`, `--flash-attn auto`, `--jinja`, `--reasoning off`, and `--reasoning-budget 0`.

## Interpretation

The previous KV-capsule blocker was not a fundamental native C API generation failure. With the known-good prompt shape and server flags, native tokenization matches server tokenization and native full-visible generation contains the hidden codeword. Track 02 can now proceed to the reviewed Family 1 capsule gate, but only after approval.

## Raw Evidence

Prompt-bearing raw artifacts are ignored under:

```text
research/01-ssd-native-inference-current/benchmarks/native-server-parity-bridge-2026-06-04/raw/
```

## Next Step

Run Family 1 capsule gates using this parity-proven prompt/token route. `native_live_append_tail_only` must pass before restored capsule semantics are interpreted.
