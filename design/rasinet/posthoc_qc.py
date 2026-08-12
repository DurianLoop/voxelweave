from __future__ import annotations

import argparse
import csv
import time
from collections import defaultdict
from pathlib import Path

import nibabel as nib
import numpy as np

from ixi_diffusion.common import ensure_dir, load_nifti, write_csv, write_json

from .posthoc_uncertainty import SOURCE_SETS, _baseline_path, _gt_path, _prediction_path


ROOT = Path(__file__).resolve().parents[1]


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _to_float(row: dict, key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else float("nan")


def _safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64).reshape(-1)
    b = np.asarray(b, dtype=np.float64).reshape(-1)
    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) < 2:
        return float("nan")
    a = a[mask]
    b = b[mask]
    if float(np.std(a)) <= 1e-12 or float(np.std(b)) <= 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _case_name_from_method_file(path: Path, prefix: str) -> str:
    name = path.name
    if not name.startswith(prefix):
        raise ValueError(f"Unexpected file name for prefix {prefix!r}: {name}")
    return name[len(prefix) :]


def _case_names(reference) -> list[str]:
    return [
        _case_name_from_method_file(path, reference.pred_prefix)
        for path in sorted(reference.pred_dir.glob(f"{reference.pred_prefix}*.nii.gz"))
    ]


def _nii_shape(path: Path) -> tuple[int, ...] | None:
    if not path.exists():
        return None
    return tuple(int(v) for v in nib.load(str(path)).shape)


def _generated_indices(depth: int, factor: int) -> list[int]:
    return [idx for idx in range(depth) if idx % factor != 0]


def _split_method(method: str) -> tuple[str, str]:
    if "__" not in method:
        return method, ""
    return tuple(method.split("__", 1))  # type: ignore[return-value]


def build_manifest(profile: str, source_set: str, factor: int) -> tuple[list[dict], list[str]]:
    sources = tuple(source for source in SOURCE_SETS[source_set] if source.pred_dir.exists())
    if not sources:
        raise FileNotFoundError(f"No sources found for source_set={source_set}")
    reference = sources[0]
    rows: list[dict] = []
    cases = _case_names(reference)
    for case_name in cases:
        gt_path = _gt_path(reference, case_name)
        linear_path = _baseline_path(reference, "linear", case_name)
        cubic_path = _baseline_path(reference, "cubic", case_name)
        gt_shape = _nii_shape(gt_path)
        linear_shape = _nii_shape(linear_path)
        cubic_shape = _nii_shape(cubic_path)
        shapes = [shape for shape in [gt_shape, linear_shape, cubic_shape] if shape is not None]
        method_paths: dict[str, Path] = {}
        method_shapes: dict[str, tuple[int, ...] | None] = {}
        for source in sources:
            path = _prediction_path(source, case_name)
            method_paths[source.name] = path
            method_shapes[source.name] = _nii_shape(path)
            if method_shapes[source.name] is not None:
                shapes.append(method_shapes[source.name])
        unique_shapes = sorted({str(shape) for shape in shapes})
        generated = _generated_indices(gt_shape[2], factor) if gt_shape is not None and len(gt_shape) == 3 else []
        row = {
            "profile": profile,
            "source_set": source_set,
            "case": case_name,
            "gt_path": str(gt_path),
            "linear_path": str(linear_path),
            "cubic_path": str(cubic_path),
            "gt_exists": int(gt_path.exists()),
            "linear_exists": int(linear_path.exists()),
            "cubic_exists": int(cubic_path.exists()),
            "gt_shape": str(gt_shape),
            "linear_shape": str(linear_shape),
            "cubic_shape": str(cubic_shape),
            "generated_slices_expected": len(generated),
            "generated_slice_rule": f"idx % {factor} != 0",
            "shape_aligned": int(len(unique_shapes) == 1),
        }
        for source in sources:
            row[f"{source.name}_path"] = str(method_paths[source.name])
            row[f"{source.name}_exists"] = int(method_paths[source.name].exists())
            row[f"{source.name}_shape"] = str(method_shapes[source.name])
        rows.append(row)
    return rows, [source.name for source in sources]


