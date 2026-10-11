"""Render source identities, architectures and all consequential tables for visual checking."""
import sys,json,time,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'visual_attempt01'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();resource_guard();tick=time.perf_counter()
    assert shutil.disk_usage(ROOT).free>8_050_000_000
    OUT.mkdir(exist_ok=False);rows=[]
    for key,pages in [('segnetmri',[1,3,4,5,6]),('calibrationless',[1,5,6,8,9])]:
        source=HERE/f'primary_attempt01/{key}.pdf';doc=pdfium.PdfDocument(str(source))
        for n in pages:
            resource_guard();page=doc[n-1];bitmap=page.render(scale=1.5);im=bitmap.to_pil()
            p=OUT/f'{key}_page{n:03d}.png';im.save(p);im.close();bitmap.close();page.close()
            rows.append(dict(paper=key,physical_page=n,image=base.entry(p),PDF_source=base.entry(source),visual_reviewed=False))
        doc.close()
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=rows,
       source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'primary_attempt01/receipt.json')],
       original_PDF_reexported=False,render_is_not_visual_review=True,medical_arrays_loaded=0,
       neural_forwards=0,GPU_forwards=0,elapsed_seconds=time.perf_counter()-tick)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',q);print(json.dumps(dict(complete=True,rendered_pages=len(rows))),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
