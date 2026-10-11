"""Continue from the already obtained PDFs using existing Poppler, without changing the environment."""
import concurrent.futures, hashlib, json, re, shutil, subprocess, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/action_interaction_primary_2026-10-07'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def extract(key):
    p=OUT/(key+'.pdf'); rows=[]
    assert p.read_bytes().startswith(b'%PDF')
    info=subprocess.run([shutil.which('pdfinfo'),str(p)],capture_output=True,timeout=30)
    assert info.returncode==0
    infopath=OUT/(key+'_pdfinfo.txt');assert not infopath.exists();infopath.write_bytes(info.stdout+info.stderr)
    n=int(re.search(rb'^Pages:\s+(\d+)',info.stdout,re.M)[1])
    for i in range(1,n+1):
        text=OUT/(key+f'_page{i:02d}.txt');assert not text.exists()
        proc=subprocess.run([shutil.which('pdftotext'),'-f',str(i),'-l',str(i),'-layout','-enc','UTF-8',str(p),str(text)],capture_output=True,timeout=30)
        assert proc.returncode==0
        rows.append(dict(page=i,file=text.relative_to(ROOT).as_posix(),sha256=sha(text),characters=len(text.read_text(encoding='utf-8'))))
    return dict(key=key,pdf_sha256=sha(p),physical_pages=n,texts=rows,reading_performed=False,extraction_success=True)
def lookup():
    url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.title':'Scalable learning of sampling patterns for MRI','rows':3})
    r=dict(url=url,reading_performed=False)
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'MRI-local-research/1.0'})
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=30) as response:
            b=response.read(2_000_001);r['status']=response.status
        assert len(b)<=2_000_000
        p=OUT/'scalable_sampling_crossref.json';assert not p.exists();p.write_bytes(b)
        data=json.loads(b)
        r.update(success=True,file=p.relative_to(ROOT).as_posix(),sha256=sha(p),records=[{k:v.get(k) for k in ('title','DOI','author','link','published','URL')} for v in data['message']['items']])
    except Exception as e:r.update(success=False,error=f'{type(e).__name__}: {e}')
    return r
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        jobs=[pool.submit(extract,key) for key in ('learning_compressive_mri','adaptive_submodularity')];q=pool.submit(lookup)
        results=[x.result() for x in jobs];index=q.result()
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),records=results,index=index,complete=True,environment_unchanged=True,prior_failed_attempt_retained=True,reading_performed=False)
    p=OUT/'extraction_attempt02.json';assert not p.exists();p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(records=[{k:r[k] for k in ('key','physical_pages','extraction_success')} for r in results],index=index),ensure_ascii=False))
    return int(not index['success'])
if __name__=='__main__':raise SystemExit(main())
