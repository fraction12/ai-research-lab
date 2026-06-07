# Capsule Contract

## Contract Tested

For each Family 1 case, the runner evaluated a prefix `P`, saved sequence state for `seq_id=0` using llama.cpp sequence-file APIs, restored that sequence state into a clean context, appended only the tail `T` at `len(prefix_tokens)`, and generated an answer. The tail request did not resend the prefix text.

## API Route

- Requested route: `auto`
- Effective route: `seq_file`
- Internal route: `seq-file`
- Sequence file APIs available: `True`
- Sequence memory APIs available: `True`

## Saved State

- API: `llama_state_seq_save_file(ctx, path, seq_id=0, prefix_tokens, prefix_token_count)`
- Restored API: `llama_state_seq_load_file(ctx, path, seq_id=0, token_buffer, token_buffer_capacity, token_count_out)`
- Mean capsule bytes: `859630.6666666666`
- Min capsule bytes: `787500`
- Max capsule bytes: `935040`
- Mean restored bytes: `859630.6666666666`
- Mean save ms: `5.5970433381541325`
- Mean restore ms: `6.297223330087339`

## Position Contract

- Prefix/full prompt starts tokenize with `add_special=true`.
- Appended tail tokenizes with `add_special=false`.
- Prefix prefill starts at position `0`.
- Tail append starts at `len(prefix_tokens)`.
- Generation starts at `len(prefix_tokens) + len(tail_tokens)`.

## What Was Not Claimed

This contract does not claim correctness for richer structured retrieval, graph reasoning, GraphWalks, agent-context tasks, or other models/backends. It proves the narrow Family 1 sequence-file continuation gate on this pinned stack.
