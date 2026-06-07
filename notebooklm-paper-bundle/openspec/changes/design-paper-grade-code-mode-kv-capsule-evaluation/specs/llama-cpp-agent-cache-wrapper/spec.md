## MODIFIED Requirements

### Requirement: Record Code-mode KV capsule route metadata
Paper-facing model runs SHALL record enough llama.cpp, model, and capsule metadata to audit restored-state behavior.

#### Scenario: Paper run emits restored capsule record
- **WHEN** `code_mode_restored_kv_capsule` runs in a paper-grade campaign
- **THEN** the record includes model profile, model path/hash where practical, quantization, tokenizer/template notes, llama.cpp version/hash, DLL path/name, state route requested/effective, sequence id, capsule bytes, save/restore timing, restored token count, and generated-token hash where available

#### Scenario: Paper run emits readiness record
- **WHEN** the campaign begins execution on DushyantPC
- **THEN** readiness output records GPU status, duplicate process status, model profile resolution, sequence-state symbol availability, raw-path ignore status, and command provenance before broad execution
