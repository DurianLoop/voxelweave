"""Pin author's public implementation; listing files does not count as reading them."""
import sys,json,ssl,urllib.request,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard
from retrieve_stronger_adaptation_primary import Redirect
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();out=HERE/'author_tree_attempt01';out.mkdir(exist_ok=False);records=[]
    ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
    op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),Redirect())
    def get(key,url):
        r=dict(key=key,requested_url=url,complete=False);started=time.perf_counter()
        try:
            resource_guard();req=urllib.request.Request(url,headers={'User-Agent':'MRI-primary-author-source-review/1.0','Accept':'application/vnd.github+json'})
            with op.open(req,timeout=30) as response:
                data=response.read(500001);assert len(data)<=500000 and response.status==200
                r.update(HTTP_status=response.status,effective_url=response.geturl());dump(out/(key+'_headers.json'),dict(response.headers.items()))
            p=out/(key+'.json')
            with p.open('xb') as f:f.write(data)
            r.update(complete=True,source_binding=entry(p));obj=json.loads(data)
        except Exception as e:r['error']=repr(e);obj=None
        r['elapsed_seconds']=time.perf_counter()-started;records.append(r);dump(out/(key+'_HTTP_RECEIPT.json'),r);return obj
    repo=get('repo','https://api.github.com/repos/adalca/papago');assert repo and repo['full_name']=='adalca/papago'
    branch=repo['default_branch'];ref=get('ref','https://api.github.com/repos/adalca/papago/git/ref/heads/'+branch);assert ref and ref['object']['type']=='commit'
    commit=ref['object']['sha'];tree=get('tree','https://api.github.com/repos/adalca/papago/git/trees/'+commit+'?recursive=1');assert tree and not tree['truncated']
    files=[dict(path=v['path'],blob_sha=v['sha'],bytes=v.get('size')) for v in tree['tree'] if v['type']=='blob']
    result=dict(complete=True,errors=[],repo='adalca/papago',default_branch=branch,pinned_commit=commit,files=files,records=records,
        author_code_files_actually_read=0,author_code_executed=False,medical_arrays_loaded=0,GT_arrays_loaded=0,neural_forwards=0,
        publication_claim_confirmed=False,goal_status='active',source_bindings=[entry(p) for p in [Path(__file__),HERE/'AUTHOR_IMPLEMENTATION_PROTOCOL.md',
            HERE/'extraction_attempt02/blocks.json',ROOT/'final_training_medical_execution_2026_10_08/retrieve_stronger_adaptation_primary.py']])
    dump(out/'receipt.json',result);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    print(json.dumps({k:v for k,v in result.items() if k not in ['records','source_bindings']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
