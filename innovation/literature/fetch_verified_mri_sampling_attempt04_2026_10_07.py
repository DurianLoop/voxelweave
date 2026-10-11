import concurrent.futures, hashlib, json, re, shutil, subprocess, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'literature/source_cache/action_interaction_primary_2026-10-07'
def fetch(job):
    key,url,pdf=job; r=dict(key=key,url=url,reading_performed=False)
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(urllib.request.Request(url,headers={'User-Agent':'MRI-local-research/1.0'}),timeout=30) as res:
            b=res.read((32_000_000 if pdf else 2_000_000)+1);r.update(status=res.status,final_url=res.geturl())
        assert len(b)<=(32_000_000 if pdf else 2_000_000)
        p=OUT/(key+('.pdf' if pdf else '.json'));assert not p.exists()
        if pdf:assert b.startswith(b'%PDF')
        p.write_bytes(b);r.update(file=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
        if pdf:
            info=subprocess.run([shutil.which('pdfinfo'),str(p)],capture_output=True,timeout=30);assert info.returncode==0
            n=int(re.search(rb'^Pages:\s+(\d+)',info.stdout,re.M)[1]);r['physical_pages']=n
            rows=[]
            for i in range(1,n+1):
                t=OUT/(key+f'_page{i:02d}.txt');assert not t.exists()
                x=subprocess.run([shutil.which('pdftotext'),'-f',str(i),'-l',str(i),'-layout','-enc','UTF-8',str(p),str(t)],capture_output=True,timeout=30);assert x.returncode==0
                rows.append(dict(page=i,file=t.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(t.read_bytes()).hexdigest()))
            r['texts']=rows
        else:
            data=json.loads(b);r.update(title=data.get('title'),doi=data.get('doi'),locations=[{k:l.get(k) for k in ('landing_page_url','pdf_url','version')} for l in data.get('locations',[])])
        r['success']=True
    except Exception as e:r.update(success=False,error=f'{type(e).__name__}: {e}')
    return r
def main():
    jobs=[('compressive_mri_verified','https://arxiv.org/pdf/1805.01266',True),('scalable_sampling_doi_verified','https://api.openalex.org/works/https://doi.org/10.1109/ICASSP40776.2020.9053345',False)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(fetch,jobs))
    p=OUT/'verified_acquisition_attempt04.json';assert not p.exists();p.write_text(json.dumps(dict(records=rows,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v for k,v in r.items() if k!='texts'} for r in rows],ensure_ascii=False))
    return int(not all(r['success'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
