## Context

The first GPT-OSS correctness smoke failed as a quality measurement because raw llama.cpp `/completion` produced reasoning text and incomplete answers. Online llama.cpp documentation says the OpenAI-compatible chat endpoint supports `response_format`, and the raw completion endpoint supports llama.cpp-specific controls such as `json_schema` and grammar-like constrained output. The raw endpoint is the better fit because the session-tail experiment depends on explicit slot save/restore around `/completion`.

## Goals / Non-Goals

**Goals:**
- Add a `json-answer` protocol that forces the model to return a JSON object with an `answer` string.
- Keep both full-prompt and session-tail modes on the same raw `/completion` slot path.
- Preserve raw response text while scoring the extracted answer.

**Non-Goals:**
- Do not switch the benchmark to `/v1/chat/completions`.
- Do not change dataset scoring rules.
- Do not claim parity until both the full baseline and session-tail path pass scorer-friendly prompts.

## Decisions

1. Use `/completion` `json_schema` instead of chat `response_format`.

   Chat completions are attractive because they apply model chat templates, but our current session-tail prototype needs direct slot control. A constrained raw completion gives us answer hygiene while keeping the same slot semantics.

2. Score the extracted answer, not the JSON envelope.

   Dataset scorers expect plain answers: node sets, exact strings, or instruction-following text. The response record will keep `raw_response` and `response`, where `response` is the extracted answer when parsing succeeds.

3. Make the protocol optional.

   Keeping `raw` as a supported protocol lets us compare old and new behavior, and avoids breaking existing recorded smoke artifacts.

## Risks / Trade-offs

- [Risk] Older llama.cpp builds may not honor `json_schema` on `/completion`. -> Mitigation: keep raw output and parse failures visible in response records.
- [Risk] Constrained decoding may change model behavior. -> Mitigation: apply the same protocol to full-prompt and session-tail modes so quality comparison stays fair.
- [Risk] JSON answer extraction can hide malformed outputs. -> Mitigation: record `answer_parse_error` and preserve `raw_response`.
