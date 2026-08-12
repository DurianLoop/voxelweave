from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "rasinet" / "runs" / "posthoc_uncertainty"
REPORT_ROOT = ROOT / "rasinet" / "reports" / "posthoc_uncertainty"
PAPER_ROOT = ROOT / "rasinet" / "paper"
FIGURE_DIR = PAPER_ROOT / "figures"
SOURCE_DIR = FIGURE_DIR / "source_data"

PROFILES = {
    "full_test115": "IXI T2",
    "fastmri_full": "fastMRI-brain T2",
    "ningxia_cv": "NingXia T2 CV",
}

METHOD_DISPLAY = {
    "i3net": "I3Net",
    "hat": "HAT",
    "swinir": "SwinIR",
    "acsinet": "ACSI",
}
METHOD_ORDER = {"I3Net": 0, "HAT": 1, "SwinIR": 2, "ACSI": 3}
DATASET_ORDER = {"IXI T2": 0, "fastMRI-brain T2": 1, "NingXia T2 CV": 2}
PROXY_ORDER = {
    "Baseline disagreement": 0,
    "Residual to linear": 1,
    "Residual to cubic": 2,
    "TTA variance": 3,
}


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict]) -> None:
    _ensure_dir(path.parent)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _to_float(row: dict, key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else float("nan")


def _split_method(method: str) -> tuple[str, str]:
    if "__" not in method:
        return method, ""
    return tuple(method.split("__", 1))  # type: ignore[return-value]


def _display_method(method: str) -> str:
    return METHOD_DISPLAY.get(method, method)


def _save_figure(fig: plt.Figure, stem: str) -> list[Path]:
    _ensure_dir(FIGURE_DIR)
    paths = [FIGURE_DIR / f"{stem}.png", FIGURE_DIR / f"{stem}.pdf"]
    fig.savefig(paths[0], dpi=240, bbox_inches="tight")
    fig.savefig(paths[1], bbox_inches="tight")
    plt.close(fig)
    return paths


def plot_framework() -> list[Path]:
    fig, ax = plt.subplots(figsize=(12.0, 4.6))
    ax.axis("off")
    boxes = [
        (0.04, 0.58, 0.18, 0.22, "Existing outputs\nI3Net / HAT / SwinIR / ACSI"),
        (0.04, 0.20, 0.18, 0.22, "Coarse references\nlinear / cubic"),
        (0.34, 0.39, 0.20, 0.25, "Post-hoc proxy\nbaseline disagreement"),
        (0.66, 0.58, 0.18, 0.22, "Voxel / slice\nuncertainty map"),
        (0.66, 0.20, 0.18, 0.22, "Risk coverage\nfailure ranking"),
    ]
    for x, y, w, h, text in boxes:
        patch = plt.Rectangle((x, y), w, h, fc="#f4f6f8", ec="#243447", lw=1.5)
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=11)
    arrows = [
        ((0.22, 0.69), (0.34, 0.53)),
        ((0.22, 0.31), (0.34, 0.49)),
        ((0.54, 0.52), (0.66, 0.69)),
        ((0.54, 0.48), (0.66, 0.31)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.8, "color": "#243447"})
    ax.text(
        0.5,
        0.92,
        "Reliability layer for MRI through-plane interpolation",
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.06,
        "Training-free main path: read existing predictions, estimate uncertainty, rank risk.",
        ha="center",
        va="center",
        fontsize=10,
        color="#4b5563",
    )
    return _save_figure(fig, "figure1_framework")


