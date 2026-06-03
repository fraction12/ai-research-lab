---
name: pp-paper-harvester
description: "Internal paper metadata harvesting for lab research notes. Trigger phrases: `harvest paper anchors`, `collect arXiv paper metadata`, `find scholarly papers on`, `use paper harvester`, `run paper-harvester`."
author: "Dushyant Garg"
license: "Apache-2.0"
argument-hint: "<command> [args] | install cli|mcp"
allowed-tools: "Read Bash"
metadata:
  openclaw:
    requires:
      bins:
        - paper-harvester-pp-cli
---

# Paper Harvester — Printing Press CLI

## Prerequisites: Install the CLI

This skill drives the `paper-harvester-pp-cli` binary. **You must verify the CLI is installed before invoking any command from this skill.** If it is missing, install it first:

1. Verify: `paper-harvester-pp-cli --version`
2. If missing on this lab machine, install it from the promoted local Printing Press library:
   ```bash
   install -m 0755 /Users/dushyantgarg/printing-press/library/paper-harvester/paper-harvester-pp-cli /opt/homebrew/bin/paper-harvester-pp-cli
   ```
3. If the promoted binary is missing, rebuild it locally first (requires Go 1.26.4 or newer):
   ```bash
   cd /Users/dushyantgarg/printing-press/library/paper-harvester
   go build -o paper-harvester-pp-cli ./cmd/paper-harvester-pp-cli
   install -m 0755 paper-harvester-pp-cli /opt/homebrew/bin/paper-harvester-pp-cli
   ```

If `--version` reports "command not found" after install, the install step did not put the binary on `$PATH`. Do not proceed with skill commands until verification succeeds. This is an internal lab CLI, not a public `printing-press-library` package.

Paper Harvester collects OpenAlex metadata and arXiv confirmation pages for known paper anchors, preserving raw provider files and compact summaries. It is built for research evidence, not paper-library product management.

## When to Use This CLI

Use Paper Harvester when research threads need to collect metadata for known scholarly paper anchors, especially arXiv-heavy prior-art lists. Do not use it as a general browser scraper or PDF downloader.

## Anti-triggers

Do not use this CLI for:
- Do not use this CLI to download PDFs by default.
- Do not use this CLI for write operations against providers.
- Do not use this CLI as a consumer paper-library product.

## Unique Capabilities

These capabilities aren't available in any other tool for this API.

### Evidence workflows
- **`harvest anchors`** — Harvest known arXiv anchors into raw provider files and compact summaries.

  _Use this when a research note already has arXiv anchors and needs auditable metadata quickly._

  ```bash
  paper-harvester-pp-cli harvest anchors --agent
  ```

## Command Reference

**arxiv** — Fetch arXiv abstract pages for confirmation metadata

- `paper-harvester-pp-cli arxiv <arxiv_id>` — Fetch an arXiv abstract page as confirmation metadata

**works** — Search and fetch OpenAlex scholarly works

- `paper-harvester-pp-cli works get` — Get one OpenAlex work by OpenAlex ID, DOI URL, DOI, PMID, PMCID, or MAG ID
- `paper-harvester-pp-cli works list` — Search OpenAlex works


### Finding the right command

When you know what you want to do but not which command does it, ask the CLI directly:

```bash
paper-harvester-pp-cli which "<capability in your own words>"
```

`which` resolves a natural-language capability query to the best matching command from this CLI's curated feature index. Exit code `0` means at least one match; exit code `2` means no confident match — fall back to `--help` or use a narrower query.

## Recipes

### Fetch one arXiv-backed OpenAlex work

```bash
paper-harvester-pp-cli works get https://doi.org/10.48550/arxiv.2605.03375 --agent --select id,title,publication_year,open_access
```

Gets exact metadata for a known arXiv paper while preserving agent-readable JSON.

### Search with compact fields

```bash
paper-harvester-pp-cli works list --search "stateful inference agent tool calling" --per-page 5 --agent --select id,title,publication_year
```

Keeps OpenAlex search output bounded for research-thread context.

### Harvest known anchors

```bash
paper-harvester-pp-cli harvest anchors --agent
```

Writes raw OpenAlex JSON and arXiv HTML confirmation files for the lab's current anchor list.

## Auth Setup

No authentication required.

Run `paper-harvester-pp-cli doctor` to verify setup.

## Agent Mode

Add `--agent` to any command. Expands to: `--json --compact --no-input --no-color --yes`.