def build_alignment_summary(manifest_rows: list[dict], method_names: list[str]) -> list[dict]:
    required = ["gt", "linear", "cubic", *method_names]
    rows: list[dict] = []
    for name in required:
        exists_key = f"{name}_exists"
        shape_key = f"{name}_shape"
        exists_count = sum(int(row.get(exists_key, 0)) for row in manifest_rows)
        shape_values = sorted({row.get(shape_key, "") for row in manifest_rows if row.get(shape_key, "") != "None"})
        rows.append(
            {
                "item": name,
                "cases": len(manifest_rows),
                "exists_count": exists_count,
                "missing_count": len(manifest_rows) - exists_count,
                "unique_shapes": "; ".join(shape_values),
            }
        )
    rows.append(
        {
            "item": "all_shape_aligned",
            "cases": len(manifest_rows),
            "exists_count": sum(int(row["shape_aligned"]) for row in manifest_rows),
            "missing_count": len(manifest_rows) - sum(int(row["shape_aligned"]) for row in manifest_rows),
            "unique_shapes": "",
        }
    )
    return rows


def check_generated_slices(metrics_dir: Path, manifest_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    per_case_rows = _read_csv(metrics_dir / "per_case_posthoc_reliability.csv")
    expected_by_case = {row["case"]: int(row["generated_slices_expected"]) for row in manifest_rows}
    rows = []
    for row in per_case_rows:
        expected = expected_by_case.get(row["case"])
        actual = int(float(row["generated_slices"]))
        rows.append(
            {
                "method": row["method"],
                "case": row["case"],
                "expected_generated_slices": expected,
                "actual_generated_slices": actual,
                "matches_expected": int(expected == actual),
            }
        )
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["method"]].append(row)
    summary = [
        {
            "method": method,
            "rows": len(selected),
            "matched_rows": sum(int(row["matches_expected"]) for row in selected),
            "mismatched_rows": len(selected) - sum(int(row["matches_expected"]) for row in selected),
        }
        for method, selected in sorted(grouped.items())
    ]
    return rows, summary


def _proxy_arrays(pred: np.ndarray, linear: np.ndarray, cubic: np.ndarray, disagreement: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "residual_linear": np.abs(pred.astype(np.float32) - linear.astype(np.float32)),
        "residual_cubic": np.abs(pred.astype(np.float32) - cubic.astype(np.float32)),
        "baseline_disagreement": disagreement,
    }


