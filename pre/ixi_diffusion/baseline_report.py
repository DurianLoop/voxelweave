from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .common import read_case_ids
from .settings import IXI_ROOT, PROFILES, build_paths


PRIMARY_METRICS = [
    "psnr",
    "ssim",
    "mae",
    "mse",
    "rmse",
    "nmse",
    "nrmse",
    "ncc",
    "snli",
    "mask_psnr",
    "mask_ssim",
    "auto_dice",
    "auto_hd95",
]


def _load_manifest(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _split_report(seed: int = 3407) -> dict[str, int]:
    split_dir = IXI_ROOT / "splits" / f"seed{seed}"
    train = set(read_case_ids(split_dir / "train_cases.txt"))
    val = set(read_case_ids(split_dir / "val_cases.txt"))
    test = set(read_case_ids(split_dir / "test_cases.txt"))
    return {
        "train_cases": len(train),
        "val_cases": len(val),
        "test_cases": len(test),
        "train_val_overlap": len(train & val),
        "train_test_overlap": len(train & test),
        "val_test_overlap": len(val & test),
    }


def _case_lookup(modality: str) -> dict[str, str]:
    cases = pd.read_csv(IXI_ROOT / "metadata" / "ixi_cases.csv")
    lookup: dict[str, str] = {}
    for _, row in cases.iterrows():
        source_name = Path(str(row[f"{modality}_path"])).name
        lookup[source_name] = str(row["case_id"])
    return lookup


def _eval_case_report(manifest: dict, modality: str, seed: int = 3407) -> dict[str, int | list[str]]:
    test_cases = set(read_case_ids(IXI_ROOT / "splits" / f"seed{seed}" / "test_cases.txt"))
    lookup = _case_lookup(modality)
    bad_cases = []
    for row in manifest["eval_cases"]:
        source_name = Path(str(row["source"])).name
        case_id = lookup.get(source_name)
        if case_id not in test_cases:
            bad_cases.append(str(row["case"]))
    return {
        "eval_cases": len(manifest["eval_cases"]),
        "eval_cases_not_in_test": len(bad_cases),
        "bad_eval_cases": bad_cases,
    }


def _file_count_report(paths) -> dict[str, int]:
    return {
        "gt_files": len(list(paths.eval_gt.glob("*.nii.gz"))),
        "pred_files": len(list(paths.diffusion_outputs.glob("*.nii.gz"))),
        "linear_files": len(list(paths.baseline_linear.glob("*.nii.gz"))),
        "cubic_files": len(list(paths.baseline_cubic.glob("*.nii.gz"))),
    }


def _generated_slice_report(manifest: dict, per_case: pd.DataFrame) -> dict[str, int]:
    expected = {row["case"]: int(row["target_depth"]) - int(row["sparse_depth"]) for row in manifest["eval_cases"]}
    mismatches = 0
    checked = 0
    for _, row in per_case.iterrows():
        case = str(row["case"])
        if case not in expected:
            continue
        checked += 1
        if int(row["generated_slices"]) != expected[case]:
            mismatches += 1
    return {"generated_slice_rows_checked": checked, "generated_slice_mismatches": mismatches}


def _improvement_report(summary: pd.DataFrame, method: str) -> dict[str, float]:
    methods = set(summary["method"].astype(str))
    if method not in methods or "linear" not in methods:
        return {}
    target = summary[summary["method"] == method].iloc[0]
    linear = summary[summary["method"] == "linear"].iloc[0]
    report = {
        "psnr_vs_linear": float(target["psnr_mean"] - linear["psnr_mean"]),
        "ssim_vs_linear": float(target["ssim_mean"] - linear["ssim_mean"]),
        "mae_vs_linear": float(target["mae_mean"] - linear["mae_mean"]),
        "rmse_vs_linear": float((target["mse_mean"] ** 0.5) - (linear["mse_mean"] ** 0.5)),
        "auto_dice_vs_linear": float(target["auto_dice_mean"] - linear["auto_dice_mean"]),
        "auto_hd95_vs_linear": float(target["auto_hd95_mean"] - linear["auto_hd95_mean"]),
    }
    for key in ["nmse", "nrmse", "snli"]:
        mean_key = f"{key}_mean"
        if mean_key in summary.columns:
            report[f"{key}_vs_linear"] = float(target[mean_key] - linear[mean_key])
    return report


def _per_case_win_report(per_case: pd.DataFrame, method: str, baseline: str = "linear") -> dict[str, int]:
    if method not in per_case["method"].values or baseline not in per_case["method"].values:
        return {}
    available_metrics = [metric for metric in PRIMARY_METRICS if metric in per_case.columns]
    pivot = per_case.pivot(index="case", columns="method", values=available_metrics)
    cases = sorted(set(per_case[per_case["method"] == method]["case"]) & set(per_case[per_case["method"] == baseline]["case"]))
    out = {"cases_compared": len(cases)}
    higher_is_better = ["psnr", "ssim", "ncc", "mask_psnr", "mask_ssim", "auto_dice"]
    lower_is_better = ["mae", "mse", "rmse", "nmse", "nrmse", "snli", "auto_hd95"]
    for metric in higher_is_better:
        if metric not in available_metrics:
            continue
        out[f"{metric}_wins_vs_{baseline}"] = int((pivot[metric].loc[cases, method] > pivot[metric].loc[cases, baseline]).sum())
    for metric in lower_is_better:
        if metric not in available_metrics:
            continue
        out[f"{metric}_wins_vs_{baseline}"] = int((pivot[metric].loc[cases, method] < pivot[metric].loc[cases, baseline]).sum())
    return out


def build_report(profile_name: str) -> tuple[dict, str]:
    profile = PROFILES[profile_name]
    paths = build_paths(profile.name)
    manifest = _load_manifest(paths.run_dir / "run_manifest.json")
    summary = pd.read_csv(paths.metrics / "summary_metrics.csv")
    per_case = pd.read_csv(paths.metrics / "per_case_metrics.csv")
    method = {
        "resunet_residual": "resunet",
        "saint_spatial_aware": "saint",
    }.get(profile.method, "diffusion")

    report = {
        "profile": profile.name,
        "dataset": f"IXI-{profile.modality}",
        "method": method,
        "split": _split_report(),
        "eval_cases": _eval_case_report(manifest, profile.modality),
        "file_counts": _file_count_report(paths),
        "generated_slices": _generated_slice_report(manifest, per_case),
        "summary_vs_linear": _improvement_report(summary, method),
        "per_case_wins_vs_linear": _per_case_win_report(per_case, method, "linear"),
        "per_case_wins_vs_cubic": _per_case_win_report(per_case, method, "cubic"),
    }

    lines = [
        f"# Baseline Report: {profile.name}",
        "",
        f"- Dataset: `{report['dataset']}`",
        f"- Method: `{method}`",
        f"- Profile: `{profile.name}`",
        "",
        "## Split Sanity",
        "",
    ]
    for key, value in report["split"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Evaluation Sanity", ""])
    for key, value in report["eval_cases"].items():
        if key != "bad_eval_cases":
            lines.append(f"- {key}: `{value}`")
    for key, value in report["file_counts"].items():
        lines.append(f"- {key}: `{value}`")
    for key, value in report["generated_slices"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Summary vs Linear", ""])
    for key, value in report["summary_vs_linear"].items():
        lines.append(f"- {key}: `{value:.4f}`")
    lines.extend(["", "## Per-Case Wins vs Linear", ""])
    for key, value in report["per_case_wins_vs_linear"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Per-Case Wins vs Cubic", ""])
    for key, value in report["per_case_wins_vs_cubic"].items():
        lines.append(f"- {key}: `{value}`")
    return report, "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="resunet_full", choices=sorted(PROFILES))
    args = parser.parse_args()
    paths = build_paths(args.profile)
    report, markdown = build_report(args.profile)
    paths.metrics.mkdir(parents=True, exist_ok=True)
    (paths.metrics / "baseline_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (paths.metrics / "baseline_report.md").write_text(markdown, encoding="utf-8")
    print(f"Wrote {paths.metrics / 'baseline_report.json'}")
    print(f"Wrote {paths.metrics / 'baseline_report.md'}")


if __name__ == "__main__":
    main()
