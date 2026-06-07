# Continuation Interpretation

Date: 2026-06-03

## Decision

For `gpt-oss-20b-mxfp4.gguf` on the DushyantPC llama.cpp portable Vulkan backend, the current tail-only `/completion` protocol is not a valid semantic continuation primitive.

The decisive pattern is:

| Control | Result | Meaning |
| --- | ---: | --- |
| `full` | 3/3 pass | The model can solve the tiny task when the remembered token and question are visible together. |
| `fresh-tail` | 0/3 pass | The tail prompt alone is not accidentally guessable. |
| `live-tail` | 0/3 pass | Same-slot tail-only completion did not use the primed prefix as semantic prior context. |
| `restored-tail` | 0/3 pass | Save/restore did not recover semantic continuation behavior. |

All tail-only failures returned valid JSON with parsed answer `I am a secret token`, so the failure is not scorer/parser brittleness.

## Restore Sanity

The restored-tail path did write and restore slot files:

| Case | Slot file | Saved tokens | Restored tokens |
| --- | --- | ---: | ---: |
| `secret-alpha` | `secret-alpha-984845f9cc0284a4-slot.bin` | 37 | 37 |
| `secret-bravo` | `secret-bravo-e5a1968c2c16063b-slot.bin` | 38 | 38 |
| `secret-charlie` | `secret-charlie-ee554eba9f2163d3-slot.bin` | 38 | 38 |

Because `live-tail` failed before any disk save/restore was involved, the first-order issue is not simply slot-file storage.

## Failure Taxonomy

| Category | Classification | Evidence |
| --- | --- | --- |
| Model weakness | Unlikely primary cause | `full` passed 3/3 with exact token answers. |
| Prompt protocol issue | Implicated | Tail-only calls behaved like the unprimed `fresh-tail` control. |
| Scorer/parser brittleness | Ruled out for this litmus | All 12 responses parsed as JSON answer objects. |
| Session/cache semantic issue | Implicated at endpoint/protocol level | `live-tail` failed 3/3 with no save/restore. |
| Position/compatibility issue | Not isolated | `restored-tail` failed, but `live-tail` also failed. |
| Runtime/storage issue | Unlikely primary cause | No runtime errors; slot save/restore telemetry reported 37 to 38 tokens restored. |

## Implication For Track 02

The prior six-case GraphWalks `live-tail` and restored `session-tail` failures should not be treated as evidence that disk persistence alone corrupts useful KV state. The stronger interpretation is that the current harness protocol is asking llama.cpp for a second independent tail completion, not a reliably chat/session-formatted continuation over the primed context.

For GraphWalks-like reasoning-over-prefix work, fallback remains full-prompt execution until the protocol changes or a lower-level continuation primitive is validated.

Options 2 and 3 remain open:

| Option | Use When |
| --- | --- |
| Same-backend stronger/different model control | We want to test whether a different model/format happens to tolerate this protocol. |
| Lower-level repair probe | We want a real mechanism path that does not depend on tail-only `/completion` behaving like append continuation. |