def plot_risk_coverage() -> list[Path]:
    source_rows = []
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.5), sharex=True)
    for ax, (profile, dataset) in zip(axes, PROFILES.items()):
        path = RUN_ROOT / profile / "metrics" / "risk_coverage_posthoc.csv"
        grouped: dict[str, dict[float, list[float]]] = defaultdict(lambda: defaultdict(list))
        for row in _read_csv(path):
            method, proxy = _split_method(row["method"])
            if proxy != "baseline_disagreement":
                continue
            grouped[_display_method(method)][_to_float(row, "coverage")].append(_to_float(row, "retained_mae"))
        for method in sorted(grouped, key=lambda name: METHOD_ORDER.get(name, 99)):
            coverages = sorted(grouped[method], reverse=True)
            retained = [float(np.nanmean(grouped[method][coverage])) for coverage in coverages]
            ax.plot(coverages, retained, marker="o", lw=2.0, ms=4, label=method)
            for coverage, mae in zip(coverages, retained):
                source_rows.append({"Dataset": dataset, "Method": method, "Coverage": coverage, "Retained MAE": mae})
        ax.invert_xaxis()
        ax.set_title(dataset)
        ax.set_xlabel("Coverage kept")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("Retained MAE")
    axes[-1].legend(loc="upper right", fontsize=8)
    fig.suptitle("Risk-coverage with baseline disagreement", fontsize=14, fontweight="bold")
    fig.tight_layout()
    _write_csv(SOURCE_DIR / "figure2_risk_coverage.csv", source_rows)
    return _save_figure(fig, "figure2_risk_coverage")


def plot_masked_vs_all() -> list[Path]:
    rows = _read_csv(REPORT_ROOT / "paper_experiments" / "masked_bootstrap_ci_by_method_proxy.csv")
    by_key: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
    for row in rows:
        if row["proxy"] != "baseline_disagreement":
            continue
        if row["metric"] not in {"pixel_corr_all", "pixel_corr_nonzero"}:
            continue
        dataset = PROFILES[row["profile"]]
        by_key[(dataset, row["method"])][row["metric"]] = float(row["mean"])
    source_rows = []
    for (dataset, method), values in by_key.items():
        source_rows.append(
            {
                "Dataset": dataset,
                "Method": method,
                "All-pixel corr": values.get("pixel_corr_all", float("nan")),
                "Nonzero corr": values.get("pixel_corr_nonzero", float("nan")),
            }
        )
    source_rows.sort(key=lambda row: (DATASET_ORDER.get(row["Dataset"], 99), METHOD_ORDER.get(row["Method"], 99)))
    x = np.arange(len(source_rows))
    width = 0.38
    fig, ax = plt.subplots(figsize=(13.0, 4.8))
    ax.bar(x - width / 2, [row["All-pixel corr"] for row in source_rows], width, label="All pixels", color="#4c78a8")
    ax.bar(x + width / 2, [row["Nonzero corr"] for row in source_rows], width, label="Nonzero mask", color="#f58518")
    labels = [f"{row['Dataset']}\n{row['Method']}" for row in source_rows]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Pixel error-uncertainty corr")
    ax.set_title("All-pixel vs nonzero-mask correlation")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    _write_csv(SOURCE_DIR / "figure3_masked_vs_all.csv", source_rows)
    return _save_figure(fig, "figure3_masked_vs_all")


def plot_proxy_ablation() -> list[Path]:
    rows = _read_csv(PAPER_ROOT / "tables" / "table_proxy_ablation.csv")
    rows.sort(key=lambda row: (DATASET_ORDER.get(row["Dataset"], 99), PROXY_ORDER.get(row["Proxy"], 99)))
    datasets = list(PROFILES.values())
    proxies = ["Baseline disagreement", "Residual to linear", "Residual to cubic", "TTA variance"]
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 4.8), sharey=False)
    colors = {"Pixel Corr": "#4c78a8", "Slice Corr": "#54a24b"}
    for ax, metric in zip(axes, ["Pixel Corr", "Slice Corr"]):
        x = np.arange(len(datasets))
        width = 0.18
        for idx, proxy in enumerate(proxies):
            values = []
            for dataset in datasets:
                row = next((item for item in rows if item["Dataset"] == dataset and item["Proxy"] == proxy), None)
                values.append(float(row[metric]) if row else float("nan"))
            offset = (idx - 1.5) * width
            ax.bar(x + offset, values, width, label=proxy)
        ax.set_xticks(x)
        ax.set_xticklabels(datasets, rotation=20, ha="right")
        ax.set_title(metric)
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Error-uncertainty corr")
    axes[1].legend(loc="upper right", fontsize=8)
    fig.suptitle("SwinIR proxy ablation", fontsize=14, fontweight="bold")
    fig.tight_layout()
    _write_csv(SOURCE_DIR / "figure4_proxy_ablation.csv", rows)
    return _save_figure(fig, "figure4_proxy_ablation")


