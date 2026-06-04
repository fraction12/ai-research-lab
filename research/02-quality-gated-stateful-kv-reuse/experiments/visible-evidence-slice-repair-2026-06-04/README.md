# Visible Evidence Slice Repair

Date: 2026-06-04

Machine: DushyantPC

Scope: six selected GraphWalks `parents` cases only. This is not a broad benchmark.

## Result

Adding a small visible evidence slice to the hidden-prefix/session-tail path improved correctness from `0/6` to `4/6`.

| Control | Cases | Passes | Mean score |
| --- | ---: | ---: | ---: |
| Hidden prefix + original session tail | 6 | 0 | 0.0 |
| Hidden prefix + visible extracted evidence tail | 6 | 4 | 0.6666666666666666 |
| Imported verified edge-evidence control | 6 | 6 | 1.0 |

## Per-Case Comparison

| Case | Hidden score | Visible score | Prompt token delta | Prompt ms delta | Evidence edges | Evidence bytes | Repaired |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `graphwalks-6` | 0.0 | 1.0 | 96 | 1547.484 | 3 | 74 | yes |
| `graphwalks-9` | 0.0 | 1.0 | 94 | 1473.947 | 3 | 74 | yes |
| `graphwalks-11` | 0.0 | 1.0 | 61 | 952.567 | 1 | 24 | yes |
| `graphwalks-13` | 0.0 | 1.0 | 61 | 1036.242 | 1 | 24 | yes |
| `graphwalks-16` | 0.0 | 0.0 | 135 | 2082.340 | 6 | 149 | no |
| `graphwalks-19` | 0.0 | 0.0 | 107 | 1679.690 | 4 | 99 | no |

Aggregate prompt overhead from the visible evidence tail:

- Prompt tokens: +554 total, +92.33333333333333 mean per case.
- Prompt processing time: +8772.27 ms total, +1462.045 ms mean per case.
- Visible evidence lines: 18 total, 3.0 mean per case.
- Visible evidence bytes: 444 total, 74.0 mean per case.
- Added tail bytes including the evidence wrapper: 2148 total, 358.0 mean per case.

## What Failed

The two remaining visible-evidence failures were `graphwalks-16` and `graphwalks-19`. In both, the extracted evidence slice contained the correct incoming edge lines, but GPT-OSS generated a verbose explanation and hit the `--predict 192` cap before closing the JSON answer. That makes the immediate remaining issue a prompt protocol / verbosity problem, not an evidence extraction miss.

## Interpretation

This is a strong Track 02 signal, but not pure KV reuse. Hidden prefix alone did not preserve usable GraphWalks semantics for the tail. A tiny role-aware visible slice repaired four cases and exposed a narrower remaining failure mode for the two largest slices.

The next smallest test is a compact-answer visible evidence tail on `graphwalks-16` and `graphwalks-19`, keeping the same hidden prefix, model, runner, and token cap.
