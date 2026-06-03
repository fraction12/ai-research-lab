# Research Index

This folder holds the lab's active research tracks and idea archive.

## Tracks

| Track | Purpose | Status |
| --- | --- | --- |
| `01-ssd-native-inference-current` | Preserve the current Flashcache/SSD-native inference prototype, evidence, docs, and tests. | Existing work moved intact. |
| `02-quality-gated-stateful-kv-reuse` | Investigate correctness contracts and fallback policy for stateful KV/session reuse. | Next main research candidate. |
| `03-role-aware-context-compilation` | Explore compiling agent context into roles and intentionally recomputing quality-critical anchors. | High-risk discovery track. |
| `04-negative-space-ideas` | Store frontier scans and candidate gaps that may become future tracks. | Living research ideas folder. |

## Track Rules

- Each track should have its own README.
- Each serious experiment should record hypothesis, baseline, controls, metrics, confounders, raw artifact path, and stop rule.
- Track-specific references should stay with the track or with the negative-space idea that introduced them.
- Root OpenSpec remains the lab-level workflow for structural changes.

## Promotion Path

```text
negative-space note
-> discovery hypothesis
-> smallest falsifying test
-> reproducible track artifact
-> paper roadmap or abandoned result
```
