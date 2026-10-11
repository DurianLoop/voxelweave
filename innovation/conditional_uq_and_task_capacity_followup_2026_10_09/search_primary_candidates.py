"""Bounded primary indexing; metadata is screening, not full-text reading."""
import sys,time,json,ssl,urllib.request,urllib.parse,concurrent.futures,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from retrieve_stronger_adaptation_primary import Redirect
QUERIES={
 'small_lesion': '(TITLE_ABS:"small lesion" OR TITLE_ABS:"small lesions" OR TITLE_ABS:"foreground sampling") AND (TITLE_ABS:segmentation) AND (TITLE_ABS:MRI OR TITLE_ABS:"magnetic resonance") AND FIRST_PDATE:[1900-01-01 TO 2026-10-09]',
 'posterior_task': '(TITLE_ABS:"posterior uncertainty" OR TITLE_ABS:"uncertainty quantification" OR TITLE_ABS:"posterior sampling") AND (TITLE_ABS:"MRI reconstruction" OR TITLE_ABS:"magnetic resonance reconstruction") AND FIRST_PDATE:[1900-01-01 TO 2026-10-09]'
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def guard():
 r=resource_guard();assert r['workspace_free_bytes']-2_000_000-2_000_000-3_000_000-2_800_000>=8_000_000_000
 assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
 return r
def fetch(key,query,out):
 url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query,format='json',pageSize=8,resultType='lite',sort='RELEVANCE'))
 row=dict(key=key,query=query,requested_url=url,complete=False)
 try:
  guard();ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
  op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),Redirect())
  req=urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'application/json'})
  with op.open(req,timeout=30) as response:
   data=response.read(2_000_001);assert len(data)<=2_000_000 and response.status==200
   row.update(status=response.status,effective_url=response.geturl(),headers=dict(response.headers.items()))
  v=json.loads(data);p=out/(key+'.json')
  with p.open('xb') as f:f.write(data)
  row.update(complete=True,source=dict(path=p.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha(p)),hit_count=v['hitCount'],returned_count=len(v['resultList']['result']))
 except Exception as e:row['error']=repr(e)
 return row
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();guard();out=HERE/'index_attempt01';out.mkdir(exist_ok=False)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(fetch,k,q,out) for k,q in QUERIES.items()];rows=[f.result() for f in futures]
 receipt=dict(complete=all(v['complete'] for v in rows),errors=[v['error'] for v in rows if not v['complete']],records=rows,elapsed_seconds=time.perf_counter()-started,resources=guard(),fulltexts_read=0,publication_claim_confirmed=False,goal_status='active')
 dump(out/'receipt.json',receipt)
 for row in rows:
  print(json.dumps(row,ensure_ascii=False),flush=True)
  if row['complete']:
   v=json.loads((out/(row['key']+'.json')).read_text(encoding='utf-8'))
   for item in v['resultList']['result']:print(json.dumps(item,ensure_ascii=False),flush=True)
 return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
