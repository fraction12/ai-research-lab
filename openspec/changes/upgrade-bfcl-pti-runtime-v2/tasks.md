## 1. Spec And Baseline

- [x] Record official BFCL v1 baseline: `969 / 1390 = 69.88%`.
- [x] Document no-cheat PTI v2 boundary in OpenSpec.
- [x] Add PTI v2 implementation metadata to exports/control packets.

## 2. Language-Aware Export

- [x] Add failing tests for Python, JavaScript, and Java BFCL prompt-result rendering.
- [x] Implement language-aware literal and call rendering.
- [x] Regenerate export-only smoke artifacts from existing model records.

## 3. Schema-Aware PTI Validation

- [x] Add tests for unknown functions, missing required args, unexpected args, and primitive type mismatches.
- [x] Implement generic schema validation using only the BFCL function catalog.
- [x] Expose validation telemetry without using expected answers.

## 4. PTI Prompt Contract

- [x] Add tests that the stable prefix includes abstention, exact call count, no helper calls, exact schema names, and optional/default rules.
- [x] Update the BFCL PTI stable-prefix contract.

## 5. Smokes

- [x] Run local unit tests for official exporter and BFCL adapter.
- [x] Run OpenSpec strict validation for this change and all specs.
- [x] Run export-only smoke and inspect Java/JavaScript result dialects.
- [x] Run targeted DushyantPC smoke before any full BFCL rerun.
