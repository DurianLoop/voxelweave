"""Two bounded exact-title queries; abstracts are discovery only."""
import sys,time,ssl,gzip,json,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
from resource_guard_v1 import HERE,guard,entry,dump
started=time.perf_counter();before=guard(started);out=HERE/'strong_task_source_locator_attempt01';out.mkdir(exist_ok=False)
queries=[('brainsegfounder','ti:BrainSegFounder',3),('swin_pretraining','ti:"Self-Supervised Pre-Training of Swin Transformers"',2)]
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()));records=[]
for name,query,n in queries:
 guard(started);url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode(dict(search_query=query,max_results=n))
 r=dict(name=name,requested_url=url,query=query,complete=False,maintext_read=False)
 try:
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
   raw=response.read(300001);assert len(raw)<=300000;r.update(http_status=response.status,effective_url=response.url)
  p=out/(name+'.xml.gz');p.write_bytes(gzip.compress(raw,mtime=0));ns={'a':'http://www.w3.org/2005/Atom'};atom=ET.fromstring(raw);rows=[]
  for v in atom.findall('a:entry',ns):
   rows.append(dict(id=v.findtext('a:id',namespaces=ns),title=' '.join(v.findtext('a:title',namespaces=ns).split()),summary=' '.join(v.findtext('a:summary',namespaces=ns).split()),
    authors=[x.findtext('a:name',namespaces=ns) for x in v.findall('a:author',ns)],published=v.findtext('a:published',namespaces=ns),updated=v.findtext('a:updated',namespaces=ns),links=[x.attrib for x in v.findall('a:link',ns)]))
  r.update(complete=True,saved=entry(p),entries=rows)
 except Exception as e:r.update(http_status=getattr(e,'code',None),error_type=type(e).__name__,error=str(e))
 records.append(r);print(json.dumps(r,ensure_ascii=False),flush=True)
 if r.get('http_status')==429:break
receipt=dict(complete=len(records)==2 and all(v['complete'] for v in records),errors=[v['error'] for v in records if 'error' in v],records=records,primary_papers_read=0,
 source_bindings=[entry(Path(__file__)),entry(HERE/'ROUND51_AUTHOR_SOURCE_PROTOCOL.md')],resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',receipt);raise SystemExit(int(not receipt['complete']))
