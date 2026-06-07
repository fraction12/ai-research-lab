# Tail-Only KV Capsule Continuation Repair

## Result

The Family 1 repair gate passed on the official llama.cpp sequence-file state route. The primary 30-case run used `--state-route auto`, resolved to `seq_file`, and passed all ordered controls:

- `native_full_visible_prefix_plus_tail`: `30/30` answer-contained
- `native_fresh_tail_only`: `0/30` answer-contained, expected negative control
- `native_live_append_tail_only`: `30/30` answer-contained
- `native_restored_capsule_append_tail_only`: `30/30` answer-contained

Decision: `family1_sequence_state_restored_capsule_semantic_passed`. Stop rule: `restored_capsule_passed_stop_before_expansion`.

This is a narrow positive result: it proves Family 1 simple-codeword semantic continuation for the pinned GPT-OSS/native CUDA stack using `llama_state_seq_save_file` / `llama_state_seq_load_file`. It does not prove GraphWalks, richer retrieval, agent-loop quality, or general KV capsule correctness.

## Route

- Requested state route: `auto`
- Effective state route: `seq_file`
- Internal state route: `seq-file`
- Sequence file API available: `True`
- Sequence memory API available: `True`

Mean capsule size was `859630.6666666666` bytes across 30 restored cases.

## Evidence Boundary

The preliminary 3-case smoke gate also passed on `seq_file`. The 30-case gate is the primary result. Prompt-bearing raw records, console logs, runner scripts, and state files remain under the ignored Track 01 benchmark path. Committed artifacts contain only sanitized hashes/counts/timings/routes/classifications.

## Next Frontier

The immediate next research step is richer structured retrieval/Family 2 on the same `seq_file` route, with the same full-visible, fresh-tail, live-append, restored-capsule ordering.
