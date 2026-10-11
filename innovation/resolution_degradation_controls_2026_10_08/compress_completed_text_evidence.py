"""Transparent NTFS compression of exactly the verified offline text subset, preserving frozen bytes."""
import sys,time,json,gzip,ctypes,subprocess,hashlib,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
from probe_transparent_storage import physical_size,attributes


def eligible(p):
    if not p.is_relative_to(ROOT) or p.is_relative_to(HERE) or p.suffix not in ['.json','.txt','.html']:return False
    parts=p.relative_to(ROOT).parts
    if parts[0] in ['data','tools','experiments','spatial_adaptation_matched_2026_10_08'] or any('training_attempt' in x for x in parts):return False
    paper=p.is_relative_to(ROOT/'literature/extracted') or p.is_relative_to(ROOT/'literature/search_snapshots')
    evidence=any(s in p.name.upper() for s in ['ARCHIVE_MANIFEST','APPEND_INDEX','TOOL_OBSERVATIONS','READING_PROVENANCE','VISIBLE_DIALOGUE'])
    return bool(paper or evidence)


def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before_resources=resource_guard()
    journal=HERE/'full_real_pipeline_attempt01/fields.jsonl.gz'
    def guard():
        resource_guard();assert time.perf_counter()-started<300
        size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        assert size+max(0,1_500_000-journal.stat().st_size)+150_000+100_000+25_000<5_000_000
    guard();index=HERE/'APPEND_INDEX.json'
    assert sha(index)=='b22589f518e68e358a46bf9bca3893e6fa470b5cca34b0e95152f6c9fa8fd69b'
    q=read(index);assert q['complete'] and q['cumulative_frozen_evidence_files']==6376
    chain=q['prior_chain']+[entry(index)];allrows=[]
    for b in chain:
        p=bind(b);v=read(p);allrows.extend(v.get('evidence_files',v.get('new_evidence_files',[])))
    frozen={b['path']:b for b in allrows};assert len(frozen)==6376
    selected=[]
    for b in frozen.values():
        p=(ROOT/b['path']).resolve()
        if not eligible(p) or not p.is_file():continue
        size=p.stat().st_size
        if not(131072<=size<=4000000):continue
        attrs=attributes(p)
        if attrs&(0x1|0x800|0x4000|0x200):continue
        bind(b)
        selected.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=size,sha256=b['sha256'],before_attributes=attrs,before_physical_bytes=physical_size(p)))
    selected.sort(key=lambda b:(-b['bytes'],b['path']))
    assert len(selected)==29 and sum(b['bytes'] for b in selected)==28116603
    assert sum(b['bytes'] for b in selected)<30_000_000
    out=HERE/'completed_text_compression_attempt01';out.mkdir(exist_ok=False)
    plan=out/'planned_targets.json.gz'
    with plan.open('xb') as f:f.write(gzip.compress((json.dumps(selected,ensure_ascii=False,indent=2)+'\n').encode('utf-8'),mtime=0))
    r=dict(complete=False,errors=[],files=[],planned_files=29,logical_bytes=28116603,
           source_content_and_paths_unchanged_required=True,metadata_compression_attribute_only_changed=True,
           MRI_data_files_touched=False,model_files_touched=False,live_outputs_touched=False,
           other_PIDs_enumerated=False,other_PIDs_modified=False,confirmation_patients_opened=False,
           planned_targets=entry(plan),resources_before=before_resources,new_medical_effects=0,
           publication_claim_confirmed=False,goal_status='active')
    for i,b in enumerate(selected,1):
        guard();p=bind(b);assert eligible(p) and p.resolve().is_relative_to(ROOT)
        result=subprocess.run(['compact.exe','/C','/I','/Q',str(p.resolve())],capture_output=True,text=True,timeout=20)
        assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256'],'Frozen logical content changed'
        attrs=attributes(p);physical=physical_size(p)
        v=dict(source_binding={k:b[k] for k in ['path','bytes','sha256']},
            compact_exit=result.returncode,compressed=bool(attrs&0x800),
            before_attributes=b['before_attributes'],after_attributes=attrs,
            before_physical_bytes=b['before_physical_bytes'],after_physical_bytes=physical,
            physical_bytes_saved=b['before_physical_bytes']-physical,logical_content_verified_unchanged=True)
        if result.returncode or not v['compressed']:
            v.update(stdout=result.stdout,stderr=result.stderr);r['errors'].append(dict(path=b['path'],error='compact failed or compressed attribute absent'))
        r['files'].append(v)
        if i%5==0 or i==len(selected):print(json.dumps(dict(files_processed=i,planned_files=len(selected),physical_bytes_saved_so_far=sum(x['physical_bytes_saved'] for x in r['files']))),flush=True)
    r.update(complete=len(r['files'])==29 and not r['errors'],all29_frozen_logical_bytes_and_hashes_verified=True,
             physical_bytes_saved=sum(x['physical_bytes_saved'] for x in r['files']),
             resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started,
             source_bindings=[entry(p) for p in [Path(__file__),HERE/'COMPLETED_TEXT_TRANSPARENT_COMPRESSION_PROTOCOL_TURN29.md',
                 HERE/'probe_transparent_storage.py',HERE/'transparent_storage_probe_attempt01/receipt.json',index]])
    dump(out/'receipt.json',r);guard()
    print(json.dumps({k:v for k,v in r.items() if k not in ['files','source_bindings']}),flush=True)
    return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
