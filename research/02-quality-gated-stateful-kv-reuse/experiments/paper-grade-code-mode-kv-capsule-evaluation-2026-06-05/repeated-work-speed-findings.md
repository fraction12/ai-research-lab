# Repeated-Work Speed Findings

Generated: 2026-06-07 00:36:51 UTC

## Result

The repeated-work experiment completed after a Codex-first run and a KV-only resume.

On the 100-case selected BFCL cohort:

- `kv_capsule_code_mode`: `100/100` pass
- `codex_ollama_regular_tools_compaction`: `87/100` pass
- Codex compaction events observed in the BFCL workload: `0`
- KV cumulative wall time: `853,499 ms` (`14.2 min`)
- Codex cumulative wall time: `11,521,048 ms` (`192.0 min`)
- KV visible input tokens: `3,900`
- Codex reported visible input tokens: `243,088,507`

The run writes canonical machine-readable outputs:

- `repeated-work-speed-summary.json`
- `repeated-work-speed-run-info.json`

## Interpretation

This is a strong operational result for the current KV capsule + Code Mode harness:

- The KV arm preserved quality across all 100 repeated tasks.
- The Codex/Ollama baseline missed 13 cases.
- The KV arm used dramatically less visible task input and completed much faster in this run.

The clean paper-safe claim is:

> On the selected 100-case BFCL repeated-work stream, the KV capsule + Code Mode harness completed all tasks correctly with far lower visible prompt burden and lower cumulative wall time than the tested Codex/Ollama regular-tool baseline.

## Compaction Baseline Correction

The Codex/Ollama arm must not be described as a successful real-compaction baseline.

Although the controller used the `gemma4-ollama-compact` Codex profile and the profile had previously emitted `context_compacted` in pressure testing, the actual BFCL repeated-work run logged `0` compaction events. The run created one Codex prompt/result pair per BFCL case and did not produce auditable evidence that the Codex context window filled and compacted during the benchmark.

Therefore the completed result is best labeled:

- `codex_ollama_regular_tools_attempted_compaction_no_events`

It is evidence against the tested Codex/Ollama repeated-task route as executed. It is not evidence against a true single-thread Codex auto-compaction baseline.

The required follow-up is a detached Codex-only baseline that:

- keeps the BFCL stream in one continuing Codex thread;
- uses a forced/budgeted auto-compaction threshold low enough to require compaction;
- records `context_compacted` or equivalent markers during the actual BFCL workload;
- is rejected as a compaction baseline if no compaction markers appear.

## Caveats

Do not claim this as a definitive win over real compaction yet.

The Codex profile had previously emitted `context_compacted` in pressure testing, but the actual BFCL repeated-work workload logged `0` compaction events. Therefore this run is evidence against the tested Codex/Ollama baseline as executed, not against all possible real-compaction baselines.

The Codex token telemetry appears cumulative across resumed turns. Treat its exact token count as route-reported cumulative burden, not clean per-task token accounting.

The run required a KV-only resume after the original controller passed `--case-limit None` to the KV arm. The finalizer reconstructs Codex records from raw artifacts and merges them with the KV resume records; this is reproducible through `paper_campaign_repeated_work_finalize.py`.

## Next Step

For paper-grade speed claims, run a follow-up where Codex compaction is forced or budgeted enough to produce auditable `context_compacted` events during the actual BFCL workload, then compare that result against this KV run.
