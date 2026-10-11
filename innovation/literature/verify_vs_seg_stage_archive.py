"""Verify source/protocol lineage and hash the concrete VS-SEG stage artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "literature/source_cache/vs_seg_stage_archive_2026-10-02.json"
WRITE = "--write" in sys.argv


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1_048_576), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    errors = []
    current = ROOT / "VS_SEG_CPU_COMPATIBILITY_PROBE_PLAN_2026-10-02.md"
    old = ROOT / "VS_SEG_CPU_COMPATIBILITY_PROBE_PLAN_2026-10-02_v1.md"
    if WRITE:
        text = current.read_text(encoding="utf-8").split("\n\nAfter a successful small-input strict-load probe,", 1)[0] + "\n"
        if hashlib.sha256(text.encode()).hexdigest() != "dbf20f8fcd48552eef80bb314e444d72ff2c5f2aa40192aff20931cac54ae2bd":
            raise ValueError("Cannot reconstruct exact pre-addendum software plan")
        old.write_bytes(text.encode("utf-8"))
    if not old.is_file() or sha256(old) != "dbf20f8fcd48552eef80bb314e444d72ff2c5f2aa40192aff20931cac54ae2bd":
        errors.append("Initial CPU probe plan snapshot missing or differs")
    author = ROOT / "literature/source_cache/vs_seg_author_code_2026-10-01"
    index = json.loads((author / "index.json").read_text())
    author_verified = 0
    for item in index:
        if "git_blob_sha" not in item:
            continue
        raw = (author / item["file"]).read_bytes()
        if hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() != item["git_blob_sha"]:
            errors.append(f"Author Git blob differs: {item['file']}")
        if hashlib.sha256(raw).hexdigest() != item["sha256"]:
            errors.append(f"Author SHA-256 differs: {item['file']}")
        author_verified += 1
    original_protocol = ROOT / "VS_SEG_THIN3D_MODEL_CONFIRMATION_PROTOCOL_2026-10-01.md"
    protocol_hash = sha256(original_protocol)
    contract_path = ROOT / "experiments/vs_seg_thin3d_model_confirmation/run_contract.json"
    contract_hash = sha256(contract_path)
    contract = json.loads(contract_path.read_text())
    frozen_inputs = {"protocol_sha256": original_protocol,
                     "nonpixel_sha256": ROOT / "literature/source_cache/vs_seg_nonpixel_cohort_2026-10-01.json",
                     "mapping_sha256": ROOT / "literature/source_cache/vs_seg_official_inventory_2026-10-01/mapping.csv",
                     "script_sha256": ROOT / "experiments/vs_seg_thin3d_model_confirmation.py",
                     "preflight_sha256": ROOT / "experiments/vs_seg_001_model_preflight.json"}
    for key, path in frozen_inputs.items():
        if sha256(path) != contract[key]:
            errors.append(f"Stopped original frozen input differs: {key}")
    cases = []
    for path in sorted((ROOT / "experiments/vs_seg_thin3d_model_confirmation/cases").glob("*.json")):
        record = json.loads(path.read_text())
        if record.get("contract_sha256") != contract_hash:
            errors.append(f"Stopped original case protocol differs: {path.name}")
        cases.append(record)
    if len(cases) != 14 or sum(r["complete"] for r in cases) != 1:
        errors.append("Stopped 14-case history changed")
    candidates = set()
    for pattern in ("VS_SEG*.md", "SESSION*VS_SEG*.md"):
        candidates.update(ROOT.glob(pattern))
    for pattern in ("*vs_seg*.py", "*vs_seg*.md"):
        candidates.update((ROOT / "literature").glob(pattern))
    candidates.update({ROOT / "literature/fetch_task_metric_papers_2026_10_02.py",
                       ROOT / "literature/2026-10-02_task_metric_reading_and_innovation_limits.md",
                       ROOT / "GPU_FOLLOWUP_TASK_FIDELITY_PREPARATION_2026-10-02.md"})
    candidates.update(p for p in (ROOT / "literature/source_cache/task_metric_papers_2026-10-02").rglob("*") if p.is_file())
    for path in (ROOT / "experiments").glob("vs_seg*"):
        candidates.update([path] if path.is_file() else (x for x in path.rglob("*") if x.is_file()))
    candidates.update((ROOT / "experiments").glob("verify_vs_seg*.py"))
    for path in (ROOT / "literature/source_cache").glob("vs_seg*"):
        candidates.update([path] if path.is_file() else (x for x in path.rglob("*") if x.is_file()))
    for path in (ROOT / "data").glob("vs_seg*"):
        candidates.update([path] if path.is_file() else (x for x in path.rglob("*") if x.is_file()))
    candidates.update(x for x in (ROOT / "tools/vs_seg_cpu_compat").rglob("*") if x.is_file())
    slicer_stage = ROOT / "tools/vs_seg_slicer_cpu"
    candidates.update(x for x in slicer_stage.rglob("*") if x.is_file())
    slicerrt_verified = 0
    routes = ROOT / "literature/source_cache/vs_seg_original_mask_routes_2026-10-02"
    conversion_index = routes / "conversion_paths_index.json"
    if conversion_index.exists():
        for item in json.loads(conversion_index.read_text())["sources"]:
            raw = (routes / item["file"]).read_bytes()
            if hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() != item["git_blob_sha"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
                errors.append("SlicerRT authenticated source differs: " + item["file"])
            slicerrt_verified += 1
    runtime_manifest = slicer_stage / "runtime_manifest.json"
    if runtime_manifest.exists():
        for item in json.loads(runtime_manifest.read_text())["entries"]:
            p = slicer_stage / item["file"]
            if p.stat().st_size != item["bytes"] or sha256(p) != item["sha256"]:
                errors.append("Isolated Slicer runtime changed: " + item["file"])
        download = json.loads((slicer_stage / "download_attempt_01.json").read_text())
        for item in download["packages"]:
            p = slicer_stage / item["file"]
            h = hashlib.sha512()
            with p.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1_048_576), b""):
                    h.update(chunk)
            if h.hexdigest() != item["official_sha512"]:
                errors.append("Official Slicer package digest differs: " + item["file"])
        development = ROOT / "experiments/vs_seg_original_mask_cpu_development"
        old_conversion = json.loads((development / "attempt_03.json").read_text())
        if sha256(development / "development_converter_v1_snapshot.py") != old_conversion["script_sha256"]:
            errors.append("Original development converter source snapshot differs")
    candidates.discard(MANIFEST)
    entries = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)}
               for p in sorted(candidates)]
    result = {"scope": "VS-SEG stage protocols, visible conversation records, scripts, source archives, runtime dependencies and outputs",
              "author_original_files_git_blob_verified": author_verified,
              "slicerrt_source_git_blobs_verified": slicerrt_verified,
              "stopped_original_attempts": len(cases), "stopped_original_completed": sum(r["complete"] for r in cases),
              "original_protocol_sha256": protocol_hash,
              "original_run_contract_sha256": contract_hash,
              "scientific_publication_goal_achieved": False, "entries": entries}
    if WRITE and not errors:
        MANIFEST.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    elif not WRITE and (not MANIFEST.exists() or json.loads(MANIFEST.read_text()) != result):
        errors.append("Stage manifest is missing or out of date")
    print(json.dumps({"files": len(entries), "bytes": sum(r["bytes"] for r in entries),
                      "author_original_git_blobs_verified": author_verified, "errors": errors}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
