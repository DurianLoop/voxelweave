"""Read-only primary PDF rendering, no PDF re-export and no neural imports."""
import sys, json, time, shutil
from pathlib import Path
from datetime import datetime, timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base

def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority()
    assert shutil.disk_usage(ROOT).free>8_050_000_000
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    import pypdfium2 as pdfium
    tick=time.perf_counter();out=HERE/'visual_attempt01';out.mkdir(exist_ok=False);rows=[]
    for key,pages in [('l2sr',[7,9,14,16,18,29]),('diagnostic',[4,5,6,7,11])]:
        source=HERE/'primary_attempt01'/(key+'.pdf');doc=pdfium.PdfDocument(str(source))
        for n in pages:
            page=doc[n-1];bitmap=page.render(scale=1.3);im=bitmap.to_pil()
            path=out/f'{key}_page{n:02d}.png';assert not path.exists();im.save(path)
            rows.append(dict(paper=key,physical_page=n,image=base.entry(path),PDF_source=base.entry(source),visual_reviewed=False))
            im.close();bitmap.close();page.close()
        doc.close()
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=rows,
        source_bindings=[base.entry(Path(__file__)),base.entry(HERE/'primary_attempt01/receipt.json')],
        elapsed_seconds=time.perf_counter()-tick,original_PDF_reexported=False,render_is_not_visual_review=True,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    base.new(out/'receipt.json',result)
    print(json.dumps(dict(complete=True,rendered_pages=len(rows),elapsed_seconds=result['elapsed_seconds'])),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
