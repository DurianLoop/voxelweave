"""Download only actual indexed identities; public verified HTTPS and bounded extraction."""
import sys,json,time,shutil,traceback,ssl
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from urllib.request import build_opener,ProxyHandler,HTTPSHandler,Request
from urllib.error import HTTPError
from urllib.parse import urlsplit
import query_seranet_stdlib_v3 as prior
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'primary_attempt01'
base=prior.base;resource_guard=prior.resource_guard
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def fetch(job):
    key,record,url=job;tick=time.perf_counter();row=dict(key=key,indexed_record=record,requested_url=url,complete=False,errors=[])
    try:
        context=ssl.create_default_context();assert context.verify_mode==ssl.CERT_REQUIRED and context.check_hostname
        opener=build_opener(ProxyHandler({}),HTTPSHandler(context=context),prior.LimitedRedirect())
        request=Request(url,headers={'User-Agent':'MRI-innovation-literature-audit/1.0'},method='GET')
        with opener.open(request,timeout=30) as response:
            row.update(HTTP_status=response.status,effective_url=response.geturl())
            assert urlsplit(response.geturl()).scheme=='https'
            base.new(OUT/(key+'_headers.json'),dict(status=response.status,headers=dict(response.headers)))
            chunks=[];total=0
            while True:
                block=response.read(65536)
                if not block:break
                total+=len(block);assert total<=10_000_000 and time.perf_counter()-tick<=35
                chunks.append(block)
            body=b''.join(chunks)
        dest=OUT/(key+'.pdf')
        with dest.open('xb') as f:f.write(body)
        assert body.startswith(b'%PDF-'),'Returned body is not PDF; original response preserved'
        row.update(complete=True,file=base.entry(dest))
    except HTTPError as e:
        row.update(HTTP_status=e.code,effective_url=e.geturl())
        base.new(OUT/(key+'_HTTP_error_headers.json'),dict(status=e.code,headers=dict(e.headers)))
        body=e.read(3_000_001);assert len(body)<=3_000_000
        p=OUT/(key+'_HTTP_error_body.bin')
        with p.open('xb') as f:f.write(body)
        row['error_response']=base.entry(p);row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    except Exception as e:row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    row['download_complete']=row['complete'];row['elapsed_seconds']=time.perf_counter()-tick;return row
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();assert shutil.disk_usage(ROOT).free>8_050_000_000
    index=HERE/'index_attempt03/receipt.json';q=read(index);assert q['complete'] and not q['errors']
    chapter=next(e for r in q['records'] for e in r.get('entries',[]) if e.get('DOI')=='10.1007/978-3-031-17247-2_6')
    assert chapter['title']==['Segmentation-Aware MRI Reconstruction'] and chapter['author']
    urls=[b['URL'] for b in chapter['link']];assert len(urls)==1 and urls[0].startswith('https://link.springer.com/content/pdf/')
    sadfn=next(e for r in q['records'] for e in r.get('entries',[]) if e.get('id','').endswith('/1804.01210v1'))
    assert sadfn['title']=='A Segmentation-aware Deep Fusion Network for Compressed Sensing MRI'
    arxivurls=[b['href'] for b in sadfn['links'] if b.get('type')=='application/pdf'];assert len(arxivurls)==1
    OUT.mkdir(exist_ok=False);tick=time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(fetch,[('acar_segmentation_aware',chapter,urls[0]),('sadfn',sadfn,arxivurls[0])]))
    sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
    import pypdfium2 as pdfium
    for row in rows:
        if not row['complete']:continue
        try:
            doc=pdfium.PdfDocument(str(ROOT/row['file']['path']));row['physical_pages']=len(doc);row['page_texts']=[]
            for n in range(len(doc)):
                resource_guard();page=doc[n];tp=page.get_textpage();s=tp.get_text_range();p=OUT/f"{row['key']}_page{n+1:03d}.txt"
                with p.open('x',encoding='utf-8') as f:f.write(s)
                row['page_texts'].append(dict(physical_page=n+1,text_read=False,**base.entry(p)));tp.close();page.close()
            doc.close()
        except Exception as e:row['complete']=False;row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
        errors=[e for r in rows for e in r['errors']],records=rows,source_bindings=[base.entry(p) for p in
        (Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_SELECTION.md',index,HERE/'query_seranet_stdlib_v3.py')],
        public_GET_only=True,TLS_verification_disabled=False,automatic_retries=False,authentication_used=False,
        new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0,
        resource_snapshot=resource_guard(),elapsed_seconds=time.perf_counter()-tick)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=result['complete'],records=[{k:r.get(k) for k in ['key','complete','download_complete','HTTP_status','physical_pages','file','errors']} for r in rows]),ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
