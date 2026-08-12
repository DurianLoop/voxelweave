from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ixi_diffusion.common import ensure_dir, load_nifti


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docx" / "experiment_notes" / "visual_qc" / "saint_vs_swinir"
STRIDE = 4


@dataclass(frozen=True)
class CaseSelection:
    dataset: str
    label: str
    fold: str
    case: str
    saint_psnr: float
    swinir_psnr: float
    delta_psnr: float
    saint_ssim: float
    swinir_ssim: float
    delta_ssim: float
    saint_mae: float
    swinir_mae: float
    delta_mae: float
    saint_ncc: float
    swinir_ncc: float
    delta_ncc: float
    gt_path: Path
    linear_path: Path
    saint_path: Path
    swinir_path: Path


def _read_rows(path: Path, method: str) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("method") == method]
    return {row["case"]: row for row in rows}


def _f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def _join_rows(
    saint_rows: dict[str, dict[str, str]],
    swinir_rows: dict[str, dict[str, str]],
) -> list[tuple[str, dict[str, str], dict[str, str]]]:
    common = sorted(set(saint_rows).intersection(swinir_rows))
    return [(case, saint_rows[case], swinir_rows[case]) for case in common]


def _make_selection(
    dataset: str,
    label: str,
    fold: str,
    case: str,
    saint: dict[str, str],
    swinir: dict[str, str],
    gt_path: Path,
    linear_path: Path,
    saint_path: Path,
    swinir_path: Path,
) -> CaseSelection:
    return CaseSelection(
        dataset=dataset,
        label=label,
        fold=fold,
        case=case,
        saint_psnr=_f(saint, "psnr"),
        swinir_psnr=_f(swinir, "psnr"),
        delta_psnr=_f(saint, "psnr") - _f(swinir, "psnr"),
        saint_ssim=_f(saint, "ssim"),
        swinir_ssim=_f(swinir, "ssim"),
        delta_ssim=_f(saint, "ssim") - _f(swinir, "ssim"),
        saint_mae=_f(saint, "mae"),
        swinir_mae=_f(swinir, "mae"),
        delta_mae=_f(saint, "mae") - _f(swinir, "mae"),
        saint_ncc=_f(saint, "ncc"),
        swinir_ncc=_f(swinir, "ncc"),
        delta_ncc=_f(saint, "ncc") - _f(swinir, "ncc"),
        gt_path=gt_path,
        linear_path=linear_path,
        saint_path=saint_path,
        swinir_path=swinir_path,
    )


