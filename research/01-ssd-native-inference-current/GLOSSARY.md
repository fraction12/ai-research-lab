# Glossary

## KV Cache

Stored attention keys and values from previous tokens, reused so the model does not recompute the entire prefix.

## Prefill

The phase where a model processes the input prompt before generating the first new token.

## Decode

The phase where a model generates new tokens one at a time after prefill.

## Prefix Cache

A cache of reusable prompt prefixes or their derived inference state.

## Attention Sink

An initial token or small group of initial tokens that a model attends to strongly as an attention anchor, even when the token content is not semantically important.

## Rolling KV Cache

A bounded KV cache that keeps recent tokens while older tokens roll out of the active cache.

## Prefix Block Store

A content-addressed store for reusable prompt blocks and cache-key metadata.

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
