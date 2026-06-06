## Context

Track 02 is testing whether stable local-agent state can be persisted as a KV capsule and later restored so the model can append only the volatile tail while still behaving like it saw `stable prefix + tail`.

The current evidence is split:

- Gemma 4 12B on DushyantPC passed the narrow sequence-file KV capsule gates: full visible, native live append, and restored capsule append passed, while fresh tail-only failed.
- The later HF benchmark did not produce interpretable restored-capsule evidence because IFEval leaked enough information through the tail and GraphWalks was not full-visible reliable for Gemma 4 under the tested protocol.
- The OpenClaw Code mode note suggests a separate axis of context compilation: hide the broad tool catalog behind a small `exec`/`wait` model-visible contract and let a constrained runtime search, describe, and call policy-filtered tools.

This design combines those two ideas as a controlled local-agent runtime harness probe. It asks whether a local model can use fewer visible tokens and still perform more reliable tool-heavy work when:

1. stable instructions, tool protocol, catalog metadata, workspace state, and trace facts live in a reusable KV capsule;
2. the visible prompt contains only the current task, compact evidence when allowed, and a small Code mode contract;
3. tool execution is mediated through a hidden catalog with deterministic policy, telemetry, and failure handling.

## Goals / Non-Goals

**Goals:**

- Produce a handoff-quality experiment design that another agent can implement without rediscovering the research framing.
- Build a staged viability test before any larger benchmark run.
- Test Code mode, KV capsules, and compact evidence as separable mechanisms.
- Use deterministic prefix-dependent task cases so negative controls are meaningful.
- Preserve paper-grade telemetry: prompt sizes, capsule route, capsule identity, live-vs-restored parity, generated-code validity, tool-call correctness, safety behavior, runtime timing, and failure classes.
- Define go/no-go thresholds for scaling to a larger benchmark.

**Non-Goals:**

- Do not claim Code mode or KV capsules make a model generally smarter from this prototype alone.
- Do not use HF GraphWalks or IFEval as the first combined viability suite unless they pass prefix-dependence and full-visible gates.
- Do not build a production OpenClaw integration before a simulated harness proves the mechanism.
- Do not bypass tool policy, approvals, denied-tool filtering, or sandbox boundaries for convenience.
- Do not persist raw volatile prompts, tool outputs, generated code, or capsule payloads in committed files.

## Decisions

### Decision 1: Start with a controlled prototype suite, then scale

The first suite SHOULD be purpose-built, deterministic, and prefix-dependent. It should include agent-like tool-use patterns that are hard to validate with generic HF rows:

- single-tool selection from a large catalog;
- search then dependent tool calls;
- parallel calls with aggregation;
- retry after a bounded tool failure;
- continuation from a prior task trace;
- denied, forged, stale, or wrong-session tool ids.

Alternatives considered:

- Run HF GraphWalks/IFEval immediately. Rejected for this combined probe because the previous HF run showed those splits can either leak through the tail or fail full-visible baseline.
- Use only synthetic codewords and key-value facts. Rejected as too narrow; those already proved the low-level capsule route but not agent behavior.

### Decision 2: Treat Code mode as a contract that can be simulated first

The implementation SHOULD support two routes:

- `simulated_code_mode`: a local deterministic harness where the model is prompted to emit an OpenClaw-shaped `exec` code cell, then the harness validates and executes only allowed catalog calls through a deliberately small emulator.
- `openclaw_code_mode`: a real OpenClaw Code mode route if the runtime is available and can be controlled safely.

The simulated route is acceptable for the first research gate if it preserves the same semantic contract: the model sees only the Code mode control surface and the hidden tool catalog is accessed through search, describe, and call operations.

For model-bearing Gemma runs, the simulated route MUST be a bounded continuation loop:

1. the model emits one `EXEC {"code":"..."}` or `FINAL ...` line;
2. the host parses and validates the exec request, accepting strict JSON first and only narrow compatibility forms for observed Gemma/OpenClaw-style fragments;
3. the host statically extracts a bounded subset of `tools.search`, `tools.describe`, and `tools.call` operations from the code cell, then executes those operations through the hidden catalog;
4. the host appends a compact `EXEC_RESULT` observation to the same llama sequence when another model step is needed, or treats an answer-bearing host tool result as terminal when the route is configured for host-answer finalization;
5. the loop continues until a final answer is produced, an answer-bearing tool result is returned, or a bounded stop rule fires.

The first failed two-case smoke proved that one-shot generation is not a valid Code mode route: Gemma emitted tool intent, but the adapter scored the raw intent as a final answer. A second smoke found that fabricated `TOOL_RESULT` or `EXEC_RESULT` text must be rejected as model output. Those failures are prompt/runtime-loop blockers, not capsule evidence.

