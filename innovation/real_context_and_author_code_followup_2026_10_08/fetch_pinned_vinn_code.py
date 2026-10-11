"""Read-only fixed tag resolution and bounded public source acquisition; never import sources."""
import sys,json,ssl,time
from pathlib import Path
from urllib.request import Request,build_opener,ProxyHandler,HTTPSHandler,HTTPRedirectHandler
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
class Redirect(HTTPRedirectHandler):
    max_redirections=3
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        assert urlsplit(newurl).scheme=='https';return super().redirect_request(req,fp,code,msg,headers,newurl)
def get(url,path):
    ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
    opener=build_opener(ProxyHandler({}),HTTPSHandler(context=ctx),Redirect())
    with opener.open(Request(url,headers={'User-Agent':'MRI-public-source-read/1.0','Accept':'application/vnd.github+json'}),timeout=30) as response:
        body=response.read(400001);assert len(body)<=400000
        dump(path.with_suffix(path.suffix+'.headers.json'),dict(requested_url=url,effective_url=response.geturl(),status=response.status,headers=dict(response.headers)))
    with path.open('xb') as f:f.write(body)
    return body
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    out=HERE/'vinn_code_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],repository='https://github.com/Deep-MI/FastSurfer',requested_tag='v2.3.0',records=[],
        author_code_files_actually_read=0,author_code_imported=False,author_code_executed=False,medical_arrays_loaded=0,CUDA_initialized=False)
    try:
        ref=json.loads(get('https://api.github.com/repos/Deep-MI/FastSurfer/git/ref/tags/v2.3.0',out/'tag_ref.json'))
        obj=ref['object'];assert ref['ref']=='refs/tags/v2.3.0'
        if obj['type']=='tag':
            tag=json.loads(get('https://api.github.com/repos/Deep-MI/FastSurfer/git/tags/'+obj['sha'],out/'annotated_tag.json'));obj=tag['object']
        assert obj['type']=='commit' and len(obj['sha'])==40;commit=obj['sha'];r['pinned_commit']=commit
        paths=['FastSurferCNN/models/interpolation_layer.py','FastSurferCNN/models/networks.py','FastSurferCNN/models/sub_module.py','FastSurferCNN/data_loader/augmentation.py']
        def fetch(rel):
            record=dict(repo_path=rel,complete=False,errors=[],actual_source_reading_completed=False)
            path=out/rel.replace('/','__');url='https://raw.githubusercontent.com/Deep-MI/FastSurfer/'+commit+'/'+rel
            try:get(url,path);record.update(complete=True,url=url,source_binding=entry(path))
            except Exception as e:record['errors'].append(type(e).__name__+': '+str(e))
            return record
        with ThreadPoolExecutor(max_workers=2) as pool:r['records']=list(pool.map(fetch,paths))
        r['errors']=[e for v in r['records'] for e in v['errors']];r['complete']=all(v['complete'] for v in r['records'])
        r['tag_is_not_proven_exact_2022_paper_training_version']=True
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
    r.update(elapsed_seconds=time.perf_counter()-started,source_bindings=[entry(p) for p in [Path(__file__),HERE/'AUTHOR_CODE_READ_PROTOCOL.md']]);dump(out/'receipt.json',r)
    assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<2_000_000 and time.perf_counter()-started<180
    print(json.dumps(r),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
