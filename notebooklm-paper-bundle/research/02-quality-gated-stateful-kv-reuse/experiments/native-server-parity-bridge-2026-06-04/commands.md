# Native Server Parity Bridge Commands

## OpenSpec

```bash
openspec validate bridge-native-server-parity-for-kv-capsule --type change --strict
openspec validate --all --strict
```

## Sync checkpoint to DushyantPC

```bash
git bundle create /tmp/track02-native-server-parity.bundle fa8d3f0..HEAD
scp /tmp/track02-native-server-parity.bundle DushyantPC:C:/Users/Dushyant/Projects/track02-native-server-parity.bundle
ssh DushyantPC "powershell -NoProfile -Command "cd C:\\Users\\Dushyant\\Projects\\ai-research-lab; git fetch C:\\Users\\Dushyant\\Projects\\track02-native-server-parity.bundle HEAD:refs/remotes/bundle/native-server-parity; git merge --ff-only refs/remotes/bundle/native-server-parity""
```

## Bridge runner

The ignored raw runner was copied to DushyantPC and executed only in `--mode bridge`:

```powershell
python research\01-ssd-native-inference-current\benchmarks\native-server-parity-bridge-2026-06-04\raw\native_server_parity_bridge.py `
  --mode bridge `
  --cases 3 `
  --predict 48 `
  --temperature 0.0 `
  --ctx-size 32768 `
  --n-gpu-layers -1 `
  --backend cuda_v13
```

Server command used by runner:

```text
C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe --host 127.0.0.1 --port 54867 --ctx-size 32768 --parallel 1 --cache-prompt --slots --no-ui --no-warmup --no-mmap --flash-attn auto --jinja --reasoning off --reasoning-budget 0 --model C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb
```

## Copyback

```bash
scp 'DushyantPC:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/native-server-parity-bridge-2026-06-04/raw/*' research/01-ssd-native-inference-current/benchmarks/native-server-parity-bridge-2026-06-04/raw/
```
