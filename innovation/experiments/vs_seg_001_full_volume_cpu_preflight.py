"""Full-volume x4 technical preflight on a fixed, previously seen training case."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import time
import traceback
from pathlib import Path

from vs_seg_task_cpu_support import ROOT, load_model, resource_gate

OUT = ROOT / "experiments/vs_seg_001_full_volume_cpu_preflight"
PLAN = ROOT / "VS_SEG_001_FULL_VOLUME_CPU_PREFLIGHT_PROTOCOL_2026-10-02.md"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    report = {"attempt": attempt, "complete": False, "patient": "VS-SEG-001", "author_split": "training", "independent_confirmation": False, "protocol_sha256": sha(PLAN), "script_sha256": sha(Path(__file__)), "conditions": []}
    start = time.perf_counter()
    try:
        report["resource_gate"] = resource_gate()
        segmenter, runtime = load_model()
        import nibabel as nib
        import numpy as np
        import torch
        from scipy.interpolate import PchipInterpolator
        from skimage.transform import resize
        from monai.transforms import NormalizeIntensity
        from remind_native_t2_ixi_pair import MODELS, predict, prepared
        from vs_seg_001_label_pixel_feasibility import load_pair
        tuple_dir = ROOT / "experiments/vs_seg_001_tuple_equivalence"
        tuple_proof = json.loads((tuple_dir / "attempt_01.json").read_text())
        if not tuple_proof["complete"] or not tuple_proof["bitwise_logits_equal"]:
            raise ValueError("Tuple-equivalent inferer not established")
        tuple_path = tuple_dir / "monai_0_4_tuple_inferer.py"
        if sha(tuple_path) != tuple_proof["tuple_inferer_sha256"]:
            raise ValueError("Tuple inferer changed")
        spec = importlib.util.spec_from_file_location("vs_seg_validated_tuple_inferer", tuple_path)
        infer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(infer)
        volume, _, _ = load_pair()
        conversion_path = ROOT / "experiments/vs_seg_original_mask_cpu_development/attempt_03.json"
        conversion = json.loads(conversion_path.read_text())
        native_mask = next(r for r in conversion["patients"] if r["patient"] == "VS-SEG-001")
        mask_path = ROOT / native_mask["masks_file"]
        if sha(mask_path) != native_mask["masks_sha256"]:
            raise ValueError("Original native label changed")
        labels = np.load(mask_path)
        label = labels["original_mask_rcz"]
        affine = labels["affine_ijk_ras"][:, [1, 0, 2, 3]]
        orientation = nib.orientations.ornt_transform(nib.orientations.io_orientation(affine), nib.orientations.axcodes2ornt("RAS"))
        canonical_affine = affine @ nib.orientations.inv_ornt_aff(orientation, volume.shape)
        label_ras = np.ascontiguousarray(nib.orientations.apply_orientation(label, orientation))
        anchors = volume[:, :, ::4]
        prep = prepared(anchors)
        planes, lo, hi = prep
        span = float(hi - lo)
        if span <= 0 or not np.isfinite(span):
            raise ValueError("Invalid observed-only span")
        observed = list(range(0, volume.shape[2], 4))
        last = observed[-1]
        targets = [z for z in range(1, last) if z % 4]
        if len(targets) != 57:
            raise ValueError("Fixed native target count changed")
        report.update({"runtime": runtime, "tuple_equivalence_sha256": sha(tuple_dir / "attempt_01.json"), "conversion_sha256": sha(conversion_path), "original_label_sha256": sha(mask_path), "observation_indices": observed, "internal_targets": targets, "unsupported_terminal_planes": list(range(last + 1, volume.shape[2])), "observed_min": float(lo), "observed_max": float(hi), "array_shape_rcz": list(volume.shape), "canonical_affine": canonical_affine.tolist()})
        support_by_z = {}
        for z in targets:
            i = z // 4
            left, right = anchors[:, :, i], anchors[:, :, i + 1]
            support_by_z[z] = (abs(left) > .01 * max(float(abs(left).max()), 1e-6)) | (abs(right) > .01 * max(float(abs(right).max()), 1e-6))
        models = {}
        for name in ("hat", "swinir"):
            if sha(MODELS[name][1]) != MODELS[name][2]:
                raise ValueError("Frozen reconstruction checkpoint changed")
            models[name] = MODELS[name][0](MODELS[name][1], device="cpu")
        report["reconstruction_checkpoint_sha256"] = {name: MODELS[name][2] for name in models}
        conditions = ("native", "raw_linear", "raw_pchip", "pipeline_linear", "pipeline_pchip", "hat", "swinir")
        for name in conditions:
            resource_gate()
            condition_start = time.perf_counter()
            generated = volume.copy() if name == "native" else np.zeros_like(volume)
            generated[:, :, observed] = volume[:, :, observed]
            if name != "native":
                generated[:, :, last + 1:] = volume[:, :, last, None]
                for z in targets:
                    i, fraction = z // 4, (z % 4) / 4
                    left, right = anchors[:, :, i], anchors[:, :, i + 1]
                    enough = i >= 1 and i + 2 < anchors.shape[2]
                    if name == "raw_linear" or (name == "raw_pchip" and not enough):
                        plane = (1 - fraction) * left + fraction * right
                    elif name == "raw_pchip":
                        indices = np.arange(i - 1, i + 3)
                        plane = PchipInterpolator(4 * indices, anchors[:, :, indices], axis=-1)(z)
                    elif name.startswith("pipeline_"):
                        if name == "pipeline_pchip" and enough:
                            indices = np.arange(i - 1, i + 3)
                            coarse = PchipInterpolator(4 * indices, np.stack([planes[j] for j in indices]), axis=0)(z)
                        else:
                            coarse = (1 - fraction) * planes[i] + fraction * planes[i + 1]
                        plane = resize(np.clip(coarse, 0, 1), volume.shape[:2], preserve_range=True, anti_aliasing=True) * span + lo
                    else:
                        plane = predict(models[name], prep, i, fraction, volume.shape[:2])
                    generated[:, :, z] = np.asarray(plane, dtype=np.float32)
                if not np.array_equal(generated[:, :, observed], volume[:, :, observed]):
                    raise ValueError("Observed native planes were modified")
            if not np.isfinite(generated).all():
                raise ValueError("Nonfinite reconstruction")
            reconstruction_seconds = time.perf_counter() - condition_start
            errors = []
            for z in targets:
                square = ((generated[:, :, z] - volume[:, :, z]).astype(np.float64) / span) ** 2
                support = support_by_z[z]
                lesion = label[:, :, z] & support
                errors.append({"z": z, "support_pixels": int(support.sum()), "support_sse": float(square[support].sum()), "support_nmse": float(square[support].mean()), "lesion_pixels": int(lesion.sum()), "lesion_sse": float(square[lesion].sum()), "lesion_nmse": float(square[lesion].mean()) if lesion.any() else None, "full_image_nmse": float(square.mean())})
            summaries = {}
            for region in ("support", "lesion"):
                count = sum(x[region + "_pixels"] for x in errors)
                means = [x[region + "_nmse"] for x in errors if x[region + "_nmse"] is not None]
                summaries[region] = {"pixels": count, "target_equal_nmse": float(np.mean(means)) if means else None, "pixel_weighted_nmse": sum(x[region + "_sse"] for x in errors) / count if count else None}
            reconstruction_file = OUT / f"{name}_volume_attempt_{attempt:02d}.npz"
            np.savez_compressed(reconstruction_file, image_rcz=generated, affine_rcz_ras=affine)
            task_start = time.perf_counter()
            ras = np.ascontiguousarray(nib.orientations.apply_orientation(generated, orientation))
            normalized = NormalizeIntensity()(ras[None].copy())
            inputs = torch.from_numpy(np.ascontiguousarray(normalized)).unsqueeze(0)
            with torch.inference_mode():
                logits = infer.sliding_window_inference(inputs, roi_size=(384, 384, 64), sw_batch_size=1, predictor=lambda x: segmenter(x)[0], mode="gaussian")
            if not bool(torch.isfinite(logits).all()) or torch.cuda.is_initialized():
                raise ValueError("Invalid CPU task inference")
            prediction = logits.argmax(dim=1)[0].numpy().astype(bool)
            tp, fp, fn = int((prediction & label_ras).sum()), int((prediction & ~label_ras).sum()), int((~prediction & label_ras).sum())
            pred_file = OUT / f"{name}_prediction_attempt_{attempt:02d}.npz"
            np.savez_compressed(pred_file, prediction_ras=prediction, affine=canonical_affine)
            voxel_mm3 = float(abs(np.linalg.det(affine[:3, :3])))
            record = {"condition": name, "observed_planes_bitwise_preserved": True, "original_label_voxels": int(label_ras.sum()), "prediction_voxels": int(prediction.sum()), "dice": float(2 * tp / (2 * tp + fp + fn)), "tp": tp, "fp": fp, "fn": fn, "signed_volume_difference_mm3": float((prediction.sum() - label_ras.sum()) * voxel_mm3), "absolute_relative_volume_error": float(abs(int(prediction.sum()) - int(label_ras.sum())) / label_ras.sum()), "image_metrics": summaries, "per_plane_image_errors": errors, "reconstruction_file": reconstruction_file.relative_to(ROOT).as_posix(), "reconstruction_sha256": sha(reconstruction_file), "prediction_file": pred_file.relative_to(ROOT).as_posix(), "prediction_sha256": sha(pred_file), "reconstruction_seconds": reconstruction_seconds, "task_seconds": time.perf_counter() - task_start}
            report["conditions"].append(record)
            (OUT / f"progress_attempt_{attempt:02d}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({k: record[k] for k in ("condition", "dice", "image_metrics", "reconstruction_seconds", "task_seconds")}), flush=True)
            del logits, inputs, normalized, ras, generated
        report["cuda_initialized"] = torch.cuda.is_initialized()
        report["complete"] = len(report["conditions"]) == len(conditions)
    except Exception as exc:
        report.update({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
    report["elapsed_seconds"] = time.perf_counter() - start
    (OUT / f"attempt_{attempt:02d}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"attempt": attempt, "complete": report["complete"], "conditions": len(report["conditions"]), "error": report.get("error"), "elapsed_seconds": report["elapsed_seconds"]}), flush=True)
    if not report["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
