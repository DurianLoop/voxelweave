"""Public repository webpage after API quota failure; no further API calls or credentials."""
import json,gzip,time,ssl,urllib.request,re,traceback
from pathlib import Path
from resource_guard_v1 import HERE,guard,entry,dump
started=time.perf_counter();before=guard(started);out=HERE/'greedy_public_page_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=False,errors=[],author_code_executed=False,GitHub_API_retried=False,patient_data_uploaded=False,
 public_page_requested_url='https://github.com/Timsey/pg_mri',separate_public_webpage_read=True,
 per_response_max_bytes=1200000,max_saved_gzip_bytes=150000)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
try:
 with opener.open(urllib.request.Request(r['public_page_requested_url'],headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
  data=response.read(1200001);assert len(data)<=1200000;r.update(http_status=response.status,effective_url=response.url)
 s=data.decode('utf-8');compressed=gzip.compress(data,mtime=0);assert len(compressed)<=150000
 p=out/'repository.html.gz';p.write_bytes(compressed)
 scripts=re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',s,re.S);parsed=[]
 for item in scripts:
  try:parsed.append(json.loads(item))
  except json.JSONDecodeError:pass
 def values(v,key):
  if isinstance(v,dict):
   if key in v:yield v[key]
   for x in v.values():yield from values(x,key)
  elif isinstance(v,list):
   for x in v:yield from values(x,key)
 oids=[v for j in parsed for v in values(j,'currentOid') if isinstance(v,str) and re.fullmatch('[0-9a-f]{40}',v)]
 branches=[v for j in parsed for v in values(j,'defaultBranch') if isinstance(v,str)]
 paths=[v for j in parsed for v in values(j,'items') if isinstance(v,list)]
 assert len(set(oids))==1,(oids,branches)
 r.update(complete=True,current_commit_sha=oids[0],default_branches=branches,repository_root_item_lists=paths,
  current_commit_is_verified_paper_release=False,saved_page=entry(p))
except Exception as e:r.update(error_type=type(e).__name__,http_status=getattr(e,'code',None));r['errors'].append(str(e));r['traceback']=traceback.format_exc()
r.update(source_bindings=[entry(Path(__file__)),entry(HERE/'ROUND51_AUTHOR_SOURCE_PROTOCOL.md'),entry(HERE/'greedy_author_tree_attempt01/receipt.json')],
 policy_amendment='One public repository HTML response up to1.2MB, gzip<=150KB; unchanged stage caps; API403 retained and not retried.',
 resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True);raise SystemExit(int(not r['complete']))
