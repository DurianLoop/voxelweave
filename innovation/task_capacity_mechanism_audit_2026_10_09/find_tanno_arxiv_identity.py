"""Single bounded alternative-title identity screen; never counts as fulltext reading."""
import sys,time,json,ssl,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent
from fetch_tanno_pmc import guard,entry,dump
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();guard();out=HERE/'tanno_arxiv_identity_attempt01';out.mkdir(exist_ok=False)
 q='au:Tanno AND ti:uncertainty';url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode(dict(search_query=q,start=0,max_results=8))
 r=dict(complete=False,errors=[],requested_url=url,fulltexts_read=0,actual_reading_completed=False,publication_claim_confirmed=False,goal_status='active')
 try:
  context=ssl.create_default_context();assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
  op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context))
  with op.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0'}),timeout=30) as res:
   data=res.read(40001);assert len(data)<=40000 and res.status==200;r.update(status=res.status,effective_url=res.geturl(),headers=dict(res.headers.items()))
  p=out/'response.xml'
  with p.open('xb') as f:f.write(data)
  root=ET.fromstring(data);ns={'a':'http://www.w3.org/2005/Atom'};records=[]
  for e in root.findall('a:entry',ns):
   record={k:' '.join(e.findtext('a:'+k,default='',namespaces=ns).split()) for k in ['id','title','published','updated','summary']}
   record['authors']=[v.findtext('a:name',namespaces=ns) for v in e.findall('a:author',ns)];records.append(record)
  r.update(complete=True,source=entry(p),records=records)
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
 r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
