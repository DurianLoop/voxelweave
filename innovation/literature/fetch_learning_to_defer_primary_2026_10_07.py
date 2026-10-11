"""Acquire two preselected public primary-method PDFs; reading is registered separately."""
import concurrent.futures,hashlib,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/learning_to_defer_primary_2026-10-07'
PAPERS=[('mozannar_sontag_2020','2006.01862','https://arxiv.org/pdf/2006.01862'),
        ('madras_2018','1711.06646','https://arxiv.org/pdf/1711.06646')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fetch(item):
    key,identifier,url=item;directory=OUT/key;directory.mkdir(exist_ok=False)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),key=key,identifier=identifier,url=url,
           script_sha256=sha(__file__),fulltext_acquired=False,actual_reading_completed=False)
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI research reading'}),timeout=25) as response:
            raw=response.read(20_000_001);r.update(http_status=response.status,final_url=response.geturl(),content_type=response.headers.get('Content-Type'))
        path=directory/'original.pdf';path.write_bytes(raw);r.update(response_file=path.name,response_sha256=sha(path))
        assert len(raw)<=20_000_000 and raw.startswith(b'%PDF'),'Public response not an in-budget PDF'
        p=subprocess.run([shutil.which('pdfinfo'),str(path)],capture_output=True,timeout=20);assert p.returncode==0
        (directory/'pdfinfo.txt').write_bytes(p.stdout);m=re.search(rb'^Pages:\s+(\d+)',p.stdout,re.M);assert m
        count=int(m.group(1));assert count<=40;pages=[]
        for page in range(1,count+1):
            text=directory/f'physical_page_{page:02d}.txt'
            c=[shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(path),str(text)]
            p=subprocess.run(c,capture_output=True,timeout=20);assert p.returncode==0
            pages.append(dict(physical_page=page,text_file=text.name,sha256=sha(text),text=text.read_text(encoding='utf-8')))
        index=directory/'physical_pages.json';index.write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        r.update(fulltext_acquired=True,physical_pages=count,pdf_sha256=sha(path),index_file=index.name,index_sha256=sha(index))
        print(json.dumps(dict(key=key,first_page_text=pages[0]['text'][:1800]),ensure_ascii=False),flush=True)
    except Exception as e:r['error']=type(e).__name__+': '+str(e)
    with (directory/'acquisition_attempt01.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    return r
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(fetch,PAPERS))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,script_sha256=sha(__file__),papers=results,
           actual_new_fulltexts_read=0,actual_training_updates=0,actual_gpu_updates=0)
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps([{k:p.get(k) for k in ['key','fulltext_acquired','physical_pages','error']} for p in results]),flush=True)
    return int(not all(p['fulltext_acquired'] for p in results))
if __name__=='__main__':raise SystemExit(main())
