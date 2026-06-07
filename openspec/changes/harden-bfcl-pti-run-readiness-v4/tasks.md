## 1. OpenSpec Gate

- [ ] 1.1 Create v4 run-readiness OpenSpec proposal, design, tasks, and spec delta.
- [ ] 1.2 Validate `openspec validate harden-bfcl-pti-run-readiness-v4 --type change --strict`.
- [ ] 1.3 Validate `openspec validate --all --strict`.

## 2. Failure Taxonomy

- [ ] 2.1 Add a script or documented command that summarizes the latest 15-case weak-category smoke into a no-cheat failure taxonomy.
- [ ] 2.2 Classify remaining failures as model-owned, harness-owned, or unknown.
- [ ] 2.3 Commit the taxonomy artifact under the BFCL official lane or paper calibration artifacts.

## 3. TDD For Compiler Diagnostics

- [ ] 3.1 Add failing tests for precise missing required field diagnostics.
- [ ] 3.2 Add failing tests for nested schema path/type diagnostics.
- [ ] 3.3 Add failing tests for enum exact-copy diagnostics.
- [ ] 3.4 Add failing tests for identifier literal-copy diagnostics.
- [ ] 3.5 Add failing tests for unknown/ambiguous function diagnostics.
- [ ] 3.6 Add failing tests for request-derived call-count diagnostics.
- [ ] 3.7 Add failing tests proving diagnostics do not accept or emit expected answers.

## 4. TDD For Stepwise Repair

- [ ] 4.1 Add failing tests for structural repair prompts with slot-level preserve/repair/reconsider plans.
- [ ] 4.2 Add failing tests for plan repair prompts after structural repair.
- [ ] 4.3 Add failing tests for complete final call-list output contracts.
- [ ] 4.4 Add failing tests for one empty/unparseable repair retry.
- [ ] 4.5 Add failing tests that repair cannot damage schema-valid preserved calls without a visible-schema reason.
- [ ] 4.6 Add failing tests proving repair prompts exclude `possible_answer`, `expected_answer`, `expected_calls`, `ground_truth`, category labels, and scorer hints.

## 5. Implementation

- [ ] 5.1 Implement richer compiler diagnostic records.
- [ ] 5.2 Implement compact visible schema/signature rendering.
- [ ] 5.3 Implement generic PTI pre-submit checklist in the stable prefix.
- [ ] 5.4 Implement stepwise structural/plan repair prompt builders.
- [ ] 5.5 Wire stepwise repair into the active BFCL restored-KV model loop.
- [ ] 5.6 Preserve valid call slots through repair and trace whether preserved calls changed.
- [ ] 5.7 Keep export language-aware without answer-key transformations.

## 6. Local Validation

- [ ] 6.1 Run focused BFCL/PTI unit tests.
- [ ] 6.2 Run Python compile for changed benchmark scripts.
- [ ] 6.3 Run OpenSpec change validation.
- [ ] 6.4 Run full OpenSpec strict validation.

## 7. DushyantPC Step Smokes

- [ ] 7.1 Sync the committed or staged implementation to DushyantPC without destructive checkout commands.
- [ ] 7.2 Run DushyantPC unit smoke.
- [ ] 7.3 Run DushyantPC missing-required-argument micro-smoke.
- [ ] 7.4 Run DushyantPC nested-type/argument-shape micro-smoke.
- [ ] 7.5 Run DushyantPC enum/literal-copy micro-smoke.
- [ ] 7.6 Run DushyantPC function-choice micro-smoke.
- [ ] 7.7 Run DushyantPC call-count micro-smoke.
- [ ] 7.8 Run DushyantPC incomplete-output/empty-repair retry micro-smoke.

## 8. Run-Readiness Gates

- [ ] 8.1 Run DushyantPC 15-case weak-category restored-KV smoke.
- [ ] 8.2 Require at least `13/15`, `irrelevance 3/3`, no category below `2/3`, no unrecovered empty repairs, and no preserved-call damage.
- [ ] 8.3 If 15-case gate passes, run DushyantPC 50-case targeted restored-KV smoke.
- [ ] 8.4 Run official partial evaluator on the 50-case export.
- [ ] 8.5 Update failure taxonomy and readiness docs.
- [ ] 8.6 Only after the 50-case gate passes, mark the full `1390` non-live candidate rerun as approved to launch.

## 9. Documentation And Handoff

- [ ] 9.1 Document the no-cheat boundary in the official BFCL lane README.
- [ ] 9.2 Document the final smoke results and stop/go decision.
- [ ] 9.3 Commit and push the OpenSpec change plus implementation and smoke artifacts.
