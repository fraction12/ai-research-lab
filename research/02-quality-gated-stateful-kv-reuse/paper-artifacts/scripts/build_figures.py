#!/usr/bin/env python3
"""Build paper figures with Matplotlib for web and paper outputs."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TRACK = ROOT / "research" / "02-quality-gated-stateful-kv-reuse"
EXPERIMENT = TRACK / "experiments" / "paper-grade-code-mode-kv-capsule-evaluation-2026-06-05"
OUT_DIR = TRACK / "paper-artifacts" / "figures"
MANIFEST = OUT_DIR / "figure-manifest.json"


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
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
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


def save_web_figure(fig, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{name}.svg", bbox_inches="tight")


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
        ax.text(min(value + 1.5, 101.5), yi, note, va="center", ha="left", color=INK, fontsize=9)


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
        ax.text(value + xmax * 0.015, yi, note, va="center", ha="left", color=INK, fontsize=9)


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
    fig, (ax1, ax2) = plt.subplots(
        1,
        2,
        figsize=(10.8, 3.9),
        gridspec_kw={"width_ratios": [1.6, 0.9], "wspace": 0.38},
    )
    horizontal_rate(
        ax1,
        [LABELS[k] for k in positive],
        [counts[k]["gate_passed"] for k in positive],
        [f'{counts[k]["gate_passed"]}/100' for k in positive],
        color=BLUE,
    )
    ax1.set_title("Positive lanes")
    leak_values = [counts[k]["records"] - counts[k]["gate_passed"] for k in negatives]
    y = list(range(len(negatives)))
    ax2.scatter(leak_values, y, color=VERMILLION, s=42, zorder=3)
    ax2.set_yticks(y, [LABELS[k] for k in negatives])
    ax2.invert_yaxis()
    ax2.set_xlim(-0.2, 5)
    ax2.set_xticks([0, 1, 2, 3, 4, 5])
    ax2.set_xlabel("Leaks observed (count)")
    apply_grid(ax2)
    for yi, value in zip(y, leak_values, strict=True):
        ax2.text(value + 0.12, yi, f"{value} / 100", va="center", ha="left", color=INK, fontsize=9)
    ax2.set_title("Negative-control leaks")
    fig.suptitle("Control-ladder outcome on selected 100-case cohort", y=1.03, fontsize=13)
    save_figure(fig, "figure-01-control-ladder")
    plt.close(fig)


def build_control_ladder_mobile(plt, selected: dict) -> None:
    counts = selected["counts_by_control"]
    positive = [
        "code_mode_full_visible",
        "code_mode_native_live_append",
        "code_mode_restored_kv_capsule",
        "direct_full_visible_tools",
        "compact_visible_evidence_code_mode",
    ]
    negatives = ["code_mode_fresh_tail_only", "code_mode_wrong_capsule_negative"]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5.4, 7.6), gridspec_kw={"height_ratios": [2.35, 1]})
    horizontal_rate(
        ax1,
        [LABELS[k].replace("\n", " ") for k in positive],
        [counts[k]["gate_passed"] for k in positive],
        [f'{counts[k]["gate_passed"]}/100' for k in positive],
        color=BLUE,
    )
    ax1.set_title("Positive lanes")
    leak_values = [counts[k]["records"] - counts[k]["gate_passed"] for k in negatives]
    y = list(range(len(negatives)))
    ax2.scatter(leak_values, y, color=VERMILLION, s=48, zorder=3)
    ax2.set_yticks(y, [LABELS[k].replace("\n", " ") for k in negatives])
    ax2.invert_yaxis()
    ax2.set_xlim(-0.2, 5)
    ax2.set_xticks([0, 1, 2, 3, 4, 5])
    ax2.set_xlabel("Leaks observed (count)")
    apply_grid(ax2)
    for yi, value in zip(y, leak_values, strict=True):
        ax2.text(value + 0.12, yi, f"{value}/100", va="center", ha="left", color=INK, fontsize=10)
    ax2.set_title("Negative-control leaks")
    fig.suptitle("Control ladder: selected 100-case cohort", y=0.985, fontsize=13)
    fig.subplots_adjust(left=0.28, right=0.95, top=0.91, bottom=0.08, hspace=0.72)
    save_web_figure(fig, "figure-01-control-ladder-mobile")
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
    fig, ax = plt.subplots(figsize=(8.2, 3.45))
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


def build_latency_mobile(plt, selected: dict) -> None:
    timing = selected["timing_mean_ms"]
    controls = [
        "code_mode_full_visible",
        "code_mode_native_live_append",
        "code_mode_restored_kv_capsule",
        "direct_full_visible_tools",
        "compact_visible_evidence_code_mode",
    ]
    values = [timing[k] for k in controls]
    fig, ax = plt.subplots(figsize=(5.4, 4.6))
    horizontal_count(
        ax,
        [LABELS[k].replace("\n", " ") for k in controls],
        values,
        [f"{v:,.0f} ms" for v in values],
        color=GRAY,
        xlabel="Mean total latency (ms); lower is better",
        xmax=max(values) * 1.28,
    )
    ax.set_title("Selected-cohort latency")
    save_web_figure(fig, "figure-02-latency-mobile")
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
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
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
        ax.text(101.5, yi, f"{p}/{t}", va="center", ha="left", fontsize=9, color=INK)
    save_figure(fig, "figure-03-codex-failures")
    plt.close(fig)


def build_codex_failures_mobile(plt) -> None:
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
    fig, ax = plt.subplots(figsize=(5.4, 4.8))
    ax.barh(y, pass_rates, color=BLUE, height=0.58, label="pass")
    ax.barh(y, fail_rates, left=pass_rates, color=SOFT_VERMILLION, height=0.58, label="fail")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of audited category sample (%)")
    ax.set_title("Natural baseline pass/fail")
    ax.legend(loc="lower right", frameon=False, ncols=2)
    apply_grid(ax)
    for yi, p, t in zip(y, passed, totals, strict=True):
        ax.text(101.5, yi, f"{p}/{t}", va="center", ha="left", fontsize=9, color=INK)
    save_web_figure(fig, "figure-03-codex-failures-mobile")
    plt.close(fig)


def log_bar(plt, rows: list[tuple[str, float, str]], *, title: str, xlabel: str, filename: str) -> None:
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    notes = [r[2] for r in rows]
    y = list(range(len(rows)))
    fig, ax = plt.subplots(figsize=(8.2, 2.9))
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
        ax.text(value * 1.08, yi, note, va="center", ha="left", fontsize=9, color=INK)
    ax.set_xlim(1, xmax * 9)
    save_figure(fig, filename)
    plt.close(fig)


def log_bar_mobile(plt, rows: list[tuple[str, float, str]], *, title: str, xlabel: str, filename: str) -> None:
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    notes = [r[2] for r in rows]
    y = list(range(len(rows)))
    fig, ax = plt.subplots(figsize=(5.4, 3.45))
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
        ax.text(value * 1.08, yi, note, va="center", ha="left", fontsize=9, color=INK)
    ax.set_xlim(1, xmax * 12)
    save_web_figure(fig, f"{filename}-mobile")
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
    build_control_ladder_mobile(plt, selected)
    build_latency(plt, selected)
    build_latency_mobile(plt, selected)
    build_codex_failures(plt)
    build_codex_failures_mobile(plt)
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
    log_bar_mobile(
        plt,
        [
            ("KV capsule + PTI", kv["visible_input_tokens"], f'{kv["visible_input_tokens"]:,.0f}'),
            ("Codex text compaction", natural["visible_input_tokens"], f'{natural["visible_input_tokens"]:,.0f}'),
            ("Codex attempted", attempted["visible_input_tokens"], f'{attempted["visible_input_tokens"]:,.0f}'),
        ],
        title="Visible input tokens",
        xlabel="Log10 scale",
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
    log_bar_mobile(
        plt,
        [
            ("KV capsule + PTI", kv["cumulative_wall_ms"], "14.2 min"),
            ("Codex text compaction", natural["cumulative_wall_ms"], "3.28 h"),
            ("Codex attempted", attempted["cumulative_wall_ms"], "3.20 h"),
        ],
        title="Cumulative wall time",
        xlabel="Milliseconds, log10 scale",
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
    log_bar_mobile(
        plt,
        [
            ("KV capsule + PTI", kv["output_tokens"], f'{kv["output_tokens"]:,.0f}'),
            ("Codex text compaction", natural["output_tokens"], f'{natural["output_tokens"]:,.0f}'),
            ("Codex attempted", attempted["output_tokens"], f'{attempted["output_tokens"]:,.0f}'),
        ],
        title="Output tokens",
        xlabel="Log10 scale",
        filename="figure-06-output-tokens",
    )
    manifest = {
        "generated_by": str((ARTIFACTS := TRACK / "paper-artifacts") / "scripts" / "build_figures.py"),
        "outputs": sorted(p.name for p in OUT_DIR.glob("figure-*.*")),
        "source_artifacts": [
            str(EXPERIMENT / "selected-cohort-summary.json"),
            str(EXPERIMENT / "repeated-work-speed-summary.json"),
            str(EXPERIMENT / "repeated-work-speed-findings.md"),
        ],
        "figures": {
            "figure-01-control-ladder": {
                "source": "selected-cohort-summary.json",
                "claim_boundary": "Mechanism/control evidence only; not a speedup claim.",
            },
            "figure-02-latency": {
                "source": "selected-cohort-summary.json",
                "claim_boundary": "Reports committed run means; no replicated uncertainty interval.",
            },
            "figure-03-codex-failures": {
                "source": "repeated-work-speed-findings.md",
                "claim_boundary": "Diagnostic category breakdown; not causal compaction evidence.",
            },
            "figure-04-visible-input-tokens": {
                "source": "repeated-work-speed-summary.json",
                "claim_boundary": "Uses route-reported cumulative visible-input telemetry.",
            },
            "figure-05-wall-time": {
                "source": "repeated-work-speed-summary.json",
                "claim_boundary": "Practical runtime comparison; not prompt-identical mechanism comparison.",
            },
            "figure-06-output-tokens": {
                "source": "repeated-work-speed-summary.json",
                "claim_boundary": "Harness burden comparison assuming comparable task success.",
            },
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(OUT_DIR)


if __name__ == "__main__":
    main()
