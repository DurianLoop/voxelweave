"""Stdlib HTML extraction after the missing-bs4 attempt; previous source/failure preserved."""
import sys,time,ssl,gzip,json,urllib.request,re
from html.parser import HTMLParser
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard

class ArticleParser(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.article=0;self.stack=[];self.blocks=[];self.formulas=[];self.tables=[];self.title=[];self.in_title=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='title':self.in_title=True
  if tag=='article':self.article+=1
  if not self.article:return
  if tag in ['h1','h2','h3','h4','p','figcaption','table','math']:
   self.stack.append(dict(tag=tag,id=a.get('id'),alttext=a.get('alttext'),text=[],raw=[self.get_starttag_text()]))
  for v in self.stack:
   if v['tag']=='math' and tag!='math':v['raw'].append(self.get_starttag_text())
 def handle_data(self,data):
  if self.in_title:self.title.append(data)
  for v in self.stack:
   v['text'].append(data)
   if v['tag']=='math':v['raw'].append(data)
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
  for v in self.stack:
   if v['tag']=='math':v['raw'].append('</'+tag+'>')
  indices=[i for i,v in enumerate(self.stack) if v['tag']==tag]
  if indices:
   i=indices[-1];v=self.stack.pop(i);text=' '.join(''.join(v['text']).split())
   if tag=='math':self.formulas.append(dict(id=v['id'],alttext=v['alttext'],mathml=''.join(v['raw'])))
   elif tag=='table':self.tables.append(dict(id=v['id'],text=text))
   if tag!='math' and text and not (tag=='p' and any(x['tag'] in ['table','figcaption'] for x in self.stack)):
    self.blocks.append(dict(index=len(self.blocks),tag=tag,id=v['id'],text=text))
  if tag=='article':self.article-=1

started=time.perf_counter();out=HERE/'gin_primary_html_attempt02';out.mkdir(exist_ok=False)
r=dict(complete=False,errors=[],version='2111.12525v5',maintext_actually_read=False,new_maintexts_actually_read=0,
 figure_pixels_read=False,external_supplement_read=False,author_code_executed=False,patient_data_uploaded=False,
 previous_missing_bs4_import_failure_preserved=True)
try:
 v=resource_guard();assert v['workspace_free_bytes']-43_300_000>=8_000_000_000
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
 url='https://arxiv.org/html/2111.12525v5'
 with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=30) as response:
  data=response.read(1_200_001);assert len(data)<=1_200_000;r.update(requested_url=url,effective_url=response.url,http_status=response.status)
 source=out/'primary.html.gz';source.write_bytes(gzip.compress(data,mtime=0))
 text=data.decode('utf-8');p=ArticleParser();p.feed(text)
 assert p.blocks and 'Causality' in text and 'Ouyang' in text
 # Retain the extracted references as a separate scope; no claim of reading them.
 for name,value in [('blocks',p.blocks),('formulas',p.formulas),('tables',p.tables)]:
  (out/(name+'.json.gz')).write_bytes(gzip.compress((json.dumps(value,ensure_ascii=False)+'\n').encode(),mtime=0))
 r.update(complete=True,title=' '.join(''.join(p.title).split()),blocks=len(p.blocks),math_nodes=len(p.formulas),tables=len(p.tables),
  primary_sources=[entry(f) for f in out.glob('*.gz')],
  section_headings=[b for b in p.blocks if b['tag'] in ['h1','h2','h3','h4']])
except Exception as e:r['errors'].append(dict(type=type(e).__name__,message=str(e)))
r['source_bindings']=[entry(f) for f in [Path(__file__),HERE/'fetch_gin_primary_html.py',HERE/'GIN_PRIMARY_HTML_PROTOCOL.md',HERE/'gin_author_locator_attempt01/receipt.json']]
assert time.perf_counter()-started<180 and sum(f.stat().st_size for f in out.rglob('*') if f.is_file())<500_000
dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False));raise SystemExit(int(not r['complete']))
