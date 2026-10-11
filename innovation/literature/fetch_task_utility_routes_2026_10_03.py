"""Acquire public author/PMC routes; extract only authenticated returned content."""
import hashlib, json, sys, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'source_cache/task_utility_fulltexts_2026-10-03'
OPENER=urllib.request.build_opener(urllib.request.ProxyHandler({}))

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fetch(key,url,cap=12000000):
 row=dict(key=key,url=url,started_utc=datetime.now(timezone.utc).isoformat());p=OUT/(key+'_attempt_01.response')
 try:
  with OPENER.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-audit/1.0'}),timeout=30) as r:
   raw=r.read(cap+1);row.update(http_status=r.status,final_url=r.url)
  p.write_bytes(raw)
  if len(raw)>cap: raise ValueError('Bounded response cap exceeded')
 except Exception as exc: row['error']=type(exc).__name__+': '+str(exc)
 if p.exists(): row.update(raw_file=p.name,raw_sha256=sha(p),bytes=p.stat().st_size)
 row['finished_utc']=datetime.now(timezone.utc).isoformat()
 return row

def text(e): return ' '.join(''.join(e.itertext()).split()) if e is not None else ''

def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);rows=[]
 row=fetch('benchmark_repo','https://api.github.com/repos/NikolasMorshuis/UndersampledMRISeg');rows.append(row)
 if not row.get('error'):
  try:
   info=json.loads((OUT/row['raw_file']).read_text(encoding='utf-8'));branch=info['default_branch']
   r=fetch('benchmark_readme','https://raw.githubusercontent.com/NikolasMorshuis/UndersampledMRISeg/'+branch+'/README.md');r['default_branch_at_access']=branch;rows.append(r)
  except Exception as exc: row['parse_error']=str(exc)
 query='ti:"Understanding Benefits and Pitfalls"'
 row=fetch('benchmark_arxiv_index','https://export.arxiv.org/api/query?'+urllib.parse.urlencode(dict(search_query=query,max_results=5)));rows.append(row)
 if not row.get('error'):
  try:
   tree=ET.fromstring((OUT/row['raw_file']).read_bytes());ns={'a':'http://www.w3.org/2005/Atom'}
   row['entries']=[dict(title=text(e.find('a:title',ns)),id=text(e.find('a:id',ns)),summary=text(e.find('a:summary',ns)),links=[x.attrib for x in e.findall('a:link',ns)]) for e in tree.findall('a:entry',ns)]
  except Exception as exc: row['parse_error']=str(exc)
 row=fetch('oncology_review_jats','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=11981920&retmode=xml');row.update(expected_doi='10.1038/s44303-025-00076-0',body_obtained=False,actual_reading_completed=False);rows.append(row)
 if not row.get('error'):
  try:
   tree=ET.fromstring((OUT/row['raw_file']).read_bytes());article=tree if tree.tag=='article' else tree.find('.//article');front=article.find('front')
   dois=[text(e).lower() for e in front.findall('.//article-id') if e.attrib.get('pub-id-type')=='doi']
   if row['expected_doi'] not in dois or article.find('body') is None: raise ValueError('DOI-certified body missing')
   chunks=[]
   def walk(e,context):
    if e.tag=='sec': context=context+[text(e.find('title'))]
    if e.tag in ('p','table-wrap','fig','disp-formula'):
     chunks.append(dict(section=' / '.join(context),kind=e.tag,text=text(e)));return
    for child in e: walk(child,context)
   walk(article.find('body'),['BODY'])
   if article.find('floats-group') is not None: walk(article.find('floats-group'),['FLOATS'])
   p=OUT/'oncology_review_paragraphs.json';p.write_text(json.dumps(chunks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t=OUT/'oncology_review_maintext.txt';t.write_text('\n\n'.join('[%04d %s %s] %s'%(i,x['section'],x['kind'],x['text']) for i,x in enumerate(chunks))+'\n',encoding='utf-8')
   row.update(body_obtained=True,title=text(front.find('.//article-title')),dois=dois,paragraphs=len(chunks),paragraph_file=p.name,paragraph_sha256=sha(p),text_file=t.name,text_sha256=sha(t),permissions=text(front.find('.//permissions')),authors=[text(x) for x in front.findall('.//contrib') if x.attrib.get('contrib-type')=='author'])
  except Exception as exc: row['parse_error']=type(exc).__name__+': '+str(exc)
 (OUT/'routes_attempt_01.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),selection_sha256=sha(ROOT/'2026-10-03_task_utility_fulltext_selection.md'),responses=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for row in rows: print(json.dumps({k:row.get(k) for k in ('key','body_obtained','title','entries','error','parse_error')},ensure_ascii=False),flush=True)

if __name__=='__main__': main()
