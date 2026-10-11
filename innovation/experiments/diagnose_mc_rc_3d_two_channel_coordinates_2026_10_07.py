"""Synthetic-only separate ideal and float32 coordinate interpretations; no gate replacement."""
import gc,hashlib,json,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from mc_rc_3d_paired_sampling_fov_2026_10_07 import infer_two_channel_full_fov,torch,F,array_sha
from qualify_mc_rc_3d_paired_sampling_fov_2026_10_07 import synthetic_fields
from mc_rc_3d_direct_observed_2026_10_07 import ROOT,sha,read,two_channel_model
from mc_rc_reference_resources_2026_10_07 import resource_guard
OUT=ROOT/'experiments/mc_rc_3d_two_channel_coordinate_diagnostic_2026_10_07'
PRIMARY=ROOT/'experiments/mc_rc_3d_paired_sampling_fov_qualification_2026_10_07/attempt01.json'

def native_numpy(physical,shape,dtype):
    nz,nr,nc=physical.shape;physical=physical.astype(dtype)
    indices=[];weights=[]
    for n,m in ((nz,shape[2]),(nr,shape[0]),(nc,shape[1])):
        scale=dtype(n/m);coord=(np.arange(m,dtype=dtype)+dtype(.5))*scale-dtype(.5)
        coord=np.clip(coord,dtype(0),dtype(n-1));lo=np.floor(coord).astype(int);hi=np.minimum(lo+1,n-1)
        fraction=coord-lo.astype(dtype);indices.append((lo,hi));weights.append((dtype(1)-fraction,fraction))
    out=np.empty(shape,dtype=dtype)
    for z in range(shape[2]):
        plane=np.zeros(shape[:2],dtype=dtype)
        for a in (0,1):
            for b in (0,1):
                for c in (0,1):
                    v=physical[indices[0][a][z]][np.ix_(indices[1][b],indices[2][c])]
                    plane+=v*weights[0][a][z]*weights[1][b][:,None]*weights[2][c][None,:]
        out[:,:,z]=plane
    return out

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);start=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],arms=[],script_sha256=sha(__file__),
        actual_MRI_forwards=0,actual_MRI_training_updates=0,actual_training_updates=0,actual_GPU_forwards=0,
        confirmation_patients_opened=False,publication_claim_confirmed=False,original_56FOV_protocol_changed=False)
    path=OUT/'attempt01.json';reads=set();denied=[]
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        try:p=Path(args[0]).resolve()
        except (ValueError,OSError,TypeError):return
        mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT):
            rel=p.relative_to(ROOT).as_posix()
            if rel.startswith('data/') or p.name.endswith(('.zip','.nii','.nii.gz')) or 'mc_rc_validation' in rel or 'confirmation' in rel:
                denied.append(rel);raise PermissionError('Synthetic coordinate diagnosis prohibits MRI reads: '+rel)
            reads.add(rel)
    sys.addaudithook(audit)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-start<=600
        v=resource_guard();assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
        size=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file());assert size<=25_000_000
        v.update(cpu_threads=4,stage_saved_bytes=size,stage_saved_limit=25_000_000);return v
    save()
    try:
        torch.set_num_threads(4);r['resources_before']=guard();q=read(PRIMARY);assert q['complete'] and not q['errors']
        previous=read(ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json')
        cp_record=next(a for a in previous['synthetic_arms'] if a['kind']=='direct')['checkpoint'];cp_path=ROOT/cp_record['file']
        assert sha(cp_path)==cp_record['sha256'];cp=torch.load(cp_path,map_location='cpu',weights_only=False)
        model=two_channel_model(cp['model']);fields,grid=synthetic_fields();shape=q['synthetic_input']['native_shape_rcz']
        sources=[PRIMARY,cp_path,Path(__file__),ROOT/'MC_RC_3D_TWO_CHANNEL_COORDINATE_DIAGNOSTIC_PROTOCOL_2026-10-07.md',
            ROOT/'experiments/qualify_mc_rc_3d_paired_sampling_fov_2026_10_07.py',ROOT/'experiments/mc_rc_3d_paired_sampling_fov_2026_10_07.py',
            ROOT/'experiments/mc_rc_3d_direct_observed_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',
            ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py']
        sources.extend(ROOT/a['synthetic_probability_file'] for a in q['FOV_checks'])
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources]
        for kind in ('dense','direct'):
            guard();a=next(a for a in q['FOV_checks'] if a['kind']==kind)
            native,physical,meta=infer_two_channel_full_fov(model,fields[kind],fields['availability'],grid,shape)
            old=np.load(ROOT/a['synthetic_probability_file'],allow_pickle=False)
            assert np.array_equal(native,old) and meta==a['production']
            ideal64=native_numpy(physical,shape,np.float64);ideal=ideal64.astype(np.float32)
            f32=native_numpy(physical,shape,np.float32)
            with torch.inference_mode():
                reference64=F.interpolate(torch.from_numpy(physical.astype(np.float64))[None,None],
                    size=(shape[2],shape[0],shape[1]),mode='trilinear',align_corners=False)[0,0].numpy().transpose(1,2,0)
            ideal_error=float(np.max(np.abs(native-ideal)));ideal_binary=int(np.count_nonzero((native>=.5)!=(ideal>=.5)))
            f32_error=float(np.max(np.abs(native-f32)));f32_binary=int(np.count_nonzero((native>=.5)!=(f32>=.5)))
            double_error=float(np.max(np.abs(reference64-ideal64)));double_binary=int(np.count_nonzero((reference64>=.5)!=(ideal64>=.5)))
            assert ideal_error==a['native_max_abs_error'] and ideal_binary==a['threshold_disagreements']
            filename=OUT/(kind+'_synthetic_physical_probability.npy');np.save(filename,physical,allow_pickle=False)
            record=dict(kind=kind,primary_native_probability_replayed_bitwise=True,primary_physical_probability_sha256=array_sha(physical),
                original_ideal_coordinate_max_abs_error=ideal_error,original_ideal_coordinate_threshold_disagreements=ideal_binary,
                original_ideal_coordinate_absolute_gate=ideal_error<=3e-6 and ideal_binary==0,
                float32_coordinate_max_abs_error=f32_error,float32_coordinate_threshold_disagreements=f32_binary,
                float32_coordinate_replay_gate=f32_error<=3e-6 and f32_binary==0,
                float64_coordinate_max_abs_error=double_error,float64_coordinate_threshold_disagreements=double_binary,
                float64_coordinate_only_gate=double_error<=3e-12 and double_binary==0,
                physical_probability_file=filename.relative_to(ROOT).as_posix(),physical_probability_file_sha256=sha(filename),
                float32_only_coordinate_arithmetic=True,neural_forward_precision='float32',full_FOV_tiles=8)
            r['arms'].append(record);save();del native,physical,old,ideal64,ideal,f32,reference64;gc.collect()
        assert not denied
        r['io_audit']=dict(workspace_read_paths=sorted(reads),prohibited_access_attempts=denied,MRI_arrays_read=0)
        r['all_float32_and_float64_coordinate_replays_passed']=all(a['float32_coordinate_replay_gate'] and a['float64_coordinate_only_gate'] for a in r['arms'])
        r['all_original_ideal_absolute_gates_passed']=all(a['original_ideal_coordinate_absolute_gate'] for a in r['arms'])
        r['resources_after']=guard();r['complete']=True
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-start;save()
    print(json.dumps(dict(complete=r['complete'],errors=r['errors'],arms=r['arms'],
        all_coordinate_replays_passed=r.get('all_float32_and_float64_coordinate_replays_passed'),elapsed_seconds=r['elapsed_seconds']),ensure_ascii=False))
    return int(not r['complete'] or not r.get('all_float32_and_float64_coordinate_replays_passed',False))
if __name__=='__main__':raise SystemExit(main())
