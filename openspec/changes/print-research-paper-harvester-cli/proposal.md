## Why

Research threads need a reliable way to collect paper findings, source links, provider payloads, and prior-art evidence without repeating ad hoc web searches. This is an internal research workflow need, not a product or reusable commercial CLI effort.

## What Changes

- Use CLI Printing Press and printed provider CLIs as the primary paper-finding toolchain.
- Treat any generated research-paper harvester CLI as an internal lab tool for collecting research evidence.
- Keep Printing Press orchestration skills in Codex user scope.
- Keep focused research/source skills for this lab in project scope under `.codex/skills/`.
- Start with the current paper-finding path: arXiv first through `arxiv-pp-cli` / project-local `pp-arxiv`, but stop on provider rate limits.
- Use OpenAlex through `openalex-pp-cli` / project-local `pp-openalex` for exact arXiv DOI-form metadata lookups when the arXiv Atom API is rate-limited.
- Preserve raw provider outputs, command invocations, timestamps, and source URLs as research evidence.
- Do not build or keep a custom standalone product scaffold unless Printing Press output later proves it is the smallest useful way to do the job.

## Capabilities

### New Capabilities

- `research-paper-harvester-workflow`: Internal Printing Press-assisted workflow for collecting, preserving, and exporting research paper findings.

### Modified Capabilities

## Impact

- Adds/pivots OpenSpec guidance for an internal Printing Press workflow with an OpenAlex fallback path for arXiv API throttling.
- Installs user-scope Printing Press skills outside the repo.
- Adds project-scope paper-source skills under `.codex/skills/`.
- Removes the previously drafted custom `tools/researchlib/` scaffold and its tests.
- Keeps future generated CLI artifacts out of global scope unless explicitly approved.
