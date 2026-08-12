from __future__ import annotations

import argparse
import csv
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ixi_diffusion.common import ensure_dir, load_nifti, write_csv

from .committee_reliability import (
    committee_dispersion,
    risk_coverage_summary,
    target_to_committee_disagreement,
)
from .metrics import _failure_detection


REPO_ROOT = Path(__file__).resolve().parents[2]
ANALYTIC_MEMBERS = {"linear", "cubic"}
PROFILE_ALIASES = {
    "full_test115": "ixi",
    "fastmri_full": "fastmri",
    "ningxia_cv": "ningxia",
}


@dataclass(frozen=True)
class ReconstructionSource:
    name: str
    root: Path
    run_name: str = "full"
    cross_validation: bool = False

    def run_dir(self, fold: str | None = None) -> Path:
        if self.cross_validation:
            if fold is None:
                raise ValueError(f"fold is required for source {self.name}")
            return self.root / "runs" / fold / self.run_name
        return self.root / "runs" / self.run_name


@dataclass(frozen=True)
class TargetContext:
    indices: tuple[int, ...]
    error: np.ndarray
    foreground: np.ndarray
    mask_threshold: float
    slice_error: np.ndarray


def profile_sources(repo_root: Path, profile: str) -> tuple[ReconstructionSource, ...]:
    profile = PROFILE_ALIASES.get(profile, profile)
    baseline = repo_root / "baseline"
    design = repo_root / "design"
    if profile == "ixi":
        return (
            ReconstructionSource("i3net", baseline / "ixi_i3net", "full_test115_stable"),
            ReconstructionSource("hat", baseline / "ixi_hat_2p5d", "full_test115"),
            ReconstructionSource("swinir", baseline / "ixi_swinir_2p5d", "full_test115"),
            ReconstructionSource("acsinet", design / "acsinet", "full_test115"),
        )
    if profile == "fastmri":
        return (
            ReconstructionSource("i3net", baseline / "fastmri_brain_i3net"),
            ReconstructionSource("hat", baseline / "fastmri_brain_hat_2p5d"),
            ReconstructionSource("swinir", baseline / "fastmri_brain_swinir_2p5d"),
        )
    if profile == "ningxia":
        return (
            ReconstructionSource("i3net", baseline / "ningxia_t2_i3net_cv", cross_validation=True),
            ReconstructionSource("hat", baseline / "ningxia_t2_hat_2p5d_cv", cross_validation=True),
            ReconstructionSource("swinir", baseline / "ningxia_t2_swinir_2p5d_cv", cross_validation=True),
        )
    raise ValueError(f"unknown profile: {profile}")


def committee_member_names(
    target: str,
    available_members: list[str] | tuple[str, ...],
    mode: str,
    excluded_member: str | None = None,
) -> list[str]:
    if mode not in {"all", "neural", "analytic"}:
        raise ValueError(f"unknown committee mode: {mode}")
    selected = []
    for member in available_members:
        if member == target or member == excluded_member:
            continue
        if mode == "neural" and member in ANALYTIC_MEMBERS:
            continue
        if mode == "analytic" and member not in ANALYTIC_MEMBERS:
            continue
        selected.append(member)
    if not selected:
        raise ValueError(f"committee is empty for target={target}, mode={mode}")
    return selected


def _folds(sources: tuple[ReconstructionSource, ...]) -> list[str | None]:
    if not sources[0].cross_validation:
        return [None]
    run_root = sources[0].root / "runs"
    return [path.name for path in sorted(run_root.glob("fold_*")) if path.is_dir()]


def _case_names(reference: ReconstructionSource, fold: str | None) -> list[str]:
    pred_dir = reference.run_dir(fold) / "model_outputs"
    return [path.name[len("diff_") :] for path in sorted(pred_dir.glob("diff_*.nii.gz"))]


def _gt_path(reference: ReconstructionSource, fold: str | None, case_name: str, profile: str) -> Path:
    gt_dir = "eval_inputs" if profile == "full_test115" else "eval_gt"
    base = reference.run_dir(fold) / gt_dir
    if gt_dir == "eval_inputs":
        base = base / "gt"
    return base / case_name


