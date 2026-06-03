# Mission

## Topic

SSD-native inference for local AI agents.

## Why This Matters

The goal is to understand whether a new class of local inference system can make long-context agent work faster and cheaper by using SSDs as a serious memory tier.

The project is not trying to prove a slogan. It is trying to find the useful shape:

- what should stay hot in RAM or unified memory
- what can live on SSD
- what needs compression
- where prefetching matters
- which workloads benefit first

## Desired Outcome

Build enough understanding to make tasteful product and architecture decisions, then create a prototype that measures whether repeated agent workloads get materially faster.

## Constraints

- Six-hour first learning sprint
- Local-first bias
- Apple Silicon / MLX is an important playground
- llama.cpp portability may matter
- Benchmarks must separate cold, warm, and repeated runs

## First Practical Question

Can repeated OpenClaw-style agent prompts use persistent prefix/KV caching to reduce prefill time without damaging output quality?

