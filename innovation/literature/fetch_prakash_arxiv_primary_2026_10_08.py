"""Find exact-title public arXiv author manuscript using metadata, no guessed IDs."""
import hashlib
import json
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode,urlparse
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'literature/source_cache/downstream_feature_cost_primary_2026-10-08'
OUT=BASE/'prakash_arxiv_attempt01'


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def get(url,name,limit):
    path=OUT/name
    proc=subprocess.run(['curl.exe','--noproxy','*','--fail','--silent','--show-error','--location',
        '--max-redirs','3','--proto','=https','--proto-redir','=https','--max-time','30',
        '--max-filesize',str(limit),'--dump-header',str(OUT/(name+'_headers.txt')),
        '--output',str(path),'--write-out','%{http_code}\n%{url_effective}',url],capture_output=True,timeout=35)
    (OUT/(name+'_curl_stderr.txt')).write_bytes(proc.stderr)
    assert proc.returncode==0,(proc.returncode,proc.stderr.decode('utf-8',errors='replace'))
    assert path.stat().st_size<=limit
    return path,dict(requested_url=url,status_stdout=proc.stdout.decode('utf-8'),actual_curl_subprocess_exit=proc.returncode,**entry(path))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],records=[],
        source_bindings=[entry(Path(__file__)),entry(BASE/'acquisition_attempt01.json'),
            entry(ROOT/'DEPLOYMENT_FEATURE_COST_AND_DOWNSTREAM_PROTOCOL_2026-10-08.md')],
        public_GET_only=True,TLS_certificate_verification_disabled=False,new_primary_papers_read=0,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0)
    try:
        title='Leveraging self-supervised denoising for image segmentation'
        url='https://export.arxiv.org/api/query?'+urlencode({'search_query':'ti:"'+title+'"','max_results':3})
        path,meta=get(url,'title_metadata.xml',1_000_000)
        r['records'].append(meta)
        ns={'a':'http://www.w3.org/2005/Atom'}
        entries=ET.fromstring(path.read_bytes()).findall('a:entry',ns)
        candidates=[]
        for e in entries:
            name=' '.join(e.findtext('a:title',namespaces=ns).split())
            if name.casefold()==title.casefold():
                candidates.append((e,name))
        assert len(candidates)==1,[(e.findtext('a:id',namespaces=ns),e.findtext('a:title',namespaces=ns)) for e in entries]
        e,name=candidates[0]
        authors=[a.findtext('a:name',namespaces=ns) for a in e.findall('a:author',ns)]
        assert authors[0]=='Mangal Prakash' and authors[-1]=='Alexander Krull'
        pdfs=[v.attrib['href'] for v in e.findall('a:link',ns) if v.attrib.get('title')=='pdf']
        assert len(pdfs)==1
        pdfurl=pdfs[0].replace('http://','https://',1)
        assert urlparse(pdfurl).hostname in ('arxiv.org','export.arxiv.org')
        r['identity']=dict(title=name,authors=authors,arxiv_id=e.findtext('a:id',namespaces=ns),
            published=e.findtext('a:published',namespaces=ns),updated=e.findtext('a:updated',namespaces=ns),
            crossref_DOI='10.1109/isbi45749.2020.9098559',identity_source='exact-title Atom and matching first/last authors')
        pdf,pdfmeta=get(pdfurl,'prakash_verified.pdf',10_000_000)
        r['records'].append(pdfmeta)
        assert pdf.read_bytes().startswith(b'%PDF')
        sys.path.insert(0,str(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/site_packages'))
        from pypdf import PdfReader
        reader=PdfReader(pdf)
        r['physical_pages']=len(reader.pages)
        texts=[]
        for number,page in enumerate(reader.pages,1):
            p=OUT/f'prakash_page{number:02d}.txt'
            with p.open('x',encoding='utf-8') as f:
                f.write(page.extract_text() or '')
            texts.append(dict(physical_page=number,text_read=False,**entry(p)))
        r['page_texts']=texts
        r['complete']=True
    except Exception as exc:
        r['errors'].append(type(exc).__name__+': '+str(exc))
        r['traceback']=traceback.format_exc()
    r['saved_bytes']=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())
    assert r['saved_bytes']<15_000_000
    with (OUT/'acquisition_attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','identity','physical_pages','saved_bytes')},ensure_ascii=False),flush=True)
    return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
