"""Fetch two actually indexed PDFs; extraction is explicitly not reading."""
import sys,json,time,traceback
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; OUT=HERE/'primary_attempt01'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import fetch_selected_stdlib as downloader
client=downloader.prior; base=client.base

def main():
    sys.stdout.reconfigure(encoding='utf-8'); base.own_priority(); client.resource_guard()
    index=HERE/'index_attempt01/receipt.json'; q=json.loads(index.read_text(encoding='utf-8'))
    rows=next(r['entries'] for r in q['records'] if r['key']=='mri_compute_stopping')
    assert len(rows)==2
    jobs=[]
    for key,ident in [('rd_vit','2605.03999v1'),('hifi_mamba_v2','2511.18534v1')]:
        r=next(r for r in rows if r['id'].endswith('/'+ident))
        urls=[l['href'] for l in r['links'] if l.get('type')=='application/pdf']
        assert urls==['https://arxiv.org/pdf/'+ident]
        jobs.append((key,r,urls[0]))
    OUT.mkdir(exist_ok=False); downloader.OUT=OUT; tick=time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool: records=list(pool.map(downloader.fetch,jobs))
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    import pypdfium2 as pdfium
    for r in records:
        if not r['complete']:continue
        try:
            doc=pdfium.PdfDocument(str(ROOT/r['file']['path'])); r['physical_pages']=len(doc); r['page_texts']=[]
            for n in range(len(doc)):
                client.resource_guard(); page=doc[n]; tp=page.get_textpage(); p=OUT/f"{r['key']}_page{n+1:03d}.txt"
                with p.open('x',encoding='utf-8') as f:f.write(tp.get_text_range())
                r['page_texts'].append(dict(physical_page=n+1,text_read=False,**base.entry(p)))
                tp.close(); page.close()
            doc.close()
        except Exception as e:r['complete']=False;r['errors'].append(repr(e));r['traceback']=traceback.format_exc()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in records),
        errors=[e for r in records for e in r['errors']],records=records,
        source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PRIMARY_SELECTION.md',HERE/'PROTOCOL.md',index)],
        resource_snapshot=client.resource_guard(),elapsed_seconds=time.perf_counter()-tick,
        public_GET_only=True,TLS_verification_disabled=False,new_primary_papers_read=0,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=result['complete'],records=[{k:r.get(k) for k in ('key','complete','HTTP_status','physical_pages','file','errors')} for r in records]),ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
