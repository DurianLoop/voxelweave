"""Narrow metadata queries, DOI-linked author PDF and official data pages."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime,timezone
from pathlib import Path
from search_action_selection_and_crossmoda_2026_10_02 import work

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/action_crossmoda_adaptive_2026-10-02'
PLAN=ROOT/'2026-10-02_action_crossmoda_adaptive_selection.md'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def targets():
    rows=[]
    for key,q in [('mri_experts_exact','"MRI" AND "mixture of experts"'),('restoration_selection_exact','"image restoration" AND "model selection"'),
                  ('restoration_performance_exact','"image restoration" AND "performance prediction"')]:
        rows.append((key,'openalex','https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q,'filter':'to_publication_date:2026-10-02','per-page':8}),q))
    q='TITLE_ABS:(MRI OR "magnetic resonance") AND TITLE_ABS:reconstruction AND TITLE_ABS:("model selection" OR "mixture of experts" OR "selective prediction") AND FIRST_PDATE:[2000-01-01 TO 2026-10-02]'
    rows.append(('mri_action_epmc','epmc','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':12}),q))
    rows.extend([('crossmoda_author_pdf','pdf','https://kclpure.kcl.ac.uk/ws/files/385489735/Crossmoda_summary_paper_rebuttal_unmarked_arxiv.pdf','exact DOI linked acceptedVersion'),
                 ('crossmoda_2021_data','html','https://crossmoda.grand-challenge.org/Data/','official homepage link'),
                 ('crossmoda_2022_home','html','https://crossmoda2022.grand-challenge.org/','official homepage link')])
    return rows

def fetch(t,attempt):
    key,provider,url,q=t;limit=20_000_000 if provider=='pdf' else 4_000_000
    row={'key':key,'provider':provider,'url':url,'query':q,'started_utc':datetime.now(timezone.utc).isoformat()}
    path=OUT/f'{key}_attempt_{attempt:02d}.response'
    try:
        try:
            with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-source-audit/1.0'}),timeout=30) as response:
                raw=response.read(limit+1);row.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
        except urllib.error.HTTPError as exc:
            raw=exc.read(limit+1);path.write_bytes(raw);row.update(http_status=exc.code,final_url=exc.url);raise
        path.write_bytes(raw)
        if len(raw)>limit:raise ValueError('Response exceeds declared cap')
        if provider=='openalex':
            data=json.loads(raw);row.update(reported_total=data['meta']['count'],items=[work(r) for r in data['results']])
        elif provider=='epmc':
            data=json.loads(raw);row.update(reported_total=data['hitCount'],items=[{'title':r.get('title'),'doi':r.get('doi'),'pmcid':r.get('pmcid'),
                'pmid':r.get('id'),'year':r.get('pubYear'),'abstract':r.get('abstractText'),'fulltext_urls':r.get('fullTextUrlList')} for r in data['resultList']['result']])
        elif provider=='pdf':
            if raw[:5]!=b'%PDF-':raise ValueError('DOI-linked response is not a PDF')
            pdf=OUT/f'{key}_attempt_{attempt:02d}.pdf';pdf.write_bytes(raw);row.update(pdf_file=pdf.name,pdf_sha256=sha(pdf),valid_pdf_header=True)
        else:
            html=raw.decode('utf-8',errors='replace');row['links']=sorted(set(urllib.parse.urljoin(row['final_url'],u) for u in re.findall(r'href=[\"\x27]([^\"\x27]+)',html)))
    except Exception as exc:row['error']=f'{type(exc).__name__}: {exc}'
    if path.exists():row.update(raw_file=path.name,raw_sha256=sha(path),bytes=path.stat().st_size)
    row['finished_utc']=datetime.now(timezone.utc).isoformat();return row

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=True);attempt=len(list(OUT.glob('attempt_*.json')))+1
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(lambda t:fetch(t,attempt),targets()))
    result={'attempt':attempt,'script_sha256':sha(__file__),'helper_sha256':sha(ROOT/'search_action_selection_and_crossmoda_2026_10_02.py'),
            'plan_sha256':sha(PLAN),'scope':'bounded metadata, author PDF and official web; no patient image/label reads','responses':rows}
    (OUT/f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for row in rows:
        print(json.dumps({k:row.get(k) for k in ('key','http_status','reported_total','pdf_file','error')}))
        for x in row.get('items',[]):print(json.dumps({k:x.get(k) for k in ('title','doi','pmcid')},ensure_ascii=False))

if __name__=='__main__':main()
