# kv-capsule-semantic-continuation Specification Delta

## ADDED Requirements

### Requirement: Require native/server parity before KV capsule reruns
The KV capsule semantic-continuation workflow SHALL treat native full-visible server parity as a prerequisite for interpreting any native live append or restored capsule result.

#### Scenario: Preserve prior blocker result
- **WHEN** a native/server parity bridge is planned or run
- **THEN** it preserves `research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-semantic-continuation-2026-06-04/` as prior evidence
- **AND** it does not rewrite the prior `native_prompt_generation_protocol_blocker` / `restored_capsule_semantics_uninterpretable` result

#### Scenario: Block capsule interpretation until parity passes
- **WHEN** native full-visible generation has not yet matched refreshed server full-visible behavior on the codeword baseline
- **THEN** `native_live_append_tail_only` and `native_restored_capsule_append_tail_only` are not run or are treated as uninterpretable
- **AND** the workflow records `native_server_parity_failure` or a narrower protocol blocker instead of a KV-capsule semantic failure

#### Scenario: Resume capsule ladder after parity passes
- **WHEN** native full-visible parity passes on the refreshed codeword set
- **THEN** the workflow may rerun only Family 1 codeword capsule controls first
- **AND** `native_live_append_tail_only` must pass before `native_restored_capsule_append_tail_only` is interpreted
