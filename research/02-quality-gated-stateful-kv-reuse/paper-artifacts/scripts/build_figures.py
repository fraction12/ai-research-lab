#!/usr/bin/env python3
"""Build paper figures with Matplotlib for web and paper outputs."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TRACK = ROOT / "research" / "02-quality-gated-stateful-kv-reuse"
EXPERIMENT = TRACK / "experiments" / "paper-grade-code-mode-kv-capsule-evaluation-2026-06-05"
OUT_DIR = TRACK / "paper-artifacts" / "figures"


LABELS = {
    "code_mode_full_visible": "Full visible\nPTI",
    "code_mode_native_live_append": "Native live\nappend",
    "code_mode_restored_kv_capsule": "Restored\nKV capsule",
    "code_mode_fresh_tail_only": "Fresh tail\nnegative",
    "code_mode_wrong_capsule_negative": "Wrong capsule\nnegative",
    "direct_full_visible_tools": "Direct visible\ntools",
    "compact_visible_evidence_code_mode": "Compact visible\nevidence",
}

BLUE = "#1f4e79"
GRAY = "#777777"
VERMILLION = "#b23b30"
SOFT_VERMILLION = "#e2aaa4"
GRID = "#dddddd"
INK = "#171717"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def setup_matplotlib():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.ticker import FuncFormatter, LogLocator
    except ModuleNotFoundError as exc:
        missing = exc.name or "matplotlib"
        raise SystemExit(
            f"Missing {missing}. Install dev requirements first:\n"
            f"  python3 -m venv .venv\n"
            f"  .venv/bin/python -m pip install -r requirements-dev.txt"
        ) from exc

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 160,
            "savefig.dpi": 300,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "axes.edgecolor": INK,
            "axes.linewidth": 0.8,
        }
    )
    return plt, FuncFormatter, LogLocator


def save_figure(fig, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "pdf"):
        fig.savefig(OUT_DIR / f"{name}.{ext}", bbox_inches="tight")


def apply_grid(ax, *, axis: str = "x") -> None:
    ax.grid(True, axis=axis, color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def horizontal_rate(ax, labels: list[str], values: list[float], notes: list[str], *, color: str) -> None:
    y = list(range(len(labels)))
    ax.barh(y, values, color=color, height=0.58)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 105)
    ax.set_xlabel("Pass rate (%)")
    ax.set_xticks([0, 25, 50, 75, 100])
    apply_grid(ax)
    for yi, value, note in zip(y, values, notes, strict=True):
        ax.text(min(value + 1.5, 101.5), yi, note, va="center", ha="left", color=INK, fontsize=8)


def horizontal_count(
    ax,
    labels: list[str],
    values: list[float],
    notes: list[str],
    *,
    color: str,
    xlabel: str,
    xmax: float | None = None,
) -> None:
    y = list(range(len(labels)))
    ax.barh(y, values, color=color, height=0.58)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    xmax = xmax or max(max(values) * 1.15, 1)
    ax.set_xlim(0, xmax)
    ax.set_xlabel(xlabel)
    apply_grid(ax)
    for yi, value, note in zip(y, values, notes, strict=True):
        ax.text(value + xmax * 0.015, yi, note, va="center", ha="left", color=INK, fontsize=8)


def build_control_ladder(plt, selected: dict) -> None:
    counts = selected["counts_by_control"]
    positive = [
        "code_mode_full_visible",
        "code_mode_native_live_append",
        "code_mode_restored_kv_capsule",
        "direct_full_visible_tools",
        "compact_visible_evidence_code_mode",
    ]
    negatives = ["code_mode_fresh_tail_only", "code_mode_wrong_capsule_negative"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.3), gridspec_kw={"width_ratios": [1.45, 1]})
    horizontal_rate(
        ax1,
        [LABELS[k] for k in positive],
        [counts[k]["gate_passed"] for k in positive],
        [f'{counts[k]["gate_passed"]}/100' for k in positive],
        color=BLUE,
    )
    ax1.set_title("Positive lanes")
    horizontal_count(
        ax2,
        [LABELS[k] for k in negatives],
        [counts[k]["records"] - counts[k]["gate_passed"] for k in negatives],
        [f'{counts[k]["records"] - counts[k]["gate_passed"]} leaks' for k in negatives],
        color=VERMILLION,
        xlabel="Leak count out of 100",
        xmax=100,
    )
    ax2.set_title("Negative-control leaks")
    fig.suptitle("Control-ladder outcome on selected 100-case cohort", y=1.04, fontsize=11)
    save_figure(fig, "figure-01-control-ladder")
    plt.close(fig)


def build_latency(plt, selected: dict) -> None:
    timing = selected["timing_mean_ms"]
    controls = [
        "code_mode_full_visible",
        "code_mode_native_live_append",
        "code_mode_restored_kv_capsule",
        "direct_full_visible_tools",
        "compact_visible_evidence_code_mode",
    ]
    values = [timing[k] for k in controls]
    fig, ax = plt.subplots(figsize=(7.4, 3.1))
    horizontal_count(
        ax,
        [LABELS[k] for k in controls],
        values,
        [f"{v:,.1f} ms" for v in values],
        color=GRAY,
        xlabel="Mean total latency (ms); lower is better",
        xmax=max(values) * 1.23,
    )
    ax.set_title("Selected-cohort latency boundary")
    save_figure(fig, "figure-02-latency")
    plt.close(fig)


def build_codex_failures(plt) -> None:
    rows = [
        ("java", 14, 17),
        ("javascript", 0, 1),
        ("multiple", 21, 25),
        ("parallel", 13, 14),
        ("parallel_multiple", 13, 17),
        ("simple", 25, 26),
    ]
    labels = [r[0] for r in rows]
    passed = [r[1] for r in rows]
    totals = [r[2] for r in rows]
    pass_rates = [(p / t) * 100 for p, t in zip(passed, totals, strict=True)]
    fail_rates = [100 - rate for rate in pass_rates]
    y = list(range(len(rows)))
    fig, ax = plt.subplots(figsize=(7.4, 3.35))
    ax.barh(y, pass_rates, color=BLUE, height=0.58, label="pass")
    ax.barh(y, fail_rates, left=pass_rates, color=SOFT_VERMILLION, height=0.58, label="fail")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of cases in audited failure sample (%)")
    ax.set_title("Natural Codex/Ollama pass/fail by BFCL category")
    ax.legend(loc="lower right", frameon=False, ncols=2)
    apply_grid(ax)
    for yi, p, t in zip(y, passed, totals, strict=True):
        ax.text(101.5, yi, f"{p}/{t}", va="center", ha="left", fontsize=8, color=INK)
    save_figure(fig, "figure-03-codex-failures")
    plt.close(fig)


def log_bar(plt, rows: list[tuple[str, float, str]], *, title: str, xlabel: str, filename: str) -> None:
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    notes = [r[2] for r in rows]
    y = list(range(len(rows)))
    fig, ax = plt.subplots(figsize=(7.4, 2.65))
    colors = [BLUE, VERMILLION, GRAY][: len(rows)]
    ax.barh(y, values, color=colors, height=0.56)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(True, axis="x", which="both", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    xmax = max(values)
    for yi, value, note in zip(y, values, notes, strict=True):
        ax.text(value * 1.08, yi, note, va="center", ha="left", fontsize=8, color=INK)
    ax.set_xlim(1, xmax * 9)
    save_figure(fig, filename)
    plt.close(fig)


def main() -> None:
    plt, _, _ = setup_matplotlib()
    selected = load_json(EXPERIMENT / "selected-cohort-summary.json")
    repeated = load_json(EXPERIMENT / "repeated-work-speed-summary.json")
    systems = repeated["systems"]
    kv = systems["kv_capsule_code_mode"]
    natural = systems["codex_ollama_regular_tools_natural_text_compaction"]
    attempted = systems["codex_ollama_regular_tools_compaction"]

    build_control_ladder(plt, selected)
    build_latency(plt, selected)
    build_codex_failures(plt)
    log_bar(
        plt,
        [
            ("KV capsule + PTI", kv["visible_input_tokens"], f'{kv["visible_input_tokens"]:,.0f}'),
            ("Codex text compaction", natural["visible_input_tokens"], f'{natural["visible_input_tokens"]:,.0f}'),
            ("Codex attempted", attempted["visible_input_tokens"], f'{attempted["visible_input_tokens"]:,.0f}'),
        ],
        title="Reported visible input tokens",
        xlabel="Visible input tokens, log10 scale",
        filename="figure-04-visible-input-tokens",
    )
    log_bar(
        plt,
        [
            ("KV capsule + PTI", kv["cumulative_wall_ms"], "14.2 min"),
            ("Codex text compaction", natural["cumulative_wall_ms"], "3.28 h"),
            ("Codex attempted", attempted["cumulative_wall_ms"], "3.20 h"),
        ],
        title="Repeated-work cumulative wall time",
        xlabel="Wall time in milliseconds, log10 scale; lower is better",
        filename="figure-05-wall-time",
    )
    log_bar(
        plt,
        [
            ("KV capsule + PTI", kv["output_tokens"], f'{kv["output_tokens"]:,.0f}'),
            ("Codex text compaction", natural["output_tokens"], f'{natural["output_tokens"]:,.0f}'),
            ("Codex attempted", attempted["output_tokens"], f'{attempted["output_tokens"]:,.0f}'),
        ],
        title="Repeated-work output tokens",
        xlabel="Output tokens, log10 scale; lower is better",
        filename="figure-06-output-tokens",
    )
    print(OUT_DIR)


if __name__ == "__main__":
    main()