def build_mask_qc(
    source_set: str,
    profile: str,
    factor: int,
    manifest_rows: list[dict],
    progress_every: int,
) -> tuple[list[dict], list[dict]]:
    started = time.time()
    sources = tuple(source for source in SOURCE_SETS[source_set] if source.pred_dir.exists())
    reference = sources[0]
    rows: list[dict] = []
    for index, manifest in enumerate(manifest_rows, start=1):
        case_name = manifest["case"]
        if progress_every > 0 and (index == 1 or index % progress_every == 0):
            print(f"[qc] mask/background {index}/{len(manifest_rows)} {case_name} elapsed={time.time() - started:.1f}s", flush=True)
        gt, _, _ = load_nifti(_gt_path(reference, case_name))
        linear, _, _ = load_nifti(_baseline_path(reference, "linear", case_name))
        cubic, _, _ = load_nifti(_baseline_path(reference, "cubic", case_name))
        predictions: dict[str, np.ndarray] = {}
        for source in sources:
            predictions[source.name], _, _ = load_nifti(_prediction_path(source, case_name))
        disagreement = np.std(
            np.stack([linear.astype(np.float32), cubic.astype(np.float32), *[pred.astype(np.float32) for pred in predictions.values()]], axis=0),
            axis=0,
        ).astype(np.float32)
        indices = _generated_indices(gt.shape[2], factor)
        gt_eval = gt[:, :, indices].astype(np.float32)
        data_max = float(np.nanmax(np.abs(gt_eval))) if np.any(np.isfinite(gt_eval)) else 0.0
        threshold = max(1e-6, 0.01 * data_max)
        nonzero_mask = np.abs(gt_eval) > threshold
        mask_fraction = float(np.mean(nonzero_mask))
        background_fraction = 1.0 - mask_fraction
        for method, pred in predictions.items():
            error = np.abs(pred[:, :, indices].astype(np.float32) - gt_eval)
            for proxy_name, uncertainty_full in _proxy_arrays(pred, linear, cubic, disagreement).items():
                uncertainty = uncertainty_full[:, :, indices].astype(np.float32)
                all_corr = _safe_corr(error, uncertainty)
                nonzero_corr = _safe_corr(error[nonzero_mask], uncertainty[nonzero_mask]) if np.any(nonzero_mask) else float("nan")
                background_corr = _safe_corr(error[~nonzero_mask], uncertainty[~nonzero_mask]) if np.any(~nonzero_mask) else float("nan")
                rows.append(
                    {
                        "profile": profile,
                        "method": f"{method}__{proxy_name}",
                        "case": case_name,
                        "proxy": proxy_name,
                        "mask_threshold": threshold,
                        "nonzero_fraction": mask_fraction,
                        "background_fraction": background_fraction,
                        "pixel_corr_all": all_corr,
                        "pixel_corr_nonzero": nonzero_corr,
                        "pixel_corr_background": background_corr,
                        "corr_drop_nonzero_minus_all": nonzero_corr - all_corr if np.isfinite(nonzero_corr) and np.isfinite(all_corr) else float("nan"),
                    }
                )
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["method"]].append(row)
    summary = []
    for method, selected in sorted(grouped.items()):
        for key in [
            "nonzero_fraction",
            "background_fraction",
            "pixel_corr_all",
            "pixel_corr_nonzero",
            "pixel_corr_background",
            "corr_drop_nonzero_minus_all",
        ]:
            values = np.asarray([float(row[key]) for row in selected], dtype=np.float64)
            values = values[np.isfinite(values)]
            summary.append(
                {
                    "method": method,
                    "metric": key,
                    "cases": len(selected),
                    "mean": float(np.mean(values)) if values.size else float("nan"),
                    "std": float(np.std(values)) if values.size else float("nan"),
                }
            )
    return rows, summary


def build_pixel_slice_disagreement(metrics_dir: Path) -> tuple[list[dict], list[dict]]:
    rows = _read_csv(metrics_dir / "per_case_posthoc_reliability.csv")
    flagged = []
    for row in rows:
        pixel_corr = _to_float(row, "pixel_error_uncertainty_corr")
        slice_corr = _to_float(row, "slice_error_uncertainty_corr")
        sign_disagree = int(np.isfinite(pixel_corr) and np.isfinite(slice_corr) and pixel_corr * slice_corr < 0)
        large_gap = int(np.isfinite(pixel_corr) and np.isfinite(slice_corr) and abs(pixel_corr - slice_corr) >= 0.35)
        if sign_disagree or large_gap:
            method, proxy = _split_method(row["method"])
            flagged.append(
                {
                    "method": method,
                    "proxy": proxy,
                    "case": row["case"],
                    "pixel_corr": pixel_corr,
                    "slice_corr": slice_corr,
                    "abs_gap": abs(pixel_corr - slice_corr),
                    "sign_disagree": sign_disagree,
                    "large_gap": large_gap,
                    "mean_abs_error": row["mean_abs_error"],
                    "mean_uncertainty": row["mean_uncertainty"],
                }
            )
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in flagged:
        grouped[f"{row['method']}__{row['proxy']}"].append(row)
    summary = [
        {
            "method": method,
            "flagged_cases": len(selected),
            "sign_disagree_cases": sum(int(row["sign_disagree"]) for row in selected),
            "large_gap_cases": sum(int(row["large_gap"]) for row in selected),
        }
        for method, selected in sorted(grouped.items())
    ]
    return flagged, summary


