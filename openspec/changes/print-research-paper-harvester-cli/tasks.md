## 1. Pivot Scope

- [x] 1.1 Remove the custom `tools/researchlib/` scaffold and tests.
- [x] 1.2 Rewrite proposal/design/spec around an internal Printing Press-assisted paper-harvesting workflow.
- [x] 1.3 Make clear this is not a product or marketable standalone CLI.

## 2. Printing Press Setup

- [x] 2.1 Verify `cli-printing-press`, `printing-press-library`, `arxiv-pp-cli`, and `openalex-pp-cli` are installed.
- [x] 2.2 Install Printing Press orchestration skills into Codex user scope.
- [x] 2.3 Install paper-source focused skills into this repo's project scope.
- [x] 2.4 Verify project-scope skills are visible in `.codex/skills/`.

## 3. First Paper-Finding Path

- [x] 3.1 Use `pp-arxiv` / `arxiv-pp-cli` as the first research-paper finding path.
- [x] 3.2 Harvest the current negative-space scan source anchors or Track 02 stateful KV reuse queries. Completed for 11 negative-space anchors through `openalex-pp-cli works get https://doi.org/10.48550/arxiv.<id>` plus arXiv HTML confirmation after arXiv Atom rate limits.
- [x] 3.3 Save raw outputs, command lines, timestamps, and source URLs in a track-appropriate evidence folder.
- [x] 3.4 Export only used references into the relevant track docs or negative-space note.

## 4. Validation

- [x] 4.1 Run `openspec validate --all --strict`.
- [x] 4.2 Run Printing Press and provider CLI version/doctor checks.
- [x] 4.3 Record OpenAlex API-key limitation for rate-limit status/higher-volume workflows, while exact arXiv DOI-form metadata lookup works without a key.

## 5. Printed Internal CLI

- [x] 5.1 Author a narrow Printing Press spec/research bundle for `paper-harvester`.
- [x] 5.2 Generate `paper-harvester` with `cli-printing-press`.
- [x] 5.3 Add the workflow command for OpenAlex arXiv DOI-form lookup plus arXiv HTML confirmation if generation does not provide it directly.
- [x] 5.4 Run build, shipcheck or the closest available verification set, and a live smoke harvest against the current negative-space anchors.
- [x] 5.5 Install the generated/focused `paper-harvester` skill into this repo's `.codex/skills/`.
