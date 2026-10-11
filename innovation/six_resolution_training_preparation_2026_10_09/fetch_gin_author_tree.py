"""Resolve author-linked public repository to one fixed commit; no source execution."""
import sys,ssl,time,gzip,json,urllib.request,urllib.parse
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
started=time.perf_counter();out=HERE/'gin_author_tree_attempt01';out.mkdir(exist_ok=False)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
def fetch(url,name,limit=200000):
 v=resource_guard();assert v['workspace_free_bytes']-43_300_000>=8_000_000_000 and time.perf_counter()-started<180
 with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0','Accept':'application/json'}),timeout=25) as response:
  data=response.read(limit+1);assert len(data)<=limit;source=dict(requested_url=url,effective_url=response.url,http_status=response.status)
 path=out/(name+'.gz');path.write_bytes(gzip.compress(data,mtime=0));source['saved']=entry(path);return json.loads(data),source
r=dict(complete=False,errors=[],repository='cheng-01037/Causality-Medical-Image-Domain-Generalization',author_code_executed=False,
 final_peer_reviewed_paper_actually_read=False,medical_data_uploaded=False)
try:
 base='https://api.github.com/repos/'+r['repository'];meta,ms=fetch(base,'metadata.json')
 commit,cs=fetch(base+'/commits/'+urllib.parse.quote(meta['default_branch'],safe=''),'commit.json')
 tree,ts=fetch(base+'/git/trees/'+commit['sha']+'?recursive=1','tree.json',300000);assert not tree.get('truncated')
 r.update(complete=True,commit_sha=commit['sha'],commit_date=commit['commit']['committer']['date'],default_branch=meta['default_branch'],
  metadata_source=ms,commit_source=cs,tree_source=ts,
  text_files=[x for x in tree['tree'] if x['type']=='blob' and x['path'].endswith(('.py','.md','.txt','.json','.yaml','.yml'))])
except Exception as e:r['errors'].append(dict(type=type(e).__name__,message=str(e)))
r['source_bindings']=[entry(p) for p in [Path(__file__),HERE/'GIN_AUTHOR_CODE_PROTOCOL.md',HERE/'gin_author_locator_attempt01/arxiv.gz']]
dump(out/'receipt.json',r);print(json.dumps(r,ensure_ascii=False));raise SystemExit(int(not r['complete']))
