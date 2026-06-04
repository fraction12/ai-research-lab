# Hidden-Prefix Semantic Continuation Probe

Date: 2026-06-04

This focused gate asks whether the pinned GPT-OSS llama.cpp slot restore path makes a hidden prefix semantically usable for a later `/completion` tail request. It runs before any noiseless GraphWalks evidence rerun.

## Scope

Analyzed scope is the codeword family only: 10 deterministic codeword variants x 3 controls = 30 records. The planned key/value ladder was intentionally stopped after the codeword gate because the codeword result was decisive. One extra `kv-01` full-visible record was written before manual stop and is excluded from all metrics here.

## Result

| Control | Strict exact match | Answer contained/extractable | Output status |
| --- | ---: | ---: | --- |
| `full_visible_prefix_plus_tail` | 0/10 | 10/10 | {'exact_only': 0, 'contains_with_extra_text': 10, 'missing': 0, 'malformed': 0} |
| `fresh_tail_only` | 0/10 | 0/10 | {'exact_only': 0, 'contains_with_extra_text': 0, 'missing': 10, 'malformed': 0} |
| `restored_hidden_prefix_plus_tail` | 0/10 | 0/10 | {'exact_only': 0, 'contains_with_extra_text': 0, 'missing': 10, 'malformed': 0} |

Restored hidden-prefix responses exactly matched fresh tail-only responses in 10/10 cases by raw response hash. Restored controls reported slot save/restore telemetry in 10/10 cases, with `n_saved`/`n_restored` values [16, 17, 19] and slot bytes [787500, 836680, 935040].

## Interpretation

Full visible answers were verbose, but contained the correct codeword in 10/10 cases. That is an output-protocol issue, not a visible-prefix semantic failure. Fresh tail-only contained the codeword in 0/10, and restored hidden-prefix also contained it in 0/10 while matching fresh tail-only exactly.

Decision: the current pinned llama.cpp + GPT-OSS restored hidden-prefix protocol behaves like fresh tail-only on this codeword gate. Mechanical slot save/restore happened, but the restored prefix was not semantically available to the tail completion. Do not interpret prior GraphWalks hidden-prefix failures as evidence against hidden KV reuse in general; interpret them as failures of this protocol/backend usage.

## Artifacts

Prompt-bearing raw artifacts are preserved under ignored Track 01 paths listed in `artifact-manifest.json`. Committed files in this directory contain hashes, metrics, and classifications only.
