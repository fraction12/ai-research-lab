## ADDED Requirements

### Requirement: Validate restored-prefix full-resend reuse
The system SHALL provide a focused restored-prefix full-resend probe that preserves full prompt visibility while measuring whether a restored llama.cpp slot reduces prompt processing for exact-prefix matches.

#### Scenario: Run exact-prefix full-resend probe
- **WHEN** the restored-prefix full-resend probe runs on a synthetic case
- **THEN** it runs a cold full-prompt baseline with no restored slot
- **AND** it primes and saves the stable prefix slot
- **AND** it restores the matching slot before resending the full prompt
- **AND** it records correctness, raw output, parsed answer, prompt hashes, timing, token counts, and slot save/restore telemetry for each step

#### Scenario: Check exact-prefix safety controls
- **WHEN** the restored-prefix full-resend probe runs perturbation or wrong-slot controls
- **THEN** it verifies that the model answers according to the visible full prompt
- **AND** it records whether restored state leaked the original or wrong-slot answer into the output
- **AND** it records whether prompt-processing timing/token counts differ from the exact-match restored-full run

#### Scenario: Gate GraphWalks follow-up
- **WHEN** the tiny synthetic restored-prefix full-resend probe completes
- **THEN** the system classifies the result as correctness-safe with useful acceleration, correctness-safe without useful acceleration, correctness drift, unsafe cache leakage, or runtime failure
- **AND** it only recommends running the six selected GraphWalks cases when synthetic correctness parity, safety controls, and useful acceleration evidence pass

#### Scenario: Preserve mechanism artifacts
- **WHEN** the restored-prefix full-resend probe writes raw outputs, prompts, logs, slot files, and summaries
- **THEN** raw artifacts are written under ignored Track 01 benchmark result/cache paths
- **AND** committed Track 02 artifacts record exact raw paths, hashes, commands, model/backend metadata, run classifications, and next-step decisions
