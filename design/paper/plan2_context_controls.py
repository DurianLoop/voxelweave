"""EXPLORATORY context/intensity controls and factor-pair decomposition.

The controls test whether PC-v1 is merely sensitive to arbitrary intensity
changes and whether its ranking survives reasonable normalization.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "plan2_outputs" / "context_controls"
sys.path.insert(0, str(ROOT / "design"))
from rasinet.cross_scale_physical import matches, planes  # noqa: E402
from rasinet.icassp_statistics import ranking_metrics  # noqa: E402
from rasinet.optimization_protocol import case_names, gt_path, prediction_path, profile_sources  # noqa: E402

SCALES = (2, 4, 6)
TARGETS = ("i3net", "hat", "swinir")
PAIRS = ((2, 4), (2, 6), (4, 6))


def normalize(volume: np.ndarray, kind: str) -> np.ndarray:
    if kind == "raw":
        return volume
    foreground = volume[np.abs(volume) > max(1e-6, 0.01 * float(np.max(np.abs(volume))))]
    if kind == "robust_percentile":
        low, high = np.percentile(foreground, [1, 99])
        return (volume - low) / max(float(high - low), 1e-6)
    if kind == "foreground_zscore":
        return (volume - float(np.mean(foreground))) / max(float(np.std(foreground)), 1e-6)
    raise ValueError(kind)


def pair_score(a: np.ndarray, b: np.ndarray, match) -> float:
    values = []
    for za, zb, _, _ in match:
        va, vb = a[:, :, za], b[:, :, zb]
        threshold = 0.01 * max(float(np.max(np.abs(va))), float(np.max(np.abs(vb))), 1e-6)
        mask = (np.abs(va) > threshold) | (np.abs(vb) > threshold)
        values.append(float(np.mean(np.abs(va[mask] - vb[mask]))))
    return float(np.median(values))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sources = {s: profile_sources("fastmri", s) for s in SCALES}
    cases = sorted(set.intersection(*[set(case_names(sources[s]["i3net"], None)) for s in SCALES]))
    truth = pd.read_csv(ROOT / "design" / "rasinet" / "outputs" / "nested_optimization" / "common_errors_per_case_development.csv")
    truth = truth[truth.dataset.eq("fastmri") & truth.target_model.isin(TARGETS)]
    truth = truth.set_index(["case", "target_model", "scale"]).common_error
    records = []
    gain = {2: 0.98, 4: 1.00, 6: 1.02}
    for case in cases:
        for target in TARGETS:
            imgs = {s: nib.load(str(prediction_path(sources[s][target], None, case))) for s in SCALES}
            vols = {s: imgs[s].get_fdata(dtype=np.float32) for s in SCALES}
            gts = {s: nib.load(str(gt_path(sources[s]["i3net"], None, case))).get_fdata(dtype=np.float32) for s in SCALES}
            pooled_foreground = np.concatenate([
                vols[s][np.abs(vols[s]) > max(1e-6, 0.01 * float(np.max(np.abs(vols[s]))))] for s in SCALES
            ])
            pooled_range = max(float(np.percentile(pooled_foreground, 99) - np.percentile(pooled_foreground, 1)), 1e-6)
            matched = {(a, b): matches(planes(imgs[a], a), planes(imgs[b], b)) for a, b in PAIRS}
            variants = {
                "raw": vols,
                "robust_percentile": {s: normalize(vols[s], "robust_percentile") for s in SCALES},
                "foreground_zscore": {s: normalize(vols[s], "foreground_zscore") for s in SCALES},
                "pooled_dynamic_range": {s: vols[s] / pooled_range for s in SCALES},
                "factor_gain_raw": {s: vols[s] * gain[s] for s in SCALES},
                "factor_gain_then_robust": {s: normalize(vols[s] * gain[s], "robust_percentile") for s in SCALES},
            }
            for variant, data in variants.items():
                pair_values = {pair: pair_score(data[pair[0]], data[pair[1]], matched[pair]) for pair in PAIRS}
                for scale in SCALES:
                    involved = [value for pair, value in pair_values.items() if scale in pair]
                    gt_fg = gts[scale][np.abs(gts[scale]) > max(1e-6, 0.01 * float(np.max(np.abs(gts[scale]))))]
                    gt_range = max(float(np.percentile(gt_fg, 99) - np.percentile(gt_fg, 1)), 1e-6)
                    records.append({"case": case, "target_model": target, "scale": scale, "variant": variant,
                                    "score": float(np.median(involved)), "common_error": float(truth.loc[(case, target, scale)]),
                                    "range_normalized_error": float(truth.loc[(case, target, scale)]) / gt_range})
                for pair, value in pair_values.items():
                    records.append({"case": case, "target_model": target, "scale": f"pair_{pair[0]}_{pair[1]}",
                                    "variant": variant, "score": value, "common_error": float(np.mean([truth.loc[(case, target, pair[0])], truth.loc[(case, target, pair[1])]])),
                                    "range_normalized_error": float("nan")})
        print(f"completed {case}", flush=True)
    frame = pd.DataFrame(records)
    frame.to_csv(OUT / "per_case.csv", index=False)
    evaluated = frame[~frame.scale.astype(str).str.startswith("pair_")].copy()
    rows = []
    for (variant, scale, target), group in evaluated.groupby(["variant", "scale", "target_model"]):
        raw_metrics = ranking_metrics(group.common_error, group.score)
        norm_metrics = ranking_metrics(group.range_normalized_error, group.score)
        rows.append({"variant": variant, "scale": scale, "target_model": target, **raw_metrics,
                     **{f"range_normalized_error_{k}": v for k, v in norm_metrics.items()}})
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "profile_results.csv", index=False)
    aggregate = result.groupby("variant", as_index=False)[["normalized_aurc", "case_spearman", "case_kendall", "rrr_50",
        "range_normalized_error_normalized_aurc", "range_normalized_error_case_spearman",
        "range_normalized_error_case_kendall", "range_normalized_error_rrr_50"]].mean()
    aggregate.to_csv(OUT / "aggregate_results.csv", index=False)

    pair_rows = []
    pair_frame = frame[frame.scale.astype(str).str.startswith("pair_")]
    for (variant, pair, target), group in pair_frame.groupby(["variant", "scale", "target_model"]):
        values = ranking_metrics(group.common_error, group.score)
        pair_rows.append({"variant": variant, "pair": pair, "target_model": target, **values})
    pd.DataFrame(pair_rows).to_csv(OUT / "factor_pair_results.csv", index=False)
    (OUT / "manifest.json").write_text(json.dumps({"cases": len(cases), "targets": TARGETS, "variants": list(variants)}, indent=2), encoding="utf-8")
    print(aggregate.to_string(index=False))


if __name__ == "__main__":
    main()
