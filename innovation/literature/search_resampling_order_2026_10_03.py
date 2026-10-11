"""Bounded public title/abstract search independent of diagnostic effect values."""
import hashlib,json,sys,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'source_cache/resampling_order_search_2026-10-03'
QUERIES={
 'lesion_interpolation':'(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:interpolation AND (TITLE_ABS:"partial volume" OR TITLE_ABS:resampling) AND (TITLE_ABS:segmentation OR TITLE_ABS:lesion)',
 'reconstruction_processing':'(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"super-resolution" OR TITLE_ABS:reconstruction) AND (TITLE_ABS:preprocessing OR TITLE_ABS:resampling) AND (TITLE_ABS:"image quality" OR TITLE_ABS:segmentation)',
 'radiomics_resampling':'(TITLE_ABS:resampling OR TITLE_ABS:interpolation) AND TITLE_ABS:radiomics AND TITLE_ABS:reproducibility',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);responses=[];opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for key,query in QUERIES.items():
  row=dict(key=key,query=query,started_utc=datetime.now(timezone.utc).isoformat());p=OUT/(key+'_attempt_01.response');row['url']='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query+' AND FIRST_PDATE:[1900-01-01 TO 2026-10-03]',format='json',resultType='core',pageSize=12))
  try:
   with opener.open(urllib.request.Request(row['url'],headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as r: raw=r.read(5000001);row.update(http_status=r.status,final_url=r.url)
   p.write_bytes(raw)
   if len(raw)>5000000: raise ValueError('5MB index cap exceeded')
   data=json.loads(raw);items=data['resultList']['result'];row.update(reported_total=data['hitCount'],returned=len(items),items=[dict(title=x.get('title'),doi=x.get('doi'),pmcid=x.get('pmcid'),year=x.get('pubYear'),authors=x.get('authorString'),abstract=x.get('abstractText'),open_access=x.get('isOpenAccess')) for x in items])
  except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
  if p.exists(): row.update(raw_file=p.name,raw_sha256=sha(p),bytes=p.stat().st_size)
  row['finished_utc']=datetime.now(timezone.utc).isoformat();responses.append(row);print(json.dumps({k:row.get(k) for k in ('key','reported_total','returned','error')}),flush=True)
 (OUT/'attempt_01.json').write_text(json.dumps(dict(script_sha256=sha(__file__),plan_sha256=sha(ROOT/'2026-10-03_resampling_order_search_plan.md'),responses=responses,scope='title/abstract index only'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__': main()
