"""Execute the predeclared two developers with corrected first-batch geometry."""
from __future__ import annotations

import copy
import csv
import json
import os
import sys
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import numpy as np
import pydicom
import torch
import mc_rc_three_development_action_oracle as helper
from vs_seg_task_cpu_support import ROOT, resource_gate
from vs_seg_full_volume_runtime import reconstruct, sha
from remind_native_t2_ixi_pair import MODELS, prepared

OUT = ROOT / "experiments/mc_rc_001_002_raw_action_oracle"
PLAN = ROOT / "MC_RC_001_002_RAW_ACTION_EXECUTION_PLAN_2026-10-02.md"
PREPARATION = ROOT / "experiments/mc_rc_three_development_action_oracle/next_development_followup_preparation.json"
HEADERS = ROOT / "literature/source_cache/mc_rc_three_patient_headers_2026-10-02"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")


def freeze():
    prep = read(PREPARATION)
    first_gate = ROOT / "experiments/mc_rc_native_t2_label_gate"
    inputs = [("source_header_sha256", HEADERS / "attempt_01.json"), ("source_refined_sha256", first_gate / "geometry_availability_attempt_01.json"), ("source_label_result_sha256", first_gate / "label_grid_attempt_01.json"), ("source_proof_sha256", first_gate / "independent_raw_geometry_grid_verification.json")]
    for key, path in inputs:
        if sha(path) != prep[key]:
            raise ValueError("Prepared first-batch source differs " + key)
    proof = read(first_gate / "independent_raw_geometry_grid_verification.json")
    if proof["errors"] or prep["status"] != "prepared_not_executed" or [r["patient"] for r in prep["selected"]] != ["VS-MC-RC-001", "VS-MC-RC-002"]:
        raise ValueError("Prepared developer role/source proof differs")
    cases = []
    for chosen in prep["selected"]:
        row, label = copy.deepcopy(chosen["header_row"]), copy.deepcopy(chosen["label_row"])
        refined = chosen["refined_source_geometry"]
        if not refined["refined_header_and_label_grid_passed"]:
            raise ValueError("Prepared corrected source preflight not passed")
        row["summary"].update(affine_rcz_ras=refined["fitted_affine_rcz_ras"], affine_rcz_lps=refined["fitted_affine_rcz_lps"], native_spacing_rcz_mm=refined["native_spacing_rcz_mm"], header_qualified_candidate=refined["refined_header_qualified"], max_affine_position_residual_mm=refined["max_fitted_position_residual_mm"], fit_method="first-batch post-result all-IPP correction; independently verified")
        label["grid"] = refined["grid_with_fitted_affine"]
        label["header_and_label_grid_preflight_passed"] = refined["refined_header_and_label_grid_passed"]
        cases.append({"patient": chosen["patient"], "header": row, "label": label, "role": "development", "geometry_lineage": "retained first-batch correction, not original median-step estimate"})
    cls, checkpoint, expected = MODELS["hat"]
    if sha(checkpoint) != expected:
        raise ValueError("Frozen HAT weight differs")
    files = [PLAN, Path(__file__), PREPARATION, checkpoint, *[p for _, p in inputs], ROOT / "experiments/mc_rc_three_development_action_oracle.py", ROOT / "experiments/vs_seg_full_volume_runtime.py", ROOT / "experiments/remind_native_t2_ixi_pair.py", ROOT / "experiments/vs_seg_task_cpu_support.py", ROOT.parent / "baseline/ixi_hat_2p5d/train.py", ROOT.parent / "baseline/ixi_hat_2p5d/model.py", ROOT.parent / "pre/ixi_diffusion/common.py"]
    for case in cases:
        files.extend([HEADERS / case["header"]["header_file"], ROOT / case["header"]["transfer"]["file"], ROOT / case["label"]["label_file"]])
    prior_result = ROOT / "experiments/mc_rc_three_development_action_oracle/attempt_01.json"
    files.append(prior_result)
    contract = {"created_utc": datetime.now(timezone.utc).isoformat(), "cases": cases, "primary_action": ["raw_pchip", "hat"], "secondary_action": ["pipeline_pchip", "hat"], "tile_size": 32, "selection_after_prior_development_results": True, "original_pipeline_primary_success": False, "independent_confirmation": False,
                "files": [{"path": p.relative_to(ROOT.parent).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(set(files))]}
    write(OUT / "run_contract.json", contract)
    return cases, cls, checkpoint


def technical_headers(case):
    row = case["header"]
    records = []
    with zipfile.ZipFile(ROOT / row["transfer"]["file"]) as archive:
        for member in row["summary"]["ordered_zip_members"]:
            with archive.open(member) as stream:
                ds = pydicom.dcmread(stream, stop_before_pixels=True)
            if str(ds.PatientID) != case["patient"] or str(ds.SeriesInstanceUID) != row["source"]["SeriesInstanceUID"] or str(ds.StudyInstanceUID) != row["source"]["StudyInstanceUID"] or str(ds.get("PhotometricInterpretation", "")) != "MONOCHROME2" or int(ds.get("NumberOfFrames", 1)) != 1:
                raise ValueError("Raw MR technical identity/photometric/frame gate failed")
            records.append({"sop_uid": str(ds.SOPInstanceUID), "transfer_syntax": str(ds.file_meta.TransferSyntaxUID), "bits_allocated": int(ds.BitsAllocated), "slope": float(ds.get("RescaleSlope", 1)), "intercept": float(ds.get("RescaleIntercept", 0))})
    return records


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resource_gate()
    OUT.mkdir(parents=True, exist_ok=False)
    cases, cls, checkpoint = freeze()
    helper.HEADERS, helper.BASES = HEADERS, ("raw_pchip", "pipeline_pchip")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    def deny_cuda(*args, **kwargs):
        raise RuntimeError("CUDA initialization prohibited")
    torch.cuda._lazy_init = deny_cuda
    model = cls(checkpoint, device="cpu")
    result = {"started_utc": datetime.now(timezone.utc).isoformat(), "complete": False, "run_contract_sha256": sha(OUT / "run_contract.json"), "patients_expected": 2, "patients": [], "failures": [], "gpu_used": False, "publication_claim_confirmed": False, "original_pipeline_primary_success": False}
    write(OUT / "attempt_01.json", result)
    for case in cases:
        start = time.perf_counter()
        try:
            resource_gate()
            transport = technical_headers(case)
            native, label = helper.decode(case)
            prep = prepared(native[:, :, ::4])
            if prep[2] <= prep[1]:
                raise ValueError("Invalid observed-only normalization")
            hat = reconstruct("hat", native, prep, {"hat": model})
            if torch.cuda.is_initialized():
                raise ValueError("Unexpected CUDA initialization")
            output = OUT / (case["patient"] + "_hat.npz")
            np.savez_compressed(output, image_rcz=hat, affine_rcz_ras=np.array(case["header"]["summary"]["affine_rcz_ras"]))
            tile_file = OUT / (case["patient"] + "_tiles.csv")
            with tile_file.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["patient", "base", "z", "row", "col", "support_pixels", "d", "m", "alpha", "base_sse", "oracle_sse", "oracle_gain"])
                writer.writeheader()
                analysis = helper.analyse(case, native, label, hat, prep, writer)
            analysis.update(technical_header_records=transport, hat_file=output.relative_to(ROOT).as_posix(), hat_sha256=sha(output), tiles_file=tile_file.relative_to(ROOT).as_posix(), tiles_sha256=sha(tile_file), seconds=time.perf_counter() - start)
            result["patients"].append(analysis)
            print(json.dumps({"patient": case["patient"], "seconds": analysis["seconds"], "actions": [{k: a[k] for k in ("base", "support_gain_db_vs_better_fixed", "lesion_guard", "development_gate_passed")} for a in analysis["actions"]]}), flush=True)
            del native, label, hat
        except Exception as exc:
            result["failures"].append({"patient": case["patient"], "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
            print(json.dumps(result["failures"][-1]), flush=True)
        write(OUT / "attempt_01.json", result)
    result.update(complete=len(result["patients"]) == 2 and not result["failures"], finished_utc=datetime.now(timezone.utc).isoformat(), cuda_initialized=torch.cuda.is_initialized())
    result["primary_fixed_action_development_gate_passed"] = result["complete"] and all(next(a for a in p["actions"] if a["base"] == "raw_pchip")["development_gate_passed"] for p in result["patients"])
    prior = read(ROOT / "experiments/mc_rc_three_development_action_oracle/attempt_01.json")
    result["all_five_raw_development_gate_passed"] = result["primary_fixed_action_development_gate_passed"] and prior["complete"] and all(next(a for a in p["actions"] if a["base"] == "raw_pchip")["development_gate_passed"] for p in prior["patients"])
    write(OUT / "attempt_01.json", result)
    print(json.dumps({"complete": result["complete"], "primary_fixed_action_development_gate_passed": result["primary_fixed_action_development_gate_passed"], "all_five_raw_development_gate_passed": result["all_five_raw_development_gate_passed"], "failures": result["failures"]}), flush=True)
    return int(not result["complete"])


if __name__ == "__main__":
    raise SystemExit(main())
