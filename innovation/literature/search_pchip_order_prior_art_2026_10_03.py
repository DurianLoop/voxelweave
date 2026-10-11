"""Two narrow public-index queries; no claim of exhaustive novelty search."""
import hashlib,json,sys,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/pchip_order_prior_art_2026-10-03'
QUERIES={
 'pchip_mri':'(TITLE_ABS:PCHIP OR TITLE_ABS:"piecewise cubic Hermite") AND (TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance" OR TITLE_ABS:resampling)',
 'imaging_order':'(TITLE_ABS:interpolation OR TITLE_ABS:resampling) AND (TITLE_ABS:"order of" OR TITLE_ABS:noncommutative OR TITLE_ABS:commutativity) AND (TITLE_ABS:imaging OR TITLE_ABS:MRI)',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));responses=[]
 for key,query in QUERIES.items():
  path=OUT/(key+'_attempt_01.response');row=dict(key=key,query=query,started_utc=datetime.now(timezone.utc).isoformat())
  row['url']='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query+' AND FIRST_PDATE:[1900-01-01 TO 2026-10-03]',format='json',resultType='core',pageSize=12))
  try:
   with opener.open(urllib.request.Request(row['url'],headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:
    raw=response.read(5000001);row.update(http_status=response.status,final_url=response.url)
   path.write_bytes(raw)
   if len(raw)>5000000: raise ValueError('Index response cap exceeded')
   data=json.loads(raw);items=data['resultList']['result'];row.update(reported_total=data['hitCount'],items=[dict(title=x.get('title'),doi=x.get('doi'),pmcid=x.get('pmcid'),year=x.get('pubYear'),abstract=x.get('abstractText')) for x in items])
  except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
  if path.exists(): row.update(raw_file=path.name,raw_sha256=sha(path),bytes=path.stat().st_size)
  row['finished_utc']=datetime.now(timezone.utc).isoformat();responses.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 (OUT/'attempt_01.json').write_text(json.dumps(dict(script_sha256=sha(__file__),scope='Two narrow Europe PMC title/abstract queries only; absent results do not establish novelty',responses=responses),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__': main()
