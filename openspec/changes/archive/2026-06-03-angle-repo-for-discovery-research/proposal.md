## Why

The project should not only validate obvious SSD/KV-cache optimizations. It should deliberately search for non-obvious mechanisms and counter-consensus experiments while keeping enough rigor to distinguish real discoveries from measurement artifacts.

## What Changes

- Add a discovery-research playbook for generating, scoring, and testing strange or against-the-grain hypotheses.
- Update the paper roadmap so the research program explicitly includes high-risk experiment lanes.
- Update `AGENTS.md` so future agents do not only optimize known cache paths; they must surface surprising hypotheses, confounders, and falsification plans.
- Cross-link the discovery playbook from the README and decision log.

## Capabilities

### New Capabilities

### Modified Capabilities

- `research-positioning-doc`: Adds discovery-research guidance for underexplored, counter-consensus, and high-risk experiment design.

## Impact

- Documentation-only.
- No runtime code, benchmark behavior, APIs, or dependencies change.
- Future research work should include both conservative baselines and at least one clearly stated non-obvious hypothesis when the goal is discovery.
