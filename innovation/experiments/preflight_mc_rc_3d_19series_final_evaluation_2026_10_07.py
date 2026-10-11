"""Synthetic/metadata qualification of complete final evaluation; no MRI/GT pixel loads."""
import ast,gc,itertools,json,subprocess,sys,time,traceback
from mc_rc_3d_19series_final_eval_2026_10_07 import *
from verify_mc_rc_3d_19series_common_init_final_2026_10_07 import independent_counts,independent_aggregate,trees_close,functional_fov
PREF=ROOT/'experiments/mc_rc_3d_19series_final_evaluation_preflight_2026_10_07'
def main():
    sys.stdout.reconfigure(encoding='utf-8');PREF.mkdir(exist_ok=False);torch.set_num_threads(4);started=time.perf_counter()
    path=PREF/'attempt01.json';r=dict(created_utc=now(),complete=False,errors=[],script_sha256=sha(__file__),
        real_MRI_or_GT_pixel_arrays_loaded=0,actual_training_updates=0,actual_gpu_updates=0,publication_claim_confirmed=False)
    dump_new(path,r)
    try:
        guard(started)
        names=['mc_rc_3d_19series_final_eval_2026_10_07.py','evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py',
            'verify_mc_rc_3d_19series_common_init_final_2026_10_07.py','preflight_mc_rc_3d_19series_final_evaluation_2026_10_07.py']
        for n in names:ast.parse((ROOT/'experiments'/n).read_text(encoding='utf-8'))
        cases=roles();metadata=[]
        for role,c,row in cases:
            g=lattice(c);shape=tuple(int(n)+int(lo)+int(hi) for n,(lo,hi) in zip(g['unpadded_shape_zrc'],g['padding']))
            locations,axes=tile_plan(shape);metadata.append(dict(role=role,patient=c['patient'],uid=c['uid'],native_shape=c['native_shape'],
                physical_shape_zrc=shape,axis_starts=axes,tiles=len(locations),packed_bytes_per_arm=(math.prod(c['native_shape'])+7)//8))
        assert sum(m['tiles'] for m in metadata if m['role']=='development')==1139
        assert 2*sum(m['packed_bytes_per_arm'] for m in metadata)==115491840
        r.update(metadata28_series=metadata,two_arm_56_packed_bytes=115491840,
            planned_total56_tiles=2*sum(m['tiles'] for m in metadata),development_tiles_per_arm=1139)
        # Execute the actual CLI's readiness route; no monkeypatched model/role gate.
        assert not OUT.exists() and not readiness()['ready']
        probe=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'experiments/evaluate_mc_rc_3d_19series_common_init_final_2026_10_07.py'),
            '--readiness-only'],capture_output=True,text=True,encoding='utf-8',timeout=30)
        assert probe.returncode==3;status=json.loads(probe.stdout)
        assert status['status']=='execution_deferred' and not status['ready'] and status['MR_or_GT_arrays_loaded']==0 and not status['CUDA_initialized']
        assert not OUT.exists();r['actual_readiness_probe']=dict(exit_code=probe.returncode,output=status,evaluation_output_not_created=True)
        positions=(0,1,4,6);verified=0
        for gtbits,pbits in itertools.product(range(16),repeat=2):
            gt=np.zeros((1,1,8),bool);p=np.zeros_like(gt)
            for i,z in enumerate(positions):gt[0,0,z]=bool(gtbits&(1<<i));p[0,0,z]=bool(pbits&(1<<i))
            primary=metrics(p,gt);ind=independent_counts(p,gt);assert trees_close(primary,ind)
            verified+=1
        r['all256_binary_domain_count_and_undefined_cases_verified']=verified
        rng=np.random.default_rng([SEED,620]);packed=[]
        for n in (1,7,8,9,63,64,65,105):
            a=(rng.random((1,1,n))>.45);file=PREF/('synthetic_packed_'+str(n)+'.npz');pack_prediction(file,a)
            assert np.array_equal(unpack_prediction(file),a);packed.append(dict(voxels=n,raw_packed_bytes=(n+7)//8,sha256=sha(file)))
        r['packing_nonbyte_shapes']=packed
        gt=np.zeros((1,1,8),bool);gt[0,0,1]=True
        rows=[]
        for patient,uid,p in [('A','A1',gt.copy()),('A','A2',np.zeros_like(gt)),('B','B1',gt.copy())]:
            rows.append(dict(patient=patient,uid=uid,metrics=metrics(p,gt)))
        pa=aggregate(rows,{'A','B'});ia=independent_aggregate(rows,{'A','B'})
        assert trees_close(pa,ia) and pa['patient_first_means']['full']['dice']==.75
        assert abs(sum(v['metrics']['full']['dice'] for v in rows)/3-2/3)<1e-15
        assert pa['patient_first_means']['tail']['dice'] is None and pa['patient_first_means']['full']['precision'] is None
        assert not gates(pa)['no_series_complete_miss']
        r['unequal_series_patient_aggregation']=dict(patient_first_Dice=.75,incorrect_series_first_Dice=2/3,
            undefined_precision_and_tail_retained=True,positive_mean_does_not_hide_complete_miss=True,independent_Fraction_means_equal=True)
        # Exercise real production-sized patch inference/functional assembly on a synthetic small unpadded volume.
        torch.manual_seed(SEED);model=TaskUNet3D().eval();state={k:v.detach().clone() for k,v in model.state_dict().items()}
        grid=dict(unpadded_shape_zrc=[17,29,31],padding=[(23,24),(49,50),(48,49)])
        assert tuple(n+lo+hi for n,(lo,hi) in zip(grid['unpadded_shape_zrc'],grid['padding']))==PATCH
        phantom=np.pad(rng.normal(size=grid['unpadded_shape_zrc']).astype(np.float32),grid['padding']);native=[31,35,19]
        wrapped=GuardedModel(model,lambda:guard(started));production,pm=infer_full_fov(wrapped,phantom,grid,native)
        independent,im=functional_fov(state,phantom,grid,native,lambda:guard(started))
        error=float(np.max(np.abs(production-independent)));binary=int(np.count_nonzero((production>=.5)!=(independent>=.5)))
        assert error<=3e-6 and binary==0 and im['float64_coordinate_gate_passed']
        assert pm['axis_starts']==im['axis_starts'] and pm['total_tiles']==im['total_tiles']==1
        r['synthetic_full_patch_inference']=dict(float32_max_probability_error=error,float32_threshold_disagreements=binary,
            float64_coordinate_max_probability_error=im['float64_coordinate_max_probability_error'],
            float64_coordinate_threshold_disagreements=im['float64_coordinate_threshold_disagreements'],all_original_numeric_gates_passed=True,
            padding_and_nonidentity_native_mapping_exercised=True,real_MRI_generalization_not_tested=True)
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in
            [ROOT/'experiments'/n for n in names]+[PROTOCOL,ROOT/'SESSION_19SERIES_COMMON_INIT_FINAL_EVALUATION_METADATA_PREPARATION_2026-10-07.json']]
        assert time.perf_counter()-started<=120 and sum(p.stat().st_size for p in PREF.rglob('*') if p.is_file())<10000000
        r.update(complete=True,cuda_initialized=torch.cuda.is_initialized(),resources_after=guard(started))
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=now();r['elapsed_seconds']=time.perf_counter()-started;atomic_json(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','planned_total56_tiles','two_arm_56_packed_bytes',
        'synthetic_full_patch_inference','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
