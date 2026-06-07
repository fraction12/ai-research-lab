#!/usr/bin/env python3
"""Build a self-contained HTML research-paper site from paper artifacts."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TRACK = ROOT / "research" / "02-quality-gated-stateful-kv-reuse"
EXPERIMENT = TRACK / "experiments" / "paper-grade-code-mode-kv-capsule-evaluation-2026-06-05"
PRIMARY50 = TRACK / "experiments" / "nonhandmade-code-mode-kv-agent-benchmark-2026-06-05"
ARTIFACTS = TRACK / "paper-artifacts"
OUT = TRACK / "paper-site" / "site" / "index.html"


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


def fmt_int(value: float | int) -> str:
    return f"{value:,.0f}"


def fmt_minutes(ms: float) -> str:
    minutes = ms / 60000
    if minutes >= 60:
        return f"{minutes / 60:.2f} h"
    return f"{minutes:.1f} min"


def svg_bar_chart(
    title: str,
    rows: list[tuple[str, float, str]],
    *,
    max_value: float | None = None,
    unit: str = "",
    width: int = 980,
    height: int | None = None,
    color: str = "#245c73",
    accent: str | None = None,
) -> str:
    height = height or (130 + len(rows) * 48)
    left, right, top, bottom = 210, 58, 58, 46
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_v = max_value or max(v for _, v, _ in rows) or 1
    gap = 14
    bar_h = max(18, (plot_h - gap * (len(rows) - 1)) / len(rows))
    parts = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
        f'<text x="{left}" y="28" class="chart-title">{esc(title)}</text>',
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" class="axis" />',
    ]
    for i, (label, value, note) in enumerate(rows):
        y = top + i * (bar_h + gap)
        w = 0 if max_v == 0 else (value / max_v) * plot_w
        fill = accent if accent and i == 0 else color
        label_lines = label.split("\n")
        for j, line in enumerate(label_lines):
            parts.append(f'<text x="{left - 14}" y="{y + 14 + j * 15}" class="ylabel">{esc(line)}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{w:.1f}" height="{bar_h:.1f}" rx="4" class="bar" fill="{fill}" />')
        parts.append(f'<text x="{left + w + 10}" y="{y + bar_h / 2 + 5}" class="value">{esc(note or (fmt_int(value) + unit))}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def svg_log_bar_chart(title: str, rows: list[tuple[str, float, str]], *, width: int = 980, height: int | None = None) -> str:
    import math

    height = height or (130 + len(rows) * 52)
    left, right, top, bottom = 230, 70, 58, 48
    plot_w = width - left - right
    plot_h = height - top - bottom
    logs = [math.log10(max(v, 1)) for _, v, _ in rows]
    min_log = 0
    max_log = max(logs) or 1
    gap = 16
    bar_h = max(20, (plot_h - gap * (len(rows) - 1)) / len(rows))
    palette = ["#2b7a78", "#a33d2e", "#777777"]
    parts = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
        f'<text x="{left}" y="28" class="chart-title">{esc(title)} (log scale)</text>',
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" class="axis" />',
    ]
    for i, (label, value, note) in enumerate(rows):
        y = top + i * (bar_h + gap)
        w = ((math.log10(max(value, 1)) - min_log) / (max_log - min_log)) * plot_w if max_log > min_log else plot_w
        parts.append(f'<text x="{left - 14}" y="{y + bar_h / 2 + 5}" class="ylabel">{esc(label)}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{w:.1f}" height="{bar_h:.1f}" rx="4" class="bar" fill="{palette[i % len(palette)]}" />')
        parts.append(f'<text x="{left + w + 10}" y="{y + bar_h / 2 + 5}" class="value">{esc(note)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def svg_donut(title: str, rows: list[tuple[str, int]], *, width: int = 520, height: int = 360) -> str:
    total = sum(v for _, v in rows)
    colors = ["#2b7a78", "#245c73", "#8a6f2a", "#a33d2e", "#6f5f90", "#4f6f52"]
    cx, cy, r = 150, 180, 88
    import math

    def point(angle: float) -> tuple[float, float]:
        return cx + r * math.cos(angle), cy + r * math.sin(angle)

    start = -math.pi / 2
    parts = [
        f'<svg class="chart compact-chart" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
        f'<text x="28" y="30" class="chart-title">{esc(title)}</text>',
    ]
    for i, (label, value) in enumerate(rows):
        frac = value / total
        end = start + frac * math.tau
        x1, y1 = point(start)
        x2, y2 = point(end)
        large = 1 if end - start > math.pi else 0
        parts.append(
            f'<path d="M {cx} {cy} L {x1:.2f} {y1:.2f} A {r} {r} 0 {large} 1 {x2:.2f} {y2:.2f} Z" '
            f'fill="{colors[i % len(colors)]}" class="slice" />'
        )
        start = end
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="52" fill="#f7f3eb" />')
    parts.append(f'<text x="{cx}" y="{cy - 3}" class="donut-total">{total}</text>')
    parts.append(f'<text x="{cx}" y="{cy + 18}" class="donut-label">cases</text>')
    lx, ly = 292, 88
    for i, (label, value) in enumerate(rows):
        y = ly + i * 34
        parts.append(f'<rect x="{lx}" y="{y - 12}" width="14" height="14" rx="2" fill="{colors[i % len(colors)]}" />')
        parts.append(f'<text x="{lx + 24}" y="{y}" class="legend">{esc(label)}: {value}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


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
      --paper: #f7f3eb;
      --ink: #151515;
      --muted: #5f6767;
      --line: #d6cec0;
      --green: #2b7a78;
      --blue: #245c73;
      --red: #a33d2e;
      --gold: #8a6f2a;
      --panel: #fffaf1;
      --code: #eee6d8;
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
      max-width: 1180px;
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
      max-width: 960px;
      margin: 0 auto 42px;
      text-align: center;
      border-bottom: 2px solid var(--ink);
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
      font-size: clamp(34px, 6vw, 66px);
      line-height: 1.02;
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
      max-width: 960px;
      margin: 0 auto 54px;
    }}
    h2 {{
      font-size: 30px;
      line-height: 1.18;
      margin: 0 0 16px;
      border-top: 1px solid var(--line);
      padding-top: 28px;
    }}
    h3 {{
      font-size: 21px;
      margin: 28px 0 10px;
      line-height: 1.25;
    }}
    p {{ margin: 0 0 14px; }}
    .abstract {{
      font-size: 17px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 22px 24px;
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 28px 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .kpi {{
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 6px;
      padding: 14px 16px;
    }}
    .kpi b {{ display: block; font-size: 26px; line-height: 1.05; margin-bottom: 6px; }}
    .kpi span {{ color: var(--muted); font-size: 12px; line-height: 1.3; display: block; }}
    .figure {{
      margin: 26px 0 34px;
      padding: 18px;
      border: 1px solid var(--line);
      background: #fbf7ef;
      border-radius: 6px;
      overflow-x: auto;
    }}
    .caption {{
      margin: 10px 2px 0;
      color: var(--muted);
      font-size: 13px;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .chart {{ width: 100%; min-width: 720px; height: auto; display: block; }}
    .compact-chart {{ min-width: 460px; max-width: 560px; margin: 0 auto; }}
    .chart-title, .value, .ylabel, .legend, .donut-label {{
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    .chart-title {{ font-size: 18px; font-weight: 720; fill: var(--ink); }}
    .ylabel {{ font-size: 13px; text-anchor: end; fill: #303636; }}
    .value {{ font-size: 13px; fill: #303636; }}
    .axis {{ stroke: #9f9688; stroke-width: 1; }}
    .bar {{ opacity: .94; }}
    .slice {{ stroke: var(--paper); stroke-width: 2; }}
    .donut-total {{ font: 720 30px ui-sans-serif, system-ui; text-anchor: middle; fill: var(--ink); }}
    .donut-label {{ font-size: 12px; text-anchor: middle; fill: var(--muted); }}
    .legend {{ font-size: 13px; fill: #303636; }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 18px 0 24px;
      background: var(--panel);
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
    th {{ background: #ece4d6; font-weight: 720; }}
    tr:last-child td {{ border-bottom: 0; }}
    code {{
      background: var(--code);
      border-radius: 4px;
      padding: 1px 4px;
      font-size: .92em;
    }}
    .callout {{
      border-left: 4px solid var(--green);
      background: var(--panel);
      padding: 15px 18px;
      margin: 20px 0;
      border-radius: 0 6px 6px 0;
    }}
    .warning {{ border-left-color: var(--red); }}
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
      max-width: 960px;
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
        {svg_bar_chart("Selected cohort pass rate", pass_rows, max_value=100, accent="#2b7a78")}
        <p class="caption">Figure 1. Positive lanes and baselines on the selected 100-case BFCL-derived cohort. Source: <code>selected-cohort-summary.json</code>.</p>
      </div>
      <div class="figure">
        {svg_bar_chart("Selected cohort mean latency", timing_rows, color="#8a6f2a")}
        <p class="caption">Figure 2. This mechanism run supports semantic preservation, not a restored-KV speedup. Source: <code>selected-cohort-summary.json</code>.</p>
      </div>
      <div class="two-col">
        <div class="figure">
          {svg_donut("Selected cohort category mix", list(selected["category_counts"].items()))}
          <p class="caption">Figure 3. Category mix for the selected 100-case cohort.</p>
        </div>
        <div class="figure">
          {svg_bar_chart("Codex natural baseline pass by category", failure_chart_rows, max_value=26, height=420, color="#a33d2e")}
          <p class="caption">Figure 4. Natural Codex/Ollama text-compaction pass counts by category. Source: <code>repeated-work-speed-findings.md</code>.</p>
        </div>
      </div>
      <div class="figure">
        {svg_log_bar_chart("Repeated-work visible input burden", token_rows)}
        <p class="caption">Figure 5. Log scale because the visible-token gap is too large for a linear chart. Codex token telemetry should be read as route-reported cumulative burden.</p>
      </div>
      <div class="figure">
        {svg_log_bar_chart("Repeated-work cumulative wall time", runtime_rows)}
        <p class="caption">Figure 6. KV completed the repeated-work stream in 14.2 minutes versus 3.28 hours for the natural Codex/Ollama text-compaction lane.</p>
      </div>
      <div class="figure">
        {svg_log_bar_chart("Repeated-work output token burden", output_rows)}
        <p class="caption">Figure 7. Output-token telemetry also shows the practical harness burden difference. Source: <code>repeated-work-speed-summary.json</code>.</p>
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
