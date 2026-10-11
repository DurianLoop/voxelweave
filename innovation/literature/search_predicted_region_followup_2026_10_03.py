"""Bounded, single-attempt targeted literature screen; no paper-claim inference."""
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'source_cache/predicted_region_search_2026-10-03'
PLAN = ROOT / '2026-10-03_predicted_region_followup_search_plan.md'
QUERIES = {
 'task_sr': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:"super-resolution" AND (TITLE_ABS:"segmentation-guided" OR TITLE_ABS:"lesion segmentation" OR TITLE_ABS:"task-driven")',
 'domain_scale': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:segmentation AND (TITLE_ABS:"domain generalization" OR TITLE_ABS:"domain adaptation") AND (TITLE_ABS:resolution OR TITLE_ABS:spacing OR TITLE_ABS:anisotropic)',
 'task_risk': 'TITLE_ABS:reconstruction AND (TITLE_ABS:medical OR TITLE_ABS:MRI) AND (TITLE_ABS:"downstream task" OR TITLE_ABS:"task-based") AND (TITLE_ABS:hallucination OR TITLE_ABS:uncertainty OR TITLE_ABS:robust)',
 'resolution_robust': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:segmentation AND (TITLE_ABS:"resolution-agnostic" OR TITLE_ABS:"low-resolution" OR TITLE_ABS:anisotropic) AND (TITLE_ABS:robust OR TITLE_ABS:generalization OR TITLE_ABS:"domain randomization")',
}
def sha(p):
 return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8')
 OUT.mkdir(exist_ok=False)
 rows=[]
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for key,query in QUERIES.items():
  row=dict(key=key,query=query,started_utc=datetime.now(timezone.utc).isoformat())
  url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query+' AND FIRST_PDATE:[1900-01-01 TO 2026-10-03]',format='json',resultType='core',pageSize=12))
  path=OUT/(key+'_attempt_01.response');row['url']=url
  try:
   with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:
    raw=response.read(5000001);row.update(http_status=response.status,final_url=response.url)
   path.write_bytes(raw)
   if len(raw)>5000000: raise ValueError('5MB fixed response cap exceeded')
   data=json.loads(raw);items=data['resultList']['result']
   row.update(reported_total=data['hitCount'],returned=len(items),items=[dict(title=x.get('title'),doi=x.get('doi'),pmid=x.get('id'),pmcid=x.get('pmcid'),year=x.get('pubYear'),abstract=x.get('abstractText'),authors=x.get('authorString'),open_access=x.get('isOpenAccess')) for x in items])
  except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
  if path.exists(): row.update(raw_file=path.name,raw_sha256=sha(path),bytes=path.stat().st_size)
  row['finished_utc']=datetime.now(timezone.utc).isoformat();rows.append(row)
  print(json.dumps({k:row.get(k) for k in ('key','reported_total','returned','error')}),flush=True)
 with (OUT/'attempt_01.json').open('x',encoding='utf-8') as f:
  json.dump(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),plan_sha256=sha(PLAN),scope='title/abstract screening only',responses=rows),f,ensure_ascii=False,indent=2)
if __name__=='__main__': main()
