"""Reopen predictions and independently recompute patient confusion/physical distances."""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path

from vs_seg_task_cpu_support import ROOT, resource_gate, load_model
from vs_seg_full_volume_cohort import CONTRACT, OUT, cases_from_sources, successful_conditions, verify_contract, write_json
from vs_seg_full_volume_runtime import array_sha, decode_source, sha, reconstruct, image_metrics


def direct_surface_metrics(prediction, reference, spacing):
    import numpy as np
    from scipy.ndimage import binary_erosion, distance_transform_edt, generate_binary_structure
    edge_p = prediction ^ binary_erosion(prediction, structure=generate_binary_structure(3, 1), border_value=0)
    edge_r = reference ^ binary_erosion(reference, structure=generate_binary_structure(3, 1), border_value=0)
    if not edge_p.any() or not edge_r.any():
        return {"status": "both_empty_undefined" if not edge_p.any() and not edge_r.any() else "one_empty_infinite"}
    # Full-grid distance transforms do not reuse the production crop optimization.
    p_to_r = distance_transform_edt(~edge_r, sampling=spacing)[edge_p]
    r_to_p = distance_transform_edt(~edge_p, sampling=spacing)[edge_r]
    return {"status": "finite", "assd_mm": float(np.r_[p_to_r, r_to_p].mean()),
            "masd_mm": float((p_to_r.mean() + r_to_p.mean()) / 2),
            "hd95_mm": float(np.quantile(np.r_[p_to_r, r_to_p], .95))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--patient")
    parser.add_argument("--regenerate", action="store_true")
    args = parser.parse_args()
    start = time.perf_counter()
    resource_gate()
    contract = verify_contract()
    import nibabel as nib
    import numpy as np
    from scipy.ndimage import binary_erosion, distance_transform_edt, generate_binary_structure
    models = {}
    if args.regenerate:
        _, runtime = load_model()
        from remind_native_t2_ixi_pair import MODELS, prepared
    errors, checked = [], []
    for case in cases_from_sources():
        if args.patient and case["patient"] != args.patient:
            continue
        records = successful_conditions(case["patient"], sha(CONTRACT))
        if not records:
            continue
        volume, affine, refs = decode_source(case)
        if args.regenerate:
            prep = prepared(volume[:, :, ::4])
        orientation = nib.orientations.ornt_transform(nib.orientations.io_orientation(affine), nib.orientations.axcodes2ornt("RAS"))
        can_affine = affine @ nib.orientations.inv_ornt_aff(orientation, volume.shape)
        spacing = nib.affines.voxel_sizes(can_affine)
        last = (volume.shape[2] - 1) // 4 * 4
        slab = np.zeros(volume.shape, dtype=bool)
        slab[:, :, :last + 1] = True
        slab = nib.orientations.apply_orientation(slab, orientation)
        references = {key: nib.orientations.apply_orientation(value, orientation) for key, value in refs.items()}
        for name, record in records.items():
            resource_gate()
            prediction_file = ROOT / record["prediction_file"]
            with np.load(prediction_file) as saved:
                prediction = saved["prediction_ras"]
                if prediction.dtype != bool or prediction.shape != slab.shape or not np.array_equal(saved["affine"], can_affine):
                    errors.append(case["patient"] + "/" + name + " prediction grid/dtype differs")
            if array_sha(prediction) != record["prediction_array_sha256"] or array_sha(volume) != record["native_array_sha256"]:
                errors.append(case["patient"] + "/" + name + " array content hash differs")
            for ref_key, reference in references.items():
                edge = reference ^ binary_erosion(reference, structure=generate_binary_structure(3, 1), border_value=0)
                keep = distance_transform_edt(~edge, sampling=spacing) > 1
                for domain_key, keep_domain in (("full", np.ones_like(slab)), ("observed_anchor_slab", slab), ("exclude_reference_boundary_1mm", keep)):
                    p, g = prediction[keep_domain], reference[keep_domain]
                    tp = int(np.count_nonzero(p & g))
                    fp = int(p.sum()) - tp
                    fn = int(g.sum()) - tp
                    reported = record["task_metrics"][ref_key][domain_key]
                    if tuple(reported[k] for k in ("tp", "fp", "fn")) != (tp, fp, fn):
                        errors.append(case["patient"] + "/" + name + "/" + ref_key + "/" + domain_key + " confusion counts differ")
                    denom = 2 * tp + fp + fn
                    expected = 2 * tp / denom if denom else None
                    if domain_key == "exclude_reference_boundary_1mm" and not g.any():
                        expected = None
                    if expected is None and reported["dice"] is not None or expected is not None and (reported["dice"] is None or abs(reported["dice"] - expected) > 1e-12):
                        errors.append(case["patient"] + "/" + name + " Dice differs")
                    if domain_key == "full":
                        recomputed = direct_surface_metrics(prediction, reference, spacing)
                        if recomputed["status"] != reported["boundary"]["status"]:
                            errors.append(case["patient"] + "/" + name + " empty-boundary status differs")
                        if recomputed["status"] == "finite" and any(abs(recomputed[k] - reported["boundary"][k]) > 1e-10 for k in ("assd_mm", "masd_mm", "hd95_mm")):
                            errors.append(case["patient"] + "/" + name + " full-grid physical boundary distances differ")
            rows = record["per_plane_image_errors"]
            if [r["z"] for r in rows] != [z for z in range(1, last) if z % 4]:
                errors.append(case["patient"] + "/" + name + " target list differs")
            for region, summary in record["image_metrics"].items():
                valid = [r[region] for r in rows if r[region]["pixels"]]
                n = sum(r["pixels"] for r in valid)
                target = float(np.mean([r["nmse"] for r in valid])) if valid else None
                weighted = sum(r["sse"] for r in valid) / n if n else None
                if summary["pixels"] != n or summary["target_equal_nmse"] != target or summary["pixel_weighted_nmse"] != weighted:
                    errors.append(case["patient"] + "/" + name + " saved image aggregation differs")
            if args.regenerate:
                if name in MODELS and name not in models:
                    models[name] = MODELS[name][0](MODELS[name][1], device="cpu")
                regenerated = reconstruct(name, volume, prep, models)
                if array_sha(regenerated) != record["reconstructed_array_sha256"]:
                    errors.append(case["patient"] + "/" + name + " regenerated reconstruction content hash differs")
                summaries, regenerated_rows = image_metrics(regenerated, volume, refs, float(prep[2] - prep[1]))
                if summaries != record["image_metrics"] or regenerated_rows != record["per_plane_image_errors"]:
                    errors.append(case["patient"] + "/" + name + " regenerated image statistics differ")
                del regenerated
            checked.append({"patient": case["patient"], "condition": name, "prediction_sha256": sha(prediction_file)})
    if args.patient and not checked:
        errors.append("Requested patient has no completed conditions")
    report = {"script_sha256": sha(Path(__file__)), "contract_sha256": sha(CONTRACT), "checked_conditions": checked,
              "errors": errors, "elapsed_seconds": time.perf_counter() - start,
              "checks": ["source and prediction hashes", "physical grid", "confusion counts", "two labels", "slab", "1mm reference band", "independent full-grid ASSD/HD95", "saved image aggregation"],
              "reconstruction_pixels_independently_regenerated": args.regenerate,
              "publication_confirmation": False, "main_denominator": len(contract["main_roster"])}
    target = OUT / ("verification_" + (args.patient or "all") + ".json")
    write_json(target, report)
    print(json.dumps({"checked_conditions": len(checked), "errors": errors, "seconds": report["elapsed_seconds"]}), flush=True)
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
