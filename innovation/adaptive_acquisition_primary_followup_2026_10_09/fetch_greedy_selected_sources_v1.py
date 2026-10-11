"""Fetch fixed-commit authors files selected from real src listing and README."""
import gzip,json,time,ssl,urllib.request,traceback
from pathlib import Path
from resource_guard_v1 import HERE,guard,read,entry,bind,dump
started=time.perf_counter();before=guard(started);source=read(HERE/'greedy_src_listing_attempt01/receipt.json');assert source['complete'];sha=source['current_commit_sha']
out=HERE/'greedy_selected_sources_attempt01';out.mkdir(exist_ok=False);records=[]
paths=['src/train_policy.py','src/compute_snr.py','src/helpers/data_loading.py','notebooks/mi_ent_curves.ipynb']
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
for path in paths:
 guard(started);url='https://raw.githubusercontent.com/Timsey/pg_mri/'+sha+'/'+path;r=dict(path_on_author_repo=path,requested_url=url,complete=False,text_actually_read=False,code_executed=False)
 try:
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
   raw=response.read(100001);assert len(raw)<=100000;r.update(http_status=response.status,effective_url=response.url)
  raw.decode('utf-8');p=out/(path.replace('/','__')+'.gz');p.write_bytes(gzip.compress(raw,mtime=0))
  r.update(complete=True,saved=entry(p),raw_bytes=len(raw))
  if path.endswith('.ipynb'):
   notebook=json.loads(raw);code=[dict(index=i,cell_type=v['cell_type'],source=''.join(v.get('source',[]))) for i,v in enumerate(notebook['cells']) if v['cell_type'] in ('code','markdown')]
   cp=out/'mi_notebook_cells.json.gz';cp.write_bytes(gzip.compress((json.dumps(code,ensure_ascii=False)+'\n').encode(),mtime=0));r['extracted_cells']=entry(cp);r['cell_count']=len(code)
 except Exception as e:r.update(http_status=getattr(e,'code',None),error_type=type(e).__name__,error=str(e))
 records.append(r);print(json.dumps(r,ensure_ascii=False),flush=True)
 if r.get('http_status')==429:break
receipt=dict(complete=len(records)==len(paths) and all(v['complete'] for v in records),errors=[v['error'] for v in records if 'error' in v],current_commit_sha=sha,records=records,
 author_code_executed=False,source_bindings=[entry(Path(__file__)),entry(HERE/'ROUND51_AUTHOR_SOURCE_PROTOCOL.md'),entry(HERE/'greedy_src_listing_attempt01/receipt.json')],
 resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',receipt);raise SystemExit(int(not receipt['complete']))
