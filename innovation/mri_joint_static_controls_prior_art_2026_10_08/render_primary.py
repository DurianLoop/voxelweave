"""Render primary algorithm, cohort and numerical pages without editing PDFs."""
import sys,json,time,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();assert shutil.disk_usage(ROOT).free>8_050_000_000
    out=HERE/'visual_attempt01';out.mkdir(exist_ok=False);tick=time.perf_counter();rows=[]
    jobs=[('masc',HERE/'primary_attempt01/masc.pdf',[4,5,7,10,11,12,17,18]),
        ('thesis',HERE/'thesis_size_verified_attempt02/cartesian_thesis.pdf',[66,110,112,114])]
    for key,source,pages in jobs:
        doc=pdfium.PdfDocument(str(source))
        for n in pages:
            page=doc[n-1];bitmap=page.render(scale=1.4);im=bitmap.to_pil();p=out/f'{key}_page{n:03d}.png';im.save(p)
            rows.append(dict(paper=key,physical_page=n,image=base.entry(p),PDF_source=base.entry(source),visual_reviewed=False))
            im.close();bitmap.close();page.close()
        doc.close()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=rows,
        source_bindings=[base.entry(Path(__file__)),base.entry(HERE/'primary_attempt01/receipt.json'),
            base.entry(HERE/'thesis_text_attempt01/receipt.json')],original_PDF_reexported=False,
        render_is_not_visual_review=True,elapsed_seconds=time.perf_counter()-tick,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(out/'receipt.json',result);print(json.dumps(dict(complete=True,rendered_pages=len(rows))),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
