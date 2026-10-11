"""Pre-freeze brute-force metric checks and previously seen 001 equivalence only."""
from __future__ import annotations
import json
import time
import traceback
from pathlib import Path

from vs_seg_task_cpu_support import ROOT, load_model, resource_gate
from vs_seg_full_volume_runtime import CONDITIONS, array_sha, image_metrics, inference, load_tuple_inferer, reconstruct, sha
from vs_seg_full_volume_metrics import boundary_distances, outside_reference_band, paired_bootstrap, surface, task_metrics

OUT = ROOT / "experiments/vs_seg_full_volume_development_checks"


def metric_checks():
    import numpy as np
    from scipy.spatial.distance import cdist
    from scipy.ndimage import binary_erosion, generate_binary_structure
    tests, errors = [], []
    spacing = np.array([.46875, .46875, 1.5])
    a = np.zeros((9, 10, 11), dtype=bool)
    a[1:6, 2:7, 3:8] = True
    b = np.zeros_like(a)
    b[2:7, 2:7, 3:8] = True
    small = np.zeros_like(a)
    small[2:4, 3:5, 4:6] = True
    for name, p, g in (("identical", a, a), ("translated", b, a), ("border_touching", np.roll(a, -2, axis=0), a), ("unequal_surface_sizes", small, a), ("single_voxel", None, None)):
        if name == "single_voxel":
            p = np.zeros_like(a)
            p[4, 5, 6] = True
            g = np.zeros_like(a)
            g[4, 5, 5] = True
        points_p = np.argwhere(surface(p)) * spacing
        points_g = np.argwhere(surface(g)) * spacing
        distances = cdist(points_p, points_g)
        directed_p, directed_g = distances.min(axis=1), distances.min(axis=0)
        expected = [np.r_[directed_p, directed_g].mean(), np.percentile(np.r_[directed_p, directed_g], 95), (directed_p.mean() + directed_g.mean()) / 2]
        actual = boundary_distances(p, g, spacing)
        difference = max(abs(actual["assd_mm"] - expected[0]), abs(actual["hd95_mm"] - expected[1]), abs(actual["masd_mm"] - expected[2]))
        if difference > 1e-12:
            errors.append(name + " boundary distance differs from all-pairs physical coordinates")
        domain = np.ones(a.shape, dtype=bool)
        domain[:, :, 9:] = False
        computed = task_metrics(p, g, spacing, domain)
        vals = np.array([(bool(pp), bool(gg)) for pp, gg in zip(p.ravel(), g.ravel())])
        tp = int(sum(pp and gg for pp, gg in vals))
        fp = int(sum(pp and not gg for pp, gg in vals))
        fn = int(sum(not pp and gg for pp, gg in vals))
        if (tp, fp, fn) != tuple(computed["full"][k] for k in ("tp", "fp", "fn")):
            errors.append(name + " confusion counts differ from voxel loop")
        grid = np.indices(g.shape).reshape(3, -1).T * spacing
        min_dist = cdist(grid, points_g).min(axis=1).reshape(g.shape)
        if not np.array_equal(outside_reference_band(g, spacing), min_dist > 1):
            errors.append(name + " reference band differs from all-pairs distances")
        reordered = boundary_distances(p.transpose(2, 0, 1), g.transpose(2, 0, 1), spacing[[2, 0, 1]])
        if abs(reordered["assd_mm"] - expected[0]) > 1e-12 or abs(reordered["hd95_mm"] - expected[1]) > 1e-12:
            errors.append(name + " metric changed under axis/spacing permutation")
        tests.append({"name": name, "max_boundary_error_mm": difference})
    empty = np.zeros_like(a)
    if boundary_distances(empty, a, spacing)["status"] != "one_empty_infinite" or task_metrics(empty, a, spacing, np.ones_like(a))["full"]["dice"] != 0:
        errors.append("Empty prediction convention differs")
    if boundary_distances(empty, empty, spacing)["status"] != "both_empty_undefined":
        errors.append("Both-empty convention differs")
    singleton = empty.copy()
    singleton[3, 3, 3] = True
    core = task_metrics(singleton, singleton, spacing, np.ones_like(a))["exclude_reference_boundary_1mm"]
    if core["dice"] is not None or not core["reference_core_empty"]:
        errors.append("Empty reference core was treated as finite Dice")
    values = np.array([-.2, .1, -.05, -.4, .01])
    boot = paired_bootstrap(values)
    rng = np.random.default_rng(20261012)
    means = [sum(values[j] for j in rng.integers(0, len(values), size=len(values))) / len(values) for _ in range(5000)]
    if not np.allclose(boot["ci95_percentile"], np.percentile(means, [2.5, 97.5]), atol=1e-15, rtol=0):
        errors.append("Bootstrap differs from independent patient loop")
    constant = paired_bootstrap([-1] * 45)
    if constant["ci95_percentile"] != [-1, -1]:
        errors.append("Constant-difference bootstrap incorrect")
    return {"tests": tests, "empty_conventions_checked": True, "patient_bootstrap_checked": True}, errors


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    result = {"attempt": attempt, "complete": False, "patient": "VS-SEG-001", "heldout_pixels_read": False,
              "script_sha256": sha(Path(__file__)), "runtime_script_sha256": sha(ROOT / "experiments/vs_seg_full_volume_runtime.py"),
              "metrics_script_sha256": sha(ROOT / "experiments/vs_seg_full_volume_metrics.py"), "errors": []}
    start = time.perf_counter()
    try:
        result["resources"] = resource_gate()
        result["metric_checks"], result["errors"] = metric_checks()
        segmenter, runtime = load_model()
        import nibabel as nib
        import numpy as np
        import torch
        from remind_native_t2_ixi_pair import MODELS, prepared
        old_dir = ROOT / "experiments/vs_seg_001_full_volume_cpu_preflight"
        previous = json.loads((old_dir / "attempt_01.json").read_text())
        original = {r["condition"]: r for r in previous["conditions"]}
        native_file = ROOT / original["native"]["reconstruction_file"]
        with np.load(native_file) as data:
            volume, affine = data["image_rcz"], data["affine_rcz_ras"]
        with np.load(ROOT / "experiments/vs_seg_original_mask_cpu_development/VS-SEG-001_masks_attempt_03.npz") as data:
            refs = {"original_json": data["original_mask_rcz"], "rtstruct": data["rtstruct_mask_rcz"]}
        prep = prepared(volume[:, :, ::4])
        models = {name: MODELS[name][0](MODELS[name][1], device="cpu") for name in ("hat", "swinir")}
        orientation = nib.orientations.ornt_transform(nib.orientations.io_orientation(affine), nib.orientations.axcodes2ornt("RAS"))
        infer = load_tuple_inferer()
        result["runtime"] = runtime
        result["equivalence"] = []
        for name in CONDITIONS:
            generated = reconstruct(name, volume, prep, models)
            saved = np.load(ROOT / original[name]["reconstruction_file"])["image_rcz"]
            equal = np.array_equal(generated, saved)
            if not equal:
                result["errors"].append(name + " reconstructed pixels differ from fixed 001 output")
            metrics, rows = image_metrics(generated, volume, refs, float(prep[2] - prep[1]))
            error = abs(metrics["support"]["target_equal_nmse"] - original[name]["image_metrics"]["support"]["target_equal_nmse"])
            if error > 1e-14:
                result["errors"].append(name + " support NMSE differs from preflight")
            record = {"condition": name, "bitwise_reconstruction_equal": equal,
                      "max_pixel_difference": float(np.max(abs(generated - saved))), "support_nmse_difference": error,
                      "array_sha256": array_sha(generated), "targets": len(rows)}
            if name == "pipeline_pchip":
                prediction = inference(segmenter, infer, generated, orientation)
                old_prediction = np.load(ROOT / original[name]["prediction_file"])["prediction_ras"]
                record["bitwise_prediction_equal"] = bool(np.array_equal(prediction, old_prediction))
                if not record["bitwise_prediction_equal"]:
                    result["errors"].append("Generalized inference differs from 001 saved prediction")
            result["equivalence"].append(record)
            print(json.dumps(record), flush=True)
        # Test the actual 448-grid, eight-window code path using padded development pixels.
        padded = np.pad(volume, ((32, 32), (32, 32), (0, 0)))
        grid_start = time.perf_counter()
        synthetic_pred = inference(segmenter, infer, padded, orientation)
        result["synthetic_448_eight_window_probe"] = {"shape": list(synthetic_pred.shape), "seconds": time.perf_counter() - grid_start,
                                                    "prediction_sha256": array_sha(synthetic_pred), "scientific_endpoint": False,
                                                    "input": "001 padded 32 zero voxels on each in-plane side"}
        result["cuda_initialized"] = torch.cuda.is_initialized()
        result["complete"] = not result["errors"] and not result["cuda_initialized"]
    except Exception as exc:
        result.update({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
        result["errors"].append(result["error"])
    result["elapsed_seconds"] = time.perf_counter() - start
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"complete": result["complete"], "errors": result["errors"], "seconds": result["elapsed_seconds"]}), flush=True)
    if not result["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
