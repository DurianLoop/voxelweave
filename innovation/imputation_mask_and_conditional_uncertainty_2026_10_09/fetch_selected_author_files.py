"""Download five files at the exact tree commit and verify Git blob IDs."""
import sys,ssl,json,time,hashlib,urllib.request,urllib.parse
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard
from retrieve_stronger_adaptation_primary import Redirect
FILES=['README.md','citations.bib','src/@wgmm/recon.m','src/@wgmm/sigmarecon.m','src/tools/sampleSigmaRecon.m']
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();treepath=HERE/'author_tree_attempt01/receipt.json';tree=read(treepath)
    assert tree['complete'] and not tree['errors'];commit=tree['pinned_commit'];catalog={v['path']:v for v in tree['files']}
    out=HERE/'author_files_attempt01';out.mkdir(exist_ok=False);records=[]
    ctx=ssl.create_default_context();assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
    op=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ctx),Redirect())
    for i,name in enumerate(FILES):
        started=time.perf_counter();resource_guard();expected=catalog[name];url='https://raw.githubusercontent.com/adalca/papago/'+commit+'/'+urllib.parse.quote(name,safe='/')
        r=dict(author_path=name,pinned_commit=commit,requested_url=url,complete=False)
        try:
            with op.open(urllib.request.Request(url,headers={'User-Agent':'MRI-author-source-reading/1.0'}),timeout=30) as response:
                data=response.read(500001);assert len(data)<=500000 and response.status==200
                r.update(HTTP_status=response.status,effective_url=response.geturl());dump(out/(str(i).zfill(2)+'_headers.json'),dict(response.headers.items()))
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==expected['blob_sha'] and len(data)==expected['bytes']
            p=out/(str(i).zfill(2)+'_'+Path(name).name)
            with p.open('xb') as f:f.write(data)
            r.update(complete=True,git_blob_sha1=blob,source_binding=entry(p),line_count=len(data.decode('utf-8').splitlines()),actual_reading_completed=False)
        except Exception as e:r['error']=repr(e)
        r['elapsed_seconds']=time.perf_counter()-started;records.append(r);dump(out/(str(i).zfill(2)+'_HTTP_RECEIPT.json'),r)
    result=dict(complete=all(v['complete'] for v in records),errors=[v.get('error') for v in records if not v['complete']],records=records,
        root_license_not_present_in_pinned_tree=True,repository_license_metadata=None,current_commit_not_asserted_paper_release=True,
        author_code_files_actually_read=0,author_code_executed=False,medical_arrays_loaded=0,neural_forwards=0,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'AUTHOR_IMPLEMENTATION_PROTOCOL.md',treepath,HERE/'author_tree_attempt01/repo.json']])
    assert not any('/' not in v['path'] and 'license' in v['path'].lower() for v in tree['files'])
    dump(out/'receipt.json',result);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    print(json.dumps({k:v for k,v in result.items() if k!='source_bindings'},ensure_ascii=False),flush=True)
    assert result['complete']
if __name__=='__main__':main()