def build_failure_case_review(metrics_dir: Path, top_k: int) -> list[dict]:
    rows = _read_csv(metrics_dir / "per_case_posthoc_reliability.csv")
    review_rows: list[dict] = []
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["method"]].append(row)
    for method, selected in sorted(grouped.items()):
        base_method, proxy = _split_method(method)
        by_error = sorted(selected, key=lambda row: -_to_float(row, "mean_abs_error"))
        by_unc = sorted(selected, key=lambda row: -_to_float(row, "mean_uncertainty"))
        error_rank = {row["case"]: rank for rank, row in enumerate(by_error, start=1)}
        uncertainty_rank = {row["case"]: rank for rank, row in enumerate(by_unc, start=1)}
        cases = sorted(
            {row["case"] for row in by_error[:top_k]} | {row["case"] for row in by_unc[:top_k]},
            key=lambda case: (min(error_rank.get(case, 10**9), uncertainty_rank.get(case, 10**9)), case),
        )
        by_case = {row["case"]: row for row in selected}
        for case_name in cases:
            row = by_case[case_name]
            review_rows.append(
                {
                    "method": base_method,
                    "proxy": proxy,
                    "case": case_name,
                    "error_rank": error_rank[case_name],
                    "uncertainty_rank": uncertainty_rank[case_name],
                    "in_top_error": int(error_rank[case_name] <= top_k),
                    "in_top_uncertainty": int(uncertainty_rank[case_name] <= top_k),
                    "mean_abs_error": row["mean_abs_error"],
                    "mean_uncertainty": row["mean_uncertainty"],
                    "pixel_corr": row["pixel_error_uncertainty_corr"],
                    "slice_corr": row["slice_error_uncertainty_corr"],
                }
            )
    return review_rows


def _metric_mean(summary_rows: list[dict], method: str, metric: str) -> float:
    for row in summary_rows:
        if row["method"] == method and row["metric"] == metric:
            return float(row["mean"])
    return float("nan")


