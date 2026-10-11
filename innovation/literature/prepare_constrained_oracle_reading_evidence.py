"""Bounded rereading evidence from six already archived papers; no network."""
from __future__ import annotations
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "literature/source_cache/constrained_oracle_reading_2026-10-02"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    specs = [
        ("SafeRestore", "literature/extracted/SafeRestore_2026.txt", [(270, 435), (440, 526)]),
        ("MoEDiff_SR", "literature/extracted/2025_MoEDiff-SR_Mixture_of_Experts-Guided_Diffusion_Model_for_Region-Adaptive_MRI_SR.txt", [(1, 44), (180, 330)]),
        ("Glioma_task_UQ", "literature/extracted/glioma_task_aware_uq_2026.txt", [(1398, 1490), (1987, 2022)]),
        ("CISS_SR", "literature/source_cache/task_throughplane_fulltexts_2026-10-02/ciss_vs_2026_maintext.txt", [(9, 40)]),
        ("Segmentation_guided", "literature/source_cache/segmentation_guided_mri_2026-10-01/article.txt", []),
        ("SURE_parameter", "literature/source_cache/risk_action_bodies_2026-10-02/gsure_parameter_2012_efetch_attempt_01_maintext.txt", []),
    ]
    records = []
    for name, relative, intervals in specs:
        path = ROOT / relative
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        chunks = []
        for first, last in intervals:
            chunks.append({"first_line": first, "last_line": last, "text": "\n".join(lines[first - 1:last])})
        if not intervals:
            patterns = [r"segmentation-loss", r"segmentation loss", r"volume", r"nontrivial null", r"null space", r"projected-MSE", r"projected MSE"]
            seen = set()
            for pattern in patterns:
                for match in list(re.finditer(pattern, raw, flags=re.I))[:2]:
                    lo, hi = max(0, match.start() - 250), min(len(raw), match.end() + 800)
                    if lo in seen:
                        continue
                    chunks.append({"first_character": lo, "last_character": hi, "search_term": pattern, "text": raw[lo:hi]})
                    seen.add(lo)
        record = {"paper": name, "source_file": relative, "source_sha256": sha(path), "scope": "selected relevant methods/results passages reread; not a new full-text acquisition or entire-paper equation audit", "excerpts": chunks}
        out = OUT / (name + "_bounded_excerpts.json")
        out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        records.append({"paper": name, "source_file": relative, "source_sha256": sha(path), "excerpts_file": out.relative_to(ROOT).as_posix(), "excerpts_sha256": sha(out), "excerpt_count": len(chunks)})
    rendered, render_error = [], None
    specs_pdf = [(ROOT / "literature/SafeRestore_2026.pdf", [5, 6, 7]), (ROOT / "literature/2025_MoEDiff-SR_Mixture_of_Experts-Guided_Diffusion_Model_for_Region-Adaptive_MRI_SR.pdf", [4])]
    renderer = "PyMuPDF"
    try:
        import fitz
        for path, pages in specs_pdf:
            with fitz.open(path) as document:
                for page in pages:
                    out = OUT / (path.stem + "_page_" + str(page) + ".png")
                    document[page - 1].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(out)
                    rendered.append({"source_pdf": path.relative_to(ROOT).as_posix(), "source_sha256": sha(path), "page": page, "png": out.relative_to(ROOT).as_posix(), "png_sha256": sha(out)})
    except ImportError as error:
        render_error = str(error)
        renderer = shutil.which("pdftoppm")
        if renderer:
            for path, pages in specs_pdf:
                for page in pages:
                    out = OUT / (path.stem + "_page_" + str(page) + ".png")
                    command = [renderer, "-f", str(page), "-l", str(page), "-scale-to", "1600", "-singlefile", "-png", str(path), str(out.with_suffix(""))]
                    run = subprocess.run(command, capture_output=True, timeout=45)
                    if run.returncode or not out.is_file():
                        raise RuntimeError(run.stderr.decode("utf-8", errors="replace"))
                    rendered.append({"source_pdf": path.relative_to(ROOT).as_posix(), "source_sha256": sha(path), "page": page, "png": out.relative_to(ROOT).as_posix(), "png_sha256": sha(out)})
            render_error = None
    index = {"created_utc": datetime.now(timezone.utc).isoformat(), "script_sha256": sha(Path(__file__)), "network_requests_made": 0, "new_papers_acquired": 0, "papers_reread": len(records), "records": records, "rendered_pages": rendered, "renderer": renderer, "render_error": render_error, "prior_renderer_limitation": "PyMuPDF unavailable; existing MiKTeX Poppler fallback used, no environment changes", "gpu_used": False}
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"papers_reread": len(records), "rendered_pages": len(rendered), "render_error": render_error}))

if __name__ == "__main__":
    main()
