## Context

The user identified a real DeepClean campaign in the LightningITB repo as the strongest available prompt source. The archived design records why scoped synthesis replaced whole-repo synthesis, why safe/fix-ready candidates went first, why behavior tests were required before refactors, why PRs were the unit of progress, and why the ledger mattered more than ignored `.deepclean` state.

The raw original chat prompt is not stored verbatim, so this repo should treat the fixture as a sanitized prompt distilled from source artifacts.

## Goals / Non-Goals

**Goals:**

- Add a realistic DeepClean campaign benchmark fixture.
- Preserve source provenance and campaign decisions inside the fixture metadata.
- Compare the realistic fixture against the existing synthetic fixture using the same harness.

**Non-Goals:**

- Copy LightningITB private `.deepclean` artifacts.
- Store raw chat transcripts.
- Automate DeepClean or GitHub actions from this benchmark.

## Decisions

- **Keep this as a separate fixture.** The synthetic fixture remains useful as a small controlled baseline, while the LightningITB fixture carries real workflow texture.
- **Use the user's sanitized prompt as the main stable block.** This respects the provided prompt and avoids inventing unverified raw transcript content.
- **Add source notes in fixture metadata.** The benchmark harness already stores fixture hashes, so provenance in the fixture is enough for traceability.

## Risks / Trade-offs

- **The fixture is still sanitized.** Mitigation: label it as distilled, not verbatim.
- **Timing can vary run to run.** Mitigation: record measured numbers in docs and keep JSON artifacts local.
- **The fixture is shorter than a full Codex session.** Mitigation: use this as a better baseline, then scale with larger real prompt bundles later.
