# Resources

## Core Videos

- Reiner Pope on Dwarkesh: https://youtu.be/xmkSf5IS-zw  
  Use for inference economics, memory bandwidth, sparsity, and context cost.

- LMCache intro: https://www.youtube.com/watch?v=rINy7mFyRAU  
  Use for KV reuse and cache-layer thinking.

- Prince Canuma MLX talk: https://www.youtube.com/watch?v=zTLJNHj0DeQ  
  Use for Apple Silicon and MLX local inference direction.

## Core Reading

- vLLM PagedAttention: https://docs.vllm.ai/en/stable/design/paged_attention/  
  Learn how KV cache paging works.

- LMCache architecture: https://docs.lmcache.ai/developer_guide/architecture.html  
  Learn the production shape of KV cache reuse.

- LMCache local storage backend: https://docs.lmcache.ai/dev/kv_cache/storage_backends/local_storage.html  
  Learn local disk/offload mechanics.

- Apple LLM in a Flash: https://machinelearning.apple.com/research/efficient-large-language  
  Learn the flash-memory framing.

- FlexGen: https://arxiv.org/abs/2303.06865  
  Learn older offload ancestry and tradeoffs.

## Tools and Repos

- oMLX: https://github.com/jundot/omlx  
  Closest practical Apple Silicon reference.

- Matt Pocock skills: https://github.com/mattpocock/skills  
  Source of the repo-local `teach` skill.

## Compression

- TurboQuant coverage: https://www.tomshardware.com/tech-industry/artificial-intelligence/googles-turboquant-compresses-llm-kv-caches-to-3-bits-with-no-accuracy-loss

- TurboQuant hub: https://turbo-quant.com/turboquant-paper

