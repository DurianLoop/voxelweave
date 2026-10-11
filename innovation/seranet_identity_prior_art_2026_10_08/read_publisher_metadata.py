"""Read only the official redirect's public chapter HTML with anonymous in-memory cookies."""
import sys,json,time,ssl,traceback,http.cookiejar,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import build_opener,ProxyHandler,HTTPSHandler,HTTPCookieProcessor,Request
from urllib.error import HTTPError
import query_seranet_stdlib_v3 as prior
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'publisher_metadata_attempt01'
base=prior.base
def main():
    sys.stdout.reconfigure(encoding='utf-8');prior.resource_guard();OUT.mkdir(exist_ok=False);tick=time.perf_counter()
    inp=HERE/'primary_attempt01/acar_segmentation_aware_HTTP_error_headers.json'
    q=json.loads(inp.read_text(encoding='utf-8'));assert q['status']==303
    url=urllib.parse.urljoin('https://link.springer.com',q['headers']['location'])
    assert url=='https://link.springer.com/chapter/10.1007/978-3-031-17247-2_6'
    row=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],requested_url=url,
        source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PUBLISHER_METADATA_PLAN.md',inp)],
        public_GET_only=True,TLS_verification_disabled=False,anonymous_cookie_memory_only=True,
        authentication_used=False,automatic_retries=False,new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0)
    try:
        context=ssl.create_default_context();assert context.verify_mode==ssl.CERT_REQUIRED and context.check_hostname
        opener=build_opener(ProxyHandler({}),HTTPSHandler(context=context),prior.LimitedRedirect(),HTTPCookieProcessor(http.cookiejar.CookieJar()))
        req=Request(url,headers={'User-Agent':'MRI-innovation-literature-audit/1.0'},method='GET')
        with opener.open(req,timeout=30) as response:
            row.update(HTTP_status=response.status,effective_url=response.geturl())
            base.new(OUT/'headers.json',dict(status=response.status,headers=dict(response.headers)))
            chunks=[];total=0
            while True:
                block=response.read(65536)
                if not block:break
                total+=len(block);assert total<=3_000_000 and time.perf_counter()-tick<=35
                chunks.append(block)
            body=b''.join(chunks)
        p=OUT/'chapter.html'
        with p.open('xb') as f:f.write(body)
        row.update(complete=True,file=base.entry(p),downloaded_bytes=len(body),full_text_read=False)
    except HTTPError as e:
        row.update(HTTP_status=e.code,effective_url=e.geturl())
        base.new(OUT/'HTTP_error_headers.json',dict(status=e.code,headers=dict(e.headers)))
        body=e.read(3_000_001);assert len(body)<=3_000_000;p=OUT/'HTTP_error_body.bin'
        with p.open('xb') as f:f.write(body)
        row.update(error_response=base.entry(p));row['errors'].append(type(e).__name__+': '+str(e))
    except Exception as e:row['errors'].append(type(e).__name__+': '+str(e));row['traceback']=traceback.format_exc()
    row['elapsed_seconds']=time.perf_counter()-tick
    base.new(OUT/'receipt.json',row)
    print(json.dumps({k:row.get(k) for k in ['complete','HTTP_status','effective_url','downloaded_bytes','errors']},ensure_ascii=False),flush=True)
    return int(not row['complete'])
if __name__=='__main__':raise SystemExit(main())