def plot_calibration_bins() -> list[Path]:
    source_rows = []
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.3), sharex=True)
    for ax, (profile, dataset) in zip(axes, PROFILES.items()):
        rows = _read_csv(RUN_ROOT / profile / "metrics" / "calibration_bins_posthoc.csv")
        grouped: dict[int, dict[str, list[float]]] = defaultdict(lambda: {"unc": [], "err": []})
        for row in rows:
            if row["method"] != "swinir__baseline_disagreement":
                continue
            bin_id = int(row["bin"])
            grouped[bin_id]["unc"].append(_to_float(row, "mean_uncertainty"))
            grouped[bin_id]["err"].append(_to_float(row, "mean_abs_error"))
        bins = sorted(grouped)
        errors = [float(np.nanmean(grouped[idx]["err"])) for idx in bins]
        ax.plot(bins, errors, marker="o", lw=2.0)
        for idx, err in zip(bins, errors):
            source_rows.append({"Dataset": dataset, "Method": "SwinIR", "Proxy": "Baseline disagreement", "Bin": idx, "Mean abs error": err})
        ax.set_title(dataset)
        ax.set_xlabel("Uncertainty decile")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("Mean absolute error")
    fig.suptitle("Calibration-style monotonicity by uncertainty decile", fontsize=14, fontweight="bold")
    fig.tight_layout()
    _write_csv(SOURCE_DIR / "supp_calibration_bins.csv", source_rows)
    return _save_figure(fig, "supp_calibration_bins")


def plot_visual_qc_contact_sheet() -> list[Path]:
    visual_dir = REPORT_ROOT / "full_test115" / "figures" / "visual_qc"
    selected = [
        "high_risk_high_error_01_IXI014-HH-1236-T2.png",
        "low_risk_low_error_01_IXI260-HH-1805-T2.png",
        "low_uncertainty_high_error_01_IXI072-HH-2324-T2.png",
        "high_uncertainty_low_error_01_IXI482-HH-2178-T2.png",
    ]
    titles = [
        "High risk / high error",
        "Low risk / low error",
        "Low uncertainty / high error",
        "High uncertainty / low error",
    ]
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 7.5))
    for ax, name, title in zip(axes.reshape(-1), selected, titles):
        img = mpimg.imread(visual_dir / name)
        ax.imshow(img)
        ax.set_title(title, fontsize=10)
        ax.axis("off")
    fig.suptitle("Representative visual QC panels", fontsize=14, fontweight="bold")
    fig.tight_layout()
    _write_csv(SOURCE_DIR / "figure5_visual_qc_cases.csv", [{"Panel": title, "File": name} for title, name in zip(titles, selected)])
    return _save_figure(fig, "figure5_visual_qc")


def write_figure_index(paths: list[Path]) -> None:
    lines = [
        "# Paper figure index",
        "",
        "All figures are generated by `rasinet/paper_figures.py`.",
        "",
    ]
    for path in paths:
        if path.suffix.lower() == ".png":
            lines.append(f"- `{path.name}`")
    (FIGURE_DIR / "figure_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_paper_figures() -> list[Path]:
    _ensure_dir(FIGURE_DIR)
    _ensure_dir(SOURCE_DIR)
    paths: list[Path] = []
    paths.extend(plot_framework())
    paths.extend(plot_risk_coverage())
    paths.extend(plot_masked_vs_all())
    paths.extend(plot_proxy_ablation())
    paths.extend(plot_visual_qc_contact_sheet())
    paths.extend(plot_calibration_bins())
    write_figure_index(paths)
    return paths


def main() -> None:
    paths = build_paper_figures()
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
