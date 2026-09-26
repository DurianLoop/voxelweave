"""Controlled common-mode blur experiment for cross-model vs cross-factor scores.

EXPLORATORY. Uses the first eight lexicographically sorted fastMRI cases,
chosen without inspecting outcomes. All outputs stay under design/paper.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import ndimage, stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "plan2_outputs" / "common_mode_mechanism"
sys.path.insert(0, str(ROOT / "design"))
from rasinet.cross_scale_physical import matches, planes  # noqa: E402
from rasinet.icassp_scores import deployment_mask, generated_indices, score_map  # noqa: E402
from rasinet.optimization_protocol import (  # noqa: E402
    analytical_path, case_names, gt_path, prediction_path, profile_sources
)

SCALES = (2, 4, 6)
TARGETS = ("i3net", "hat", "swinir")
SEVERITIES = (0.0, 0.5, 1.0, 1.5)


def load(path: Path) -> np.ndarray:
    return nib.load(str(path)).get_fdata(dtype=np.float32)


def blur(volume: np.ndarray, sigma: float) -> np.ndarray:
    return volume if sigma == 0 else ndimage.gaussian_filter(volume, sigma=(sigma, sigma, 0), mode="nearest")


def error_mae(pred: np.ndarray, gt: np.ndarray, scale: int) -> float:
    idx = list(generated_indices(gt.shape[2], scale))
    support = np.abs(gt[:, :, idx]) > max(1e-6, 0.01 * float(np.max(np.abs(gt[:, :, idx]))))
    return float(np.mean(np.abs(pred[:, :, idx][support] - gt[:, :, idx][support])))


def cross_model(target: str, outputs: dict[str, np.ndarray], scale: int) -> float:
    committee = {name: value for name, value in outputs.items() if name != target}
    mask = deployment_mask(outputs[target], committee, "target_0.01", scale)
    idx = list(generated_indices(outputs[target].shape[2], scale))
    values = score_map(target, outputs[target][:, :, idx], {k: v[:, :, idx] for k, v in committee.items()}, "target_abs_median")
    return float(np.mean(values[mask[:, :, idx]]))


def physical_scores(target_volumes: dict[int, np.ndarray], images: dict[int, nib.spatialimages.SpatialImage]) -> dict[int, float]:
    pair_values: dict[tuple[int, int], float] = {}
    for a, b in ((2, 4), (2, 6), (4, 6)):
        match = matches(planes(images[a], a), planes(images[b], b))
        values = []
        for za, zb, _, _ in match:
            va, vb = target_volumes[a][:, :, za], target_volumes[b][:, :, zb]
            threshold = 0.01 * max(float(np.max(np.abs(va))), float(np.max(np.abs(vb))), 1e-6)
            mask = (np.abs(va) > threshold) | (np.abs(vb) > threshold)
            values.append(float(np.mean(np.abs(va[mask] - vb[mask]))))
        pair_values[(a, b)] = float(np.median(values))
    return {scale: float(np.median([v for pair, v in pair_values.items() if scale in pair])) for scale in SCALES}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sources = {scale: profile_sources("fastmri", scale) for scale in SCALES}
    cases = sorted(set.intersection(*[set(case_names(sources[s]["i3net"], None)) for s in SCALES]))[:8]
    records = []
    for case in cases:
        images = {s: {t: nib.load(str(prediction_path(sources[s][t], None, case))) for t in TARGETS} for s in SCALES}
        originals = {}
        gts = {}
        for scale in SCALES:
            originals[scale] = {t: images[scale][t].get_fdata(dtype=np.float32) for t in TARGETS}
            originals[scale]["linear"] = load(analytical_path(sources[scale]["i3net"], None, "linear", case))
            originals[scale]["cubic"] = load(analytical_path(sources[scale]["i3net"], None, "cubic", case))
            gts[scale] = load(gt_path(sources[scale]["i3net"], None, case))
        for mode in ("shared_uniform", "shared_factor_dependent", "target_only_factor_dependent"):
            for severity in SEVERITIES:
                for target in TARGETS:
                    altered: dict[int, dict[str, np.ndarray]] = {}
                    target_volumes = {}
                    for scale in SCALES:
                        sigma = severity if mode == "shared_uniform" else severity * {2: 0.5, 4: 1.0, 6: 1.5}[scale]
                        altered[scale] = {}
                        for name, volume in originals[scale].items():
                            should_blur = mode.startswith("shared") or name == target
                            altered[scale][name] = blur(volume, sigma) if should_blur else volume
                        target_volumes[scale] = altered[scale][target]
                    pc = physical_scores(target_volumes, {s: images[s][target] for s in SCALES})
                    for scale in SCALES:
                        records.append({
                            "case": case, "target_model": target, "scale": scale, "mode": mode, "severity": severity,
                            "sigma": severity if mode == "shared_uniform" else severity * {2: 0.5, 4: 1.0, 6: 1.5}[scale],
                            "common_error": error_mae(target_volumes[scale], gts[scale], scale),
                            "cross_model_disagreement": cross_model(target, altered[scale], scale),
                            "physical_consistency": pc[scale],
                        })
        print(f"completed {case}", flush=True)
    frame = pd.DataFrame(records)
    frame.to_csv(OUT / "per_case.csv", index=False)
    summary = frame.groupby(["mode", "severity"], as_index=False).agg(
        mean_error=("common_error", "mean"),
        mean_cross_model=("cross_model_disagreement", "mean"),
        mean_physical=("physical_consistency", "mean"),
    )
    base = summary[summary.severity.eq(0)].set_index("mode")
    summary["error_change"] = summary.apply(lambda r: r.mean_error - base.loc[r["mode"], "mean_error"], axis=1)
    summary["cross_model_change"] = summary.apply(lambda r: r.mean_cross_model - base.loc[r["mode"], "mean_cross_model"], axis=1)
    summary["physical_change"] = summary.apply(lambda r: r.mean_physical - base.loc[r["mode"], "mean_physical"], axis=1)
    summary.to_csv(OUT / "summary.csv", index=False)
    correlations = []
    for (mode, severity), group in frame.groupby(["mode", "severity"]):
        correlations.append({
            "mode": mode, "severity": severity,
            "rho_error_cross_model": float(stats.spearmanr(group.common_error, group.cross_model_disagreement).statistic),
            "rho_error_physical": float(stats.spearmanr(group.common_error, group.physical_consistency).statistic),
        })
    pd.DataFrame(correlations).to_csv(OUT / "correlations.csv", index=False)
    payload = {"cases": cases, "case_selection": "first eight lexicographically sorted, outcome-blind", "rows": len(frame)}
    (OUT / "manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
