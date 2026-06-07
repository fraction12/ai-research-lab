# Source Audit Notes

Status: Stage 1 source audit complete. No model runs have started.

## Decision

Use BFCL first.

BFCL is the closest public source to the current seven-control harness because it stresses function/tool selection, arguments, multiple calls, parallel calls, no-call/irrelevance, executable/API-style categories, and multi-turn categories. It lets us leave handmade fixtures without immediately adding tau-bench/tau2 simulated users or ToolSandbox stateful host execution.

## Pinned Sources

- BFCL leaderboard/code: `https://gorilla.cs.berkeley.edu/leaderboard`, official checkpoint reported as `f7cf735`, package `bfcl-eval==2025.12.17`.
- BFCL data: `https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard`, observed main head `61fc0608cfd831fcfbbaa676ebdfef0ed963eeda`.
- tau2 follow-on: `https://github.com/sierra-research/tau2-bench`, observed main head `1746a25db265724f6fed2260934bb67f1514fad7`.
- ToolSandbox follow-on: `https://github.com/apple/ToolSandbox`, observed main head `165848b9a78cead7ca7fe7c89c688b58e6501219`.

## Stage 1 Scope

Start with BFCL non-live JSONL categories. Defer live/agentic categories until the adapter proves source provenance, category scoring, deterministic sampling, and prefix-dependence labeling.

The BFCL dataset card says to read the JSONL files directly and not use Hugging Face `load_dataset`.

## Track 2 Review Gate

Track 2 approved Stage 1 source audit and BFCL adapter prep. It gave a conditional no-go for model smoke until the dry run proves:

- source provenance
- faithful scorer reconstruction
- deterministic category sampling
- prefix-dependence labeling
- exact seven-control record generation

## Added Required Fields

Before any model smoke, records need:

- `primary_eligible`, `primary_eligibility_reason`, `prefix_dependency_class`
- source release/revision/category/row hash/license fields
- native scorer name/version/mode and unsupported scorer features
- expected and parsed call/argument hashes
- transform version/hash and fields used/excluded
- `template`, `template_alias`, `alias_registry_version`, `host_filled_args`, `final_source`, `parse_status`
- wrong-capsule source and mismatch rationale
- `delta_prompt_contains_stable_prefix`, seq token counts, `n_past`, generation start, capsule bytes/hash

## Stop Rule

If BFCL scorer support is partial for a category, that category is diagnostic-only until native or faithful category scoring is proven.
