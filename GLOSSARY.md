# Glossary

## KV Cache

Stored attention keys and values from previous tokens, reused so the model does not recompute the entire prefix.

## Prefill

The phase where a model processes the input prompt before generating the first new token.

## Decode

The phase where a model generates new tokens one at a time after prefill.

## Prefix Cache

A cache of reusable prompt prefixes or their derived inference state.

## PagedAttention

A KV cache layout strategy that stores attention state in paged blocks to reduce fragmentation and improve serving efficiency.

## MoE

Mixture of Experts. A sparse model architecture where only some expert submodules are activated for each token.

## Expert Paging

Keeping frequently used MoE experts in fast memory while loading colder experts from slower storage when needed.

## Read Amplification

Extra bytes read from storage beyond the data that was actually useful.

## Warm Run

An inference run that benefits from previously populated caches.

## Cold Run

An inference run with no relevant cache already available.

