## ADDED Requirements

### Requirement: Preserve external benchmark provenance for Code-mode KV control ladders
Correctness workflows SHALL preserve external benchmark provenance, deterministic transforms, baseline-pass gating, and per-control scoring when used for non-handmade Code-mode + KV capsule experiments.

#### Scenario: Materialize external tool-use benchmark cases
- **WHEN** the correctness workflow materializes BFCL, tau-bench/tau2-bench, or ToolSandbox cases for the Code-mode KV ladder
- **THEN** each case records source benchmark, revision, row id or deterministic offset, row hash, benchmark category, source fields used and excluded, transform version, scorer version, stable prefix hash, volatile tail hash, and full prompt hash

#### Scenario: Score external control ladder
- **WHEN** the correctness workflow scores a non-handmade Code-mode KV control matrix
- **THEN** it records benchmark scorer output per control
- **AND** records whether each row is primary-eligible, diagnostic-only, leaked, unsupported, or blocked
