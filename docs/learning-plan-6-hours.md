# Six-Hour Learning Plan

Spend the six hours learning memory hierarchy for inference, not generic AI.

## Hour 1: The Physics

Watch: Reiner Pope on Dwarkesh

https://youtu.be/xmkSf5IS-zw

Focus on:

- memory bandwidth
- batching
- MoE sparsity
- context cost
- why inference is constrained by data movement

Output: write five bullets on what makes tokens slow.

## Hour 2: KV Cache and PagedAttention

Read:

- https://docs.vllm.ai/en/stable/design/paged_attention/
- https://www.runpod.io/articles/guides/vllm-pagedattention-continuous-batching

Focus on:

- KV cache layout
- paging
- fragmentation
- continuous batching
- why serving becomes memory management

Output: sketch how PagedAttention maps logical tokens to physical blocks.

## Hour 3: Disk and SSD KV Systems

Watch:

- https://www.youtube.com/watch?v=rINy7mFyRAU

Read:

- https://docs.lmcache.ai/developer_guide/architecture.html
- https://docs.lmcache.ai/dev/kv_cache/storage_backends/local_storage.html

Focus on:

- KV cache offload
- local storage backends
- cache hit rates
- prefill acceleration
- multi-tier memory

Output: define what should be cache key material for an agent prompt.

## Hour 4: Apple Silicon and MLX

Watch:

- https://www.youtube.com/watch?v=zTLJNHj0DeQ

Read:

- https://thinksmart.life/research/posts/apple-silicon-mlx-llm-guide/
- https://github.com/jundot/omlx

Focus on:

- unified memory
- MLX execution model
- local inference ergonomics
- oMLX's SSD-backed cache direction

Output: decide whether the first prototype wraps MLX, llama.cpp, or both.

## Hour 5: Compression

Read:

- https://www.tomshardware.com/tech-industry/artificial-intelligence/googles-turboquant-compresses-llm-kv-caches-to-3-bits-with-no-accuracy-loss
- https://turbo-quant.com/turboquant-paper

Focus on:

- KV cache quantization
- 2-bit to 4-bit storage
- quality drift
- cache capacity gains
- bandwidth reduction

Output: list the first three things to compress and what quality test would catch damage.

## Hour 6: Offload Ancestry and Thesis

Read:

- https://machinelearning.apple.com/research/efficient-large-language
- https://arxiv.org/abs/2303.06865

Then stop consuming and write one page covering:

- target workload
- memory tiers
- what lives on SSD
- what stays hot
- prefetch strategy
- benchmark definition

