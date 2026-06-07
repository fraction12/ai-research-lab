# Capsule Contract

This Family 1 gate tested an opaque llama.cpp context state capsule created with `llama_state_get_size` / `llama_state_get_data`, then restored with `llama_state_set_data`.

## Contract Tested

- Prefix prefill: simple codeword prefix only.
- Prefix tokenization route: `add_special=true`.
- Tail append route: `add_special=false`.
- Restore target: fresh native context initialized from the same model and context parameters.
- Append position: `n_past_before_tail_append` equals the prefix token count.
- Generation start: `generation_start_pos` equals prefix token count plus tail token count.

## Observed State

- Restored capsule controls run: 3.
- Answer-contained restored capsule pass: 3/3.
- Mean capsule bytes: 869395.0.
- Mean capsule save ms: 1.147866656538099.
- Mean capsule restore ms: 151.6506333524982.
- State bytes requested equaled state bytes restored in all restored controls.

## Validity Boundary

This establishes a semantic continuation result only for the 3-case simple codeword Family 1 gate on the pinned GPT-OSS/llama.cpp b9493 bundle. It does not claim GraphWalks correctness, broad benchmark quality, or cross-model compatibility.
