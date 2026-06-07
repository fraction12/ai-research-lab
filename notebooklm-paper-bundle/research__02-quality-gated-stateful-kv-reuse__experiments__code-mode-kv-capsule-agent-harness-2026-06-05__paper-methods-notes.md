# Paper Methods Notes

This artifact is a model-bearing viability probe, not the final paper benchmark.

The Code-mode route follows the OpenClaw documented shape at the contract level: a narrow `exec`/`wait` model-visible surface, a hidden run-scoped tool catalog, policy-filtered calls, and host-mediated execution. The implementation here is a local emulator, not a production OpenClaw runtime.

The KV route uses llama.cpp sequence-file state on Gemma 4 12B. The restored condition appends only the volatile tail after restoring the stable prefix state. The runner records capsule bytes, sequence tokens saved/loaded, route metadata, prompt sizes, timing, and live-vs-restored hashes.

Interpret the 30-case result as support for three separable mechanisms:

- Code-mode tool-surface compression: `code_mode_full_visible` passed 30/30 while direct visible tools passed 19/30 gates.
- Hidden prefix/capsule state: `code_mode_native_live_append` and `code_mode_restored_kv_capsule` both passed 30/30 while fresh-tail passed 0/30 answers.
- Capsule semantic parity: live/restored response, normalized response, and generated-token hashes matched 30/30.

The next paper-facing benchmark should keep the same controls but move to non-handmade task sources. It should continue to report by task family and distinguish direct-tool weakness, compact-evidence weakness, Code-mode bridge brittleness, and true capsule divergence.
