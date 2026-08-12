from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "docx" / "experiment_notes" / "multiscale_x2_x4_x6_i3net_table.md"
METRICS = ["PSNR", "SSIM", "MAE", "MSE", "NCC"]
METHOD_ORDER = ["linear", "cubic", "i3net"]
METHOD_LABELS = {"linear": "Linear", "cubic": "Cubic", "i3net": "I3Net (2024)"}
IXI_PROFILES = {"x2": "full_test115_x2_fast", "x4": "full_test115_stable", "x6": "full_test115_x6_fast"}
FASTMRI_PROFILES = {"x2": "full_x2", "x4": "full", "x6": "full_x6"}
NINGXIA_PROFILES = {"x2": "full_x2", "x4": "full", "x6": "full_x6"}


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _float(value: str | None) -> float:
    if value in {None, "", "nan", "NaN"}:
        return float("nan")
    return float(value)


def _mean(values: list[float]) -> float:
    finite = [value for value in values if math.isfinite(value)]
    return sum(finite) / len(finite) if finite else float("nan")


def _fmt(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return "pending"
    return f"{value:.4f}"


def _collect_paper_table(path: Path) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for row in _read_csv(path):
        method = row.get("method", "")
        if method not in METHOD_ORDER:
            continue
        out[method] = {metric: _float(row.get(metric)) for metric in METRICS}
    return out


def _collect_ningxia(profile: str, run_root: Path) -> dict[str, dict[str, float]]:
    grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for fold_dir in sorted(run_root.glob("fold_*")):
        summary = fold_dir / profile / "metrics" / "summary_metrics.csv"
        for row in _read_csv(summary):
            method = row.get("method", "")
            if method not in METHOD_ORDER:
                continue
            for metric in METRICS:
                grouped[method][metric].append(_float(row.get(f"{metric.lower()}_mean")))
    return {
        method: {metric: _mean(values) for metric, values in metric_values.items()}
        for method, metric_values in grouped.items()
    }


def _flat_columns() -> list[str]:
    columns = ["Scale", "Method"]
    for dataset in ["IXI-T2", "fastMRI-brain-T2", "NingXia-T2 CV"]:
        for metric in METRICS:
            columns.append(f"{dataset} {metric}")
    return columns


def build_table(ixi_root: Path, fastmri_root: Path, ningxia_root: Path) -> tuple[list[str], list[list[str]]]:
    columns = _flat_columns()
    rows: list[list[str]] = []
    for scale in ["x2", "x4", "x6"]:
        ixi = _collect_paper_table(ixi_root / IXI_PROFILES[scale] / "metrics" / "paper_table.csv")
        fastmri = _collect_paper_table(fastmri_root / FASTMRI_PROFILES[scale] / "metrics" / "paper_table.csv")
        ningxia = _collect_ningxia(NINGXIA_PROFILES[scale], ningxia_root)
        for method in METHOD_ORDER:
            row = [scale, METHOD_LABELS[method]]
            for source in [ixi, fastmri, ningxia]:
                values = source.get(method, {})
                row.extend(_fmt(values.get(metric)) for metric in METRICS)
            rows.append(row)
    return columns, rows


def write_markdown(columns: list[str], rows: list[list[str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# T2 Through-Plane Interpolation Multi-Scale Table Draft",
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.extend(
        [
            "",
            "Note: this draft currently targets the I3Net-style multi-scale block: Linear, Cubic, and I3Net over x2/x4/x6. Cells marked pending mean the corresponding run has not generated paper_table.csv or NingXia fold summaries yet.",
        ]
    )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an I3Net-like x2/x4/x6 table draft from completed runs.")
    parser.add_argument("--ixi-root", type=Path, default=ROOT / "ixi_i3net" / "runs")
    parser.add_argument("--fastmri-root", type=Path, default=ROOT / "fastmri_brain_i3net" / "runs")
    parser.add_argument("--ningxia-root", type=Path, default=ROOT / "ningxia_t2_i3net_cv" / "runs")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    columns, rows = build_table(args.ixi_root, args.fastmri_root, args.ningxia_root)
    write_markdown(columns, rows, args.out)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
