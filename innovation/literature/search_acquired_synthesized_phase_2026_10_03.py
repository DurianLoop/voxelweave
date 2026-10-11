"""Three narrow direct-neighbour queries for the newly measured phase pattern."""
import json,hashlib,sys,urllib.parse,urllib.request
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/acquired_synthesized_phase_search_2026-10-03'
QUERIES={
 'acquired_synthesized':'(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"super-resolution" OR TITLE_ABS:"slice interpolation") AND (TITLE_ABS:"data consistency" OR TITLE_ABS:"acquired slices" OR TITLE_ABS:"observed slices")',
 'periodic_pattern':'(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"super-resolution" OR TITLE_ABS:interpolation) AND (TITLE_ABS:checkerboard OR TITLE_ABS:"periodic artifacts" OR TITLE_ABS:interleaved OR TITLE_ABS:"inter-slice inconsistency")',
 'seg_resolution_shift':'(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:segmentation AND (TITLE_ABS:blur OR TITLE_ABS:sharpness) AND (TITLE_ABS:"domain shift" OR TITLE_ABS:"resolution mismatch" OR TITLE_ABS:"resolution shift")',
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
 for key,query in QUERIES.items():
  p=OUT/(key+'_attempt_01.response');row=dict(key=key,query=query,started_utc=datetime.now(timezone.utc).isoformat());row['url']='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query+' AND FIRST_PDATE:[1900-01-01 TO 2026-10-03]',format='json',resultType='core',pageSize=12))
  try:
   with opener.open(urllib.request.Request(row['url'],headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:raw=response.read(5000001);row.update(http_status=response.status,final_url=response.url)
   p.write_bytes(raw)
   if len(raw)>5000000:raise ValueError('Index cap exceeded')
   data=json.loads(raw);items=data['resultList']['result'];row.update(reported_total=data['hitCount'],returned=len(items),items=[dict(title=x.get('title'),doi=x.get('doi'),pmcid=x.get('pmcid'),abstract=x.get('abstractText'),year=x.get('pubYear')) for x in items])
  except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)
  if p.exists():row.update(raw_file=p.name,raw_sha256=sha(p),bytes=p.stat().st_size)
  row['finished_utc']=datetime.now(timezone.utc).isoformat();rows.append(row);(OUT/'attempt_01.json').write_text(json.dumps(dict(script_sha256=sha(__file__),plan_sha256=sha(ROOT/'2026-10-03_acquired_synthesized_phase_search_plan.md'),responses=rows,scope='Limited title/abstract queries; not fulltext reading or proof of novelty'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:row.get(k) for k in ('key','reported_total','returned','error')}),flush=True)
if __name__=='__main__':main()
