"""Bounded public-index collision search; no patient/model access."""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'source_cache/risk_action_assumptions_2026-10-02'
PLAN = ROOT / '2026-10-02_risk_action_assumptions_search_plan.md'
QUERIES = {
    'mri_stein': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:Stein OR TITLE_ABS:SURE OR TITLE_ABS:ENSURE)',
    'ensemble_stein': 'TITLE_ABS:"ensemble" AND TITLE_ABS:"Stein" AND TITLE_ABS:"risk"',
    'correlated_pairs': 'TITLE_ABS:"correlated" AND TITLE_ABS:"noisy" AND (TITLE_ABS:Stein OR TITLE_ABS:"risk")',
    'mri_risk_selection': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:reconstruction AND (TITLE_ABS:"risk estimation" OR TITLE_ABS:"model selection")',
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fetch(item, attempt):
    key, query = item
    url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode({
        'query': query + ' AND FIRST_PDATE:[2000-01-01 TO 2026-10-02]', 'format':'json',
        'resultType':'core', 'pageSize':15})
    path = OUT / f'{key}_attempt_{attempt:02d}.response'
    row = {'key':key, 'query':query, 'url':url, 'requested_cap':15,
           'started_utc':datetime.now(timezone.utc).isoformat()}
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(urllib.request.Request(url, headers={'User-Agent':'MRI-literature-audit/1.0'}), timeout=30) as response:
                raw = response.read(5_000_001)
                row.update(http_status=response.status, final_url=response.url,
                           content_type=response.headers.get('Content-Type'))
        except urllib.error.HTTPError as exc:
            raw = exc.read(5_000_001)
            row.update(http_status=exc.code, final_url=exc.url)
            path.write_bytes(raw)
            raise
        path.write_bytes(raw)
        if len(raw)>5_000_000:
            raise ValueError('Response exceeded 5 MB cap')
        data = json.loads(raw)
        rows = data['resultList']['result']
        row.update(reported_total=data['hitCount'], returned=len(rows), items=[{
            'title':r.get('title'), 'doi':r.get('doi'), 'pmid':r.get('id'), 'pmcid':r.get('pmcid'),
            'year':r.get('pubYear'), 'abstract':r.get('abstractText'), 'authors':r.get('authorString'),
            'fulltext_urls':r.get('fullTextUrlList'), 'oa':r.get('isOpenAccess')} for r in rows])
    except Exception as exc:
        row['error'] = f'{type(exc).__name__}: {exc}'
    if path.exists():
        row.update(raw_file=path.name, raw_sha256=sha(path), bytes=path.stat().st_size)
    row['finished_utc'] = datetime.now(timezone.utc).isoformat()
    return row

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob('attempt_*.json')))+1
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda item:fetch(item, attempt), QUERIES.items()))
    result = {'attempt':attempt, 'scope':'bounded title/abstract metadata, not full-text reading',
              'plan_sha256':sha(PLAN), 'script_sha256':sha(__file__), 'responses':rows}
    (OUT / f'attempt_{attempt:02d}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    for row in rows:
        print(json.dumps({k:row.get(k) for k in ('key','reported_total','returned','error')}, ensure_ascii=False))
        for r in row.get('items',[]):
            print(json.dumps({k:r.get(k) for k in ('title','doi','pmcid','year')}, ensure_ascii=False))

if __name__=='__main__':
    main()
