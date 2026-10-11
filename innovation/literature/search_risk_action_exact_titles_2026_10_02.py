"""Adaptive exact-title public lookup; keep initial failed-recall screen."""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'source_cache/risk_action_exact_titles_2026-10-02'
PLAN = ROOT / '2026-10-02_risk_action_exact_query_addendum.md'
QUERIES = [
 ('ensure', 'crossref', "Ensemble Stein's Unbiased Risk Estimator for Unsupervised Learning"),
 ('esure', 'crossref', "Extending Stein's Unbiased Risk Estimator to Train Deep Denoisers with Correlated Pairs of Noisy Images"),
 ('gsure', 'crossref', "Generalized Stein's Unbiased Risk Estimator for Training Deep Neural Networks"),
 ('epmc_unbiased', 'europepmc', 'TITLE_ABS:"unbiased risk" AND (TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance")'),
]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fetch(query, attempt):
    key, provider, phrase = query
    if provider=='crossref':
        url = 'https://api.crossref.org/works?' + urllib.parse.urlencode({'query.title':phrase, 'rows':3, 'filter':'until-pub-date:2026-10-02'})
    else:
        url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode({'query':phrase+' AND FIRST_PDATE:[2000-01-01 TO 2026-10-02]', 'format':'json', 'resultType':'core','pageSize':15})
    path = OUT / f'{key}_attempt_{attempt:02d}.response'
    row = {'key':key, 'provider':provider, 'query':phrase, 'url':url, 'started_utc':datetime.now(timezone.utc).isoformat()}
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(urllib.request.Request(url, headers={'User-Agent':'MRI-literature-audit/1.0'}), timeout=30) as response:
                raw = response.read(5_000_001)
                row.update(http_status=response.status, final_url=response.url)
        except urllib.error.HTTPError as exc:
            raw=exc.read(5_000_001)
            row.update(http_status=exc.code,final_url=exc.url)
            path.write_bytes(raw)
            raise
        path.write_bytes(raw)
        if len(raw)>5_000_000:
            raise ValueError('Response exceeds 5 MB cap')
        data=json.loads(raw)
        if provider=='crossref':
            items=data['message']['items']
            row.update(reported_total=data['message']['total-results'], items=[{
                'title':r.get('title',[None])[0], 'doi':r.get('DOI'), 'abstract':r.get('abstract'),
                'published':r.get('published'), 'fulltext_urls':r.get('link'), 'url':r.get('URL'),
                'authors':r.get('author')} for r in items])
        else:
            items=data['resultList']['result']
            row.update(reported_total=data['hitCount'], items=[{
                'title':r.get('title'), 'doi':r.get('doi'), 'pmcid':r.get('pmcid'), 'pmid':r.get('id'),
                'year':r.get('pubYear'), 'abstract':r.get('abstractText'), 'fulltext_urls':r.get('fullTextUrlList'),
                'authors':r.get('authorString')} for r in items])
        row['returned']=len(items)
    except Exception as exc:
        row['error']=f'{type(exc).__name__}: {exc}'
    if path.exists():
        row.update(raw_file=path.name, raw_sha256=sha(path), bytes=path.stat().st_size)
    row['finished_utc']=datetime.now(timezone.utc).isoformat()
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(lambda q:fetch(q,attempt),QUERIES))
    result={'attempt':attempt,'plan_sha256':sha(PLAN),'script_sha256':sha(__file__),'scope':'exact-title metadata, not full text','responses':rows}
    (OUT / f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for row in rows:
        print(json.dumps({k:row.get(k) for k in ('key','returned','reported_total','error')},ensure_ascii=False))
        for r in row.get('items',[]):
            print(json.dumps({k:r.get(k) for k in ('title','doi','pmcid','year','fulltext_urls')},ensure_ascii=False))

if __name__=='__main__':
    main()
