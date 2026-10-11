"""Render identity, mechanism and numerical-result pages from the two new originals."""
import sys,json
from pathlib import Path
import query_seranet_stdlib_v3 as prior
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'visual_attempt02'
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium

def main():
    sys.stdout.reconfigure(encoding='utf-8');prior.base.own_priority();prior.resource_guard()
    OUT.mkdir(exist_ok=False);rows=[]
    for key,nums in [('seranet_candidate',[1,2,4,5,6,7,8]),('teacher_forcing',[1,4,5,6,7,10,13])]:
        src=HERE/'primary_attempt02'/f'{key}.pdf'
        assert src.read_bytes().startswith(b'%PDF-')
        doc=pdfium.PdfDocument(str(src))
        for n in nums:
            prior.resource_guard();page=doc[n-1];bitmap=page.render(scale=1.4);im=bitmap.to_pil()
            p=OUT/f'{key}_page{n:03d}.png';im.save(p);im.close();bitmap.close();page.close()
            rows.append(dict(key=key,physical_page=n,image=prior.base.entry(p),PDF_source=prior.base.entry(src),visual_reviewed=False))
        doc.close()
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    prior.base.new(OUT/'receipt.json',dict(complete=True,errors=[],records=rows,
        source_bindings=[prior.base.entry(p) for p in (Path(__file__),HERE/'RECURRENT_PRIMARY_SELECTION.md',HERE/'primary_attempt02/receipt.json')],
        resource_snapshot=prior.resource_guard(),rendering_not_reading=True))
    print(json.dumps(dict(complete=True,images=len(rows))))
    return 0
if __name__=='__main__':raise SystemExit(main())
