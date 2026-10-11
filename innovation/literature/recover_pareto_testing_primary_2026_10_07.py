"""Recover identity from venue index rather than reusing a failed arXiv guess."""
import hashlib,json,re,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from fetch_pareto_testing_primary_2026_10_07 import get,metas,TITLE
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/pareto_testing_primary_recovery_2026-10-07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        expected_title=TITLE,reading_performed=False,visual_review_performed=False)
    try:
        data,meta=get('https://proceedings.mlr.press/v206/',2_000_000)
        index=OUT/'volume_index.html';index.write_bytes(data)
        r.update(index_file=index.relative_to(ROOT).as_posix(),index_sha256=sha(index),index_response=meta)
        text=data.decode('utf-8');at=text.casefold().find(TITLE.casefold());assert at>=0,'Title absent from venue index'
        begin=text.rfind('<div class="paper"',0,at)
        if begin<0:begin=max(0,at-1500)
        end=text.find('<div class="paper"',at)
        if end<0:end=at+3000
        snippet=text[begin:end];(OUT/'title_index_block.html').write_text(snippet,encoding='utf-8')
        urls=re.findall(r'href=[\"\x27]([^\"\x27]+\.html)[\"\x27]',snippet)
        candidates=[]
        for url in urls:
            if url.startswith('/v206/'):url='https://proceedings.mlr.press'+url
            if url.startswith('https://proceedings.mlr.press/v206/') and url not in candidates:candidates.append(url)
        assert 1<=len(candidates)<=3,candidates
        r['identity_attempts']=[];pdfurl=None
        for i,url in enumerate(candidates):
            data,meta=get(url,2_000_000);p=OUT/f'identity{i+1:02d}.html';p.write_bytes(data)
            html=data.decode('utf-8');titles=metas(html,'citation_title')
            r['identity_attempts'].append(dict(url=url,titles=titles,response=meta,file=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
            if any(' '.join(t.split()).casefold()==TITLE.casefold() for t in titles):
                pdfs=metas(html,'citation_pdf_url');assert len(pdfs)==1 and pdfs[0].startswith('https://proceedings.mlr.press/')
                pdfurl=pdfs[0];r.update(official_title_verified=True,official_authors=metas(html,'citation_author'),
                    official_date=metas(html,'citation_publication_date'),requested_pdf_url=pdfurl);break
        assert pdfurl
        data,meta=get(pdfurl,32_000_000);assert data.startswith(b'%PDF-')
        pdf=OUT/'pareto_testing.pdf';pdf.write_bytes(data)
        r.update(pdf_file=pdf.relative_to(ROOT).as_posix(),pdf_sha256=sha(pdf),pdf_bytes=len(data),pdf_response=meta)
        q=subprocess.run([shutil.which('pdfinfo'),str(pdf)],capture_output=True,timeout=30)
        (OUT/'pdfinfo.raw').write_bytes(q.stdout+q.stderr);assert q.returncode==0
        n=int(re.search(rb'^Pages:\s+(\d+)',q.stdout,re.M)[1]);r['physical_pages']=n;assert n<=60
        rows=[]
        for page in range(1,n+1):
            p=OUT/f'page{page:02d}.txt'
            q=subprocess.run([shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(pdf),str(p)],capture_output=True,timeout=30)
            assert q.returncode==0;rows.append(dict(page=page,file=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
        r.update(complete=True,text_pages=rows)
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}')
    with (OUT/'download_extraction_attempt02.json').open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps({k:v for k,v in r.items() if k!='text_pages'},ensure_ascii=False));return 0 if r['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
