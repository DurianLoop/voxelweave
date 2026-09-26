"""Extended geometry audit for PC-v1-FROZEN; writes only under paper."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "plan2_outputs"
sys.path.insert(0, str(ROOT / "design"))
from rasinet.optimization_protocol import profile_sources, prediction_path  # noqa: E402


def resolved_prediction(dataset: str, scale: int, source, fold: str | None, case: str) -> Path:
    path = prediction_path(source, fold, case)
    if path.exists():
        return path
    if dataset == "ningxia" and scale in (2, 6):
        archived = ROOT / "baseline" / f"{source.root.name}_root_results_202607"
        candidate = archived / "runs" / str(fold) / source.run_name / source.output_dir / f"diff_{case}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(path)


def geometry(img: nib.spatialimages.SpatialImage) -> dict[str, object]:
    affine = np.asarray(img.affine, float)
    vectors = affine[:3, :3]
    spacing = np.linalg.norm(vectors, axis=0)
    normal = vectors[:, 2] / max(spacing[2], 1e-12)
    return {
        "shape": tuple(int(v) for v in img.shape),
        "spacing": spacing,
        "normal": normal,
        "orientation": "".join(nib.aff2axcodes(affine)),
        "fov_xy": spacing[:2] * np.asarray(img.shape[:2]),
        "affine": affine,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source_rows = pd.read_csv(ROOT / "design" / "rasinet" / "outputs" / "nested_optimization" / "cross_scale_physical_pair_scores.csv")
    records = []
    for row in source_rows.itertuples(index=False):
        fold = None if row.fold == "none" else row.fold
        sources_a = profile_sources(row.dataset, int(row.scale_a))
        sources_b = profile_sources(row.dataset, int(row.scale_b))
        ga = geometry(nib.load(str(resolved_prediction(row.dataset, int(row.scale_a), sources_a[row.target_model], fold, row.case))))
        gb = geometry(nib.load(str(resolved_prediction(row.dataset, int(row.scale_b), sources_b[row.target_model], fold, row.case))))
        cosine = float(np.clip(abs(np.dot(ga["normal"], gb["normal"])), -1, 1))
        records.append({
            "dataset": row.dataset, "fold": row.fold, "case": row.case, "target_model": row.target_model,
            "scale_a": row.scale_a, "scale_b": row.scale_b,
            "orientation_a": ga["orientation"], "orientation_b": gb["orientation"],
            "normal_angle_deg": float(np.degrees(np.arccos(cosine))),
            "inplane_spacing_max_abs_delta_mm": float(np.max(np.abs(ga["spacing"][:2] - gb["spacing"][:2]))),
            "slice_step_abs_delta_mm": float(abs(ga["spacing"][2] - gb["spacing"][2])),
            "fov_xy_max_abs_delta_mm": float(np.max(np.abs(ga["fov_xy"] - gb["fov_xy"]))),
            "inplane_shape_equal": ga["shape"][:2] == gb["shape"][:2],
            "orientation_equal": ga["orientation"] == gb["orientation"],
            "affine_max_abs_delta": float(np.max(np.abs(ga["affine"] - gb["affine"]))),
            "matched_generated_planes": int(row.matched_generated_planes),
            "max_plane_distance_mm": float(row.max_plane_distance_mm),
        })
    frame = pd.DataFrame(records)
    frame.to_csv(OUT / "extended_geometry_audit.csv", index=False)
    summary = {
        "records": len(frame),
        "all_inplane_shapes_equal": bool(frame.inplane_shape_equal.all()),
        "all_orientations_equal": bool(frame.orientation_equal.all()),
        "max_normal_angle_deg": float(frame.normal_angle_deg.max()),
        "max_inplane_spacing_delta_mm": float(frame.inplane_spacing_max_abs_delta_mm.max()),
        "max_slice_step_delta_mm": float(frame.slice_step_abs_delta_mm.max()),
        "max_fov_xy_delta_mm": float(frame.fov_xy_max_abs_delta_mm.max()),
        "max_affine_abs_delta": float(frame.affine_max_abs_delta.max()),
        "max_matched_plane_distance_mm": float(frame.max_plane_distance_mm.max()),
        "minimum_matched_planes": int(frame.matched_generated_planes.min()),
    }
    (OUT / "extended_geometry_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
