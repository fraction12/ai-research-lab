# arXiv Source Package

This directory contains the first arXiv-facing source draft for the attention-state reuse paper.

Repository snapshot tag: `arxiv-v1.0`.

Files:

- `main.tex` - paper draft converted from the paper-site draft and tightened around the arXiv claim frame.
- `references.bib` - bibliography for current cited work.
- `figures/` - only the PDF figures included by `main.tex`: `figure-01-control-ladder.pdf`, `figure-04-visible-input-tokens.pdf`, `figure-05-wall-time.pdf`, `figure-07-initial-official-bfcl.pdf`, and `figure-08-bfcl-reference-comparison.pdf`.

Build target:

```bash
latexmk -pdf main.tex
```

Local build status: `texlive` was installed through Homebrew on 2026-06-16. `latexmk` and `pdflatex` are on PATH, and `main.tex` compiles to `main.pdf` from a clean copy of this package.

Provenance:

- Main draft source: `paper-site/scripts/build_paper_site.py`
- Generated HTML: `paper-site/site/index.html`
- Claims ledger: `paper-artifacts/paper-claims-ledger.md`
- Data ledger: `paper-artifacts/paper-data-ledger.md`
- Edit checklist: `paper-artifacts/arxiv-edit-checklist-2026-06-16.md`
