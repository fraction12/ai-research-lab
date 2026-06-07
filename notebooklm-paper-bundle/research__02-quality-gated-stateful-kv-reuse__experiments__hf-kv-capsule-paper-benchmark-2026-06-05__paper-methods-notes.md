# Paper Methods Notes

This experiment used HF-backed candidate rows from `google/IFEval` train and `openai/graphwalks` train with the GraphWalks `parents` subset. Candidate artifacts recorded row offsets, source row hashes, prompt hashes, transform version, prompt protocol version, scorer version, dataset revisions, and licenses in ignored raw/input paths.

The primary stop-rule lesson is methodological. A full-visible-passing selected cohort is necessary but not sufficient for KV capsule evidence. The fresh-tail negative control must also miss. The selected IFEval cohort failed that requirement because the current split places the user task in the tail and leaves only protocol/hint material in the prefix.

GraphWalks failed before capsule interpretation because full-visible calibration found no passing rows. This should be treated as a model/protocol/scorer baseline failure for this runtime, not as restored-state evidence.

Future paper-quality work should either construct HF-backed prefix-dependent transformations with explicit fresh-tail miss requirements, or use task families where the reusable prefix contains necessary evidence and the volatile tail only asks a query over that evidence.
