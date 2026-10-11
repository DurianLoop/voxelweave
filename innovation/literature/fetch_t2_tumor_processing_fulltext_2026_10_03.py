"""One new public pathology study selected from the narrow follow-up index."""
import hashlib,json,sys,urllib.parse,urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/t2_tumor_processing_fulltext_2026-10-03'
DOI='10.1148/ryai.230208'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def content(e): return ' '.join(''.join(e.itertext()).split())
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);raw_path=OUT/'neuroblastoma_attempt_01.xml'
 row=dict(created_utc=datetime.now(timezone.utc).isoformat(),selection='Direct T2 tumor image-processing and segmentation alterations study from pchip_order_prior_art index; not selected by CPU effects',expected_doi=DOI,pmcid='PMC11294951',script_sha256=sha(__file__),search_index_sha256=sha(ROOT/'source_cache/pchip_order_prior_art_2026-10-03/attempt_01.json'),fulltext_acquired=False,actual_reading_completed=False)
 row['url']='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode(dict(db='pmc',id='11294951',rettype='full',retmode='xml'))
 try:
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  with opener.open(urllib.request.Request(row['url'],headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:
   raw=response.read(12000001);row.update(http_status=response.status,final_url=response.url)
  raw_path.write_bytes(raw)
  if len(raw)>12000000: raise ValueError('12MB response cap exceeded')
  root=ET.fromstring(raw);article=root if root.tag=='article' else root.find('.//article')
  if article is None or article.find('body') is None: raise ValueError('Article/body absent')
  dois=[content(e) for e in article.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi']
  if DOI.lower() not in [d.lower() for d in dois]: raise ValueError('DOI mismatch')
  blocks=[dict(tag=e.tag,text=content(e)) for e in article.find('body').iter() if e.tag in ('title','p','table-wrap','fig','disp-formula')]
  floats=article.find('floats-group')
  if floats is not None: blocks.extend(dict(tag=e.tag,text=content(e)) for e in floats if e.tag in ('table-wrap','fig'))
  p=OUT/'neuroblastoma_blocks.json';p.write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  t=OUT/'neuroblastoma_maintext.txt';t.write_text('\n\n'.join('[%04d %s] %s'%(i,b['tag'],b['text']) for i,b in enumerate(blocks))+'\n',encoding='utf-8')
  permissions=article.find('.//permissions')
  row.update(fulltext_acquired=True,title=content(article.find('.//article-title')),dois=dois,permissions=content(permissions) if permissions is not None else None,blocks=len(blocks),block_file=p.name,block_sha256=sha(p),text_file=t.name,text_sha256=sha(t),warning='Flattened JATS tables/formula/captions; visual figures and supplementary material not inspected')
 except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
 if raw_path.exists(): row.update(raw_file=raw_path.name,raw_sha256=sha(raw_path),bytes=raw_path.stat().st_size)
 row['finished_utc']=datetime.now(timezone.utc).isoformat();(OUT/'attempt_01.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:row.get(k) for k in ('title','fulltext_acquired','blocks','error')}),flush=True)
if __name__=='__main__': main()
