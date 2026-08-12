from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import nibabel as nib
import numpy as np

from .cross_scale_protocol import ningxia_case_group, ningxia_test_group
from .optimization_protocol import (
    ANALYTICAL, FAMILIES, PRIMARY_TARGETS, REPO_ROOT, UNIVERSAL_NEURAL,
    analytical_path, case_names, folds, gt_path, prediction_path, profile_sources,
)

OUT = Path(__file__).resolve().parent / "outputs" / "optimization"


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    profiles = [("ixi", 4)] + [(d, s) for d in ("fastmri", "ningxia") for s in (2, 4, 6)]
    registry: list[dict] = []
    issues: list[str] = []
    availability: dict[str, list[str]] = {}
    for dataset, scale in profiles:
        sources = profile_sources(dataset, scale)
        reference = sources["i3net"]
        expected_all: list[str] = []
        by_fold: dict[str, tuple[str, ...]] = {}
        for fold in folds(dataset):
            cases = case_names(reference, fold)
            by_fold[fold or ""] = cases
            expected_all.extend(cases)
        for method in tuple(sources) + ANALYTICAL:
            count = 0
            missing: list[str] = []
            shape_bad = affine_bad = finite_bad = oof_bad = 0
            mins: list[float] = []
            maxs: list[float] = []
            first_path = ""
            for fold in folds(dataset):
                held_out = ningxia_test_group(REPO_ROOT, fold) if fold else ""
                for case in by_fold[fold or ""]:
                    path = analytical_path(reference, fold, method, case) if method in ANALYTICAL else prediction_path(sources[method], fold, case)
                    if not path.exists():
                        missing.append(str(path))
                        continue
                    if not first_path:
                        first_path = str(path.parent)
                    gt_image = nib.load(str(gt_path(reference, fold, case)))
                    image = nib.load(str(path))
                    data = image.get_fdata(dtype=np.float32)
                    count += 1
                    shape_bad += int(data.shape != gt_image.shape)
                    affine_bad += int(not np.allclose(image.affine, gt_image.affine, atol=1e-5, rtol=0.0))
                    finite_bad += int(not np.isfinite(data).all())
                    if fold:
                        oof_bad += int(ningxia_case_group(case) != held_out)
                    mins.append(float(np.nanmin(data)))
                    maxs.append(float(np.nanmax(data)))
            expected = len(expected_all)
            status = "passed" if count == expected and not missing and shape_bad == affine_bad == finite_bad == oof_bad == 0 else "failed"
            profile = f"{dataset}_x{scale}"
            if status == "passed":
                availability.setdefault(method, []).append(profile)
            else:
                issues.append(f"{profile}/{method}: count={count}/{expected}, missing={len(missing)}, shape={shape_bad}, affine={affine_bad}, finite={finite_bad}, oof={oof_bad}")
            registry.append({
                "canonical_method": method,
                "architecture_family": FAMILIES[method],
                "analytical_or_neural": "analytical" if method in ANALYTICAL else "neural",
                "dataset": dataset,
                "scale": scale,
                "case_count": count,
                "expected_cases": expected,
                "prediction_path": first_path,
                "output_shape_status": "passed" if shape_bad == 0 else "failed",
                "affine_status": "passed" if affine_bad == 0 else "failed",
                "intensity_min": min(mins) if mins else "",
                "intensity_max": max(maxs) if maxs else "",
                "out_of_fold": "passed" if dataset == "ningxia" and oof_bad == 0 else ("not_applicable" if dataset != "ningxia" else "failed"),
                "can_be_target": method in PRIMARY_TARGETS and status == "passed",
                "can_be_committee_member": status == "passed",
                "audit_status": status,
                "exclusion_reason": "" if status == "passed" else "missing_or_invalid_profile",
                "inference_cost": "unknown" if method not in ANALYTICAL else "cpu_low",
            })
    write_csv(OUT / "model_bank_registry.csv", registry)
    universal_profiles = {f"{d}_x{s}" for d in ("fastmri", "ningxia") for s in (2, 4, 6)}
    universal = [m for m in UNIVERSAL_NEURAL + ANALYTICAL if universal_profiles.issubset(set(availability.get(m, [])))]
    x4 = [m for m, profiles_ in availability.items() if any(p.endswith("_x4") for p in profiles_)]
    lines = [
        "# Model Bank Audit", "", f"Generated: {datetime.now(timezone.utc).isoformat()}", "",
        "## Universal multiscale bank", "", ", ".join(universal) or "None", "",
        "These methods passed identity, shape, affine, finite-value, and NingXia OOF checks on all six fastMRI/NingXia profiles.", "",
        "## Expanded factor-four bank", "", ", ".join(sorted(x4)), "",
        "## Role separation", "",
        "Main universal targets are I3Net, HAT, and SwinIR because they are available in IXI development and all multiscale profiles. Other valid neural outputs are committee candidates until development-only fidelity and complementarity screening is complete.", "",
        "## Audit issues", "",
    ]
    lines.extend(f"- {issue}" for issue in issues) if issues else lines.append("No integrity failures.")
    (OUT / "MODEL_BANK_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"universal={universal}")
    print(f"rows={len(registry)} issues={len(issues)} output={OUT}")


if __name__ == "__main__":
    main()
