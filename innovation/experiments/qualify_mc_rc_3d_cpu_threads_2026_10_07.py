"""Bounded actual batch CPU timing; every state reset and all updates discarded."""
import json, os, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT, read, sha, array_sha, resource_guard, fixed_cases, source_image, lattice, physical_mr,
    physical_label, read_reference_label, TaskUNet3D, loss, tile_plan, PATCH, torch, np)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash

OUT = ROOT / 'experiments/mc_rc_3d_cpu_thread_qualification_2026_10_07'
def main():
    sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(exist_ok=False)
    path=OUT/'attempt01.json'; started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[],
           script_sha256=sha(__file__), benchmarks=[], actual_resource_test_cpu_updates=0,
           actual_formal_training_updates=0, actual_gpu_updates=0, logical_cpus=os.cpu_count(),
           validation_effects_opened=False, confirmation_patients_opened=False,
           scientific_confirmation_patients=0, publication_claim_confirmed=False)
    def save(): path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-started<=300, 'CPU timing wall-clock bound exceeded'
        out=resource_guard(); out['cpu_threads']=torch.get_num_threads(); return out
    save()
    try:
        assert r['logical_cpus']>=8
        source=ROOT/'experiments/mc_rc_3d_all_tile_head_fit_2026_10_07/attempt01.json'
        proof=ROOT/'experiments/mc_rc_3d_all_tile_head_fit_2026_10_07/module_features_and_full_fov_verification_attempt01.json'
        q,cert=read(source),read(proof)
        assert q['complete'] and cert['complete'] and not q['errors'] and not cert['errors']
        arm=q['arms'][0]; assert arm['kind']=='native_reference'
        cp=ROOT/arm['checkpoint_file']; assert sha(cp)==arm['checkpoint_sha256']
        protocol=ROOT/'MC_RC_3D_BACKBONE_CONTEXT_REFIT_PROTOCOL_2026-10-07.md'
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (source,proof,cp,protocol)]
        r['resources_before']=guard(); role,case,row=fixed_cases()[0]
        assert role=='development' and case['patient']=='VS-MC-RC-001'
        grid=lattice(case); native_label=read_reference_label(case); target=physical_label(native_label,grid)
        normalized,stats=source_image(case,row,'native_reference'); image=physical_mr(normalized,grid)
        assert array_sha(image)==arm['physical_input_sha256'] and array_sha(target)==arm['physical_label_sha256']
        locations,_=tile_plan(image.shape); pair=[locations[4],locations[5]]
        slices=[tuple(slice(s,s+p) for s,p in zip(start,PATCH)) for start in pair]
        x=torch.from_numpy(np.stack([image[sl] for sl in slices])[:,None])
        y=torch.from_numpy(np.stack([target[sl] for sl in slices])[:,None])
        state=torch.load(cp,map_location='cpu',weights_only=True)['state_dict']; reference_probability=None
        r.update(patient=case['patient'],uid=case['uid'],tile_locations=[list(v) for v in pair],
                 input_sha256=array_sha(x.numpy()),target_sha256=array_sha(y.numpy()),
                 initial_weights_sha256=state_hash(state))
        for threads in (1,4):
            torch.set_num_threads(threads); guard()
            model=TaskUNet3D(); model.load_state_dict(state,strict=True); model.train()
            assert state_hash(model.state_dict())==r['initial_weights_sha256']
            with torch.inference_mode(): initial=model(x)[0].sigmoid().numpy().copy()
            if reference_probability is None: reference_probability=initial
            error=float(np.max(np.abs(initial-reference_probability)))
            disagreements=int(np.count_nonzero((initial>=.5)!=(reference_probability>=.5)))
            optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
            b=dict(threads=threads,updates=0,history=[],initial_probability_max_error_vs_one_thread=error,
                   initial_threshold_disagreements_vs_one_thread=disagreements)
            r['benchmarks'].append(b)
            for step in range(6):
                guard(); tick=time.perf_counter(); optimizer.zero_grad(set_to_none=True)
                outputs=model(x); value=loss(outputs,y); assert torch.isfinite(value)
                value.backward(); assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
                optimizer.step(); elapsed=time.perf_counter()-tick
                b['history'].append(dict(update=step+1,warmup=step<2,seconds=elapsed,loss=float(value.detach())))
                b['updates']+=1; r['actual_resource_test_cpu_updates']+=1; save()
                print(json.dumps(dict(threads=threads,update=step+1,seconds=elapsed)),flush=True)
            b['median_timed_seconds_per_update']=float(np.median([v['seconds'] for v in b['history'] if not v['warmup']]))
            b['discarded_final_weights_sha256']=state_hash(model.state_dict()); b['resources_after']=guard()
            del model,optimizer,outputs,value
        one,four=r['benchmarks']; r['four_to_one_speed_ratio']=four['median_timed_seconds_per_update']/one['median_timed_seconds_per_update']
        r['four_thread_gate']=dict(probability_error=four['initial_probability_max_error_vs_one_thread']<=3e-6,
                                  twenty_percent_faster=r['four_to_one_speed_ratio']<=.8)
        r['selected_threads']=4 if all(r['four_thread_gate'].values()) else 1
        r['selected_seconds_per_update']=r['benchmarks'][int(r['selected_threads']==4)]['median_timed_seconds_per_update']
        r['projected_two_arm_1024_updates_seconds']=2048*r['selected_seconds_per_update']
        r['cuda_initialized']=torch.cuda.is_initialized(); assert not r['cuda_initialized']
        r['complete']=r['actual_resource_test_cpu_updates']==12; r['resources_after']=guard()
        assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<=1_000_000
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e)); r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat(); r['elapsed_seconds']=time.perf_counter()-started; save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','selected_threads','selected_seconds_per_update',
        'projected_two_arm_1024_updates_seconds','actual_resource_test_cpu_updates','cuda_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__': raise SystemExit(main())
