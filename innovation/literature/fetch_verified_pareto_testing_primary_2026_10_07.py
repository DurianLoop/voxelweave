"""Title-verified acquisition from a candidate official venue or arXiv page."""
import hashlib,json,re,shutil,subprocess,sys,urllib.request
from datetime import datetime,timezone
from html import unescape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/pareto_testing_verified_primary_2026-10-07'
TITLE='Efficiently Controlling Multiple Risks with Pareto Testing'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(url,limit):
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(urllib.request.Request(url,headers={'User-Agent':'MRI-local-research/1.0'}),timeout=30) as response:
        data=response.read(limit+1);assert len(data)<=limit
        return data,dict(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
def metas(text,key):
    tags=re.findall(r'<meta\s+[^>]*>',text,re.I);values=[]
    for tag in tags:
        attributes=dict((k.lower(),unescape(v)) for k,quote,v in re.findall(r'(\w+)\s*=\s*([\"\x27])(.*?)\2',tag,re.S))
        if attributes.get('name','').lower()==key.lower():values.append(attributes.get('content',''))
    return values
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        expected_title=TITLE,identity_attempts=[],reading_performed=False,visual_review_performed=False,
        source_bindings=[dict(path='literature/source_cache/pareto_testing_official_search_2026-10-07/search_attempt03.json',sha256='8078cd2be0c2aedc9a8232715be6dc64157f67487a1a106ef464bd18fa3873e2')])
    try:
        url=None
        for i,candidate in enumerate(('https://arxiv.org/abs/2210.07913',)):
            row=dict(url=candidate,title_verified=False);r['identity_attempts'].append(row)
            try:
                data,meta=get(candidate,2_000_000);p=OUT/f'identity{i+1:02d}.html';p.write_bytes(data)
                text=data.decode('utf-8');titles=metas(text,'citation_title')
                row.update(response=meta,file=p.relative_to(ROOT).as_posix(),sha256=sha(p),titles=titles)
                if not any(' '.join(x.split()).casefold()==TITLE.casefold() for x in titles):continue
                pdfs=metas(text,'citation_pdf_url');assert len(pdfs)==1
                assert pdfs[0].startswith(('https://proceedings.mlr.press/','https://arxiv.org/pdf/'))
                row['title_verified']=True;url=pdfs[0]
                r.update(official_authors=metas(text,'citation_author'),official_date=metas(text,'citation_publication_date'),requested_pdf_url=url)
                break
            except Exception as e:row['error']=f'{type(e).__name__}: {e}'
        assert url,'No official identity matched the expected title'
        data,meta=get(url,32_000_000);assert data.startswith(b'%PDF-')
        pdf=OUT/'pareto_testing.pdf';pdf.write_bytes(data)
        r.update(pdf_file=pdf.relative_to(ROOT).as_posix(),pdf_sha256=sha(pdf),pdf_bytes=len(data),pdf_response=meta)
        info=subprocess.run([shutil.which('pdfinfo'),str(pdf)],capture_output=True,timeout=30)
        (OUT/'pdfinfo.raw').write_bytes(info.stdout+info.stderr);assert info.returncode==0
        n=int(re.search(rb'^Pages:\s+(\d+)',info.stdout,re.M)[1]);r['physical_pages']=n;assert n<=60
        rows=[]
        for page in range(1,n+1):
            p=OUT/f'page{page:02d}.txt'
            q=subprocess.run([shutil.which('pdftotext'),'-f',str(page),'-l',str(page),'-layout','-enc','UTF-8',str(pdf),str(p)],capture_output=True,timeout=30)
            assert q.returncode==0;rows.append(dict(page=page,file=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
        r.update(complete=True,text_pages=rows)
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}')
    with (OUT/'download_extraction_attempt01.json').open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps({k:v for k,v in r.items() if k!='text_pages'},ensure_ascii=False));return 0 if r['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
