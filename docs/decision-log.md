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

