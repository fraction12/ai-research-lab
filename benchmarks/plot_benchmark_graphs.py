#!/usr/bin/env python3
"""Generate publication-oriented benchmark figures from local result JSON."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.ticker import FuncFormatter
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by missing envs
    missing = exc.name or "matplotlib"
    raise SystemExit(
        f"Missing Python package '{missing}'. Install chart dependencies with:\n"
        "  python3 -m pip install -r requirements-dev.txt"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
PRINTY_RAW = ROOT / "benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw"
LARGE_RAW = ROOT / "benchmarks/datasets/printtestbot-large-prefix-2026-06-02/raw"
OUT_DIR = ROOT / "docs/assets/benchmark-graphs"

COLORS = {
    "ink": "#222222",
    "muted": "#5f6368",
    "grid": "#cfcfcf",
    "paper": "#ffffff",
    "surface": "#ffffff",
    "warm": "#0072B2",
    "restart": "#D55E00",
    "direct": "#0072B2",
    "cache": "#009E73",
    "slot": "#E69F00",
    "target": "#D55E00",
    "accent": "#CC79A7",
}


@dataclass(frozen=True)
class CacheSummary:
    label: str
    before_ms: float
    after_ms: float
    saved_ms: float
    saved_ratio: float


def configure_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 300,
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.titleweight": "normal",
            "axes.labelsize": 8,
            "axes.edgecolor": COLORS["ink"],
            "axes.linewidth": 0.8,
            "axes.facecolor": "#EAEAEA",
            "figure.facecolor": "white",
            "text.color": COLORS["ink"],
            "axes.labelcolor": COLORS["muted"],
            "xtick.color": COLORS["muted"],
            "ytick.color": COLORS["muted"],
            "grid.color": "#CFCFCF",
            "grid.linewidth": 0.6,
            "axes.grid": True,
            "legend.frameon": False,
            "legend.fontsize": 8,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ms_to_s(value: float) -> float:
    return value / 1000.0


def ns_to_s(value: float) -> float:
    return value / 1_000_000_000.0


def seconds_label(value: float, _pos: object | None = None) -> str:
    if value >= 100:
        return f"{value:.0f}s"
    if value >= 10:
        return f"{value:.1f}s"
    return f"{value:.2f}s"


def percent_label(value: float, _pos: object | None = None) -> str:
    return f"{value:.0f}%"


def mb_label(value: float, _pos: object | None = None) -> str:
    return f"{value:.0f}MB"


def save_figure(fig: plt.Figure, stem: str) -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = [OUT_DIR / f"{stem}.svg", OUT_DIR / f"{stem}.pdf", OUT_DIR / f"{stem}.png"]
    for path in paths:
        fig.savefig(path, bbox_inches="tight", pad_inches=0.025)
        if path.suffix == ".svg":
            svg = path.read_text(encoding="utf-8")
            path.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    return paths


def annotate_title(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.suptitle(title, x=0.02, y=0.985, ha="left", va="top", fontsize=10.5, fontweight="semibold")
    fig.text(0.02, 0.935, subtitle, ha="left", va="top", fontsize=8, color=COLORS["muted"])


def apply_standard_layout(
    fig: plt.Figure,
    *,
    left: float = 0.12,
    right: float = 0.985,
    top: float = 0.82,
    bottom: float = 0.15,
) -> None:
    fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom)


def finish_axes(ax: plt.Axes, y_formatter: FuncFormatter | None = None) -> None:
    ax.grid(axis="y", alpha=0.95)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", length=0)
    if y_formatter:
        ax.yaxis.set_major_formatter(y_formatter)


def cache_summary_from_comparison(label: str, comparison: dict[str, Any], before_key: str, after_key: str) -> CacheSummary:
    before = float(comparison[before_key])
    after = float(comparison[after_key])
    saved = before - after
    return CacheSummary(label=label, before_ms=before, after_ms=after, saved_ms=saved, saved_ratio=saved / before)


def average(rows: list[CacheSummary], label: str) -> CacheSummary:
    before = sum(row.before_ms for row in rows) / len(rows)
    after = sum(row.after_ms for row in rows) / len(rows)
    saved = before - after
    return CacheSummary(label=label, before_ms=before, after_ms=after, saved_ms=saved, saved_ratio=saved / before)


def small_prefix_rows() -> list[CacheSummary]:
    gemma_slot = cache_summary_from_comparison(
        "Gemma slot restore",
        load_json(PRINTY_RAW / "llama-cpp-slot-cache-gemma-3-270m-it-q8.json")["comparison"],
        "baseline_prompt_ms_sum",
        "restored_prompt_ms_sum",
    )
    gemma_wrapper = cache_summary_from_comparison(
        "Gemma Flashcache",
        load_json(PRINTY_RAW / "flashcache-wrapper-gemma-3-270m-it-q8.json")["comparison"],
        "direct_prompt_ms_sum",
        "wrapper_prompt_ms_sum",
    )
    gpt_slot_files = [
        PRINTY_RAW / "20260602T220157Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-llama-cpp-prompt-cache.json",
        PRINTY_RAW / "20260602T230623Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-llama-cpp-prompt-cache.json",
        PRINTY_RAW / "20260603T000124Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-llama-cpp-prompt-cache.json",
    ]
    gpt_wrapper_files = [
        PRINTY_RAW / "20260602T220711Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-flashcache-wrapper.json",
        PRINTY_RAW / "20260602T231145Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-flashcache-wrapper.json",
        PRINTY_RAW / "20260603T000643Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-flashcache-wrapper.json",
    ]
    gpt_slot = average(
        [
            cache_summary_from_comparison(
                "gpt-oss slot restore",
                load_json(path)["comparison"],
                "baseline_prompt_ms_sum",
                "restored_prompt_ms_sum",
            )
            for path in gpt_slot_files
        ],
        "gpt-oss slot mean",
    )
    gpt_wrapper = average(
        [
            cache_summary_from_comparison(
                "gpt-oss Flashcache",
                load_json(path)["comparison"],
                "direct_prompt_ms_sum",
                "wrapper_prompt_ms_sum",
            )
            for path in gpt_wrapper_files
        ],
        "gpt-oss Flashcache mean",
    )
    return [gemma_slot, gemma_wrapper, gpt_slot, gpt_wrapper]


def large_prefix_file(prefix_kb: int, suffix: str) -> Path:
    matches = sorted(LARGE_RAW.glob(f"*large-prefix-{prefix_kb}kb-{suffix}.json"))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one {prefix_kb}kb {suffix} file, found {matches}")
    return matches[0]


def wrapper_ladder() -> tuple[list[float], list[float], list[float], list[float]]:
    prefix_kb: list[float] = []
    direct_s: list[float] = []
    cache_s: list[float] = []
    saved_s: list[float] = []
    for size in [16, 32, 64]:
        data = load_json(large_prefix_file(size, "flashcache-wrapper"))
        prefix_kb.append(data["prompt_set"]["prefix_prompt_bytes"] / 1024.0)
        comparison = data["comparison"]
        direct = ms_to_s(float(comparison["direct_prompt_ms_sum"]))
        cached = ms_to_s(float(comparison["wrapper_prompt_ms_sum"]))
        direct_s.append(direct)
        cache_s.append(cached)
        saved_s.append(direct - cached)
    return prefix_kb, direct_s, cache_s, saved_s


def slot_size_ladder() -> tuple[list[float], list[float]]:
    files = [
        PRINTY_RAW / "20260603T000124Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-llama-cpp-prompt-cache.json",
        large_prefix_file(16, "llama-cpp-prompt-cache"),
        large_prefix_file(32, "llama-cpp-prompt-cache"),
        large_prefix_file(64, "llama-cpp-prompt-cache"),
    ]
    prefix_kb: list[float] = []
    slot_mb: list[float] = []
    for path in files:
        data = load_json(path)
        prefix_kb.append(data["prompt_set"]["prefix_prompt_bytes"] / 1024.0)
        slot_mb.append(data["slot_cache"]["file_bytes"] / 1_000_000.0)
    return prefix_kb, slot_mb


def linear_projection(xs: list[float], ys: list[float], target_x: float) -> float:
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    intercept = (sy - slope * sx) / n
    return intercept + slope * target_x


def write_chart_data() -> None:
    prefix_kb, direct_s, cache_s, saved_s = wrapper_ladder()
    slot_prefix_kb, slot_mb = slot_size_ladder()
    rows = small_prefix_rows()
    projected_direct_s = linear_projection(prefix_kb, direct_s, 128.0)
    projected_cache_s = linear_projection(prefix_kb, cache_s, 128.0)
    payload = {
        "small_prefix_cache_outcomes": [asdict(row) for row in rows],
        "large_prefix_flashcache_ladder": [
            {
                "prefix_kb": prefix_kb[idx],
                "direct_prompt_eval_s": direct_s[idx],
                "flashcache_prompt_eval_s": cache_s[idx],
                "saved_s": saved_s[idx],
                "saved_ratio": saved_s[idx] / direct_s[idx],
            }
            for idx in range(len(prefix_kb))
        ],
        "slot_file_size_ladder": [
            {"prefix_kb": slot_prefix_kb[idx], "slot_file_mb": slot_mb[idx]}
            for idx in range(len(slot_prefix_kb))
        ],
        "projection": {
            "prefix_kb": 128.0,
            "direct_prompt_eval_s": projected_direct_s,
            "flashcache_prompt_eval_s": projected_cache_s,
            "saved_s": projected_direct_s - projected_cache_s,
            "metal_target_prompt_eval_s": projected_direct_s * 0.75,
            "method": "linear fit from measured 16KB, 32KB, and 64KB large-prefix ladder",
        },
    }
    (OUT_DIR / "chart-data.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def paper_evidence_chart() -> list[Path]:
    restart_data = load_json(PRINTY_RAW / "ollama-restart-compare-gpt-oss-20b.json")
    sequences = {seq["name"]: seq["summary"] for seq in restart_data["strategies"][0]["sequences"]}
    warm = sequences["warm-sequence"]
    restarted = sequences["restarted-sequence"]
    warm_s = [
        ns_to_s(warm["prompt_eval_duration_sum"]),
        ns_to_s(warm["load_duration_sum"]),
        ns_to_s(warm["total_duration_sum"]),
    ]
    restarted_s = [
        ns_to_s(restarted["prompt_eval_duration_sum"]),
        ns_to_s(restarted["load_duration_sum"]),
        ns_to_s(restarted["total_duration_sum"]),
    ]

    small_rows = small_prefix_rows()
    prefix_kb, direct_s, cache_s, _saved_s = wrapper_ladder()
    slot_prefix_kb, slot_mb = slot_size_ladder()
    projected_direct_s = linear_projection(prefix_kb, direct_s, 128.0)
    projected_cache_s = linear_projection(prefix_kb, cache_s, 128.0)
    projected_target_s = projected_direct_s * 0.75

    fig, axes = plt.subplots(2, 2, figsize=(10.8, 5.6), constrained_layout=False)
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.105, top=0.82, wspace=0.28, hspace=0.48)
    ax_a, ax_b, ax_c, ax_d = axes.flat

    legend_handles = [
        Line2D([0], [0], color=COLORS["warm"], marker="o", linewidth=1.7, label="Warm sequence"),
        Line2D([0], [0], color=COLORS["restart"], marker="o", linewidth=1.7, label="Restarted sequence"),
        Patch(facecolor=COLORS["slot"], label="Slot restore"),
        Patch(facecolor=COLORS["cache"], label="Flashcache wrapper"),
        Line2D([0], [0], color=COLORS["direct"], marker="o", linewidth=1.7, label="Direct full prompt"),
        Line2D([0], [0], color=COLORS["target"], marker="o", linewidth=1.6, linestyle=(0, (2, 3)), label="Metal target"),
        Line2D([0], [0], color=COLORS["accent"], marker="o", linewidth=1.7, label="Slot file size"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, 0.985),
        columnspacing=1.45,
        handlelength=2.4,
    )

    # (a) Warm-vs-restarted persistence gap.
    x = list(range(3))
    x_labels = ["Prompt\nEval", "Model\nLoad", "Total\nRequest"]
    ax_a.plot(x, warm_s, color=COLORS["warm"], marker="o", linewidth=1.9)
    ax_a.plot(x, restarted_s, color=COLORS["restart"], marker="o", linewidth=1.9)
    ax_a.set_title("(a) Restarting removes warm-state benefit", pad=3)
    ax_a.set_xticks(x, x_labels)
    ax_a.set_ylabel("Seconds across seven turns")
    ax_a.set_ylim(0, max(restarted_s) * 1.18)
    finish_axes(ax_a, FuncFormatter(seconds_label))
    ax_a.annotate(
        "2.36x prompt eval",
        xy=(0, restarted_s[0]),
        xytext=(0.18, restarted_s[0] + 8.5),
        arrowprops={"arrowstyle": "-", "color": COLORS["muted"], "lw": 0.8},
        fontsize=7.5,
        color=COLORS["muted"],
    )

    # (b) Small-prefix outcomes.
    names = ["Gemma\nslot", "Gemma\nFC", "gpt-oss\nslot", "gpt-oss\nFC"]
    savings_pct = [row.saved_ratio * 100 for row in small_rows]
    bar_colors = [COLORS["slot"], COLORS["cache"], COLORS["slot"], COLORS["cache"]]
    ax_b.bar(range(len(names)), savings_pct, color=bar_colors, width=0.6)
    ax_b.axhline(0, color=COLORS["ink"], linewidth=0.7)
    ax_b.set_title("(b) Small-prefix gains are backend-dependent", pad=3)
    ax_b.set_xticks(range(len(names)), names)
    ax_b.set_ylabel("Prompt-eval reduction")
    ax_b.set_ylim(0, 68)
    finish_axes(ax_b, FuncFormatter(percent_label))
    for idx, value in enumerate(savings_pct):
        label = f"{value:.1f}%"
        ax_b.text(idx, value + 1.4, label, ha="center", va="bottom", fontsize=7.5)

    # (c) Large-prefix ladder plus projection.
    projected_x = [prefix_kb[-1], 128.0]
    ax_c.axvspan(prefix_kb[-1], 128.0, color="#F2F2F2", zorder=0)
    ax_c.plot(prefix_kb, direct_s, color=COLORS["direct"], marker="o", linewidth=1.9)
    ax_c.plot(prefix_kb, cache_s, color=COLORS["cache"], marker="o", linewidth=1.9)
    ax_c.plot(projected_x, [direct_s[-1], projected_direct_s], color=COLORS["direct"], marker="o", linewidth=1.7, linestyle=(0, (4, 3)))
    ax_c.plot(projected_x, [cache_s[-1], projected_cache_s], color=COLORS["cache"], marker="o", linewidth=1.7, linestyle=(0, (4, 3)))
    ax_c.plot(projected_x, [cache_s[-1], projected_target_s], color=COLORS["target"], marker="o", linewidth=1.5, linestyle=(0, (2, 3)))
    ax_c.axvline(prefix_kb[-1], color=COLORS["muted"], linestyle="--", linewidth=0.8)
    ax_c.text(prefix_kb[-1] + 2.0, 174, "Projection\nboundary", rotation=90, va="top", ha="left", fontsize=7, color=COLORS["muted"])
    ax_c.set_title("(c) Larger stable prefixes increase absolute savings", pad=3)
    ax_c.set_xticks([16, 32, 64, 128], ["16K", "32K", "64K", "128K"])
    ax_c.set_ylabel("Prompt-eval seconds")
    ax_c.set_xlabel("Reusable prefix bytes")
    ax_c.set_xlim(10, 132)
    ax_c.set_ylim(0, 185)
    finish_axes(ax_c, FuncFormatter(seconds_label))
    ax_c.annotate(
        "23.0s projected saved",
        xy=(128.0, projected_cache_s),
        xytext=(82, 142),
        arrowprops={"arrowstyle": "-", "color": COLORS["muted"], "lw": 0.8},
        fontsize=7.5,
        color=COLORS["muted"],
    )

    # (d) Whole-slot SSD cost.
    ax_d.plot(slot_prefix_kb, slot_mb, color=COLORS["accent"], marker="o", linewidth=1.9)
    ax_d.fill_between(slot_prefix_kb, slot_mb, color=COLORS["accent"], alpha=0.13)
    ax_d.set_title("(d) Whole-slot blobs grow quickly", pad=3)
    ax_d.set_xticks([5.4, 16, 32, 64], ["5K", "16K", "32K", "64K"])
    ax_d.set_ylabel("Slot file size on SSD")
    ax_d.set_xlabel("Reusable prefix bytes")
    ax_d.set_ylim(0, max(slot_mb) * 1.2)
    finish_axes(ax_d, FuncFormatter(mb_label))
    ax_d.annotate(
        "361MB at 64K",
        xy=(slot_prefix_kb[-1], slot_mb[-1]),
        xytext=(38, 330),
        arrowprops={"arrowstyle": "-", "color": COLORS["muted"], "lw": 0.8},
        fontsize=7.5,
        color=COLORS["muted"],
    )

    return save_figure(fig, "fig1-flashcache-evidence")


def warm_restart_chart() -> list[Path]:
    data = load_json(PRINTY_RAW / "ollama-restart-compare-gpt-oss-20b.json")
    sequences = {seq["name"]: seq["summary"] for seq in data["strategies"][0]["sequences"]}
    warm = sequences["warm-sequence"]
    restarted = sequences["restarted-sequence"]
    labels = ["Prompt eval", "Model load", "Total request"]
    warm_s = [
        ns_to_s(warm["prompt_eval_duration_sum"]),
        ns_to_s(warm["load_duration_sum"]),
        ns_to_s(warm["total_duration_sum"]),
    ]
    restarted_s = [
        ns_to_s(restarted["prompt_eval_duration_sum"]),
        ns_to_s(restarted["load_duration_sum"]),
        ns_to_s(restarted["total_duration_sum"]),
    ]

    fig, ax = plt.subplots(figsize=(8.9, 5.25), constrained_layout=False)
    annotate_title(fig, "Warm runs are much cheaper than restarted runs", "Ollama gpt-oss:20b on the Printy changed-tail workflow")
    apply_standard_layout(fig)
    x = range(len(labels))
    width = 0.34
    ax.bar([i - width / 2 for i in x], warm_s, width, label="Warm", color=COLORS["warm"])
    ax.bar([i + width / 2 for i in x], restarted_s, width, label="Restarted", color=COLORS["restart"])
    ax.set_xticks(list(x), labels)
    ax.set_ylabel("Seconds across seven turns")
    ax.set_ylim(0, max(restarted_s) * 1.24)
    finish_axes(ax, FuncFormatter(seconds_label))
    ax.legend(loc="upper left", ncols=2)
    for i, (warm_value, restart_value) in enumerate(zip(warm_s, restarted_s)):
        ax.text(i - width / 2, warm_value + 1.0, seconds_label(warm_value), ha="center", va="bottom", fontsize=9)
        ax.text(i + width / 2, restart_value + 1.0, seconds_label(restart_value), ha="center", va="bottom", fontsize=9)
    return save_figure(fig, "ollama-warm-vs-restarted")


def exact_repeat_chart() -> list[Path]:
    data = load_json(PRINTY_RAW / "ollama-exact-repeat-gpt-oss-20b.json")
    runs = data["strategies"][0]["scenarios"][0]["runs"]
    values = [ns_to_s(run["prompt_eval_duration"]) for run in runs]

    fig, ax = plt.subplots(figsize=(7.6, 4.8), constrained_layout=False)
    annotate_title(fig, "Exact replay gets cheap, but it is not the target", "Ollama gpt-oss:20b repeats one identical Printy turn")
    apply_standard_layout(fig)
    ax.bar(["Run 1", "Run 2"], values, color=[COLORS["direct"], COLORS["cache"]], width=0.46)
    ax.set_ylabel("Prompt-eval seconds")
    ax.set_ylim(0, max(values) * 1.34)
    finish_axes(ax, FuncFormatter(seconds_label))
    for idx, value in enumerate(values):
        ax.text(idx, value + 0.02, seconds_label(value), ha="center", va="bottom", fontsize=10)
    return save_figure(fig, "ollama-exact-repeat-control")


def small_prefix_chart() -> list[Path]:
    rows = small_prefix_rows()
    labels = [row.label for row in rows]
    values = [row.saved_ratio * 100 for row in rows]
    colors = [COLORS["slot"], COLORS["cache"], COLORS["slot"], COLORS["cache"]]

    fig, ax = plt.subplots(figsize=(9.2, 5.4), constrained_layout=False)
    annotate_title(fig, "Small-prefix cache outcomes", "Prompt-eval savings on the 5.5KB Printy reusable prefix")
    apply_standard_layout(fig, left=0.27, right=0.985, top=0.78, bottom=0.14)
    y_positions = list(range(len(rows)))
    ax.barh(y_positions, values, color=colors, height=0.56)
    ax.set_yticks(y_positions, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Prompt-eval reduction")
    ax.set_xlim(0, 68)
    ax.xaxis.set_major_formatter(FuncFormatter(percent_label))
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="both", length=0)
    for idx, row in enumerate(rows):
        value = row.saved_ratio * 100
        ax.text(value + 1.2, idx - 0.08, f"{value:.1f}%", va="center", ha="left", fontsize=10, fontweight="bold")
        ax.text(
            value + 1.2,
            idx + 0.18,
            f"{seconds_label(ms_to_s(row.before_ms))} -> {seconds_label(ms_to_s(row.after_ms))}; saved {seconds_label(ms_to_s(row.saved_ms))}",
            va="center",
            ha="left",
            fontsize=8.5,
            color=COLORS["muted"],
        )
    return save_figure(fig, "small-prefix-cache-outcomes")


def large_prefix_chart() -> list[Path]:
    prefix_kb, direct_s, cache_s, _saved_s = wrapper_ladder()
    fig, ax = plt.subplots(figsize=(8.9, 5.35), constrained_layout=False)
    annotate_title(fig, "Flashcache savings grow as reusable context grows", "gpt-oss-20b GGUF, seven Printy turns, synthetic stable-prefix ladder")
    apply_standard_layout(fig)
    ax.plot(prefix_kb, direct_s, color=COLORS["direct"], marker="o", linewidth=2.4, label="Direct full prompt")
    ax.plot(prefix_kb, cache_s, color=COLORS["cache"], marker="o", linewidth=2.4, label="Flashcache wrapper")
    ax.set_xticks(prefix_kb, [f"{value:.0f}KB" for value in prefix_kb])
    ax.set_ylabel("Prompt-eval seconds across seven turns")
    ax.set_xlabel("Reusable stable prefix")
    ax.set_ylim(0, max(direct_s) * 1.24)
    finish_axes(ax, FuncFormatter(seconds_label))
    ax.legend(loc="upper left", ncols=2)
    for x, direct, cached in zip(prefix_kb, direct_s, cache_s):
        ax.text(x, direct + 3.0, seconds_label(direct), ha="center", va="bottom", fontsize=9, color=COLORS["direct"])
        ax.text(x, cached - 4.0, seconds_label(cached), ha="center", va="top", fontsize=9, color=COLORS["cache"])
    return save_figure(fig, "large-prefix-flashcache-ladder")


def slot_size_chart() -> list[Path]:
    prefix_kb, slot_mb = slot_size_ladder()
    fig, ax = plt.subplots(figsize=(8.9, 5.35), constrained_layout=False)
    annotate_title(fig, "Saved slot blobs get large quickly", "gpt-oss-20b GGUF llama.cpp slot files for reusable prefixes")
    apply_standard_layout(fig)
    ax.plot(prefix_kb, slot_mb, color=COLORS["accent"], marker="o", linewidth=2.6)
    ax.fill_between(prefix_kb, slot_mb, color=COLORS["accent"], alpha=0.12)
    ax.set_xticks(prefix_kb, [f"{value:.1f}KB" if value < 10 else f"{value:.0f}KB" for value in prefix_kb])
    ax.set_ylabel("Slot file size on SSD")
    ax.set_xlabel("Reusable stable prefix")
    ax.set_ylim(0, max(slot_mb) * 1.2)
    finish_axes(ax, FuncFormatter(mb_label))
    for x, y in zip(prefix_kb, slot_mb):
        ax.text(x, y + 12, f"{y:.1f}MB", ha="center", va="bottom", fontsize=9, color=COLORS["accent"])
    return save_figure(fig, "slot-file-size-ladder")


def gains_projection_chart() -> list[Path]:
    prefix_kb, direct_s, cache_s, _saved_s = wrapper_ladder()
    target_x = 128.0
    direct_projection = linear_projection(prefix_kb, direct_s, target_x)
    cache_projection = linear_projection(prefix_kb, cache_s, target_x)
    metal_target = direct_projection * 0.75

    fig, ax = plt.subplots(figsize=(7.2, 4.1), constrained_layout=False)
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.165, top=0.765)
    annotate_title(
        fig,
        "Flashcache gains and projection target",
        "Measured gpt-oss-20b prompt-eval time over seven Printy turns; 128KB is a linear projection.",
    )

    measured_x = prefix_kb
    projected_x = [prefix_kb[-1], target_x]
    ax.axvspan(prefix_kb[-1], target_x, color="#f5f5f5", zorder=0)
    ax.axvline(prefix_kb[-1], color=COLORS["muted"], linestyle="--", linewidth=0.8)
    ax.text(prefix_kb[-1] + 2.0, 181, "Projection boundary", rotation=90, va="top", ha="left", fontsize=7.5, color=COLORS["muted"])
    ax.plot(measured_x, direct_s, color=COLORS["direct"], marker="o", linewidth=1.9, label="Direct full prompt")
    ax.plot(measured_x, cache_s, color=COLORS["cache"], marker="o", linewidth=1.9, label="Flashcache wrapper")
    ax.plot(projected_x, [direct_s[-1], direct_projection], color=COLORS["direct"], marker="o", linewidth=1.7, linestyle=(0, (4, 3)), label="Linear projection")
    ax.plot(projected_x, [cache_s[-1], cache_projection], color=COLORS["cache"], marker="o", linewidth=1.7, linestyle=(0, (4, 3)))
    ax.plot(projected_x, [cache_s[-1], metal_target], color=COLORS["target"], marker="o", linewidth=1.5, linestyle=(0, (2, 3)), label="Metal target")
    ax.set_xticks([16, 32, 64, 128], ["16KB", "32KB", "64KB", "128KB"])
    ax.set_xlim(10, 134)
    ax.set_ylim(0, 190)
    ax.set_ylabel("Prompt-eval seconds across seven turns")
    ax.set_xlabel("Reusable stable prefix")
    finish_axes(ax, FuncFormatter(seconds_label))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.19), ncols=4, columnspacing=1.0, handlelength=1.8)
    ax.annotate(
        f"{direct_projection - cache_projection:.1f}s projected saved",
        xy=(128, cache_projection),
        xytext=(78, 136),
        arrowprops={"arrowstyle": "-", "color": COLORS["muted"], "lw": 0.8},
        fontsize=7.5,
        color=COLORS["muted"],
    )
    ax.annotate(
        "target from partial restore + prefetch",
        xy=(128, metal_target),
        xytext=(72, 98),
        arrowprops={"arrowstyle": "-", "color": COLORS["muted"], "lw": 0.8},
        fontsize=7.5,
        color=COLORS["muted"],
    )

    fig.text(
        0.02,
        0.025,
        "Source: docs/assets/benchmark-graphs/chart-data.json. Projection is directional and should be replaced by measured 128KB data when available.",
        fontsize=7.5,
        color=COLORS["muted"],
        family="monospace",
    )
    return save_figure(fig, "flashcache-gains-projection")


def main() -> int:
    configure_style()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_chart_data()
    written: list[Path] = []
    for chart in [
        paper_evidence_chart,
        warm_restart_chart,
        exact_repeat_chart,
        small_prefix_chart,
        large_prefix_chart,
        slot_size_chart,
        gains_projection_chart,
    ]:
        written.extend(chart())
    written.append(OUT_DIR / "chart-data.json")
    for path in sorted(written):
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
