# Research Cockpit

Local Codex-native research interface for the AI research lab.

Run from the repo root:

```bash
cd apps/research-cockpit
npm install
npm run build
python3 server.py --port 8765
```

Then open:

```text
http://127.0.0.1:8765
```

inside the Codex in-app browser.

## What It Indexes

- Research tracks under `research/`
- Experiment folders under `research/*/experiments/*`
- Experiment artifacts such as `summary.json`, `case-metrics.json`, `failure-classifications.json`, `artifact-manifest.json`, `commands.md`, and `model-info.json`
- Paper harvest evidence summaries under `research/*/evidence/**`
- Benchmark and correctness summary JSON from Track 01
- OpenSpec changes and task progress

## UI System

The cockpit is a Vite + TypeScript app using Google's open-source Material Web components (`@material/web`) from npm, plus local SVG charts for the data visualization layer. The Python server remains a narrow repo indexer/API and static host for the built app.

For frontend development, run the API and Vite dev server in separate terminals:

```bash
cd apps/research-cockpit
npm run api
npm run dev
```

Then open `http://127.0.0.1:8765` in the Codex in-app browser.

## Codex Workflow

The cockpit is read-only in v1. Use the Agent Actions panel to generate structured prompts for the active Codex thread. Paste the prompt back into Codex so the agent can inspect files, run tools, and make edits under the normal repo workflow.

This keeps research mutations explicit and reviewable while giving the user and Codex a shared visual surface.

## Validation

```bash
cd apps/research-cockpit
npm run check
npm run build
cd ../..
python3 -m unittest discover -s apps/research-cockpit/tests
openspec validate --all --strict
```
