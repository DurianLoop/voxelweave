"""Resolve public pinned Git tag via read-only advertisement after API rate limit."""
import sys,time,json,re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
from fetch_pinned_vinn_code import get
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter();out=HERE/'vinn_code_attempt02';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],records=[],requested_tag='v2.3.0',author_code_files_actually_read=0,author_code_imported=False,author_code_executed=False,
        tag_is_not_proven_exact_2022_paper_training_version=True,medical_arrays_loaded=0,CUDA_initialized=False)
    try:
        payload=get('https://github.com/Deep-MI/FastSurfer.git/info/refs?service=git-upload-pack',out/'git_advertisement.bin')
        pos=0;refs={};lines=[]
        while pos<len(payload):
            size=int(payload[pos:pos+4],16);pos+=4
            if size==0:continue
            assert size>=4 and pos+size-4<=len(payload)
            line=payload[pos:pos+size-4].split(b'\0')[0].decode('utf-8').strip();pos+=size-4;lines.append(line)
            m=re.fullmatch(r'([0-9a-f]{40}) (refs/[^ ]+)',line)
            if m:refs[m.group(2)]=m.group(1)
        assert 'refs/tags/v2.3.0' in refs
        commit=refs.get('refs/tags/v2.3.0^{}',refs['refs/tags/v2.3.0']);assert re.fullmatch('[0-9a-f]{40}',commit)
        r.update(pinned_commit=commit,tag_reference_SHA=refs['refs/tags/v2.3.0'],peeled_tag_commit_SHA=refs.get('refs/tags/v2.3.0^{}'))
        dump(out/'selected_refs.json',dict(selected_refs={k:v for k,v in refs.items() if k in ['refs/tags/v2.3.0','refs/tags/v2.3.0^{}']},advertisement=entry(out/'git_advertisement.bin')))
        paths=['FastSurferCNN/models/interpolation_layer.py','FastSurferCNN/models/networks.py','FastSurferCNN/models/sub_module.py','FastSurferCNN/data_loader/augmentation.py']
        def fetch(rel):
            q=dict(repo_path=rel,complete=False,errors=[],actual_source_reading_completed=False);dest=out/rel.replace('/','__');url='https://raw.githubusercontent.com/Deep-MI/FastSurfer/'+commit+'/'+rel
            try:get(url,dest);q.update(complete=True,url=url,source_binding=entry(dest))
            except Exception as e:q['errors'].append(type(e).__name__+': '+str(e))
            return q
        with ThreadPoolExecutor(max_workers=2) as pool:r['records']=list(pool.map(fetch,paths))
        r['errors']=[e for q in r['records'] for e in q['errors']];r['complete']=all(q['complete'] for q in r['records'])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e))
    r.update(elapsed_seconds=time.perf_counter()-started,source_bindings=[entry(p) for p in [Path(__file__),HERE/'fetch_pinned_vinn_code.py',HERE/'AUTHOR_CODE_READ_PROTOCOL.md',HERE/'AUTHOR_CODE_GIT_ADVERTISEMENT_PROTOCOL.md']]);dump(out/'receipt.json',r)
    assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<2_000_000 and time.perf_counter()-started<180
    print(json.dumps(r),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
