"""Fetch imported helper at fixed commit identified in already downloaded author's file."""
import time,gzip,ssl,json,urllib.request
from pathlib import Path
from resource_guard_v1 import HERE,guard,read,entry,dump
started=time.perf_counter();before=guard(started);v=read(HERE/'greedy_selected_sources_attempt01/receipt.json');assert v['complete'];sha=v['current_commit_sha']
url='https://raw.githubusercontent.com/Timsey/pg_mri/'+sha+'/src/policy_model/policy_model_utils.py'
p=HERE/'greedy_selected_sources_attempt01/src__policy_model__policy_model_utils.py.gz';assert not p.exists();out=HERE/'greedy_policy_utils_fetch_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=False,errors=[],requested_url=url,current_commit_sha=sha,text_actually_read=False,author_code_executed=False)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
try:
 with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
  raw=response.read(100001);assert len(raw)<=100000;r.update(http_status=response.status,effective_url=response.url)
 raw.decode('utf-8');p.write_bytes(gzip.compress(raw,mtime=0));r.update(complete=True,saved=entry(p),raw_bytes=len(raw))
except Exception as e:r.update(http_status=getattr(e,'code',None),error_type=type(e).__name__);r['errors'].append(str(e))
r.update(source_bindings=[entry(Path(__file__)),entry(HERE/'greedy_selected_sources_attempt01/receipt.json')],resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r);print(json.dumps(r),flush=True);raise SystemExit(int(not r['complete']))
