## 1. Spec and Scope

- [x] 1.1 Create OpenSpec proposal, spec, design, and task checklist.
- [x] 1.2 Bound v1 to read-only visualization plus explicit Codex prompt handoff.

## 2. Local App Skeleton

- [x] 2.1 Add `apps/research-cockpit/` with stdlib Python indexer/API and Vite TypeScript frontend.
- [x] 2.2 Add README with run command, data sources, and Codex browser usage.
- [x] 2.3 Add npm scripts, TypeScript config, and Vite build/dev workflow.

## 3. Repo Indexer

- [x] 3.1 Index research tracks, notes, evidence folders, and experiment folders.
- [x] 3.2 Parse experiment summaries, case metrics, failure classifications, model info, artifact manifests, and commands where present.
- [x] 3.3 Parse paper-harvest evidence summaries.
- [x] 3.4 Parse OpenSpec changes and task progress.
- [x] 3.5 Expose `GET /api/overview` and read-only file preview API.

## 4. Cockpit UI

- [x] 4.1 Build overview, track matrix, OpenSpec board, experiment browser, paper browser, and graph sections.
- [x] 4.2 Add charts for experiment controls, benchmark/savings signals, paper year/OA status, and OpenSpec progress.
- [x] 4.3 Add filters/search and source-path links/previews.
- [x] 4.4 Add agent-action prompt generator.
- [x] 4.5 Use Google's open-source Material Web component library for the cockpit controls and interaction surfaces.
- [x] 4.6 Apply white/blue/grey Material theme across the cockpit and data visualizations.
- [x] 4.7 Convert the cockpit shell from one continuous scroll page into route-based pages with active navigation.

## 5. Validation

- [x] 5.1 Add lightweight unit tests for index extraction helpers.
- [x] 5.2 Run `python3 -m unittest` for the cockpit.
- [x] 5.3 Run `openspec validate --all --strict`.
- [x] 5.4 Start the local server and verify the app loads.
- [x] 5.5 Use Codex browser preview or screenshot verification for desktop and narrow viewport layout.
- [x] 5.6 Run TypeScript check and Vite production build.
