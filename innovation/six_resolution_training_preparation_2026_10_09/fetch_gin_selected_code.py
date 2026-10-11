"""Download seven explicitly selected fixed Git blobs and verify Git SHA1; do not execute them."""
import sys,time,ssl,json,gzip,urllib.request,urllib.parse,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard
selected=['README.md','models/imagefilter.py','models/imagefilter3d.py','configs_exp.py',
 'models/exp_trainer.py','dev_traintest_ginipa.py','biasfield_interpolate_cchen/adv_bias.py']
started=time.perf_counter();meta=read(HERE/'gin_author_tree_attempt01/receipt.json');assert meta['complete']
out=HERE/'gin_selected_author_code_attempt01';out.mkdir(exist_ok=False);records=[]
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
for name in selected:
 row=dict(path_in_repository=name,complete=False,actual_lines_read=False,source_executed=False)
 try:
  v=resource_guard();assert time.perf_counter()-started<180 and v['workspace_free_bytes']-43_300_000>=8_000_000_000
  b=next(b for b in meta['text_files'] if b['path']==name);assert b['size']<25000
  url='https://raw.githubusercontent.com/'+meta['repository']+'/'+meta['commit_sha']+'/'+urllib.parse.quote(name,safe='/')
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0'}),timeout=20) as response:
   data=response.read(25001);assert len(data)==b['size'];row.update(requested_url=url,effective_url=response.url,http_status=response.status)
  gitsha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert gitsha==b['sha']
  target=out/(name.replace('/','__')+'.source.txt');target.write_bytes(data)
  row.update(complete=True,saved=entry(target),git_blob_sha1_verified=gitsha,lines=len(data.decode().splitlines()))
 except Exception as e:row['error']=dict(type=type(e).__name__,message=str(e))
 records.append(row)
assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<500000
r=dict(complete=all(v['complete'] for v in records),records=records,commit_sha=meta['commit_sha'],author_code_executed=False,
 source_bindings=[entry(p) for p in [Path(__file__),HERE/'GIN_AUTHOR_CODE_PROTOCOL.md',HERE/'gin_author_tree_attempt01/receipt.json']])
dump(out/'receipt.json',r);print(json.dumps(r));raise SystemExit(int(not r['complete']))
