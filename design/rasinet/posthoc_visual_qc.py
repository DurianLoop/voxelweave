from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ixi_diffusion.common import ensure_dir, load_nifti, write_csv

from .posthoc_uncertainty import SOURCE_SETS, _baseline_path, _gt_path, _prediction_path


ROOT = Path(__file__).resolve().parents[1]


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _to_float(row: dict, key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else float("nan")


def _generated_indices(depth: int, factor: int) -> list[int]:
    return [idx for idx in range(depth) if idx % factor != 0]


def _rank(values: dict[str, float], reverse: bool) -> dict[str, int]:
    ordered = sorted(values.items(), key=lambda item: item[1], reverse=reverse)
    return {case: rank for rank, (case, _) in enumerate(ordered, start=1)}


def _case_stem(case_name: str) -> str:
    if case_name.endswith(".nii.gz"):
        return case_name[:-7]
    return Path(case_name).stem


def _normalise_slice(image: np.ndarray) -> np.ndarray:
    finite = image[np.isfinite(image)]
    if finite.size == 0:
        return np.zeros_like(image, dtype=np.float32)
    lo, hi = np.percentile(finite, [1, 99])
    if hi <= lo:
        return np.zeros_like(image, dtype=np.float32)
    return np.clip((image - lo) / (hi - lo), 0.0, 1.0).astype(np.float32)


def select_cases(profile: str, method: str, proxy: str, top_n: int, mismatch_n: int) -> list[dict]:
    metrics_dir = ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / profile / "metrics"
    target = f"{method}__{proxy}"
    rows = [row for row in _read_csv(metrics_dir / "per_case_posthoc_reliability.csv") if row["method"] == target]
    if not rows:
        raise ValueError(f"No per-case rows found for {target}")

    error = {row["case"]: _to_float(row, "mean_abs_error") for row in rows}
    uncertainty = {row["case"]: _to_float(row, "mean_uncertainty") for row in rows}
    pixel_corr = {row["case"]: _to_float(row, "pixel_error_uncertainty_corr") for row in rows}
    slice_corr = {row["case"]: _to_float(row, "slice_error_uncertainty_corr") for row in rows}

    error_high_rank = _rank(error, reverse=True)
    unc_high_rank = _rank(uncertainty, reverse=True)
    error_low_rank = _rank(error, reverse=False)
    unc_low_rank = _rank(uncertainty, reverse=False)
    row_by_case = {row["case"]: row for row in rows}

    selected: list[dict] = []

    high_cases = sorted(error, key=lambda case: (error_high_rank[case] + unc_high_rank[case], error_high_rank[case]))[:top_n]
    low_cases = sorted(error, key=lambda case: (error_low_rank[case] + unc_low_rank[case], error_low_rank[case]))[:top_n]
    high_unc_low_error = sorted(error, key=lambda case: (unc_high_rank[case] + error_low_rank[case], unc_high_rank[case]))[:mismatch_n]
    low_unc_high_error = sorted(error, key=lambda case: (unc_low_rank[case] + error_high_rank[case], error_high_rank[case]))[:mismatch_n]
    pixel_slice_gap = sorted(error, key=lambda case: -abs(pixel_corr[case] - slice_corr[case]))[:mismatch_n]

    groups = [
        ("high_risk_high_error", high_cases),
        ("low_risk_low_error", low_cases),
        ("high_uncertainty_low_error", high_unc_low_error),
        ("low_uncertainty_high_error", low_unc_high_error),
        ("pixel_slice_gap", pixel_slice_gap),
    ]
    seen: set[tuple[str, str]] = set()
    for group, cases in groups:
        for order, case in enumerate(cases, start=1):
            key = (group, case)
            if key in seen:
                continue
            seen.add(key)
            row = row_by_case[case]
            selected.append(
                {
                    "group": group,
                    "group_order": order,
                    "case": case,
                    "method": method,
                    "proxy": proxy,
                    "mean_abs_error": row["mean_abs_error"],
                    "mean_uncertainty": row["mean_uncertainty"],
                    "error_high_rank": error_high_rank[case],
                    "uncertainty_high_rank": unc_high_rank[case],
                    "error_low_rank": error_low_rank[case],
                    "uncertainty_low_rank": unc_low_rank[case],
                    "pixel_corr": row["pixel_error_uncertainty_corr"],
                    "slice_corr": row["slice_error_uncertainty_corr"],
                    "abs_pixel_slice_gap": abs(pixel_corr[case] - slice_corr[case]),
                }
            )
    return selected


def _load_case_arrays(source_set: str, case_name: str, method: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sources = tuple(source for source in SOURCE_SETS[source_set] if source.pred_dir.exists())
    by_name = {source.name: source for source in sources}
    reference = sources[0]
    target_source = by_name[method]
    gt, _, _ = load_nifti(_gt_path(reference, case_name))
    pred, _, _ = load_nifti(_prediction_path(target_source, case_name))
    linear, _, _ = load_nifti(_baseline_path(reference, "linear", case_name))
    cubic, _, _ = load_nifti(_baseline_path(reference, "cubic", case_name))
    predictions = []
    for source in sources:
        volume, _, _ = load_nifti(_prediction_path(source, case_name))
        predictions.append(volume.astype(np.float32))
    disagreement = np.std(np.stack([linear.astype(np.float32), cubic.astype(np.float32), *predictions], axis=0), axis=0)
    return gt.astype(np.float32), pred.astype(np.float32), np.abs(pred.astype(np.float32) - gt.astype(np.float32)), disagreement.astype(np.float32)


def _choose_slice(error: np.ndarray, uncertainty: np.ndarray, factor: int, group: str) -> int:
    indices = _generated_indices(error.shape[2], factor)
    if not indices:
        return error.shape[2] // 2
    error_score = error[:, :, indices].mean(axis=(0, 1))
    unc_score = uncertainty[:, :, indices].mean(axis=(0, 1))
    if group == "low_risk_low_error":
        combined = error_score + unc_score
        return indices[int(np.argmin(combined))]
    if group == "high_uncertainty_low_error":
        return indices[int(np.argmax(unc_score))]
    combined = error_score + unc_score
    return indices[int(np.argmax(combined))]


def save_panel(
    figure_dir: Path,
    row: dict,
    source_set: str,
    factor: int,
) -> Path:
    case_name = row["case"]
    gt, pred, error, uncertainty = _load_case_arrays(source_set, case_name, row["method"])
    slice_idx = _choose_slice(error, uncertainty, factor, row["group"])

    pred_slice = _normalise_slice(pred[:, :, slice_idx])
    error_slice = _normalise_slice(error[:, :, slice_idx])
    uncertainty_slice = _normalise_slice(uncertainty[:, :, slice_idx])

    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.4))
    axes[0].imshow(np.rot90(pred_slice), cmap="gray")
    axes[0].set_title("Prediction")
    axes[1].imshow(np.rot90(error_slice), cmap="magma")
    axes[1].set_title("Abs error")
    axes[2].imshow(np.rot90(uncertainty_slice), cmap="viridis")
    axes[2].set_title("Uncertainty proxy")
    for ax in axes:
        ax.axis("off")
    fig.suptitle(
        f"{row['group']} | {row['method']} + {row['proxy']} | {_case_stem(case_name)} | z={slice_idx}",
        fontsize=10,
    )
    fig.tight_layout()
    path = figure_dir / f"{row['group']}_{int(row['group_order']):02d}_{_case_stem(case_name)}.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    row["slice_index"] = slice_idx
    row["panel_path"] = str(path)
    return path


