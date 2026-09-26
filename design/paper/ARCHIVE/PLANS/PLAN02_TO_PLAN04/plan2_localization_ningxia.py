"""CONFIRMATORY cross-dataset localization replication on NingXia OOF cases."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "plan2_outputs" / "localization" / "ningxia_confirmation"
sys.path.insert(0, str(ROOT / "design"))
from rasinet.cross_scale_physical import matches, planes  # noqa: E402
from rasinet.optimization_protocol import case_names, gt_path, prediction_path, profile_sources  # noqa: E402

SCALES = (2, 4, 6)
TARGETS = ("i3net", "hat", "swinir")


def resolved(source, scale: int, fold: str, case: str, ground_truth: bool = False) -> Path:
    path = gt_path(source, fold, case) if ground_truth else prediction_path(source, fold, case)
    if path.exists(): return path
    archived = ROOT / "baseline" / f"{source.root.name}_root_results_202607"
    tail = Path(source.gt_dir) / case if ground_truth else Path(source.output_dir) / f"diff_{case}"
    candidate = archived / "runs" / fold / source.run_name / tail
    if candidate.exists(): return candidate
    raise FileNotFoundError(path)


def corr(a, b) -> float:
    if len(a) < 3 or np.std(a) < 1e-12 or np.std(b) < 1e-12: return 0.0
    return float(stats.spearmanr(a, b).statistic)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sources = {s: profile_sources("ningxia", s) for s in SCALES}
    records = []
    for fold_index in range(8):
        fold = f"fold_{fold_index:02d}"
        cases = sorted(set.intersection(*[
            set(p.name[5:] for p in (ROOT / "baseline" / f"{sources[s]['i3net'].root.name}_root_results_202607" / "runs" / fold / sources[s]["i3net"].run_name / sources[s]["i3net"].output_dir).glob("diff_*.nii.gz"))
            if s in (2, 6) else set(case_names(sources[s]["i3net"], fold)) for s in SCALES
        ]))
        for case in cases:
            for target in TARGETS:
                imgs = {s: nib.load(str(resolved(sources[s][target], s, fold, case))) for s in SCALES}
                pred = {s: imgs[s].get_fdata(dtype=np.float32) for s in SCALES}
                gt = {s: nib.load(str(resolved(sources[s]["i3net"], s, fold, case, True))).get_fdata(dtype=np.float32) for s in SCALES}
                for a, b in ((2, 4), (2, 6), (4, 6)):
                    for za, zb, distance, _ in matches(planes(imgs[a], a), planes(imgs[b], b)):
                        pa, pb = pred[a][:, :, za], pred[b][:, :, zb]
                        ea, eb = np.abs(pa - gt[a][:, :, za]), np.abs(pb - gt[b][:, :, zb])
                        inc = np.abs(pa - pb); avg_error = .5 * (ea + eb)
                        threshold = .01 * max(float(np.max(np.abs(pa))), float(np.max(np.abs(pb))), 1e-6)
                        mask = (np.abs(pa) > threshold) | (np.abs(pb) > threshold)
                        records.append({"fold": fold, "case": case, "target_model": target, "pair": f"{a}-{b}", "za": za, "zb": zb,
                            "plane_distance_mm": distance, "pixel_spearman": corr(inc[mask], avg_error[mask]),
                            "mean_inconsistency": float(np.mean(inc[mask])), "mean_error": float(np.mean(avg_error[mask])),
                            "top10_error_capture": float(np.mean(avg_error[mask][inc[mask] >= np.quantile(inc[mask], .9)]) / max(np.mean(avg_error[mask]), 1e-12))})
            print(f"completed {fold}/{case}", flush=True)
    frame = pd.DataFrame(records); frame.to_csv(OUT / "per_plane.csv", index=False)
    case = frame.groupby(["case", "target_model", "pair"], as_index=False).agg(
        inconsistency=("mean_inconsistency", "median"), error=("mean_error", "median"),
        pixel_spearman=("pixel_spearman", "median"), top10_error_capture=("top10_error_capture", "median"))
    case.to_csv(OUT / "case_pair_summary.csv", index=False)
    summary = {"cases": int(frame.case.nunique()), "planes": len(frame),
        "median_pixel_spearman": float(frame.pixel_spearman.median()),
        "pixel_spearman_iqr": [float(frame.pixel_spearman.quantile(.25)), float(frame.pixel_spearman.quantile(.75))],
        "median_top10_error_capture_ratio": float(frame.top10_error_capture.median()),
        "slice_level_spearman": corr(frame.mean_inconsistency, frame.mean_error),
        "case_pair_level_spearman": corr(case.inconsistency, case.error)}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__": main()
