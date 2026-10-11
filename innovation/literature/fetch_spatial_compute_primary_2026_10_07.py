"""Two official public sources; acquisition does not assert paper reading."""
import concurrent.futures, hashlib, json, re, shutil, subprocess, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/spatial_compute_primary_2026-10-07'
LIMIT=32_000_000
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def acquire(job):
    key,url=job; r=dict(key=key,requested_url=url,complete=False,errors=[],new_paper_read=False); start=time.perf_counter()
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        def get(u):
            with opener.open(urllib.request.Request(u,headers={'User-Agent':'MRI-public-literature/1.0'}),timeout=25) as q:
                b=q.read(LIMIT+1); assert len(b)<=LIMIT
                return b,dict(requested_url=u,final_url=q.geturl(),http_status=q.status,content_type=q.headers.get('Content-Type'),bytes=len(b))
        raw,landing=get(url); r['landing_response']=landing
        page=OUT/(key+'_landing.html'); page.write_bytes(raw);r['landing_file']=page.relative_to(ROOT).as_posix();r['landing_sha256']=sha(page)
        links=re.findall(r'href=[\"\']([^\"\']+\.pdf)[\"\']',raw.decode('utf-8',errors='replace'))
        links=[urllib.parse.urljoin(url,u) for u in links if '/papers/' in u or '/content/' in u]
        assert links,'No official PDF in landing page'
        raw,meta=get(links[0]);assert raw.startswith(b'%PDF');pdf=OUT/(key+'.pdf');pdf.write_bytes(raw)
        r.update(pdf_response=meta,pdf_file=pdf.relative_to(ROOT).as_posix(),pdf_sha256=sha(pdf),pdf_bytes=len(raw))
        info=subprocess.run([shutil.which('pdfinfo'),str(pdf)],capture_output=True,timeout=30)
        (OUT/(key+'_pdfinfo.txt')).write_bytes(info.stdout+info.stderr);r['pdfinfo_exit']=info.returncode;assert info.returncode==0
        pages=int(re.search(rb'^Pages:\s+(\d+)',info.stdout,re.M)[1]);r['physical_pages']=pages;texts=[]
        for p in range(1,pages+1):
            dest=OUT/f'{key}_page{p:02d}.txt'
            x=subprocess.run([shutil.which('pdftotext'),'-f',str(p),'-l',str(p),'-layout','-enc','UTF-8',str(pdf),str(dest)],capture_output=True,timeout=30)
            assert x.returncode==0
            texts.append(dict(physical_page=p,path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),characters=len(dest.read_text(encoding='utf-8')),extraction_exit=x.returncode))
        r.update(page_texts=texts,complete=True)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
    r['elapsed_seconds']=time.perf_counter()-start;return r
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=False)
    jobs=[('sact','https://openaccess.thecvf.com/content_cvpr_2017/html/Figurnov_Spatially_Adaptive_Computation_CVPR_2017_paper.html'),
          ('dynconv','https://openaccess.thecvf.com/content_CVPR_2020/html/Verelst_Dynamic_Convolutions_Exploiting_Spatial_Sparsity_for_Faster_Inference_CVPR_2020_paper.html')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(acquire,jobs))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),protocol_sha256=sha(ROOT/'literature/2026-10-07_spatial_compute_primary_protocol.md'),public_GET_only=True,system_proxy_unchanged=True,new_primary_papers_read=0,records=rows)
    (OUT/'acquisition_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v.get(k) for k in ('key','complete','physical_pages','pdf_bytes','errors')} for v in rows]),flush=True)
    return int(not all(v['complete'] for v in rows))
if __name__=='__main__':raise SystemExit(main())
