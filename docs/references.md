# References

## Current Systems and Repos

- Ollama API usage metrics: https://docs.ollama.com/api/usage
  Source for local timing fields such as `prompt_eval_count`, `prompt_eval_duration`, `eval_count`, and `eval_duration`.

- Ollama generate API reference: https://github.com/ollama/ollama/blob/main/docs/api.md
  Source for non-streaming `/api/generate` behavior and response timing fields.

- oMLX: https://github.com/jundot/omlx
  Apple Silicon inference server with continuous batching and SSD caching. Closest practical local reference.

- oMLX product site: https://omlx.ai/
  Claims hot RAM plus cold SSD KV cache for Apple Silicon local agent workflows.

- llama.cpp server prompt cache and slot save/restore: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
  Practical local prompt/KV cache persistence reference.

- OpenAI Chat Completions API reference: https://developers.openai.com/api/reference/resources/chat
  Compatibility shape for the local wrapper's first non-streaming `/v1/chat/completions` subset.

- LMCache architecture: https://docs.lmcache.ai/developer_guide/architecture.html
  Production-shaped KV cache layer.

- LMCache local storage backend: https://docs.lmcache.ai/kv_cache/storage_backends/local_storage.html
  Concrete disk/offload mechanics.

- vLLM automatic prefix caching: https://docs.vllm.ai/en/latest/design/prefix_caching/
  Current design doc for hash-based prefix KV block reuse.

- vLLM PagedAttention: https://docs.vllm.ai/en/stable/design/paged_attention/
  Key mental model for paged KV memory.

- NVIDIA Dynamo KV cache offloading: https://docs.nvidia.com/dynamo/backends/v-llm/kv-cache-offloading
  Production signal that multi-tier KV cache matters.

## Papers and Research

- Apple, LLM in a Flash: https://machinelearning.apple.com/research/efficient-large-language
  Original flash-memory framing for inference.

- Apple LLM in a Flash paper: https://arxiv.org/abs/2312.11514
  Paper version.

- FlexGen: https://arxiv.org/abs/2303.06865
  Earlier offload system; useful ancestry, more throughput/batch oriented than local interactive use.

- PagedAttention / vLLM paper: https://arxiv.org/abs/2309.06180
  Establishes block-based KV cache memory management and sharing across requests.

- StreamingLLM / Attention Sinks: https://arxiv.org/html/2309.17453v4
  Learn why rolling KV cache should keep initial attention-sink tokens instead of blindly evicting old context.

- StreamingLLM code: https://github.com/mit-han-lab/streaming-llm
  Reference implementation for attention-sink plus rolling KV cache behavior.

- CacheGen: https://arxiv.org/abs/2310.07240
  KV cache compression and streaming for reducing context-loading delay.

- Prompt Cache: https://arxiv.org/abs/2311.04934
  Modular attention-state reuse for repeated prompt segments such as system prompts, templates, and documents.

- CachedAttention: https://arxiv.org/abs/2403.19708
  Hierarchical KV caching for multi-turn conversations.

- Mooncake: https://arxiv.org/abs/2407.00079
  KVCache-centric disaggregated serving architecture that uses CPU, DRAM, and SSD resources.

- KVFlow: https://arxiv.org/abs/2507.07400
  Workflow-aware KV cache management for LLM-based multi-agent workflows.

- AdaptCache: https://arxiv.org/abs/2509.00105
  KV-cache-native DRAM/SSD storage hierarchy with compression and placement decisions.

- Tutti: https://arxiv.org/abs/2605.03375
  Recent SSD-backed KV cache work focused on making NVMe restoration practical for long-context serving.

- Don't Break the Cache: https://arxiv.org/abs/2601.06007
  Evaluation of prompt caching strategies for long-horizon agentic tasks across hosted providers.

- TurboQuant hub: https://turbo-quant.com/turboquant-paper
  KV compression direction.

## Articles and Explainers

- RunPod on vLLM PagedAttention and continuous batching: https://www.runpod.io/articles/guides/vllm-pagedattention-continuous-batching

- Tom's Hardware on TurboQuant KV cache compression: https://www.tomshardware.com/tech-industry/artificial-intelligence/googles-turboquant-compresses-llm-kv-caches-to-3-bits-with-no-accuracy-loss

- MLX Apple Silicon guide: https://thinksmart.life/research/posts/apple-silicon-mlx-llm-guide/

- Simon Willison on SSD / Flash-MoE style demos: https://simonwillison.net/2026/Mar/18/llm-in-a-flash/

## Videos

- Reiner Pope on Dwarkesh: https://youtu.be/xmkSf5IS-zw
  Inference economics, sparsity, memory, and scaling intuition.

- LMCache intro: https://www.youtube.com/watch?v=rINy7mFyRAU
  KV cache reuse and serving implications.

- Prince Canuma MLX talk: https://www.youtube.com/watch?v=zTLJNHj0DeQ  
  Apple Silicon and MLX local inference direction.

## Skill Source

- Matt Pocock skills repo: https://github.com/mattpocock/skills
- Skills directory listing: https://www.skills.sh/mattpocock/skills
- Installed repo-local skill: `.codex/skills/teach`
