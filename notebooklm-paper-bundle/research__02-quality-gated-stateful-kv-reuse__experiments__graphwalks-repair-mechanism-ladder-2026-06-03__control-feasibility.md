# Control Feasibility

Date: 2026-06-03

This file records feasibility for the focused GraphWalks repair/mechanism ladder before live model execution.

## Scope

Fixed case set:

- `graphwalks-6`
- `graphwalks-9`
- `graphwalks-11`
- `graphwalks-13`
- `graphwalks-16`
- `graphwalks-19`

No broad benchmarks are part of this change.

## Control Coverage

| Control | Covered by existing command? | Local case composition sufficient? | Track 01 code change? | Notes |
| --- | --- | --- | --- | --- |
| `full` replay reference | Yes | Yes | No | Existing `run --mode full --score`. Not expected to be rerun unless needed for local sanity. |
| restored `session-tail` baseline | Yes | Yes | No | Existing `run --mode session-tail --score`; used as `query_visible_graph_hidden` in this ladder. |
| `live-tail` no-restore | No | No | Yes | Added minimal `run --mode live-tail`: primes stable prefix and continues tail in the same server/slot without slot save/restore. |
| `anchor_recompute_64` | Yes | Yes | No | Derived case file prepends last 64 whitespace tokens of stable prefix to tail prompt, then runs restored `session-tail`. |
| `anchor_recompute_128` | Yes | Yes | No | Derived case file prepends last 128 whitespace tokens of stable prefix to tail prompt, then runs restored `session-tail`. |
| `anchor_recompute_256` | Yes | Yes | No | Derived case file prepends last 256 whitespace tokens of stable prefix to tail prompt, then runs restored `session-tail`. |
| `query_visible_graph_hidden` | Yes | Yes | No | Original selected case shape: graph/task evidence is hidden in restored prefix; operation/query remains visible in tail. |
| `graph_and_query_visible_tail` | Yes | Yes | No | Derived case replaces stable prefix with a short neutral instruction and places original full prompt in visible tail. |
| `graph_and_query_visible_session_format` | Yes | Yes | No | Derived case preserves original stable prefix and duplicates original full prompt visibly in tail. |
| position/compatibility probe | Partial | Yes | No | Uses recorded prompt hashes, byte counts, context size, backend metadata, and restore telemetry from response records. |

## Harness Change

The only Track 01 harness change required before live execution is a minimal `live-tail` correctness mode in `benchmarks/flashcache_correctness_eval.py`.

Behavior:

1. Start a managed llama.cpp server for the case.
2. Send the protocol-adjusted stable prefix with `cache_prompt=false` and `n_predict=prime_n_predict`.
3. Send the protocol-adjusted tail prompt in the same slot with `cache_prompt=true`.
4. Do not call slot save or restore.
5. Write the same response JSONL shape as other modes with `mode: "live-tail"`, prompt hashes, timings, and session setup telemetry.

Focused test coverage:

```text
cd research/01-ssd-native-inference-current
python3 -m unittest tests.test_flashcache_correctness_eval
```

Result on macOS checkout before DushyantPC live runs:

```text
Ran 22 tests
OK
```

## Derived Input Paths

Prompt-bearing inputs are intentionally ignored by git:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/graphwalks-six-selected-cases.jsonl
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/graphwalks-six-anchor-recompute-64-cases.jsonl
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/graphwalks-six-anchor-recompute-128-cases.jsonl
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/graphwalks-six-anchor-recompute-256-cases.jsonl
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/graphwalks-six-query-visible-graph-hidden-cases.jsonl
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/graphwalks-six-graph-and-query-visible-tail-cases.jsonl
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/graphwalks-six-graph-and-query-visible-session-format-cases.jsonl
```

`artifact-manifest.json` records hashes and construction metadata for these files.

## Caveat

The anchor-span controls use deterministic whitespace-token suffixes as prompt-level repair proxies. They are not model-token spans and they are not KV-layer selective recompute.
