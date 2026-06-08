# BFCL Updated-Harness Regression Audit - 2026-06-08

## Scope

Compared the frozen initial official BFCL non-live baseline against the completed updated-harness clean official evaluator run.

Baseline:
- Source: paper ledger / v1 official calibration.
- Score: `969/1390`, BFCL Non-Live AST Acc `69.88%`.

Updated clean run:
- Source: DushyantPC `C:\ai\bfcl-official-full-nonlive-v4-run\lane\official-export\score-full-nonlive-v4-clean\`.
- Records: `1390/1390`, unique case IDs `1390`, backend/runtime errors `0`.
- Score: BFCL Non-Live AST Acc `58.83%`.

## Category Delta

| Category | Baseline | Updated | Delta |
|---|---:|---:|---:|
| simple_python | `162/200` `81.00%` | `314/400` `78.50%` | `-2.50 pp` |
| simple_java | `84/200` `42.00%` | `39/100` `39.00%` | `-3.00 pp` |
| simple_javascript | `132/200` `66.00%` | `25/50` `50.00%` | `-16.00 pp` |
| multiple | `171/200` `85.50%` | `146/200` `73.00%` | `-12.50 pp` |
| parallel | `133/200` `66.50%` | `120/200` `60.00%` | `-6.50 pp` |
| parallel_multiple | `129/200` `64.50%` | `93/200` `46.50%` | `-18.00 pp` |
| irrelevance | `137/240` `57.08%` | `211/240` `87.92%` | `+30.83 pp` |

## Failure Shape

The updated harness did not collapse at parsing. Most outputs were parsed as BFCL call lists. The main regression is under-calling and empty/none finalization on real tool-call tasks.

Raw record shape:

| Category | Local scorer | Empty final source | Count mismatches | Avg expected calls | Avg parsed calls |
|---|---:|---:|---:|---:|---:|
| simple_python | `264/400` | `25` | `25` | `1.00` | `0.94` |
| simple_java | `41/100` | `32` | `35` | `1.00` | `0.71` |
| simple_javascript | `18/50` | `19` | `19` | `1.00` | `0.62` |
| multiple | `115/200` | `17` | `24` | `1.00` | `0.95` |
| parallel | `106/200` | `23` | `69` | `2.69` | `2.04` |
| parallel_multiple | `75/200` | `31` | `91` | `3.04` | `2.17` |
| irrelevance | `211/240` | `15` | `29` | `0.00` | `0.13` |

Official evaluator failure types:

- `parallel_multiple`: `91` wrong-count failures, `16` cannot-find-match failures, `31` failures were empty `[]`.
- `parallel`: `70` wrong-count failures, `10` cannot-find-match failures, `23` failures were empty `[]`.
- `multiple`: `24` wrong-count failures, `22` string-value failures, `17` failures were empty `[]`.
- `simple_javascript`: `19` wrong-output-format failures, all `19` were empty `[]`.
- `simple_java`: `32` wrong-output-format failures, all `32` were empty `[]`; `18` decoder failures.
- `simple_python`: `25` wrong-count failures, `39` string-value failures, `25` failures were empty `[]`.
- `irrelevance`: `29` remaining failures are non-empty decoded calls where no call was expected.

## Representative Failures

`parallel_multiple_14` expected four calls for tiger history/projections. The model emitted only two history calls:

`[animal_population.get_history(country='Bangladesh', species='tigers', years=5), animal_population.get_history(country='India', species='tigers', years=5)]`

`parallel_multiple_65` expected one property search plus two valuation calls. The model emitted only the two valuation calls.

`parallel_15` expected multiple tax calculations. The model emitted only one call:

`[calculate_capital_gains_tax(long_term_gain=25000, short_term_gain=15000, state='California')]`

`simple_javascript_2`, `simple_javascript_3`, `simple_javascript_5`, and many other JavaScript failures exported as `[]`, producing BFCL AST decoder wrong-output-format errors.

`parallel_multiple_10` emitted useful calls but used natural date strings instead of BFCL-accepted ISO date strings:

`date='June 30th 2023'` instead of `date='2023-06-30'`.

## Current Read

This is a harness/protocol regression, not an official evaluator glitch and not evidence that KV restore itself failed.

The updated v4 direction bought much better no-call behavior on irrelevance rows, but made the model too conservative on real tool-call rows. The practical failure mode is:

1. The model emits fewer calls than requested, especially when expected call count is greater than one.
2. The model sometimes emits `[]` on real tasks, especially Java/JavaScript/simple cases.
3. Remaining failures include value normalization misses such as date format, location spelling, units, and exact string literals.

The likely regression came from the v2/v3/v4 PTI hardening sequence: stricter schema/repair pressure and stronger "do not invent" constraints improved abstention but reduced action recall. The core prompt already says to count independent operations, but the model is not following that reliably under the updated contract.

## Recommended Next Move

Do not run another full BFCL yet.

Run targeted smokes that isolate the regression:

1. **Prompt ablation smoke:** keep current parser/exporter, but compare v1/v2/v3/v4 stable-prefix contracts on a 70-row stratified set: 10 per category.
2. **Action-recall prompt repair:** add stronger positive instruction for real tasks: if a provided function can satisfy an explicit requested operation, emit the call; `[]` is only for requests with no applicable provided function.
3. **Call-count repair loop:** when schema-only validation detects `parsed_count < minimum_call_count`, retry with a terse repair message before finalizing.
4. **Language bucket guard:** Java/JavaScript simple rows need a special no-empty regression test, because empty `[]` dominates the drop there.
5. **Value normalization audit:** separately test safe model-visible normalization instructions for dates, city/state strings, and unit literals without answer-key postprocessing.

Success gate before another full run:

- preserve irrelevance at or near the updated result,
- recover `parallel_multiple` and `multiple` call-count behavior on the targeted smoke,
- eliminate most `[]` outputs in simple Java/JavaScript real-call rows.
