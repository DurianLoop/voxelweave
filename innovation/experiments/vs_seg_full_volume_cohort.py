"""Frozen, resumable one-worker CPU queue. Run --freeze before patient inference."""
from __future__ import annotations
import argparse
import json
import importlib.metadata
import os
import sys
import time
import traceback
from pathlib import Path

from vs_seg_task_cpu_support import ROOT, load_model, resource_gate
from vs_seg_full_volume_runtime import CONDITIONS, array_sha, decode_source, image_metrics, inference, load_tuple_inferer, reconstruct, sha
from vs_seg_full_volume_metrics import outside_reference_band, paired_bootstrap, task_metrics

OUT = ROOT / "experiments/vs_seg_full_volume_cohort"
PLAN = ROOT / "VS_SEG_FULL_VOLUME_COHORT_PROTOCOL_2026-10-02.md"
CONTRACT = OUT / "run_contract.json"
SOURCE = ROOT / "literature/source_cache/vs_seg_full_volume_source_gate_2026-10-02/attempt_01.json"
CONVERSION = ROOT / "experiments/vs_seg_full_volume_source_masks/attempt_02.json"


def package_versions():
    return {name: importlib.metadata.version(name) for name in ("numpy", "scipy", "torch", "scikit-image", "nibabel", "pydicom")}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def cases_from_sources():
    source, conversion = json.loads(SOURCE.read_text()), json.loads(CONVERSION.read_text())
    if not source["complete"] or not conversion["complete"] or len(source["fixed_roster"]) != 46:
        raise ValueError("Fixed 46-patient source or conversion incomplete")
    masks = {r["patient"]: r for r in conversion["patients"]}
    cases = [{**r, **{k: masks[r["patient"]][k] for k in ("input_file", "input_sha256", "masks_file", "masks_sha256")}}
             for r in source["patients"]]
    if [r["patient"] for r in cases] != source["fixed_roster"] or sum(r["main_ciss_source_qualified"] for r in cases) != 45:
        raise ValueError("Fixed roster/main CISS denominator differs")
    return cases


