## Why

The GraphWalks repair ladder showed `live-tail` and restored `session-tail` both failing 0/6, but that result depends on a backend assumption: a second llama.cpp `/completion` call on the same slot must behave like an append continuation over previously primed tokens. We need a tiny semantic litmus before interpreting further failures as model, prompt, or KV-reuse behavior.

## What Changes

- Add a focused session-continuation litmus that compares full-prompt, same-slot live-tail, and save/restore tail-only execution on simple memory-token prompts.
- Record exact commands, prompts, raw outputs, parsed answers, pass/fail scores, model/runtime metadata, and continuation interpretation.
- Keep this separate from GraphWalks and broad correctness benchmarks.
- Preserve Options 2 and 3 for later; this change only answers whether the session primitive itself is semantically usable.

## Capabilities

### New Capabilities

### Modified Capabilities

- `llama-cpp-agent-cache-wrapper`: Add requirements for a tiny session-continuation litmus that verifies same-slot and restored-slot tail-only calls can recall primed content before relying on session-tail benchmark interpretations.

## Impact

- Affected code: Track 01 benchmark/litmus tooling under `research/01-ssd-native-inference-current/benchmarks/`.
- Affected docs/artifacts: Track 02 experiment record under `research/02-quality-gated-stateful-kv-reuse/experiments/session-continuation-litmus-2026-06-03/`.
- No broad benchmarks, no GraphWalks reruns, and no new model downloads in this change.
