"""Retrieve three authenticated JATS bodies; acquisition is not reading."""
import hashlib,json,sys,urllib.parse,urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/sparse_task_joint_fulltexts_2026-10-03'
PAPERS=[('joint_scar','PMC10959501','10.1109/isbi53787.2023.10230541'),
 ('soft_spinal','PMC13110827','10.1016/j.media.2025.103473'),
 ('drips','PMC12633610','10.1101/2025.10.22.25337423')]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text(e):return ' '.join(''.join(e.itertext()).split())
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);rows=[]
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for key,pmcid,doi in PAPERS:
  path=OUT/(key+'_attempt_01.xml');r=dict(key=key,pmcid=pmcid,expected_doi=doi,fulltext_acquired=False,actual_reading_completed=False)
  r['url']='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode(dict(db='pmc',id=pmcid[3:],rettype='full',retmode='xml'))
  try:
   with opener.open(r['url'],timeout=30) as response:raw=response.read(12000001);r['http_status']=response.status
   path.write_bytes(raw);assert len(raw)<=12000000
   tree=ET.fromstring(raw);article=tree if tree.tag=='article' else tree.find('.//article');assert article is not None and article.find('body') is not None
   dois=[text(e) for e in article.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi'];assert doi.casefold() in [x.casefold() for x in dois]
   blocks=[dict(tag=e.tag,text=text(e)) for e in article.find('body').iter() if e.tag in ('title','p','table-wrap','fig','disp-formula')]
   floats=article.find('floats-group')
   if floats is not None:blocks.extend(dict(tag=e.tag,text=text(e)) for e in floats if e.tag in ('table-wrap','fig'))
   b=OUT/(key+'_blocks.json');b.write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
   t=OUT/(key+'_maintext.txt');t.write_text('\n\n'.join('[%04d %s] %s'%(i,x['tag'],x['text']) for i,x in enumerate(blocks))+'\n',encoding='utf-8')
   r.update(fulltext_acquired=True,title=text(article.find('.//article-title')),dois=dois,blocks=len(blocks),block_file=b.name,block_sha256=sha(b),text_file=t.name,text_sha256=sha(t))
  except Exception as exc:r['error']=type(exc).__name__+': '+str(exc)
  if path.exists():r.update(raw_file=path.name,raw_sha256=sha(path),bytes=path.stat().st_size)
  rows.append(r);(OUT/'attempt_01.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),selection_sha256=sha(ROOT/'2026-10-03_sparse_task_joint_selection.md'),papers=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps({k:r.get(k) for k in ('key','title','fulltext_acquired','blocks','error')},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
