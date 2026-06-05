#!/usr/bin/env python3
"""Local research cockpit server for the AI research lab."""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import re
import socketserver
import sys
import time
from dataclasses import dataclass
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "dist"
REPO_ROOT = APP_DIR.parents[1]

TRACK_NAME_RE = re.compile(r"^\d{2}-.+")
CHECKBOX_RE = re.compile(r"^\s*-\s+\[(?P<mark>[ xX])\]")
JSON_PREVIEW_LIMIT = 750_000


@dataclass
class ParseIssue:
    path: str
    message: str


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def safe_repo_file(raw_path: str) -> Path:
    raw_path = unquote(raw_path).lstrip("/")
    candidate = (REPO_ROOT / raw_path).resolve()
    if REPO_ROOT.resolve() not in candidate.parents and candidate != REPO_ROOT.resolve():
        raise ValueError("path is outside the repository")
    if not candidate.is_file():
        raise FileNotFoundError(raw_path)
    return candidate


def read_text(path: Path, limit: int = JSON_PREVIEW_LIMIT) -> str:
    data = path.read_bytes()[:limit]
    return data.decode("utf-8", errors="replace")


def read_json(path: Path, issues: list[ParseIssue] | None = None) -> Any | None:
    try:
        return json.loads(read_text(path))
    except Exception as exc:  # noqa: BLE001 - parser should keep the page alive.
        if issues is not None:
            issues.append(ParseIssue(repo_path(path), str(exc)))
        return None


def first_heading_or_paragraph(markdown: str) -> str:
    lines = [line.strip() for line in markdown.splitlines()]
    for line in lines:
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    for line in lines:
        if line and not line.startswith("#") and not line.startswith("|") and not line.startswith("-"):
            return line[:260]
    return ""


def task_counts(tasks_path: Path) -> dict[str, int | str]:
    if not tasks_path.exists():
        return {"completed": 0, "total": 0, "status": "missing"}
    total = 0
    completed = 0
    for line in read_text(tasks_path).splitlines():
        match = CHECKBOX_RE.match(line)
        if not match:
            continue
        total += 1
        completed += 1 if match.group("mark").lower() == "x" else 0
    status = "complete" if total and completed == total else "in-progress"
    if total == 0:
        status = "unknown"
    return {"completed": completed, "total": total, "status": status}


def file_mtime(path: Path) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(path.stat().st_mtime))


def has_any(path: Path, names: list[str]) -> list[str]:
    return [name for name in names if (path / name).exists()]


def index_tracks() -> list[dict[str, Any]]:
    tracks: list[dict[str, Any]] = []
    research_dir = REPO_ROOT / "research"
    if not research_dir.exists():
        return tracks
    for track_dir in sorted(p for p in research_dir.iterdir() if p.is_dir() and TRACK_NAME_RE.match(p.name)):
        readme = track_dir / "README.md"
        title = track_dir.name
        summary = ""
        if readme.exists():
            text = read_text(readme)
            title = first_heading_or_paragraph(text) or title
            summary = first_heading_or_paragraph("\n".join(text.splitlines()[1:])) or ""
        experiments_dir = track_dir / "experiments"
        evidence_dir = track_dir / "evidence"
        tracks.append(
            {
                "id": track_dir.name,
                "title": title,
                "summary": summary,
                "path": repo_path(track_dir),
                "readmePath": repo_path(readme) if readme.exists() else None,
                "noteCount": len(list(track_dir.glob("*.md"))),
                "experimentCount": len([p for p in experiments_dir.iterdir() if p.is_dir()]) if experiments_dir.exists() else 0,
                "evidenceCount": len([p for p in evidence_dir.rglob("*") if p.is_file()]) if evidence_dir.exists() else 0,
                "lastModified": file_mtime(max(track_dir.rglob("*"), key=lambda p: p.stat().st_mtime)) if any(track_dir.rglob("*")) else file_mtime(track_dir),
            }
        )
    return tracks


