## Context

The repo currently mixes lab-level research posture with the original SSD-native inference code and benchmark artifacts at the root. The user wants the repo to become an AI research lab with separate research tracks and an ideas archive.

## Goals / Non-Goals

**Goals:**

- Make the root read as an AI research lab.
- Preserve the existing SSD-native work as a complete first research track.
- Create clear track folders for the next two research directions.
- Preserve existing dirty benchmark graph changes instead of reverting or overwriting them.
- Rename the GitHub repo and local folder to `ai-research-lab`.

**Non-Goals:**

- Do not rewrite the current benchmark or Flashcache code.
- Do not force every track into a final paper structure today.
- Do not move root OpenSpec out of place, because it is still the lab-level spec workflow.

## Decisions

- Use `research/01-ssd-native-inference-current/` for the current work.
  - Rationale: keeps the existing prototype, docs, tests, and evidence together.

- Use `research/02-quality-gated-stateful-kv-reuse/` for the next main paper candidate.
  - Rationale: gives the quality-gated KV project its own planning space without mixing it with the first prototype.

- Use `research/03-role-aware-context-compilation/` for the contrarian context-compilation plus intentional-recompute direction.
  - Rationale: separates this higher-risk idea from the near-term KV correctness track.

- Use `research/04-negative-space-ideas/` for frontier scans and research-gap notes.
  - Rationale: keeps idea discovery active without overcommitting every scan to a project track.

- Keep root OpenSpec and root AGENTS/README as lab-level artifacts.
  - Rationale: future changes should still use one workspace-level spec system.

## Risks / Trade-offs

- Moving paths may disrupt old commands -> Mitigation: add track READMEs with validation commands and update root docs.
- Existing uncommitted graph changes may get mixed into the reframe commit -> Mitigation: preserve them with the moved first track and mention them in the final summary.
- GitHub rename may fail if auth or repo settings block it -> Mitigation: validate with `gh repo view`, then update the remote URL manually if needed.
