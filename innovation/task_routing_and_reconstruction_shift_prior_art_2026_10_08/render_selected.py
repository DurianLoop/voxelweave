"""Render existing PDF pages for formula/table QA; preserve original PDFs."""
import sys,json,time,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium

def main():
    sys.stdout.reconfigure(encoding='utf-8');tick=time.perf_counter();resource_guard();assert shutil.disk_usage(ROOT).free>8_050_000_000
    out=HERE/'visual_attempt01';out.mkdir(exist_ok=False);rows=[]
    jobs=[('tadt',HERE/'tadt_size_verified_attempt03/tadt.pdf',[1,3,4,5,6,7,9,10]),
          ('medical_shift',HERE/'primary_attempt02/medical_shift.pdf',[5,7,10,11,21,23,28])]
    for key,source,pages in jobs:
        doc=pdfium.PdfDocument(str(source))
        for n in pages:
            resource_guard();page=doc[n-1];bitmap=page.render(scale=1.5);im=bitmap.to_pil();p=out/f'{key}_page{n:03d}.png';im.save(p)
            rows.append(dict(paper=key,physical_page=n,image=base.entry(p),PDF_source=base.entry(source),visual_reviewed=False))
            im.close();bitmap.close();page.close()
        doc.close()
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=rows,
        source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'primary_attempt02/receipt.json',HERE/'tadt_text_attempt05/receipt.json')],
        original_PDF_reexported=False,render_is_not_visual_review=True,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        elapsed_seconds=time.perf_counter()-tick,resources_after=resource_guard())
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(out/'receipt.json',q);print(json.dumps(dict(complete=True,rendered_pages=len(rows))),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
