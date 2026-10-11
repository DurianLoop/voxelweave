"""Run the new resource worker on full-PATCH synthetic bundles, prohibiting MRI IO."""
import hashlib,json,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);at=time.perf_counter();reads=set();denied=[]
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        try:p=Path(args[0]).resolve()
        except (TypeError,ValueError,OSError):return
        mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT):
            rel=p.relative_to(ROOT).as_posix()
            if rel.startswith('data/') or p.name.endswith(('.zip','.nii','.nii.gz','.npz','.pt')) or 'mc_rc_validation' in rel or 'confirmation' in rel:
                denied.append(rel);raise PermissionError('Synthetic workflow prohibits MRI/weight IO: '+rel)
            reads.add(rel)
    sys.addaudithook(audit)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],synthetic_only=True,
        MRI_arrays_loaded=0,MRI_forwards=0,MRI_training_updates=0,GPU_forwards=0,publication_claim_confirmed=False,
        real19series_resource_qualification_completed=False,updated_weights_saved=False,task_effects_scored=False)
    path=OUT/'attempt01.json'
    def save():
        path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<5_000_000
    save()
    try:
        import mc_rc_3d_paired_resource_worker_2026_10_07 as w
        from qualify_mc_rc_3d_paired_sampling_fov_2026_10_07 import synthetic_fields
        from mc_rc_reference_resources_2026_10_07 import resource_guard
        w.torch.set_num_threads(4)
        def guard():
            assert time.perf_counter()-at<=600 and not w.torch.cuda.is_initialized()
            assert w.torch.get_num_threads()==4 and w.torch.get_num_interop_threads()==1
            v=resource_guard();v['cpu_threads']=4;return v
        r['resources_before']=guard()
        sources=[Path(__file__),ROOT/'MC_RC_3D_PAIRED_REAL_RESOURCE_ENTRY_PROTOCOL_2026-10-07.md',
            ROOT/'experiments/mc_rc_3d_paired_resource_worker_2026_10_07.py',ROOT/'experiments/run_mc_rc_3d_paired_real_resource_2026_10_07.py',
            ROOT/'experiments/mc_rc_3d_paired_sampling_fov_2026_10_07.py',ROOT/'experiments/mc_rc_3d_direct_observed_2026_10_07.py',
            ROOT/'experiments/qualify_mc_rc_3d_paired_sampling_fov_2026_10_07.py',ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py']
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources]
        for p in sources:(OUT/(p.name+'.source_snapshot')).write_bytes(p.read_bytes())
        fields,grid=synthetic_fields()
        b1=dict(dense=fields['dense'],numerator=fields['direct'],availability=fields['availability'],valid_grid=fields['valid'],
            target=fields['target'],grid=grid,native_shape_rcz=[33,35,17])
        dense2=(fields['dense']*.7+fields['valid']*.2).astype(w.np.float32)
        b2=dict(b1,dense=dense2,numerator=(dense2*fields['availability']).astype(w.np.float32))
        cache={'SYNTHETIC_UID_1':b1,'SYNTHETIC_UID_2':b2}
        original=[{k:w.array_sha(b[k]) for k in ('dense','numerator','availability','valid_grid','target')} for b in (b1,b2)]
        stream=[dict(step=i+1,round_index=i,patient='SYNTHETIC_PATIENT',uid=u) for i,u in enumerate(('SYNTHETIC_UID_1','SYNTHETIC_UID_2','SYNTHETIC_UID_1'))]
        r.update(frozen_stream=stream,synthetic_shape_zrc=list(fields['dense'].shape),patch=list(w.PATCH),batch_size=2,
            synthetic_grid=grid,native_shape_rcz=[33,35,17],input_array_sha256=original)
        w.run_workflow(cache,stream,'cpu',guard,save,r,'SYNTHETIC_UID_1')
        assert r['actual_resource_updates']==8 and r['completed_model_forward_calls']==24
        assert original==[{k:w.array_sha(b[k]) for k in ('dense','numerator','availability','valid_grid','target')} for b in (b1,b2)]
        assert not denied
        r.update(complete=True,input_arrays_not_mutated=True,resources_after=guard(),CUDA_initialized=False,
            io_audit=dict(workspace_read_paths=sorted(reads),denied_read_attempts=denied,MRI_data_reads=0),
            counts=dict(synthetic_updates=8,training_forward_calls=8,FOV_forward_calls=16,FOV_tiles=32),
            representative_FOV_only=True,all19series_MRI_resource_qualification_not_claimed=True)
    except Exception as e:
        r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-at;save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','actual_resource_updates','completed_model_forward_calls','elapsed_seconds','gate')}),flush=True)
    return 0 if r['complete'] and not r['errors'] else 1
if __name__=='__main__':raise SystemExit(main())
