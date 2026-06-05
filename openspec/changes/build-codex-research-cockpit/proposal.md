## Why

The lab now has multiple research tracks, OpenSpec changes, paper-harvest evidence, benchmark outputs, and experiment folders. The data is valuable but scattered across markdown, JSON, raw provider payloads, and active task lists. A Codex-native cockpit should make that state visible inside the Codex app while preserving the repo's file-backed research workflow.

## What Changes

- Add a local web app under `apps/research-cockpit/`.
- Add a dependency-light repo indexer that reads research tracks, OpenSpec changes, experiments, benchmark summaries, paper evidence, and negative-space notes.
- Serve a browser cockpit that runs in Codex's in-app browser against a local development server.
- Add chart and visualization views for experiment pass rates, benchmark savings, paper evidence, task state, and track activity.
- Add an agent-action panel that creates structured prompts for the active Codex thread instead of mutating research files directly.
- Keep v1 read-only except for optional copied prompt text or future explicit action files.

## Capabilities

### New Capabilities

- `research-cockpit`: Local Codex-native research cockpit for browsing, visualizing, and coordinating lab research data.

### Modified Capabilities

None.

## Impact

- Adds a small local application and scripts, without introducing a repo-wide build system.
- Gives Codex and the user a shared browser surface for research status, data charts, and next-action prompts.
- Does not replace OpenSpec, paper-harvester, or track-specific experiment artifacts; it indexes and visualizes them.
- Does not claim a direct private Codex thread API. The v1 connection model is Codex-native through shared local files, in-app browser, terminal, and structured prompts.
