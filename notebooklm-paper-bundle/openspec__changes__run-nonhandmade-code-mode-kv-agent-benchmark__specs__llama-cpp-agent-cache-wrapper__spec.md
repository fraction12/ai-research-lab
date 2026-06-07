## ADDED Requirements

### Requirement: Emit Code-mode KV capsule parity telemetry
The llama.cpp cache wrapper and benchmark runner SHALL expose enough telemetry to compare Code-mode full-visible, native live append, restored capsule append, fresh-tail negative, and wrong-capsule negative controls.

#### Scenario: Run restored Code-mode capsule control
- **WHEN** a non-handmade benchmark case runs `code_mode_restored_kv_capsule`
- **THEN** the record includes capsule route, sequence id, saved/restored token counts, n_past, capsule file bytes, capsule hash where practical, save timing, restore timing, prompt eval timing, decode timing, generated token ids hash where available, normalized response hash, and whether the volatile tail resent stable prefix text

#### Scenario: Run live/restored parity check
- **WHEN** a selected case has both `code_mode_native_live_append` and `code_mode_restored_kv_capsule` outputs
- **THEN** the runner records quality parity, response-hash parity, generated-token-hash parity where available, and restored-only failure classification
