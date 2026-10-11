"""Recover HTTP canonical links by verified HTTPS transport; attempt01 stays intact."""
import concurrent.futures, hashlib, json, re, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from html import unescape
from fetch_calibration_selection_primary_2026_10_07 import ROOT, OUT as PRIOR, ITEMS, get, sha

OUT=ROOT/'literature/source_cache/calibration_selection_pmlr_attempt02_2026-10-07'
def recover(item):
    key,title,landing,url=item; r=dict(key=key,expected_title=title,requested_pdf_url=url,
        reading_performed=False,success=False)
    try:
        identity=PRIOR/(key+'_identity.html'); text=identity.read_text(encoding='utf-8')
        titles=[unescape(s) for s in re.findall(r'<meta\s+name=["\']citation_title["\']\s+content=["\'](.*?)["\']',text,re.I)]
        links=re.findall(r'<meta\s+name=["\']citation_pdf_url["\']\s+content=["\'](.*?)["\']',text,re.I)
        assert title in titles and len(links)==1
        a,b=urlsplit(links[0]),urlsplit(url)
        assert a.scheme in ('http','https') and b.scheme=='https' and a.netloc==b.netloc=='proceedings.mlr.press'
        assert (a.path,a.query,a.fragment)==(b.path,b.query,b.fragment)
        r.update(identity_title_verified=True,official_canonical_pdf_url=links[0],https_transport_equivalent=True,
            identity_file=identity.relative_to(ROOT).as_posix(),identity_sha256=sha(identity))
        data,meta=get(url,32_000_000); assert data.startswith(b'%PDF-')
        pdf=OUT/(key+'.pdf');pdf.write_bytes(data)
        r.update(pdf_file=pdf.relative_to(ROOT).as_posix(),pdf_bytes=len(data),pdf_sha256=sha(pdf),pdf_response=meta)
        info=subprocess.run([shutil.which('pdfinfo'),str(pdf)],capture_output=True,timeout=30)
        (OUT/(key+'_pdfinfo.raw')).write_bytes(info.stdout+info.stderr);assert info.returncode==0
        n=int(re.search(rb'^Pages:\s+(\d+)',info.stdout,re.M)[1]);r['physical_pages']=n;assert n<=60
        rows=[]
        for page in range(1,n+1):
            p=OUT/(key+f'_page{page:02d}.txt')
            q=subprocess.run([shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(pdf),str(p)],capture_output=True,timeout=30)
            assert q.returncode==0
            rows.append(dict(page=page,file=p.relative_to(ROOT).as_posix(),sha256=sha(p),characters=len(p.read_text(encoding='utf-8'))))
        r.update(success=True,text_pages=rows)
    except Exception as e:r['error']=f'{type(e).__name__}: {e}'
    return r
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(recover,ITEMS[:2]))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['success'] for r in rows),records=rows,
        script_sha256=sha(__file__),source_bindings=[dict(path='literature/source_cache/calibration_selection_primary_2026-10-07/download_extraction_attempt01.json',sha256=sha(PRIOR/'download_extraction_attempt01.json'))])
    with (OUT/'download_extraction_attempt02.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps([{k:v for k,v in r.items() if k!='text_pages'} for r in rows],ensure_ascii=False))
    return 0 if result['complete'] else 1
if __name__=='__main__':raise SystemExit(main())

