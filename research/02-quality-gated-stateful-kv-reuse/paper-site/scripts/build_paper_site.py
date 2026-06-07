#!/usr/bin/env python3
"""Build a self-contained HTML research-paper site from paper artifacts."""

from __future__ import annotations

import html
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TRACK = ROOT / "research" / "02-quality-gated-stateful-kv-reuse"
EXPERIMENT = TRACK / "experiments" / "paper-grade-code-mode-kv-capsule-evaluation-2026-06-05"
PRIMARY50 = TRACK / "experiments" / "nonhandmade-code-mode-kv-agent-benchmark-2026-06-05"
ARTIFACTS = TRACK / "paper-artifacts"
FIGURES = ARTIFACTS / "figures"
FIGURE_BUILDER = ARTIFACTS / "scripts" / "build_figures.py"
OUT = TRACK / "paper-site" / "site" / "index.html"
SITE_FIGURES = OUT.parent / "figures"


def build_matplotlib_figures() -> None:
    subprocess.run([sys.executable, str(FIGURE_BUILDER)], cwd=ROOT, check=True)
    SITE_FIGURES.mkdir(parents=True, exist_ok=True)
    for svg in FIGURES.glob("*.svg"):
        shutil.copy2(svg, SITE_FIGURES / svg.name)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


selected = load_json(EXPERIMENT / "selected-cohort-summary.json")
repeated = load_json(EXPERIMENT / "repeated-work-speed-summary.json")


LABELS = {
    "code_mode_full_visible": "Full visible\nPTI",
    "code_mode_native_live_append": "Native live\nappend",
    "code_mode_restored_kv_capsule": "Restored\nKV capsule",
    "code_mode_fresh_tail_only": "Fresh tail\nnegative",
    "code_mode_wrong_capsule_negative": "Wrong capsule\nnegative",
    "direct_full_visible_tools": "Direct visible\ntools",
    "compact_visible_evidence_code_mode": "Compact visible\nevidence",
}

SYSTEM_LABELS = {
    "kv_capsule_code_mode": "KV capsule + PTI",
    "codex_ollama_regular_tools_natural_text_compaction": "Codex/Ollama text compaction",
    "codex_ollama_regular_tools_compaction": "Codex attempted compaction",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def figure_img(name: str, alt: str) -> str:
    svg = SITE_FIGURES / f"{name}.svg"
    if not svg.exists():
        raise FileNotFoundError(f"Missing figure asset: {svg}")
    version = int(svg.stat().st_mtime)
    img = f'<img class="paper-figure-img" src="figures/{esc(svg.name)}?v={version}" alt="{esc(alt)}" loading="lazy" />'
    mobile = SITE_FIGURES / f"{name}-mobile.svg"
    if not mobile.exists():
        return img
    mobile_version = int(mobile.stat().st_mtime)
    return (
        '<picture>'
        f'<source media="(max-width: 760px)" srcset="figures/{esc(mobile.name)}?v={mobile_version}" />'
        f"{img}"
        "</picture>"
    )


build_matplotlib_figures()


def fmt_int(value: float | int) -> str:
    return f"{value:,.0f}"


def fmt_minutes(ms: float) -> str:
    minutes = ms / 60000
    if minutes >= 60:
        return f"{minutes / 60:.2f} h"
    return f"{minutes:.1f} min"


def table(headers: list[str], rows: list[list[object]]) -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "\n".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in rows)
    return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


counts = selected["counts_by_control"]
timing = selected["timing_mean_ms"]
systems = repeated["systems"]
natural = systems["codex_ollama_regular_tools_natural_text_compaction"]
kv = systems["kv_capsule_code_mode"]
attempted = systems["codex_ollama_regular_tools_compaction"]

positive_controls = [
    "code_mode_full_visible",
    "code_mode_native_live_append",
    "code_mode_restored_kv_capsule",
    "direct_full_visible_tools",
    "compact_visible_evidence_code_mode",
]

