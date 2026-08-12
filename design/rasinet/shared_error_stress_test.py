from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import yaml

from .committee_experiments import _baseline_path, _case_names, _gt_path, _prediction_path, profile_sources
from .icassp_scores import deployment_mask, generated_indices, score_map


REPO_ROOT = Path(__file__).resolve().parents[2]
STRENGTHS = (0.0, 0.25, 0.5, 0.75, 1.0)


def _load(path: Path) -> np.ndarray:
    data = nib.load(str(path)).get_fdata(dtype=np.float32)
    if data.ndim != 3 or not np.isfinite(data).all():
        raise ValueError(f"invalid volume: {path}")
    return data


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _fixed_patch(outputs: dict[str, np.ndarray], indices: tuple[int, ...]) -> np.ndarray:
    consensus = np.median(np.stack(list(outputs.values()), axis=0), axis=0)
    generated = np.abs(consensus[:, :, list(indices)])
    support = generated > max(1e-6, 0.05 * float(np.max(generated)))
    coordinates = np.argwhere(support)
    if coordinates.size == 0:
        raise ValueError("empty consensus support")
    center = np.median(coordinates, axis=0).astype(int)
    radius = np.maximum(np.asarray(support.shape) // np.asarray((8, 8, 10)), 2)
    local = np.zeros_like(support, dtype=bool)
    starts = np.maximum(center - radius, 0)
    stops = np.minimum(center + radius + 1, support.shape)
    local[
        starts[0] : stops[0],
        starts[1] : stops[1],
        starts[2] : stops[2],
    ] = True
    local &= support
    patch = np.zeros_like(consensus, dtype=bool)
    patch[:, :, list(indices)] = local
    if not np.any(patch):
        raise ValueError("empty corruption patch")
    return patch


def _apply_bias(volume: np.ndarray, patch: np.ndarray, amount: float) -> np.ndarray:
    corrupted = volume.copy()
    corrupted[patch] += np.float32(amount)
    return corrupted


def _cluster_bootstrap_mean(
    rows: list[dict[str, object]], metric: str, samples: int, seed: int
) -> tuple[float, float, float, int]:
    cases = sorted({str(row["case"]) for row in rows})
    case_means = np.asarray(
        [
            np.mean([float(row[metric]) for row in rows if str(row["case"]) == case])
            for case in cases
        ],
        dtype=np.float64,
    )
    rng = np.random.default_rng(seed)
    estimates = np.empty(samples, dtype=np.float64)
    for index in range(samples):
        selected = rng.integers(0, case_means.size, size=case_means.size)
        estimates[index] = float(np.mean(case_means[selected]))
    return (
        float(np.mean(case_means)),
        float(np.percentile(estimates, 2.5)),
        float(np.percentile(estimates, 97.5)),
        len(cases),
    )


def run(
    profile: str,
    factor: int,
    strengths: tuple[float, ...],
    case_limit: int,
    bootstrap_samples: int,
    seed: int,
    output: Path,
) -> None:
    sources = profile_sources(REPO_ROOT, profile)
    reference = sources[0]
    cases = _case_names(reference, None)[:case_limit]
    case_rows: list[dict[str, object]] = []
    for case_index, case_name in enumerate(cases, start=1):
        print(f"[stress] case={case_index}/{len(cases)} {case_name}", flush=True)
        outputs = {
            source.name: _load(_prediction_path(source, None, case_name))
            for source in sources
        }
        outputs["linear"] = _load(_baseline_path(reference, None, "linear", case_name))
        outputs["cubic"] = _load(_baseline_path(reference, None, "cubic", case_name))
        gt = _load(_gt_path(reference, None, case_name, profile))
        indices = generated_indices(gt.shape[2], factor)
        eval_indices = list(indices)
        patch = _fixed_patch(outputs, indices)
        patch_eval = patch[:, :, eval_indices]
        gt_eval = gt[:, :, eval_indices]
        for target in (source.name for source in sources):
            base_target = outputs[target]
            committee_names = tuple(name for name in outputs if name != target)
            base_committee = {name: outputs[name] for name in committee_names}
            fixed_mask = deployment_mask(base_target, base_committee, "target_0.01", factor)[:, :, eval_indices]
            base_target_eval = base_target[:, :, eval_indices]
            base_committee_eval = {name: volume[:, :, eval_indices] for name, volume in base_committee.items()}
            base_disagreement = score_map(target, base_target_eval, base_committee_eval, "target_abs_median")
            dynamic_range = float(np.percentile(base_target_eval[fixed_mask], 99) - np.percentile(base_target_eval[fixed_mask], 1))
            for mode in ("target_specific", "shared"):
                for strength in strengths:
                    amount = strength * 0.25 * max(dynamic_range, 1e-6)
                    target_volume = _apply_bias(base_target_eval, patch_eval, amount)
                    if mode == "shared":
                        committee = {
                            name: _apply_bias(base_committee_eval[name], patch_eval, amount)
                            for name in committee_names
                        }
                    else:
                        committee = base_committee_eval
                    disagreement = (
                        base_disagreement
                        if mode == "shared" or strength == 0.0
                        else score_map(target, target_volume, committee, "target_abs_median")
                    )
                    error = np.abs(target_volume - gt_eval)
                    committee_mae = float(
                        np.mean(
                            [
                                np.mean(np.abs(member_volume - gt_eval)[fixed_mask])
                                for member_volume in committee.values()
                            ]
                        )
                    )
                    case_rows.append(
                        {
                            "case": case_name,
                            "target": target,
                            "mode": mode,
                            "strength": strength,
                            "bias_amount": amount,
                            "patch_fraction": float(np.mean(patch[:, :, list(indices)])),
                            "foreground_mae": float(np.mean(error[fixed_mask])),
                            "committee_foreground_mae": committee_mae,
                            "disagreement": float(np.mean(disagreement[fixed_mask])),
                        }
                    )

    summary_rows: list[dict[str, object]] = []
    for mode in ("target_specific", "shared"):
        for strength_index, strength in enumerate(strengths):
            selected = [row for row in case_rows if row["mode"] == mode and row["strength"] == strength]
            for metric_index, metric in enumerate(("foreground_mae", "committee_foreground_mae", "disagreement")):
                point, low, high, case_count = _cluster_bootstrap_mean(
                    selected,
                    metric,
                    bootstrap_samples,
                    seed + 100 * strength_index + 10 * metric_index + (0 if mode == "target_specific" else 1),
                )
                summary_rows.append(
                    {
                        "mode": mode,
                        "strength": strength,
                        "metric": metric,
                        "number_of_cases": case_count,
                        "cases_times_targets": len(selected),
                        "mean": point,
                        "ci95_low": low,
                        "ci95_high": high,
                    }
                )

    output.mkdir(parents=True, exist_ok=True)
    _write_csv(output / "per_case.csv", case_rows)
    _write_csv(output / "summary.csv", summary_rows)
    _plot(summary_rows, output / "shared_error_stress.pdf")


def _plot(rows: list[dict[str, object]], output: Path) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(6.8, 2.35))
    styles = {"target_specific": ("#0072B2", "o", "Target-specific"), "shared": ("#D55E00", "s", "Shared")}
    for axis, metric, title in zip(axes, ("foreground_mae", "disagreement"), ("True foreground MAE", "Disagreement score")):
        for mode, (color, marker, label) in styles.items():
            selected = sorted(
                (row for row in rows if row["mode"] == mode and row["metric"] == metric),
                key=lambda row: float(row["strength"]),
            )
            x = np.asarray([float(row["strength"]) for row in selected])
            y = np.asarray([float(row["mean"]) for row in selected])
            low = np.asarray([float(row["ci95_low"]) for row in selected])
            high = np.asarray([float(row["ci95_high"]) for row in selected])
            axis.plot(x, y, color=color, marker=marker, linewidth=1.4, markersize=4, label=label)
            axis.fill_between(x, low, high, color=color, alpha=0.14, linewidth=0)
        axis.set_xlabel("Corruption strength")
        axis.set_ylabel(title)
        axis.grid(True, color="#D0D0D0", linewidth=0.5)
    axes[0].legend(frameon=False, fontsize=8)
    figure.tight_layout(pad=0.6, w_pad=1.0)
    figure.savefig(output, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlled target-specific and shared-error stress test.")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--case-limit", type=int, default=20)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260715)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "design" / "rasinet" / "outputs" / "shared_error_stress")
    args = parser.parse_args()
    payload: dict[str, object] = {}
    if args.config is not None:
        payload = yaml.safe_load(args.config.read_text(encoding="utf-8")) or {}
    run(
        profile=str(payload.get("profile", "full_test115")),
        factor=int(payload.get("factor", 4)),
        strengths=tuple(float(value) for value in payload.get("strengths", STRENGTHS)),
        case_limit=int(payload.get("case_limit", args.case_limit)),
        bootstrap_samples=int(payload.get("bootstrap_samples", args.bootstrap_samples)),
        seed=int(payload.get("seed", args.seed)),
        output=(REPO_ROOT / str(payload["output"])).resolve() if "output" in payload else args.output,
    )


if __name__ == "__main__":
    main()
