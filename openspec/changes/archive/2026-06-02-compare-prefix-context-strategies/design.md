## Context

Ollama's generate API returns timing fields and a `context` array. The official API reference says that `context` can be sent to a later `/api/generate` call to keep conversational memory, but marks the parameter deprecated. That makes it useful as a local proxy for stable-prefix reuse, not as the target architecture.

The comparison needs to answer whether a stable-prefix strategy looks valuable enough to justify deeper work. A negative result is useful: if Ollama context reuse is slower or neutral, it tells us the proxy is not the final answer and that true prefix/KV persistence needs a lower-level backend.

## Goals / Non-Goals

**Goals:**

- Compare full prompt versus prefix-context strategy using the same fixture.
- Report strategy-level prompt evaluation totals and deltas.
- Keep the benchmark readable and dependency-free.
- Preserve existing full-prompt behavior as the default mode.

**Non-Goals:**

- Implement SSD-backed KV persistence.
- Claim Ollama context reuse is equivalent to prefix/KV cache reuse.
- Judge model output quality beyond short response excerpts.

## Decisions

- **Add `--strategy full|prefix-context|compare`.** Existing users get the same default behavior, while comparison mode runs both strategies.
- **Use common stable/semi-stable blocks as the reusable prefix.** This simulates the part of an agent workflow that should survive across changed-tail runs.
- **Run volatile tails with the primed context.** Scenario-specific volatile and non-common blocks become the changing tail.
- **Do not persist raw context arrays.** Result JSON records context length and hashes, but not the full token array, keeping artifacts smaller.
- **Report amortized cost.** The prime cost only pays off if reused across multiple tails, so the comparison includes prime-plus-tail and amortized deltas.

## Risks / Trade-offs

- **Ollama `context` is deprecated and may not reduce prompt eval work.** -> Mitigation: label the result as proxy-only and use the data to decide whether to move lower-level.
- **The priming response changes the conversation context.** -> Mitigation: use a tiny `OK` priming response and report that the strategy is approximate.
- **Strategy comparison can be noisy.** -> Mitigation: persist JSON results and allow multiple runs.