def select_fastmri_cases() -> list[CaseSelection]:
    saint_root = ROOT / "fastmri_brain_t2_saint_expanded" / "runs" / "full"
    swinir_root = ROOT / "fastmri_brain_swinir_2p5d" / "runs" / "full"
    joined = _join_rows(
        _read_rows(saint_root / "metrics" / "per_case_metrics.csv", "saint"),
        _read_rows(swinir_root / "metrics" / "per_case_metrics.csv", "swinir"),
    )
    scored = sorted(joined, key=lambda item: _f(item[1], "psnr") - _f(item[2], "psnr"))
    picks = [
        ("small_gap", scored[0]),
        ("median_gap", scored[len(scored) // 2]),
        ("large_gap", scored[-1]),
    ]
    selections = []
    for label, (case, saint, swinir) in picks:
        selections.append(
            _make_selection(
                "fastMRI-brain-T2 expanded",
                label,
                "",
                case,
                saint,
                swinir,
                saint_root / "eval_gt" / case,
                saint_root / "baseline_outputs" / "linear" / f"linear_{case}",
                saint_root / "saint_outputs" / f"diff_{case}",
                swinir_root / "model_outputs" / f"diff_{case}",
            )
        )
    return selections


def _ningxia_joined() -> list[tuple[str, str, dict[str, str], dict[str, str]]]:
    out = []
    saint_root = ROOT / "ningxia_t2_saint_cv" / "runs"
    swinir_root = ROOT / "ningxia_t2_swinir_2p5d_cv" / "runs"
    for saint_metrics in sorted(saint_root.glob("fold_*/full/metrics/per_case_metrics.csv")):
        fold = saint_metrics.parents[2].name
        swinir_metrics = swinir_root / fold / "full" / "metrics" / "per_case_metrics.csv"
        if not swinir_metrics.exists():
            continue
        for case, saint, swinir in _join_rows(_read_rows(saint_metrics, "saint"), _read_rows(swinir_metrics, "swinir")):
            out.append((fold, case, saint, swinir))
    return out


def select_ningxia_cases() -> list[CaseSelection]:
    joined = _ningxia_joined()
    scored = sorted(joined, key=lambda item: _f(item[3], "psnr") - _f(item[2], "psnr"))
    near_tie = min(scored, key=lambda item: abs(_f(item[3], "psnr") - _f(item[2], "psnr")))
    picks = [
        ("saint_better", scored[0]),
        ("near_tie", near_tie),
        ("swinir_better", scored[-1]),
    ]
    selections = []
    for label, (fold, case, saint, swinir) in picks:
        saint_run = ROOT / "ningxia_t2_saint_cv" / "runs" / fold / "full"
        swinir_run = ROOT / "ningxia_t2_swinir_2p5d_cv" / "runs" / fold / "full"
        selections.append(
            _make_selection(
                "NingXia-T2 case-level CV",
                label,
                fold,
                case,
                saint,
                swinir,
                saint_run / "eval_gt" / case,
                saint_run / "baseline_outputs" / "linear" / f"linear_{case}",
                saint_run / "saint_outputs" / f"diff_{case}",
                swinir_run / "model_outputs" / f"diff_{case}",
            )
        )
    return selections


def _window(volume: np.ndarray) -> tuple[float, float]:
    finite = volume[np.isfinite(volume)]
    return float(np.percentile(finite, 1)), float(np.percentile(finite, 99))


def _choose_slice(gt: np.ndarray, saint: np.ndarray, swinir: np.ndarray) -> int:
    depth = min(gt.shape[2], saint.shape[2], swinir.shape[2])
    candidates = [idx for idx in range(depth) if idx % STRIDE != 0]
    if not candidates:
        candidates = list(range(depth))
    scores = [float(np.mean(np.abs(saint[:, :, idx] - swinir[:, :, idx]))) for idx in candidates]
    return int(candidates[int(np.argmax(scores))])


def _gradient_mae(pred: np.ndarray, gt: np.ndarray, z: int) -> float:
    pred_slice = pred[:, :, z]
    gt_slice = gt[:, :, z]
    pred_gx, pred_gy = np.gradient(pred_slice)
    gt_gx, gt_gy = np.gradient(gt_slice)
    return float(np.mean(np.abs(pred_gx - gt_gx) + np.abs(pred_gy - gt_gy)))


def _show(ax, image: np.ndarray, title: str, vmin: float, vmax: float, cmap: str = "gray") -> None:
    ax.imshow(np.rot90(image), cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title, fontsize=9)
    ax.axis("off")


def write_panel(selection: CaseSelection) -> dict[str, object]:
    gt, _, _ = load_nifti(selection.gt_path)
    linear, _, _ = load_nifti(selection.linear_path)
    saint, _, _ = load_nifti(selection.saint_path)
    swinir, _, _ = load_nifti(selection.swinir_path)
    z = _choose_slice(gt, saint, swinir)
    vmin, vmax = _window(gt)
    saint_err = np.abs(saint[:, :, z] - gt[:, :, z])
    swinir_err = np.abs(swinir[:, :, z] - gt[:, :, z])
    err_vmax = float(np.percentile(np.concatenate([saint_err.ravel(), swinir_err.ravel()]), 99))
    if err_vmax <= 0:
        err_vmax = 1.0

    fig, axes = plt.subplots(2, 4, figsize=(14, 7), constrained_layout=True)
    _show(axes[0, 0], linear[:, :, z], "Linear coarse", vmin, vmax)
    _show(axes[0, 1], gt[:, :, z], "GT", vmin, vmax)
    _show(axes[0, 2], saint[:, :, z], f"SAINT PSNR {selection.saint_psnr:.2f}", vmin, vmax)
    _show(axes[0, 3], swinir[:, :, z], f"SwinIR PSNR {selection.swinir_psnr:.2f}", vmin, vmax)
    _show(axes[1, 0], saint_err, "|SAINT-GT|", 0.0, err_vmax, cmap="magma")
    _show(axes[1, 1], swinir_err, "|SwinIR-GT|", 0.0, err_vmax, cmap="magma")
    _show(axes[1, 2], saint[:, :, z] - swinir[:, :, z], "SAINT - SwinIR", -err_vmax, err_vmax, cmap="coolwarm")
    _show(axes[1, 3], np.abs(saint[:, :, z] - swinir[:, :, z]), "|SAINT-SwinIR|", 0.0, err_vmax, cmap="viridis")
    fig.suptitle(
        f"{selection.dataset} / {selection.label} / {selection.fold or 'full'} / {selection.case} / z={z}",
        fontsize=11,
    )
    safe_case = selection.case.replace(".nii.gz", "").replace(".", "_")
    out_path = OUT_DIR / f"{selection.dataset.split()[0].replace('-', '_')}_{selection.label}_{selection.fold or 'full'}_{safe_case}.png"
    ensure_dir(out_path.parent)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return {
        "dataset": selection.dataset,
        "label": selection.label,
        "fold": selection.fold,
        "case": selection.case,
        "selected_slice": z,
        "saint_psnr": selection.saint_psnr,
        "swinir_psnr": selection.swinir_psnr,
        "saint_minus_swinir_psnr": selection.delta_psnr,
        "saint_ssim": selection.saint_ssim,
        "swinir_ssim": selection.swinir_ssim,
        "saint_minus_swinir_ssim": selection.delta_ssim,
        "saint_mae": selection.saint_mae,
        "swinir_mae": selection.swinir_mae,
        "saint_minus_swinir_mae": selection.delta_mae,
        "saint_ncc": selection.saint_ncc,
        "swinir_ncc": selection.swinir_ncc,
        "saint_minus_swinir_ncc": selection.delta_ncc,
        "saint_slice_gradient_mae": _gradient_mae(saint, gt, z),
        "swinir_slice_gradient_mae": _gradient_mae(swinir, gt, z),
        "panel": str(out_path.relative_to(ROOT)),
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(rows: list[dict[str, object]]) -> None:
    lines = [
        "# SAINT vs SwinIR Visual QC",
        "",
        "本文件自动挑选 fastMRI-brain-T2 expanded 和 NingXia-T2 的代表病例，并生成对比面板。",
        "",
        "选择规则：fastMRI 按 `SAINT PSNR - SwinIR PSNR` 选 small/median/large gap；NingXia 按 `SwinIR PSNR - SAINT PSNR` 选 SAINT better / near tie / SwinIR better。",
        "",
        "| Dataset | Label | Fold | Case | Slice | SAINT PSNR | SwinIR PSNR | PSNR delta | SAINT SSIM | SwinIR SSIM | SAINT grad-MAE | SwinIR grad-MAE | Panel |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["dataset"]),
                    str(row["label"]),
                    str(row["fold"]),
                    str(row["case"]),
                    str(row["selected_slice"]),
                    f"{float(row['saint_psnr']):.4f}",
                    f"{float(row['swinir_psnr']):.4f}",
                    f"{float(row['saint_minus_swinir_psnr']):.4f}",
                    f"{float(row['saint_ssim']):.4f}",
                    f"{float(row['swinir_ssim']):.4f}",
                    f"{float(row['saint_slice_gradient_mae']):.4f}",
                    f"{float(row['swinir_slice_gradient_mae']):.4f}",
                    str(row["panel"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "解读提示：`PSNR delta` 为 SAINT - SwinIR。fastMRI 中正值越大，SAINT 优势越明显；NingXia 中若为负值，表示 SwinIR 在该病例上 PSNR 更高。",
            "面板列顺序为 Linear coarse / GT / SAINT / SwinIR / SAINT error / SwinIR error / SAINT-SwinIR / absolute model difference。",
        ]
    )
    (OUT_DIR / "saint_vs_swinir_visual_qc.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    selections = select_fastmri_cases() + select_ningxia_cases()
    rows = [write_panel(selection) for selection in selections]
    _write_csv(OUT_DIR / "selected_cases.csv", rows)
    _write_markdown(rows)
    print(f"Visual QC written: {OUT_DIR}")


if __name__ == "__main__":
    main()
