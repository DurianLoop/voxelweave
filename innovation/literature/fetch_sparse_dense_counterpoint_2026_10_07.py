"""Acquire title-verified Jaritz primary; keep byte diagnostics for Windows."""
import hashlib,json,re,shutil,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/sparse_dense_counterpoint_2026-10-07'
def main():
    url='https://arxiv.org/pdf/1808.00769';d=json.loads((OUT/'identity_attempt01.json').read_text(encoding='utf-8'))
    assert d['success'] and any(any(l['pdf_url']==url for l in v['locations']) for v in d['verified_candidates'])
    r=dict(requested_url=url,reading_performed=False,success=False)
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(urllib.request.Request(url,headers={'User-Agent':'MRI-local-research/1.0'}),timeout=30) as response:
            b=response.read(32_000_001);r.update(status=response.status,final_url=response.url)
        assert b.startswith(b'%PDF-') and len(b)<=32_000_000
        pdf=OUT/'jaritz_sparse_dense.pdf';assert not pdf.exists();pdf.write_bytes(b)
        proc=subprocess.run([shutil.which('pdfinfo'),str(pdf)],capture_output=True,timeout=30)
        (OUT/'pdfinfo.raw').write_bytes(proc.stdout+proc.stderr);assert proc.returncode==0
        n=int(re.search(rb'^Pages:\s+(\d+)',proc.stdout,re.M)[1]);texts=[]
        for page in range(1,n+1):
            p=OUT/f'page{page:02d}.txt';assert not p.exists()
            q=subprocess.run([shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(pdf),str(p)],capture_output=True,timeout=30)
            assert q.returncode==0
            texts.append(dict(page=page,file=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        r.update(success=True,pdf_bytes=len(b),pdf_sha256=hashlib.sha256(b).hexdigest(),physical_pages=n,texts=texts)
    except Exception as e:r['error']=f'{type(e).__name__}: {e}'
    with (OUT/'acquisition_attempt01.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in r.items() if k!='texts'}));return int(not r['success'])
if __name__=='__main__':raise SystemExit(main())
