"""One public publisher GET from the DOI metadata link, without credentials."""
import sys,time,json,ssl,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
import search_primary_candidates as h
HERE=Path(__file__).resolve().parent
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();h.guard();out=HERE/'tanno_publisher_attempt01';out.mkdir(exist_ok=False)
 cr=json.loads((HERE/'crossref_attempt01/00.json').read_text(encoding='utf-8'))['message'];links=[v for v in cr['link'] if v.get('content-type')=='text/xml'];assert len(links)==1
 url=links[0]['URL'];assert url.startswith('https://api.elsevier.com/');row=dict(doi=cr['DOI'],title=cr['title'][0],requested_url=url,complete=False,fulltext_obtained=False,fulltext_read=False,authenticated_request=False)
 try:
  ctx=ssl.create_default_context();op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),h.Redirect());req=urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'text/xml'})
  with op.open(req,timeout=30) as response:
   data=response.read(1_000_001);assert len(data)<=1_000_000 and response.status==200
   row.update(status=response.status,effective_url=response.geturl(),headers=dict(response.headers.items()))
  remaining=2_000_000-sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());assert len(data)+20000<remaining
  root=ET.fromstring(data);p=out/'response.xml'
  with p.open('xb') as f:f.write(data)
  elements=[v for v in root.iter() if v.tag.rsplit('}',1)[-1]=='full-text-retrieval-response'];body=[v for v in root.iter() if v.tag.rsplit('}',1)[-1] in ['body','rawtext']]
  row.update(complete=True,source=dict(path=p.relative_to(h.ROOT).as_posix(),bytes=len(data),sha256=h.sha(p)),fulltext_obtained=bool(body),root_tag=root.tag,body_elements=len(body))
 except Exception as e:row['error']=repr(e)
 row.update(elapsed_seconds=time.perf_counter()-started,resources=h.guard());h.dump(out/'receipt.json',row);print(json.dumps(row,ensure_ascii=False),flush=True);return int(not row['complete'])
if __name__=='__main__':raise SystemExit(main())
