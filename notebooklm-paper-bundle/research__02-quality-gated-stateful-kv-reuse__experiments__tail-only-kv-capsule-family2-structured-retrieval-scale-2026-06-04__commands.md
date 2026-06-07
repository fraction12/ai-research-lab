# Commands

## Local Prep

```bash
python3 -m py_compile research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-family2-structured-retrieval-scale-2026-06-04/raw/tail_only_kv_capsule_family2_scale.py
python3 research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-family2-structured-retrieval-scale-2026-06-04/raw/tail_only_kv_capsule_family2_scale.py --help
openspec validate scale-tail-only-kv-capsule-structured-retrieval --type change --strict
```

## Remote Model-Bearing Gates

The model-bearing commands were run by orchestration on DushyantPC using held/foreground SSH. Raw prompt-bearing outputs were copied back under the ignored Track 01 raw path.

```powershell
python tail_only_kv_capsule_family2_scale.py --mode family2-smoke --state-route auto
python tail_only_kv_capsule_family2_scale.py --mode family2-30 --state-route auto
```

Primary run metadata:

- mode: `family2-30`
- effective route: `seq_file` / `seq-file`
- decision: `family2_sequence_state_restored_capsule_semantic_passed_hash_warning`
- record count: `120`

## Packaging And Validation

```bash
openspec validate scale-tail-only-kv-capsule-structured-retrieval --type change --strict
openspec validate replicate-kv-capsule-gemma4-12b --type change --strict
openspec validate --all --strict
```
