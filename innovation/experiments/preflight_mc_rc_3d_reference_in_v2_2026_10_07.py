"""Label/native-free CPU qualification of reference-statistics IN; no task-effect endpoint."""
import json,sys,time,traceback,zipfile
from datetime import datetime,timezone
import nibabel
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,observed_package,lattice,physical_mr,torch,np,SEED)
from mc_rc_observed_only_training_input import reconstruct,stats
from mc_rc_3d_independent_replay_2026_10_07 import functional_forward
from mc_rc_3d_reference_instance_norm_v2_2026_10_07 import reference_statistics_forward,reference_norm
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_reference_in_preflight_v2_2026_10_07'
def compare(a,b):
    return dict(probability_max_absolute_error_by_head=[float((x.sigmoid()-y.sigmoid()).abs().max()) for x,y in zip(a,b)],
                prediction_disagreements_by_head=[int(((x>=0)!=(y>=0)).sum()) for x,y in zip(a,b)])
def check_self(reference,state,persist):
    with torch.inference_mode():
        ordinary=functional_forward(reference,state)
        candidate,baseline=reference_statistics_forward(reference,reference,state)
    r=compare(candidate,ordinary);q=compare(baseline,ordinary)
    persist(dict(shape=list(reference.shape),candidate_self_replay=r,reference_stream_replay=q))
    assert max(r['probability_max_absolute_error_by_head'])<=3e-6 and r['prediction_disagreements_by_head']==[0,0,0]
    assert q['probability_max_absolute_error_by_head']==[0,0,0] and q['prediction_disagreements_by_head']==[0,0,0]
    return dict(shape=list(reference.shape),candidate_self_replay=r,reference_stream_replay=q)
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt01.json';started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],self_replays=[],
           script_sha256=sha(__file__),protocol_sha256=sha(ROOT/'MC_RC_3D_REFERENCE_IN_PREFLIGHT_PROTOCOL_2026-10-07.md'),
           source_bindings=[],observations_before_assertions=[],primitive_checks=[],actual_training_updates=0,actual_gpu_updates=0,scientific_confirmation_patients=0,
           ground_truth_pixels_opened=False,native_hidden_mri_pixels_opened=False,task_effect_endpoint_computed=False,
           validation_effects_opened=False,confirmation_patients_opened=False,publication_claim_confirmed=False)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def persist(observation):
        r['observations_before_assertions'].append(observation);save()
    def guard():
        assert time.perf_counter()-started<=360
        return resource_guard()
    def deny_patient_pixel_load(*args,**kwargs):raise AssertionError('Native ZIP or NIfTI/GT pixel reader forbidden in preflight')
    save()
    try:
        r['resources_before']=guard()
        # These public APIs are not needed for reading the approved observed NPZ.
        nibabel.load=deny_patient_pixel_load;zipfile.ZipFile=deny_patient_pixel_load
        prodpath=ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/attempt_01.json';prod=read(prodpath)
        assert prod['complete'] and not prod['errors']
        base=next(a for a in prod['arms'] if a['kind']=='raw_pchip')
        cp=ROOT/base['checkpoint_file'];assert sha(cp)==base['checkpoint_sha256']
        state=torch.load(cp,map_location='cpu',weights_only=True)['state_dict']
        assert state_hash(state)==base['final_weights_sha256']
        sources=[cp,prodpath,ROOT/'MC_RC_3D_REFERENCE_IN_PREFLIGHT_PROTOCOL_2026-10-07.md',
                 ROOT/'experiments/mc_rc_3d_reference_instance_norm_v2_2026_10_07.py',
                 ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py',
                 ROOT/'experiments/mc_rc_observed_only_training_input.py',
                 ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py']
        sources += [ROOT/'MC_RC_3D_REFERENCE_IN_NUMERICAL_ADDENDUM_V2_2026-10-07.md',ROOT/'experiments/mc_rc_3d_reference_in_preflight_2026_10_07/attempt01.json',ROOT/'experiments/prepare_reference_in_preflight_v2_2026_10_07.py']
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources]
        primitive_rng=torch.Generator().manual_seed(SEED+1)
        for shape in ((2,4,8,8,8),(1,3,4,4,4)):
            ref=torch.randn(shape,generator=primitive_rng)
            cand=ref*.7+torch.randn(shape,generator=primitive_rng)*.2+1.7
            gamma=torch.linspace(.8,1.4,shape[1]);beta=torch.linspace(-.3,.2,shape[1])
            with torch.inference_mode():actual,_=reference_norm(cand,ref,gamma,beta)
            nr=ref.numpy().astype(np.float64);nc=cand.numpy().astype(np.float64)
            mean=nr.mean(axis=(2,3,4),keepdims=True);var=nr.var(axis=(2,3,4),keepdims=True)
            expected=(nc-mean)/np.sqrt(var+1e-5)*gamma.numpy()[None,:,None,None,None]+beta.numpy()[None,:,None,None,None]
            error=float(np.max(np.abs(actual.numpy()-expected)))
            check=dict(shape=list(shape),non_identical_inputs=True,max_absolute_error=error,rtol=2e-5,atol=3e-6)
            r['primitive_checks'].append(check);save()
            assert np.allclose(actual.numpy(),expected,rtol=2e-5,atol=3e-6)
        generator=torch.Generator().manual_seed(SEED)
        for shape in ((2,1,16,16,16),(1,1,32,32,32)):
            guard();synthetic=torch.randn(shape,generator=generator);r['self_replays'].append(check_self(synthetic,state,persist));save()
        role,case,row=fixed_cases()[0];assert role=='development' and case['patient']=='VS-MC-RC-001'
        observed=observed_package(case,row);st=stats(observed.pixels);grid=lattice(case)
        pc=reconstruct(observed,'raw_pchip');linear=reconstruct(observed,'raw_linear')
        assert np.array_equal(pc[:,:,observed.indices],observed.pixels) and np.array_equal(linear[:,:,observed.indices],observed.pixels)
        normalized_pc=((pc.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
        assert array_sha(normalized_pc)==row['inputs']['raw_pchip_observed_shared']['normalized_rcz_sha256']
        normalized_linear=((linear.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
        pc_grid=physical_mr(normalized_pc,grid);linear_grid=physical_mr(normalized_linear,grid)
        sl=(slice(0,64),slice(0,128),slice(0,128))
        reference=torch.from_numpy(pc_grid[sl].copy())[None,None]
        candidate=torch.from_numpy(linear_grid[sl].copy())[None,None]
        guard();r['self_replays'].append(check_self(reference,state,persist));save()
        trace=[]
        with torch.inference_mode():
            ordinary=functional_forward(candidate,state)
            controlled,baseline=reference_statistics_forward(candidate,reference,state,trace)
            ordinary_pc=functional_forward(reference,state)
        assert len(trace)==14 and compare(baseline,ordinary_pc)['probability_max_absolute_error_by_head']==[0,0,0]
        r['different_input_observation']=dict(patient=case['patient'],series_uid=case['uid'],tile_start_zrc=[0,0,0],
            tile_selected_using_gt=False,observed_array_sha256=array_sha(observed.pixels),observed_package_sha256=row['observed_package_sha256'],
            native_lattice_anchors_identical=True,physical_grid_anchors_identical_not_asserted=True,observed_statistics=st,
            reference_patch_sha256=array_sha(reference.numpy()),candidate_patch_sha256=array_sha(candidate.numpy()),
            ordinary_vs_reference_statistics=compare(ordinary,controlled),layers=trace,
            limitation='Output sensitivity of an unqualified checkpoint; no ground-truth task benefit or causal fraction')
        r['resources_after']=guard();assert not torch.cuda.is_initialized();r['cuda_initialized']=False;r['complete']=True
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-started;save()
    assert path.stat().st_size<=2_000_000
    print(json.dumps({k:r.get(k) for k in ('complete','errors','self_replays','actual_training_updates','cuda_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
