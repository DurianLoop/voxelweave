"""Pinned public arXiv v5 HTML; extraction is separate from actual reading."""
import sys,time,ssl,gzip,json,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
from bs4 import BeautifulSoup
started=time.perf_counter();out=HERE/'gin_primary_html_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=False,errors=[],version='2111.12525v5',maintext_actually_read=False,new_maintexts_actually_read=0,
 figure_pixels_read=False,external_supplement_read=False,author_code_executed=False,patient_data_uploaded=False)
try:
 v=resource_guard();assert v['workspace_free_bytes']-43_300_000>=8_000_000_000
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
 url='https://arxiv.org/html/2111.12525v5'
 with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=30) as response:
  data=response.read(1_200_001);assert len(data)<=1_200_000;r.update(requested_url=url,effective_url=response.url,http_status=response.status)
 source=out/'primary.html.gz';source.write_bytes(gzip.compress(data,mtime=0))
 soup=BeautifulSoup(data,'html.parser');article=soup.find('article')
 assert article is not None and 'Causality' in article.get_text() and 'Ouyang' in article.get_text()
 blocks=[]
 for node in article.find_all(['h1','h2','h3','h4','p','figcaption','table']):
  if node.find_parent(class_='ltx_bibliography') is not None:continue
  if node.name=='p' and node.find_parent(['figcaption','table']) is not None:continue
  text=' '.join(node.get_text(' ',strip=True).split())
  if text:blocks.append(dict(index=len(blocks),tag=node.name,id=node.get('id'),text=text))
 formulas=[dict(id=n.get('id'),alttext=n.get('alttext'),mathml=str(n)) for n in article.find_all('math')]
 tables=[dict(index=i,id=n.get('id'),text=' '.join(n.get_text(' ',strip=True).split()),rows=[[' '.join(c.get_text(' ',strip=True).split()) for c in tr.find_all(['td','th'])] for tr in n.find_all('tr')]) for i,n in enumerate(article.find_all('table'))]
 for name,value in [('blocks',blocks),('formulas',formulas),('tables',tables)]:
  (out/(name+'.json.gz')).write_bytes(gzip.compress((json.dumps(value,ensure_ascii=False)+'\n').encode(),mtime=0))
 r.update(complete=True,title=soup.title.get_text() if soup.title else None,blocks=len(blocks),math_nodes=len(formulas),tables=len(tables),
  primary_sources=[entry(p) for p in out.glob('*.gz')])
except Exception as e:r['errors'].append(dict(type=type(e).__name__,message=str(e)))
r['source_bindings']=[entry(p) for p in [Path(__file__),HERE/'GIN_PRIMARY_HTML_PROTOCOL.md',HERE/'gin_author_locator_attempt01/receipt.json']]
assert time.perf_counter()-started<180 and sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<500_000
dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False));raise SystemExit(int(not r['complete']))
