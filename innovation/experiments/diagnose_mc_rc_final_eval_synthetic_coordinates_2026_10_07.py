"""Preserve exact numbers behind failed synthetic preflight; no MRI or optimizer step."""
import json,sys,time
from mc_rc_3d_19series_final_eval_2026_10_07 import *
from verify_mc_rc_3d_19series_common_init_final_2026_10_07 import functional_fov
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(4);started=time.perf_counter();guard(started)
    target=ROOT/'experiments/mc_rc_final_eval_synthetic_coordinate_diagnostic_2026_10_07.json';assert not target.exists()
    rng=np.random.default_rng([SEED,620])
    for n in (1,7,8,9,63,64,65,105):rng.random((1,1,n))
    torch.manual_seed(SEED);model=TaskUNet3D().eval();state={k:v.detach().clone() for k,v in model.state_dict().items()}
    grid=dict(unpadded_shape_zrc=[17,29,31],padding=[(23,24),(49,50),(48,49)])
    phantom=np.pad(rng.normal(size=grid['unpadded_shape_zrc']).astype(np.float32),grid['padding']);native=[31,35,19]
    production,pm=infer_full_fov(GuardedModel(model,lambda:guard(started)),phantom,grid,native)
    independent,im=functional_fov(state,phantom,grid,native,lambda:guard(started))
    error=float(np.max(np.abs(production-independent)));binary=int(np.count_nonzero((production>=.5)!=(independent>=.5)))
    locs=np.argwhere((production>=.5)!=(independent>=.5));details=[dict(index_rcz=v.tolist(),production_probability=float(production[tuple(v)]),
        independent_probability=float(independent[tuple(v)])) for v in locs[:20]]
    r=dict(created_utc=now(),complete=True,script_sha256=sha(__file__),real_MRI_or_GT_pixel_arrays_loaded=0,actual_training_updates=0,
        actual_gpu_updates=0,float32_max_probability_error=error,float32_threshold_disagreements=binary,
        float32_original_gate_passed=error<=3e-6 and binary==0,functional_and_float64=im,production_inference=pm,
        first20_threshold_disagreement_voxels=details,original_preflight_failure_preserved=True,
        publication_claim_confirmed=False,elapsed_seconds=time.perf_counter()-started)
    dump_new(target,r);print(json.dumps(r,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
