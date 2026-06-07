# Commands

Date: 2026-06-03

All live model commands were run on DushyantPC from:

```bat
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current
```

## Focused Tests

macOS checkout:

```bash
cd research/01-ssd-native-inference-current
python3 -m unittest tests.test_flashcache_correctness_eval
```

DushyantPC checkout:

```bat
cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current
python -m unittest tests.test_flashcache_correctness_eval
```

## Live-Tail Dry Run

```bat
python benchmarks\flashcache_correctness_eval.py run --cases benchmarks\correctness-eval-inputs\graphwalks-repair-mechanism-ladder-2026-06-03\graphwalks-six-selected-cases.jsonl --mode live-tail --answer-protocol json-answer --dry-run --score --output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\dry-run-live-tail-responses.jsonl --score-output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\dry-run-live-tail-scores.json
```

## Live No-Restore Control

```bat
python benchmarks\flashcache_correctness_eval.py run --cases benchmarks\correctness-eval-inputs\graphwalks-repair-mechanism-ladder-2026-06-03\graphwalks-six-selected-cases.jsonl --mode live-tail --answer-protocol json-answer --server-bin %USERPROFILE%\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --ctx-size 32768 --predict 192 --temperature 0.0 --timeout 240 --cache-dir benchmarks\correctness-eval-cache\graphwalks-repair-mechanism-ladder-2026-06-03\live-tail --output-dir benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw --output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\live-tail-responses.jsonl --score --score-output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\live-tail-scores.json
```

## Restored Session-Tail Baseline

```bat
python benchmarks\flashcache_correctness_eval.py run --cases benchmarks\correctness-eval-inputs\graphwalks-repair-mechanism-ladder-2026-06-03\graphwalks-six-query-visible-graph-hidden-cases.jsonl --mode session-tail --answer-protocol json-answer --server-bin %USERPROFILE%\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --ctx-size 32768 --predict 192 --temperature 0.0 --timeout 240 --cache-dir benchmarks\correctness-eval-cache\graphwalks-repair-mechanism-ladder-2026-06-03\query-visible-graph-hidden --output-dir benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw --output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\query-visible-graph-hidden-session-tail-responses.jsonl --score --score-output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\query-visible-graph-hidden-session-tail-scores.json
```

## Anchor Recompute Controls

```bat
for %S in (64 128 256) do python benchmarks\flashcache_correctness_eval.py run --cases benchmarks\correctness-eval-inputs\graphwalks-repair-mechanism-ladder-2026-06-03\graphwalks-six-anchor-recompute-%S-cases.jsonl --mode session-tail --answer-protocol json-answer --server-bin %USERPROFILE%\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --ctx-size 32768 --predict 192 --temperature 0.0 --timeout 240 --cache-dir benchmarks\correctness-eval-cache\graphwalks-repair-mechanism-ladder-2026-06-03\anchor-recompute-%S --output-dir benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw --output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\anchor-recompute-%S-session-tail-responses.jsonl --score --score-output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\anchor-recompute-%S-session-tail-scores.json
```

## Visibility Controls

```bat
python benchmarks\flashcache_correctness_eval.py run --cases benchmarks\correctness-eval-inputs\graphwalks-repair-mechanism-ladder-2026-06-03\graphwalks-six-graph-and-query-visible-tail-cases.jsonl --mode session-tail --answer-protocol json-answer --server-bin %USERPROFILE%\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --ctx-size 32768 --predict 192 --temperature 0.0 --timeout 240 --cache-dir benchmarks\correctness-eval-cache\graphwalks-repair-mechanism-ladder-2026-06-03\graph-and-query-visible-tail --output-dir benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw --output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\graph-and-query-visible-tail-session-tail-responses.jsonl --score --score-output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\graph-and-query-visible-tail-session-tail-scores.json
```

The first attempt at `graph_and_query_visible_session_format` used a longer cache path and produced Windows path-length/log-file errors. It was rerun with the shorter cache path below, and the final response/score files were overwritten with the valid run.

```bat
python benchmarks\flashcache_correctness_eval.py run --cases benchmarks\correctness-eval-inputs\graphwalks-repair-mechanism-ladder-2026-06-03\graphwalks-six-graph-and-query-visible-session-format-cases.jsonl --mode session-tail --answer-protocol json-answer --server-bin %USERPROFILE%\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --ctx-size 32768 --predict 192 --temperature 0.0 --timeout 240 --cache-dir benchmarks\correctness-eval-cache\gw-repair-gqvsf --output-dir benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw --output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\graph-and-query-visible-session-format-session-tail-responses.jsonl --score --score-output benchmarks\correctness-eval-results\graphwalks-repair-mechanism-ladder-2026-06-03\raw\graph-and-query-visible-session-format-session-tail-scores.json
```
