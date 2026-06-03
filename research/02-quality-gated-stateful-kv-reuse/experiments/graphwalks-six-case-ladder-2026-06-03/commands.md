# Commands

This file records commands run during setup and command shapes proposed for the eventual live ladder. Commands in the setup section did not start llama.cpp or generate model answers except where explicitly noted as future commands.

## Setup Commands Run

Materialize twenty bounded GraphWalks candidate cases:

```bash
cd research/01-ssd-native-inference-current

python3 benchmarks/flashcache_correctness_eval.py sample \
  --dataset graphwalks \
  --limit 20 \
  --max-prompt-chars 5000 \
  --output benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/graphwalks-20-candidates.jsonl
```

Observed warnings:

```text
urllib3 NotOpenSSLWarning for LibreSSL 2.8.3
HF Hub unauthenticated request warning
multiprocessing resource_tracker leaked semaphore warning at shutdown
```

Filter the exact six selected cases:

```bash
cd research/01-ssd-native-inference-current

python3 - <<'PY'
import json
from pathlib import Path

root = Path("benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03")
source = root / "graphwalks-20-candidates.jsonl"
selected_ids = {"graphwalks-6", "graphwalks-9", "graphwalks-11", "graphwalks-13", "graphwalks-16", "graphwalks-19"}
rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
picked = [row for row in rows if row.get("case_id") in selected_ids]
found = {row.get("case_id") for row in picked}
missing = sorted(selected_ids - found)
extra = sorted(found - selected_ids)
if missing or extra or len(picked) != len(selected_ids):
    raise SystemExit(f"bad selected set: found={sorted(found)} missing={missing} extra={extra} count={len(picked)}")
(root / "graphwalks-six-selected-cases.jsonl").write_text(
    "".join(json.dumps(row, sort_keys=True) + "\n" for row in picked),
    encoding="utf-8",
)
PY
```

Verify command plumbing without a live model:

```bash
cd research/01-ssd-native-inference-current

python3 benchmarks/flashcache_correctness_eval.py run \
  --cases benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/graphwalks-six-selected-cases.jsonl \
  --mode both \
  --answer-protocol json-answer \
  --model benchmarks/models/gpt-oss-20b-mxfp4.gguf \
  --ctx-size 32768 \
  --predict 192 \
  --temperature 0.0 \
  --dry-run \
  --output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/dry-run-both-responses.jsonl \
  --score \
  --score-output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/dry-run-both-scores.json
```

## Proposed Live Commands

Full-prompt replay variance:

```bash
cd research/01-ssd-native-inference-current

for run in 01 02 03; do
  python3 benchmarks/flashcache_correctness_eval.py run \
    --cases benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/graphwalks-six-selected-cases.jsonl \
    --mode full \
    --answer-protocol json-answer \
    --model benchmarks/models/gpt-oss-20b-mxfp4.gguf \
    --ctx-size 32768 \
    --predict 192 \
    --temperature 0.0 \
    --output-dir benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw \
    --output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/full-replay-${run}-responses.jsonl \
    --score \
    --score-output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/full-replay-${run}-scores.json
done
```

Session-tail replay and basic reset/restore sanity:

```bash
cd research/01-ssd-native-inference-current

for run in 01 02 03; do
  python3 benchmarks/flashcache_correctness_eval.py run \
    --cases benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/graphwalks-six-selected-cases.jsonl \
    --mode session-tail \
    --answer-protocol json-answer \
    --model benchmarks/models/gpt-oss-20b-mxfp4.gguf \
    --ctx-size 32768 \
    --predict 192 \
    --temperature 0.0 \
    --cache-dir benchmarks/correctness-eval-cache/graphwalks-six-case-ladder-2026-06-03/session-tail-${run} \
    --output-dir benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw \
    --output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/session-tail-${run}-responses.jsonl \
    --score \
    --score-output benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/session-tail-${run}-scores.json
done
```

Visible-prefix/session-formatted and stronger-tail-hint commands should use derived local case JSONL files. See `control-feasibility.md` before creating those derived files.

## Live Commands Run

All live commands were run on DushyantPC from:

```text
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current
```

Backend and model:

```text
--server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe
--model benchmarks\models\gpt-oss-20b-mxfp4.gguf
--ctx-size 32768
--predict 192
--temperature 0.0
--timeout 240
```

Controls executed:

```text
full-replay-01, full-replay-02, full-replay-03
session-tail-01, session-tail-02, session-tail-03
visible-prefix-session-formatted
stronger-tail-hints-session-tail
```

Raw outputs were written under:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/
```

Prompt-bearing derived inputs were written under:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/
```
