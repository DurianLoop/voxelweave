"""Conditional multi-patient CPU resource qualification; every new weight discarded."""
import collections,gc,json,sys,time,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,lattice,physical_mr,
    physical_label,read_reference_label,sample_batch,TaskUNet3D,loss,SEED,torch,np)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07'
FIT=ROOT/'experiments/mc_rc_3d_backbone_context_low_lr_2026_10_07/attempt01.json'
PROOF=FIT.parent/'independent_both1024_and_full_fov_attempt01.json'
EXIT=ROOT/'SESSION_OBSERVED_EXITS_LOW_LR_CONTEXT_2026-10-07.json'
PROTOCOL=ROOT/'MC_RC_3D_19SERIES_CPU_LOW_LR_ENTRY_ADDENDUM_2026-10-07.md'
def stream_for(cases):
    by=collections.defaultdict(list)
    for case,row in cases:by[case['patient']].append(case['uid'])
    patients=sorted(by);seeds=np.random.SeedSequence(SEED).spawn(len(patients)+1)
    order_rng=np.random.default_rng(seeds[0]);series_orders={}
    for patient,seed in zip(patients,seeds[1:]):
        values=sorted(by[patient]);indices=np.random.default_rng(seed).permutation(len(values))
        series_orders[patient]=[values[int(i)] for i in indices]
    stream=[]
    for round_index in range(max(map(len,by.values()))):
        for i in order_rng.permutation(len(patients)):
            patient=patients[int(i)];uids=series_orders[patient]
            stream.append(dict(step=len(stream)+1,round_index=round_index,patient=patient,uid=uids[round_index%len(uids)]))
    assert set(x['uid'] for x in stream)==set(c['uid'] for c,r in cases)
    assert len(set(collections.Counter(x['patient'] for x in stream).values()))==1
    return stream,series_orders
def prerequisites():
    fit,proof,exits=read(FIT),read(PROOF),read(EXIT)
    assert exits['training_observed_tool_exit']==exits['independent_verifier_observed_tool_exit']==0
    assert exits['complete'] and exits['training_result_sha256']==sha(FIT) and exits['verifier_result_sha256']==sha(PROOF)
    assert fit['complete'] and fit['status']=='completed' and not fit['errors'] and fit['actual_cpu_backbone_updates']==2048
    assert proof['complete'] and not proof['errors'] and proof['result_sha256']==sha(FIT)
    assert fit['both_original_fit_gates_passed'] and len(fit['arms'])==len(proof['arms'])==2
    for arm,p in zip(fit['arms'],proof['arms']):
        assert arm['kind']==p['kind'] and arm['training_fit_gate_passed'] and all(p['original_training_fit_gate'].values())
        assert p['full_tile_stream_and_labels_verified'] and p['history_rows_verified']==1024
        assert p['coverage']['all_three_head_tile_probability_max_error']<=3e-6
        assert p['production_coordinate_replay_max_probability_error']<=3e-6 and p['production_coordinate_replay_threshold_disagreements']==0
        assert p['production_float32_vs_numpy_coordinate']['original_strict_gate_passed'] and p['independent_float64_coordinate']['gate_passed']
        assert sha(ROOT/arm['checkpoint_file'])==arm['checkpoint_sha256']
    return fit
