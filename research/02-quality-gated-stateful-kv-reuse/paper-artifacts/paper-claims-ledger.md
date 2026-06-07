# Paper Claims Ledger

Date: 2026-06-07

Purpose: convert `paper-data-ledger.md` into allowed paper claims, explicit overclaim boundaries, and reviewer-risk notes.

## Main Claim

| Claim ID | Paper-facing claim | Evidence IDs | Safe wording | Unsafe wording / overclaim | Reviewer risk | Mitigation |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | A KV-capsule harness can let the same local model reuse stable tool/context knowledge through restored hidden state instead of repeatedly carrying or compacting that context as text. | E1, E5, E6, E11, E12 | "For repeated stable-context tool-use workloads, a KV-capsule harness restored hidden state from a stable prefix and allowed Gemma 4 to answer task tails without resending the full stable context." | "KV capsules universally replace context windows" or "KV beats compaction in all agent settings." | Reviewers may object that the repeated-work comparison is not prompt-identical. | State that the Codex/Ollama lane is a practical runtime baseline and use E1 for mechanism controls. |
| C2 | On the selected 100-case repeated-work stream, the KV-capsule + programmatic tool-interface harness outperformed the tested Codex/Ollama text-compaction harness using the same model. | E5, E6, E8 | "In our selected 100-case BFCL repeated-work stream, the KV-capsule system achieved 100/100 while the natural Codex/Ollama regular-tool text-compaction lane achieved 86/100, with 89 audited Codex compaction events." | "Our harness beats Codex generally" or "Gemma 4 beats Codex." | Codex is a harness, not a model; prompts differ. | Repeat "same model, different runtime/harness" and label it as a practical systems comparison. |

## Mechanism Claims

| Claim ID | Paper-facing claim | Evidence IDs | Safe wording | Unsafe wording / overclaim | Reviewer risk | Mitigation |
| --- | --- | --- | --- | --- | --- | --- |
| C3 | Restored KV can reproduce native live-append behavior under controls. | E1, E9, E10, E11, E12 | "Restored KV matched native live append on the selected 100-case cohort and on supporting earlier control ladders." | "Restored KV is always identical to live append." | Earlier Family 2 scale had partial deterministic hash parity. | Use E1 for 100/100 native/restored hash parity; mention E12 as semantic pass with hash warning. |
| C4 | Fresh-tail and wrong-capsule controls show the task tails alone were insufficient. | E1, E9, E10, E11, E12 | "Fresh-tail and wrong-capsule controls stayed closed in the paper-grade selected cohort, supporting dependence on the stable hidden prefix." | "The model cannot solve any task without hidden state." | Negative controls are constructed for prefix dependence. | Describe the cohort as quality-gated and prefix-dependent. |
| C5 | The selected-cohort mechanism result is semantic preservation, not a speed result. | E4 | "In the selected-cohort mechanism run, restored KV was slower than full visible and native live append, so speed is not claimed from that run." | "Restored KV is inherently faster." | Reviewers will notice restored KV mean latency is higher in E4. | Put this boundary in Results or Limitations before reviewers have to infer it. |

## Programmatic Tool-Interface Claims

| Claim ID | Paper-facing claim | Evidence IDs | Safe wording | Unsafe wording / overclaim | Reviewer risk | Mitigation |
| --- | --- | --- | --- | --- | --- | --- |
| C6 | The internal `code_mode` harness should be described externally as a programmatic tool interface. | E1, E9, E10, E13 | "The harness exposes a compact programmatic tool interface; internal artifacts retain `code_mode` in run labels." | "We evaluate full programmatic tool calling." | The implementation uses structured `EXEC`/compiled templates and deterministic scoring, not fully free-form PTC in every lane. | Define the interface precisely in Methods and call Anthropic-style PTC related/adjacent, not identical. |
| C7 | The programmatic tool-interface lane beat direct visible tool schemas on the selected 100-case cohort. | E1, E2 | "Programmatic full visible passed 100/100 versus direct visible tools at 91/100 on the selected cohort." | "Programmatic interfaces always beat direct tools." | Cohort is selected/quality-gated. | State selection criteria and include E9 as supporting but not universal evidence. |
| C8 | Compact visible evidence alone did not explain the restored hidden-state result. | E1, E3, E9, E10 | "Compact visible evidence was much weaker than restored hidden state on the selected cohort." | "Text summaries are useless" or "compaction never works." | Codex text compaction is a different mechanism from compact visible evidence. | Keep compact visible evidence and Codex text-compaction lanes separate. |

## Runtime Baseline Claims

| Claim ID | Paper-facing claim | Evidence IDs | Safe wording | Unsafe wording / overclaim | Reviewer risk | Mitigation |
| --- | --- | --- | --- | --- | --- | --- |
| C9 | The repeated-work KV system used far less visible prompt burden than the tested Codex/Ollama route. | E5, E6 | "KV visible input tokens were 3,900; Codex reported 245,774,883 visible input tokens. Treat Codex tokens as route-reported cumulative burden." | "Codex used exactly 245,774,883 independent per-task input tokens." | Codex telemetry appears cumulative/resumed and not clean per-task accounting. | Use "reported cumulative visible input telemetry" and avoid per-task token math unless separately audited. |
| C10 | The repeated-work KV system finished much faster cumulatively in the tested route. | E5, E6 | "KV cumulative wall was 853,499 ms versus Codex natural text compaction at 11,813,816 ms in the selected repeated-work stream." | "KV is always faster" or "KV restore itself is faster." | E4 contradicts an inherent restore-speed claim. | Frame as a repeated-work system/runtime result, not a low-level restore-latency theorem. |
| C11 | The natural Codex baseline did compact, but evidence lived in Codex session JSONL rather than per-task stdout. | E6 | "The natural chained Codex run produced 89 audited session compaction events; per-task stdout contained 0 markers." | "No compaction happened" or "stdout markers alone are sufficient." | Earlier summary initially missed compaction. | Include compaction evidence source in Methods/Reproducibility. |
| C12 | Codex failures appear mostly like tool-call accuracy misses, not parser collapse. | E8 | "The findings classify most failed cases as parseable but incorrect calls; one failed case parsed zero calls." | "Text compaction caused every failure." | Need deeper causality audit for compaction summaries. | List summary-contamination audit as future work/limitation. |

## Limitations To Say Explicitly

| Limitation ID | Limitation | Evidence IDs | Must appear in paper section |
| --- | --- | --- | --- |
| L1 | The Codex/Ollama baseline is a practical runtime comparison, not prompt-identical mechanism parity. | E5, E6, E13 | Experimental Design; Limitations |
| L2 | The selected-cohort mechanism run does not show restored KV is faster. | E4 | Results; Limitations |
| L3 | The programmatic tool interface is not full arbitrary programmatic tool calling. | E1, E9, E10 | Method; Limitations |
| L4 | The 100-case cohort is selected/quality-gated, not an official BFCL leaderboard submission. | E1, E9 | Experimental Design; Limitations |
| L5 | Codex token telemetry should be treated as route-reported cumulative burden, not clean per-task accounting. | E6 | Results; Reproducibility |
| L6 | The Codex compaction summaries still need an audit for contamination/help/harm across later tasks. | E6, E8 | Limitations; Future Work |

## Claim Review

- C1 and C2 are the paper spine.
- C3 through C5 defend the hidden-state mechanism.
- C6 through C8 defend why the interface matters without overselling it as full PTC.
- C9 through C12 support the practical harness comparison.
- No claim in this ledger depends on chat-only memory; every row points back to `paper-data-ledger.md`.
