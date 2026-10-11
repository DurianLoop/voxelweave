"""Execute the fixed eight-series source follow-up with bounded sequential transfer."""
from __future__ import annotations

import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from vs_seg_task_cpu_support import resource_gate
from mc_rc_native_header_geometry_v2 import geometry
import download_mc_rc_three_patient_headers_2026_10_02 as legacy

OUT = ROOT / "literature/source_cache/mc_rc_004_006_native_headers_2026-10-02"
DATA = ROOT / "data/mc_rc_004_006_native_header_gate"
SELECTION = ROOT / "experiments/mc_rc_native_t2_label_gate/labelled_native_expansion_preparation.json"
PLAN = ROOT / "MC_RC_004_006_NATIVE_AND_LABEL_EXECUTION_PLAN_2026-10-02.md"
TOTAL_CAP = 500_000_000
budget_used = 0
sha, read, write, now = legacy.sha, legacy.read, legacy.write, legacy.now


def download(key, url, cap, attempt):
    global budget_used
    target = DATA / f"{key}_attempt_{attempt:02d}.zip"
    partial = target.with_suffix(".partial")
    result = {"key": key, "url": url, "cap_bytes": cap, "started_utc": now()}
    count, started = 0, time.monotonic()
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            response = opener.open(urllib.request.Request(url, headers={"User-Agent": "MRI-native-labelled-source-gate/2.0", "Accept-Encoding": "identity"}), timeout=30)
        except urllib.error.HTTPError as exc:
            remaining = TOTAL_CAP - budget_used
            raw = exc.read(min(64_000, remaining))
            budget_used += len(raw)
            count += len(raw)
            error_file = OUT / f"{key}_attempt_{attempt:02d}.error_response"
            error_file.write_bytes(raw)
            result.update(http_status=exc.code, error_response_file=error_file.name, error_response_sha256=sha(error_file))
            raise
        with response:
            result.update(http_status=response.status, final_url=response.url, content_type=response.headers.get("Content-Type"), content_length=response.headers.get("Content-Length"))
            if response.status != 200:
                raise ValueError("Expected complete public archive response")
            if result["content_length"] and int(result["content_length"]) > min(cap, TOTAL_CAP - budget_used):
                raise ValueError("Declared archive exceeds remaining fixed budget")
            with partial.open("xb") as f:
                while True:
                    if time.monotonic() - started > 180:
                        raise TimeoutError("Series transfer deadline exceeded")
                    remaining = min(cap - count, TOTAL_CAP - budget_used)
                    if remaining <= 0:
                        raise ValueError("Fixed byte budget reached before EOF certification")
                    chunk = response.read(min(1_048_576, remaining))
                    if not chunk:
                        break
                    f.write(chunk)
                    count += len(chunk)
                    budget_used += len(chunk)
            if result["content_length"] and count != int(result["content_length"]):
                raise ValueError("Incomplete declared archive")
        partial.rename(target)
        result.update(complete=True, file=target.relative_to(ROOT).as_posix(), bytes=count, sha256=sha(target))
    except Exception as exc:
        result.update(complete=False, error=f"{type(exc).__name__}: {exc}", bytes=count)
        if partial.exists():
            result.update(partial_file=partial.relative_to(ROOT).as_posix(), partial_sha256=sha(partial))
    result["finished_utc"] = now()
    return result


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    resources = resource_gate()
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob("attempt_*.json"))) + 1
    selected = read(SELECTION)
    sources = sorted((r["source"] for r in selected["next_batch_series"]), key=lambda r: (r["PatientID"], r["StudyDate"], r["SeriesInstanceUID"]))
    if selected["next_batch_patient_ids"] != ["VS-MC-RC-004", "VS-MC-RC-005", "VS-MC-RC-006"] or len(sources) != 8:
        raise ValueError("Frozen source selection differs")
    legacy.OUT, legacy.DATA, legacy.geometry = OUT, DATA, geometry
    ledger = {
        "attempt": attempt, "started_utc": now(), "script_sha256": sha(__file__),
        "plan_sha256": sha(PLAN), "selection_sha256": sha(SELECTION),
        "header_helper_sha256": sha(Path(legacy.__file__)),
        "geometry_v2_sha256": sha(ROOT / "experiments/mc_rc_native_header_geometry_v2.py"),
        "resource_gate_sha256": sha(ROOT / "experiments/vs_seg_task_cpu_support.py"),
        "resources": resources, "total_cap_bytes": TOTAL_CAP, "max_connections": 1,
        "scope": "MR archive transfers contain pixel bytes; DICOM headers only; no new MR or label array decoding",
        "MR_pixel_array_decoded": False, "label_arrays_decoded": False,
        "patient_performance_statistics_computed": False, "complete": False, "series": [],
    }
    path = OUT / f"attempt_{attempt:02d}.json"
    write(path, ledger)
    for src in sources:
        resource_gate()
        uid = src["SeriesInstanceUID"]
        cap = max(5_000_000, math.ceil(1.15 * src["FileSize"]) + 1_000_000)
        transfer = download(src["PatientID"] + "_" + uid, legacy.BASE + urllib.parse.urlencode({"SeriesInstanceUID": uid}), cap, attempt)
        row = legacy.inspect_series(transfer, src, attempt)
        ledger["series"].append(row)
        ledger["total_transfer_bytes"] = budget_used
        write(path, ledger)
        print(__import__("json").dumps({"patient": src["PatientID"], "description": src["SeriesDescription"], "headers_complete": row["headers_complete"], "header_qualified_candidate": row.get("summary", {}).get("header_qualified_candidate"), "transfer_bytes": transfer["bytes"], "error": row.get("header_error", transfer.get("error"))}), flush=True)
    ledger.update(finished_utc=now(), complete=all(r["headers_complete"] for r in ledger["series"]), total_transfer_bytes=budget_used, header_qualified_series=sum(r.get("summary", {}).get("header_qualified_candidate", False) for r in ledger["series"]))
    write(path, ledger)
    print(__import__("json").dumps({"complete": ledger["complete"], "header_qualified_series": ledger["header_qualified_series"], "total_transfer_bytes": budget_used}), flush=True)
    return int(not ledger["complete"])


if __name__ == "__main__":
    raise SystemExit(main())
