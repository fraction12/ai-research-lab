# 2026-06-05 OpenClaw Code Mode Tool-Use Note

## Bottom Line

OpenClaw code mode is an experimental agent-runtime feature that changes the tool-use surface shown to the model.

Instead of sending every enabled tool schema to the model, OpenClaw exposes only two model-visible tools:

- `exec`: run a model-written JavaScript or TypeScript program in a constrained QuickJS-WASI guest runtime.
- `wait`: resume a suspended code-mode run when nested tool calls are still pending.

The normal OpenClaw, plugin, MCP, and client tools are not removed. They are hidden from the model-facing prompt and registered in a run-scoped catalog that the guest program can search, describe, and call through a narrow host bridge.

This is not a new LLM model architecture and not a replacement for tool policy. It is a tool-surface adapter: a way to turn a large direct tool list into a small programmable orchestration interface.

Primary source: [OpenClaw code mode documentation](https://docs.openclaw.ai/reference/code-mode).

## What It Is

OpenClaw agents normally receive a set of visible tools after policy filtering. A visible tool is a typed callable action such as `exec`, `browser`, `web_search`, `message`, or `image_generate`; OpenClaw documentation describes these as structured function definitions sent to the model after active profile, allow/deny policy, provider restrictions, sandbox state, channel permissions, and plugin availability are resolved. Source: [OpenClaw tools overview](https://github.com/openclaw/openclaw/blob/main/docs/tools/index.md).

Code mode changes that final model-facing shape:

1. OpenClaw resolves the agent, model, provider, sandbox, channel, sender, and run policy.
2. OpenClaw builds the effective tool list.
3. OpenClaw applies allow and deny policy.
4. If `tools.codeMode.enabled` is true and tools are active, OpenClaw registers the effective tools in a hidden code-mode catalog.
5. OpenClaw removes normal tools from the model-visible tool list.
6. OpenClaw adds only code-mode `exec` and `wait`.

The result is that the model does not pick directly from dozens or hundreds of tool schemas. It writes a small program that can inspect and call the hidden catalog.

## What It Is Not

OpenClaw code mode is not Codex Code Mode.

The OpenClaw docs explicitly distinguish the two:

- Codex Code Mode runs in the Codex coding harness and uses an `exec.command`-style shell command contract.
- OpenClaw code mode runs in the OpenClaw generic agent runtime and uses an `exec.code` contract for JavaScript or TypeScript.

OpenClaw code mode is also not provider-native code execution. The model is not relying on a provider-side Python sandbox or remote code interpreter. OpenClaw evaluates the generated JS/TS in its own QuickJS-WASI guest runtime, then routes nested tool calls back through OpenClaw's existing tool executor.

It also does not bypass OpenClaw authorization. Nested calls still go through OpenClaw tool policy, approvals, hooks, channel context, sandbox policy, and audit/trajectory paths.

Sources: [OpenClaw code mode](https://docs.openclaw.ai/reference/code-mode), [Permission modes](https://docs.openclaw.ai/tools/permission-modes).

## Why It Exists

The immediate problem is large tool catalogs.

Direct tool exposure makes the model prompt carry many tool schemas. That can be expensive and hard for the model to navigate. OpenClaw's docs frame code mode as useful when an agent has a large enabled tool catalog or repeatedly needs to search, combine, and call tools before answering.

Code mode gives the model:

- a smaller prompt surface: only `exec` and `wait` are visible;
- programmable orchestration: loops, joins, filters, transforms, conditionals, and parallel nested calls can happen inside one code cell;
- provider neutrality: OpenClaw can use the same generic pattern for OpenClaw, plugin, MCP, and client tools;
- policy preservation: nested tool calls still re-enter OpenClaw's normal executor;
- fail-closed behavior: if code mode is enabled but the runtime is unavailable, OpenClaw should fail instead of silently exposing the full broad tool surface.

Source: [OpenClaw code mode, "Why is this good?"](https://docs.openclaw.ai/reference/code-mode).

## Runtime Contract

### Activation

Code mode is off by default. It activates only when `tools.codeMode.enabled: true` is configured and the run has active tools.

Minimal config:

```json5
{
  tools: {
    codeMode: {
      enabled: true
    }
  }
}
```

OpenClaw also accepts shorthand:

```json5
{
  tools: {
    codeMode: true
  }
}
```

Supported limits include:

- `timeoutMs`
- `memoryLimitBytes`
- `maxOutputBytes`
- `maxSnapshotBytes`
- `maxPendingToolCalls`
- `snapshotTtlSeconds`
- `searchDefaultLimit`
- `maxSearchLimit`

If code mode is enabled but QuickJS-WASI cannot load, the documented behavior is fail-closed for that run.

### Model-Visible Tools

The model sees:

- `exec`
- `wait`

All other enabled tools move into the hidden catalog.

### Guest Runtime

The `exec` tool evaluates model-generated JavaScript or TypeScript in QuickJS-WASI. TypeScript support is a transform into JavaScript, not full typechecking or module resolution.

Important constraints:

- no `import` or `require`;
- no filesystem access from the guest runtime;
- no network access from the guest runtime;
- no subprocess access from the guest runtime;
- no environment variable access;
- no host global objects;
- memory, time, output, snapshot, and pending-call limits are enforced.

The guest code itself is treated as hostile. The sandbox is only one layer; operators may still need OS-level hardening for high-risk deployments.

Source: [OpenClaw code mode, "QuickJS-WASI runtime" and "Security boundary"](https://docs.openclaw.ai/reference/code-mode).

## Hidden Catalog And Tool Calls

The hidden catalog contains tools after normal policy filtering:

1. OpenClaw core tools.
2. Bundled plugin tools.
3. External plugin tools.
4. MCP tools.
5. Client-provided tools for the current run.

Catalog ids are stable within one run and intended to be deterministic across equivalent tool sets when possible. The recommended id shape is:

```text
<source>:<owner>:<tool-name>
```

Examples from the docs:

```text
openclaw:core:message
plugin:browser:browser_request
mcp:github:create_issue
client:app:select_file
```

The catalog omits code-mode control tools such as `exec`, `wait`, `tool_search_code`, `tool_search`, `tool_describe`, and `tool_call`. This prevents recursive code-mode calls and keeps the control surface narrow.

Guest code can use helpers such as:

- `ALL_TOOLS`: compact metadata for available non-MCP tools.
- `tools.search(...)`: search the hidden catalog.
- `tools.describe(...)`: inspect a matching tool.
- `tools.call(...)`: call a tool by id.

MCP tools are handled through a generated `MCP` namespace. The docs say MCP entries remain in the run-scoped catalog for policy, approvals, hooks, telemetry, transcript projection, and exact ids, but MCP calls in code mode use `MCP.<server>.<tool>({ ...input })` rather than direct `tools.call(...)`.

Source: [OpenClaw code mode, "Tool catalog" and "Tool Search interaction"](https://docs.openclaw.ai/reference/code-mode).

## `wait`, Snapshots, And Long Nested Calls

Nested tool calls can be slow, approval-gated, interactive, or streaming. The model should not need to keep one long `exec` call open while the host waits for external work.

The `wait` tool exists for resumability:

1. `exec` starts guest code.
2. Guest code makes nested tool calls.
3. If nested work is pending, OpenClaw snapshots the QuickJS VM.
4. `exec` returns a waiting result with a `runId`.
5. When pending work settles, the model calls `wait` with that `runId`.
6. OpenClaw restores the VM, re-registers host callbacks, delivers nested results, drains pending jobs, and returns completed, failed, or waiting again.

Snapshots are runtime state, not user-authored artifacts. They are size-limited, TTL-limited, and scoped to the run and session that created them. A `wait` from the wrong run or session should fail.

Source: [OpenClaw code mode, "Runtime state"](https://docs.openclaw.ai/reference/code-mode).

## Permission And Safety Model

Code mode reduces the model-visible tool surface, but it does not make tool use automatically safe.

Nested tool calls preserve:

- active agent id;
- session id and session key;
- sender and channel context;
- sandbox policy;
- approval policy;
- plugin `before_tool_call` hooks;
- abort signal;
- streaming updates where available;
- trajectory and audit events.

This matters because the generated code is just another way to ask OpenClaw to call tools. If a dangerous tool is allowed, code mode may still reach it through the catalog. The docs' safety story depends on effective tool policy, permission modes, sandboxing, runtime limits, telemetry, and fail-closed behavior.

OpenClaw permission modes for host exec include `deny`, `allowlist`, `ask`, `auto`, and `full`. The recommended default for coding agents is `auto`, which uses deterministic allowlist matches first, then auto-review or human approval for misses. Source: [Permission modes](https://docs.openclaw.ai/tools/permission-modes).

## How It Compares To Related Tool-Use Surfaces

| Surface | Model sees | Runtime idea | Best for | Main risk |
| --- | --- | --- | --- | --- |
| Direct tool calling | Every visible tool schema | Model chooses one tool call at a time | Small catalogs, simple tools | Prompt bloat and tool-selection confusion |
| OpenClaw Tool Search | Compact search/describe/call tools | Model searches a hidden catalog through tool calls | Large catalogs without generated programs | More multi-step orchestration overhead |
| OpenClaw code mode | `exec` and `wait` | Model writes JS/TS that searches and calls hidden catalog | Large catalogs, joins, loops, transforms, parallel tool calls | Model-generated code becomes a new hostile runtime surface |
| Codex Code Mode | Codex native exec contract | Model writes shell commands in a coding harness | Repo coding and shell-based workflows | Different runtime and policy surface |
| Provider code execution | Provider-defined code sandbox | Provider runs code remotely | Data analysis / code execution with provider tools | Provider-specific capabilities and trust boundary |

OpenClaw code mode is closest to "Tool Search plus a tiny program executor." It moves catalog search and multi-tool orchestration inside a constrained guest program.

## Why This Matters For This Lab

OpenClaw code mode is relevant to several lab themes:

### 1. Tool Schemas As Context Pressure

Tool schemas are repeated agent context. In large agent systems, the tool catalog can become a large stable prefix. Code mode reduces the visible prompt surface from many schemas to two control tools plus compact catalog access inside the runtime.

This connects to Track 02's state-reuse work and Track 03's role-aware context compilation: tool schemas may be better treated as a hidden, policy-filtered runtime catalog rather than fully visible natural-language prompt state.

### 2. Role-Aware Context Compilation

Code mode effectively separates:

- visible orchestration contract: `exec` and `wait`;
- hidden tool metadata: run-scoped catalog;
- executable control flow: JS/TS cell;
- policy and safety: host-side executor and approvals.

That is a concrete example of role-aware context compilation. It assigns different context roles to different transport surfaces instead of flattening everything into one prompt.

### 3. Programmatic Tool Orchestration

The model can use code-level loops, joins, filters, and conditionals. That may improve tool-use reliability for workflows like:

- search multiple data sources;
- call a family of tools in parallel;
- merge structured outputs;
- retry failures with bounded logic;
- transform tool outputs before final reasoning.

But it also creates a new validation problem: the model's generated program may be wrong even if every nested tool call is valid.

### 4. Correctness Contracts

OpenClaw code mode has a contract-shaped design:

- exact model-visible tools should be `exec` and `wait`;
- hidden catalog must be scoped to the current run;
- denied tools must be absent;
- nested calls must preserve approvals and hooks;
- guest code must lack filesystem, network, subprocess, module, and environment access;
- telemetry must show nested calls without leaking secrets.

This is close to the lab's broader theme: agent systems need explicit contracts for when hidden state and hidden capabilities are equivalent to visible prompt state.

## Research Hypotheses

### Hypothesis 1: Tool-Surface Compression Improves Agent Reliability

Mainstream assumption challenged: more explicit tool schemas in the model prompt are better because the model can see all affordances.

Alternative: for large catalogs, hiding schemas behind a compact code/search surface may improve reliability by reducing prompt load and letting the model inspect only relevant tools.

Smallest test:

- Same model, same task suite, same tool set.
- Compare direct tool exposure, Tool Search, and code mode.
- Measure task success, tool-call count, prompt tokens, wrong-tool rate, and approval misses.

Stop rule:

- If code mode does not reduce prompt tokens or wrong-tool calls on large catalogs, it is not useful for this lab's context-pressure thesis.

### Hypothesis 2: Programmatic Orchestration Helps Multi-Tool Workflows But Hurts Simple Tasks

Mainstream assumption challenged: a single uniform tool-call interface should serve all tasks.

Alternative: generated code is helpful for joins, loops, and parallel calls, but unnecessary or risky for single-tool tasks.

Smallest test:

- Task bucket A: single known tool.
- Task bucket B: search plus two dependent tool calls.
- Task bucket C: parallel tool calls plus aggregation.
- Compare direct tools, Tool Search, and code mode.

Stop rule:

- If code mode only helps by making extra unnecessary calls, it is an orchestration smell rather than a reliability win.

### Hypothesis 3: Hidden Tool Catalogs Need Semantic Conformance Tests

Mainstream assumption challenged: if the policy-filtered catalog is correct, hiding it from the model is enough.

Alternative: hidden catalogs need conformance tests proving the model can discover the intended tool and cannot discover denied or cross-session tools.

Smallest test:

- Create two agents or sessions with overlapping and denied tool ids.
- Enable code mode.
- Ask the model to find and call allowed, denied, ambiguous, and forged tools.
- Verify denied tools are absent and forged ids fail.

Stop rule:

- If denied tools can be inferred or called by guessed id, the surface is not safe enough for high-risk local agents.

## Open Questions

- Does hiding detailed schemas reduce model confusion, or does it make the model worse at selecting the right tool because it has to search/describe first?
- How much prompt-token reduction does code mode produce for realistic OpenClaw agent catalogs?
- Does generated JS/TS improve multi-tool composition compared with ordinary tool-call chains?
- How often does code mode fail due to syntax errors, TypeScript transform failures, timeout, or snapshot expiry?
- Does `wait` resumability preserve enough execution context for complex nested workflows without confusing the model?
- Can telemetry reconstruct nested tool behavior well enough for audits and debugging?
- How does code mode interact with prompt caching, provider-specific tool restrictions, and local non-frontier models?
- Is code mode better treated as a general runtime feature or as a specialized large-catalog escape hatch?

## Practical Operator Notes

- Code mode is experimental and disabled by default.
- Enable it explicitly with `tools.codeMode.enabled: true`.
- Confirm the provider payload shape with targeted debug logging when testing.
- Keep explicit limits for timeout, memory, output, snapshot size, and pending calls.
- Treat generated code as hostile.
- Do not grant broad host exec unless the session and host are trusted.
- Test denied-tool absence and recursive-call rejection.
- Use telemetry to confirm nested tool calls are visible under the parent code-mode call.

## Source Links

- OpenClaw code mode reference: https://docs.openclaw.ai/reference/code-mode
- OpenClaw tools overview: https://github.com/openclaw/openclaw/blob/main/docs/tools/index.md
- OpenClaw permission modes: https://docs.openclaw.ai/tools/permission-modes
- OpenClaw agent configuration example: https://docs.openclaw.ai/gateway/config-agents
- OpenClaw ACP agents: https://docs.openclaw.ai/tools/acp-agents
- QuickJS-WASI reference repository: https://github.com/paralin/go-quickjs-wasi

## Positioning For The Lab

OpenClaw code mode should be treated as a concrete example of a broader research pattern:

> Agent runtimes can reduce prompt-visible tool surface by moving tool schemas into a policy-filtered hidden catalog and letting the model orchestrate tool use through a compact programmable interface.

This is promising, but not automatically safe. The interesting research question is not "can the model call tools through code?" The sharper question is:

> What correctness, audit, and policy contracts are required when the model no longer sees the full tool surface directly, but can discover and call it through generated code?

That question fits this repo's negative-space themes around role-aware context compilation, semantic contracts, and quality-gated local agent loops.
