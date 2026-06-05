## Context

This repo is already a file-backed research workspace. Most useful state lives in markdown and JSON:

- Track READMEs and notes under `research/`.
- Experiment folders under `research/*/experiments/*`.
- Benchmark/correctness result JSON under Track 01 benchmark folders.
- Paper-harvest evidence under Track 04 evidence folders.
- OpenSpec changes under `openspec/changes/`.
- Repo-local Codex skills under `.codex/skills/`.

The app should behave like a Codex-native cockpit: a local web surface the user opens in Codex's in-app browser while the current Codex thread remains the agent that can read files, run commands, and implement follow-up work.

## Product Direction

MVP: **Research Cockpit, not autonomous researcher.**

The v1 app is a rich read-only observer plus prompt generator. It should make the state visible and help the user ask Codex for precise next actions. It should not directly run experiments, edit files, or commit changes.

## Architecture

Use a small TypeScript web app with a dependency-light Python API:

```text
apps/research-cockpit/
  package.json           # Vite + TypeScript + Material Web
  vite.config.ts
  tsconfig.json
  server.py              # stdlib HTTP server + repo indexer API + built static host
  index.html
  src/
    main.ts
    styles.css
  README.md
```

Rationale:

- The cockpit is now complex enough to benefit from TypeScript API models, a proper module boundary, and a real frontend build.
- Vite keeps the local development loop fast and does not require a larger framework.
- Python stdlib remains the right fit for repo indexing because the existing implementation is file-backed, tested, and dependency-light.
- SVG chart primitives are enough for the MVP and can be replaced later if the app grows.

## Indexer

`server.py` will expose:

- `GET /api/overview`: complete snapshot for the SPA.
- `GET /api/file?path=<repo-relative-path>`: read-only text preview for safe repo-relative files.
- `GET /`: static app.

The indexer will:

- Walk only known research/OpenSpec paths.
- Ignore `.git`, large model/cache folders, and ignored benchmark bulk directories unless summary-like files are explicitly useful.
- Parse JSON defensively and attach parse warnings instead of failing the page.
- Include source paths and derived-field provenance.

## Visualization

The SPA will render:

- Lab overview metrics.
- Track matrix with activity/evidence counts.
- OpenSpec progress bars.
- Experiment table with filters.
- Control comparison bar charts where `summary.json` exposes pass-rate/mean-score controls.
- Benchmark/savings chart where benchmark results expose strategy/scenario timings.
- Paper evidence charts by publication year and OA status.
- Research graph as a lightweight SVG network: track -> experiment/evidence/paper.
- Agent action prompt panel.

Navigation is route-based inside the shell. The sidebar stays persistent, while `#overview`, `#experiments`, `#papers`, `#graph`, and `#actions` each render as separate pages rather than sections in one continuous document. Data-heavy panels use internal scrolling where needed so a route behaves like a focused workspace page instead of a long report.

Design direction: dense lab console. Compact, utilitarian, white/blue/grey Material palette with high-contrast chart colors. No landing page, no hero, no nested decorative cards.

The UI uses Google's open-source Material Web components (`@material/web`) for controls, buttons, chips, progress indicators, dialogs, selects, and text fields. V1 bundles Material Web through Vite/npm so the app has a proper TypeScript/JavaScript development workflow. The custom data visualization layer remains local SVG because Material Web does not provide chart components.

## Agent Action Model

V1 uses explicit prompt handoff:

- User chooses action and target.
- App generates a structured prompt.
- User pastes it into the active Codex thread.
- Codex performs the work with normal repo tools and verification.

This avoids pretending the app has private access to the active thread API. It still fits Codex-native use because Codex can run the server, inspect the app in the browser, and act on generated prompts.

## Risks / Trade-offs

- **Static parser drift:** research artifact shapes will evolve. Mitigation: defensive extraction and warnings.
- **Too much data:** raw provider files and large benchmark outputs can overwhelm the UI. Mitigation: index summaries and selected raw metadata, not full raw payload content.
- **False certainty from charts:** charts can make incomplete experiments look decisive. Mitigation: show artifact gaps, source paths, and warnings.
- **No direct thread API:** v1 prompt handoff is less magical. Mitigation: it is transparent and reliable inside current Codex constraints.

## Future Extensions

- Action files under `.codex/research-cockpit/actions/` that Codex can pick up.
- WebSocket refresh while experiments run.
- SQLite or DuckDB cache for larger experiment collections.
- MCP tool surface if the cockpit becomes more than a local viewer.
- Chart export for papers/reports.
