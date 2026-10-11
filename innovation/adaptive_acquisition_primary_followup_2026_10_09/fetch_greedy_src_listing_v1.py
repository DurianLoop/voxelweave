"""Read fixed public src directory and README; no Git API retry or author execution."""
import gzip,json,ssl,time,urllib.request,re,traceback
from pathlib import Path
from resource_guard_v1 import HERE,guard,read,entry,bind,dump
started=time.perf_counter();before=guard(started);old=read(HERE/'greedy_public_page_attempt01/receipt.json');assert old['complete'];sha=old['current_commit_sha'];bind(old['saved_page'])
out=HERE/'greedy_src_listing_attempt01';out.mkdir(exist_ok=False);records=[];r=dict(complete=False,errors=[],current_commit_sha=sha,records=records,author_code_executed=False)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
try:
 for label,url,limit in [('src_directory','https://github.com/Timsey/pg_mri/tree/'+sha+'/src',1200000),('README','https://raw.githubusercontent.com/Timsey/pg_mri/'+sha+'/README.md',100000)]:
  guard(started)
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=25) as response:
   raw=response.read(limit+1);assert len(raw)<=limit;record=dict(name=label,requested_url=url,effective_url=response.url,http_status=response.status)
  p=out/(label+('.html.gz' if label=='src_directory' else '.md'));data=gzip.compress(raw,mtime=0) if label=='src_directory' else raw;assert len(data)<=150000;p.write_bytes(data);record['saved']=entry(p)
  if label=='src_directory':
   j=[]
   for v in re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',raw.decode('utf-8'),re.S):
    try:j.append(json.loads(v))
    except json.JSONDecodeError:pass
   def values(v,key):
    if isinstance(v,dict):
     if key in v:yield v[key]
     for x in v.values():yield from values(x,key)
    elif isinstance(v,list):
     for x in v:yield from values(x,key)
   oids=[x for v in j for x in values(v,'currentOid')];assert sha in oids
   record['directory_item_lists']=[x for v in j for x in values(v,'items') if isinstance(x,list)]
  else:record['text']=raw.decode('utf-8')
  records.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
 r['complete']=len(records)==2
except Exception as e:r.update(error_type=type(e).__name__,http_status=getattr(e,'code',None));r['errors'].append(str(e));r['traceback']=traceback.format_exc()
r.update(source_bindings=[entry(Path(__file__)),entry(HERE/'ROUND51_AUTHOR_SOURCE_PROTOCOL.md'),entry(HERE/'greedy_public_page_attempt01/receipt.json')],resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r);raise SystemExit(int(not r['complete']))
