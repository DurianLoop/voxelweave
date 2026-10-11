"""Anonymous exact current commit/tree metadata; no author code execution."""
import json,gzip,time,ssl,urllib.request,traceback
from pathlib import Path
from resource_guard_v1 import HERE,guard,entry,dump
started=time.perf_counter();before=guard(started);out=HERE/'greedy_author_tree_attempt01';out.mkdir(exist_ok=False)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
rows=[];r=dict(complete=False,errors=[],records=rows,author_code_executed=False,patient_data_uploaded=False,original_training_modified=False)
def get(name,url):
 guard(started)
 with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0','Accept':'application/vnd.github+json'}),timeout=25) as response:
  data=response.read(300001);assert len(data)<=300000
  row=dict(name=name,requested_url=url,effective_url=response.url,http_status=response.status)
 p=out/(name+'.json.gz');p.write_bytes(gzip.compress(data,mtime=0));row['saved']=entry(p);rows.append(row)
 return json.loads(data)
try:
 commits=get('current_commit','https://api.github.com/repos/Timsey/pg_mri/commits?per_page=1');assert len(commits)==1
 commit=commits[0];sha=commit['sha'];tree_sha=commit['commit']['tree']['sha'];assert len(sha)==len(tree_sha)==40
 tree=get('fixed_tree','https://api.github.com/repos/Timsey/pg_mri/git/trees/'+tree_sha+'?recursive=1');assert not tree['truncated'] and tree['sha']==tree_sha
 r.update(complete=True,current_commit_sha=sha,current_commit_date=commit['commit']['committer']['date'],tree_sha=tree_sha,
  current_commit_is_verified_paper_release=False,files=[dict(path=v['path'],size=v.get('size'),sha=v['sha']) for v in tree['tree'] if v['type']=='blob'])
except Exception as e:r.update(error_type=type(e).__name__,http_status=getattr(e,'code',None));r['errors'].append(str(e));r['traceback']=traceback.format_exc()
r.update(source_bindings=[entry(Path(__file__)),entry(HERE/'ROUND51_AUTHOR_SOURCE_PROTOCOL.md'),entry(HERE/'primary_html_attempt01/greedy/primary.html.gz')],resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True);raise SystemExit(int(not r['complete']))
