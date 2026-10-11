"""Independent scalar-tile / actual-pixel verification of the post-result oracle.

No producer analysis functions, optimization routines or neural networks are used.
Source arrays are decoded again; SciPy PCHIP replaces the producer's Hermite code.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import nibabel as nib
import numpy as np
import pydicom
from scipy.interpolate import PchipInterpolator
from vs_seg_task_cpu_support import ROOT, resource_gate

OUT = ROOT / "experiments/mc_rc_five_developer_constrained_oracle"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1_048_576), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def source(case):
    header = case["header"]
    objects = []
    with zipfile.ZipFile(ROOT / header["transfer"]["file"]) as archive:
        for name in header["summary"]["ordered_zip_members"]:
            with archive.open(name) as stream:
                objects.append(pydicom.dcmread(stream))
    iop = np.asarray(objects[0].ImageOrientationPatient, dtype=float)
    locations = [np.dot(np.asarray(d.ImagePositionPatient, dtype=float), np.cross(iop[:3], iop[3:])) for d in objects]
    if not np.all(np.diff(locations) > 0):
        raise ValueError("Source order is not increasing native position")
    image = np.stack([d.pixel_array.astype(np.float32) * float(d.get("RescaleSlope", 1)) + float(d.get("RescaleIntercept", 0)) for d in objects], axis=-1)
    label_img = nib.load(ROOT / case["label"]["label_file"])
    transform = np.linalg.solve(np.asarray(header["summary"]["affine_rcz_ras"]), label_img.affine)
    label = nib.orientations.apply_orientation(np.asarray(label_img.dataobj) != 0, nib.orientations.io_orientation(transform))
    if image.shape != label.shape or not np.isfinite(image).all():
        raise ValueError("Source array / label gate failed")
    return image, label


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    initial_resource = resource_gate()
    result, frozen = read(OUT / "attempt_01.json"), read(OUT / "run_contract.json")
    errors, checked = [], []

    def require(ok, message):
        if not ok:
            errors.append(message)

    def close(actual, expected, message, atol=1e-10, rtol=1e-7):
        require(np.allclose(actual, expected, rtol=rtol, atol=atol), message)

    require(result["complete"] and len(result["patients"]) == 5, "Incomplete fixed-five result")
    require(sha(OUT / "run_contract.json") == result["run_contract_sha256"], "Run contract changed")
    for entry in frozen["files"]:
        path = (ROOT.parent / entry["path"]).resolve()
        require(path.is_relative_to(ROOT) and path.is_file() and sha(path) == entry["sha256"], "Frozen lineage changed: " + entry["path"])
    require([p["patient"] for p in result["patients"]] == ["VS-MC-RC-001", "VS-MC-RC-002", "VS-MC-RC-004", "VS-MC-RC-005", "VS-MC-RC-006"], "Fixed roster changed")
    total_targets = total_tiles = 0
    for patient in result["patients"]:
        resource_gate()
        name = patient["patient"]
        begin_errors = len(errors)
        contract = read(ROOT / patient["source_contract"])
        original = read((ROOT / patient["source_contract"]).parent / "attempt_01.json")
        old_proof = read((ROOT / patient["source_contract"]).parent / "independent_numerical_and_forward_verification.json")
        require(not old_proof["errors"] and old_proof["result_sha256"] == sha((ROOT / patient["source_contract"]).parent / "attempt_01.json"), "Original sampled-forward proof changed: " + name)
        case = next(c for c in contract["cases"] if c["patient"] == name)
        saved = next(p for p in original["patients"] if p["patient"] == name)
        old_action = next(a for a in saved["actions"] if a["base"] == "raw_pchip")
        native, label = source(case)
        with np.load(ROOT / saved["hat_file"]) as bundle:
            hat = bundle["image_rcz"]
        require(sha(ROOT / saved["hat_file"]) == saved["hat_sha256"], "HAT artifact changed: " + name)
        require(sha(ROOT / patient["coefficients_file"]) == patient["coefficients_sha256"], "Coefficient artifact changed: " + name)
        with np.load(ROOT / patient["coefficients_file"]) as bundle:
            coef_saved, keys, alpha, unalpha = [bundle[k] for k in ("coefficients", "tile_z_row_col", "constrained_alpha", "unconstrained_alpha")]
            npz_limits = bundle["lesion_limits"]
        require(np.isfinite(alpha).all() and ((alpha >= 0) & (alpha <= 1)).all(), "Invalid box solution: " + name)
        observations = list(range(0, native.shape[2], 4))
        targets = [z for z in range(1, observations[-1]) if z % 4]
        require(observations == saved["observation_indices"] and targets == saved["targets"], "Observation/target convention differs: " + name)
        observed = native[:, :, observations]
        span = float(observed.max()) - float(observed.min())
        interpolator = PchipInterpolator(observations, observed.astype(float), axis=2)
        lesion_counts = {}
        for z in targets:
            left, right = observed[:, :, z // 4], observed[:, :, z // 4 + 1]
            mask = (np.abs(left) > .01 * max(float(np.abs(left).max()), 1e-6)) | (np.abs(right) > .01 * max(float(np.abs(right).max()), 1e-6))
            lesion_counts[z] = int((mask & label[:, :, z]).sum())
        nonempty = sum(n > 0 for n in lesion_counts.values())
        total_roi = sum(lesion_counts.values())
        require(nonempty > 0 and total_roi > 0, "Empty lesion endpoint: " + name)
        coefficients, actual_keys = [], []
        plane_metrics = {tag: [] for tag in ("baseline", "candidate", "unconstrained", "constrained")}
        alpha_lookup = {tuple(k): (float(a), float(u)) for k, a, u in zip(keys, alpha, unalpha)}
        for z in targets:
            i, phase = z // 4, (z % 4) / 4
            if i == 0 or i + 2 >= len(observations):
                base = ((1 - phase) * observed[:, :, i] + phase * observed[:, :, i + 1]).astype(np.float32)
            else:
                base = interpolator(z).astype(np.float32)
            left, right = observed[:, :, i], observed[:, :, i + 1]
            support = (np.abs(left) > .01 * max(float(np.abs(left).max()), 1e-6)) | (np.abs(right) > .01 * max(float(np.abs(right).max()), 1e-6))
            roi = support & label[:, :, z]
            e = (native[:, :, z].astype(float) - base) / span
            delta = (hat[:, :, z].astype(float) - base) / span
            a_map, u_map = np.zeros(base.shape), np.zeros(base.shape)
            for rr in range(0, base.shape[0], 32):
                for cc in range(0, base.shape[1], 32):
                    sl = np.s_[rr:rr + 32, cc:cc + 32]
                    if not support[sl].any():
                        continue
                    key = (z, rr, cc)
                    require(key in alpha_lookup, "Missing scalar tile: " + name + str(key))
                    a, u = alpha_lookup[key]
                    a_map[sl], u_map[sl] = a, u
                    row = []
                    for mask, factor in ((support[sl], int(support.sum()) * len(targets)), (roi[sl], int(roi.sum()) * nonempty), (roi[sl], total_roi)):
                        ev, dv = e[sl][mask], delta[sl][mask]
                        row.extend([float(np.dot(ev, ev)) / factor if factor else 0., float(np.dot(ev, dv)) / factor if factor else 0., float(np.dot(dv, dv)) / factor if factor else 0.])
                    coefficients.append(row)
                    actual_keys.append(key)
            for tag, a in (("baseline", 0.), ("candidate", 1.), ("unconstrained", u_map), ("constrained", a_map)):
                # Reconstruct actual normalized pixel errors, independently of coefficients.
                square = (e - a * delta) ** 2
                plane_metrics[tag].append({"z": z, "support_pixels": int(support.sum()), "support_sse": float(square[support].sum()), "lesion_pixels": int(roi.sum()), "lesion_sse": float(square[roi].sum())})
        coef = np.asarray(coefficients)
        require(np.array_equal(actual_keys, keys), "Tile ordering differs: " + name)
        close(coef, coef_saved, "Scalar-tile coefficients differ: " + name, atol=1e-14)
        def aggregate(rows):
            les = [r for r in rows if r["lesion_pixels"]]
            return np.asarray([np.mean([r["support_sse"] / r["support_pixels"] for r in rows]), np.mean([r["lesion_sse"] / r["lesion_pixels"] for r in les]), sum(r["lesion_sse"] for r in les) / total_roi])
        values = {tag: aggregate(rows) for tag, rows in plane_metrics.items()}
        limits = np.minimum(values["baseline"][1:], values["candidate"][1:])
        for tag in ("baseline", "candidate", "unconstrained"):
            close(values[tag], patient[tag + "_losses"], "Actual pixel endpoint differs: " + name + " " + tag)
        solution = patient["solution"]
        close(limits, solution["lesion_limits"], "Actual pixel guard limits differ: " + name)
        close(limits, npz_limits, "NPZ guard limits differ: " + name)
        close(values["constrained"], solution["losses_support_lesion_equal_lesion_pixel"], "Actual pixel constrained losses differ: " + name)
        lam = np.asarray(solution["multipliers"])
        require(np.isfinite(lam).all() and (lam >= 0).all(), "Nonnegative dual multiplier gate failed: " + name)
        b = coef[:, 0] + lam[0] * coef[:, 3] + lam[1] * coef[:, 6]
        m = coef[:, 1] + lam[0] * coef[:, 4] + lam[1] * coef[:, 7]
        d = coef[:, 2] + lam[0] * coef[:, 5] + lam[1] * coef[:, 8]
        require((coef[:, [0, 2, 3, 5, 6, 8]] >= 0).all(), "Invalid nonnegative square coefficients: " + name)
        vertex = np.divide(m, d, out=np.zeros_like(m), where=d > 0)
        interior = (vertex >= 0) & (vertex <= 1) & (d > 0)
        minimum = np.minimum(b, b - 2 * m + d)
        minimum[interior] = np.minimum(minimum[interior], b[interior] - m[interior] ** 2 / d[interior])
        # Independent lower bound is a sum of scalar quadratic minima, not
        # the producer's evaluation of the Lagrangian at its chosen alpha.
        dual = float(minimum.sum() - np.dot(lam, limits))
        primal = float(values["constrained"][0])
        gap = primal - dual
        violation = values["constrained"][1:] - limits
        gradient = 2 * (d * alpha - m)
        residual = np.where(alpha <= 0, np.minimum(gradient, 0), np.where(alpha >= 1, np.maximum(gradient, 0), gradient))
        stationarity = float(np.max(np.abs(residual)))
        complementary = float(np.max(np.abs(lam * violation)))
        certified = bool(np.isfinite(values["constrained"]).all() and np.isfinite(dual) and (violation <= 1e-10).all() and -1e-10 <= gap <= 1e-8 and stationarity <= 1e-8 and (lam >= 0).all() and ((alpha >= 0) & (alpha <= 1)).all())
        gain = 10 * math.log10(min(values["baseline"][0], values["candidate"][0]) / primal)
        close(gain, patient["constrained_support_gain_db_vs_better_fixed"], "Actual pixel gain differs: " + name, atol=1e-10)
        close(dual, solution["dual_lower_bound"], "Independent dual lower bound differs: " + name, atol=1e-12)
        require(certified == solution["numerically_certified"] and (certified and gain >= .1) == patient["post_result_constrained_space_gate_passed"], "Numerical / diagnostic gate differs: " + name)
        require(old_action["development_gate_passed"] == patient["unconstrained_original_gate_passed"], "Original failure changed: " + name)
        item = {"patient": name, "targets": len(targets), "tiles": len(keys), "actual_pixel_losses": {k: v.tolist() for k, v in values.items()}, "maximum_coefficient_abs_difference": float(np.max(np.abs(coef - coef_saved))), "violations": violation.tolist(), "dual_lower_bound_independent_scalar_minima": dual, "primal_dual_gap": gap, "box_stationarity_residual": stationarity, "complementary_slackness_residual": complementary, "numerically_certified": certified, "gain_db": gain, "patient_errors": errors[begin_errors:], "post_result_space_gate_passed": certified and gain >= .1, "independent_confirmation": False}
        checked.append(item)
        total_targets += len(targets)
        total_tiles += len(keys)
        print(json.dumps({k: item[k] for k in ("patient", "targets", "tiles", "gain_db", "numerically_certified", "patient_errors")}), flush=True)
        del native, label, hat, observed, interpolator
    all_pass = all(p["post_result_space_gate_passed"] for p in checked)
    require(total_targets == 240 and all_pass == result["all_five_constrained_space_gate_passed"], "Fixed-five aggregate differs")
    require(result["original_unconstrained_raw_gate_passed"] is False and result["post_result_diagnostic"] is True and result["publication_claim_confirmed"] is False, "Scientific conclusion changed")
    proof = {"created_utc": datetime.now(timezone.utc).isoformat(), "verification_script_sha256": sha(__file__), "result_sha256": sha(OUT / "attempt_01.json"), "run_contract_sha256": sha(OUT / "run_contract.json"), "scope": "Fresh raw decode; independent SciPy PCHIP, scalar tile coefficients, actual-pixel endpoint/constraint recomputation and scalar-minimum dual/KKT check", "initial_resource_gate": initial_resource, "patients": checked, "targets": total_targets, "tiles": total_tiles, "errors": errors, "all_five_constrained_space_gate_passed": all_pass, "original_unconstrained_raw_gate_passed": False, "neural_networks_executed": 0, "full_HAT_output_regenerated": False, "prior_HAT_sampled_forward_proofs_checked": True, "gpu_used": False, "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False}
    (OUT / "independent_pixel_and_dual_verification.json").write_text(json.dumps(proof, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: proof[k] for k in ("targets", "tiles", "errors", "all_five_constrained_space_gate_passed")}), flush=True)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
