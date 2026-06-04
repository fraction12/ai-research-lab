# Commands

## Local Tests

Run from:

```text
/Users/dushyantgarg/Documents/Projects/ai-research-lab/research/01-ssd-native-inference-current
```

```bash
python3 -m unittest tests.test_llama_cpp_prefix_reuse_audit
python3 benchmarks/llama_cpp_prefix_reuse_audit.py --dry-run --prefix-repeat 4 --output /tmp/llama-cpp-prefix-reuse-audit-dry.json
```

## DushyantPC Focused Test

```bash
ssh dushyantpc "cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current && python -m unittest tests.test_llama_cpp_prefix_reuse_audit"
```

## DushyantPC Model Audit

```bash
ssh dushyantpc "cd C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current && python benchmarks\llama_cpp_prefix_reuse_audit.py --server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --ctx-size 32768 --predict 32 --prime-n-predict 0 --prefix-repeat 256 --temperature 0.0 --timeout 300 --cache-dir benchmarks\lcpr-cache\lcpr-2026-06-04 --output benchmarks\lcpr-results\lcpr-2026-06-04\gpt-oss-20b-mxfp4-llama-cpp-prefix-reuse-audit.json"
```

## Copy Raw Artifacts Back To Mac

```bash
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/lcpr-results/lcpr-2026-06-04 research/01-ssd-native-inference-current/benchmarks/lcpr-results/
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/lcpr-cache/lcpr-2026-06-04 research/01-ssd-native-inference-current/benchmarks/lcpr-cache/
```

## Validation

```bash
python3 -m unittest discover -s tests
npx --yes @fission-ai/openspec@latest validate --all --strict
```
