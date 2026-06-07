# Commands

This file records the verified DushyantPC command metadata for the imported edge-evidence control. Prompt-bearing request bodies remain in ignored raw artifacts.

## Verified Server Command

Source command artifact:

```text
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\gptoss-llcpp-2026-06-04\raw\repair-edge-evidence-six-command.json
```

SHA256:

```text
2F58AAD28DCD8F4F376F4F2FC3136AFD817D5F386334886C6CC07C177E274021
```

Server command:

```powershell
C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe `
  --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb `
  --host 127.0.0.1 `
  --port 50601 `
  --ctx-size 32768 `
  --parallel 1 `
  --slot-save-path benchmarks\correctness-eval-cache\gptoss-edge-evidence-six\slot `
  --cache-prompt `
  --slots `
  --no-ui `
  --no-warmup `
  --no-mmap `
  --flash-attn auto `
  --jinja `
  --reasoning off `
  --reasoning-budget 0
```

The actual raw prompts, responses, scores, and command records are preserved under:

```text
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\gptoss-llcpp-2026-06-04\raw\
```

## Hash Verification Commands

These were used from the Mac worktree to verify the imported raw artifact hashes:

```bash
ssh DushyantPC 'powershell -NoProfile -Command "Get-FileHash -Algorithm SHA256 ''C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\gptoss-llcpp-2026-06-04\raw\repair-edge-evidence-six-command.json'',''C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\gptoss-llcpp-2026-06-04\raw\repair-edge-evidence-six-prompts.jsonl'',''C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\gptoss-llcpp-2026-06-04\raw\repair-edge-evidence-six-responses.jsonl'',''C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\correctness-eval-results\gptoss-llcpp-2026-06-04\raw\repair-edge-evidence-six-scores.json'' | Select-Object Path,Hash | Format-List"'
```

## Imported Raw Artifacts

Pinned lower-level full baseline:

```text
pinned-harmony-full-command.json
pinned-harmony-full-prompts.jsonl
pinned-harmony-full-responses.jsonl
pinned-harmony-full-scores.json
```

Final-only repair on the two baseline misses:

```text
repair-final-exhaustive-v2-two-command.json
repair-final-exhaustive-v2-two-prompts.jsonl
repair-final-exhaustive-v2-two-responses.jsonl
repair-final-exhaustive-v2-two-scores.json
```

Verified incoming-edge evidence control:

```text
repair-edge-evidence-six-command.json
repair-edge-evidence-six-prompts.jsonl
repair-edge-evidence-six-responses.jsonl
repair-edge-evidence-six-scores.json
```
