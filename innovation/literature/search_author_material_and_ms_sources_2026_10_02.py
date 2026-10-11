"""Public author/repository and source screens; never load patient/model data."""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT / 'source_cache/author_material_and_ms_sources_2026-10-02'
PLAN=ROOT / '2026-10-02_author_material_and_ms_source_plan.md'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def queries():
    rows=[]
    for key,q in [('github_doi','"mrm.30030" in:readme'),('github_title','"Predictive uncertainty" MRI in:readme')]:
        url='https://api.github.com/search/repositories?'+urllib.parse.urlencode({'q':q,'per_page':5})
        rows.append((key,'github',url,q))
    for key,q in [('mslesseg','TITLE_ABS:MSLesSeg'),('msseg2','TITLE_ABS:"MSSEG-2"'),
                  ('crossmoda_later','TITLE_ABS:CrossMoDA AND FIRST_PDATE:[2023-01-01 TO 2026-10-02]')]:
        url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q+' AND FIRST_PDATE:[2000-01-01 TO 2026-10-02]', 'format':'json','resultType':'core','pageSize':10})
        rows.append((key,'europepmc',url,q))
    rows.extend([('ensure_abs','html','https://arxiv.org/abs/2010.10631','exact reference21'),
                 ('ensure_v1','pdf','https://arxiv.org/pdf/2010.10631v1','exact reference21 v1')])
    return rows

def fetch(item,attempt):
    key,provider,url,q=item
    path=OUT / f'{key}_attempt_{attempt:02d}.response'
    row={'key':key,'provider':provider,'url':url,'query':q,'started_utc':datetime.now(timezone.utc).isoformat()}
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-audit/1.0','Accept':'application/vnd.github+json' if provider=='github' else '*/*'}),timeout=30) as response:
                raw=response.read(20_000_001)
                row.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
        except urllib.error.HTTPError as exc:
            raw=exc.read(20_000_001)
            row.update(http_status=exc.code,final_url=exc.url)
            path.write_bytes(raw)
            raise
        path.write_bytes(raw)
        if len(raw)>20_000_000:
            raise ValueError('Response exceeds 20 MB cap')
        if provider=='github':
            d=json.loads(raw)
            row.update(reported_total=d.get('total_count'),items=[{k:r.get(k) for k in ('full_name','html_url','description','default_branch','license','owner','fork','archived')} for r in d.get('items',[])])
        elif provider=='europepmc':
            d=json.loads(raw)
            row.update(reported_total=d['hitCount'],items=[{'title':r.get('title'),'doi':r.get('doi'),'pmcid':r.get('pmcid'),'pmid':r.get('id'),
                      'year':r.get('pubYear'),'authors':r.get('authorString'),'abstract':r.get('abstractText'),'fulltext_urls':r.get('fullTextUrlList')} for r in d['resultList']['result']])
        elif provider=='pdf':
            row['valid_pdf_header']=raw[:5]==b'%PDF-'
            if not row['valid_pdf_header']:
                raise ValueError('Response is not PDF')
            pdf=OUT / f'{key}_attempt_{attempt:02d}.pdf'
            pdf.write_bytes(raw)
            row.update(pdf_file=pdf.name,pdf_sha256=sha(pdf))
        else:
            row.update(contains_exact_arxiv_id=b'2010.10631' in raw, html_received=b'<html' in raw.lower())
    except Exception as exc:
        row['error']=f'{type(exc).__name__}: {exc}'
    if path.exists():
        row.update(raw_file=path.name,raw_sha256=sha(path),bytes=path.stat().st_size)
    row['finished_utc']=datetime.now(timezone.utc).isoformat()
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(lambda item:fetch(item,attempt),queries()))
    result={'attempt':attempt,'script_sha256':sha(__file__),'plan_sha256':sha(PLAN),'scope':'bounded public author and dataset availability, not fulltext reading','responses':rows}
    (OUT / f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for row in rows:
        print(json.dumps({k:row.get(k) for k in ('key','http_status','reported_total','error','pdf_file')},ensure_ascii=False))
        for r in row.get('items',[]):
            print(json.dumps({k:r.get(k) for k in ('title','doi','pmcid','full_name','html_url','description')},ensure_ascii=False))

if __name__=='__main__':
    main()
