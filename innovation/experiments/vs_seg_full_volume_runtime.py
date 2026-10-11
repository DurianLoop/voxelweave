"""CPU reconstruction and inference, matching the fixed 001 technical contract."""
from __future__ import annotations
import hashlib
import importlib.util
import io
import json
import zipfile
from pathlib import Path

from vs_seg_task_cpu_support import ROOT
import numpy as np

CONDITIONS = ("native", "raw_linear", "raw_pchip", "pipeline_linear", "pipeline_pchip", "hat", "swinir")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1_048_576), b""):
            h.update(part)
    return h.hexdigest()


def array_sha(array):
    a = np.ascontiguousarray(array)
    h = hashlib.sha256(json.dumps({"shape": list(a.shape), "dtype": a.dtype.str}, sort_keys=True).encode())
    h.update(memoryview(a).cast("B"))
    return h.hexdigest()


def load_tuple_inferer():
    path = ROOT / "experiments/vs_seg_001_tuple_equivalence/monai_0_4_tuple_inferer.py"
    proof = json.loads((path.parent / "attempt_01.json").read_text())
    if not proof["complete"] or not proof["bitwise_logits_equal"] or sha(path) != proof["tuple_inferer_sha256"]:
        raise ValueError("Tuple inference equivalence proof differs")
    spec = importlib.util.spec_from_file_location("fixed_tuple_inferer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decode_source(case):
    import pydicom
    payload = json.loads((ROOT / case["input_file"]).read_text())
    item = payload["source_inputs"]["image_zip"]
    source = ROOT / item["path"]
    if sha(source) != item["sha256"]:
        raise ValueError("Native image source hash differs")
    with zipfile.ZipFile(source) as archive:
        ds = [pydicom.dcmread(io.BytesIO(archive.read(n))) for n in archive.namelist() if n.lower().endswith(".dcm")]
    direction = np.asarray(ds[0].ImageOrientationPatient, dtype=float)
    normal = np.cross(direction[:3], direction[3:])
    ds.sort(key=lambda h: float(np.asarray(h.ImagePositionPatient, dtype=float) @ normal))
    expected = case["sop_instance_uids_sorted"]
    if [str(x.SOPInstanceUID) for x in ds] != expected:
        raise ValueError("Native SOP identity/order differs")
    if any(str(x.PatientID) != case["patient"] or str(x.SeriesInstanceUID) != payload["series_instance_uid"]
           or str(x.PhotometricInterpretation) != "MONOCHROME2" for x in ds):
        raise ValueError("Decoded patient/series/photometric identity differs")
    volume = np.stack([x.pixel_array.astype(np.float32) * float(x.get("RescaleSlope", 1))
                       + float(x.get("RescaleIntercept", 0)) for x in ds], axis=-1)
    expected_shape = tuple(payload["dimensions_ijk"][i] for i in (1, 0, 2))
    if volume.shape != expected_shape or not np.isfinite(volume).all():
        raise ValueError("Decoded shape or finite-pixel gate failed")
    labels = np.load(ROOT / case["masks_file"])
    affine = labels["affine_ijk_ras"][:, [1, 0, 2, 3]]
    if not np.allclose(labels["affine_ijk_ras"], payload["affine_ijk_ras"], atol=1e-6, rtol=0):
        raise ValueError("Native image/label grid differs")
    refs = {"original_json": labels["original_mask_rcz"].astype(bool), "rtstruct": labels["rtstruct_mask_rcz"].astype(bool)}
    if any(x.shape != volume.shape or not x.any() for x in refs.values()):
        raise ValueError("Reference label shape/nonempty gate failed")
    return volume, affine, refs


def reconstruct(name, volume, prep, models):
    from scipy.interpolate import PchipInterpolator
    from skimage.transform import resize
    from remind_native_t2_ixi_pair import predict
    if name not in CONDITIONS:
        raise ValueError("Unknown fixed condition")
    anchors = volume[:, :, ::4]
    planes, lo, hi = prep
    span = float(hi - lo)
    if not np.isfinite(span) or span <= 0:
        raise ValueError("Invalid observed-only normalization span")
    observed = np.arange(0, volume.shape[2], 4)
    last = int(observed[-1])
    generated = volume.copy() if name == "native" else np.zeros_like(volume)
    generated[:, :, observed] = volume[:, :, observed]
    if name != "native":
        generated[:, :, last + 1:] = volume[:, :, last, None]
        for z in range(1, last):
            if z % 4 == 0:
                continue
            i, t = z // 4, z % 4 / 4
            left, right = anchors[:, :, i], anchors[:, :, i + 1]
            enough = i >= 1 and i + 2 < anchors.shape[2]
            if name == "raw_linear" or (name == "raw_pchip" and not enough):
                plane = (1 - t) * left + t * right
            elif name == "raw_pchip":
                indices = np.arange(i - 1, i + 3)
                plane = PchipInterpolator(4 * indices, anchors[:, :, indices], axis=-1)(z)
            elif name.startswith("pipeline_"):
                if name == "pipeline_pchip" and enough:
                    indices = np.arange(i - 1, i + 3)
                    coarse = PchipInterpolator(4 * indices, np.stack([planes[j] for j in indices]), axis=0)(z)
                else:
                    coarse = (1 - t) * planes[i] + t * planes[i + 1]
                plane = resize(np.clip(coarse, 0, 1), volume.shape[:2], preserve_range=True, anti_aliasing=True) * span + lo
            else:
                plane = predict(models[name], prep, i, t, volume.shape[:2])
            generated[:, :, z] = np.asarray(plane, dtype=np.float32)
    if not np.isfinite(generated).all() or not np.array_equal(generated[:, :, observed], volume[:, :, observed]):
        raise ValueError("Nonfinite reconstruction or modified observed planes")
    if name != "native" and not np.array_equal(generated[:, :, last + 1:], np.repeat(volume[:, :, last, None], volume.shape[2] - last - 1, axis=2)):
        raise ValueError("Unsupported tail convention differs")
    return generated


def image_metrics(generated, volume, refs, span):
    rows = []
    for z in range(1, (volume.shape[2] - 1) // 4 * 4):
        if not z % 4:
            continue
        left, right = volume[:, :, z - z % 4], volume[:, :, z - z % 4 + 4]
        support = (abs(left) > .01 * max(float(abs(left).max()), 1e-6)) | (abs(right) > .01 * max(float(abs(right).max()), 1e-6))
        if not support.any():
            raise ValueError("Empty fixed observed-only support")
        square = ((generated[:, :, z] - volume[:, :, z]).astype(np.float64) / span) ** 2
        row = {"z": z, "residue": z % 4, "full_image_nmse": float(square.mean())}
        regions = {"support": support, **{k + "_lesion": support & v[:, :, z] for k, v in refs.items()}}
        for key, region in regions.items():
            n = int(region.sum())
            row[key] = {"pixels": n, "sse": float(square[region].sum()), "nmse": float(square[region].mean()) if n else None}
        rows.append(row)
    summaries = {}
    for key in ("support", "original_json_lesion", "rtstruct_lesion"):
        n = sum(x[key]["pixels"] for x in rows)
        means = [x[key]["nmse"] for x in rows if x[key]["nmse"] is not None]
        summaries[key] = {"pixels": n, "target_equal_nmse": float(np.mean(means)) if means else None,
                          "pixel_weighted_nmse": sum(x[key]["sse"] for x in rows) / n if n else None,
                          "nonempty_targets": len(means)}
    return summaries, rows


def inference(segmenter, infer, generated, orientation):
    import nibabel as nib
    import torch
    from monai.transforms import NormalizeIntensity
    ras = np.ascontiguousarray(nib.orientations.apply_orientation(generated, orientation))
    normalized = NormalizeIntensity()(ras[None].copy())
    inputs = torch.from_numpy(np.ascontiguousarray(normalized)).unsqueeze(0)
    with torch.inference_mode():
        logits = infer.sliding_window_inference(inputs, roi_size=(384, 384, 64), sw_batch_size=1,
                                                predictor=lambda x: segmenter(x)[0], mode="gaussian")
    if not bool(torch.isfinite(logits).all()) or torch.cuda.is_initialized():
        raise ValueError("Invalid CPU-only task inference")
    prediction = logits.argmax(dim=1)[0].numpy().astype(bool)
    return prediction
