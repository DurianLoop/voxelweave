"""Separate inventory/compression of immutable non-current qualification checkpoints; preserve all bytes."""
import json,sys,time,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'resource_recovery_and_generalization_controls_2026_10_09'))
from inventory_frozen_text_storage import physical
def main():
    started=time.perf_counter();mode=sys.argv[1];assert mode in ['inventory','compress']
    def guard():
        r=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        assert time.perf_counter()-started<300 and size<2_000_000
        assert r['workspace_free_bytes']-40_800_000-(2_000_000-size)>=8_000_000_000
        return r
    before=guard();index=ROOT/'action_oracle_and_prior_art_2026_10_09/APPEND_INDEX.json'
    assert sha(index)=='6a78df3186809768867f5454466efb6f011ed20089cbc94aee7af943fd0698d4'
    v=read(index);assert v['complete'] and v['cumulative_frozen_evidence_files']==7291
    if mode=='inventory':
        rows=[]
        for b in v['prior_chain']+[entry(index)]:
            q=read(bind(b));assert q['complete'] and not q['errors'];rows.extend(q.get('evidence_files',q.get('new_evidence_files',[])))
        assert len(rows)==len({b['path'] for b in rows})==7291
        current=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json')
        excluded={(ROOT/a['checkpoint_path']).resolve() for a in current['arms']}
        targets=[]
        for b in rows:
            p=(ROOT/b['path']).resolve()
            if not p.is_relative_to(ROOT) or p.is_relative_to(ROOT/'tools') or p in excluded or p.suffix!='.pt':continue
            s=physical(p)
            if s['compressed'] or s['attributes']&(0x1|0x200|0x400|0x4000):continue
            targets.append(dict(source_binding=b,storage_before=s))
        targets.sort(key=lambda x:x['source_binding']['bytes'],reverse=True);targets=targets[:40]
        for t in targets:bind(t['source_binding']);guard()
        out=HERE/'inventory_attempt01';out.mkdir(exist_ok=False)
        r=dict(complete=True,errors=[],known_frozen_files=7291,read_only_inventory=True,compression_executed=False,
            current_two_parent_checkpoints_excluded=True,targets=targets,selected_files=len(targets),
            selected_logical_bytes=sum(t['source_binding']['bytes'] for t in targets),model_arrays_deserialized=0,
            source_bindings=[entry(p) for p in [Path(__file__),HERE/'PROTOCOL.md',index]],resources_before=before,resources_after=guard())
    else:
        ip=HERE/'inventory_attempt01/receipt.json';inventory=read(ip);assert inventory['complete'] and not inventory['compression_executed']
        targets=inventory['targets'];assert targets and len(targets)<=40
        for t in targets:assert physical(bind(t['source_binding']))==t['storage_before'];guard()
        out=HERE/'compression_attempt01';out.mkdir(exist_ok=False)
        dump(out/'frozen_config.json',dict(inventory=entry(ip),targets=targets,source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md')]))
        r=dict(complete=False,errors=[],files=[],planned_files=len(targets),compression_executed=True,model_arrays_deserialized=0,
            source_bindings=[entry(ip),entry(out/'frozen_config.json')])
        try:
            for t in targets:
                guard();p=bind(t['source_binding']);assert physical(p)==t['storage_before']
                call=subprocess.run(['compact.exe','/C','/I','/Q',str(p)],capture_output=True,text=True,errors='replace',timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
                after=physical(p);same=sha(p)==t['source_binding']['sha256'] and p.stat().st_size==t['source_binding']['bytes']
                r['files'].append(dict(source_binding=t['source_binding'],storage_before=t['storage_before'],storage_after=after,
                    compact_exit=call.returncode,logical_bytes_and_SHA_unchanged=same,API_physical_bytes_saved=t['storage_before']['physical_bytes']-after['physical_bytes'],
                    stdout=call.stdout,stderr=call.stderr))
                assert call.returncode==0 and after['compressed'] and same
                if len(r['files'])%10==0:print(json.dumps(dict(files_processed=len(r['files']),API_saved_bytes=sum(v['API_physical_bytes_saved'] for v in r['files']))),flush=True)
            r['complete']=True
        except Exception as e:r['errors'].append(dict(type=type(e).__name__,message=str(e)))
        r.update(files_processed=len(r['files']),API_physical_bytes_saved=sum(v['API_physical_bytes_saved'] for v in r['files']),
            all_selected_logical_SHA_unchanged=r['complete'],resources_before=before,resources_after=guard())
    r.update(elapsed_seconds=time.perf_counter()-started,logical_source_contents_modified=False,source_paths_changed=False,
        files_deleted_or_moved=False,other_PIDs_enumerated=False,other_PIDs_modified=False,original_training_modified=False,
        publication_claim_confirmed=False,goal_status='active')
    dump(out/'receipt.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ['targets','files','source_bindings']}))
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