def main():
    sys.stdout.reconfigure(encoding='utf-8');fit=prerequisites();OUT.mkdir(exist_ok=False)
    path=OUT/'attempt01.json';started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],status='preparing',script_sha256=sha(__file__),
        arms=[],actual_resource_test_cpu_updates=0,actual_formal_training_updates=0,actual_gpu_updates=0,
        updated_weights_saved=False,task_effects_scored=False,validation_MR_or_GT_loaded=False,validation_metadata_only=True,
        validation_effects_opened=False,confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    def save():
        path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<5_000_000
    def guard():
        assert time.perf_counter()-started<=1200,'Frozen wall-clock limit exceeded'
        return resource_guard()
    save()
    try:
        torch.set_num_threads(4);assert torch.get_num_interop_threads()==1
        r['resources_before']=guard();r.update(cpu_intraop_threads=4,cpu_interop_threads=1)
        cases=[(case,row) for role,case,row in fixed_cases() if role=='development']
        assert len(cases)==19 and len({c['patient'] for c,row in cases})==11
        frozen,orders=stream_for(cases);r.update(frozen_stream=frozen,frozen_series_orders=orders,planned_updates_per_arm=len(frozen),
            training_patient_ids=sorted({c['patient'] for c,row in cases}),development_series_uids=sorted(c['uid'] for c,row in cases))
        sources=[FIT,PROOF,EXIT,PROTOCOL,ROOT/'MC_RC_3D_19SERIES_CPU_QUALIFICATION_PREPARATION_2026-10-07.md',
                 ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
                 ROOT/'experiments/mc_rc_3d_19series_resource_planning_2026_10_07/attempt01.json']
        sources.extend(ROOT/a['checkpoint_file'] for a in fit['arms'])
        for c,row in cases:
            sources.extend(ROOT/c[k] for k in ('header_file','mr_zip_file','label_file'))
            sources.append(ROOT/row['observed_package'])
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(sources))]
        for original in fit['arms']:
            guard();kind=original['kind'];arm=dict(kind=kind,complete=False,history=[],cache_records=[],updates=0,
                initial_checkpoint_file=original['checkpoint_file'],initial_checkpoint_sha256=original['checkpoint_sha256'])
            r['arms'].append(arm);r['status']='loading_cache';save();cache={};cache_started=time.perf_counter()
            for c,row in cases:
                guard();tick=time.perf_counter();grid=lattice(c);native_gt=read_reference_label(c);target=physical_label(native_gt,grid)
                normalized,stats=source_image(c,row,kind);image=physical_mr(normalized,grid)
                assert image.dtype==target.dtype==np.float32 and image.shape==target.shape
                assert np.isfinite(image).all() and np.isfinite(target).all() and target.sum()>0
                cache[c['uid']]=(image,target)
                arm['cache_records'].append(dict(patient=c['patient'],uid=c['uid'],shape_zrc=list(image.shape),
                    input_sha256=array_sha(image),label_sha256=array_sha(target),label_foreground=int(target.sum()),
                    image_bytes=int(image.nbytes),label_bytes=int(target.nbytes),observed_statistics=stats,load_seconds=time.perf_counter()-tick))
                del normalized,native_gt;guard();save()
            arm['cache_elapsed_seconds']=time.perf_counter()-cache_started
            arm['cache_total_array_bytes']=sum(i.nbytes+t.nbytes for i,t in cache.values())
            planning=read(sources[7]);assert arm['cache_total_array_bytes']==planning['host_cache_plans']['one_input_and_float32_label']['bytes']
            initial=torch.load(ROOT/original['checkpoint_file'],map_location='cpu',weights_only=True)['state_dict']
            model=TaskUNet3D();model.load_state_dict(initial,strict=True);model.train();arm['initial_weights_sha256']=state_hash(model.state_dict())
            assert arm['initial_weights_sha256']==original['final_weights_sha256']
            optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001);r['status']='resource_updates';save()
            for item in frozen:
                resources=guard();tick=time.perf_counter();image,target=cache[item['uid']]
                rng=np.random.default_rng(np.random.SeedSequence([SEED,item['step']]))
                x,y,primitive=sample_batch(image,target,rng)
                input_hash,label_hash=array_sha(x.numpy()),array_sha(y.numpy());sample_seconds=time.perf_counter()-tick
                at=time.perf_counter();optimizer.zero_grad(set_to_none=True);outputs=model(x);value=loss(outputs,y)
                assert torch.isfinite(value);forward_seconds=time.perf_counter()-at
                at=time.perf_counter();value.backward();backward_seconds=time.perf_counter()-at
                at=time.perf_counter();assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
                if item['step']==1:
                    arm['first_update_branch_gradient_max']={name:max(float(p.grad.abs().max()) for p in module.parameters())
                        for name,module in (('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads))}
                    assert all(v>0 for v in arm['first_update_branch_gradient_max'].values())
                check_seconds=time.perf_counter()-at;at=time.perf_counter();optimizer.step();optimizer_seconds=time.perf_counter()-at
                elapsed=time.perf_counter()-tick;arm['updates']+=1;r['actual_resource_test_cpu_updates']+=1
                arm['history'].append(dict(**item,warmup=item['step']<=2,input_sha256=input_hash,label_sha256=label_hash,
                    augmentation_primitive=primitive,label_foreground=[int(g.sum()) for g in y],loss=float(value.detach()),lr=.001,
                    sample_and_hash_seconds=sample_seconds,forward_and_loss_seconds=forward_seconds,backward_seconds=backward_seconds,
                    gradient_check_seconds=check_seconds,optimizer_step_seconds=optimizer_seconds,total_update_seconds=elapsed,
                    resources_before=resources))
                guard();save();print(json.dumps(dict(kind=kind,step=item['step'],patient=item['patient'],uid=item['uid'],seconds=elapsed)),flush=True)
            timed=[h['total_update_seconds'] for h in arm['history'] if not h['warmup']]
            arm.update(complete=True,all_losses_and_gradients_finite=True,median_timed_seconds=float(np.median(timed)),
                max_timed_seconds=max(timed),all_step_seconds=sum(h['total_update_seconds'] for h in arm['history']),
                discarded_final_weights_sha256=state_hash(model.state_dict()))
            assert arm['discarded_final_weights_sha256']!=arm['initial_weights_sha256']
            del model,optimizer,initial,outputs,value,x,y,image,target,cache;gc.collect();guard();save()
        first,second=r['arms'];keys=('step','round_index','patient','uid','label_sha256','label_foreground','augmentation_primitive')
        assert [{k:h[k] for k in keys} for h in first['history']]==[{k:h[k] for k in keys} for h in second['history']]
        assert [{k:c[k] for k in ('patient','uid','shape_zrc','label_sha256','label_foreground')} for c in first['cache_records']]==[
            {k:c[k] for k in ('patient','uid','shape_zrc','label_sha256','label_foreground')} for c in second['cache_records']]
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        r['gate']=dict(all_series_covered=all(set(h['uid'] for h in a['history'])==set(r['development_series_uids']) for a in r['arms']),
            all_patients_balanced=all(len(set(collections.Counter(h['patient'] for h in a['history']).values()))==1 for a in r['arms']),
            paired_GT_and_augmentation_identical=True,all_parameters_gradients_finite=True,all_first_step_branches_nonzero=True,
            planned_updates_completed=all(a['updates']==len(frozen) for a in r['arms']),no_cuda=True,no_updated_weights_saved=True)
        r['complete']=all(r['gate'].values());r['status']='completed';r['resources_after']=guard()
    except Exception as e:
        r['status']='failed';r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ('status','complete','errors','actual_resource_test_cpu_updates','gate','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
