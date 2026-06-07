# Capsule Contract

This experiment tests the strong tail-only continuation contract:

1. Tokenize/prefill the reusable structured lookup prefix with `add_special=true` at position `0` in sequence id `0`.
2. Save sequence state using llama.cpp sequence-state APIs, with effective route `seq_file` and internal route `seq-file`.
3. Restore the saved sequence state into a clean context/session.
4. Tokenize/evaluate only the tail query with `add_special=false` at `len(prefix_tokens)`.
5. Generate from `len(prefix_tokens) + len(tail_tokens)` and score against the hidden prefix value.

Saved/restored object: llama.cpp sequence state for sequence id `0`, not a server prompt-cache full-prompt resend.

Primary capsule byte summary:

- mean bytes: `9516392.266666668`
- min bytes: `8681084`
- max bytes: `10377932`
- mean save ms: `14.269426668761298`
- mean restore ms: `7.2199733287561685`

What was not saved: raw prompt text, raw response text, expected answer strings, token arrays, sampler transcript, or state bytes in committed artifacts.
