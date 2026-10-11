"""Bounded public-index screen, no effect records and no fulltext claims."""
import hashlib, json, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'source_cache/task_utility_search_2026-10-03'
QUERIES = {
 'task_aware': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:reconstruction OR TITLE_ABS:"super-resolution") AND (TITLE_ABS:"downstream task" OR TITLE_ABS:"task-based" OR TITLE_ABS:"task-aware")',
 'task_uncertainty': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:reconstruction AND TITLE_ABS:uncertainty AND (TITLE_ABS:segmentation OR TITLE_ABS:lesion OR TITLE_ABS:diagnostic)',
 'selective_restoration': '(TITLE_ABS:medical OR TITLE_ABS:MRI) AND (TITLE_ABS:"selective restoration" OR TITLE_ABS:"restoration risk" OR TITLE_ABS:"reconstruction quality prediction" OR TITLE_ABS:"reconstruction error prediction")',
}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(exist_ok=False); responses=[]
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for key, query in QUERIES.items():
  row=dict(key=key,query=query,started_utc=datetime.now(timezone.utc).isoformat()); path=OUT/(key+'_attempt_01.response')
  row['url']='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query+' AND FIRST_PDATE:[1900-01-01 TO 2026-10-03]',format='json',resultType='core',pageSize=12))
  try:
   with opener.open(urllib.request.Request(row['url'],headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:
    raw=response.read(5000001); row.update(http_status=response.status,final_url=response.url)
   path.write_bytes(raw)
   if len(raw)>5000000: raise ValueError('5 MB response cap exceeded')
   data=json.loads(raw); items=data['resultList']['result']; row.update(reported_total=data['hitCount'],returned=len(items),items=[dict(title=x.get('title'),doi=x.get('doi'),id=x.get('id'),pmcid=x.get('pmcid'),year=x.get('pubYear'),abstract=x.get('abstractText'),authors=x.get('authorString'),open_access=x.get('isOpenAccess')) for x in items])
  except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
  if path.exists(): row.update(raw_file=path.name,raw_sha256=sha(path),bytes=path.stat().st_size)
  row['finished_utc']=datetime.now(timezone.utc).isoformat(); responses.append(row)
  print(json.dumps({k:row.get(k) for k in ('key','reported_total','returned','error')}),flush=True)
 (OUT/'attempt_01.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),plan_sha256=sha(ROOT/'2026-10-03_task_utility_search_plan.md'),scope='title/abstract index only',responses=responses),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': main()
