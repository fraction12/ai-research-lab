## 1. Research And Scope

- [x] 1.1 Review official OpenClaw code mode documentation.
- [x] 1.2 Review OpenClaw tool, permission, and ACP/session documentation relevant to tool execution and policy.
- [x] 1.3 Identify how code mode differs from direct tool exposure, Tool Search, Codex Code Mode, and provider-native code execution.

## 2. Write Research Note

- [x] 2.1 Create a standalone Track 04 research note with source links.
- [x] 2.2 Explain what code mode is, how activation works, the runtime contract, hidden catalog, `exec`/`wait`, snapshots, tool calls, MCP namespace, and telemetry.
- [x] 2.3 Add research implications for local-agent context compilation, tool schema overhead, safety, and correctness.
- [x] 2.4 Add risks, open questions, and smallest useful experiments.

## 3. Validate

- [x] 3.1 Run `openspec validate document-openclaw-code-mode-research-note --type change --strict`.
- [x] 3.2 Run `openspec validate --all --strict`.
- [x] 3.3 Report dirty worktree status without touching unrelated user/other-thread changes.
