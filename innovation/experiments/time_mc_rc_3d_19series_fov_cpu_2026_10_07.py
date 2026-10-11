"""Measure complete development inference only; no labels and no task effect scores."""
import gc,json,sys,time,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,lattice,physical_mr,TaskUNet3D,
    infer_full_fov,tile_plan,torch,np)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_19series_fov_cpu_timing_2026_10_07'
Q=ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json'
PROOF=Q.parent/'independent_stream_and_batch_attempt01.json'
EXIT=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_CPU_RESOURCE_2026-10-07.json'
PROTOCOL=ROOT/'MC_RC_3D_19SERIES_FOV_CPU_TIMING_PROTOCOL_2026-10-07.md'
def main():
    sys.stdout.reconfigure(encoding='utf-8');q,p,e=read(Q),read(PROOF),read(EXIT)
    assert q['complete'] and p['complete'] and not q['errors'] and not p['errors'] and all(q['gate'].values())
    assert p['source_sha256']==sha(Q) and e['qualification_result_sha256']==sha(Q) and e['verifier_result_sha256']==sha(PROOF)
    assert e['qualification_observed_tool_exit']==e['independent_verifier_observed_tool_exit']==0
    OUT.mkdir(exist_ok=False);path=OUT/'attempt01.json';started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),arms=[],
        cpu_intraop_threads=4,cpu_interop_threads=1,actual_training_updates=0,actual_gpu_updates=0,GT_files_loaded=0,
        task_effects_scored=False,validation_MR_or_GT_loaded=False,confirmation_patients_opened=False,
        predictions_saved=False,publication_claim_confirmed=False)
    def save():
        path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<10_000_000
    def guard():
        assert time.perf_counter()-started<=1800,'Frozen full-FOV timing wall-clock limit exceeded'
        observed=resource_guard();observed['cpu_threads']=torch.get_num_threads();return observed
    save()
    try:
        torch.set_num_threads(4);assert torch.get_num_interop_threads()==1;r['resources_before']=guard()
        cases=sorted([(c,row) for role,c,row in fixed_cases() if role=='development'],key=lambda pair:(pair[0]['patient'],pair[0]['uid']))
        assert len(cases)==19 and len({c['patient'] for c,row in cases})==11
        r['planned_tiles_per_arm']=sum(len(tile_plan(tuple(np.array(lattice(c)['unpadded_shape_zrc'])+np.sum(lattice(c)['padding'],axis=1)))[0]) for c,row in cases)
        assert r['planned_tiles_per_arm']==1139
        sources=[Q,PROOF,EXIT,PROTOCOL,ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py']
        sources.extend(ROOT/a['initial_checkpoint_file'] for a in q['arms'])
        r['source_bindings']=[dict(path=s.relative_to(ROOT).as_posix(),sha256=sha(s)) for s in sources];save()
        for qa in q['arms']:
            guard();cp=ROOT/qa['initial_checkpoint_file'];assert sha(cp)==qa['initial_checkpoint_sha256']
            state=torch.load(cp,map_location='cpu',weights_only=True)['state_dict'];model=TaskUNet3D();model.load_state_dict(state,strict=True);model.eval()
            assert state_hash(model.state_dict())==qa['initial_weights_sha256'];cache_hashes={c['uid']:c['input_sha256'] for c in qa['cache_records']}
            arm=dict(kind=qa['kind'],complete=False,series=[],checkpoint_file=qa['initial_checkpoint_file'],checkpoint_sha256=sha(cp))
            r['arms'].append(arm);save()
            for c,row in cases:
                before=guard();tick=time.perf_counter();normalized,stats=source_image(c,row,qa['kind']);grid=lattice(c)
                image=physical_mr(normalized,grid);input_hash=array_sha(image);assert input_hash==cache_hashes[c['uid']]
                load_seconds=time.perf_counter()-tick;del normalized;tick=time.perf_counter()
                probability,meta=infer_full_fov(model,image,grid,c['native_shape']);inference_seconds=time.perf_counter()-tick
                assert probability.dtype==np.float32 and list(probability.shape)==c['native_shape'] and np.isfinite(probability).all()
                record=dict(patient=c['patient'],uid=c['uid'],physical_input_sha256=input_hash,native_shape=c['native_shape'],
                    probability_sha256=array_sha(probability),load_and_input_hash_seconds=load_seconds,
                    complete_inference_seconds=inference_seconds,inference=meta,resources_before=before)
                arm['series'].append(record);del image,probability;gc.collect();guard();save()
                print(json.dumps(dict(kind=qa['kind'],series_completed=len(arm['series']),tiles=meta['total_tiles'],seconds=inference_seconds)),flush=True)
            arm.update(complete=True,total_tiles=sum(s['inference']['total_tiles'] for s in arm['series']),
                all19_load_and_input_hash_seconds=sum(s['load_and_input_hash_seconds'] for s in arm['series']),
                all19_complete_inference_seconds=sum(s['complete_inference_seconds'] for s in arm['series']),
                median_series_inference_seconds=float(np.median([s['complete_inference_seconds'] for s in arm['series']])))
            assert arm['total_tiles']==1139 and state_hash(model.state_dict())==qa['initial_weights_sha256'] and sha(cp)==qa['initial_checkpoint_sha256']
            del model,state;guard();save()
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized'];r['resources_after']=guard()
        r['complete']=len(r['arms'])==2 and all(a['complete'] for a in r['arms'])
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','elapsed_seconds','GT_files_loaded','actual_training_updates')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
