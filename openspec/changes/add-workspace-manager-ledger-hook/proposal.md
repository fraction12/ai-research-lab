## Why

The Workspace Manager coordinates multiple Codex research threads, but its current status view has to be reconstructed from thread history. A small passive hook can keep a local operations ledger current after manager turns, making "what's next?" faster and less error-prone.

## What Changes

- Add a project-local Codex `Stop` hook for the lab repo.
- Add a lightweight ledger script that records Workspace Manager turn summaries into a local JSON state file.
- Keep the hook passive: it will not block turns, continue turns, run research tasks, or mutate research artifacts.
- Keep generated ledger state out of Git while tracking the hook config and script.

## Capabilities

### New Capabilities

- `workspace-manager-ledger`: Local Codex hook support for recording Workspace Manager coordination status.

### Modified Capabilities

## Impact

- Adds `.codex/hooks.json` and `.codex/hooks/workspace_manager_ledger.py`.
- Adds `.gitignore` entries for generated manager ledger state.
- Adds a new OpenSpec change for the workflow.
- No runtime dependencies beyond Python 3 and the Codex hook framework.