pass_rows = [
    (LABELS[k], counts[k]["gate_passed"], f'{counts[k]["gate_passed"]}/100')
    for k in positive_controls
]
positive_rate_rows = [
    (LABELS[k], counts[k]["gate_passed"], f'{counts[k]["gate_passed"]}%')
    for k in positive_controls
]
negative_leak_rows = [
    (
        LABELS[k],
        counts[k]["records"] - counts[k]["gate_passed"],
        f'{counts[k]["records"] - counts[k]["gate_passed"]} leaks',
    )
    for k in ["code_mode_fresh_tail_only", "code_mode_wrong_capsule_negative"]
]
timing_rows = [(LABELS[k], timing[k], f"{timing[k]:,.1f} ms") for k in positive_controls]
runtime_rows = [
    ("KV capsule + PTI", kv["cumulative_wall_ms"], fmt_minutes(kv["cumulative_wall_ms"])),
    ("Codex text compaction", natural["cumulative_wall_ms"], fmt_minutes(natural["cumulative_wall_ms"])),
    ("Codex attempted", attempted["cumulative_wall_ms"], fmt_minutes(attempted["cumulative_wall_ms"])),
]
token_rows = [
    ("KV capsule + PTI", kv["visible_input_tokens"], fmt_int(kv["visible_input_tokens"])),
    ("Codex text compaction", natural["visible_input_tokens"], fmt_int(natural["visible_input_tokens"])),
    ("Codex attempted", attempted["visible_input_tokens"], fmt_int(attempted["visible_input_tokens"])),
]
output_rows = [
    ("KV capsule + PTI", kv["output_tokens"], fmt_int(kv["output_tokens"])),
    ("Codex text compaction", natural["output_tokens"], fmt_int(natural["output_tokens"])),
    ("Codex attempted", attempted["output_tokens"], fmt_int(attempted["output_tokens"])),
]
failure_rows = [
    ("java", 14, 17),
    ("javascript", 0, 1),
    ("multiple", 21, 25),
    ("parallel", 13, 14),
    ("parallel_multiple", 13, 17),
    ("simple", 25, 26),
]
failure_chart_rows = [(name, passed, f"{passed}/{total}") for name, passed, total in failure_rows]