def _baseline_path(
    reference: ReconstructionSource,
    fold: str | None,
    baseline: str,
    case_name: str,
) -> Path:
    return reference.run_dir(fold) / "baseline_outputs" / baseline / f"{baseline}_{case_name}"


def _prediction_path(source: ReconstructionSource, fold: str | None, case_name: str) -> Path:
    return source.run_dir(fold) / "model_outputs" / f"diff_{case_name}"


def _generated_indices(depth: int, factor: int) -> list[int]:
    return [index for index in range(depth) if index % factor != 0]


def _safe_corr(first: np.ndarray, second: np.ndarray) -> float:
    a = np.asarray(first, dtype=np.float64).reshape(-1)
    b = np.asarray(second, dtype=np.float64).reshape(-1)
    valid = np.isfinite(a) & np.isfinite(b)
    if int(valid.sum()) < 2:
        return float("nan")
    a = a[valid]
    b = b[valid]
    if float(np.std(a)) <= 1e-12 or float(np.std(b)) <= 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _rank(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=np.float64)
    sorted_values = values[order]
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and sorted_values[end] == sorted_values[start]:
            end += 1
        ranks[order[start:end]] = 0.5 * (start + end - 1)
        start = end
    return ranks


def _foreground_mask(prediction: np.ndarray) -> tuple[np.ndarray, float]:
    finite = np.abs(prediction[np.isfinite(prediction)])
    data_max = float(np.max(finite)) if finite.size else 0.0
    threshold = max(1e-6, 0.01 * data_max)
    return np.abs(prediction) > threshold, threshold


def _target_context(gt: np.ndarray, prediction: np.ndarray, factor: int) -> TargetContext:
    if gt.shape != prediction.shape:
        raise ValueError(f"shape mismatch: gt={gt.shape}, prediction={prediction.shape}")
    indices = _generated_indices(gt.shape[2], factor)
    gt_eval = gt[:, :, indices].astype(np.float32)
    pred_eval = prediction[:, :, indices].astype(np.float32)
    error = np.abs(pred_eval - gt_eval)
    foreground, threshold = _foreground_mask(pred_eval)
    if not np.any(foreground):
        foreground = np.ones_like(pred_eval, dtype=bool)
    return TargetContext(
        indices=tuple(indices),
        error=error,
        foreground=foreground,
        mask_threshold=threshold,
        slice_error=np.mean(error, axis=(0, 1)),
    )


def _case_metrics(
    context: TargetContext,
    uncertainty: np.ndarray,
) -> dict[str, float | int]:
    if uncertainty.shape == context.error.shape:
        unc_eval = uncertainty.astype(np.float32)
    else:
        unc_eval = uncertainty[:, :, list(context.indices)].astype(np.float32)
    if unc_eval.shape != context.error.shape:
        raise ValueError(f"uncertainty shape mismatch: error={context.error.shape}, uncertainty={unc_eval.shape}")
    slice_uncertainty = np.mean(unc_eval, axis=(0, 1))
    return {
        "generated_slices": len(context.indices),
        "mask_threshold": context.mask_threshold,
        "foreground_fraction": float(np.mean(context.foreground)),
        "mean_abs_error": float(np.mean(context.error[context.foreground])),
        "mean_uncertainty": float(np.mean(unc_eval[context.foreground])),
        "pixel_corr_foreground": _safe_corr(
            context.error[context.foreground],
            unc_eval[context.foreground],
        ),
        "pixel_corr_all": _safe_corr(context.error, unc_eval),
        "slice_corr": _safe_corr(context.slice_error, slice_uncertainty),
    }


