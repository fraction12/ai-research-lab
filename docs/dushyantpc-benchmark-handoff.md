# DushyantPC Benchmark Handoff

This is the handoff for continuing the Printy/printtestbot Flashcache benchmark on DushyantPC from another Mac.

## Scope

Use DushyantPC for model runs. Do not run the large local models on the Mac.

The current dataset is:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/
```

The fixture is:

```text
benchmarks/fixtures/printtestbot_printing_press_workflow.json
```

Read the result summary first:

```text
docs/benchmark-results.md
```

## SSH

The Mac Mini reaches the PC with this alias:

```bash
ssh dushyantpc
```

Equivalent direct target:

```bash
ssh Dushyant@100.113.203.102
```

That address is the Tailscale/private network address for DushyantPC. The other Mac must be on the same Tailscale tailnet and must have an SSH key authorized on the PC.

If the alias is missing on the other Mac, add this to `~/.ssh/config` there, using that Mac's private key path:

```sshconfig
Host dushyantpc
  HostName 100.113.203.102
  User Dushyant
  IdentityFile ~/.ssh/<key-authorized-on-dushyantpc>
  IdentitiesOnly yes
```

Do not commit private keys, tokens, raw private transcripts, Telegram chat IDs, or secrets.

## Remote Paths

Repo on DushyantPC:

```text
C:\Users\Dushyant\Projects\ssd-native-inference
```

Portable llama.cpp used for `gpt-oss-20b` GGUF:

```text
C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe
```

WinGet llama.cpp is also installed, but it could not load `gptoss` architecture during this run:

```text
C:\Users\Dushyant\AppData\Local\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe
```

GGUF models already present on DushyantPC:

```text
C:\Users\Dushyant\Projects\ssd-native-inference\benchmarks\models\gemma-3-270m-it-Q8_0.gguf
C:\Users\Dushyant\Projects\ssd-native-inference\benchmarks\models\gpt-oss-20b-mxfp4.gguf
```

Ollama model already present:

```text
gpt-oss:20b
```

## Start a Remote Shell

From a Mac:

```bash
ssh dushyantpc
```

Then in PowerShell on DushyantPC:

```powershell
cd C:\Users\Dushyant\Projects\ssd-native-inference
git pull
python --version
ollama list
```

If continuing from a non-interactive Mac shell, wrap commands like this:

```bash
ssh dushyantpc "powershell -NoProfile -Command \"cd C:\Users\Dushyant\Projects\ssd-native-inference; git pull; python --version\""
```

## How This Dataset Was Built

The fixture was hand-curated from Printy/printtestbot prompt assembly and a Printing Press CLI fix/retry loop.

It intentionally splits the workflow into:

```text
stable_prefix -> semi_stable_context -> volatile_tail per turn
```

The reusable cache boundary is after `stable_prefix + semi_stable_context`, before the changing command output/failure/patch tail.

The benchmark goal is not exact replay. The goal is to test whether changed-tail agent workflows preserve useful prefix/KV work across warm sessions, restarts, and Flashcache slot save/restore.

## Re-run Ollama Baselines

Run full changed-tail prompt baseline:

```powershell
python benchmarks\ollama_workflow_benchmark.py --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --model gpt-oss:20b --host http://localhost:11434 --strategy full --runs 1 --num-predict 8 --temperature 0 --timeout 900 --output-dir benchmarks\datasets\printtestbot-printing-press-2026-06-02\raw
```

Run exact replay control:

```powershell
python benchmarks\ollama_workflow_benchmark.py --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --model gpt-oss:20b --host http://localhost:11434 --scenario turn-03-verify-failure --strategy full --runs 2 --num-predict 8 --temperature 0 --timeout 900 --output-dir benchmarks\datasets\printtestbot-printing-press-2026-06-02\raw
```

Run warm-vs-restarted comparison:

```powershell
python benchmarks\ollama_workflow_benchmark.py --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --model gpt-oss:20b --host http://localhost:11434 --strategy restart-compare --runs 1 --num-predict 8 --temperature 0 --timeout 900 --write-prefix-manifest --output-dir benchmarks\datasets\printtestbot-printing-press-2026-06-02\raw
```

## Re-run llama.cpp / Flashcache

Gemma 270M cache-mechanics slot test:

```powershell
python benchmarks\llama_cpp_prompt_cache_benchmark.py --model benchmarks\models\gemma-3-270m-it-Q8_0.gguf --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --predict 8 --temperature 0 --timeout 240 --output-dir benchmarks\datasets\printtestbot-printing-press-2026-06-02\raw
```

Gemma 270M Flashcache wrapper test:

```powershell
python benchmarks\flashcache_wrapper_benchmark.py --model benchmarks\models\gemma-3-270m-it-Q8_0.gguf --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --predict 8 --temperature 0 --timeout 240 --output-dir benchmarks\datasets\printtestbot-printing-press-2026-06-02\raw
```

`gpt-oss-20b` GGUF slot test. Use portable llama.cpp `b9482`, not the winget build:

```powershell
python benchmarks\llama_cpp_prompt_cache_benchmark.py --server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --predict 8 --temperature 0 --timeout 900 --ctx-size 4096 --output-dir benchmarks\datasets\printtestbot-printing-press-2026-06-02\raw
```

`gpt-oss-20b` GGUF Flashcache wrapper test:

```powershell
python benchmarks\flashcache_wrapper_benchmark.py --server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --predict 8 --temperature 0 --timeout 900 --ctx-size 4096 --output-dir benchmarks\datasets\printtestbot-printing-press-2026-06-02\raw
```

## Validation

From repo root on either machine:

```bash
python3 -m py_compile benchmarks/ollama_workflow_benchmark.py benchmarks/llama_cpp_prompt_cache_benchmark.py benchmarks/flashcache_wrapper_benchmark.py
python3 benchmarks/ollama_workflow_benchmark.py --fixture benchmarks/fixtures/printtestbot_printing_press_workflow.json --dry-run
git diff --check
```

On Windows, use `python` instead of `python3`.

## Current Interpretation

The dataset currently says:

- Ollama warm changed-tail runs are materially faster than restarted runs for `gpt-oss:20b`.
- Exact replay gets cheap, but it is not the target workload.
- Gemma 270M proves llama.cpp slot save/restore mechanics.
- `gpt-oss-20b` direct slot restore did not beat direct full prompts on the full seven-turn fixture.
- `gpt-oss-20b` Flashcache wrapper did reduce prompt processing by about 12.8%.

Next useful tests:

- Larger stable prefix, closer to real Printy repo/tool/memory context.
- More generated tokens plus a quality rubric, not only prompt-eval timing.
- Multiple runs per scenario to reduce single-run noise.
- Compare prompt layouts: canonical stable prefix first versus mixed dynamic prompt blocks.
