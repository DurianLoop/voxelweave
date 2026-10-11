"""Official title-first LTT acquisition; extraction never claims reading."""
import hashlib,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
from datetime import datetime,timezone
from html import unescape
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/learn_then_test_primary_2026-10-07'
TITLE='Learn then Test: Calibrating Predictive Algorithms to Achieve Risk Control'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(url,limit):
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(urllib.request.Request(url,headers={'User-Agent':'MRI-local-research/1.0'}),timeout=30) as response:
        b=response.read(limit+1);assert len(b)<=limit
        return b,dict(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],title=TITLE,
        reading_performed=False,visual_review_performed=False,script_sha256=sha(__file__))
    try:
        b,meta=get('https://arxiv.org/abs/2110.01052',2_000_000);p=OUT/'identity.html';p.write_bytes(b)
        r.update(identity_file=p.relative_to(ROOT).as_posix(),identity_sha256=sha(p),identity_response=meta)
        text=b.decode('utf-8');titles=[unescape(x) for x in re.findall(r'<meta\s+name=["\']citation_title["\']\s+content=["\'](.*?)["\']',text,re.I)]
        assert TITLE in titles,titles
        authors=[unescape(x) for x in re.findall(r'<meta\s+name=["\']citation_author["\']\s+content=["\'](.*?)["\']',text,re.I)]
        urls=re.findall(r'<meta\s+name=["\']citation_pdf_url["\']\s+content=["\'](.*?)["\']',text,re.I)
        assert len(urls)==1 and urls[0].startswith('https://arxiv.org/pdf/2110.01052')
        r.update(official_title_verified=True,official_authors=authors,requested_pdf_url=urls[0])
        b,meta=get(urls[0],32_000_000);assert b.startswith(b'%PDF-');pdf=OUT/'learn_then_test.pdf';pdf.write_bytes(b)
        r.update(pdf_file=pdf.relative_to(ROOT).as_posix(),pdf_sha256=sha(pdf),pdf_bytes=len(b),pdf_response=meta)
        info=subprocess.run([shutil.which('pdfinfo'),str(pdf)],capture_output=True,timeout=30)
        (OUT/'pdfinfo.raw').write_bytes(info.stdout+info.stderr);assert info.returncode==0
        n=int(re.search(rb'^Pages:\s+(\d+)',info.stdout,re.M)[1]);r['physical_pages']=n;assert n<=60
        rows=[]
        for page in range(1,n+1):
            p=OUT/f'page{page:02d}.txt';q=subprocess.run([shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(pdf),str(p)],capture_output=True,timeout=30)
            assert q.returncode==0
            rows.append(dict(page=page,file=p.relative_to(ROOT).as_posix(),sha256=sha(p),characters=len(p.read_text(encoding='utf-8'))))
        r.update(complete=True,text_pages=rows)
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}')
    with (OUT/'download_extraction_attempt01.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in r.items() if k!='text_pages'},ensure_ascii=False));return 0 if r['complete'] else 1
if __name__=='__main__':raise SystemExit(main())

