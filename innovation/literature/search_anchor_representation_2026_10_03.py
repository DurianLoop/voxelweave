"""Single-attempt, bounded indexing; acquired records are not fulltext reading."""
import hashlib,json,sys,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/anchor_representation_search_2026-10-03'
QUERIES={
 'lesion_forest':'(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:lesion AND (TITLE_ABS:"random forest" OR TITLE_ABS:"decision forest") AND TITLE_ABS:segmentation',
 'sparse_annotation':'(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:segmentation AND (TITLE_ABS:"sparse annotation" OR TITLE_ABS:"sparse slices" OR TITLE_ABS:"sparsely annotated")',
 'label_interpolation':'(TITLE_ABS:medical OR TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"mask interpolation" OR TITLE_ABS:"label interpolation" OR TITLE_ABS:"shape interpolation" OR TITLE_ABS:"contour interpolation")',
 'scale_forest':'(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND TITLE_ABS:segmentation AND (TITLE_ABS:"random forest" OR TITLE_ABS:"decision forest") AND (TITLE_ABS:resolution OR TITLE_ABS:spacing OR TITLE_ABS:scale)',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);rows=[]
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for key,query in QUERIES.items():
  row=dict(key=key,query=query,started_utc=datetime.now(timezone.utc).isoformat());p=OUT/(key+'_attempt_01.response')
  row['url']='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query+' AND FIRST_PDATE:[1900-01-01 TO 2026-10-03]',format='json',resultType='core',pageSize=12))
  try:
   with opener.open(urllib.request.Request(row['url'],headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:
    raw=response.read(5000001);row.update(http_status=response.status,final_url=response.url)
   p.write_bytes(raw)
   if len(raw)>5000000: raise ValueError('5 MB cap exceeded')
   data=json.loads(raw);items=data['resultList']['result'];row.update(reported_total=data['hitCount'],returned=len(items),items=[dict(title=x.get('title'),doi=x.get('doi'),id=x.get('id'),pmcid=x.get('pmcid'),year=x.get('pubYear'),abstract=x.get('abstractText'),authors=x.get('authorString'),open_access=x.get('isOpenAccess')) for x in items])
  except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
  if p.exists(): row.update(raw_file=p.name,raw_sha256=sha(p),bytes=p.stat().st_size)
  row['finished_utc']=datetime.now(timezone.utc).isoformat();rows.append(row);print(json.dumps({k:row.get(k) for k in ('key','reported_total','returned','error')}),flush=True)
 with (OUT/'attempt_01.json').open('x',encoding='utf-8') as f: json.dump(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),plan_sha256=sha(ROOT/'2026-10-03_anchor_representation_search_plan.md'),scope='index/title/abstract screen only',responses=rows),f,ensure_ascii=False,indent=2)
if __name__=='__main__': main()
