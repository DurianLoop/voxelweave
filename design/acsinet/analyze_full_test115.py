from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from acsinet.metrics import evaluate_consistency_method, summarize_consistency


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docx" / "experiment_notes" / "acsinet_3d_consistency"


@dataclass(frozen=True)
class MethodSpec:
    method: str
    display: str
    package: str
    run: str
    source: str
    prefix: str = "diff_"

    @property
    def run_dir(self) -> Path:
        return ROOT / self.package / "runs" / self.run


METHODS = [
    MethodSpec("i3net", "I3Net", "ixi_i3net", "full_test115_stable", "published baseline rerun"),
    MethodSpec("acsinet", "ACSI-Net", "acsinet", "full_test115", "ours"),
    MethodSpec("smamba_unet", "SMamba-UNet", "ixi_smamba_unet_2p5d", "full_test115", "strong local baseline"),
    MethodSpec("hat", "HAT", "ixi_hat_2p5d", "full_test115", "strong local baseline"),
    MethodSpec("swinir", "SwinIR", "ixi_swinir_2p5d", "full_test115", "strong local baseline"),
    MethodSpec("acvtt", "ACVTT", "ixi_acvtt_2p5d", "full_test115_b64", "public architecture adapted"),
    MethodSpec("arssr", "ARSSR", "ixi_arssr", "full_test115", "published baseline adapted"),
    MethodSpec("cycleinr", "CycleINR", "ixi_cycleinr", "full_test115", "published baseline adapted"),
]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict]) -> None:
    ensure_dir(path.parent)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _format_float(value: object, digits: int = 4) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def _markdown_table(rows: list[dict], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join(lines)


def collect_summary_table() -> list[dict]:
    rows: list[dict] = []

    acsi_summary = ROOT / "acsinet" / "runs" / "full_test115" / "metrics" / "summary_metrics.csv"
    for row in _read_csv(acsi_summary):
        if row["method"] in {"linear", "cubic"}:
            rows.append(
                {
                    "method": row["method"],
                    "display": row["method"].title(),
                    "package": "acsinet",
                    "run": "full_test115",
                    "cases": int(row["cases"]),
                    "psnr": float(row["psnr_mean"]),
                    "ssim": float(row["ssim_mean"]),
                    "mae": float(row["mae_mean"]),
                    "mse": float(row["mse_mean"]),
                    "ncc": float(row["ncc_mean"]),
                    "source": "interpolation baseline",
                }
            )

    for spec in METHODS:
        path = spec.run_dir / "metrics" / "summary_metrics.csv"
        if not path.exists():
            continue
        candidates = [row for row in _read_csv(path) if row["method"] not in {"linear", "cubic"}]
        if not candidates:
            continue
        row = candidates[0]
        rows.append(
            {
                "method": spec.method,
                "display": spec.display,
                "package": spec.package,
                "run": spec.run,
                "cases": int(row["cases"]),
                "psnr": float(row["psnr_mean"]),
                "ssim": float(row["ssim_mean"]),
                "mae": float(row["mae_mean"]),
                "mse": float(row["mse_mean"]),
                "ncc": float(row["ncc_mean"]),
                "source": spec.source,
            }
        )
    return sorted(rows, key=lambda item: item["psnr"], reverse=True)


def collect_win_rates() -> list[dict]:
    metric_specs = [
        ("psnr", "higher"),
        ("ssim", "higher"),
        ("mae", "lower"),
        ("mse", "lower"),
        ("ncc", "higher"),
    ]
    rows = _read_csv(ROOT / "acsinet" / "runs" / "full_test115" / "metrics" / "per_case_metrics.csv")
    by_case: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        by_case.setdefault(row["case"], {})[row["method"]] = row

    out: list[dict] = []
    for metric, direction in metric_specs:
        for opponent in ["linear", "cubic"]:
            wins = 0
            ties = 0
            valid = 0
            for case_rows in by_case.values():
                if "acsinet" not in case_rows or opponent not in case_rows:
                    continue
                valid += 1
                a = float(case_rows["acsinet"][metric])
                b = float(case_rows[opponent][metric])
                if a == b:
                    ties += 1
                elif (direction == "higher" and a > b) or (direction == "lower" and a < b):
                    wins += 1
            out.append(
                {
                    "metric": metric,
                    "direction": direction,
                    "opponent": opponent,
                    "wins": wins,
                    "ties": ties,
                    "valid_cases": valid,
                    "win_rate": wins / valid if valid else 0.0,
                }
            )
    return out


def collect_acsi_3d_win_rates() -> list[dict]:
    metric_specs = [
        ("zge", "lower"),
        ("zle", "lower"),
        ("edge_z_error", "lower"),
        ("interslice_ncc_mae", "lower"),
    ]
    rows = _read_csv(ROOT / "acsinet" / "runs" / "full_test115" / "metrics" / "per_case_3d_consistency.csv")
    by_case: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        by_case.setdefault(row["case"], {})[row["method"]] = row

    out: list[dict] = []
    for metric, direction in metric_specs:
        for opponent in ["linear", "cubic"]:
            wins = 0
            ties = 0
            valid = 0
            for case_rows in by_case.values():
                if "acsinet" not in case_rows or opponent not in case_rows:
                    continue
                valid += 1
                a = float(case_rows["acsinet"][metric])
                b = float(case_rows[opponent][metric])
                if a == b:
                    ties += 1
                elif direction == "lower" and a < b:
                    wins += 1
            out.append(
                {
                    "metric": metric,
                    "direction": direction,
                    "opponent": opponent,
                    "wins": wins,
                    "ties": ties,
                    "valid_cases": valid,
                    "win_rate": wins / valid if valid else 0.0,
                }
            )
    return out


def compute_cross_method_consistency() -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    acsi_metrics = ROOT / "acsinet" / "runs" / "full_test115" / "metrics"
    existing = acsi_metrics / "per_case_3d_consistency.csv"
    if existing.exists():
        rows.extend(_read_csv(existing))

    for spec in METHODS:
        if spec.method == "acsinet":
            continue
        gt_dir = spec.run_dir / "eval_inputs" / "gt"
        pred_dir = spec.run_dir / "model_outputs"
        if not gt_dir.exists() or not pred_dir.exists():
            continue
        method_rows = evaluate_consistency_method(gt_dir, pred_dir, spec.prefix, spec.method)
        rows.extend(method_rows)

    # Normalize all numeric values through csv-friendly plain dicts.
    normalized = [{key: value for key, value in row.items()} for row in rows]
    return normalized, summarize_consistency(normalized)


def write_summary_markdown(
    summary_rows: list[dict],
    win_rows: list[dict],
    win3d_rows: list[dict],
    consistency_summary: list[dict],
    *,
    cross_method_3d: bool,
) -> None:
    compact = []
    for row in summary_rows:
        compact.append(
            {
                "Method": row["display"],
                "Cases": row["cases"],
                "PSNR": _format_float(row["psnr"]),
                "SSIM": _format_float(row["ssim"]),
                "MAE": _format_float(row["mae"]),
                "NCC": _format_float(row["ncc"]),
                "Run": row["run"],
            }
        )

    win_compact = [
        {
            "Metric": row["metric"],
            "Opponent": row["opponent"],
            "Wins": f"{row['wins']}/{row['valid_cases']}",
            "Rate": _format_float(row["win_rate"], 3),
        }
        for row in win_rows + win3d_rows
    ]

    consistency_by_method = {row["method"]: row for row in consistency_summary}
    consistency_compact = []
    for method in ["i3net", "acsinet", "smamba_unet", "hat", "swinir", "linear", "cubic"]:
        row = consistency_by_method.get(method)
        if not row:
            continue
        consistency_compact.append(
            {
                "Method": method,
                "Cases": row["cases"],
                "ZGE": _format_float(row["zge_mean"]),
                "ZLE": _format_float(row["zle_mean"]),
                "EdgeZ": _format_float(row["edge_z_error_mean"]),
                "NCC-z-MAE": _format_float(row["interslice_ncc_mae_mean"]),
            }
        )

    consistency_heading = (
        "## 3D Consistency Across Available Neural Methods"
        if cross_method_3d
        else "## 3D Consistency From ACSI-Net Run"
    )
    consistency_note = (
        "- This 3D table was recomputed for available neural baselines with the same metrics."
        if cross_method_3d
        else "- This 3D table currently compares ACSI-Net with the paired linear/cubic interpolation baselines from the ACSI-Net run."
    )

    lines = [
        "# ACSI-Net IXI full_test115 Story Table",
        "",
        "## Reconstruction Positioning",
        "",
        _markdown_table(compact, ["Method", "Cases", "PSNR", "SSIM", "MAE", "NCC", "Run"]),
        "",
        "## ACSI-Net Per-Case Wins",
        "",
        _markdown_table(win_compact, ["Metric", "Opponent", "Wins", "Rate"]),
        "",
        consistency_heading,
        "",
        consistency_note,
        "",
        _markdown_table(consistency_compact, ["Method", "Cases", "ZGE", "ZLE", "EdgeZ", "NCC-z-MAE"]),
        "",
        "## Interpretation",
        "",
        "- ACSI-Net is not the reconstruction SOTA on IXI-T2 x4 because I3Net remains clearly stronger.",
        "- ACSI-Net is nevertheless a credible method candidate: it beats linear and cubic on every full_test115 case for all main reconstruction metrics.",
        "- Its central story should be anatomy-consistent volume recovery, supported by lower z-gradient, z-Laplacian, edge-z, and inter-slice NCC mismatch.",
        "- The next evidence gap is visual: sagittal/coronal panels should show why lower z-axis errors matter anatomically.",
    ]
    (OUT_DIR / "ixi_full_test115_story_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_experiment_design_note() -> None:
    text = """# ACSI-Net Paper Story and Experiment Design

## Core Story

ACSI-Net should not be framed as a generic slice-wise super-resolution network.
The paper story is: through-plane MRI interpolation should recover an anatomically coherent 3D volume, not merely maximize isolated 2D slice fidelity.

The strongest claim supported by the current IXI-T2 x4 full_test115 result is:

> ACSI-Net improves z-axis structural coherence while remaining competitive with strong 2.5D baselines, and it substantially outperforms interpolation baselines on both slice fidelity and 3D consistency.

The claim should not be:

> ACSI-Net is the overall SOTA on every reconstruction metric.

I3Net is still stronger on IXI full_test115 PSNR/SSIM, so the paper should use I3Net as the reconstruction upper baseline and ACSI-Net as the anatomy-consistency method.

## Hypotheses

1. Slice-level PSNR/SSIM are insufficient to describe through-plane interpolation quality.
2. Group prediction of all intermediate slices improves volume-level continuity versus independent slice prediction.
3. z-gradient, z-Laplacian, and edge-z losses reduce anatomical discontinuities.
4. The benefit is visible in sagittal/coronal reformats and z-profile plots.
5. ACSI-Net can be slightly below I3Net in PSNR while still contributing a distinct clinically meaningful axis: anatomical coherence.

## Main IXI-T2 x4 Experiment

Dataset:

- IXI-T2
- x4 through-plane interpolation
- full_test115 split
- 115 test volumes

Primary reconstruction metrics:

- PSNR
- SSIM
- MAE
- MSE
- NCC

Primary 3D consistency metrics:

- ZGE: z-gradient error
- ZLE: z-Laplacian error
- EdgeZ: edge continuity error along z
- NCC-z-MAE: mismatch of adjacent-slice NCC profiles

Required table groups:

1. Linear and cubic interpolation baselines.
2. Published or strong neural baselines: I3Net, HAT, SMamba-UNet, SwinIR, ACVTT, ARSSR, CycleINR.
3. ACSI-Net.

## Figure Plan

Figure 1: Motivation

- Show axial slices alone look acceptable.
- Show sagittal/coronal view reveals z-axis discontinuity.
- Use linear or cubic as the failure example.

Figure 2: Method

- Sparse anchors S0 and S4.
- Linear coarse group C1/C2/C3.
- Phase maps P1/P2/P3.
- Group decoder producing S1/S2/S3.
- Shallow 3D z-context refinement.
- Anatomy consistency losses.

Figure 3: IXI full_test115 quantitative result

- Reconstruction table.
- 3D consistency table.
- Per-case win rate bar chart for ACSI-Net vs linear/cubic.

Figure 4: Sagittal/coronal QC

- Choose best, median, and worst cases by ACSI-Net z-consistency gain.
- Columns: GT, Linear, I3Net, ACSI-Net, error map.
- Add z-profile line plot through a high-gradient anatomical boundary.

Figure 5: Ablation

- Full ACSI-Net.
- w/o z-gradient loss.
- w/o z-Laplacian loss.
- w/o edge-z loss.
- w/o z-refine.
- optional: single-slice output instead of group output.

## Experiment Order

1. Finish IXI full_test115 story package.
2. Compute 3D consistency for available full_test115 neural baselines without retraining.
3. Generate visual QC cases.
4. Only then train ablations.
5. Extend the same evaluation to fastMRI and NingXia if existing predictions are available.

## Acceptance Criteria

The ACSI-Net story is strong enough for a paper section if:

- ACSI-Net beats linear/cubic on all reconstruction metrics over full_test115.
- ACSI-Net beats linear/cubic on at least 3/4 3D consistency metrics.
- ACSI-Net remains competitive with HAT/SMamba/SwinIR.
- I3Net remains acknowledged as a stronger reconstruction baseline.
- Visual QC demonstrates fewer z-axis discontinuities in sagittal/coronal views.

## Current Status

IXI full_test115 already satisfies the first two criteria. The next missing piece is visual QC and cross-neural-baseline 3D consistency.
"""
    (OUT_DIR / "paper_story_and_experiment_design_2026-07-09.md").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-cross-method-3d",
        action="store_true",
        help="Recompute 3D consistency for all available neural baselines. This can take several minutes.",
    )
    args = parser.parse_args()

    ensure_dir(OUT_DIR)
    summary_rows = collect_summary_table()
    win_rows = collect_win_rates()
    win3d_rows = collect_acsi_3d_win_rates()

    _write_csv(OUT_DIR / "ixi_full_test115_reconstruction_summary.csv", summary_rows)
    _write_csv(OUT_DIR / "ixi_full_test115_acsi_reconstruction_win_rates.csv", win_rows)
    _write_csv(OUT_DIR / "ixi_full_test115_acsi_3d_win_rates.csv", win3d_rows)

    if args.with_cross_method_3d:
        consistency_rows, consistency_summary = compute_cross_method_consistency()
        _write_csv(OUT_DIR / "per_case_3d_consistency_all_available_methods.csv", consistency_rows)
        _write_csv(OUT_DIR / "ixi_full_test115_3d_consistency_all_available_methods.csv", consistency_summary)
    else:
        consistency_rows = _read_csv(ROOT / "acsinet" / "runs" / "full_test115" / "metrics" / "per_case_3d_consistency.csv")
        consistency_summary = _read_csv(ROOT / "acsinet" / "runs" / "full_test115" / "metrics" / "summary_3d_consistency.csv")

    write_summary_markdown(summary_rows, win_rows, win3d_rows, consistency_summary, cross_method_3d=args.with_cross_method_3d)
    write_experiment_design_note()
    print(f"Wrote ACSI-Net full_test115 analysis package to {OUT_DIR}")


if __name__ == "__main__":
    main()
