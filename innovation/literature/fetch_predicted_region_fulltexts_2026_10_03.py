"""Retrieve three specifically selected public full texts; acquisition is not reading."""
import hashlib,json,sys,urllib.parse,urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/predicted_region_fulltexts_2026-10-03'
PAPERS=[('synthseg_2023','PMC10154424','10.1016/j.media.2023.102789'),('axial_ms_2025','PMC12319988','10.1162/imag.a.45'),('fgas_2026','PMC13385847','10.1038/s41746-026-02780-6')]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def txt(e): return ' '.join(''.join(e.itertext()).split())
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);rows=[]
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for key,pmcid,doi in PAPERS:
  row=dict(key=key,pmcid=pmcid,expected_doi=doi,started_utc=datetime.now(timezone.utc).isoformat(),fulltext_acquired=False,actual_reading_completed=False)
  url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode(dict(db='pmc',id=pmcid[3:],rettype='full',retmode='xml'));row['url']=url;path=OUT/(key+'_attempt_01.xml')
  try:
   with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response:
    raw=response.read(12000001);row.update(http_status=response.status,final_url=response.url)
   path.write_bytes(raw)
   if len(raw)>12000000: raise ValueError('12MB fixed cap exceeded')
   root=ET.fromstring(raw);article=root if root.tag=='article' else root.find('.//article')
   if article is None or article.find('body') is None: raise ValueError('Missing authenticated article body')
   dois=[txt(e) for e in article.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi']
   if doi.lower() not in [x.lower() for x in dois]: raise ValueError('DOI identity differs')
   segments=[(e.tag,txt(e)) for e in article.find('body').iter() if e.tag in ('title','p','table-wrap','fig','disp-formula')]
   floats=article.find('floats-group')
   if floats is not None: segments += [(e.tag,txt(e)) for e in floats if e.tag in ('table-wrap','fig')]
   target=OUT/(key+'_maintext.txt');target.write_text('\n\n'.join('[%04d %s] %s'%(i,tag,text) for i,(tag,text) in enumerate(segments))+'\n',encoding='utf-8')
   perms=article.find('.//permissions')
   row.update(fulltext_acquired=True,title=txt(article.find('.//article-title')),dois=dois,permissions=txt(perms) if perms is not None else None,paragraphs=len(segments),text_file=target.name,text_sha256=sha(target),extraction_warning='Flattened equations/tables and figure captions; no supplementary files or visual figure review')
  except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
  if path.exists(): row.update(raw_file=path.name,raw_sha256=sha(path),bytes=path.stat().st_size)
  row['finished_utc']=datetime.now(timezone.utc).isoformat();rows.append(row)
  print(json.dumps({k:row.get(k) for k in ('key','title','fulltext_acquired','paragraphs','error')},ensure_ascii=False),flush=True)
 with (OUT/'attempt_01.json').open('x',encoding='utf-8') as f: json.dump(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),plan_sha256=sha(ROOT/'2026-10-03_predicted_region_fulltext_selection.md'),papers=rows),f,ensure_ascii=False,indent=2)
if __name__=='__main__': main()