html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Quality-Gated Hidden-State Reuse for Local Tool-Using Agents</title>
  <style>
    :root {{
      --paper: #ffffff;
      --ink: #171717;
      --muted: #555555;
      --line: #bdbdbd;
      --soft-line: #e5e5e5;
      --panel: #fafafa;
      --code: #f2f2f2;
      --primary: #1f4e79;
      --mid: #808080;
      --inverse: #b23b30;
      --inverse-soft: #e2aaa4;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
      line-height: 1.58;
    }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 5;
      border-bottom: 1px solid var(--line);
      background: rgba(247, 243, 235, 0.94);
      backdrop-filter: blur(10px);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .topbar-inner {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 10px 24px;
      display: flex;
      gap: 18px;
      align-items: center;
      justify-content: space-between;
    }}
    .brand {{ font-weight: 720; font-size: 14px; letter-spacing: 0; }}
    nav {{ display: flex; gap: 14px; flex-wrap: wrap; justify-content: flex-end; }}
    nav a {{ color: var(--muted); text-decoration: none; font-size: 13px; }}
    nav a:hover {{ color: var(--ink); }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 46px 24px 90px;
    }}
    .paper-header {{
      max-width: 900px;
      margin: 0 auto 42px;
      text-align: center;
      border-bottom: 1.5px solid var(--ink);
      padding-bottom: 28px;
    }}
    .eyebrow {{
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      text-transform: uppercase;
      font-size: 12px;
      color: var(--muted);
      letter-spacing: .08em;
      margin-bottom: 16px;
    }}
    h1 {{
      font-size: clamp(34px, 5.2vw, 54px);
      line-height: 1.06;
      margin: 0 0 18px;
      font-weight: 760;
      letter-spacing: 0;
    }}
    .subtitle {{
      max-width: 760px;
      margin: 0 auto;
      font-size: 19px;
      color: #303636;
    }}
    .meta {{
      margin-top: 22px;
      color: var(--muted);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 13px;
    }}
    section {{
      max-width: 900px;
      margin: 0 auto 48px;
      scroll-margin-top: 132px;
    }}
    h2 {{
      font-size: 27px;
      line-height: 1.18;
      margin: 0 0 16px;
      border-top: 1px solid var(--line);
      padding-top: 28px;
    }}
    h3 {{
      font-size: 19px;
      margin: 28px 0 10px;
      line-height: 1.25;
    }}
    p {{ margin: 0 0 14px; }}
    .abstract {{
      font-size: 17px;
      border-top: 1px solid var(--ink);
      border-bottom: 1px solid var(--ink);
      padding: 18px 0;
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 28px 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .kpi {{
      border: 1px solid var(--soft-line);
      background: var(--panel);
      padding: 14px 16px;
    }}
    .kpi b {{ display: block; font-size: 26px; line-height: 1.05; margin-bottom: 6px; }}
    .kpi span {{ color: var(--muted); font-size: 12px; line-height: 1.3; display: block; }}
    .figure {{
      margin: 28px 0 38px;
      padding: 0;
      border-top: 1px solid var(--ink);
      border-bottom: 1px solid var(--line);
      background: #fff;
      overflow-x: auto;
    }}
    .figure-head {{
      padding: 10px 0 8px;
      border-bottom: 1px solid var(--soft-line);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 13px;
      line-height: 1.45;
    }}
    .figure-head b {{ color: var(--ink); }}
    .figure-body {{ padding: 12px 0 6px; }}
    .figure-note {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 12px;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .caption {{
      margin: 8px 0 10px;
      color: var(--muted);
      font-size: 13px;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .chart, .paper-chart {{ width: 100%; height: auto; display: block; }}
    .paper-figure-img {{ width: 100%; height: auto; display: block; }}
    .compact-chart {{ min-width: 460px; max-width: 560px; margin: 0 auto; }}
    .small-multiples {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 22px;
      align-items: start;
    }}
    .small-multiples .paper-chart {{ min-width: 0; }}
    .chart-title, .chart-panel-title, .value, .ylabel, .legend, .donut-label, .tick, .tick-left, .axis-label {{
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    .chart-title {{ font-size: 18px; font-weight: 720; fill: var(--ink); }}
    .chart-panel-title {{ font-size: 13px; font-weight: 700; fill: var(--ink); }}
    .ylabel {{ font-size: 12px; text-anchor: end; fill: #222; }}
    .value {{ font-size: 12px; fill: #222; }}
    .axis {{ stroke: #333; stroke-width: 1; }}
    .gridline {{ stroke: #e6e6e6; stroke-width: 1; }}
    .tick {{ font-size: 11px; fill: #555; text-anchor: middle; }}
    .tick-left {{ font-size: 11px; fill: #555; text-anchor: end; }}
    .axis-label {{ font-size: 11px; fill: #555; text-anchor: middle; }}
    .rotated {{ transform: rotate(-90deg); transform-origin: 14px center; }}
    .bar {{ opacity: .94; }}
    .bar-fill {{ fill: var(--mid); }}
    .bar-fill.primary {{ fill: var(--primary); }}
    .bar-fill.mid {{ fill: var(--mid); }}
    .bar-fill.inverse {{ fill: var(--inverse); }}
    .muted-fill {{ fill: var(--inverse-soft); }}
    .slice {{ stroke: var(--paper); stroke-width: 2; }}
    .donut-total {{ font: 720 30px ui-sans-serif, system-ui; text-anchor: middle; fill: var(--ink); }}
    .donut-label {{ font-size: 12px; text-anchor: middle; fill: var(--muted); }}
    .legend {{ font-size: 13px; fill: #303636; }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 18px 0 24px;
      background: #fff;
      border: 1px solid var(--line);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: #f3f3f3; font-weight: 720; }}
    tr:last-child td {{ border-bottom: 0; }}
    code {{
      background: var(--code);
      border-radius: 4px;
      padding: 1px 4px;
      font-size: .92em;
    }}
    .callout {{
      border-left: 3px solid var(--primary);
      background: var(--panel);
      padding: 15px 18px;
      margin: 20px 0;
      border-radius: 0 6px 6px 0;
    }}
    .warning {{ border-left-color: var(--inverse); }}
    .provenance {{
      border: 1px solid var(--soft-line);
      background: var(--panel);
      padding: 14px 16px;
      margin: 20px 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 13px;
      color: var(--muted);
    }}
    .provenance b {{ color: var(--ink); }}
    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      align-items: start;
    }}
    .source-list {{
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 13px;
      color: var(--muted);
    }}
    .source-list li {{ margin-bottom: 8px; }}
    footer {{
      max-width: 900px;
      margin: 60px auto 0;
      padding-top: 24px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 13px;
    }}
    @media (max-width: 760px) {{
      .topbar-inner {{ align-items: flex-start; flex-direction: column; }}
      nav {{ justify-content: flex-start; }}
      main {{ padding: 30px 16px 70px; }}
      .paper-header {{ text-align: left; }}
      .kpi-grid {{ grid-template-columns: 1fr 1fr; }}
      .two-col {{ grid-template-columns: 1fr; }}
      .small-multiples {{ grid-template-columns: 1fr; }}
      .chart, .paper-chart {{ min-width: 0; }}
      .paper-figure-img {{ min-width: 0; }}
      .small-multiples .paper-chart {{ min-width: 560px; }}
    }}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-inner">
      <div class="brand">KV Capsule Research Paper Site</div>
      <nav>
        <a href="#abstract">Abstract</a>
        <a href="#method">Method</a>
        <a href="#results">Results</a>
        <a href="#figures">Figures</a>
        <a href="#limitations">Limitations</a>
        <a href="#sources">Sources</a>
      </nav>
    </div>
  </div>
  <main>
    <header class="paper-header">
      <div class="eyebrow">Research draft visualization · Generated from repo artifacts</div>
      <h1>Quality-Gated Hidden-State Reuse for Local Tool-Using Agents</h1>
      <p class="subtitle">A KV-capsule harness lets the same local model reuse stable tool/context knowledge through restored hidden state instead of repeatedly carrying or compacting that context as text.</p>
      <div class="meta">Gemma 4 · BFCL-derived selected cohort · Programmatic tool interface · Built from paper artifacts on 2026-06-07</div>
    </header>

    <section id="abstract">
      <h2>Abstract</h2>
      <div class="abstract">
        Local agent runtimes often repeatedly carry stable context as text: tool schemas, runtime rules, environment instructions, and task protocols. Text compaction summarizes this context but changes its representation. We study an alternative: evaluate a stable prefix once, persist the model's KV/sequence state as a capsule, and restore that hidden state before appending new task tails. We pair this with a compact programmatic tool interface and evaluate under a control ladder that compares full visible prompts, native live append, restored KV, fresh-tail negatives, wrong-capsule negatives, compact visible evidence, and direct visible tools.
      </div>
      <div class="kpi-grid">
        <div class="kpi"><b>100/100</b><span>Restored KV pass rate on the selected cohort.</span></div>
        <div class="kpi"><b>0</b><span>Fresh-tail and wrong-capsule leaks on the selected cohort.</span></div>
        <div class="kpi"><b>89</b><span>Audited Codex session compaction events in the natural baseline.</span></div>
        <div class="kpi"><b>3,900</b><span>KV repeated-work visible input tokens, versus 245,774,883 reported by Codex.</span></div>
      </div>
    </section>

    <section id="claim">
      <h2>Main Claim</h2>
      <p><strong>Paper-safe claim:</strong> for repeated stable-context tool-use workloads, a KV-capsule harness can preserve stable tool/context knowledge as restored hidden state, letting the same local model answer fresh task tails without repeatedly carrying or compacting the full stable context as text.</p>
      <div class="callout">
        <p><strong>What the current data backs:</strong> on the selected 100-case repeated-work stream, the KV-capsule + programmatic tool-interface harness achieved <code>100/100</code>, while the Codex/Ollama regular-tool natural text-compaction harness achieved <code>86/100</code> with <code>89</code> audited compaction events.</p>
      </div>
      <div class="callout warning">
        <p><strong>What this does not claim:</strong> it is not a prompt-identical KV-vs-compaction mechanism comparison, not an official BFCL leaderboard result, and not a proof that restored KV is inherently faster in every setting.</p>
      </div>
      <div class="callout warning">
        <p><strong>Current BFCL candidate boundary:</strong> the detached full non-live BFCL run started on 2026-06-07 is not included on this page yet. These figures use only completed, committed experiment artifacts. The official candidate run remains prediction generation until its exported files are scored by the official BFCL evaluator.</p>
      </div>
    </section>

    <section id="method">
      <h2>Method</h2>
      <h3>Stable Prefix, Capsule, Tail</h3>
      <p>The system builds a stable prefix containing the tool/function catalog, output contract, interface rules, and stable task protocol. The local model evaluates that prefix once. The harness saves the llama.cpp sequence/KV state as a capsule. Later it restores the capsule and appends only the volatile task tail.</p>
      <h3>Programmatic Tool Interface</h3>
      <p>Internal files still use the historical name <code>code_mode</code>. Paper-facing language uses <strong>programmatic tool interface</strong>: a compact structured contract that lets the model emit tool/function-call plans without repeatedly seeing the full visible tool schema. This is related to programmatic tool calling but should not be oversold as full arbitrary PTC.</p>
      <h3>Control Ladder</h3>
      {table(["Control", "Purpose"], [
          ["Full visible PTI", "Positive control with stable context visible."],
          ["Native live append", "Reads prefix, then appends task tail without save/restore."],
          ["Restored KV capsule", "Restores saved hidden state, then appends task tail."],
          ["Fresh tail negative", "Tests whether the tail alone leaks the answer."],
          ["Wrong capsule negative", "Tests whether irrelevant hidden state can solve the task."],
          ["Direct visible tools", "Regular visible tool-schema baseline."],
          ["Compact visible evidence", "Visible summary baseline, separate from hidden-state reuse."],
      ])}
      <h3>Figure Construction</h3>
      <p>Figures follow research-paper conventions: numbered captions state the claim and boundary, axes include units or denominators, log scales are marked explicitly, colour is limited to a colour-blind-safe blue/vermillion/gray palette, and decorative chart elements are omitted. Error bars are not shown because the current artifact is a deterministic run summary rather than a replicated estimate with variance; this is stated at the relevant figures instead of implying uncertainty we did not measure.</p>
      <div class="provenance">
        <p><b>Reproducible figure pipeline:</b> Matplotlib figures are generated by <code>paper-artifacts/scripts/build_figures.py</code> from committed summaries, written as paper-ready <code>.pdf</code> and web <code>.svg</code> outputs under <code>paper-artifacts/figures/</code>, and mirrored into the static site. The generated <code>figure-manifest.json</code> records each figure source and claim boundary.</p>
      </div>
    </section>

    <section id="results">
      <h2>Results</h2>
      <h3>Selected 100-Case Cohort</h3>
      <p>On <code>bfcl-paper-selected-cohort-v1</code>, full visible, native live append, and restored KV all passed <code>100/100</code>. Fresh-tail and wrong-capsule controls had zero leaks. Direct visible tools passed <code>91/100</code>, and compact visible evidence passed <code>19/100</code>.</p>
      {table(["Lane", "Pass / gate result", "Mean total latency"], [
          ["Full visible PTI", "100/100", "6,766.7 ms"],
          ["Native live append", "100/100", "6,782.7 ms"],
          ["Restored KV capsule", "100/100", "8,513.8 ms"],
          ["Fresh tail negative", "0 leaks; negative gate closed", "9,738.9 ms"],
          ["Wrong capsule negative", "0 leaks; negative gate closed", "7,571.6 ms"],
          ["Direct visible tools", "91/100", "8,179.8 ms"],
          ["Compact visible evidence", "19/100", "9,434.8 ms"],
      ])}

      <h3>Repeated-Work Harness Comparison</h3>
      <p>On the repeated-work stream, the KV-capsule runtime had the best pass rate, smallest visible input burden, and lowest cumulative wall time among the reported system lanes. The Codex/Ollama natural baseline did compact; the compaction evidence lives in Codex session JSONL, not in per-task stdout.</p>
      {table(["System", "Pass", "Cumulative wall", "Visible input telemetry", "Compactions"], [
          ["KV capsule + PTI", "100/100", "853,499 ms", "3,900", "0"],
          ["Codex/Ollama natural text compaction", "86/100", "11,813,816 ms", "245,774,883 reported cumulative", "89"],
          ["Codex attempted compaction, no events", "87/100", "11,521,048 ms", "243,088,507 reported", "0"],
      ])}
    </section>

    <section id="figures">
      <h2>Figures</h2>
      <div class="figure">
        <div class="figure-head"><b>Figure 1.</b> Control-ladder outcome on the selected 100-case cohort. Positive lanes are shown as pass rate; negative controls are shown separately as leak count.</div>
        <div class="figure-body">
          {figure_img("figure-01-control-ladder", "Matplotlib chart showing selected-cohort positive lane pass rates and negative-control leak counts.")}
        </div>
        <p class="caption">Source: <code>selected-cohort-summary.json</code>. The restored-KV lane matches both full-visible and native-live controls on all selected cases; fresh-tail and wrong-capsule controls produce zero leaks. This supports prefix dependence and restored-state preservation, not a speed claim.</p>
      </div>
      <div class="figure">
        <div class="figure-head"><b>Figure 2.</b> Selected-cohort latency boundary. Lower is better; this experiment supports semantic preservation, not a speedup claim for restored KV.</div>
        <div class="figure-body">
          {figure_img("figure-02-latency", "Matplotlib horizontal bar chart of selected-cohort mean total latency by control lane.")}
        </div>
        <p class="figure-note">No error bars are drawn: this figure reports mean latency from the committed run summary, not repeated-run confidence intervals.</p>
        <p class="caption">Source: <code>selected-cohort-summary.json</code>. Restored KV is correct but slower than full-visible and native-live append in this mechanism run.</p>
      </div>
      <div class="figure">
        <div class="figure-head"><b>Figure 3.</b> Natural Codex/Ollama failure distribution by BFCL category. Pass and fail proportions are shown on a common 0-100% scale, with counts printed at right.</div>
        <div class="figure-body">
          {figure_img("figure-03-codex-failures", "Matplotlib stacked horizontal bar chart showing Codex natural baseline pass and fail proportions by BFCL category.")}
        </div>
        <p class="caption">Source: <code>repeated-work-speed-findings.md</code>. Most Codex failures were parseable but incorrect calls; one failure parsed zero calls. This is diagnostic, not causal evidence that compaction summaries caused the failures.</p>
      </div>
      <div class="figure">
        <div class="figure-head"><b>Figure 4.</b> Repeated-work visible input burden. Log scale is used because the runtime gap is several orders of magnitude.</div>
        <div class="figure-body">
          {figure_img("figure-04-visible-input-tokens", "Matplotlib log-scale horizontal bar chart of reported visible input tokens.")}
        </div>
        <p class="caption">Source: <code>repeated-work-speed-summary.json</code>. Codex/Ollama telemetry is route-reported cumulative burden, not clean per-task token accounting.</p>
      </div>
      <div class="figure">
        <div class="figure-head"><b>Figure 5.</b> Repeated-work cumulative wall time. Lower is better.</div>
        <div class="figure-body">
          {figure_img("figure-05-wall-time", "Matplotlib log-scale horizontal bar chart of repeated-work cumulative wall time.")}
        </div>
        <p class="caption">Source: <code>repeated-work-speed-summary.json</code>. KV completed the stream in 14.2 minutes versus 3.28 hours for the natural Codex/Ollama text-compaction lane.</p>
      </div>
      <div class="figure">
        <div class="figure-head"><b>Figure 6.</b> Repeated-work output-token burden. Lower is better for harness overhead, assuming comparable task success.</div>
        <div class="figure-body">
          {figure_img("figure-06-output-tokens", "Matplotlib log-scale horizontal bar chart of repeated-work output-token burden.")}
        </div>
        <p class="caption">Source: <code>repeated-work-speed-summary.json</code>. Output-token telemetry shows the practical burden difference between the compact KV harness and text-threaded Codex/Ollama routes.</p>
      </div>
    </section>

    <section id="limitations">
      <h2>Limitations</h2>
      <ul>
        <li>The Codex/Ollama comparison is a practical runtime comparison, not a prompt-identical mechanism comparison.</li>
        <li>The selected cohort is quality-gated and BFCL-derived; it is not an official BFCL leaderboard submission.</li>
        <li>The programmatic tool interface is not full arbitrary programmatic tool calling.</li>
        <li>Codex visible-input telemetry is route-reported cumulative burden, not clean per-task accounting.</li>
        <li>The selected-cohort mechanism run does not show restored KV is faster than native append.</li>
        <li>The Codex compaction summaries still need a deeper contamination/help/harm audit.</li>
      </ul>
    </section>

    <section id="sources">
      <h2>Source Grounding</h2>
      <p>Every metric in this site is sourced from the paper artifacts and local experiment summaries committed in the repo.</p>
      <ul class="source-list">
        <li><code>research/02-quality-gated-stateful-kv-reuse/paper-artifacts/paper-data-ledger.md</code></li>
        <li><code>research/02-quality-gated-stateful-kv-reuse/paper-artifacts/paper-claims-ledger.md</code></li>
        <li><code>research/02-quality-gated-stateful-kv-reuse/paper-artifacts/paper-results-tables.md</code></li>
        <li><code>research/02-quality-gated-stateful-kv-reuse/paper-artifacts/paper-outline.md</code></li>
        <li><code>research/02-quality-gated-stateful-kv-reuse/paper-artifacts/scripts/build_figures.py</code></li>
        <li><code>research/02-quality-gated-stateful-kv-reuse/paper-artifacts/figures/figure-manifest.json</code></li>
        <li><code>research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/selected-cohort-summary.json</code></li>
        <li><code>research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/repeated-work-speed-summary.json</code></li>
        <li><code>research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/repeated-work-speed-findings.md</code></li>
      </ul>
    </section>

    <footer>
      Built as a static research-paper visualization from repo artifacts. Commit this generated HTML alongside the source generator whenever data changes.
    </footer>
  </main>
</body>
</html>
"""


OUT.write_text(html_doc)
print(OUT)
