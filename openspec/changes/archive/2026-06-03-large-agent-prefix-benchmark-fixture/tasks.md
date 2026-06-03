## 1. Spec And Archive Hygiene

- [x] 1.1 Sync and archive the completed benchmark progress summary change.
- [x] 1.2 Create the large-prefix fixture OpenSpec artifacts and validate them.

## 2. Fixture Generator

- [x] 2.1 Implement a deterministic large-prefix fixture generator with target byte sizes.
- [x] 2.2 Add allowlisted context collection and generated expansion metadata.
- [x] 2.3 Add secret-pattern, prefix-boundary, and context-budget checks.
- [x] 2.4 Generate 16 KB, 32 KB, and 64 KB Printy large-prefix fixture variants.

## 3. Tests And Docs

- [x] 3.1 Add focused tests for size targeting, volatile preservation, and safety failures.
- [x] 3.2 Document the large-prefix benchmark ladder and DushyantPC run commands.

## 4. Validation And PC Runs

- [x] 4.1 Run local py_compile, unit tests, fixture dry runs, summarizer checks, and OpenSpec validation.
- [x] 4.2 Refresh the DushyantPC benchmark working tree with the generated fixtures and generator.
- [x] 4.3 Run the large-prefix benchmark ladder on DushyantPC as far as context/runtime allows.
- [x] 4.4 Copy result JSONs back into the Mac/Git repo and summarize the evidence.
