"""Read-only small author metadata; no repository or archive code is executed."""
import sys,time,ssl,json,gzip,urllib.request,urllib.parse
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,dump
started=time.perf_counter();resource_guard();out=HERE/'author_metadata_attempt01';out.mkdir(exist_ok=False)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
def fetch(url,name,limit=250000):
    with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0','Accept':'application/json'}),timeout=25) as response:
        data=response.read(limit+1);assert len(data)<=limit;status=response.status;effective=response.url
    p=out/(name+'.json.gz');p.write_bytes(gzip.compress(data,mtime=0))
    return json.loads(data),dict(requested_url=url,effective_url=effective,http_status=status,saved=entry(p))
rows=[]
try:
    v,record=fetch('https://zenodo.org/api/records/18331077','routing_zenodo')
    assert str(v['id'])=='18331077' and v.get('doi')=='10.5281/zenodo.18331077'
    rows.append(dict(kind='routing_implementation',complete=True,source=record,title=v['metadata'].get('title'),
        files=[{k:x.get(k) for k in ['key','size','checksum','links']} for x in v.get('files',[])],
        code_executed=False,file_bodies_downloaded=False))
except Exception as e:rows.append(dict(kind='routing_implementation',complete=False,error=dict(type=type(e).__name__,message=str(e))))
try:
    repo='ZHW11/SFADA-for-brain-tumor-segmentation';base='https://api.github.com/repos/'+repo
    meta,ms=fetch(base,'active_github_metadata');ref,rs=fetch(base+'/git/ref/heads/'+urllib.parse.quote(meta['default_branch'],safe=''),'active_github_ref')
    commit=ref['object']['sha'];tree,ts=fetch(base+'/git/trees/'+commit+'?recursive=1','active_github_tree',500000);assert not tree.get('truncated')
    rows.append(dict(kind='active_annotation_implementation',complete=True,repo=repo,commit_sha=commit,default_branch=meta['default_branch'],
        sources=[ms,rs,ts],text_files=[x for x in tree['tree'] if x['type']=='blob' and x['path'].endswith(('.py','.md','.yml','.yaml','.json','.txt'))],code_executed=False))
except Exception as e:rows.append(dict(kind='active_annotation_implementation',complete=False,error=dict(type=type(e).__name__,message=str(e))))
assert time.perf_counter()-started<180;resource_guard()
r=dict(complete=all(x['complete'] for x in rows),records=rows,source_bindings=[entry(Path(__file__)),entry(HERE/'PRIMARY_SELECTION.md')],
    code_executed=False,medical_data_uploaded=False,elapsed_seconds=time.perf_counter()-started,goal_status='active')
dump(out/'receipt.json',r)
for x in rows:print(json.dumps(x,ensure_ascii=False),flush=True)
raise SystemExit(int(not r['complete']))