def extract_controls(summary: dict[str, Any]) -> list[dict[str, Any]]:
    controls: list[dict[str, Any]] = []

    def add_control(name: str, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        record_count = payload.get("case_count") or payload.get("record_count") or payload.get("numeric_score_count")
        pass_rate = payload.get("pass_rate")
        if pass_rate is None and payload.get("gate_pass_count") is not None and payload.get("record_count"):
            try:
                pass_rate = payload["gate_pass_count"] / payload["record_count"]
            except Exception:
                pass_rate = None
        controls.append(
            {
                "name": name,
                "passRate": pass_rate,
                "meanScore": payload.get("mean_score"),
                "caseCount": record_count,
                "gatePassCount": payload.get("gate_pass_count"),
                "failureClasses": payload.get("failure_classes") or {},
            }
        )

    for key in ("controls", "by_control", "summary"):
        section = summary.get(key)
        if isinstance(section, dict):
            for name, payload in section.items():
                add_control(str(name), payload)
    return controls


def flatten_failure_classes(payload: Any) -> dict[str, int]:
    totals: dict[str, int] = {}

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if value and all(isinstance(v, (int, float)) for v in value.values()):
                for key, count in value.items():
                    totals[str(key)] = totals.get(str(key), 0) + int(count)
                return
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(payload)
    return totals


def experiment_warnings(exp_dir: Path, readme_text: str) -> list[str]:
    warnings: list[str] = []
    required_files = ["README.md", "summary.json", "commands.md", "artifact-manifest.json"]
    for name in required_files:
        if not (exp_dir / name).exists():
            warnings.append(f"missing {name}")
    discipline_terms = ["hypothesis", "baseline", "control", "metric", "stop rule"]
    lower = readme_text.lower()
    missing_terms = [term for term in discipline_terms if term not in lower]
    if missing_terms:
        warnings.append("README may be missing: " + ", ".join(missing_terms))
    return warnings


def index_experiments(issues: list[ParseIssue]) -> list[dict[str, Any]]:
    experiments: list[dict[str, Any]] = []
    for exp_dir in sorted((REPO_ROOT / "research").glob("*/experiments/*")):
        if not exp_dir.is_dir():
            continue
        readme = exp_dir / "README.md"
        readme_text = read_text(readme) if readme.exists() else ""
        summary = read_json(exp_dir / "summary.json", issues) if (exp_dir / "summary.json").exists() else {}
        case_metrics = read_json(exp_dir / "case-metrics.json", issues) if (exp_dir / "case-metrics.json").exists() else {}
        failure_payload = read_json(exp_dir / "failure-classifications.json", issues) if (exp_dir / "failure-classifications.json").exists() else {}
        model_info = read_json(exp_dir / "model-info.json", issues) if (exp_dir / "model-info.json").exists() else {}
        manifest = read_json(exp_dir / "artifact-manifest.json", issues) if (exp_dir / "artifact-manifest.json").exists() else {}

        summary = summary if isinstance(summary, dict) else {}
        case_metrics = case_metrics if isinstance(case_metrics, dict) else {}
        model_info = model_info if isinstance(model_info, dict) else {}
        manifest = manifest if isinstance(manifest, dict) else {}
        controls = extract_controls(summary)
        cases = case_metrics.get("cases") if isinstance(case_metrics.get("cases"), list) else []
        case_count = (
            summary.get("executed_case_count")
            or summary.get("design_planned_case_count")
            or case_metrics.get("case_count")
            or summary.get("metadata", {}).get("case_count")
            or len(cases)
        )
        dataset = summary.get("dataset") or summary.get("metadata", {}).get("dataset") or manifest.get("dataset")
        model = summary.get("model") or model_info.get("model") or summary.get("metadata", {}).get("model")
        experiments.append(
            {
                "id": exp_dir.name,
                "track": exp_dir.parents[1].name,
                "title": first_heading_or_paragraph(readme_text) or exp_dir.name,
                "path": repo_path(exp_dir),
                "readmePath": repo_path(readme) if readme.exists() else None,
                "generatedAt": summary.get("generated_at") or summary.get("metadata", {}).get("generated_at"),
                "decision": summary.get("decision") or summary.get("headline") or summary.get("mechanism_interpretation"),
                "dataset": dataset,
                "model": model,
                "caseCount": case_count,
                "controls": controls,
                "failureClasses": flatten_failure_classes(failure_payload) or flatten_failure_classes(summary.get("by_control")),
                "artifactFiles": has_any(
                    exp_dir,
                    ["summary.json", "case-metrics.json", "failure-classifications.json", "artifact-manifest.json", "commands.md", "model-info.json"],
                ),
                "warnings": experiment_warnings(exp_dir, readme_text),
                "lastModified": file_mtime(max(exp_dir.rglob("*"), key=lambda p: p.stat().st_mtime)) if any(exp_dir.rglob("*")) else file_mtime(exp_dir),
            }
        )
    return experiments


def index_papers(issues: list[ParseIssue]) -> list[dict[str, Any]]:
    papers: list[dict[str, Any]] = []
    for summary_path in sorted((REPO_ROOT / "research").glob("*/evidence/**/negative-space-harvest-summary.json")):
        payload = read_json(summary_path, issues)
        if not isinstance(payload, dict):
            continue
        for paper in payload.get("papers", []):
            if not isinstance(paper, dict):
                continue
            openalex = paper.get("openalex") or {}
            html_meta = paper.get("arxiv_html_metadata") or {}
            year = openalex.get("publication_year")
            if year is None:
                date = html_meta.get("publication_date") or ""
                year = int(date[:4]) if str(date)[:4].isdigit() else None
            papers.append(
                {
                    "id": paper.get("arxiv_id") or openalex.get("id") or paper.get("openalex_doi_lookup"),
                    "title": openalex.get("title") or html_meta.get("title") or paper.get("title"),
                    "arxivId": paper.get("arxiv_id"),
                    "arxivUrl": paper.get("arxiv_abs_url"),
                    "openAlexId": openalex.get("id"),
                    "doi": openalex.get("doi") or paper.get("openalex_doi_lookup"),
                    "year": year,
                    "oaStatus": (openalex.get("open_access") or {}).get("oa_status"),
                    "status": paper.get("status"),
                    "sourcePath": repo_path(summary_path),
                    "rawOutputCount": len(paper.get("raw_outputs") or []),
                    "pdfsDownloaded": bool(payload.get("pdfs_downloaded")),
                }
            )
    return papers


def index_openspec() -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    changes_dir = REPO_ROOT / "openspec" / "changes"
    if not changes_dir.exists():
        return changes
    for change_dir in sorted(p for p in changes_dir.iterdir() if p.is_dir() and p.name != "archive"):
        counts = task_counts(change_dir / "tasks.md")
        artifacts = {
            "proposal": (change_dir / "proposal.md").exists(),
            "design": (change_dir / "design.md").exists(),
            "tasks": (change_dir / "tasks.md").exists(),
            "specs": (change_dir / "specs").exists(),
        }
        changes.append(
            {
                "name": change_dir.name,
                "path": repo_path(change_dir),
                "completedTasks": counts["completed"],
                "totalTasks": counts["total"],
                "status": counts["status"],
                "artifacts": artifacts,
                "lastModified": file_mtime(max(change_dir.rglob("*"), key=lambda p: p.stat().st_mtime)) if any(change_dir.rglob("*")) else file_mtime(change_dir),
            }
        )
    return changes


def index_benchmarks(issues: list[ParseIssue]) -> list[dict[str, Any]]:
    benchmark_paths = []
    track01 = REPO_ROOT / "research" / "01-ssd-native-inference-current" / "benchmarks"
    for glob in [
        "results/*.json",
        "llama-cpp-results/*.json",
        "flashcache-results/*.json",
        "correctness-eval-results/*scores.json",
    ]:
        benchmark_paths.extend(track01.glob(glob))

    records: list[dict[str, Any]] = []
    for path in sorted(set(benchmark_paths)):
        payload = read_json(path, issues)
        if not isinstance(payload, dict):
            continue
        controls = []
        if isinstance(payload.get("summary"), dict):
            controls = extract_controls(payload)
        strategy_summaries = []
        for strategy in payload.get("strategies", []) if isinstance(payload.get("strategies"), list) else []:
            if not isinstance(strategy, dict):
                continue
            strategy_summaries.append(
                {
                    "name": strategy.get("name"),
                    "scenarioCount": len(strategy.get("scenarios") or []),
                    "summary": strategy.get("summary") or {},
                }
            )
        records.append(
            {
                "id": path.stem,
                "path": repo_path(path),
                "kind": "correctness" if "correctness-eval-results" in repo_path(path) else "benchmark",
                "model": (payload.get("metadata") or {}).get("model"),
                "fixture": (payload.get("metadata") or {}).get("fixture_path"),
                "startedAt": (payload.get("metadata") or {}).get("started_at") or (payload.get("metadata") or {}).get("generated_at"),
                "controls": controls,
                "strategies": strategy_summaries,
                "comparison": payload.get("comparison") or {},
            }
        )
    return records


def build_graph(tracks: list[dict[str, Any]], experiments: list[dict[str, Any]], papers: list[dict[str, Any]]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for track in tracks:
        nodes.append({"id": track["id"], "label": track["id"].split("-", 1)[-1], "type": "track", "path": track["path"]})
    for exp in experiments:
        nodes.append({"id": exp["id"], "label": exp["id"], "type": "experiment", "path": exp["path"]})
        edges.append({"source": exp["track"], "target": exp["id"], "type": "contains"})
    for paper in papers[:80]:
        node_id = "paper:" + str(paper["id"])
        nodes.append({"id": node_id, "label": paper.get("arxivId") or "paper", "type": "paper", "path": paper["sourcePath"]})
        edges.append({"source": "04-negative-space-ideas", "target": node_id, "type": "evidence"})
    return {"nodes": nodes, "edges": edges}


def build_overview() -> dict[str, Any]:
    issues: list[ParseIssue] = []
    tracks = index_tracks()
    experiments = index_experiments(issues)
    papers = index_papers(issues)
    changes = index_openspec()
    benchmarks = index_benchmarks(issues)
    active_changes = [change for change in changes if change["status"] != "complete"]
    return {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repoRoot": str(REPO_ROOT),
        "metrics": {
            "tracks": len(tracks),
            "experiments": len(experiments),
            "papers": len(papers),
            "openSpecChanges": len(changes),
            "activeOpenSpecChanges": len(active_changes),
            "benchmarks": len(benchmarks),
            "warnings": sum(len(exp.get("warnings") or []) for exp in experiments) + len(issues),
        },
        "tracks": tracks,
        "experiments": experiments,
        "papers": papers,
        "openSpecChanges": changes,
        "benchmarks": benchmarks,
        "graph": build_graph(tracks, experiments, papers),
        "issues": [{"path": issue.path, "message": issue.message} for issue in issues],
    }


class CockpitHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        sys.stderr.write("research-cockpit: " + format % args + "\n")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/overview":
            self.send_json(build_overview())
            return
        if parsed.path == "/api/file":
            self.send_file_preview(parsed.query)
            return
        if not (STATIC_DIR / "index.html").exists():
            self.send_build_required()
            return
        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_build_required(self) -> None:
        body = (
            "Research Cockpit frontend has not been built yet.\n\n"
            "Run:\n"
            "  cd apps/research-cockpit\n"
            "  npm install\n"
            "  npm run build\n\n"
            "Then restart this server."
        ).encode("utf-8")
        self.send_response(HTTPStatus.SERVICE_UNAVAILABLE)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file_preview(self, query: str) -> None:
        params = parse_qs(query)
        raw_path = (params.get("path") or [""])[0]
        try:
            path = safe_repo_file(raw_path)
            text = read_text(path, 120_000)
        except Exception as exc:  # noqa: BLE001
            self.send_json({"error": str(exc), "path": raw_path}, HTTPStatus.BAD_REQUEST)
            return
        self.send_json(
            {
                "path": repo_path(path),
                "mime": mimetypes.guess_type(path.name)[0] or "text/plain",
                "text": text,
                "escapedHtml": html.escape(text),
            }
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the AI research lab cockpit.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    os.chdir(REPO_ROOT)
    with socketserver.ThreadingTCPServer((args.host, args.port), CockpitHandler) as httpd:
        httpd.allow_reuse_address = True
        url = f"http://{args.host}:{args.port}"
        print(f"Research Cockpit running at {url}")
        print("Open that URL in the Codex in-app browser.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nResearch Cockpit stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
