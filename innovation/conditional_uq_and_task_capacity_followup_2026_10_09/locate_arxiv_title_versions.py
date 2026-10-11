"""Exact title lookup in the public arXiv Atom index; never guessed identifiers."""
import json,sys,time,urllib.request,urllib.parse,ssl,xml.etree.ElementTree as ET
from pathlib import Path
import search_primary_candidates as h
HERE=Path(__file__).resolve().parent
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();h.guard();out=HERE/'arxiv_index_attempt01';out.mkdir(exist_ok=False)
 query='ti:"On Hallucinations in Tomographic Image Reconstruction" OR (ti:"Uncertainty modelling" AND au:Tanno)'
 url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode(dict(search_query=query,start=0,max_results=8));row=dict(requested_url=url,query=query,complete=False)
 try:
  ctx=ssl.create_default_context();op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),h.Redirect())
  req=urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'application/atom+xml'})
  with op.open(req,timeout=30) as response:
   data=response.read(250001);assert len(data)<=250000 and response.status==200
   row.update(status=response.status,effective_url=response.geturl(),headers=dict(response.headers.items()))
  p=out/'response.xml'
  with p.open('xb') as f:f.write(data)
  root=ET.fromstring(data);ns={'a':'http://www.w3.org/2005/Atom','x':'http://arxiv.org/schemas/atom'}
  entries=[dict(id=v.findtext('a:id',namespaces=ns),title=v.findtext('a:title',namespaces=ns),summary=v.findtext('a:summary',namespaces=ns),doi=v.findtext('x:doi',namespaces=ns),published=v.findtext('a:published',namespaces=ns),updated=v.findtext('a:updated',namespaces=ns),authors=[a.findtext('a:name',namespaces=ns) for a in v.findall('a:author',ns)],links=[l.attrib for l in v.findall('a:link',ns)]) for v in root.findall('a:entry',ns)]
  row.update(complete=True,source=dict(path=p.relative_to(h.ROOT).as_posix(),bytes=len(data),sha256=h.sha(p)),entries=entries)
 except Exception as e:row['error']=repr(e)
 row.update(elapsed_seconds=time.perf_counter()-started,resources=h.guard(),fulltexts_actually_read=0);h.dump(out/'receipt.json',row);print(json.dumps(row,ensure_ascii=False),flush=True);return int(not row['complete'])
if __name__=='__main__':raise SystemExit(main())