def _proxy_specs(
    target_name: str,
    members: dict[str, np.ndarray],
    shared_dispersion: np.ndarray,
) -> tuple[list[tuple[str, str, str, list[str], np.ndarray]], dict[str, np.ndarray]]:
    target = members[target_name]
    available = list(members)
    differences = {
        name: np.abs(target.astype(np.float32) - member.astype(np.float32))
        for name, member in members.items()
        if name != target_name
    }
    specs: list[tuple[str, str, str, list[str], np.ndarray]] = []
    for mode in ("all", "neural", "analytic"):
        names = committee_member_names(target_name, available, mode)
        uncertainty = np.median(np.stack([differences[name] for name in names], axis=0), axis=0).astype(np.float32)
        specs.append(("target_to_committee", mode, "", names, uncertainty))

    dispersion_names = list(available)
    specs.append(
        (
            "committee_dispersion",
            "all",
            "",
            dispersion_names,
            shared_dispersion,
        )
    )
    specs.append(
        (
            "residual_linear",
            "analytic",
            "",
            ["linear"],
            differences["linear"],
        )
    )
    specs.append(
        (
            "residual_cubic",
            "analytic",
            "",
            ["cubic"],
            differences["cubic"],
        )
    )
    return specs, differences


def _group_key(row: dict) -> tuple[str, str, str, str]:
    return (
        str(row["target"]),
        str(row["proxy"]),
        str(row["committee_mode"]),
        str(row["excluded_member"]),
    )


