"""Bounded direct-prior-art and official-source discovery; no MRI data."""
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

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/action_selection_and_crossmoda_2026-10-02'
PLAN=ROOT/'2026-10-02_action_selection_and_crossmoda_followup_plan.md'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def abstract(d):
    if not d:return None
    words={i:w for w,indices in d.items() for i in indices}
    return ' '.join(words[i] for i in sorted(words))

def work(r):
    return {'id':r.get('id'),'title':r.get('title'),'doi':r.get('doi'),'publication_date':r.get('publication_date'),
            'authors':[a.get('author',{}).get('display_name') for a in r.get('authorships',[])],
            'abstract':abstract(r.get('abstract_inverted_index')),'locations':r.get('locations'),
            'best_oa_location':r.get('best_oa_location'),'open_access':r.get('open_access')}

def targets():
    result=[]
    for key,q in [('mri_selection','MRI reconstruction model selection'),('mri_experts','MRI reconstruction mixture of experts'),
                  ('mri_selective','MRI selective reconstruction prediction'),('restoration_gain','image restoration predict improvement')]:
        url='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q,'filter':'to_publication_date:2026-10-02','per-page':8})
        result.append((key,'openalex',url,q))
    result.extend([('crossmoda_2026_exact','openalex_exact','https://api.openalex.org/works/https://doi.org/10.1016/j.media.2026.104282','exact DOI'),
                   ('crossmoda_official_home','html','https://crossmoda.grand-challenge.org/','2021 primary paper official link')])
    return result

def fetch(target,attempt):
    key,provider,url,q=target;row={'key':key,'provider':provider,'url':url,'query':q,'started_utc':datetime.now(timezone.utc).isoformat()}
    path=OUT/f'{key}_attempt_{attempt:02d}.response'
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-source-audit/1.0'}),timeout=30) as response:
                raw=response.read(4_000_001);row.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
        except urllib.error.HTTPError as exc:
            raw=exc.read(4_000_001);row.update(http_status=exc.code,final_url=exc.url);path.write_bytes(raw);raise
        path.write_bytes(raw)
        if len(raw)>4_000_000:raise ValueError('Source response exceeds 4MB cap')
        if provider.startswith('openalex'):
            data=json.loads(raw)
            if provider=='openalex':row.update(reported_total=data['meta']['count'],items=[work(r) for r in data['results']])
            else:row['items']=[work(data)]
        else:
            html=raw.decode('utf-8',errors='replace');row['links']=sorted(set(urllib.parse.urljoin(row['final_url'],u) for u in re.findall(r'href=[\"\x27]([^\"\x27]+)',html)))
            row['title_match']=re.findall(r'<title[^>]*>(.*?)</title>',html,re.S|re.I)
    except Exception as exc:row['error']=f'{type(exc).__name__}: {exc}'
    if path.exists():row.update(raw_file=path.name,raw_sha256=sha(path),bytes=path.stat().st_size)
    row['finished_utc']=datetime.now(timezone.utc).isoformat();return row

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(lambda t:fetch(t,attempt),targets()))
    result={'attempt':attempt,'created_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha(__file__),'plan_sha256':sha(PLAN),
            'scope':'metadata and official homepage only; not fulltext reading or source qualification','responses':rows}
    (OUT/f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for row in rows:
        print(json.dumps({k:row.get(k) for k in ('key','http_status','reported_total','error')},ensure_ascii=False))
        for item in row.get('items',[]):print(json.dumps({k:item.get(k) for k in ('title','doi','publication_date','abstract','best_oa_location')},ensure_ascii=False))
        if 'links' in row:print(json.dumps(row['links'],ensure_ascii=False))

if __name__=='__main__':main()
