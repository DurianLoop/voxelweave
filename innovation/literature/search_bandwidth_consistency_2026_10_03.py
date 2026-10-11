"""Bounded public-index retrieval, not a fulltext reading count."""
import hashlib, json, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'source_cache/bandwidth_consistency_search_2026-10-03'
QUERIES = {
 'slice_blur': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"slice interpolation" OR TITLE_ABS:"through-plane interpolation") AND (TITLE_ABS:blur OR TITLE_ABS:aliasing)',
 'anisotropic_seg': '(TITLE_ABS:"anisotropic MRI" OR TITLE_ABS:"anisotropic magnetic resonance") AND TITLE_ABS:segmentation AND (TITLE_ABS:resolution OR TITLE_ABS:"partial volume")',
 'processing_order': '(TITLE_ABS:"medical imaging" OR TITLE_ABS:MRI) AND (TITLE_ABS:resampling OR TITLE_ABS:interpolation) AND (TITLE_ABS:pipeline OR TITLE_ABS:"processing order" OR TITLE_ABS:"order of operations")',
 'slice_sr_task': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"slice super-resolution" OR TITLE_ABS:"through-plane super-resolution") AND (TITLE_ABS:segmentation OR TITLE_ABS:boundary)',
 'slice_consistency': '(TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND (TITLE_ABS:"slice consistency" OR TITLE_ABS:"slice inconsistency" OR TITLE_ABS:"inter-slice consistency") AND (TITLE_ABS:blur OR TITLE_ABS:sharpness OR TITLE_ABS:resolution)',
}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(exist_ok=False)
 opener = urllib.request.build_opener(urllib.request.ProxyHandler({})); rows = []
 for key, query in QUERIES.items():
  path = OUT / (key + '_attempt_01.response')
  row = dict(key=key, query=query, started_utc=datetime.now(timezone.utc).isoformat())
  row['url'] = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode(dict(query=query+' AND FIRST_PDATE:[1900-01-01 TO 2026-10-03]',format='json',resultType='core',pageSize=12))
  try:
   with opener.open(urllib.request.Request(row['url'],headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:
    raw = response.read(5000001); row.update(http_status=response.status,final_url=response.url)
   path.write_bytes(raw)
   if len(raw)>5000000: raise ValueError('Index response cap exceeded')
   data=json.loads(raw); items=data['resultList']['result']
   row.update(reported_total=data['hitCount'],returned=len(items),items=[dict(title=x.get('title'),doi=x.get('doi'),pmcid=x.get('pmcid'),year=x.get('pubYear'),abstract=x.get('abstractText'),authors=x.get('authorString'),open_access=x.get('isOpenAccess')) for x in items])
  except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
  if path.exists(): row.update(raw_file=path.name,raw_sha256=sha(path),bytes=path.stat().st_size)
  row['finished_utc']=datetime.now(timezone.utc).isoformat(); rows.append(row)
  (OUT/'attempt_01.json').write_text(json.dumps(dict(script_sha256=sha(__file__),plan_sha256=sha(ROOT/'2026-10-03_bandwidth_consistency_search_plan.md'),scope='Title/abstract index only; acquisition is not reading and absence is not novelty.',responses=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps({k:row.get(k) for k in ('key','reported_total','returned','error')}),flush=True)
if __name__=='__main__': main()
