"""Two bounded public reads from a paper-linked author repository; no Git commands."""
import sys,json,ssl,time,re
from pathlib import Path
from urllib.request import Request,build_opener,ProxyHandler,HTTPSHandler
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    out=HERE/'lesion_ranker_entry_attempt01';out.mkdir(exist_ok=False)
    repository='https://github.com/Pediatric-Accelerated-Intelligence-Lab/BraTS-Unofficial-Ranker'
    result=dict(complete=False,errors=[],records=[],repository=repository,actually_read=False,author_code_executed=False,
                medical_arrays_loaded=0,new_distinct_primary_maintexts_completed=0,new_patient_medical_effects=0)
    def get(url,name):
        assert url.startswith('https://');ctx=ssl.create_default_context()
        assert ctx.check_hostname and ctx.verify_mode==ssl.CERT_REQUIRED
        opener=build_opener(ProxyHandler({}),HTTPSHandler(context=ctx))
        with opener.open(Request(url,headers={'User-Agent':'MRI-public-source-read/1.0'}),timeout=30) as response:
            assert response.geturl().startswith('https://');body=response.read(200001);assert len(body)<=200000
            dump(out/(name+'.headers.json'),dict(requested_url=url,effective_url=response.geturl(),status=response.status,headers=dict(response.headers)))
        dest=out/name
        with dest.open('xb') as f:f.write(body)
        result['records'].append(dict(url=url,source_binding=entry(dest)))
        return body
    try:
        payload=get(repository+'.git/info/refs?service=git-upload-pack','git_advertisement.bin')
        pos=0;refs={}
        while pos<len(payload):
            size=int(payload[pos:pos+4],16);pos+=4
            if size==0:continue
            assert size>=4 and pos+size-4<=len(payload)
            line=payload[pos:pos+size-4].split(b'\0')[0].decode('utf-8').strip();pos+=size-4
            m=re.fullmatch(r'([0-9a-f]{40}) (HEAD|refs/[^ ]+)',line)
            if m:refs[m[2]]=m[1]
        commit=refs['HEAD'];assert re.fullmatch('[0-9a-f]{40}',commit)
        result.update(pinned_commit=commit,advertised_matching_branches={k:v for k,v in refs.items() if k.startswith('refs/heads/') and v==commit})
        get('https://raw.githubusercontent.com/Pediatric-Accelerated-Intelligence-Lab/BraTS-Unofficial-Ranker/'+commit+'/README.md','README_source.md')
        result['complete']=True
    except Exception as exc:result['errors'].append(type(exc).__name__+': '+str(exc))
    result.update(elapsed_seconds=time.perf_counter()-started,source_bindings=[entry(p) for p in [Path(__file__),HERE/'LESION_RANKER_SOURCE_PROTOCOL.md',ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/lesion_html_attempt01/blocks.json']])
    dump(out/'receipt.json',result);resource_guard()
    assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<400000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000 and time.perf_counter()-started<90
    print(json.dumps(result),flush=True);return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
