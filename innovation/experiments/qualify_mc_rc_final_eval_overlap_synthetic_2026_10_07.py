"""Two predeclared 8-tile synthetic fixtures; no MRI, optimizer updates or task effect claims."""
import gc,json,sys,time,traceback
from mc_rc_3d_19series_final_eval_2026_10_07 import *
from verify_mc_rc_3d_19series_common_init_final_2026_10_07 import functional_fov
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(4);started=time.perf_counter()
    p=ROOT/'experiments/mc_rc_final_eval_overlap_synthetic_2026_10_07.json';assert not p.exists()
    r=dict(created_utc=now(),complete=False,errors=[],script_sha256=sha(__file__),real_MRI_or_GT_pixel_arrays_loaded=0,
        actual_training_updates=0,actual_gpu_updates=0,fixtures=[],publication_claim_confirmed=False)
    dump_new(p,r)
    try:
        guard(started);torch.manual_seed(SEED);base=TaskUNet3D().eval();initial={k:v.detach().clone() for k,v in base.state_dict().items()}
        grid=dict(unpadded_shape_zrc=[70,137,141],padding=[(13,13),(11,12),(9,10)])
        rng=np.random.default_rng([SEED,621]);image=np.pad(rng.normal(size=grid['unpadded_shape_zrc']).astype(np.float32),grid['padding'])
        assert image.shape==(96,160,160)
        specs=[dict(name='mixed_predictions_identity_native',native=[137,141,70],head_fixture='original_seeded_random_weights'),
            dict(name='all_background_nonidentity_native',native=[139,145,73],head_fixture='head_weight_x0.1_bias_minus2')]
        for spec in specs:
            model=TaskUNet3D().eval();model.load_state_dict(initial)
            if spec['head_fixture']!='original_seeded_random_weights':
                with torch.no_grad():model.heads[2].weight.mul_(.1);model.heads[2].bias.fill_(-2.)
            state={k:v.detach().clone() for k,v in model.state_dict().items()};tick=time.perf_counter()
            production,pm=infer_full_fov(GuardedModel(model,lambda:guard(started)),image,grid,spec['native'])
            independent,im=functional_fov(state,image,grid,spec['native'],lambda:guard(started))
            error=float(np.max(np.abs(production-independent)));binary=int(np.count_nonzero((production>=.5)!=(independent>=.5)))
            item=dict(**spec,float32_max_probability_error=error,float32_threshold_disagreements=binary,
                float64_coordinate_max_probability_error=im['float64_coordinate_max_probability_error'],
                float64_coordinate_threshold_disagreements=im['float64_coordinate_threshold_disagreements'],
                predicted_foreground=int(np.count_nonzero(production>=.5)),total_native_voxels=int(production.size),
                probability_min=float(production.min()),probability_max=float(production.max()),
                total_tiles=pm['total_tiles'],axis_starts=pm['axis_starts'],seconds=time.perf_counter()-tick,
                original_numeric_gates_passed=error<=3e-6 and binary==0 and im['float64_coordinate_gate_passed'])
            r['fixtures'].append(item);atomic_json(p,r)
            assert pm['total_tiles']==im['total_tiles']==8 and pm['axis_starts']==im['axis_starts']
            assert pm['coverage_max']>1 and pm['coverage_min']>0 and item['original_numeric_gates_passed']
            if spec['head_fixture']=='original_seeded_random_weights':assert 0<item['predicted_foreground']<item['total_native_voxels']
            else:assert item['predicted_foreground']==0
            del model,state,production,independent;gc.collect();guard(started)
        assert time.perf_counter()-started<=120
        r.update(complete=True,real_MRI_numeric_gates_not_tested=True,source_bindings=[dict(path=s.relative_to(ROOT).as_posix(),sha256=sha(s)) for s in (
            ROOT/'experiments/mc_rc_3d_19series_final_eval_2026_10_07.py',ROOT/'experiments/verify_mc_rc_3d_19series_common_init_final_2026_10_07.py',
            ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py',PROTOCOL)])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=now();r['elapsed_seconds']=time.perf_counter()-started;atomic_json(p,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','fixtures','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
