"""Title-first public index, preventing unverified arXiv guesses."""
import concurrent.futures,hashlib,json,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/source_cache/direct_observed_primary_2026-10-07'
QUERIES=[('sparsity_invariant','Sparsity Invariant CNNs'),('confidence_propagation','Confidence Propagation through CNNs for Guided Sparse Depth Regression')]
def get(item):
    key,title=item;url='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':title,'per-page':3});r=dict(key=key,query=title,url=url,reading_performed=False)
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(urllib.request.Request(url,headers={'User-Agent':'MRI-local-research/1.0'}),timeout=30) as response:
            b=response.read(2_000_001);r['status']=response.status
        assert len(b)<=2_000_000
        p=OUT/(key+'_openalex.json');p.write_bytes(b);data=json.loads(b)
        r.update(success=True,file=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(b).hexdigest(),results=[dict(title=v.get('title'),doi=v.get('doi'),id=v.get('id'),locations=[{k:l.get(k) for k in ('pdf_url','landing_page_url','version')} for l in v.get('locations',[])]) for v in data.get('results',[])])
    except Exception as e:r.update(success=False,error=f'{type(e).__name__}: {e}')
    return r
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(get,QUERIES))
    p=OUT/'identity_attempt01.json';p.write_text(json.dumps(dict(records=rows,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(rows,ensure_ascii=False));return int(not all(r['success'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
