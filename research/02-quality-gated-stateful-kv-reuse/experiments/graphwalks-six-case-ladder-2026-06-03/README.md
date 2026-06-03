# GraphWalks Six-Case Ladder Setup

Date: 2026-06-03

This directory records the setup and control-coverage preflight for the focused Track 02 GraphWalks ladder. No live model experiments have been run in this phase.

## Scope

The fixed case set is:

- `graphwalks-6`
- `graphwalks-9`
- `graphwalks-11`
- `graphwalks-13`
- `graphwalks-16`
- `graphwalks-19`

These are the six selected GraphWalks cases from the 2026-06-03 correctness parity evidence where full prompt passed and session-tail failed.

## Setup Result

Prompt-bearing inputs were re-materialized locally under the ignored Track 01 benchmark input directory:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/
```

A no-model `--dry-run` checked command plumbing for `run --mode both --answer-protocol json-answer` and wrote ignored skeleton response/score files under:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/
```

## Current Boundary

This setup phase does not classify failures yet. The next approved phase should run the focused controls in order: full-prompt replay variance, visible-prefix/session-formatted control, stronger tail hints, reset/restore sanity, scorer/parser brittleness, and stronger-model control if practical.
