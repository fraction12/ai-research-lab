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
- uses the normal verified `gemma4-ollama-compact` profile first, so any compaction is natural rather than threshold-forced;
- records `context_compacted` or equivalent markers during the actual BFCL workload;
- is rejected as a compaction baseline if no compaction markers appear.

A lower-threshold Codex profile may be run later as a separate stress test, but it must be labeled as forced compaction and must not be blended into the natural-baseline result.

## Caveats

Do not claim this as a definitive win over real compaction yet.

The Codex profile had previously emitted `context_compacted` in pressure testing, but the actual BFCL repeated-work workload logged `0` compaction events. Therefore this run is evidence against the tested Codex/Ollama baseline as executed, not against all possible real-compaction baselines.

The Codex token telemetry appears cumulative across resumed turns. Treat its exact token count as route-reported cumulative burden, not clean per-task token accounting.

The run required a KV-only resume after the original controller passed `--case-limit None` to the KV arm. The finalizer reconstructs Codex records from raw artifacts and merges them with the KV resume records; this is reproducible through `paper_campaign_repeated_work_finalize.py`.

## Next Step

For paper-grade speed claims, first run a natural chained Codex session with the normal verified compaction profile. If it produces auditable `context_compacted` events during the actual BFCL workload, compare that result against this KV run. If natural compaction still does not trigger, report that directly and keep any forced-threshold run as a separate stress-test result.

## Natural Chained Codex Follow-Up

Generated: 2026-06-07 05:11:07 UTC

The natural chained Codex-only follow-up completed:

- Run label: `bfcl-repeated-work-codex-natural-chained-v1`
- Runtime: `codex-cli+ollama`
- Profile: `gemma4-ollama-compact`
- Model profile: `gemma4:12b`
- Records: `100 / 100`
- Codex pass: `86 / 100`
- Codex cumulative wall time: `11,813,816 ms` (`196.9 min`)
- Codex reported visible input tokens: `245,774,883`
- Codex reported output tokens: `9,068,626`
- Run stdout compaction markers: `0`
- Codex session log `type:compacted` records: `89`
- Exact `context_compacted` hits in `.codex/sessions`: `89`
- Summary-text hits: `180`

This corrects the earlier run-artifact-only read. The BFCL stdout artifacts did not contain compaction markers, but the Codex session JSONL did. Therefore this follow-up is a valid natural Codex text-summary compaction baseline for the tested route.

The paper-safe label is:

- `codex_ollama_regular_tools_natural_text_compaction`

The result is not a pure prompt-identical mechanism comparison against KV capsules. It is a practical Codex/Ollama runtime baseline: regular visible tool prompts plus Codex's natural text-summary compaction behavior.

Failure breakdown:

- `java`: `14 / 17`
- `javascript`: `0 / 1`
- `multiple`: `21 / 25`
- `parallel`: `13 / 14`
- `parallel_multiple`: `13 / 17`
- `simple`: `25 / 26`

The `14` failed cases mostly produced parseable tool calls but missed exact BFCL scoring through wrong arguments, duplicate calls, extra calls, or missing parallel calls. One failed case parsed zero calls. This looks primarily like model/tool-call accuracy under the Codex text-compacted route, not parser collapse.

Updated interpretation:

> On the selected 100-case BFCL repeated-work stream, the existing KV capsule + Code Mode result remains the quality leader at `100 / 100`, while the natural Codex/Ollama regular-tool text-compaction follow-up completed at `86 / 100` with `89` auditable compaction events in the Codex session log.

The next audit should inspect whether the Codex compaction summaries helped, hurt, or contaminated later BFCL tasks, because the summaries include prior task outputs and arguments.
