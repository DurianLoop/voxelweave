"""Bounded independent public metadata queries; acquisition is not fulltext reading."""
import hashlib, json, sys, urllib.parse, urllib.request
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/source_cache/action_utility_followup_2026-10-07'
QUERIES=[
 ('decision_utility','(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:reconstruction OR TITLE_ABS:"super-resolution") AND (TITLE_ABS:"decision" OR TITLE_ABS:"utility" OR TITLE_ABS:"selective")'),
 ('downstream_restoration','TITLE_ABS:"image restoration" AND (TITLE_ABS:"downstream" OR TITLE_ABS:"task-aware" OR TITLE_ABS:"risk")'),
 ('recent_sr_segmentation','TITLE_ABS:"super-resolution" AND TITLE_ABS:segmentation AND (TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND FIRST_PDATE:[2024-01-01 TO 2026-10-07]')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fetch(item):
    key,query=item;url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query,format='json',resultType='core',pageSize=8))
    row=dict(key=key,query=query,url=url,complete=False,actual_fulltext_read=False)
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url,timeout=25) as response:
            raw=response.read(5_000_001);row['http_status']=response.status
        dest=OUT/(key+'_attempt01.response');dest.write_bytes(raw);assert len(raw)<=5_000_000
        data=json.loads(raw);items=data['resultList']['result']
        row.update(complete=True,hit_count=data['hitCount'],returned=len(items),raw_file=dest.name,raw_sha256=sha(dest),
            items=[{k:x.get(k) for k in ('title','authorString','doi','pmcid','pubYear','id','source','isOpenAccess','fullTextUrlList','abstractText')} for x in items])
    except Exception as e:row['error']=type(e).__name__+': '+str(e)
    return row
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,QUERIES))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
        script_sha256=sha(__file__),protocol_sha256=sha(ROOT/'literature/2026-10-07_action_utility_followup_search_protocol.md'),
        queries=rows,actual_new_fulltexts_read=0,actual_training_updates=0,actual_gpu_updates=0,publication_claim_confirmed=False)
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    for row in rows:
        print(json.dumps({k:row.get(k) for k in ('key','complete','hit_count','returned','error')},ensure_ascii=False))
        for item in row.get('items',[]):print(json.dumps({k:item.get(k) for k in ('title','doi','pmcid','pubYear')},ensure_ascii=False))
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