def write_note(path: Path, rows: list[dict]) -> None:
    lines = [
        "# full_test115 visual QC case review",
        "",
        "主可视化对象：`SwinIR + baseline_disagreement`。每张图包含 prediction、absolute error、uncertainty proxy。所有 case 只用于 post-hoc reliability 检查，不代表新模型训练结果。",
        "",
        "| Group | Case | Slice | Error rank | Uncertainty rank | Pixel corr | Slice corr | Panel |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {group} | {case} | {slice_index} | {error_high_rank} | {uncertainty_high_rank} | {pixel_corr:.4f} | {slice_corr:.4f} | `{panel}` |".format(
                group=row["group"],
                case=row["case"],
                slice_index=row["slice_index"],
                error_high_rank=row["error_high_rank"],
                uncertainty_high_rank=row["uncertainty_high_rank"],
                pixel_corr=float(row["pixel_corr"]),
                slice_corr=float(row["slice_corr"]),
                panel=Path(row["panel_path"]).name,
            )
        )
    lines.extend(
        [
            "",
            "阅读建议：",
            "",
            "- `high_risk_high_error` 应用于展示 uncertainty proxy 是否能覆盖真实失败区域。",
            "- `low_risk_low_error` 用于展示低风险 case 的背景和结构区域是否稳定。",
            "- `high_uncertainty_low_error` 与 `low_uncertainty_high_error` 是必须保留的反例类别，避免只展示成功样本。",
            "- `pixel_slice_gap` 用于检查 pixel-level 与 slice-level 结论不一致的 case。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_visual_qc(profile: str, source_set: str, method: str, proxy: str, factor: int, top_n: int, mismatch_n: int) -> Path:
    report_dir = ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / profile
    figure_dir = ensure_dir(report_dir / "figures" / "visual_qc")
    selected_rows = select_cases(profile, method, proxy, top_n, mismatch_n)
    for row in selected_rows:
        save_panel(figure_dir, row, source_set, factor)
    write_csv(report_dir / "visual_qc_case_selection.csv", selected_rows)
    note_path = report_dir / "visual_qc_case_review.md"
    write_note(note_path, selected_rows)
    return note_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build visual QC panels for RASI post-hoc uncertainty.")
    parser.add_argument("--profile", default="full_test115")
    parser.add_argument("--source-set", default="ixi")
    parser.add_argument("--method", default="swinir")
    parser.add_argument("--proxy", default="baseline_disagreement")
    parser.add_argument("--factor", type=int, default=4)
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--mismatch-n", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    note_path = build_visual_qc(
        profile=args.profile,
        source_set=args.source_set,
        method=args.method,
        proxy=args.proxy,
        factor=args.factor,
        top_n=args.top_n,
        mismatch_n=args.mismatch_n,
    )
    print(f"Wrote visual QC note to {note_path}")


if __name__ == "__main__":
    main()
