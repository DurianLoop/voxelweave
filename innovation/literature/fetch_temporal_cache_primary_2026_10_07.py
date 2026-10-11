"""Two official CVF conference PDFs; fetch is not a reading claim."""
import concurrent.futures,hashlib,json,re,shutil,subprocess,sys,time,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/temporal_cache_primary_2026-10-07'
LIMIT=32_000_000
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fetch(job):
    key,url=job;started=time.perf_counter();r=dict(key=key,complete=False,errors=[],new_paper_read=False)
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        def get(u):
            with opener.open(urllib.request.Request(u,headers={'User-Agent':'MRI-public-literature/1.0'}),timeout=25) as response:
                data=response.read(LIMIT+1);assert len(data)<=LIMIT
                return data,dict(requested_url=u,final_url=response.geturl(),http_status=response.status,content_type=response.headers.get('Content-Type'),bytes=len(data))
        data,meta=get(url);landing=OUT/(key+'_landing.html');landing.write_bytes(data)
        r.update(landing_response=meta,landing_file=landing.relative_to(ROOT).as_posix(),landing_sha256=sha(landing))
        links=[urllib.parse.urljoin(url,x) for x in re.findall(r'href=[\"\']([^\"\']+\.pdf)[\"\']',data.decode('utf-8')) if '/papers/' in x]
        assert links
        data,meta=get(links[0]);assert data.startswith(b'%PDF')
        path=OUT/(key+'.pdf');path.write_bytes(data)
        r.update(pdf_response=meta,pdf_file=path.relative_to(ROOT).as_posix(),pdf_sha256=sha(path),pdf_bytes=len(data))
        info=subprocess.run([shutil.which('pdfinfo'),str(path)],capture_output=True,timeout=30)
        (OUT/(key+'_pdfinfo.txt')).write_bytes(info.stdout+info.stderr);r['pdfinfo_exit']=info.returncode;assert info.returncode==0
        pages=int(re.search(rb'^Pages:\s+(\d+)',info.stdout,re.M)[1]);r['physical_pages']=pages;texts=[]
        for number in range(1,pages+1):
            dest=OUT/f'{key}_page{number:02d}.txt'
            proc=subprocess.run([shutil.which('pdftotext'),'-f',str(number),'-l',str(number),'-layout','-enc','UTF-8',str(path),str(dest)],capture_output=True,timeout=30)
            assert proc.returncode==0
            texts.append(dict(physical_page=number,path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),extraction_exit=proc.returncode,characters=len(dest.read_text(encoding='utf-8'))))
        r.update(complete=True,page_texts=texts)
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error))
    r['elapsed_seconds']=time.perf_counter()-started;return r
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=False)
    jobs=[('skipconvs','https://openaccess.thecvf.com/content/CVPR2021/html/Habibian_Skip-Convolutions_for_Efficient_Video_Processing_CVPR_2021_paper.html'),
          ('motiondelta','https://openaccess.thecvf.com/content/ICCV2023/html/Parger_MotionDeltaCNN_Sparse_CNN_Inference_of_Frame_Differences_in_Moving_Camera_ICCV_2023_paper.html')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(fetch,jobs))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),protocol_sha256=sha(ROOT/'literature/2026-10-07_temporal_cache_primary_protocol.md'),public_GET_only=True,system_proxy_unchanged=True,new_primary_papers_read=0,records=rows)
    (OUT/'acquisition_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v.get(k) for k in ('key','complete','physical_pages','pdf_bytes','errors')} for v in rows]),flush=True)
    return int(not all(v['complete'] for v in rows))
if __name__=='__main__':raise SystemExit(main())