- **Pipeable** — JSON on stdout, errors on stderr
- **Filterable** — `--select` keeps a subset of fields. Dotted paths descend into nested structures; arrays traverse element-wise. Critical for keeping context small on verbose APIs:

  ```bash
  paper-harvester-pp-cli works list --agent --select id,name,status
  ```
- **Previewable** — `--dry-run` shows the request without sending
- **Offline-friendly** — sync/search commands can use the local SQLite store when available
- **Non-interactive** — never prompts, every input is a flag
- **Read-only** — do not use this CLI for create, update, delete, publish, comment, upvote, invite, order, send, or other mutating requests

### Response envelope

Commands that read from the local store or the API wrap output in a provenance envelope:

```json
{
  "meta": {"source": "live" | "local", "synced_at": "...", "reason": "..."},
  "results": <data>
}
```

Parse `.results` for data and `.meta.source` to know whether it's live or local. A human-readable `N results (live)` summary is printed to stderr only when stdout is a terminal AND no machine-format flag (`--json`, `--csv`, `--compact`, `--quiet`, `--plain`, `--select`) is set — piped/agent consumers and explicit-format runs get pure JSON on stdout.

## Agent Feedback

When you (or the agent) notice something off about this CLI, record it:

```
paper-harvester-pp-cli feedback "the --since flag is inclusive but docs say exclusive"
paper-harvester-pp-cli feedback --stdin < notes.txt
paper-harvester-pp-cli feedback list --json --limit 10
```

Entries are stored locally at `~/.local/share/paper-harvester-pp-cli/feedback.jsonl`. They are never POSTed unless `PAPER_HARVESTER_FEEDBACK_ENDPOINT` is set AND either `--send` is passed or `PAPER_HARVESTER_FEEDBACK_AUTO_SEND=true`. Default behavior is local-only.

Write what *surprised* you, not a bug report. Short, specific, one line: that is the part that compounds.

## Output Delivery

Every command accepts `--deliver <sink>`. The output goes to the named sink in addition to (or instead of) stdout, so agents can route command results without hand-piping. Three sinks are supported:

| Sink | Effect |
|------|--------|
| `stdout` | Default; write to stdout only |
| `file:<path>` | Atomically write output to `<path>` (tmp + rename) |
| `webhook:<url>` | POST the output body to the URL (`application/json` or `application/x-ndjson` when `--compact`) |

Unknown schemes are refused with a structured error naming the supported set. Webhook failures return non-zero and log the URL + HTTP status on stderr.

## Named Profiles

A profile is a saved set of flag values, reused across invocations. Use it when a scheduled agent calls the same command every run with the same configuration - HeyGen's "Beacon" pattern.

```
paper-harvester-pp-cli profile save briefing --json
paper-harvester-pp-cli --profile briefing works list
paper-harvester-pp-cli profile list --json
paper-harvester-pp-cli profile show briefing
paper-harvester-pp-cli profile delete briefing --yes
```

Explicit flags always win over profile values; profile values win over defaults. `agent-context` lists all available profiles under `available_profiles` so introspecting agents discover them at runtime.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Usage error (wrong arguments) |
| 3 | Resource not found |
| 5 | API error (upstream issue) |
| 7 | Rate limited (wait and retry) |
| 10 | Config error |

## Argument Parsing

Parse `$ARGUMENTS`:

1. **Empty, `help`, or `--help`** → show `paper-harvester-pp-cli --help` output
2. **Starts with `install`** → ends with `mcp` → MCP installation; otherwise → see Prerequisites above
3. **Anything else** → Direct Use (execute as CLI command with `--agent`)

## MCP Server Installation

1. Install the MCP server:
   ```bash
   go install github.com/mvanhorn/printing-press-library/library/ai/paper-harvester/cmd/paper-harvester-pp-mcp@latest
   ```
2. Register with Claude Code:
   ```bash
   claude mcp add paper-harvester-pp-mcp -- paper-harvester-pp-mcp
   ```
3. Verify: `claude mcp list`

## Direct Use

1. Check if installed: `which paper-harvester-pp-cli`
   If not found, offer to install (see Prerequisites at the top of this skill).
2. Match the user query to the best command from the Unique Capabilities and Command Reference above.
3. Execute with the `--agent` flag:
   ```bash
   paper-harvester-pp-cli <command> [subcommand] [args] --agent
   ```
4. If ambiguous, drill into subcommand help: `paper-harvester-pp-cli <command> --help`.
