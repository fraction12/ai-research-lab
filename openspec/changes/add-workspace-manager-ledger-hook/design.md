## Context

The AI research lab uses a hub-and-spoke Codex workflow. `Workspace Manager` coordinates Track 01, Track 02, Research Radar, and the paper-harvester tooling lane. The manager often needs to answer "what's next?" based on several recent thread states. Today that requires rereading thread summaries and repo artifacts.

This change adds a passive local ledger that the manager can consult as a starting point. It is not a replacement for evidence review, OpenSpec validation, or direct thread inspection when a decision is high stakes.

## Goals / Non-Goals

**Goals:**

- Keep a local JSON status board for Workspace Manager turns.
- Record enough information to orient the next manager turn quickly.
- Keep the hook passive and safe.
- Keep the first version narrow so it can be trusted.

**Non-Goals:**

- Do not run research tasks automatically.
- Do not continue turns automatically.
- Do not infer full cross-thread state from chat history.
- Do not commit generated ledger state.
- Do not require external services or model calls.

## Design

Add a repo-local `.codex/hooks.json` with a single `Stop` command handler:

```text
python3 "$(git rev-parse --show-toplevel)/.codex/hooks/workspace_manager_ledger.py"
```

The script reads the hook JSON payload from stdin, extracts the session id, turn id, cwd, transcript path, and `last_assistant_message`, then decides whether the event belongs to the Workspace Manager.

Because `Stop` matchers are ignored by Codex, filtering happens in the script. The first version uses a conservative allowlist containing the current Workspace Manager thread id and a title lookup against `~/.codex/session_index.jsonl` when available.

Matching events update:

```text
.codex/manager-ledger.json
```

The ledger structure is:

```json
{
  "schema_version": 1,
  "repo": "ai-research-lab",
  "updated_at": "2026-06-04T00:00:00Z",
  "threads": {
    "<thread-id>": {
      "thread_id": "<thread-id>",
      "title": "Workspace Manager",
      "role": "orchestration",
      "repo": "ai-research-lab",
      "status": "active",
      "current_assignment": "best-effort extracted summary",
      "last_update": "best-effort extracted summary",
      "next_action": "best-effort extracted next step",
      "cwd": "...",
      "turn_id": "...",
      "transcript_path": "...",
      "updated_at": "..."
    }
  },
  "events": []
}
```

The `events` array keeps the latest bounded event history for debugging. The thread entry stores the latest state for quick lookup.

## Classification

The hook uses deterministic text heuristics only:

- `blocked`: final message includes blocked/waiting/error wording.
- `done`: final message includes completed/landed/validated/sent wording.
- `waiting`: final message says it is waiting or standing by.
- `active`: default for manager updates.

`next_action` extraction is intentionally simple. It scans final-message lines for terms such as `next`, `wait`, `review`, `send`, `land`, `import`, or `validate`. The hook should provide a helpful hint, not a source of truth.

## Safety

- The script exits successfully and prints `{}` for both matching and non-matching events.
- Hook failures are written to a local error log and still return `{}`.
- Ledger writes use a temp file and atomic replace.
- Generated ledger and temp/error files are ignored by Git.
- The hook does not parse secrets, call external services, or run shell commands beyond the configured Python process.

## Risks / Trade-offs

- The current Workspace Manager id may change. Mitigation: also use session-index title lookup, and keep the allowlist easy to update.
- Heuristics may produce imperfect summaries. Mitigation: store the raw latest assistant message excerpt and treat the ledger as orientation, not authority.
- Project-local hooks require the project `.codex/` layer to be trusted. Mitigation: the hook is narrow and can be reviewed through Codex's hook trust flow.
