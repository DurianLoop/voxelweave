"""Discover direct mask-aware and normalization-equivariant prior art."""
import hashlib,json,sys,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/masked_normalization_restoration_search_2026-10-03'
QUERIES=['Region Normalization for Image Inpainting','Normalization Equivariance in Image Denoising','partial convolution mask normalization known regions image restoration','MRI observed slices normalization statistics reconstruction segmentation']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);rows=[];opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for i,query in enumerate(QUERIES):
  row=dict(query=query,url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':query,'rows':6}))
  try:
   with opener.open(row['url'],timeout=25) as response:raw=response.read(5000001);row['http_status']=response.status
   path=OUT/f'query_{i+1:02d}.response';path.write_bytes(raw);data=json.loads(raw);row.update(raw_file=path.name,raw_sha256=sha(path),items=[{k:x.get(k) for k in ('title','DOI','URL','link','published','author')} for x in data['message']['items']])
  except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)
  rows.append(row);(OUT/'attempt_01.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),scope='Metadata discovery only; not fulltext reading or novelty evidence',responses=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(query=query,error=row.get('error'),items=[{k:x[k] for k in ('title','DOI','URL','link')} for x in row.get('items',[])]),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