def write_qc_note(report_dir: Path, profile: str, alignment_summary: list[dict], generated_summary: list[dict], mask_summary: list[dict], disagreement_summary: list[dict], failure_rows: list[dict]) -> None:
    shape_row = next(row for row in alignment_summary if row["item"] == "all_shape_aligned")
    lines = [
        f"# RASI post-hoc 第三步 QC：{profile}",
        "",
        "本 QC 只检查 post-hoc uncertainty 分析链路，不训练新模型。",
        "",
        "## 已完成检查",
        "",
        f"- 对齐检查：{shape_row['exists_count']}/{shape_row['cases']} 个 case 的 GT、linear、cubic、I3Net、HAT、SwinIR、ACSI shape 一致。",
        f"- 生成切片检查：{sum(int(row['mismatched_rows']) for row in generated_summary)} 个 method/case 行与 x4 generated-slice 规则不一致。",
        "- 背景影响检查：已输出全像素、非零脑区、背景区域三套 pixel correlation。",
        "- pixel/slice 分歧检查：已输出相关性差距较大的 case。",
        "- failure case 排名：已按 MAE 与 uncertainty 均值输出 top cases。",
        "",
        "## 非零区域相关性摘要",
        "",
        "| Method / proxy | all pixel corr | nonzero corr | nonzero-all | background fraction |",
        "|---|---:|---:|---:|---:|",
    ]
    methods = sorted({row["method"] for row in mask_summary})
    for method in methods:
        all_corr = _metric_mean(mask_summary, method, "pixel_corr_all")
        nonzero_corr = _metric_mean(mask_summary, method, "pixel_corr_nonzero")
        delta = _metric_mean(mask_summary, method, "corr_drop_nonzero_minus_all")
        bg = _metric_mean(mask_summary, method, "background_fraction")
        lines.append(f"| {method} | {all_corr:.4f} | {nonzero_corr:.4f} | {delta:.4f} | {bg:.4f} |")
    lines.extend(
        [
            "",
            "## 输出文件",
            "",
            "- `qc_manifest.csv`",
            "- `qc_alignment_summary.csv`",
            "- `qc_generated_slice_check.csv`",
            "- `qc_generated_slice_summary.csv`",
            "- `qc_mask_background_per_case.csv`",
            "- `qc_mask_background_summary.csv`",
            "- `qc_pixel_slice_disagreement.csv`",
            "- `qc_pixel_slice_disagreement_summary.csv`",
            "- `qc_failure_case_review.csv`",
            "",
            "## 后续判断",
            "",
            "如果非零区域相关性仍保持正相关，则说明当前 reliability 结论不是单纯由背景区域支撑；如果某些 method/proxy 的 nonzero corr 大幅下降，后续主表要优先报告 masked 版本。",
        ]
    )
    (report_dir / "qc_step3_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_qc(profile: str, source_set: str, factor: int, top_k: int, progress_every: int) -> Path:
    metrics_dir = ROOT / "rasinet" / "runs" / "posthoc_uncertainty" / profile / "metrics"
    if not metrics_dir.exists():
        raise FileNotFoundError(metrics_dir)
    report_dir = ensure_dir(ROOT / "rasinet" / "reports" / "posthoc_uncertainty" / profile)
    print(f"[qc] output={report_dir}", flush=True)

    manifest_rows, method_names = build_manifest(profile, source_set, factor)
    write_csv(report_dir / "qc_manifest.csv", manifest_rows)
    alignment_summary = build_alignment_summary(manifest_rows, method_names)
    write_csv(report_dir / "qc_alignment_summary.csv", alignment_summary)

    generated_rows, generated_summary = check_generated_slices(metrics_dir, manifest_rows)
    write_csv(report_dir / "qc_generated_slice_check.csv", generated_rows)
    write_csv(report_dir / "qc_generated_slice_summary.csv", generated_summary)

    mask_rows, mask_summary = build_mask_qc(source_set, profile, factor, manifest_rows, progress_every)
    write_csv(report_dir / "qc_mask_background_per_case.csv", mask_rows)
    write_csv(report_dir / "qc_mask_background_summary.csv", mask_summary)

    disagreement_rows, disagreement_summary = build_pixel_slice_disagreement(metrics_dir)
    write_csv(report_dir / "qc_pixel_slice_disagreement.csv", disagreement_rows)
    write_csv(report_dir / "qc_pixel_slice_disagreement_summary.csv", disagreement_summary)

    failure_rows = build_failure_case_review(metrics_dir, top_k)
    write_csv(report_dir / "qc_failure_case_review.csv", failure_rows)
    write_json(
        report_dir / "qc_step3_summary.json",
        {
            "profile": profile,
            "source_set": source_set,
            "cases": len(manifest_rows),
            "alignment_summary": alignment_summary,
            "generated_slice_summary": generated_summary,
            "pixel_slice_disagreement_summary": disagreement_summary,
        },
    )
    write_qc_note(report_dir, profile, alignment_summary, generated_summary, mask_summary, disagreement_summary, failure_rows)
    print(f"[qc] done output={report_dir}", flush=True)
    return report_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QC for RASI post-hoc uncertainty outputs.")
    parser.add_argument("--profile", default="full_test115")
    parser.add_argument("--source-set", choices=sorted(SOURCE_SETS), default="ixi")
    parser.add_argument("--factor", type=int, default=4)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--progress-every", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_qc(
        profile=args.profile,
        source_set=args.source_set,
        factor=args.factor,
        top_k=args.top_k,
        progress_every=args.progress_every,
    )


if __name__ == "__main__":
    main()
