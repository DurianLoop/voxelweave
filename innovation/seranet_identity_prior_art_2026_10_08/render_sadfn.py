"""Render only the successfully downloaded original SADFN, not HTML saved under a PDF name."""
import sys,json,time
from pathlib import Path
from datetime import datetime,timezone
import query_seranet_stdlib_v3 as prior
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'visual_attempt01';base=prior.base
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium
def main():
    sys.stdout.reconfigure(encoding='utf-8');prior.resource_guard();OUT.mkdir(exist_ok=False);tick=time.perf_counter()
    source=HERE/'primary_attempt01/sadfn.pdf';assert source.read_bytes().startswith(b'%PDF-')
    doc=pdfium.PdfDocument(str(source));assert len(doc)==16;rows=[]
    for n in [1,2,6,7,8,9,10,11,12,13,14,15]:
        prior.resource_guard();page=doc[n-1];bitmap=page.render(scale=1.5);im=bitmap.to_pil();p=OUT/f'sadfn_page{n:03d}.png'
        im.save(p);im.close();bitmap.close();page.close()
        rows.append(dict(paper='sadfn',physical_page=n,image=base.entry(p),PDF_source=base.entry(source),visual_reviewed=False))
    doc.close();assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=rows,
        source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'primary_attempt01/receipt.json')],
        partial_download_failure_preserved=True,source_original_PDF_reexported=False,render_not_visual_read=True,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,elapsed_seconds=time.perf_counter()-tick))
    print(json.dumps(dict(complete=True,rendered_unique_pages=12)),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
