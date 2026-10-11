"""Render selected actual pages and enumerate public URI annotations."""
import sys,json,ctypes
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'visual_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
import pypdfium2 as pdfium
from pypdfium2 import raw

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();OUT.mkdir(exist_ok=False)
    rows=[];uris=[]
    jobs=[('rd_vit',[1,7,9,10,11,12,13,14,15,21,22,23]),('hifi_mamba_v2',[1,3,4,5,6,7,9])]
    for key,selected in jobs:
        src=HERE/'primary_attempt01'/f'{key}.pdf';doc=pdfium.PdfDocument(str(src))
        for n in range(1,len(doc)+1):
            client.resource_guard();page=doc[n-1]
            start=ctypes.c_int(0);link=raw.FPDF_LINK()
            while raw.FPDFLink_Enumerate(page.raw,ctypes.byref(start),ctypes.byref(link)):
                action=raw.FPDFLink_GetAction(link)
                if action and raw.FPDFAction_GetType(action)==raw.PDFACTION_URI:
                    size=raw.FPDFAction_GetURIPath(doc.raw,action,None,0)
                    if size:
                        buf=ctypes.create_string_buffer(size);raw.FPDFAction_GetURIPath(doc.raw,action,buf,size)
                        uris.append(dict(key=key,physical_page=n,URI=buf.value.decode('utf-8',errors='replace')))
            if n in selected:
                bm=page.render(scale=1.5);im=bm.to_pil();p=OUT/f'{key}_page{n:03d}.jpg'
                im.convert('RGB').save(p,quality=90,optimize=True)
                rows.append(dict(key=key,physical_page=n,image=client.base.entry(p),PDF_source=client.base.entry(src),visual_reviewed=False))
                im.close();bm.close()
            page.close()
        doc.close()
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<28_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],records=rows,URI_annotations=uris,
        source_bindings=[client.base.entry(p) for p in (Path(__file__),HERE/'VISUAL_AND_SOURCE_PLAN.md',HERE/'primary_attempt01/receipt.json')],
        resource_snapshot=client.resource_guard(),medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    client.base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=True,rendered_pages=len(rows),URI_annotations=uris),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
