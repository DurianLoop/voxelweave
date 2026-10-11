"""Render two original pages; rendering itself does not count as reading."""
import sys, json
from pathlib import Path
import query_seranet_stdlib_v3 as prior

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE/'table_visual_attempt01'
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    prior.base.own_priority()
    resources = prior.resource_guard()
    OUT.mkdir(exist_ok=False)
    src = HERE/'primary_attempt01/sadfn.pdf'
    assert src.read_bytes().startswith(b'%PDF-')
    doc = pdfium.PdfDocument(str(src))
    rows = []
    for n in (13,14):
        page = doc[n-1]
        bitmap = page.render(scale=2)
        im = bitmap.to_pil()
        p = OUT/f'sadfn_page{n:03d}_detail.png'
        im.save(p)
        im.close(); bitmap.close(); page.close()
        rows.append(dict(physical_page=n,image=prior.base.entry(p),PDF_source=prior.base.entry(src),visual_reviewed=False))
    doc.close()
    prior.base.new(OUT/'receipt.json',dict(complete=True,errors=[],records=rows,resource_snapshot=resources,
        source_bindings=[prior.base.entry(p) for p in (Path(__file__),HERE/'METADATA_FOLLOWUP_PLAN.md')]))
    print(json.dumps(dict(complete=True,detail_images=2,resource_snapshot=resources)))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
