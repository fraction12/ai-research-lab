# HF KV Capsule Paper Benchmark 2026-06-05

## Outcome

This run did not produce interpretable HF restored-capsule evidence. The synthetic Gemma 4 12B sequence-file preflight passed, but both HF families hit stop rules before restored capsule interpretation.

IFEval was made full-visible reliable by expanding calibration: 74 of 250 candidates passed full-visible, and the first 50 passing cases were frozen as a selected cohort. The selected cohort reran full-visible at 50/50, but `fresh_tail_only` unexpectedly passed 3 of the first 4 negative-control records. The IFEval matrix was stopped and quarantined as task split/scorer leakage: the current IFEval split leaves enough task information in the tail for the model to pass without restored prefix state.

GraphWalks `parents` full-visible calibration passed 0/100, so GraphWalks capsule and secondary evidence controls were not run.

## Interpretation

The result is not a failure of the sequence-file KV/state route. Earlier synthetic and Family 1/2 evidence remains valid for narrow prefix-dependent tasks, and the synthetic preflight here also passed. This HF paper benchmark shows that paper-facing task construction still needs work: IFEval is not prefix-dependent under the current split, while GraphWalks is not full-visible reliable for Gemma 4 12B under this protocol.

## Key Counts

- Synthetic preflight: full visible 6/6, fresh tail 0/6, live append 6/6, restored capsule append 6/6.
- IFEval live gate: full visible 1/10, native live append 1/10.
- IFEval calibration: 74/250 full-visible passes; selected 50-case cohort created.
- IFEval selected matrix: full visible 50/50; fresh tail 3/4 unexpected passes; stopped before live/restored capsule controls.
- GraphWalks live gate: full visible 0/10, native live append 0/10.
- GraphWalks calibration: full visible 0/100.

## Validity Boundary

No claim is made that restored capsules preserve HF IFEval or GraphWalks quality. No GraphWalks, secondary evidence, or amortization capsule claims are made.
