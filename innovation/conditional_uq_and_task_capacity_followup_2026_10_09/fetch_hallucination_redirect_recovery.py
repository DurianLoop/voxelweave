"""Continue from the already returned official repository redirect, without refetch."""
import sys,json,time,urllib.request,ssl
from pathlib import Path
import search_primary_candidates as h
HERE=Path(__file__).resolve().parent
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();h.guard();prior=HERE/'hallucination_author_tree_attempt01';repo=json.loads((prior/'repo.json').read_text(encoding='utf-8'));old=json.loads((prior/'repo_receipt.json').read_text(encoding='utf-8'))
 assert old['complete'] and old['status']==200 and old['source']['sha256']==h.sha(prior/'repo.json')
 assert old['effective_url']=='https://api.github.com/repositories/346122526' and repo['id']==346122526
 assert repo['name']=='hallucinations-tomo-recon' and repo['homepage']=='https://arxiv.org/abs/2012.00646' and not repo['fork']
 assert repo['full_name']=='comp-imaging-sci/hallucinations-tomo-recon';out=HERE/'hallucination_author_tree_attempt02';out.mkdir(exist_ok=False);records=[]
 def fetch(key,url):
  h.guard();ctx=ssl.create_default_context();op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),h.Redirect());req=urllib.request.Request(url,headers={'User-Agent':'MRI-literature-review/1.0','Accept':'application/vnd.github+json'})
  row=dict(requested_url=url,complete=False)
  try:
   with op.open(req,timeout=30) as response:
    data=response.read(150001);assert len(data)<=150000 and response.status==200;row.update(status=response.status,effective_url=response.geturl())
   assert len(data)+20000<2_000_000-sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
   p=out/(key+'.json')
   with p.open('xb') as f:f.write(data)
   v=json.loads(data);row.update(complete=True,source=dict(path=p.relative_to(h.ROOT).as_posix(),bytes=len(data),sha256=h.sha(p)))
  except Exception as e:row['error']=repr(e);v=None
  records.append(row);h.dump(out/(key+'_receipt.json'),row);return v
 base='https://api.github.com/repos/'+repo['full_name'];ref=fetch('ref',base+'/git/ref/heads/'+repo['default_branch']);tree=None
 if ref:
  assert ref['object']['type']=='commit';tree=fetch('tree',base+'/git/trees/'+ref['object']['sha']+'?recursive=1')
 r=dict(complete=tree is not None and not tree.get('truncated',True),errors=[v['error'] for v in records if not v['complete']],canonical_repo=repo['full_name'],paper_repo='uiuc-comp-imaging-sci/hallucinations-tomo-recon',official_redirect_identity_verified=True,repo_source=old['source'],records=records,commit=ref['object']['sha'] if ref else None,
  files=[dict(path=v['path'],blob_sha1=v['sha'],bytes=v.get('size'),url=v['url']) for v in tree.get('tree',[]) if v['type']=='blob'] if tree else [],author_files_actually_read=0,author_implementation_executed=False,elapsed_seconds=time.perf_counter()-started,resources=h.guard())
 h.dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
