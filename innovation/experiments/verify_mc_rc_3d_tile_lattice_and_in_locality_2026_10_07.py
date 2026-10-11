"""Independent metadata replay plus a numeric counterexample to finite-local IN halos."""
import itertools,json,sys,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,read,sha,resource_guard,tile_plan,TaskUNet3D,torch,np
OUT=ROOT/'experiments/mc_rc_3d_tile_lattice_audit_2026_10_07'
def main():
    sys.stdout.reconfigure(encoding='utf-8');path=OUT/'independent_and_in_locality_attempt01.json';assert not path.exists()
    source=OUT/'attempt01.json';prod=read(source)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        source_sha256=sha(source),series=[],actual_mri_task_forwards=0,mr_or_label_values_loaded=0,
        actual_training_updates=0,actual_gpu_updates=0,confirmation_patients_opened=False,
        publication_claim_confirmed=False,mathematical_counterexample_only=True)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        resource_guard();assert prod['complete'] and not prod['errors']
        model=TaskUNet3D();factor=2**(len(model.encoders)-1);assert factor==prod['downsampling_factor']==8
        norms=[m for m in model.modules() if isinstance(m,torch.nn.InstanceNorm3d)]
        assert len(norms)==14 and all(not m.track_running_stats for m in norms)
        r['current_model_instance_norm_layers']=len(norms);r['uses_input_statistics_in_eval']=True
        for row in prod['series']:
            positions,axes=tile_plan(row['padded_shape_zrc']);assert axes==row['axis_starts']
            phases=np.asarray(positions,dtype=np.int64)%factor
            shifted=int(np.count_nonzero(np.any(phases!=0,axis=1)))
            assert shifted==row['tiles_not_on_origin_pooling_lattice']
            extras=row['right_high_padding_to_multiple8'];shape=[n+e for n,e in zip(row['padded_shape_zrc'],extras)]
            aligned,aligned_axes=tile_plan(shape);assert not np.any(np.asarray(aligned,dtype=np.int64)%factor)
            r['series'].append(dict(patient=row['patient'],uid=row['uid'],all_positions_verified=len(positions),
                nonaligned_positions_verified=shifted,aligned_preparation_all_positions_mod8_zero=True,
                aligned_candidate_tiles=len(aligned),all_axis_coverage_verified=all(
                    all(any(s<=v<s+p for s in axis) for v in range(n))
                    for n,p,axis in zip(row['padded_shape_zrc'],(64,128,128),axes))))
        assert sum(s['nonaligned_positions_verified'] for s in r['series'])==prod['total_nonaligned_tiles']
        # Same crop and all its local context, with a perturbation outside that crop.
        rng=np.random.default_rng(20261007);x=rng.normal(size=(8,8,8)).astype(np.float64);eps=1e-5
        crop=(slice(0,4),slice(0,4),slice(0,4));probe=(2,2,2);changed=x.copy();changed[7,7,7]+=20
        def norm(z):return (z-z.mean())/np.sqrt(z.var()+eps)
        before,after=norm(x),norm(changed);local_before,local_after=norm(x[crop]),norm(changed[crop])
        mu=x.mean();std=np.sqrt(x.var()+eps);i=probe;j=(7,7,7);n=x.size
        analytic=-1/(n*std)-(x[i]-mu)*(x[j]-mu)/(n*std**3)
        h=1e-5;plus=x.copy();minus=x.copy();plus[j]+=h;minus[j]-=h
        numeric=(norm(plus)[i]-norm(minus)[i])/(2*h)
        module=torch.nn.InstanceNorm3d(1,eps=eps,affine=False,track_running_stats=False).double().eval()
        with torch.inference_mode():reference=module(torch.from_numpy(x)[None,None]).numpy()[0,0]
        error=float(np.max(np.abs(reference-before)))
        counterexample=dict(shape=list(x.shape),crop_shape=list(x[crop].shape),probe=list(probe),
            perturbation_coordinate=list(j),outside_crop=True,inside_crop_input_max_difference=float(np.max(np.abs(x[crop]-changed[crop]))),
            local_norm_probe_change=float(local_after[i]-local_before[i]),
            full_norm_probe_change=float(after[i]-before[i]),
            numpy_vs_torch_float64_norm_max_error=error,analytic_remote_derivative=float(analytic),
            finite_difference_remote_derivative=float(numeric),derivative_absolute_error=float(abs(analytic-numeric)))
        r['counterexample']=counterexample;save()
        assert counterexample['inside_crop_input_max_difference']==counterexample['local_norm_probe_change']==0
        assert abs(counterexample['full_norm_probe_change'])>1e-3 and abs(analytic)>1e-5
        assert error<=1e-12 and abs(analytic-numeric)<=1e-8
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        r['complete']=len(r['series'])==19;r['resources_after']=resource_guard()
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','counterexample','cuda_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
