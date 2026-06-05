# Repair Tail-Only KV Capsule Continuation

## Why

Track 02 now has narrow positive evidence for the strong tail-only capsule contract:

- `native-server-parity-bridge-2026-06-04`: server and native full-visible simple codeword behavior matched on the accepted prompt route.
- `kv-capsule-family1-semantic-gate-2026-06-04`: restored capsule append passed `3/3` simple codeword cases after ordered controls.
- `kv-capsule-family2-structured-retrieval-gate-2026-06-04`: restored capsule append passed `5/5` structured-retrieval cases after ordered controls.
- `kv-capsule-family3-mini-graph-gate-2026-06-04`: stopped at full-visible mini-graph guard, so capsule semantics were not tested for that family.

Those positives are not yet enough for a paper-grade mechanism claim. They need scaled reproduction, official-route triangulation, and a clear boundary/no-go path for the current GPT-OSS llama.cpp stack.

## What Changes

Run a focused tail-only KV/prefix-state continuation repair campaign that:

1. Keeps the target contract as `restore(capsule(prefix)) + append(tail)` without resending prefix text.
2. Reproduces Family 1 simple codeword at `30/30` cases.
3. Uses official server slot/cache APIs as diagnostics only, not as the final answer when full prompt text must be resent.
4. Uses native direct C API live append and restored capsule controls as the primary mechanism gate.
5. Prefers official llama.cpp sequence-state APIs (`llama_state_seq_*`) or a tiny C/C++ bridge over fragile whole-context state when practical.
6. Scales Family 2 only after Family 1 `30/30` passes.
7. Revisits Family 3 only as a full-visible guard redesign after Family 1 and Family 2 scaled gates are interpretable.

## Success Criteria

- OpenSpec validates before model-bearing execution.
- Family 1 full-visible, fresh-tail negative, native live append, and native restored capsule controls are run under deterministic decode.
- Family 1 passes only if restored tail-only capsule continuation is `30/30` answer-contained against a `30/30` full-visible guard, with fresh tail-only missing.
- Capsule artifacts record the exact state contract: API route, sequence id, prefix token count, append position, generation start position, capsule bytes/hash, save/restore timings, and whether sampler state is recreated.
- If Family 1 does not pass, the result escalates through documented route diagnostics instead of stopping at the first failure.
- If no viable route remains, the no-go report identifies the exact route-specific blocker and avoids universal "KV capsules impossible" claims.

## Non-Goals

- No GraphWalks, noiseless evidence, broad benchmark, or large retrieval scale in this change.
- Do not treat `cache_prompt: true` full-prompt resend as a successful tail-only capsule result.
- Do not hide output-protocol failures behind capsule interpretation; full-visible and live-append guards must pass before restored capsule semantics are interpreted.
