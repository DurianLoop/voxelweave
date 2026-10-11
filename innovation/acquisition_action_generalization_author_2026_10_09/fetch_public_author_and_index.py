"""Pinned public author repository trees and three bounded literature queries."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,ssl,time,json,gzip,urllib.request,urllib.parse,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,dump
REPOS=['pedrob37/Phys_Seg','Pubec/nnunetv2-unlearning']
QUERIES=['(MRI OR magnetic resonance) AND (test time adaptation) AND (lesion OR tumor OR tumour) AND OPEN_ACCESS:Y',
    '(MRI OR magnetic resonance) AND (task driven OR task aware OR selective reconstruction) AND OPEN_ACCESS:Y',
    '(MRI OR magnetic resonance) AND (acquisition parameters) AND (generalization OR generalisation OR uncertainty) AND OPEN_ACCESS:Y']

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter()
    def guard():
        r=resource_guard();assert time.perf_counter()-started<300
        assert r['workspace_free_bytes']-9_800_000>=8_000_000_000
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000;return r
    before=guard();out=HERE/'public_sources_attempt01';out.mkdir(exist_ok=False)
    dump(out/'frozen_config.json',dict(repositories=REPOS,queries=QUERIES,pageSize=8,source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md')]))
    context=ssl.create_default_context();assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context))
    def fetch(url,name,limit):
        guard()
        with opener.open(urllib.request.Request(url,headers={'User-Agent':'MRIResearchLiterature/1.0','Accept':'application/json'}),timeout=25) as response:
            data=response.read(limit+1);assert len(data)<=limit;state=dict(requested_url=url,effective_url=response.url,http_status=response.status)
        path=out/(name+'.json.gz')
        with path.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as gz:gz.write(data)
        state.update(saved=entry(path),uncompressed_bytes=len(data));return json.loads(data),state
    repositories=[];queries=[]
    for ri,repo in enumerate(REPOS):
        row=dict(repo=repo,complete=False)
        try:
            meta,ms=fetch('https://api.github.com/repos/'+repo,f'repo{ri}_metadata',120_000)
            commit,cs=fetch('https://api.github.com/repos/'+repo+'/commits/'+urllib.parse.quote(meta['default_branch'],safe=''),f'repo{ri}_commit',250_000)
            tree,ts=fetch('https://api.github.com/repos/'+repo+'/git/trees/'+commit['sha']+'?recursive=1',f'repo{ri}_tree',700_000)
            assert not tree.get('truncated')
            row.update(complete=True,commit_sha=commit['sha'],commit_date=commit['commit']['committer']['date'],default_branch=meta['default_branch'],
                metadata=ms,commit_source=cs,tree_source=ts,text_paths=[x for x in tree['tree'] if x['type']=='blob' and x['path'].endswith(('.py','.md','.yaml','.yml','.json','.txt'))])
        except Exception as exc:row['error']=dict(type=type(exc).__name__,message=str(exc))
        repositories.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
    for i,query in enumerate(QUERIES):
        row=dict(query=query,complete=False)
        try:
            data,state=fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query,format='json',pageSize=8,resultType='core')),f'query{i}',400_000)
            row.update(complete=True,source=state,hitCount=data['hitCount'],items=[{k:v.get(k) for k in ['id','pmcid','doi','title','authorString','firstPublicationDate','abstractText','isOpenAccess']} for v in data['resultList']['result']])
        except Exception as exc:row['error']=dict(type=type(exc).__name__,message=str(exc))
        queries.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
    result=dict(complete=all(x['complete'] for x in repositories+queries),repositories=repositories,queries=queries,resources_before=before,resources_after=guard(),
        elapsed_seconds=time.perf_counter()-started,new_maintexts_actually_read=0,author_code_executed=False,patient_arrays_loaded=0,patient_information_uploaded=False,
        publication_claim_confirmed=False,goal_status='active')
    dump(out/'receipt.json',result);return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
