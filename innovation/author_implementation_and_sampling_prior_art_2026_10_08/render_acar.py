"""Render actual original pages for identity, formula and tables; rendering is not reading."""
import sys,json
from pathlib import Path
import query_author_sources as client
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'visual_attempt01'
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.previous.resource_guard()
    OUT.mkdir(exist_ok=False);src=HERE/'primary_attempt01/acar.pdf';assert src.read_bytes().startswith(b'%PDF-')
    doc=pdfium.PdfDocument(str(src));rows=[]
    for n in [1,2,3,4,5,6,7,8]:
        client.previous.resource_guard();page=doc[n-1];bm=page.render(scale=1.7);im=bm.to_pil()
        p=OUT/f'acar_page{n:03d}.png';im.save(p);im.close();bm.close();page.close()
        rows.append(dict(physical_page=n,image=client.base.entry(p),PDF_source=client.base.entry(src),visual_reviewed=False))
    doc.close()
    client.base.new(OUT/'receipt.json',dict(complete=True,errors=[],records=rows,
        source_bindings=[client.base.entry(p) for p in (Path(__file__),HERE/'VISUAL_AND_TABLE_PLAN.md',HERE/'primary_attempt01/receipt.json')],
        resource_snapshot=client.previous.resource_guard(),medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0))
    print(json.dumps(dict(complete=True,rendered_pages=8)))
    return 0
if __name__=='__main__':raise SystemExit(main())
