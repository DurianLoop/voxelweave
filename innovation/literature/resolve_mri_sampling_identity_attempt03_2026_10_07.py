"""Correct title identities using public index; no guessed PDF retry."""
import concurrent.futures, hashlib, json, urllib.request, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/source_cache/action_interaction_primary_2026-10-07'
TITLES=[('compressive','Learning-based compressive MRI'),('scalable','Scalable Learning-Based Sampling Optimization for Compressive Dynamic MRI')]
def get(job):
    key,title=job;url='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':title,'per-page':3})
    r=dict(key=key,title=title,url=url)
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'MRI-local-research/1.0'})
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=30) as res:
            b=res.read(2_000_001);r['status']=res.status
        assert len(b)<=2_000_000
        p=OUT/(key+'_openalex_attempt03.json');assert not p.exists();p.write_bytes(b)
        data=json.loads(b);r.update(success=True,file=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(b).hexdigest(),results=[{k:v.get(k) for k in ('id','title','doi','publication_date','open_access','locations')} for v in data.get('results',[])])
    except Exception as e:r.update(success=False,error=f'{type(e).__name__}: {e}')
    return r
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(get,TITLES))
    p=OUT/'identity_attempt03.json';assert not p.exists();p.write_text(json.dumps(dict(results=results,wrong_initial_id='1710.09336: Properly Ergodic Structures; excluded from MRI reading',new_papers_read=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False))
    return int(not all(r['success'] for r in results))
if __name__=='__main__':raise SystemExit(main())
