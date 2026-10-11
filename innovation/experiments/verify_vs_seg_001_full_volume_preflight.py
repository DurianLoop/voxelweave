"""Independently reopen volumes/predictions and check the frozen CPU preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/vs_seg_001_full_volume_cpu_preflight"


def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    path = OUT / "attempt_01.json"
    result = json.loads(path.read_text())
    errors = []
    if not result["complete"] or result["cuda_initialized"] or len(result["conditions"]) != 7:
        errors.append("Preflight did not complete seven CPU conditions")
    records = {r["condition"]: r for r in result["conditions"]}
    native_file = ROOT / records["native"]["reconstruction_file"]
    native = np.load(native_file)["image_rcz"]
    affine = np.load(native_file)["affine_rcz_ras"]
    label_file = ROOT / "experiments/vs_seg_original_mask_cpu_development/VS-SEG-001_masks_attempt_03.npz"
    original = np.load(label_file)["original_mask_rcz"]
    transform = nib.orientations.ornt_transform(nib.orientations.io_orientation(affine), nib.orientations.axcodes2ornt("RAS"))
    reference = nib.orientations.apply_orientation(original, transform)
    observed = np.arange(0, native.shape[2], 4)
    target_indices = [i for i in range(observed[-1]) if i % 4]
    span = float(native[:, :, observed].max() - native[:, :, observed].min())
    verified = []
    for name, r in records.items():
        reconstruction_file = ROOT / r["reconstruction_file"]
        prediction_file = ROOT / r["prediction_file"]
        if sha(reconstruction_file) != r["reconstruction_sha256"] or sha(prediction_file) != r["prediction_sha256"]:
            errors.append(name + ": saved output hash differs")
        generated = np.load(reconstruction_file)["image_rcz"]
        prediction = np.load(prediction_file)["prediction_ras"]
        if not np.array_equal(native[:, :, observed], generated[:, :, observed]):
            errors.append(name + ": observed planes modified")
        if name != "native" and not np.array_equal(generated[:, :, observed[-1] + 1:], np.repeat(native[:, :, observed[-1], None], native.shape[2] - observed[-1] - 1, axis=2)):
            errors.append(name + ": unsupported terminal convention differs")
        if name == "raw_linear":
            for z in target_indices:
                t = z % 4 / 4
                expected = (1 - t) * native[:, :, z - z % 4] + t * native[:, :, z - z % 4 + 4]
                if not np.array_equal(expected, generated[:, :, z]):
                    errors.append("Raw linear formula mismatch")
                    break
        tp = int(np.count_nonzero(prediction & reference))
        fp = int(np.count_nonzero(prediction & ~reference))
        fn = int(np.count_nonzero(~prediction & reference))
        dice = 2 * tp / (2 * tp + fp + fn)
        if (tp, fp, fn) != (r["tp"], r["fp"], r["fn"]) or abs(dice - r["dice"]) > 1e-12:
            errors.append(name + ": task score differs")
        rows = []
        largest = 0.0
        for z, saved in zip(target_indices, r["per_plane_image_errors"]):
            left, right = native[:, :, z - z % 4], native[:, :, z - z % 4 + 4]
            support = (abs(left) > .01 * abs(left).max()) | (abs(right) > .01 * abs(right).max())
            lesion = support & original[:, :, z]
            squared = ((generated[:, :, z].astype(np.float64) - native[:, :, z].astype(np.float64)) / span) ** 2
            if saved["z"] != z or saved["support_pixels"] != int(support.sum()) or saved["lesion_pixels"] != int(lesion.sum()):
                errors.append(name + ": target or evaluation domain differs")
            largest = max(largest, abs(float(squared[support].mean()) - saved["support_nmse"]))
            rows.append((float(squared[support].mean()), float(squared[lesion].mean()) if lesion.any() else None))
        if largest > 1e-9:
            errors.append(name + ": independently recomputed image MSE differs")
        verified.append({"condition": name, "dice": dice, "max_float64_image_mse_difference": largest, "all_internal_residues_covered": sorted({z % 4 for z in target_indices}) == [1, 2, 3], "observed_preservation_verified": True})
    report = {"preflight_sha256": sha(path), "script_sha256": sha(Path(__file__)), "conditions_checked": verified, "errors": errors, "task_inference_repeated": False, "independent_confirmation": False}
    (OUT / "independent_saved_output_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
