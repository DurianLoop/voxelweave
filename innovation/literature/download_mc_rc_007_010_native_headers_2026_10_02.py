"""Execute the fixed seven-series, bounded source-only follow-up."""
from __future__ import annotations
import json
import math
import os
import sys
import urllib.parse
from pathlib import Path
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from vs_seg_task_cpu_support import resource_gate
from mc_rc_native_header_geometry_v2 import geometry
import download_mc_rc_004_006_native_headers_2026_10_02 as bounded
import download_mc_rc_three_patient_headers_2026_10_02 as header
OUT = ROOT / "literature/source_cache/mc_rc_007_010_native_headers_2026-10-02"
DATA = ROOT / "data/mc_rc_007_010_native_header_gate"
SELECTION = ROOT / "experiments/mc_rc_visible_joint_development_diagnostic/next_developer_source_preparation.json"
PLAN = ROOT / "MC_RC_007_010_SOURCE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md"
TOTAL_CAP = 350_000_000
sha, read, write, now = header.sha, header.read, header.write, header.now

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resources = resource_gate()
    selected = read(SELECTION)
    if selected["status"] != "prepared_not_executed" or selected["next_batch_patient_ids"] != ["VS-MC-RC-007", "VS-MC-RC-009", "VS-MC-RC-010"] or len(selected["next_batch_series"]) != 7 or selected["network_requests_made"] != 0:
        raise ValueError("Fixed source preparation differs")
    sources = sorted((r["source"] for r in selected["next_batch_series"]), key=lambda r: (r["PatientID"], r["StudyDate"], r["SeriesInstanceUID"]))
    if sum(r["ImageCount"] for r in sources) != 527:
        raise ValueError("Fixed API object count differs")
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    if (OUT / "attempt_01.json").exists():
        raise ValueError("No automatic retry or overwrite of fixed source attempt")
    bounded.OUT, bounded.DATA, bounded.TOTAL_CAP, bounded.budget_used = OUT, DATA, TOTAL_CAP, 0
    header.OUT, header.DATA, header.geometry = OUT, DATA, geometry
    ledger = {"attempt": 1, "started_utc": now(), "script_sha256": sha(__file__), "plan_sha256": sha(PLAN), "selection_sha256": sha(SELECTION),
              "bounded_download_helper_sha256": sha(Path(bounded.__file__)), "header_helper_sha256": sha(Path(header.__file__)), "geometry_v2_sha256": sha(ROOT / "experiments/mc_rc_native_header_geometry_v2.py"), "resource_gate_sha256": sha(ROOT / "experiments/vs_seg_task_cpu_support.py"),
              "resources": resources, "total_cap_bytes": TOTAL_CAP, "max_connections": 1, "socket_timeout_seconds": 30, "series_deadline_seconds": 180, "automatic_retries": 0,
              "scope": "MR ZIP transfer contains pixel bytes; classic DICOM headers only; all seven fixed sources", "MR_pixel_array_decoded": False, "label_arrays_decoded": False, "patient_performance_statistics_computed": False,
              "complete": False, "series": [], "scientific_independent_validation_patients": 0, "publication_claim_confirmed": False}
    path = OUT / "attempt_01.json"
    write(path, ledger)
    for src in sources:
        resource_gate()
        uid = src["SeriesInstanceUID"]
        cap = max(5_000_000, math.ceil(1.15 * src["FileSize"]) + 1_000_000)
        transfer = bounded.download(src["PatientID"] + "_" + uid, header.BASE + urllib.parse.urlencode({"SeriesInstanceUID": uid}), cap, 1)
        row = header.inspect_series(transfer, src, 1)
        ledger["series"].append(row)
        ledger["total_transfer_bytes"] = bounded.budget_used
        write(path, ledger)
        print(json.dumps({"patient": src["PatientID"], "description": src["SeriesDescription"], "headers_complete": row["headers_complete"], "header_qualified_candidate": row.get("summary", {}).get("header_qualified_candidate"), "transfer_bytes": transfer["bytes"], "error": row.get("header_error", transfer.get("error"))}), flush=True)
    ledger.update(finished_utc=now(), complete=len(ledger["series"]) == 7 and all(r["headers_complete"] for r in ledger["series"]), total_transfer_bytes=bounded.budget_used,
                  header_qualified_series=sum(r.get("summary", {}).get("header_qualified_candidate", False) for r in ledger["series"]))
    write(path, ledger)
    print(json.dumps({k: ledger[k] for k in ("complete", "header_qualified_series", "total_transfer_bytes")}), flush=True)
    return int(not ledger["complete"])

if __name__ == "__main__":
    raise SystemExit(main())
