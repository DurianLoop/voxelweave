"""Public sources for two feature-cost papers; identity and reading checked later."""
import hashlib,json,re,shutil,subprocess,sys,time,urllib.request,urllib.parse
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/shared_cost_primary_2026-10-08'
LIMIT=32_000_000
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=False);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
    for key,url,landing in [('greedy','https://arxiv.org/pdf/1206.6451',False),('cstc','https://proceedings.mlr.press/v28/xu13.html',True)]:
        start=time.perf_counter();row=dict(key=key,complete=False,errors=[],responses=[],new_paper_read=False)
        try:
            def get(address):
                with opener.open(urllib.request.Request(address,headers={'User-Agent':'MRI-public-literature/1.0'}),timeout=25) as response:
                    data=response.read(LIMIT+1);assert len(data)<=LIMIT
                    row['responses'].append(dict(requested_url=address,final_url=response.geturl(),http_status=response.status,content_type=response.headers.get('Content-Type'),bytes=len(data)))
                    return data
            data=get(url)
            if landing:
                path=OUT/(key+'_landing.html');path.write_bytes(data)
                links=[urllib.parse.urljoin(url,x) for x in re.findall(r'href=[\"\']([^\"\']+\.pdf)[\"\']',data.decode('utf-8'))];assert links
                data=get(links[0])
            assert data.startswith(b'%PDF');path=OUT/(key+'.pdf');path.write_bytes(data)
            info=subprocess.run([shutil.which('pdfinfo'),str(path)],capture_output=True,timeout=30);assert info.returncode==0
            (OUT/(key+'_pdfinfo.txt')).write_bytes(info.stdout+info.stderr);pages=int(re.search(rb'^Pages:\s+(\d+)',info.stdout,re.M)[1]);texts=[]
            for page in range(1,pages+1):
                dest=OUT/f'{key}_page{page:02d}.txt';proc=subprocess.run([shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(path),str(dest)],capture_output=True,timeout=30);assert proc.returncode==0
                texts.append(dict(physical_page=page,path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),characters=len(dest.read_text(encoding='utf-8')),extraction_exit=proc.returncode))
            row.update(complete=True,PDF=dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size),physical_pages=pages,page_texts=texts)
        except Exception as e:row['errors'].append(type(e).__name__+': '+str(e))
        row['elapsed_seconds']=time.perf_counter()-start;rows.append(row)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),public_GET_only=True,new_primary_papers_read=0,records=rows)
    (OUT/'acquisition_attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v.get(k) for k in ('key','complete','physical_pages','errors')} for v in rows]),flush=True)
    return int(not all(v['complete'] for v in rows))
if __name__=='__main__':raise SystemExit(main())
