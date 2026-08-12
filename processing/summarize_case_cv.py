from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "docx" / "experiment_notes"
MAIN_METRICS = ["psnr", "ssim", "mae", "mse", "ncc"]
METHOD_LABELS = {
    "linear": "Linear",
    "cubic": "Cubic",
    "arssr": "ArSSR",
    "cycleinr": "CycleINR",
    "swinir": "SwinIR 2.5D",
    "saint": "SAINT",
    "resunet": "ResUNet residual",
    "i3net": "I3Net",
    "hat": "HAT 2.5D",
    "smamba_unet": "SMamba-UNet 2.5D",
    "gan_2p5d": "Pix2Pix-GAN 2.5D",
    "acvtt": "ACVTT",
    "ressrdiff": "Res-SRDiff",
}
METHOD_ORDER = ["linear", "cubic", "arssr", "cycleinr", "resunet", "gan_2p5d", "acvtt", "ressrdiff", "i3net", "smamba_unet", "swinir", "hat", "saint"]


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _float(value: str | None) -> float:
    if value in {"", "nan", "NaN", None}:
        return float("nan")
    if value in {"inf", "Infinity"}:
        return float("inf")
    return float(value)


def _mean(values: list[float]) -> float:
    finite = [v for v in values if math.isfinite(v)]
    return sum(finite) / len(finite) if finite else float("nan")


def _std(values: list[float]) -> float:
    finite = [v for v in values if math.isfinite(v)]
    if len(finite) < 2:
        return float("nan")
    mu = _mean(finite)
    return math.sqrt(sum((v - mu) ** 2 for v in finite) / (len(finite) - 1))


def _fmt(value: float) -> str:
    if math.isnan(value):
        return "nan"
    if math.isinf(value):
        return "inf"
    return f"{value:.4f}"


def _collect_run(run_root: Path, model_name: str, out_rows: list[dict[str, str]], target_profile: str) -> None:
    for fold_dir in sorted(run_root.glob("fold_*")):
        candidates = [fold_dir / "metrics" / "summary_metrics.csv"]
        candidates.extend(sorted(fold_dir.glob("*/metrics/summary_metrics.csv")))
        for summary in candidates:
            if not summary.exists():
                continue
            profile = summary.parents[1].name if summary.parent.parent != fold_dir else ""
            if target_profile and profile != target_profile:
                continue
            for row in _read_csv(summary):
                normalized = {
                    "fold": fold_dir.name,
                    "profile": profile,
                    "run_root": str(run_root),
                    "model_run": model_name,
                    "method": row["method"],
                    "cases": row.get("cases", ""),
                }
                for metric in MAIN_METRICS:
                    normalized[f"{metric}_mean"] = row.get(f"{metric}_mean", "")
                out_rows.append(normalized)


