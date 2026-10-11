"""Public final code declaration; freeze a commit before reading implementation."""
import sys,json,time,ssl,urllib.request,urllib.parse
from pathlib import Path
from fetch_arxiv_maintext import guard,dump,entry,Redirect
HERE=Path(__file__).resolve().parent
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();guard();out=HERE/'author_tree_attempt01';out.mkdir(exist_ok=False)
 r=dict(complete=False,errors=[],requests=[],author_files_read=0,author_code_executed=False,publication_claim_confirmed=False,goal_status='active')
 def get(url,name):
  guard();ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
  op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),Redirect())
  with op.open(urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'application/vnd.github+json'}),timeout=30) as res:
   data=res.read(200001);assert len(data)<=200000 and res.status==200;v=json.loads(data);record=dict(requested_url=url,effective_url=res.geturl(),status=res.status)
  p=out/name
  with p.open('xb') as f:f.write(data)
  record['source']=entry(p);r['requests'].append(record);return v
 try:
  repo=get('https://api.github.com/repos/rtanno21609/SaferNeuroimageEnhancement','repo.json');name=repo['full_name'];assert name.endswith('/SaferNeuroimageEnhancement') and not repo['private']
  ref=get('https://api.github.com/repos/'+name+'/git/ref/heads/'+urllib.parse.quote(repo['default_branch'],safe=''),'ref.json');commit=ref['object']['sha'];assert len(commit)==40 and ref['object']['type']=='commit'
  tree=get('https://api.github.com/repos/'+name+'/git/trees/'+commit+'?recursive=1','tree.json');assert not tree.get('truncated')
  files=[v for v in tree['tree'] if v['type']=='blob'];r.update(complete=True,repository=name,repo_id=repo['id'],default_branch=repo['default_branch'],commit=commit,files=files)
 except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
 r['elapsed_seconds']=time.perf_counter()-started;dump(out/'receipt.json',r)
 print(json.dumps({k:v for k,v in r.items() if k!='files'},ensure_ascii=False),flush=True)
 if r['complete']:
  for v in r['files']:
   if v['path'].endswith('.py') or 'README' in v['path']:print(json.dumps(v,ensure_ascii=False),flush=True)
 return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