def freeze():
    if CONTRACT.exists():
        raise FileExistsError("Existing frozen contract must not be overwritten")
    proof = sorted((ROOT / "experiments/vs_seg_full_volume_development_checks").glob("attempt_*.json"))[-1]
    check = json.loads(proof.read_text())
    if not check["complete"] or check["errors"]:
        raise ValueError("Development metric/reconstruction checks did not pass")
    cases = cases_from_sources()
    project = ROOT.parent
    paths = {PLAN, Path(__file__).resolve(), SOURCE, CONVERSION, proof,
             ROOT / "experiments/vs_seg_full_volume_runtime.py", ROOT / "experiments/vs_seg_full_volume_metrics.py",
             ROOT / "experiments/vs_seg_full_volume_development_checks.py", ROOT / "experiments/vs_seg_task_cpu_support.py",
             ROOT / "experiments/verify_vs_seg_full_volume_cohort.py",
             ROOT / "experiments/remind_native_t2_ixi_pair.py", ROOT / "experiments/vs_seg_001_tuple_equivalence/attempt_01.json",
             ROOT / "experiments/vs_seg_001_tuple_equivalence/monai_0_4_tuple_inferer.py",
             ROOT / "experiments/vs_seg_full_volume_source_masks/independent_source_geometry_verification.json"}
    for relative in ("baseline/ixi_hat_2p5d", "baseline/ixi_swinir_2p5d", "pre/ixi_diffusion", "pre/topcow_diffusion"):
        paths.update((project / relative).glob("*.py"))
    compat = ROOT / "tools/vs_seg_cpu_compat"
    paths.update(p for p in compat.rglob("*.py") if "__pycache__" not in p.parts)
    for case in cases:
        paths.add(ROOT / case["input_file"])
        paths.add(ROOT / case["masks_file"])
        payload = json.loads((ROOT / case["input_file"]).read_text())
        paths.add(ROOT / payload["source_inputs"]["image_zip"]["path"])
    from remind_native_t2_ixi_pair import MODELS
    for name, (_, path, digest) in MODELS.items():
        if sha(path) != digest:
            raise ValueError(name + " reconstruction checkpoint differs")
        paths.add(path)
    paths.add(ROOT / "data/vs_seg_task_model_release/UNet2d5_Att_Hard_T2_final.zip")
    for field in ("script_sha256", "runtime_script_sha256", "metrics_script_sha256"):
        expected_path = {"script_sha256": proof.parent.parent / "vs_seg_full_volume_development_checks.py",
                         "runtime_script_sha256": ROOT / "experiments/vs_seg_full_volume_runtime.py",
                         "metrics_script_sha256": ROOT / "experiments/vs_seg_full_volume_metrics.py"}[field]
        if sha(expected_path) != check[field]:
            raise ValueError("Checked implementation changed before freeze: " + field)
    contract = {"version": 1, "frozen_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
                "main_roster": [r["patient"] for r in cases if r["main_ciss_source_qualified"]],
                "secondary_roster": [r["patient"] for r in cases if not r["main_ciss_source_qualified"]],
                "conditions": list(CONDITIONS), "primary_comparison": ["hat", "pipeline_pchip"],
                "bootstrap_seed": 20261012, "bootstrap_draws": 5000,
                "installed_package_versions": package_versions(), "python_version": sys.version,
                "development_patient_seen": "VS-SEG-001", "heldout_task_inference_before_freeze": False,
                "files": [{"path": p.relative_to(project).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(paths)]}
    write_json(CONTRACT, contract)
    print(json.dumps({"frozen": True, "contract_sha256": sha(CONTRACT), "files": len(contract["files"]), "main": 45, "secondary": 1}), flush=True)


def verify_contract():
    contract = json.loads(CONTRACT.read_text())
    if contract["installed_package_versions"] != package_versions() or contract["python_version"] != sys.version:
        raise ValueError("Frozen Python/package versions changed")
    for item in contract["files"]:
        path = ROOT.parent / item["path"]
        if path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
            raise ValueError("Frozen input/code changed: " + item["path"])
    if contract["conditions"] != list(CONDITIONS) or len(contract["main_roster"]) != 45:
        raise ValueError("Contract mathematical conditions/denominator differ")
    return contract


def successful_conditions(patient, contract_sha):
    records = {}
    for path in sorted((OUT / "patients" / patient).glob("*_attempt_*.json")):
        r = json.loads(path.read_text())
        if r.get("complete") and r.get("contract_sha256") == contract_sha:
            p = ROOT / r["prediction_file"]
            if not p.exists() or sha(p) != r["prediction_sha256"]:
                raise ValueError("Completed prediction missing/changed: " + str(path))
            if r["condition"] in records:
                raise ValueError("Duplicate completed condition; needs audit")
            records[r["condition"]] = r
    return records


def status(contract):
    contract_sha = sha(CONTRACT)
    by_patient = {p: successful_conditions(p, contract_sha) for p in contract["main_roster"] + contract["secondary_roster"]}
    complete_main = [p for p in contract["main_roster"] if len(by_patient[p]) == len(CONDITIONS)]
    result = {"contract_sha256": contract_sha, "complete_main_patients": len(complete_main), "fixed_main_denominator": 45,
              "completed_conditions": sum(len(x) for x in by_patient.values()), "all_conditions_planned": 46 * len(CONDITIONS),
              "main_complete": len(complete_main) == 45, "secondary_complete": all(len(by_patient[p]) == len(CONDITIONS) for p in contract["secondary_roster"]),
              "publication_claim_confirmed": False, "patients": [{"patient": p, "conditions": list(by_patient[p]), "complete": len(by_patient[p]) == len(CONDITIONS)} for p in by_patient]}
    # No inferential estimates from a changing subset of the fixed primary roster.
    if result["main_complete"]:
        summary = {}
        n = contract["main_roster"]
        summary["primary_image_difference"] = paired_bootstrap([by_patient[p]["hat"]["image_metrics"]["support"]["target_equal_nmse"] - by_patient[p]["pipeline_pchip"]["image_metrics"]["support"]["target_equal_nmse"] for p in n])
        summary["primary_task_difference"] = paired_bootstrap([by_patient[p]["hat"]["task_metrics"]["original_json"]["full"]["dice"] - by_patient[p]["pipeline_pchip"]["task_metrics"]["original_json"]["full"]["dice"] for p in n])
        result["fixed_primary_joint_direction_supported"] = all(v["ci95_percentile"][1] < 0 for v in summary.values())
        summary["descriptive_secondary_pairs"] = []
        for model in ("hat", "swinir"):
            for baseline in ("raw_linear", "raw_pchip", "pipeline_linear", "pipeline_pchip"):
                entry = {"model": model, "baseline": baseline, "formal_significance_claim": False, "task_sensitivity": {}}
                entry["support_nmse"] = paired_bootstrap([by_patient[p][model]["image_metrics"]["support"]["target_equal_nmse"] - by_patient[p][baseline]["image_metrics"]["support"]["target_equal_nmse"] for p in n])
                for ref in ("original_json", "rtstruct"):
                    for domain in ("full", "observed_anchor_slab", "exclude_reference_boundary_1mm"):
                        finite = [p for p in n if by_patient[p][model]["task_metrics"][ref][domain]["dice"] is not None and by_patient[p][baseline]["task_metrics"][ref][domain]["dice"] is not None]
                        values = [by_patient[p][model]["task_metrics"][ref][domain]["dice"] - by_patient[p][baseline]["task_metrics"][ref][domain]["dice"] for p in finite]
                        entry["task_sensitivity"][ref + "/" + domain] = {"included_patients": finite, "undefined_count": len(n) - len(finite), "estimate": paired_bootstrap(values) if values else None}
                summary["descriptive_secondary_pairs"].append(entry)
        summary["secondary_intervals_are_descriptive_without_familywise_claim"] = True
        result["analysis"] = summary
    write_json(OUT / "status.json", result)
    print(json.dumps({k: result[k] for k in ("complete_main_patients", "fixed_main_denominator", "completed_conditions", "main_complete", "secondary_complete")}), flush=True)
    return result


def run(max_patients):
    contract = verify_contract()
    contract_sha = sha(CONTRACT)
    cases = cases_from_sources()
    resource_gate()
    segmenter, runtime = load_model()
    import nibabel as nib
    import numpy as np
    import torch
    from remind_native_t2_ixi_pair import MODELS, prepared
    infer = load_tuple_inferer()
    models = {}
    started_patients = 0
    for case in cases:
        done = successful_conditions(case["patient"], contract_sha)
        if len(done) == len(CONDITIONS):
            continue
        if max_patients is not None and started_patients >= max_patients:
            break
        started_patients += 1
        try:
            resource_gate()
            volume, affine, refs = decode_source(case)
        except Exception as exc:
            directory = OUT / "patients" / case["patient"]
            attempt = len(list(directory.glob("input_attempt_*.json"))) + 1
            write_json(directory / f"input_attempt_{attempt:02d}.json", {"patient": case["patient"], "stage": "source_decode",
                       "contract_sha256": contract_sha, "complete": False, "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
            status(contract)
            raise
        orientation = nib.orientations.ornt_transform(nib.orientations.io_orientation(affine), nib.orientations.axcodes2ornt("RAS"))
        canonical_affine = affine @ nib.orientations.inv_ornt_aff(orientation, volume.shape)
        spacing = np.sqrt(np.sum(canonical_affine[:3, :3] ** 2, axis=0))
        if not np.allclose(canonical_affine[:3, :3].T @ canonical_affine[:3, :3], np.diag(spacing ** 2), atol=1e-5, rtol=0):
            raise ValueError("Boundary metric requires orthogonal physical grid")
        refs_ras = {k: np.ascontiguousarray(nib.orientations.apply_orientation(v, orientation)) for k, v in refs.items()}
        last = (volume.shape[2] - 1) // 4 * 4
        slab = np.zeros(volume.shape, dtype=bool)
        slab[:, :, :last + 1] = True
        slab_ras = np.ascontiguousarray(nib.orientations.apply_orientation(slab, orientation))
        band_keep = {k: outside_reference_band(v, spacing) for k, v in refs_ras.items()}
        prep = prepared(volume[:, :, ::4])
        patient_dir = OUT / "patients" / case["patient"]
        patient_dir.mkdir(parents=True, exist_ok=True)
        for name in CONDITIONS:
            if name in done:
                continue
            attempt = len(list(patient_dir.glob(name + "_attempt_*.json"))) + 1
            record = {"patient": case["patient"], "condition": name, "attempt": attempt, "complete": False,
                      "contract_sha256": contract_sha, "sequence": case["sequence"], "main_ciss": case["main_ciss_source_qualified"], "runtime": runtime,
                      "native_shape_rcz": list(volume.shape), "native_array_sha256": array_sha(volume), "source_input_sha256": case["input_sha256"],
                      "reference_masks_sha256": case["masks_sha256"], "array_hash_format": "sorted JSON shape/dtype followed by C-order bytes",
                      "canonical_affine": canonical_affine.tolist(), "spacing_ras_mm": spacing.tolist(),
                      "observed_indices": list(range(0, volume.shape[2], 4)), "unsupported_terminal_indices": list(range(last + 1, volume.shape[2]))}
            start = time.perf_counter()
            try:
                record["resource_gate"] = resource_gate()
                if name in MODELS and name not in models:
                    models[name] = MODELS[name][0](MODELS[name][1], device="cpu")
                generated = reconstruct(name, volume, prep, models)
                record["reconstruction_seconds"] = time.perf_counter() - start
                record["reconstructed_array_sha256"] = array_sha(generated)
                record["observed_planes_bitwise_preserved"] = True
                record["tail_copy_verified"] = name != "native"
                record["image_metrics"], record["per_plane_image_errors"] = image_metrics(generated, volume, refs, float(prep[2] - prep[1]))
                task_start = time.perf_counter()
                prediction = inference(segmenter, infer, generated, orientation)
                record["task_seconds"] = time.perf_counter() - task_start
                record["task_metrics"] = {k: task_metrics(prediction, ref, spacing, slab_ras, band_keep[k]) for k, ref in refs_ras.items()}
                path = patient_dir / f"{name}_prediction_attempt_{attempt:02d}.npz"
                with path.with_suffix(".npz.tmp").open("wb") as stream:
                    np.savez_compressed(stream, prediction_ras=prediction, affine=canonical_affine)
                os.replace(path.with_suffix(".npz.tmp"), path)
                record.update({"prediction_file": path.relative_to(ROOT).as_posix(), "prediction_sha256": sha(path),
                               "prediction_array_sha256": array_sha(prediction), "cuda_initialized": torch.cuda.is_initialized(), "complete": True})
                del generated, prediction
            except Exception as exc:
                record.update({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
            record["elapsed_seconds"] = time.perf_counter() - start
            write_json(patient_dir / f"{name}_attempt_{attempt:02d}.json", record)
            print(json.dumps({"patient": case["patient"], "condition": name, "complete": record["complete"], "seconds": record["elapsed_seconds"], "error": record.get("error")}), flush=True)
            if not record["complete"]:
                status(contract)
                raise SystemExit(1)
        status(contract)
        del volume, refs, refs_ras, slab, slab_ras, band_keep
    if torch.cuda.is_initialized():
        raise ValueError("CUDA was initialized")
    status(contract)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--max-patients", type=int)
    args = parser.parse_args()
    if args.freeze:
        freeze()
    elif args.verify_only:
        contract = verify_contract()
        print(json.dumps({"contract_verified": True, "files": len(contract["files"])}))
    elif args.status:
        status(verify_contract())
    else:
        if args.max_patients is not None and args.max_patients < 1:
            parser.error("--max-patients must be positive")
        run_attempt = len(list(OUT.glob("run_attempt_*.json"))) + 1
        started = time.perf_counter()
        session = {"attempt": run_attempt, "command_arguments": sys.argv[1:], "queue_returned_cleanly": False}
        try:
            run(args.max_patients)
            session["queue_returned_cleanly"] = True
        except BaseException as exc:
            session.update({"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
            raise
        finally:
            session["elapsed_seconds"] = time.perf_counter() - started
            write_json(OUT / f"run_attempt_{run_attempt:02d}.json", session)


if __name__ == "__main__":
    main()
