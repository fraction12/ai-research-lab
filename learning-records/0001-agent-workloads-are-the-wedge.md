# Agent Workloads Are the Wedge

## Date

2026-06-02

## Lesson

SSD-native inference is most plausible for repeated long-context agent workloads, not generic chat.

## Why It Matters

Agents repeatedly reuse system prompts, tool schemas, repo context, memory blocks, and task scaffolds. That repeated structure gives a cache layer something real to exploit.

## Implication

The first prototype should measure repeated-agent-loop speedups. It should not start with "can we run a huge dense model from disk?" as the central proof.

## Open Questions

- How much of OpenClaw's recurring context can be represented as stable prompt blocks?
- Which backend exposes enough KV/cache hooks to make this practical first?
- How much quality drift appears when KV cache compression is introduced?

