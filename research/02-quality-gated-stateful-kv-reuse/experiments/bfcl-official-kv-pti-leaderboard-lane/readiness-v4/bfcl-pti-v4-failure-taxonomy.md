# BFCL PTI Failure Taxonomy

Post-hoc only. This artifact must not be fed into model prompts, repair prompts, or export transformations.

- Records: `15`
- Passed: `10`
- Failed: `5`

## Category Counts

- `irrelevance`: `3/3` passed
- `parallel`: `2/3` passed
- `parallel_multiple`: `1/3` passed
- `simple_java`: `2/3` passed
- `simple_javascript`: `2/3` passed

## Likely Owner Counts

- `model_argument_shape`: `2`
- `model_call_count`: `2`
- `model_format_or_empty_output`: `1`

## Failures

- `bfcl:parallel:parallel_2`: `model_call_count`; schema codes: `none`
- `bfcl:parallel_multiple:parallel_multiple_0`: `model_argument_shape`; schema codes: `none`
- `bfcl:parallel_multiple:parallel_multiple_2`: `model_call_count`; schema codes: `none`
- `bfcl:simple_java:java_1`: `model_argument_shape`; schema codes: `none`
- `bfcl:simple_javascript:javascript_2`: `model_format_or_empty_output`; schema codes: `none`
