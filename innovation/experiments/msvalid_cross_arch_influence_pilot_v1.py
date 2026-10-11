"""Exploratory CPU cross-architecture finite responses on MSValid."""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import nibabel as nib
import numpy as np
import torch
from skimage.transform import resize

from msvalid_mira_confirmation import MODELS, metrics, predict, sha256, write_csv


ROOT = Path(__file__).resolve().parents[2] / "innovation"
PLAN = ROOT / "MSVALID_INFLUENCE_FUTURE_PROTOCOL_2026-09-30.md"
QUALIFIED = ROOT / "literature/msvalid_geometry_qualification.json"
LEFT = (-3, -2, -1)
RIGHT = (1, 2, 3)
CONTEXTS = tuple((l, r) for l in LEFT for r in RIGHT)
SEEDS = (6101, 6102, 6103, 6104)


def condition(pool: dict[int, np.ndarray], context: tuple[int, int],
              field: np.ndarray | None = None, anchor: int | None = None,
              epsilon: float = 0.0) -> np.ndarray:
    left_id, right_id = context
    left, right = pool[left_id], pool[right_id]
    if anchor == left_id:
        left = np.clip(left + epsilon * field, 0, 1).astype(np.float32)
    if anchor == right_id:
        right = np.clip(right + epsilon * field, 0, 1).astype(np.float32)
    rel = -left_id / (right_id - left_id)
    coarse = ((1 - rel) * left + rel * right).astype(np.float32)
    return np.stack((left, right, coarse, np.full((256, 256), rel, np.float32)))


def predict_many(net: object, conditions: list[np.ndarray], shape: tuple[int, int],
                 lo: float, hi: float) -> list[np.ndarray]:
    answers = []
    for start in range(0, len(conditions), 4):
        batch = conditions[start:start + 4]
        tensor = torch.from_numpy(np.stack(batch)).float().to(net.device)
        with torch.inference_mode():
            residuals = net.model(tensor).float().clamp(-1, 1)[:, 0].cpu().numpy()
        for cond, residual in zip(batch, residuals):
            generated = np.clip(cond[2] + residual, 0, 1)
            answer = (resize(generated, shape, preserve_range=True, anti_aliasing=True)
                      * (hi - lo) + lo).astype(np.float32)
            answers.append(answer)
    return answers


def responses(net: object, pool: dict[int, np.ndarray], context: tuple[int, int],
              base: np.ndarray, mask: np.ndarray, fields: list[np.ndarray],
              epsilon: float, shape: tuple[int, int], lo: float, hi: float) -> np.ndarray:
    blocks = []
    for anchor in context:
        conds = [condition(pool, context, field, anchor, epsilon) for field in fields]
        perturbed = predict_many(net, conds, shape, lo, hi)
        blocks.append(np.stack([(prediction - base)[mask] for prediction in perturbed]))
    return np.stack(blocks).astype(np.float32)


def influence(ref: np.ndarray, candidate: np.ndarray, reference: tuple[int, int],
              context: tuple[int, int]) -> float:
    numerator = sum(float(np.sum(ref[i].astype(np.float64) *
                                 candidate[context.index(anchor)].astype(np.float64)))
                    for i, anchor in enumerate(reference) if anchor in context)
    denominator = np.sqrt(float(np.sum(ref.astype(np.float64) ** 2)) *
                          float(np.sum(candidate.astype(np.float64) ** 2)))
    return float(numerator / denominator) if denominator > 0 else float("nan")


