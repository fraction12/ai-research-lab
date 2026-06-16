# Final Paper Cleanup Checklist - 2026-06-16

Goal: turn the current arXiv draft from a working technical draft into a clean, reviewer-safe final paper without overclaiming.

## 0. Ground Rules

- [x] Do not change core numbers unless the backing artifact is rechecked.
- [x] Keep the claim narrow: local repeated tool-use workloads, selected BFCL-derived cohort, Gemma 4 12B route.
- [x] Preserve the key mechanism distinction: hidden state is not a summary.
- [x] Avoid marketing names where plain technical wording works; define KV Capsule and PTI once, then use them consistently.
- [x] Every major claim should point to a table, figure, artifact, or explicit limitation.

## 1. Title, Abstract, and Framing

- [x] Decide final title: current title is clear, but consider whether "Attention-State Reuse" is too broad without "Quality-Gated" or "Local Tool-Using Agents" in the title.
- [x] Shorten the abstract by 15-25 percent.
- [x] Move implementation-heavy numbers out of the abstract unless they are the central claim.
- [x] Make the abstract's final sentence state the exact narrow contribution, not a generalized systems conclusion.
- [x] Ensure the first page makes clear this is not an official BFCL leaderboard submission.

## 2. Introduction

- [x] Strengthen the opening problem: repeated local agents resend stable context and summarize it back into lossy text.
- [x] Add one crisp example of stable context: tool schema + runtime rule + output contract.
- [x] Explain why summarization is the wrong object to preserve for stable tool contracts.
- [x] Tighten contribution list so each item is distinct:
  - mechanism/control ladder,
  - constrained tool interface,
  - negative controls,
  - repeated-work systems comparison.
- [x] Remove or soften any wording that implies hosted frontier-model comparison.

## 3. Related Work

- [x] Separate "serving KV reuse" from "agent memory" more sharply.
- [x] Add a one-sentence gap after each related-work paragraph explaining what this paper does differently.
- [x] Check whether vLLM/SGLang citations are enough for prefix/KV reuse, or whether LMCache/CacheBlend-style work should be cited if already in the repo's research harvest.
- [x] Keep BFCL/ToolLLM/Gorilla framing as evaluation context, not benchmark novelty.
- [x] Avoid claiming prior memory systems cannot preserve useful information; say they preserve it as visible text, which is a different representation.

## 4. Method

- [x] Add a compact pipeline diagram or pseudocode box if space allows: build prefix -> evaluate -> save state -> restore -> append task tail -> parse tool plan.
- [x] Define exactly what is saved: llama.cpp sequence/KV state, not model weights or external memory.
- [x] Define what is in the stable prefix and what is in the tail.
- [x] Explain the quality gate before results: when a capsule is valid, invalid, or rejected.
- [x] Clarify PTI without making it sound like a general new tool-calling standard.
- [ ] State the decoding/generation settings if artifact-backed and concise.

## 5. Results

- [x] Put the control-ladder result before repeated-work claims, since it establishes mechanism credibility.
- [x] Make "semantic preservation, not speed" impossible to miss in the restored-KV mechanism subsection.
- [x] Add a small negative-control table or sentence with exact leak counts: fresh-tail 0, wrong-capsule 0.
- [ ] Recheck whether "native/restored hash parity was 100/100" is fully supported and explain what hash parity means.
- [x] Ensure direct visible tools 91/100 and compact visible evidence 19/100 are framed as ablations, not universal baselines.
- [x] Make the repeated-work table caption explicitly say route-reported telemetry is not clean per-task accounting.
- [x] Consider moving "245,774,883 visible input tokens" out of abstract/body prose and into table only, because it looks suspicious without context.

## 6. Figures and Tables

- [ ] Verify all figures fit within margins on the compiled PDF.
- [ ] Check that every figure has a caption that explains what not to infer.
- [x] Ensure table labels and references resolve cleanly.
- [ ] Check if Figure 02/03/06 are unused in the LaTeX draft; either include them intentionally or omit from arXiv source package.
- [ ] Confirm figure order matches reader flow.
- [x] Run a final overfull-box scan and fix anything beyond tiny harmless warnings.

## 7. Limitations and Reviewer Objections

- [x] Expand limitations into shorter paragraphs instead of one dense block.
- [x] Add explicit limitation: selected cohort was quality-gated, so pass rates are not distribution-wide BFCL performance.
- [x] Add explicit limitation: raw Windows Codex session JSONL is absent from checkout, so compaction-event analysis relies on tracked summaries.
- [x] Add explicit limitation: baseline prompt is not prompt-identical to KV route.
- [x] Add explicit limitation: the mechanism run does not prove restored KV is faster than live append.
- [x] Add explicit limitation: safety of wrong-capsule/fresh-tail controls is scoped only to this cohort.
- [ ] Consider a short "Threats to Validity" section if the paper feels too defensive in prose.

## 8. Artifacts and Data Availability

- [x] Keep the PDF version margin-safe: no long inline paths that spill over the right margin.
- [x] Add a concise repository map in prose and keep exact paths in README/artifact manifests.
- [ ] Confirm the public GitHub repo contains the arXiv source, figures, claims ledger, data ledger, and result summaries.
- [ ] Confirm no raw secrets or private keys appear in committed artifacts.
- [ ] Decide whether to add a release tag or archived snapshot before arXiv submission.

## 9. LaTeX / arXiv Package Hygiene

- [ ] Clean LaTeX build byproducts before final packaging.
- [x] Confirm `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` passes.
- [x] Confirm bibliography resolves after a clean build.
- [ ] Confirm `main.pdf` has no obvious margin spills, missing figures, or unresolved references.
- [ ] Check arXiv source package includes only required source files, bibliography, and figures.
- [ ] Decide whether to include compiled `main.pdf` in repo while excluding build byproducts.

## 10. Final Editorial Pass

- [x] Replace internal phrases like "tested Codex/Ollama route" with reviewer-readable wording where possible.
- [x] Cut repeated caveats where one precise caveat is enough.
- [x] Make every acronym defined once: KV, PTI, BFCL.
- [ ] Read the paper aloud once for awkward sentences and "lab notebook" phrasing.
- [ ] Ensure tone is technical, modest, and confident.
- [ ] Final acceptance test: a skeptical reviewer should be able to say "narrow, but credible" rather than "interesting, but overclaimed."

## Suggested Execution Order

1. Fix title/abstract/introduction framing.
2. Clean Method definitions and quality gate.
3. Tighten Results and captions.
4. Split and sharpen Limitations.
5. Final margin/build/reference pass.
6. Create a repo tag or release snapshot for the arXiv version.
