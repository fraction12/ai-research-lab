# Commands

## Local Implementation Tests

Run from:

```text
/Users/dushyantgarg/Documents/Projects/ai-research-lab/research/01-ssd-native-inference-current
```

```bash
python3 -m unittest tests.test_restored_prefix_full_resend_probe
python3 benchmarks/flashcache_restored_prefix_full_resend_probe.py --dry-run --output /tmp/restored-prefix-probe-dry.json
```

## DushyantPC Focused Tests

Run from Mac:

```bash
ssh dushyantpc "cd C:\\Users\\Dushyant\\Projects\\ai-research-lab\\research\\01-ssd-native-inference-current && python -m unittest tests.test_restored_prefix_full_resend_probe"
```

## First Attempt, Long Path Failure

This attempt preserved the runtime/path failure. It did not produce a mechanism result.

```bash
ssh dushyantpc "cd C:\\Users\\Dushyant\\Projects\\ai-research-lab\\research\\01-ssd-native-inference-current && python benchmarks\\flashcache_restored_prefix_full_resend_probe.py --server-bin C:\\Users\\Dushyant\\Tools\\llama-b9482-vulkan\\llama-server.exe --model benchmarks\\models\\gpt-oss-20b-mxfp4.gguf --ctx-size 32768 --predict 32 --prime-n-predict 0 --temperature 0.0 --timeout 240 --cache-dir benchmarks\\restored-prefix-full-resend-cache\\restored-prefix-full-resend-2026-06-03 --output benchmarks\\restored-prefix-full-resend-results\\restored-prefix-full-resend-2026-06-03\\gpt-oss-20b-mxfp4-restored-prefix-full-resend.json"
```

Observed error class:

```text
FileNotFoundError opening long Windows log paths under restored-prefix-full-resend-cache
```

## Valid Short-Path Probe

Run from Mac:

```bash
ssh dushyantpc "cd C:\\Users\\Dushyant\\Projects\\ai-research-lab\\research\\01-ssd-native-inference-current && python benchmarks\\flashcache_restored_prefix_full_resend_probe.py --server-bin C:\\Users\\Dushyant\\Tools\\llama-b9482-vulkan\\llama-server.exe --model benchmarks\\models\\gpt-oss-20b-mxfp4.gguf --ctx-size 32768 --predict 32 --prime-n-predict 0 --temperature 0.0 --timeout 240 --cache-dir benchmarks\\rpfr-cache\\rpfr-2026-06-03 --output benchmarks\\rpfr-results\\rpfr-2026-06-03\\gpt-oss-20b-mxfp4-restored-prefix-full-resend.json"
```

## Resummarize After Gate Tightening

The model was not rerun for this step. The command recomputed `summary` from existing raw records after tightening the useful-acceleration gate.

```bash
ssh dushyantpc "cd C:\\Users\\Dushyant\\Projects\\ai-research-lab\\research\\01-ssd-native-inference-current && python -c \"import json, sys; sys.path.insert(0, 'benchmarks'); import flashcache_restored_prefix_full_resend_probe as p; path=r'benchmarks\\rpfr-results\\rpfr-2026-06-03\\gpt-oss-20b-mxfp4-restored-prefix-full-resend.json'; d=json.load(open(path, encoding='utf-8')); d['summary']=p.summarize(d['records']); open(path, 'w', encoding='utf-8').write(json.dumps(d, indent=2, sort_keys=True)+'\\n'); print(json.dumps(d['summary']['gate'], indent=2, sort_keys=True))\""
```

## Copy Raw Artifacts Back To Mac

```bash
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/rpfr-results/rpfr-2026-06-03 research/01-ssd-native-inference-current/benchmarks/rpfr-results/
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/rpfr-cache/rpfr-2026-06-03 research/01-ssd-native-inference-current/benchmarks/rpfr-cache/
scp -r dushyantpc:C:/Users/Dushyant/Projects/ai-research-lab/research/01-ssd-native-inference-current/benchmarks/restored-prefix-full-resend-results/restored-prefix-full-resend-2026-06-03 research/01-ssd-native-inference-current/benchmarks/restored-prefix-full-resend-results/
```

## Validation

```bash
python3 -m unittest tests.test_restored_prefix_full_resend_probe
npx --yes @fission-ai/openspec@latest validate --all --strict
```