def target_result(volume: np.ndarray, patient: dict, z: int,
                  hat: object, swinir: object, fields: list[np.ndarray],
                  epsilon: float) -> list[dict]:
    raw = {offset: volume[:, :, z + offset] for offset in (*LEFT, *RIGHT)}
    lo = min(float(image.min()) for image in raw.values())
    hi = max(float(image.max()) for image in raw.values())
    if not np.isfinite((lo, hi)).all() or hi <= lo:
        raise ValueError(f"{patient['patient']}/z{z}: invalid six-anchor range")
    pool = {offset: resize(((image - lo) / (hi - lo + 1e-8)).astype(np.float32),
                           (256, 256), preserve_range=True, anti_aliasing=True).astype(np.float32)
            for offset, image in raw.items()}
    reference = (-1, 3) if z % 4 == 1 else (-3, 1)
    near = [raw[offset] for offset in reference]
    mask = ((np.abs(near[0]) > .01 * max(float(np.max(np.abs(near[0]))), 1e-6)) |
            (np.abs(near[1]) > .01 * max(float(np.max(np.abs(near[1]))), 1e-6)))
    if not mask.any():
        raise ValueError(f"{patient['patient']}/z{z}: empty mask")
    h_cond = condition(pool, reference)
    h_base = predict_many(hat, [h_cond], volume.shape[:2], lo, hi)[0]
    wrapper_check = predict(hat, ([pool[reference[0]], pool[reference[1]]], lo, hi),
                            0, -reference[0] / (reference[1] - reference[0]),
                            volume.shape[:2])
    if float(np.max(np.abs(h_base - wrapper_check))) > 1e-4:
        raise AssertionError("Batched HAT prediction differs from the reference wrapper")
    h_response = responses(hat, pool, reference, h_base, mask, fields,
                           epsilon, volume.shape[:2], lo, hi)
    s_conditions = [condition(pool, context) for context in CONTEXTS]
    s_bases = predict_many(swinir, s_conditions, volume.shape[:2], lo, hi)
    s_responses = [responses(swinir, pool, context, base, mask, fields,
                             epsilon, volume.shape[:2], lo, hi)
                   for context, base in zip(CONTEXTS, s_bases)]

    # Bind predictions and responses before reading the retrospective target plane.
    y = volume[:, :, z]
    rows = []
    for context, base, s_response in zip(CONTEXTS, s_bases, s_responses):
        score = metrics(h_base, base, y, mask)
        overlap = len(set(reference) & set(context))
        row = {"patient": patient["patient"], "z": z, "residue": z % 4,
               "z_spacing_mm": patient["zooms_mm"][2],
               "reference_left": z + reference[0], "reference_right": z + reference[1],
               "companion_left": z + context[0], "companion_right": z + context[1],
               "context_left_offset": context[0], "context_right_offset": context[1],
               "span_mm": (context[1] - context[0]) * patient["zooms_mm"][2],
               "asymmetry_mm": abs(context[0] + context[1]) * patient["zooms_mm"][2],
               "shared_anchor_count": overlap, "support_pixels": int(mask.sum()),
               "epsilon": epsilon, "fields": len(fields),
               "influence": influence(h_response, s_response, reference, context),
               "observable": score["observable"],
               "error_cosine": float(np.sum(((h_base - y)[mask].astype(np.float64)) *
                                             ((base - y)[mask].astype(np.float64))) /
                                     np.sqrt(score["a_mse"] * score["b_mse"]) / mask.sum()),
               "a_mae": score["a_mae"], "b_mae": score["b_mae"],
               "disagreement_mae": score["disagreement_mae"]}
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patients", type=int, required=True)
    parser.add_argument("--epsilon", type=float, default=.01)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.patients <= 84 or args.output.exists():
        raise ValueError("Invalid patient count or output already exists")
    if args.output.resolve().parent != (ROOT / "experiments").resolve():
        raise ValueError("Output must be a new direct child of innovation/experiments")
    cohort = json.loads(QUALIFIED.read_text(encoding="utf-8"))["patients"]
    if len(cohort) != 84 or not all(p["geometry_eligible"] for p in cohort):
        raise RuntimeError("Qualified cohort changed")
    for name, (_, path, expected) in MODELS.items():
        if sha256(path) != expected:
            raise ValueError(f"{name}: checkpoint hash mismatch")
    fields = []
    for seed in SEEDS:
        field = np.random.default_rng(seed).choice([-1., 1.], size=(256, 256)).astype(np.float32)
        field -= field.mean()
        fields.append(field)
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    hat = MODELS["hat"][0](MODELS["hat"][1], device="cpu")
    swinir = MODELS["swinir"][0](MODELS["swinir"][1], device="cpu")
    args.output.mkdir(parents=True)
    start = time.perf_counter()
    rows = []
    for index, patient in enumerate(cohort[:args.patients], 1):
        path = ROOT / "data/msvalid_first_t2" / f"{patient['patient']}.nii.gz"
        volume = nib.load(str(path)).get_fdata(dtype=np.float32)
        if tuple(volume.shape) != tuple(patient["shape"]) or not np.isfinite(volume).all():
            raise ValueError(f"{patient['patient']}: changed volume")
        patient_rows = []
        for residue in (1, 3):
            for z in patient["eligible_targets"][f"residue_{residue}"]:
                patient_rows.extend(target_result(volume, patient, z, hat, swinir,
                                                  fields, args.epsilon))
                print(f"{index}/{args.patients} {patient['patient']} z={z} "
                      f"elapsed={time.perf_counter()-start:.1f}s", flush=True)
        rows.extend(patient_rows)
        write_csv(args.output / "per_context.csv", rows)
    summary = {"status": "post-result exploratory pilot; no independent confirmation",
               "plan_sha256": sha256(PLAN), "script_sha256": sha256(Path(__file__)),
               "qualification_sha256": sha256(QUALIFIED),
               "checkpoint_sha256": {name: spec[2] for name, spec in MODELS.items()},
               "patients": args.patients, "targets": len(rows) // 9,
               "contexts": len(rows), "fields": len(fields), "epsilon": args.epsilon,
               "elapsed_seconds": time.perf_counter() - start}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
