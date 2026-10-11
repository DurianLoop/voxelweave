"""Read normal public article pages where XML is not distributed; no bypass."""
import hashlib,json,sys,urllib.request
from datetime import datetime,timezone
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'source_cache/anchor_representation_fulltexts_2026-10-03'
class Paragraphs(HTMLParser):
 def __init__(self): super().__init__();self.tag=None;self.parts=[];self.segments=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style'): self.skip+=1
  if not self.skip and self.tag is None and tag in ('h1','h2','h3','h4','p','table'): self.tag=tag;self.parts=[]
 def handle_data(self,data):
  if self.tag and not self.skip: self.parts.append(data)
 def handle_endtag(self,tag):
  if tag in ('script','style'): self.skip=max(0,self.skip-1)
  if self.tag==tag:
   text=' '.join(' '.join(self.parts).split())
   if text: self.segments.append((tag,text))
   self.tag=None;self.parts=[]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[]
 for key,pmcid,doi in [('sparse_overfit_2023','PMC10434268','10.1117/1.jmi.10.4.044007'),('contour_interpolation_2022','PMC9768435','10.1117/1.jmi.9.6.064003')]:
  row=dict(key=key,pmcid=pmcid,expected_doi=doi,url='https://pmc.ncbi.nlm.nih.gov/articles/'+pmcid+'/',started_utc=datetime.now(timezone.utc).isoformat(),fulltext_acquired=False,actual_reading_completed=False);p=OUT/(key+'_html_attempt_01.response')
  try:
   with opener.open(urllib.request.Request(row['url'],headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as response: raw=response.read(12000001);row.update(http_status=response.status,final_url=response.url)
   p.write_bytes(raw)
   if len(raw)>12000000: raise ValueError('12 MB cap exceeded')
   html=raw.decode('utf-8');parser=Paragraphs();parser.feed(html)
   if doi.lower() not in html.lower() or len(parser.segments)<25: raise ValueError('DOI/body identity not authenticated; possible challenge or abstract only')
   out=OUT/(key+'_html_maintext.txt');out.write_text('\n\n'.join('[%04d %s] %s'%(i,tag,text) for i,(tag,text) in enumerate(parser.segments))+'\n',encoding='utf-8')
   row.update(fulltext_acquired=True,segments=len(parser.segments),text_file=out.name,text_sha256=sha(out),extraction_warning='Whole public HTML paragraph stream includes navigation and references; explicitly identify body reading boundaries; no supplementary or visual image review')
  except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
  if p.exists(): row.update(raw_file=p.name,raw_sha256=sha(p),bytes=p.stat().st_size)
  row['finished_utc']=datetime.now(timezone.utc).isoformat();rows.append(row);print(json.dumps({k:row.get(k) for k in ('key','http_status','fulltext_acquired','segments','error')}),flush=True)
 with (OUT/'html_alternate_attempt_01.json').open('x',encoding='utf-8') as f: json.dump(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),reason='Normal public article reading after metadata-only EFetch; no download-control bypass',papers=rows),f,ensure_ascii=False,indent=2)
if __name__=='__main__': main()
