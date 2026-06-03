#!/usr/bin/env python3
"""Harvest negative-space paper metadata through OpenAlex plus arXiv HTML.

This is an evidence runner, not a product scaffold. It keeps raw provider
payloads beside a compact summary so future research notes can trace claims
back to exact commands and URLs.
"""

from __future__ import annotations

import html.parser
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any


PAPERS = [
    {
        "title": "Stateful Inference for Low-Latency Multi-Agent Tool Calling",
        "arxiv_id": "2605.26289",
    },
    {
        "title": "Tutti",
        "arxiv_id": "2605.03375",
    },
    {
        "title": "KVDrive",
        "arxiv_id": "2605.18071",
    },
    {
        "title": "DUAL-BLADE",
        "arxiv_id": "2604.26557",
    },
    {
        "title": "Swarm",
        "arxiv_id": "2603.17803",
    },
    {
        "title": "EvoMemBench",
        "arxiv_id": "2605.18421",
    },
    {
        "title": "MemEvoBench",
        "arxiv_id": "2604.15774",
    },
    {
        "title": "Shadow in the Cache",
        "arxiv_id": "2508.09442",
    },
    {
        "title": "SafeKV",
        "arxiv_id": "2508.08438",
    },
    {
        "title": "Bench360",
        "arxiv_id": "2511.16682",
    },
    {
        "title": "Intelligence per Watt",
        "arxiv_id": "2511.07885",
    },
]


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
RAW_DIR = SCRIPT_DIR / "raw"
LOG_FILE = SCRIPT_DIR / "harvest.log"
SUMMARY_JSON = SCRIPT_DIR / "negative-space-harvest-summary.json"
SUMMARY_MD = SCRIPT_DIR / "negative-space-harvest-summary.md"
USER_AGENT = "ai-research-lab-paper-harvester/0.1"


class ArxivMetaParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.metadata: dict[str, list[str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "meta":
            return
        attr_map = {name.lower(): value for name, value in attrs if value is not None}
        name = attr_map.get("name")
        content = attr_map.get("content")
        if not name or content is None:
            return
        if name.startswith("citation_"):
            self.metadata.setdefault(name, []).append(content.strip())


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(message: str) -> None:
    line = f"{utc_now()} {message}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def tool_version(command: list[str]) -> str:
    result = run_command(command)
    text = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        return f"unavailable: {text}"
    return text


def read_json(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: pathlib.Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def unwrap_openalex(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    results = payload.get("results")
    if isinstance(results, dict) and results.get("id"):
        return results
    if payload.get("id"):
        return payload
    return None


def fetch_url(url: str, destination: pathlib.Path) -> tuple[int | None, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read()
            destination.write_bytes(body)
            return response.status, None
    except urllib.error.HTTPError as error:
        destination.write_bytes(error.read())
        return error.code, str(error)
    except urllib.error.URLError as error:
        return None, str(error)


def openalex_cli_lookup(paper: dict[str, str], force: bool) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    arxiv_id = paper["arxiv_id"]
    doi_url = f"https://doi.org/10.48550/arxiv.{arxiv_id}"
    output_path = RAW_DIR / f"openalex-cli-{arxiv_id}.json"
    stderr_path = RAW_DIR / f"openalex-cli-{arxiv_id}.stderr.txt"
    command = [
        "openalex-pp-cli",
        "works",
        "get",
        doi_url,
        "--json",
        "--no-input",
        "--no-color",
        "--yes",
        "--timeout",
        "45s",
    ]
    command_text = " ".join(command)
    provenance = {
        "provider": "OpenAlex",
        "path": "openalex-pp-cli works get",
        "command": command_text,
        "lookup_id": doi_url,
        "raw_output": str(output_path.relative_to(SCRIPT_DIR)),
        "stderr_output": str(stderr_path.relative_to(SCRIPT_DIR)),
    }

    if output_path.exists() and output_path.stat().st_size > 0 and not force:
        payload = read_json(output_path)
        provenance["status"] = "cached"
        return unwrap_openalex(payload), provenance

    log(f"openalex-cli fetch arxiv_id={arxiv_id}")
    result = run_command(command)
    output_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    provenance["exit_code"] = result.returncode
    provenance["status"] = "ok" if result.returncode == 0 else "failed"

    if result.returncode != 0:
        log(f"openalex-cli failed arxiv_id={arxiv_id} status={result.returncode}")
        return None, provenance

    try:
        return unwrap_openalex(json.loads(result.stdout)), provenance
    except json.JSONDecodeError as error:
        provenance["status"] = "invalid-json"
        provenance["error"] = str(error)
        return None, provenance


def openalex_rest_lookup(paper: dict[str, str], force: bool) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    arxiv_id = paper["arxiv_id"]
    doi_url = f"https://doi.org/10.48550/arxiv.{arxiv_id}"
    endpoint = "https://api.openalex.org/works/" + urllib.parse.quote(doi_url, safe="")
    output_path = RAW_DIR / f"openalex-rest-{arxiv_id}.json"
    provenance = {
        "provider": "OpenAlex",
        "path": "direct REST fallback",
        "url": endpoint,
        "lookup_id": doi_url,
        "raw_output": str(output_path.relative_to(SCRIPT_DIR)),
    }

    if output_path.exists() and output_path.stat().st_size > 0 and not force:
        payload = read_json(output_path)
        provenance["status"] = "cached"
        return payload if isinstance(payload, dict) and payload.get("id") else None, provenance

    log(f"openalex-rest fetch arxiv_id={arxiv_id}")
    status, error = fetch_url(endpoint, output_path)
    provenance["http_status"] = status
    if error:
        provenance["status"] = "failed"
        provenance["error"] = error
        return None, provenance

    payload = read_json(output_path)
    provenance["status"] = "ok"
    return payload if isinstance(payload, dict) and payload.get("id") else None, provenance


def arxiv_html_lookup(paper: dict[str, str], force: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    arxiv_id = paper["arxiv_id"]
    url = f"https://arxiv.org/abs/{arxiv_id}"
    output_path = RAW_DIR / f"arxiv-html-{arxiv_id}.html"
    provenance = {
        "provider": "arXiv",
        "path": "HTML fallback",
        "url": url,
        "raw_output": str(output_path.relative_to(SCRIPT_DIR)),
    }

    if output_path.exists() and output_path.stat().st_size > 0 and not force:
        html_text = output_path.read_text(encoding="utf-8", errors="replace")
        provenance["status"] = "cached"
    else:
        log(f"arxiv-html fetch arxiv_id={arxiv_id}")
        status, error = fetch_url(url, output_path)
        provenance["http_status"] = status
        if error:
            provenance["status"] = "failed"
            provenance["error"] = error
            return {}, provenance
        provenance["status"] = "ok"
        html_text = output_path.read_text(encoding="utf-8", errors="replace")

    parser = ArxivMetaParser()
    parser.feed(html_text)
    return {key: values for key, values in sorted(parser.metadata.items())}, provenance


def compact_openalex(work: dict[str, Any] | None) -> dict[str, Any]:
    if not work:
        return {}
    primary = work.get("primary_location") or {}
    best_oa = work.get("best_oa_location") or {}
    authors = []
    for authorship in work.get("authorships", [])[:12]:
        author = authorship.get("author") or {}
        name = author.get("display_name")
        if name:
            authors.append(name)
    return {
        "openalex_id": work.get("id"),
        "title": work.get("title") or work.get("display_name"),
        "doi": work.get("doi"),
        "publication_year": work.get("publication_year"),
        "publication_date": work.get("publication_date"),
        "type": work.get("type"),
        "indexed_in": work.get("indexed_in"),
        "authors": authors,
        "open_access": work.get("open_access"),
        "primary_location": {
            "id": primary.get("id"),
            "landing_page_url": primary.get("landing_page_url"),
            "pdf_url": primary.get("pdf_url"),
            "license": primary.get("license"),
            "source": (primary.get("source") or {}).get("display_name"),
            "source_type": (primary.get("source") or {}).get("type"),
        },
        "best_oa_location": {
            "id": best_oa.get("id"),
            "landing_page_url": best_oa.get("landing_page_url"),
            "pdf_url": best_oa.get("pdf_url"),
            "license": best_oa.get("license"),
            "source": (best_oa.get("source") or {}).get("display_name"),
            "source_type": (best_oa.get("source") or {}).get("type"),
        },
        "locations_count": work.get("locations_count"),
        "cited_by_count": work.get("cited_by_count"),
        "updated_date": work.get("updated_date"),
        "created_date": work.get("created_date"),
    }


def compact_arxiv(metadata: dict[str, list[str]]) -> dict[str, Any]:
    def first(key: str) -> str | None:
        values = metadata.get(key) or []
        return values[0] if values else None

    return {
        "arxiv_id": first("citation_arxiv_id"),
        "title": first("citation_title"),
        "authors": metadata.get("citation_author", []),
        "publication_date": first("citation_publication_date"),
        "pdf_url": first("citation_pdf_url"),
    }


def write_markdown(summary: dict[str, Any]) -> None:
    lines = [
        "# Negative-Space Paper Harvest Summary",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "Metadata was collected through `openalex-pp-cli works get` using arXiv DOI-form identifiers, with direct OpenAlex REST only as fallback and arXiv HTML as a confirmation path. No PDFs were downloaded.",
        "",
        "| arXiv ID | Status | OpenAlex title | OpenAlex ID | OA status | License | Raw files |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for paper in summary["papers"]:
        openalex = paper.get("openalex") or {}
        primary = openalex.get("primary_location") or {}
        best_oa = openalex.get("best_oa_location") or {}
        oa = openalex.get("open_access") or {}
        license_value = primary.get("license") or best_oa.get("license") or ""
        raw_files = ", ".join(paper.get("raw_outputs", []))
        lines.append(
            "| {arxiv_id} | {status} | {title} | {openalex_id} | {oa_status} | {license} | {raw_files} |".format(
                arxiv_id=paper["arxiv_id"],
                status=paper["status"],
                title=(openalex.get("title") or "").replace("|", "\\|"),
                openalex_id=openalex.get("openalex_id") or "",
                oa_status=oa.get("oa_status") or "",
                license=license_value or "",
                raw_files=raw_files,
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Raw provider outputs live in `raw/` next to this summary.",
            "- OpenAlex PDF URLs and arXiv PDF URLs are metadata only; this run did not fetch full-text artifacts.",
            "- arXiv Atom API remained unavailable/rate-limited in earlier attempts, so this run used arXiv HTML pages only for confirmation metadata.",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    force = os.environ.get("HARVEST_FORCE", "").lower() in {"1", "true", "yes"}
    delay_seconds = float(os.environ.get("HARVEST_DELAY_SECONDS", "5"))
    summary: dict[str, Any] = {
        "generated_at": utc_now(),
        "purpose": "Negative-space scan source-anchor metadata harvest",
        "tool_versions": {
            "openalex-pp-cli": tool_version(["openalex-pp-cli", "--version"]),
            "python": sys.version.split()[0],
        },
        "default_delay_seconds": delay_seconds,
        "pdfs_downloaded": False,
        "papers": [],
    }

    log("fallback OpenAlex/arXiv HTML harvest starting")
    log(f"delay_seconds={delay_seconds} force={force}")

    for index, paper in enumerate(PAPERS):
        arxiv_id = paper["arxiv_id"]
        if index:
            time.sleep(delay_seconds)

        openalex_work, openalex_provenance = openalex_cli_lookup(paper, force)
        rest_provenance = None
        if openalex_work is None:
            time.sleep(delay_seconds)
            openalex_work, rest_provenance = openalex_rest_lookup(paper, force)

        time.sleep(delay_seconds)
        arxiv_metadata, arxiv_provenance = arxiv_html_lookup(paper, force)

        raw_outputs = [openalex_provenance["raw_output"], arxiv_provenance["raw_output"]]
        if rest_provenance:
            raw_outputs.insert(1, rest_provenance["raw_output"])

        status = "ok" if openalex_work and arxiv_metadata else "partial"
        summary["papers"].append(
            {
                "arxiv_id": arxiv_id,
                "input_title": paper["title"],
                "arxiv_abs_url": f"https://arxiv.org/abs/{arxiv_id}",
                "openalex_doi_lookup": f"https://doi.org/10.48550/arxiv.{arxiv_id}",
                "status": status,
                "openalex": compact_openalex(openalex_work),
                "arxiv_html_metadata": compact_arxiv(arxiv_metadata),
                "provenance": {
                    "openalex_cli": openalex_provenance,
                    "openalex_rest_fallback": rest_provenance,
                    "arxiv_html": arxiv_provenance,
                },
                "raw_outputs": raw_outputs,
            }
        )
        log(f"paper complete arxiv_id={arxiv_id} status={status}")

    write_json(SUMMARY_JSON, summary)
    write_markdown(summary)
    log(f"wrote summary_json={SUMMARY_JSON.relative_to(SCRIPT_DIR)}")
    log(f"wrote summary_md={SUMMARY_MD.relative_to(SCRIPT_DIR)}")
    log("fallback OpenAlex/arXiv HTML harvest complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
