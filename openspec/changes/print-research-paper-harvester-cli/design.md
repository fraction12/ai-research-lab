## Context

The lab is doing research, not building a new product. The goal is to use Printing Press properly so the machine can act as our research hand: find papers, collect metadata, preserve raw outputs, keep source trails, and help export references into track docs or negative-space notes.

The earlier `researchlib` scaffold was the wrong emphasis. It treated the workflow like a standalone local product. That scaffold has been removed. The correct center of gravity is Printing Press and focused printed CLIs.

Installed and verified machine/user setup:

- `brew install go` installed Go 1.26.3, then `brew upgrade go` moved the machine to Go 1.26.4 after `govulncheck` flagged fixed standard-library vulnerabilities in Go 1.26.3.
- `cli-printing-press --version` reports `cli-printing-press 4.20.1`.
- `printing-press-library --version` reports `0.1.15`.
- `arxiv-pp-cli --version` reports `arxiv-pp-cli 1.0.0`.
- `openalex-pp-cli --version` reports `openalex-pp-cli 1.0.0`.
- `arxiv-pp-cli doctor --agent` reports API reachable and no auth required.
- `openalex-pp-cli doctor --agent` reports API reachable but `OPENALEX_API_KEY` is not configured.
- `openalex-pp-cli works get https://doi.org/10.48550/arxiv.<id>` works without an API key for exact arXiv DOI-form metadata lookups.
- User-scope Codex skills installed: `printing-press`, `printing-press-amend`, `printing-press-catalog`, `printing-press-import`, `printing-press-output-review`, `printing-press-polish`, `printing-press-publish`, `printing-press-reprint`, `printing-press-retro`, and `printing-press-score`.
- Project-scope Codex skills installed for this repo: `pp-arxiv` and `pp-openalex`.

## Goals / Non-Goals

**Goals:**

- Use Printing Press as the primary mechanism for paper-harvesting CLI work.
- Start with arXiv because the current research scans are arXiv-heavy and `arxiv-pp-cli` is installed.
- Keep provider-specific research skills project-local when they are for this lab's research workflow.
- Preserve command lines, raw JSON/output files, source URLs, query text, timestamps, and provider status.
- Make the workflow useful for Track 02 and negative-space scans before expanding provider coverage.

**Non-Goals:**

- Do not build a standalone product, marketable CLI, or general library manager.
- Do not keep the custom `researchlib` scaffold.
- Do not fetch PDFs/full text by default.
- Do not put generated/focused research-harvester skills in user scope unless explicitly approved.
- Do not block arXiv-first work on OpenAlex or Semantic Scholar API keys.

## Decisions

- Use Printing Press first, not custom code first.
  - Rationale: the user's goal is to print/use a CLI that gets research-paper collection done, not hand-build a product.

- Keep global/user scope for Printing Press orchestration skills only.
  - Rationale: these are general machine-level capabilities useful across projects.

- Keep research-source skills project scoped.
  - Rationale: the generated/focused paper-harvester behavior is tied to this lab's research workflow and should travel with this repo.

- Use `pp-arxiv` and `arxiv-pp-cli` as the first paper-finding path.
  - Rationale: arXiv is enough for the current negative-space and Track 02 paper trails, and it does not require keys.

- Use `pp-openalex` for exact arXiv DOI-form metadata when arXiv Atom is throttled.
  - Rationale: OpenAlex exact work lookup works without a key for the current arXiv-heavy scan, while the OpenAlex rate-limit endpoint still requires an API key.

- Record evidence files before optimizing any local database layer.
  - Rationale: for research, durable provenance matters more than a polished internal data model.

## Printing Press Workflow Shape

1. Use project-local `pp-arxiv` / `arxiv-pp-cli` to search and fetch exact papers or bounded category/topic results.
2. If arXiv Atom is rate-limited, use project-local `pp-openalex` / `openalex-pp-cli works get https://doi.org/10.48550/arxiv.<id>` to collect exact metadata.
3. Use arXiv HTML pages only as a rate-safe confirmation fallback, not for PDF/full-text download.
4. Save raw provider JSON/output into a dated research artifact folder for the active track or negative-space scan.
5. Normalize only enough for immediate research use: title, authors, year/date, identifiers, source URL, provider, query, and why it matters.
6. Export references into track docs only after a paper is actually used as evidence.
7. Print a focused internal `paper-harvester` CLI with `/printing-press` / `cli-printing-press`, using a narrow generated API scaffold plus hand-authored workflow command only where the printed OpenAlex/arXiv pieces need composition.
8. Install that generated focused skill into `.codex/skills/`, not user scope.

## Risks / Trade-offs

- arXiv rate limits or times out -> Use bounded queries, retry later, record failed attempts, and fall back to OpenAlex DOI-form metadata plus arXiv HTML confirmation.
- Printed provider CLIs do not compose enough -> Print a narrow internal harvester CLI after we see the actual workflow gaps.
- Provider output formats change -> Preserve raw outputs and command versions in evidence folders.
- Generated skill scope leaks globally -> Install focused/generated research skills into this repo's `.codex/skills/` only.
- Overbuilding returns -> Stop at "gets papers collected with provenance"; do not add product features without a research need.

## Open Questions

- What should the printed internal CLI be called? Decision: `paper-harvester`, because it describes the job without implying a product.
- Which corpus should be harvested first? Recommendation: the existing negative-space scan anchors, then Track 02 stateful KV reuse queries.
- How much of the composed workflow can be generated directly from the spec? The OpenAlex lookup endpoint should be generated; the cross-provider harvest/summary command may need a small hand-authored Cobra command on top of the printed scaffold.
