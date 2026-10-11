"""Bounded public primary metadata/fulltext acquisition; never marks downloading as reading."""
import sys,json,time,ssl,traceback,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlencode,urlsplit
from urllib.request import build_opener,ProxyHandler,HTTPSHandler,HTTPRedirectHandler,Request
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'adaptation_sources_attempt01'
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
class Redirect(HTTPRedirectHandler):
    max_redirections=3
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        assert urlsplit(newurl).scheme=='https';return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(key,url,suffix):
    tick=time.perf_counter();r=dict(key=key,requested_url=url,complete=False,errors=[],actual_reading_completed=False)
    try:
        resource_guard();ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
        op=build_opener(ProxyHandler({}),HTTPSHandler(context=ctx),Redirect())
        with op.open(Request(url,headers={'User-Agent':'MRI-innovation-primary-reading/1.0'}),timeout=30) as h:
            r.update(HTTP_status=h.status,effective_url=h.geturl());assert urlsplit(h.geturl()).scheme=='https'
            dump(OUT/(key+'_headers.json'),dict(status=h.status,headers=dict(h.headers)))
            blocks=[];size=0
            while True:
                b=h.read(65536)
                if not b:break
                blocks.append(b);size+=len(b);assert size<=2_000_000 and time.perf_counter()-tick<35
            content=b''.join(blocks)
        p=OUT/(key+suffix)
        with p.open('xb') as f:f.write(content)
        r.update(complete=True,file=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=len(content))
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
    r['elapsed_seconds']=time.perf_counter()-tick;return r
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();OUT.mkdir(exist_ok=False);tick=time.perf_counter()
    queries=[('genesis','TITLE:"Models Genesis"'),('stacked','TITLE:"Deep stacked transformation for generalizable medical image segmentation"'),('stu','TITLE:"STU-Net"')]
    jobs=[(k,'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode({'query':q,'format':'json','pageSize':3,'resultType':'core'}),'.json') for k,q in queries]
    with ThreadPoolExecutor(max_workers=3) as p:records=list(p.map(lambda a:fetch(*a),jobs))
    for r in records:
        if r['complete']:
            q=json.loads((ROOT/r['file']).read_text(encoding='utf-8'));r['hit_count']=q.get('hitCount')
            r['entries']=[{k:x.get(k) for k in ['id','source','title','authorString','doi','pmcid','isOpenAccess','pubYear','firstPublicationDate','abstractText']} for x in q.get('resultList',{}).get('result',[])]
    dump(OUT/'index_receipt.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in records),
        errors=[e for r in records for e in r['errors']],records=records,actual_primary_papers_read=0,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,public_GET_only=True,TLS_verification_disabled=False,
        resource_snapshot=resource_guard(),elapsed_seconds=time.perf_counter()-tick,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [Path(__file__),HERE/'STRONGER_ADAPTATION_READING_PROTOCOL.md']]))
    print(json.dumps(records,ensure_ascii=False),flush=True)
    return int(not all(r['complete'] for r in records))
if __name__=='__main__':raise SystemExit(main())
