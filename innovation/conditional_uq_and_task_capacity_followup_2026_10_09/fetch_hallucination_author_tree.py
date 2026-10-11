"""Follow the paper's code URL and pin its current commit, read-only."""
import sys,json,ssl,urllib.request,time
from pathlib import Path
import search_primary_candidates as h
HERE=Path(__file__).resolve().parent;REPO='uiuc-comp-imaging-sci/hallucinations-tomo-recon'
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();h.guard();out=HERE/'hallucination_author_tree_attempt01';out.mkdir(exist_ok=False);rows=[]
 def fetch(key,url):
  h.guard();record=dict(requested_url=url,complete=False)
  try:
   ctx=ssl.create_default_context();op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),h.Redirect());req=urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'application/vnd.github+json'})
   with op.open(req,timeout=30) as response:
    data=response.read(150001);assert len(data)<=150000 and response.status==200
    record.update(status=response.status,effective_url=response.geturl())
   assert len(data)+20000<2_000_000-sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
   obj=json.loads(data);p=out/(key+'.json')
   with p.open('xb') as f:f.write(data)
   record.update(complete=True,source=dict(path=p.relative_to(h.ROOT).as_posix(),bytes=len(data),sha256=h.sha(p)))
  except Exception as e:record['error']=repr(e);obj=None
  rows.append(record);h.dump(out/(key+'_receipt.json'),record);return obj
 repo=fetch('repo','https://api.github.com/repos/'+REPO);ref=tree=None
 if repo:
  assert repo['full_name']==REPO;ref=fetch('ref','https://api.github.com/repos/'+REPO+'/git/ref/heads/'+repo['default_branch'])
 if ref:
  assert ref['object']['type']=='commit';tree=fetch('tree','https://api.github.com/repos/'+REPO+'/git/trees/'+ref['object']['sha']+'?recursive=1')
 r=dict(complete=tree is not None and not tree.get('truncated',True),errors=[v['error'] for v in rows if not v['complete']],records=rows,commit=ref['object']['sha'] if ref else None,
  files=[dict(path=v['path'],blob_sha1=v['sha'],bytes=v.get('size'),url=v['url']) for v in tree.get('tree',[]) if v['type']=='blob'] if tree else [],
  elapsed_seconds=time.perf_counter()-started,author_files_actually_read=0,author_implementation_executed=False,resources=h.guard())
 h.dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
