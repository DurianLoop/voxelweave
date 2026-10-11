"""Separate immutable inventory and transparent compression of prior6997 text only."""
import sys,time,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'resource_recovery_and_generalization_controls_2026_10_09'))
from inventory_frozen_text_storage import sha,entry,dump,physical,EXTENSIONS
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,bind,read

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();mode=sys.argv[1];assert mode in ['inventory','compress']
    def guard():
        r=resource_guard();assert time.perf_counter()-started<300
        assert r['workspace_free_bytes']-11_800_000>=8_000_000_000
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000;return r
    before=guard();prev=ROOT/'resource_recovery_and_generalization_controls_2026_10_09'
    index=prev/'APPEND_INDEX.json';proof=prev/'APPEND_PROOF.json'
    assert sha(index)=='af51442f0daab1459e40de7a17ca6c0332ca1aa206a7a05f0def71a9a016a4bf'
    assert sha(proof)=='6b3d95d59b2eb8ee6075c5db04b16101808b2eb69c5540b26a8207a9f13614d2'
    if mode=='inventory':
        q=read(index);assert q['complete'] and q['cumulative_frozen_evidence_files']==6997
        rows=[]
        for b in q['prior_chain']+[entry(index)]:rows.extend(read(bind(b)).get('evidence_files',read(ROOT/b['path']).get('new_evidence_files',[])))
        assert len(rows)==len({b['path'] for b in rows})==6997
        selected=[]
        for b in rows:
            p=(ROOT/b['path']).resolve()
            if p.suffix.lower() not in EXTENSIONS or b['bytes']<4096 or p.is_relative_to(ROOT/'tools'):continue
            if not p.is_relative_to(ROOT):continue
            state=physical(p)
            if state['compressed'] or state['attributes']&(0x1|0x200|0x4000|0x400):continue
            selected.append(dict(source_binding=b,absolute_path=str(p),storage_before=state))
        selected.sort(key=lambda x:x['source_binding']['bytes'],reverse=True);selected=selected[:1000]
        for row in selected:bind(row['source_binding']);guard()
        out=HERE/'inventory_attempt01';out.mkdir(exist_ok=False)
        result=dict(complete=True,errors=[],known_frozen_files=6997,read_only_inventory=True,targets=selected,
            selected_files=len(selected),selected_logical_bytes=sum(x['source_binding']['bytes'] for x in selected),compression_executed=False,
            source_bindings=[entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',index,proof]],resources_before=before,resources_after=guard())
    else:
        inventory=HERE/'inventory_attempt01/receipt.json';v=read(inventory);assert v['complete'] and not v['compression_executed']
        targets=v['targets'];assert targets and len(targets)<=1000
        for row in targets:
            p=bind(row['source_binding']);assert physical(p)==row['storage_before'];guard()
        out=HERE/'compression_attempt01';out.mkdir(exist_ok=False)
        dump(out/'frozen_config.json',dict(inventory=entry(inventory),targets=targets,source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md')]))
        result=dict(complete=False,errors=[],files=[],planned_files=len(targets),compression_executed=True,source_bindings=[entry(inventory),entry(out/'frozen_config.json')])
        try:
            for target in targets:
                guard();p=bind(target['source_binding']);assert physical(p)==target['storage_before']
                call=subprocess.run(['compact.exe','/C','/I','/Q',str(p)],capture_output=True,text=True,errors='replace',timeout=30)
                unchanged=p.stat().st_size==target['source_binding']['bytes'] and sha(p)==target['source_binding']['sha256'];after=physical(p)
                result['files'].append(dict(source_binding=target['source_binding'],storage_before=target['storage_before'],storage_after=after,
                    compact_exit=call.returncode,logical_bytes_and_SHA_unchanged=unchanged,API_physical_bytes_saved=target['storage_before']['physical_bytes']-after['physical_bytes'],
                    stdout=call.stdout,stderr=call.stderr))
                assert unchanged and call.returncode==0 and after['compressed']
                if len(result['files'])%100==0:print(json.dumps(dict(processed=len(result['files']),planned=len(targets),API_saved_bytes=sum(x['API_physical_bytes_saved'] for x in result['files']))),flush=True)
            result['complete']=True
        except Exception as exc:result['errors'].append(dict(type=type(exc).__name__,message=str(exc)))
        result.update(files_processed=len(result['files']),API_physical_bytes_saved=sum(x['API_physical_bytes_saved'] for x in result['files']),
            all_selected_logical_SHA_unchanged=result['complete'],resources_before=before,resources_after=guard())
    result.update(elapsed_seconds=time.perf_counter()-started,source_logical_bytes_or_paths_modified=False,MRI_model_or_live_files_selected=False,
        other_PIDs_enumerated=False,other_PIDs_modified=False,publication_claim_confirmed=False,goal_status='active')
    dump(out/'receipt.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['targets','files','source_bindings']},ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