def _summaries(profile: str, rows: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    grouped: dict[tuple[str, str, str, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault(_group_key(row), []).append(row)
    summaries: list[dict] = []
    risk_rows: list[dict] = []
    failure_rows: list[dict] = []
    for key, selected in sorted(grouped.items()):
        target, proxy, mode, excluded = key
        errors = np.asarray([float(row["mean_abs_error"]) for row in selected], dtype=np.float64)
        scores = np.asarray([float(row["mean_uncertainty"]) for row in selected], dtype=np.float64)
        risk = risk_coverage_summary(errors, scores)
        pixel_fg = np.asarray([float(row["pixel_corr_foreground"]) for row in selected], dtype=np.float64)
        pixel_all = np.asarray([float(row["pixel_corr_all"]) for row in selected], dtype=np.float64)
        slice_corr = np.asarray([float(row["slice_corr"]) for row in selected], dtype=np.float64)
        summary = {
            "profile": profile,
            "target": target,
            "proxy": proxy,
            "committee_mode": mode,
            "excluded_member": excluded,
            "committee_members": selected[0]["committee_members"],
            "cases": len(selected),
            "pixel_corr_foreground_mean": float(np.nanmean(pixel_fg)),
            "pixel_corr_foreground_std": float(np.nanstd(pixel_fg)),
            "pixel_corr_all_mean": float(np.nanmean(pixel_all)),
            "pixel_corr_all_std": float(np.nanstd(pixel_all)),
            "slice_corr_mean": float(np.nanmean(slice_corr)),
            "slice_corr_std": float(np.nanstd(slice_corr)),
            "case_error_uncertainty_pearson": _safe_corr(errors, scores),
            "case_error_uncertainty_spearman": _safe_corr(_rank(errors), _rank(scores)),
        }
        for name in (
            "aurc",
            "oracle_aurc",
            "random_aurc",
            "excess_aurc",
            "normalized_aurc",
            "risk_at_25",
            "risk_at_50",
            "risk_at_75",
            "relative_risk_reduction_at_25",
            "relative_risk_reduction_at_50",
            "relative_risk_reduction_at_75",
        ):
            summary[name] = float(risk[name])
        summaries.append(summary)

        for curve_name, values in (
            ("estimated", risk["risk"]),
            ("oracle", risk["oracle_risk"]),
            ("random", risk["random_risk"]),
        ):
            for coverage, value in zip(risk["coverage"], values):
                risk_rows.append(
                    {
                        "profile": profile,
                        "target": target,
                        "proxy": proxy,
                        "committee_mode": mode,
                        "excluded_member": excluded,
                        "curve": curve_name,
                        "coverage": float(coverage),
                        "risk": float(value),
                    }
                )

        failure_input = [
            {"mean_abs_error": float(row["mean_abs_error"]), "mean_uncertainty": float(row["mean_uncertainty"])}
            for row in selected
        ]
        failure_rows.append(
            {
                "profile": profile,
                "target": target,
                "proxy": proxy,
                "committee_mode": mode,
                "excluded_member": excluded,
                **_failure_detection(failure_input),
            }
        )
    return summaries, risk_rows, failure_rows


def run_profile(profile: str, factor: int = 4, progress_every: int = 10) -> Path:
    if profile not in PROFILE_ALIASES:
        raise ValueError(f"unknown paper profile: {profile}")
    started = time.time()
    sources = profile_sources(REPO_ROOT, profile)
    reference = sources[0]
    rows: list[dict] = []
    member_score_rows: list[dict] = []
    folds = _folds(sources)
    case_total = sum(len(_case_names(reference, fold)) for fold in folds)
    case_index = 0
    print(
        f"[committee] profile={profile} cases={case_total} methods={','.join(source.name for source in sources)}",
        flush=True,
    )
    for fold in folds:
        for case_name in _case_names(reference, fold):
            case_index += 1
            if progress_every > 0 and (case_index == 1 or case_index % progress_every == 0):
                print(
                    f"[committee] case={case_index}/{case_total} fold={fold or '-'} name={case_name} "
                    f"elapsed={time.time() - started:.1f}s",
                    flush=True,
                )
            gt, _, _ = load_nifti(_gt_path(reference, fold, case_name, profile))
            linear, _, _ = load_nifti(_baseline_path(reference, fold, "linear", case_name))
            cubic, _, _ = load_nifti(_baseline_path(reference, fold, "cubic", case_name))
            members: dict[str, np.ndarray] = {"linear": linear, "cubic": cubic}
            for source in sources:
                path = _prediction_path(source, fold, case_name)
                if not path.exists():
                    raise FileNotFoundError(path)
                prediction, _, _ = load_nifti(path)
                members[source.name] = prediction
            case_key = f"{fold}/{case_name}" if fold else case_name
            generated_indices = _generated_indices(gt.shape[2], factor)
            generated_members = {
                name: volume[:, :, generated_indices].astype(np.float32)
                for name, volume in members.items()
            }
            shared_dispersion = committee_dispersion(generated_members.values())
            for source in sources:
                target = members[source.name]
                context = _target_context(gt, target, factor)
                specs, differences = _proxy_specs(source.name, generated_members, shared_dispersion)
                for member_name, difference in differences.items():
                    diff_eval = difference
                    member_score_rows.append(
                        {
                            "profile": profile,
                            "case": case_key,
                            "fold": fold or "",
                            "target": source.name,
                            "member": member_name,
                            "mean_member_disagreement": float(np.mean(diff_eval[context.foreground])),
                            "mean_abs_error": float(np.mean(context.error[context.foreground])),
                        }
                    )
                for proxy, mode, excluded, committee_names, uncertainty in specs:
                    metrics = _case_metrics(context, uncertainty)
                    rows.append(
                        {
                            "profile": profile,
                            "case": case_key,
                            "fold": fold or "",
                            "target": source.name,
                            "proxy": proxy,
                            "committee_mode": mode,
                            "excluded_member": excluded,
                            "committee_members": ";".join(committee_names),
                            **metrics,
                        }
                    )

    summaries, risk_rows, failure_rows = _summaries(profile, rows)
    metrics_dir = ensure_dir(REPO_ROOT / "design" / "rasinet" / "runs" / "committee_reliability" / profile / "metrics")
    write_csv(metrics_dir / "per_case_committee.csv", rows)
    write_csv(metrics_dir / "per_member_disagreement_scores.csv", member_score_rows)
    write_csv(metrics_dir / "summary_committee.csv", summaries)
    write_csv(metrics_dir / "risk_coverage_committee.csv", risk_rows)
    write_csv(metrics_dir / "failure_detection_committee.csv", failure_rows)
    print(
        f"[committee] done profile={profile} rows={len(rows)} summaries={len(summaries)} "
        f"elapsed={time.time() - started:.1f}s output={metrics_dir}",
        flush=True,
    )
    return metrics_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run target-specific committee reliability experiments.")
    parser.add_argument("--profile", choices=sorted(PROFILE_ALIASES), required=True)
    parser.add_argument("--factor", type=int, default=4)
    parser.add_argument("--progress-every", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_profile(args.profile, factor=args.factor, progress_every=args.progress_every)


if __name__ == "__main__":
    main()
