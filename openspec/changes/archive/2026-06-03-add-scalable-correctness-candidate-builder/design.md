## Context

The correctness runner can already sample single datasets, run full/session-tail responses, and select full-passing cases with the baseline ladder. The first GPT-OSS 20B ladder selected only three IFEval cases from twelve candidates. GraphWalks was formatted correctly but semantically wrong, and MRCR produced a placeholder answer under the current prompt protocol. Hand-written sampling scripts are not enough for repeated benchmark runs.

## Goals / Non-Goals

**Goals:**
- Make candidate-set generation repeatable from the CLI.
- Favor cases that the full-prompt baseline is more likely to answer correctly.
- Add answer hints that describe the scorer-facing answer shape without leaking reference answers.
- Produce metadata that explains the target dataset mix and local candidate source.

**Non-Goals:**
- Do not tune generation settings automatically.
- Do not loosen scoring rules to manufacture passes.
- Do not commit sampled prompt/case JSONL files that contain dataset prompt text.
- Do not make claims about session-tail parity until the selected full-passing set is large enough.

## Decisions

1. Add a `build-candidates` command instead of relying on ad hoc Python snippets.

   This keeps the experiment reproducible and lets future runs vary dataset mix, prompt-length caps, and IFEval easy-filter behavior from the command line.

2. Use explicit dataset specs in the candidate builder.

   A compact syntax like `ifeval:80,graphwalks:20,mrcr:10` lets the benchmark runner express the target mix without creating separate files and shell loops.

3. Keep the IFEval easy filter as an opt-in sampling profile.

   The first ladder showed many hard format constraints fail under GPT-OSS 20B. The easy profile limits IFEval rows to supported single-instruction checks with small bounded parameters. The default profile remains unfiltered so this does not hide dataset difficulty unless the run opts into it.

4. Add answer hints inside the JSON answer protocol.

   The model already receives a JSON schema for `{"answer": "..."}`. Dataset-specific hints tell the model what to put inside the `answer` string, such as a JSON-style node list for GraphWalks or the exact requested text for MRCR. These hints do not include reference labels.

## Risks / Trade-offs

- [Risk] Easy candidate profiles may overstate quality. -> Mitigation: record the sampling profile and selected case count in reports and dataset summaries.
- [Risk] Larger PC ladders are slow. -> Mitigation: build candidates locally, run full selection first, and only run session-tail on selected cases.
- [Risk] Dataset-specific hints may improve full baselines without proving raw agent prompts. -> Mitigation: treat this as a controlled correctness protocol and keep raw protocol runs separate.
