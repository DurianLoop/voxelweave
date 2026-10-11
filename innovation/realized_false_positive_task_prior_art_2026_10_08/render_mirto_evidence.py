"""Render selected MIRTO pages; rendering is not an actual visual review."""
import sys,json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'visual_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium
def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.resource_guard();OUT.mkdir(exist_ok=False)
    src=HERE/'primary_attempt01/mirto.pdf';doc=pdfium.PdfDocument(str(src));rows=[]
    for n in [1,3,5,6,9,13,15,16,21,25,32,35,40]:
        client.resource_guard();page=doc[n-1];bm=page.render(scale=1.6);im=bm.to_pil();p=OUT/f'mirto_page{n:03d}.jpg'
        im.convert('RGB').save(p,quality=90,optimize=True)
        rows.append(dict(physical_page=n,image=client.base.entry(p),PDF_source=client.base.entry(src),visual_reviewed=False))
        im.close();bm.close();page.close()
    doc.close();assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=rows,
        source_bindings=[client.base.entry(p) for p in [Path(__file__),HERE/'VISUAL_AND_FALLBACK_PLAN.md',HERE/'primary_attempt01/receipt.json']],
        resource_snapshot=client.resource_guard(),medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    client.base.new(OUT/'receipt.json',q);print(json.dumps(dict(complete=True,rendered_pages=len(rows),resource_snapshot=q['resource_snapshot'])),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