Alternatives considered:

- Require real OpenClaw Code mode before starting. Rejected because it adds integration risk before the research question is de-risked.
- Expose the entire catalog visibly and call it Code mode. Rejected because it would destroy the tool-surface compression variable.
- Score the first generation as a final answer. Rejected because Code mode is specifically a host-mediated tool loop; scoring tool-intent text confounds model weakness with missing runtime behavior.

### Decision 3: Use a full paired control matrix

Each selected case MUST run the controls that isolate each mechanism:

| Control id | Purpose |
| --- | --- |
| `direct_full_visible_tools` | Baseline with full visible instructions and direct tool schemas. |
| `code_mode_full_visible` | Tests Code mode with full stable context visible. |
| `code_mode_fresh_tail_only` | Negative control for tail leakage. |
| `code_mode_native_live_append` | Tests hidden prefix append semantics without persistence. |
| `code_mode_restored_kv_capsule` | Main combined KV capsule plus Code mode condition. |
| `code_mode_wrong_capsule_negative` | Ensures capsule/catalog/session identity matters. |
| `compact_visible_evidence_code_mode` | Separates compact evidence scheduling from hidden KV state. |
| `tool_search_no_code_mode` | Optional ablation for hidden catalog search without generated programs. |

The restored condition is interpretable only if full-visible and native live append pass, fresh tail-only underperforms, and wrong-capsule negative fails or is rejected.

### Decision 4: Make the stable prefix capsule explicit

The stable prefix SHOULD contain:

- system/developer agent rules;
- the Code mode visible contract and output format;
- hidden catalog summary, catalog hash, and tool namespace rules, but not every full direct tool schema as visible text;
- workspace map and task fixtures;
- policy invariants, denied-tool behavior, and approval constraints;
- prior task trace/checkpoint facts for long-horizon continuation cases;
- scorer instructions and answer format constraints when they are stable.

The volatile tail SHOULD contain only the current task request, case id, and any allowed compact evidence slice for the specific control.

### Decision 5: Record mechanism-level telemetry, not just pass rates

The runner MUST record enough data to explain failures:

- prompt token/byte counts for prefix, tail, full prompt, and visible evidence;
- model path, model hash, quantization, tokenizer/template identity, llama.cpp build, hardware, GPU, context settings, seed, temperature, and generation limits;
- capsule route, capsule id, sequence id, prefix token count, `n_past`, path/hash/bytes, save/restore timing, and compatibility metadata;
- hidden catalog id, catalog hash, visible contract hash, denied-tool set hash, and tool search/describe/call transcript;
- generated code or structured plan hash, validation status, syntax/runtime errors, timeout, memory/output limit flags, and pending/wait behavior if implemented;
- semantic pass/fail, tool selection correctness, argument correctness, response hash, normalized response hash, token hash where available, and failure class.

### Decision 6: Gate scale-up behind smoke criteria

The implementation SHOULD run in phases:

1. Harness-only dry run with a stub model response to validate tooling and scoring.
2. Two-case model smoke across all controls.
3. Twelve-case viability suite: two cases per task bucket.
4. Thirty-case viability suite: five cases per task bucket.
5. Larger benchmark only if the thirty-case suite passes the interpretation gates.

The larger benchmark design should be a later change if this probe passes.

## Risks / Trade-offs

- [Risk] The simulated Code mode route diverges from real OpenClaw behavior. -> Mitigation: keep the contract explicit, record route identity, and require a real-route confirmation before external claims.
- [Risk] Fresh tail-only passes because the tail leaks the answer or full task shape. -> Mitigation: quarantine those cases and do not count them as KV evidence.
- [Risk] Direct tools outperform Code mode on simple tasks. -> Mitigation: analyze by task bucket; Code mode is expected to help more with large catalogs, loops, joins, retries, and continuation.
- [Risk] Generated code introduces new failure modes. -> Mitigation: score code validity separately from tool-call correctness and answer correctness.
- [Risk] Wrong capsule still passes. -> Mitigation: treat that as task invalidity, scorer leakage, or unsafe capsule identity enforcement; stop paper interpretation until fixed.
- [Risk] The runner overloads DushyantPC. -> Mitigation: staged gates, no duplicate process launches, small max tokens, fixed cohorts, and checkpointed raw artifacts.
- [Risk] Compact visible evidence equals restored capsule performance. -> Mitigation: report that as context scheduling/tool-surface value, not hidden KV value.
