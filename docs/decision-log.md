# Decision Log

## 2026-06-02: Initial Wedge

Decision: target agent workloads first.

Reason: agents repeat long context in a way normal chat does not. Stable prefixes and tool schemas make prefix/KV caching much more valuable.

## 2026-06-02: SSD Role

Decision: treat SSD as a cache/storage tier, not VRAM.

Reason: dense per-token weight access is hostile to SSD latency and bandwidth. Prefix cache, KV cache, and cold sparse experts have better access patterns.

## 2026-06-02: First Prototype

Decision: build benchmark harness before runtime machinery.

Reason: this space is full of impressive demos and weak measurements. The project needs cold/warm/repeated-agent-loop numbers from day one.

## 2026-06-02: Local Backend

Decision: start by wrapping an existing backend rather than writing a transformer runtime.

Reason: the invention should be in storage-aware inference state, not reimplementing matrix kernels.

## 2026-06-02: Persistence Gap

Decision: treat cross-session stable-prefix persistence as the next prototype target.

Reason: aligned prompts get cheaper while Ollama stays warm, but restarting the model before each changed-tail prompt increased prompt evaluation from 7,985.0 ms to 21,065.1 ms on the LightningITB DeepClean campaign fixture. That 13,080.1 ms gap is the first concrete target for persistent prefix/KV cache work.

## 2026-06-02: Attention Sinks

Decision: distinguish attention-sink candidates from ordinary reusable prefix blocks.

Reason: StreamingLLM shows that initial-token KV can stabilize rolling cache behavior. The prefix store should therefore mark sink candidates and avoid treating all old prompt state as equally evictable or offloadable.

## 2026-06-02: Research Positioning

Decision: position the project as a local-agent persistence wedge, not as the invention of KV caching or SSD-backed inference.

Reason: online prior-art review found established work in prefix caching, prompt-state reuse, hierarchical KV storage, and SSD-backed KV systems. The remaining defensible question is whether persistent, storage-aware prefix/KV reuse can make realistic local agent loops fast across changed-tail prompts and cold or restarted sessions.

## 2026-06-02: llama.cpp Baseline

Decision: treat llama.cpp slot save/restore as the first close backend baseline and likely first wrapper target.

Reason: a local run against the LightningITB fixture showed that saving a 672-token reusable prefix slot and restoring it across fresh `llama-server` processes reduced prompt evaluation from 310.686 ms to 172.911 ms on `gemma-3-270m-it-Q8_0.gguf`. Custom SSD-native work now has to beat this baseline or add useful indexing, policy, and ergonomics around it.

## 2026-06-03: Paper Direction

Decision: frame the publishable research topic around quality-gated persistent/session KV reuse for local agent loops.

Reason: the online prior-art scan found that prefix caching, prompt-state reuse, multi-tier KV storage, SSD/NVMe KV offload, and agentic prompt caching are already active research areas. The remaining wedge is the correctness contract: when restored-prefix or session-tail execution on local non-frontier models is equivalent enough to full-prompt execution, how failures should be attributed, and when the system should fall back to full-prompt mode.

## 2026-06-03: Discovery Research Posture

Decision: make controlled contrarian experiments a first-class part of the repo.

Reason: a publishable result is unlikely to come from only optimizing known cache paths. The project should deliberately challenge mainstream assumptions, such as exact-prefix reuse, all-or-nothing equivalence, and recompute-as-failure, while requiring each strange idea to define a measurable prediction, controls, confounders, and a stop rule.
