"""One-case CPU model preflight under the frozen VS-SEG protocol."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
import torch
from scipy.interpolate import PchipInterpolator
from skimage.transform import resize

from remind_native_t2_ixi_pair import MODELS, predict, prepared
from vs_seg_001_label_pixel_feasibility import load_pair, metrics


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "VS_SEG_THIN3D_MODEL_CONFIRMATION_PROTOCOL_2026-10-01.md"
PILOT = ROOT / "experiments/vs_seg_001_label_pixel_feasibility/result.json"
OUT = ROOT / "experiments/vs_seg_001_model_preflight.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    frozen = json.loads(PILOT.read_text(encoding="utf-8"))
    if not frozen["complete"] or frozen["patient"] != "VS-SEG-001":
        raise ValueError("Analytic-only source pilot changed")
    for name in ("hat", "swinir"):
        if sha256(MODELS[name][1]) != MODELS[name][2]:
            raise ValueError(f"Frozen {name} checkpoint changed")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    volume, mask, _ = load_pair()
    anchors = volume[:, :, ::4]
    prep = prepared(anchors)
    planes, lo, hi = prep
    span = float(hi - lo)
    if abs(span - frozen["observed_span"]) > 1e-4:
        raise ValueError("Observed span changed")
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    rows = []
    for residue in (1, 3):
        for z in frozen["targets"][str(residue)]:
            i = z // 4
            rel = (z - 4 * i) / 4
            left, right = anchors[:, :, i], anchors[:, :, i + 1]
            support = ((np.abs(left) > .01 * max(float(np.max(np.abs(left))), 1e-6)) |
                       (np.abs(right) > .01 * max(float(np.max(np.abs(right))), 1e-6)))
            lesion = mask[:, :, z] & support
            if int(lesion.sum()) != next(x for x in frozen["rows"] if x["z"] == z)["tumor"]["linear"]["pixels"]:
                raise ValueError("Frozen tumor ROI changed")
            coarse = ((1 - rel) * planes[i] + rel * planes[i + 1]).astype(np.float32)
            pipeline_linear = (resize(np.clip(coarse, 0, 1), volume.shape[:2],
                                      preserve_range=True, anti_aliasing=True) * span + lo).astype(np.float32)
            indices = np.arange(i - 1, i + 3)
            coarse_pchip = PchipInterpolator(4 * indices, np.stack([planes[j] for j in indices]), axis=0)(z)
            pipeline_pchip = (resize(np.clip(coarse_pchip, 0, 1), volume.shape[:2],
                                     preserve_range=True, anti_aliasing=True) * span + lo).astype(np.float32)
            outputs = {"hat": predict(hat, prep, i, rel, volume.shape[:2]),
                       "swinir": predict(swinir, prep, i, rel, volume.shape[:2]),
                       "pipeline_linear": pipeline_linear, "pipeline_pchip": pipeline_pchip}
            row = {"z": z, "residue": residue}
            for roi_name, roi in (("tumor", lesion), ("support", support)):
                row[roi_name] = {name: metrics(output, volume[:, :, z], roi, span)
                                 for name, output in outputs.items()}
            rows.append(row)
    result = {"patient": "VS-SEG-001", "complete": len(rows) == 4,
              "protocol_sha256": sha256(PROTOCOL), "analytic_pilot_sha256": sha256(PILOT),
              "checkpoint_sha256": {name: MODELS[name][2] for name in ("hat", "swinir")},
              "gpu_used": False, "rows": rows}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"complete": result["complete"], "rows": len(rows),
                      "means": {roi: {method: float(np.mean([row[roi][method]["normalized_mse"] for row in rows]))
                                      for method in ("hat", "swinir", "pipeline_linear", "pipeline_pchip")}
                                for roi in ("tumor", "support")}}, indent=2))


if __name__ == "__main__":
    main()
