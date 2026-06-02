# References

## Current Systems and Repos

- oMLX: https://github.com/jundot/omlx  
  Apple Silicon inference server with continuous batching and SSD caching. Closest practical local reference.

- LMCache architecture: https://docs.lmcache.ai/developer_guide/architecture.html  
  Production-shaped KV cache layer.

- LMCache local storage backend: https://docs.lmcache.ai/dev/kv_cache/storage_backends/local_storage.html  
  Concrete disk/offload mechanics.

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

