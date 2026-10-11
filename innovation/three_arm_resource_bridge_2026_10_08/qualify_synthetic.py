"""Qualify new three-arm workflow on artificial observed inputs with full PATCH."""
import hashlib,json,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
OUT=HERE/'synthetic_attempt01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);tick=time.perf_counter();reads=set();denied=[]
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        try:p=Path(args[0]).resolve()
        except (TypeError,ValueError,OSError):return
        mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT.parent):
            if p.is_relative_to(ROOT):rel=p.relative_to(ROOT).as_posix()
            else:rel=p.relative_to(ROOT.parent).as_posix()
            if rel.startswith('data/') or p.name.endswith(('.zip','.nii','.nii.gz','.npy','.npz','.pt')) or 'mc_rc_validation' in rel or 'confirmation' in rel:
                denied.append(rel);raise PermissionError('Synthetic qualification prohibits medical/weight IO: '+rel)
            reads.add(rel)
    sys.addaudithook(audit)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],synthetic_only=True,
        medical_arrays_loaded=0,prediction_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,
        MRI_forwards=0,MRI_training_updates=0,GPU_forwards=0,head_fits=0,new_papers_read=0,
        real19series_resource_qualification_completed=False,updated_weights_saved=False,task_effects_scored=False,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
    path=OUT/'receipt.json'
    def save():
        path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<10_000_000
    save()
    try:
        import three_arm_resource_worker as w
        from synthetic_case import fixture
        from mc_rc_reference_resources_2026_10_07 import resource_guard
        w.torch.set_num_threads(4)
        def guard():
            assert time.perf_counter()-tick<=600 and not w.torch.cuda.is_initialized()
            assert w.torch.get_num_threads()==4 and w.torch.get_num_interop_threads()==1
            v=resource_guard();v['cpu_threads']=4;return v
        sources=([Path(__file__),HERE/'PROTOCOL.md',HERE/'three_arm_resource_worker.py',HERE/'synthetic_case.py']+
            [ROOT/'experiments'/name for name in ('mc_rc_3d_paired_resource_worker_2026_10_07.py',
                'mc_rc_3d_paired_sampling_fov_2026_10_07.py','mc_rc_3d_direct_observed_2026_10_07.py',
                'mc_rc_common_projected_observed_2026_10_08.py','mc_rc_reference_resources_2026_10_07.py',
                'mc_rc_3d_baseline_v2_2026_10_07.py','mc_rc_3d_baseline_2026_10_07.py')])
        r['source_bindings']=[entry(p) for p in sources]
        for i,p in enumerate(sources):
            with (OUT/(str(i).zfill(2)+'_'+p.name+'.source_snapshot')).open('xb') as f:f.write(p.read_bytes())
        r['resources_before']=guard();cache={};factory=[]
        for which in (1,2):
            observed,grid,target=fixture(which);fields,st,meta=w.three_fields(observed,grid)
            assert fields['dense'].shape==(68,132,136)
            uid='SYNTHETIC_UID_'+str(which);cache[uid]=dict(**fields,target=target,grid=grid,native_shape_rcz=[33,35,17])
            factory.append(dict(uid=uid,observed_source_sha256=w.array_sha(observed.pixels),statistics=st,input_factory_metadata=meta,
                array_sha256={k:w.array_sha(cache[uid][k]) for k in w.FIELDS}))
        r['factory_records']=factory
        stream=[dict(step=i+1,round_index=i,patient='SYNTHETIC_PATIENT',uid=uid)
            for i,uid in enumerate(('SYNTHETIC_UID_1','SYNTHETIC_UID_2','SYNTHETIC_UID_1'))]
        r.update(frozen_stream=stream,synthetic_shape_zrc=[68,132,136],patch=list(w.PATCH),batch_size=2,
            synthetic_grid=grid,native_shape_rcz=[33,35,17])
        try:w.arm_view(cache['SYNTHETIC_UID_1'],'unknown')
        except ValueError:r['unknown_arm_rejected']=True
        else:raise AssertionError('Unknown arm accepted')
        w.run_workflow(cache,stream,'cpu',guard,save,r,'SYNTHETIC_UID_1')
        assert r['actual_resource_updates']==12 and r['completed_model_forward_calls']==36
        assert all({k:w.array_sha(cache[v['uid']][k]) for k in w.FIELDS}==v['array_sha256'] for v in factory)
        for a in r['arms']:
            for b in r['arms']:
                if a['kind']!=b['kind']:assert any(x['input_batch_sha256']!=y['input_batch_sha256'] for x,y in zip(a['history'],b['history']))
        assert not denied
        r.update(complete=True,input_arrays_not_mutated=True,all_three_branch_batch_hashes_distinct=True,
            resources_after=guard(),CUDA_initialized=False,io_audit=dict(workspace_read_paths=sorted(reads),denied_read_attempts=denied),
            counts=dict(synthetic_updates=12,training_forward_calls=12,FOV_forward_calls=24,FOV_tiles=48),
            representative_FOV_only=True,all19series_MRI_resource_qualification_not_claimed=True)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-tick;save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','actual_resource_updates','completed_model_forward_calls','elapsed_seconds','gate')},ensure_ascii=False),flush=True)
    return int(not r['complete'] or bool(r['errors']))

if __name__=='__main__':raise SystemExit(main())
