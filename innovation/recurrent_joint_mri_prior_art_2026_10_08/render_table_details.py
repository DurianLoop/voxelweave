"""Extra readable crops for visual transcription; same seven source pages."""
import sys,json,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'table_visual_attempt01'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();tick=time.perf_counter()
    OUT.mkdir(exist_ok=False);rows=[];source=HERE/'primary_attempt01/mmar.pdf'
    doc=pdfium.PdfDocument(str(source))
    for n in [17,19,20,22,23,24,25]:
        resource_guard();page=doc[n-1];bitmap=page.render(scale=3);im=bitmap.to_pil()
        w,h=im.size
        top,bottom=(.46,.80) if n==20 else (.37,.74)
        box=(round(.18*w),round(top*h),round(.475*w),round(bottom*h))
        crop=im.crop(box);p=OUT/f'mmar_page{n:03d}_macro.png';crop.save(p)
        crop.close();im.close();bitmap.close();page.close()
        rows.append(dict(physical_page=n,PDF_source=base.entry(source),image=base.entry(p),
                         full_render_scale=3,crop_box=box,visual_reviewed=False))
    doc.close()
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,
        errors=[],records=rows,source_bindings=[base.entry(p) for p in
        (Path(__file__),HERE/'PROTOCOL.md',HERE/'visual_attempt01/receipt.json')],
        additional_unique_source_pages=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        elapsed_seconds=time.perf_counter()-tick))
    print(json.dumps(dict(complete=True,cropped_images=7,additional_unique_pages=0)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
