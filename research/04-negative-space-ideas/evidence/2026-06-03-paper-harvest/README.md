# 2026-06-03 Paper Harvest

Purpose: first Printing Press-assisted paper-finding pass for the current negative-space scan anchors.

## Attempt: arXiv exact-ID harvest

Timestamp: 2026-06-03T16:40:50Z

Command:

```bash
arxiv-pp-cli query --id-list '2605.26289,2605.03375,2605.18071,2604.26557,2603.17803,2605.18421,2604.15774,2508.09442,2508.08438,2511.16682,2511.07885' --max-results 11 --timeout 60s --agent --deliver file:research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/arxiv-negative-space-anchors.json
```

Result:

```text
server error 503, retrying in 2s (attempt 2/3)
rate limited, waiting 5s (attempt 3/3, rate adjusted to 0.0 req/s)
Error: GET /api/query returned HTTP 429: Rate exceeded.
GET /api/query returned HTTP 429: Rate exceeded.
```

No raw result file was produced. Retry after the arXiv rate-limit window clears, or split the ID list into smaller batches.

## Rate-safe retry plan

Use `rate-safe-arxiv-harvest.sh` instead of a single multi-ID request. It follows the official arXiv API guidance to avoid rapid repeated calls, but uses a more conservative default: one exact-ID request per paper, 30 minutes of initial cooldown, and 30 seconds between requests.

The script stops immediately on HTTP 429/rate-limit output so the run does not keep hammering the provider after arXiv asks us to wait.

Command:

```bash
research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/rate-safe-arxiv-harvest.sh
```

Outputs:

- `raw/arxiv-<id>.json`: one saved provider output per successful paper lookup.
- `harvest.log`: command timing, CLI version, success/failure status, and provider error text.

Source note: arXiv's API manual asks clients making repeated API calls to "play nice" and include a 3 second delay, and recommends smaller/refined result slices for larger result sets.

## Attempt: rate-safe single-ID harvest

Timestamp: 2026-06-03T16:48:07Z to 2026-06-03T16:50:23Z

Command:

```bash
research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/rate-safe-arxiv-harvest.sh
```

Configured behavior:

- Initial cooldown: 120 seconds for this first test run.
- Batch size: one arXiv ID per request.
- Stop condition: exit immediately on HTTP 429/rate-limit output.

Result:

```text
2026-06-03T16:50:07Z fetch id=2605.26289
rate limited, waiting 5s (attempt 1/3, rate adjusted to 0.0 req/s)
rate limited, waiting 5s (attempt 2/3, rate adjusted to 0.0 req/s)
rate limited, waiting 5s (attempt 3/3, rate adjusted to 0.0 req/s)
Error: GET /api/query returned HTTP 429: Rate exceeded.
GET /api/query returned HTTP 429: Rate exceeded.
2026-06-03T16:50:23Z stop id=2605.26289 status=7 reason=rate-limited
```

No raw result file was produced. The current IP/client remained inside arXiv's rate window after the initial two-minute cooldown. Do not retry immediately; the runner now defaults to a 30-minute cooldown before the first request.

## Attempt: user-triggered retry

Timestamp: 2026-06-03T16:58:36Z to 2026-06-03T16:59:53Z

Command:

```bash
ARXIV_INITIAL_COOLDOWN_SECONDS=0 ARXIV_HARVEST_DELAY_SECONDS=30 research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/rate-safe-arxiv-harvest.sh
```

Configured behavior:

- Initial cooldown skipped because enough wall-clock time had passed since the previous attempt.
- Batch size: one arXiv ID per request.
- Stop condition: exit immediately on rate-limit output.

Result:

```text
2026-06-03T16:58:36Z fetch id=2605.26289
rate limited, waiting 5s (attempt 1/3, rate adjusted to 0.0 req/s)
rate limited, waiting 5s (attempt 2/3, rate adjusted to 0.0 req/s)
rate limited, waiting 5s (attempt 3/3, rate adjusted to 0.0 req/s)
Error: GET /api/query returned HTTP 503: <!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>503</title>
  </head>
  <body>
    503
  </body>
</html>
GET /api/query returned HTTP 503: <!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>503</title>
  </head>
  <body>
    503
  </body>
</html>
2026-06-03T16:59:53Z stop id=2605.26289 status=5 reason=rate-limited
```

No raw result file was produced. The printed CLI still observed rate-limit output during retries, then received a provider-side 503. Treat this as provider-side throttling/unavailability for the current client/IP; do not retry rapidly.

## Attempt: OpenAlex exact DOI-form lookup plus arXiv HTML confirmation

Timestamp: 2026-06-03T17:13:35Z to 2026-06-03T17:15:26Z

Command:

```bash
research/04-negative-space-ideas/evidence/2026-06-03-paper-harvest/fallback-openalex-arxiv-harvest.py
```

Provider strategy:

- Use `openalex-pp-cli works get https://doi.org/10.48550/arxiv.<id>` for exact arXiv DOI-form metadata lookup.
- Use direct OpenAlex REST only if the printed CLI lookup fails.
- Fetch `https://arxiv.org/abs/<id>` HTML as confirmation metadata.
- Do not fetch PDFs or full text.
- Use a 5 second delay between provider requests.

Result:

```text
2026-06-03T17:13:35Z fallback OpenAlex/arXiv HTML harvest starting
2026-06-03T17:15:26Z fallback OpenAlex/arXiv HTML harvest complete
```

All 11 source anchors completed with `status=ok`.

Outputs:

- `negative-space-harvest-summary.json`: normalized metadata, provider provenance, raw output paths, and no-PDF status.
- `negative-space-harvest-summary.md`: compact agent-readable table.
- `raw/openalex-cli-<id>.json`: raw OpenAlex provider output from the printed CLI.
- `raw/arxiv-html-<id>.html`: raw arXiv HTML confirmation page.

## Printed CLI follow-up: `paper-harvester`

Timestamp: 2026-06-03T17:41:49Z to 2026-06-03T17:56:00Z

The fallback workflow above was folded into a proper internal Printing Press CLI named `paper-harvester`.

Generated/promoted CLI:

- Runstate source: `/Users/dushyantgarg/printing-press/.runstate/ai-research-lab-7f46b067/runs/20260603-134149/working/paper-harvester-pp-cli/`
- Local library source: `/Users/dushyantgarg/printing-press/library/paper-harvester/`
- Installed binary: `/opt/homebrew/bin/paper-harvester-pp-cli`
- Project skill: `.codex/skills/pp-paper-harvester/SKILL.md`

Verification:

- `cli-printing-press shipcheck` passed all 6 legs.
- Full live dogfood acceptance passed 43/43 mandatory tests and wrote `phase5-acceptance.json`.
- `paper-harvester-pp-cli harvest anchors` harvested all 11 current negative-space anchors with `status=ok`.
- No PDFs or full-text artifacts were downloaded.
