"""Bounded public primary-source retrieval; never execute retrieved content."""
import concurrent.futures, hashlib, json, sys, time, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'literature/source_cache/action_interaction_primary_2026-10-07'
REQUESTS = [
    ('learning_compressive_mri', 'https://arxiv.org/pdf/1710.09336', 32_000_000, True),
    ('adaptive_submodularity', 'https://arxiv.org/pdf/1003.3967', 32_000_000, True),
    ('scalable_sampling_index', 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode({'query':'learning sampling patterns MRI scalable','format':'json','resultType':'core','pageSize':5}), 2_000_000, False),
]
def sha(b): return hashlib.sha256(b).hexdigest()
def retrieve(item):
    name, url, limit, pdf = item; tick=time.perf_counter()
    row=dict(name=name,requested_url=url,byte_limit=limit,reading_performed=False)
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        req=urllib.request.Request(url,headers={'User-Agent':'MRI-local-research/1.0'})
        with opener.open(req,timeout=30) as response:
            b=response.read(limit+1); row.update(status=response.status,final_url=response.geturl(),content_type=response.headers.get('Content-Type'))
        if len(b)>limit: raise RuntimeError('response exceeds fixed byte limit')
        if pdf and not b.startswith(b'%PDF'): raise RuntimeError('not a PDF response')
        p=OUT/(name+('.pdf' if pdf else '.json')); p.write_bytes(b)
        row.update(file=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=sha(b),retrieval_success=True)
        if pdf:
            import fitz
            with fitz.open(p) as doc:
                pages=[doc[i].get_text() for i in range(len(doc))]
                meta=doc.metadata
            text='\n\n'.join(f'=== PHYSICAL PAGE {i+1} ===\n{page}' for i,page in enumerate(pages))
            t=OUT/(name+'.txt'); t.write_text(text,encoding='utf-8')
            row.update(physical_pages=len(pages),metadata=meta,text_file=t.relative_to(ROOT).as_posix(),text_sha256=sha(t.read_bytes()))
        else:
            data=json.loads(b); row['hitCount']=data.get('hitCount'); row['records']=[{k:r.get(k) for k in ('id','title','doi','authorString','firstPublicationDate','pmcid','abstractText')} for r in data.get('resultList',{}).get('result',[])]
    except Exception as e: row.update(retrieval_success=False,error=f'{type(e).__name__}: {e}')
    row['seconds']=time.perf_counter()-tick
    return row
def main():
    sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(parents=True,exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: rows=list(pool.map(retrieve,REQUESTS))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(Path(__file__).read_bytes()),records=rows,complete=True,reading_performed=False)
    (OUT/'acquisition_attempt01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)
    return int(not all(r['retrieval_success'] for r in rows))
if __name__=='__main__': raise SystemExit(main())