def summarize(run_roots: list[tuple[str, Path]], out_dir: Path, table_title: str, profile: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fold_rows: list[dict[str, str]] = []
    for model_name, run_root in run_roots:
        _collect_run(run_root, model_name, fold_rows, profile)

    per_fold_path = out_dir / "ningxia_case_cv_per_fold.csv"
    with per_fold_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["fold", "profile", "run_root", "model_run", "method", "cases"] + [
            f"{metric}_mean" for metric in MAIN_METRICS
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(fold_rows)

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in fold_rows:
        grouped[row["method"]].append(row)

    summary_rows = []
    for method in sorted(grouped):
        unique_by_fold = {}
        for row in grouped[method]:
            unique_by_fold.setdefault(row["fold"], row)
        rows = list(unique_by_fold.values())
        out = {"method": method, "folds": str(len({r["fold"] for r in rows}))}
        for metric in MAIN_METRICS:
            values = [_float(r[f"{metric}_mean"]) for r in rows]
            out[f"{metric}_mean"] = _fmt(_mean(values))
            out[f"{metric}_std"] = _fmt(_std(values))
        summary_rows.append(out)

    summary_path = out_dir / "ningxia_case_cv_summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["method", "folds"] + [f"{metric}_{stat}" for metric in MAIN_METRICS for stat in ["mean", "std"]]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    md_lines = [f"# {table_title}", ""]
    md_lines.append("| Method | Folds | PSNR mean | SSIM mean | MAE mean | MSE mean | NCC mean |")
    md_lines.append("|---|---:|---:|---:|---:|---:|---:|")
    rows_by_method = {row["method"]: row for row in summary_rows}
    for method in METHOD_ORDER:
        if method not in rows_by_method:
            continue
        row = rows_by_method[method]
        md_lines.append(
            "| "
            + " | ".join(
                [
                    METHOD_LABELS.get(method, method),
                    row["folds"],
                    row["psnr_mean"],
                    row["ssim_mean"],
                    row["mae_mean"],
                    row["mse_mean"],
                    row["ncc_mean"],
                ]
            )
            + " |"
        )
    md_lines.append("")
    md_lines.append(
        "Note: this table averages case-level CV fold means; the main table only uses PSNR / SSIM / MAE / MSE / NCC."
    )
    (out_dir / "ningxia_case_cv_summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"CV per-fold written: {per_fold_path}")
    print(f"CV summary written: {summary_path}")
    print(f"CV markdown written: {out_dir / 'ningxia_case_cv_summary.md'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize NingXia case-level CV results.")
    parser.add_argument("--saint-run-root", type=Path, default=ROOT / "ningxia_t2_saint_cv" / "runs")
    parser.add_argument("--resunet-run-root", type=Path, default=ROOT / "ningxia_t2_resunet_cv" / "runs")
    parser.add_argument("--arssr-run-root", type=Path, default=ROOT / "ningxia_t2_arssr_cv" / "runs")
    parser.add_argument("--cycleinr-run-root", type=Path, default=ROOT / "ningxia_t2_cycleinr_cv" / "runs")
    parser.add_argument("--swinir-run-root", type=Path, default=ROOT / "ningxia_t2_swinir_2p5d_cv" / "runs")
    parser.add_argument("--i3net-run-root", type=Path, default=ROOT / "ningxia_t2_i3net_cv" / "runs")
    parser.add_argument("--hat-run-root", type=Path, default=ROOT / "ningxia_t2_hat_2p5d_cv" / "runs")
    parser.add_argument("--smamba-run-root", type=Path, default=ROOT / "ningxia_t2_smamba_unet_2p5d_cv" / "runs")
    parser.add_argument("--gan-run-root", type=Path, default=ROOT / "ningxia_t2_gan_2p5d_cv" / "runs")
    parser.add_argument("--acvtt-run-root", type=Path, default=ROOT / "ningxia_t2_acvtt_2p5d_cv" / "runs")
    parser.add_argument("--ressrdiff-run-root", type=Path, default=ROOT / "ningxia_t2_ressrdiff_2p5d_cv" / "runs")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--title", default="NingXia-T2 Case-Level CV")
    parser.add_argument("--profile", default="full")
    parser.add_argument("--include-arssr", action="store_true")
    parser.add_argument("--include-cycleinr", action="store_true")
    parser.add_argument("--include-swinir", action="store_true")
    parser.add_argument("--include-i3net", action="store_true")
    parser.add_argument("--include-hat", action="store_true")
    parser.add_argument("--include-smamba", action="store_true")
    parser.add_argument("--include-gan", action="store_true")
    parser.add_argument("--include-acvtt", action="store_true")
    parser.add_argument("--include-ressrdiff", action="store_true")
    args = parser.parse_args()

    run_roots = [("saint", args.saint_run_root), ("resunet", args.resunet_run_root)]
    if args.include_arssr:
        run_roots.append(("arssr", args.arssr_run_root))
    if args.include_cycleinr:
        run_roots.append(("cycleinr", args.cycleinr_run_root))
    if args.include_swinir:
        run_roots.append(("swinir", args.swinir_run_root))
    if args.include_i3net:
        run_roots.append(("i3net", args.i3net_run_root))
    if args.include_gan:
        run_roots.append(("gan", args.gan_run_root))
    if args.include_acvtt:
        run_roots.append(("acvtt", args.acvtt_run_root))
    if args.include_ressrdiff:
        run_roots.append(("ressrdiff", args.ressrdiff_run_root))
    if args.include_smamba:
        run_roots.append(("smamba", args.smamba_run_root))
    if args.include_hat:
        run_roots.append(("hat", args.hat_run_root))
    summarize(run_roots, args.out_dir, args.title, args.profile)


if __name__ == "__main__":
    main()
