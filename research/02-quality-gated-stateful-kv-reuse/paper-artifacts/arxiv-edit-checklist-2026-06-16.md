# arXiv Edit Checklist

Created: 2026-06-16

Goal: turn the current HTML research draft into a defensible arXiv preprint without overclaiming the KV Capsule + PTI results.

## Claim Frame

- [x] Use `Attention-State Reuse for Local Tool-Using Agents` as the main paper frame.
- [x] Treat `KV Capsule` and `PTI` as system components, not the full scientific claim.
- [x] Split the mechanism claim from the repeated-work systems claim.
- [x] State that the work is not a hosted-model comparison and not a prompt-identical compaction comparison.
- [x] Preserve the central sentence: the capsule is not a summary; it is the model's computed attention state after reading the prefix.

## Main Draft Edits

- [x] Shorten the abstract so it leads with the contribution and only the essential numbers.
- [x] Define PTI first as a constrained structured local tool interface, then introduce the acronym.
- [x] Keep the selected 100-case control ladder as the main mechanism result.
- [x] Keep the repeated-work stream as the main practical systems result.
- [x] Move BFCL leaderboard-style comparison language out of the main Results flow and into calibration/appendix framing.
- [x] Convert the draft into an arXiv-facing LaTeX source package.
- [x] Rewrite figure captions in paper voice for the first LaTeX source pass.
- [x] Add an initial reproducibility/data appendix with artifact provenance and calibration caveats.

## Reviewer Defense

- [x] Selected cohort is explicitly described as quality-gated and BFCL-derived.
- [x] Full BFCL non-live run is explicitly calibration, not a public leaderboard submission.
- [x] Mechanism latency result says restored KV was slower than full visible/native append in that run.
- [x] Baseline visible-token telemetry is described as cumulative reported burden, not clean per-task accounting.
- [x] Codex/Ollama baseline is framed as a practical local-agent route, not a prompt-identical scientific control.
- [x] PTI is framed as narrower than arbitrary programmatic tool calling.

## arXiv Package Still Needed

- [x] `main.tex`
- [x] `references.bib`
- [x] Figure assets copied into an arXiv-safe `figures/` directory.
- [x] README or appendix note describing local artifact provenance.
- [x] Build check with `latexmk` or equivalent. `brew install texlive` installed `latexmk` and `pdflatex`; `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` succeeds.
- [ ] Final overclaim audit against `paper-claims-ledger.md`.
