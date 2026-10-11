"""Resume both backbones over all inference contexts, fixed last checkpoints only."""
import json, sys, time, traceback
from datetime import datetime, timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT, read, sha, array_sha, resource_guard, fixed_cases, source_image, lattice, physical_mr,
    physical_label, read_reference_label, TaskUNet3D, loss, tile_plan, sample_batch,
    infer_full_fov, PATCH, SEED, torch, np)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
from mc_rc_3d_independent_replay_2026_10_07 import logical_counts

OUT=ROOT/'experiments/mc_rc_3d_backbone_context_refit_2026_10_07'
def main():
    sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(exist_ok=False)
    path=OUT/'attempt01.json'; started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),status='preparing',complete=False,errors=[],
           script_sha256=sha(__file__),arms=[],actual_cpu_backbone_updates=0,actual_gpu_updates=0,
           planned_updates_per_arm=1024,planned_total_updates=2048,seed=SEED,
           validation_effects_opened=False,confirmation_patients_opened=False,
           scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-started<=5400,'Frozen total wall-clock limit exceeded'
        resources=resource_guard(); resources['cpu_threads']=torch.get_num_threads(); return resources
    save()
    try:
        qualification=ROOT/'experiments/mc_rc_3d_cpu_thread_qualification_2026_10_07/attempt01.json'
        basepath=ROOT/'experiments/mc_rc_3d_all_tile_head_fit_2026_10_07/attempt01.json'
        proofpath=basepath.parent/'module_features_and_full_fov_verification_attempt01.json'
        q,base,proof=read(qualification),read(basepath),read(proofpath)
        assert all(v['complete'] and not v['errors'] for v in (q,base,proof))
        assert q['selected_threads']==4 and all(q['four_thread_gate'].values())
        sources=[qualification,basepath,proofpath,ROOT/'MC_RC_3D_BACKBONE_CONTEXT_REFIT_PROTOCOL_2026-10-07.md',
                 ROOT/'MC_RC_3D_BACKBONE_CONTEXT_REFIT_EXECUTION_ADDENDUM_2026-10-07.md',
                 ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
                 ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py']
        for binding in base['source_bindings']:assert sha(ROOT/binding['path'])==binding['sha256']
        sources.extend(ROOT/binding['path'] for binding in base['source_bindings'])
        sources.extend(ROOT[a['checkpoint_file']] for a in base['arms'])
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(sources))]
        torch.set_num_threads(4); r['resources_before']=guard()
        role,case,row=fixed_cases()[0]; assert role=='development' and case['patient']=='VS-MC-RC-001'
        assert case['uid']==base['series_uid']
        grid=lattice(case); label=read_reference_label(case); target=physical_label(label,grid)
        r.update(training_patient_ids=[case['patient']],series_uid=case['uid'],physical_label_sha256=array_sha(target),
                 cpu_intraop_threads=torch.get_num_threads(),cpu_interop_threads=torch.get_num_interop_threads(),
                 architecture_trainable_parameters=sum(p.numel() for p in TaskUNet3D().parameters()))
        assert r['cpu_interop_threads']==1
        rng=np.random.default_rng(SEED); epochs=[rng.permutation(16).tolist() for _ in range(128)]
        stream=[indices[at:at+2] for indices in epochs for at in range(0,16,2)]
        assert len(stream)==1024 and all(sorted(indices)==list(range(16)) for indices in epochs)
        r['frozen_tile_pair_stream']=stream; r['frozen_stream_sha256']=array_sha(np.asarray(stream,dtype=np.int64))
        r['status']='training'; save()
        for original_arm in base['arms']:
            guard(); kind=original_arm['kind']; normalized,stats=source_image(case,row,kind); image=physical_mr(normalized,grid)
            assert array_sha(image)==original_arm['physical_input_sha256']
            assert array_sha(target)==original_arm['physical_label_sha256']
            locations,starts=tile_plan(image.shape); assert locations==[tuple(v) for v in original_arm['tile_locations']]
            source_checkpoint=ROOT/original_arm['checkpoint_file']; assert sha(source_checkpoint)==original_arm['checkpoint_sha256']
            initial=torch.load(source_checkpoint,map_location='cpu',weights_only=True)['state_dict']
            model=TaskUNet3D(); model.load_state_dict(initial,strict=True); model.train()
            optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
            arm=dict(kind=kind,complete=False,evaluation_complete=False,updates_completed=0,history=[],
                     source_checkpoint_file=original_arm['checkpoint_file'],source_checkpoint_sha256=sha(source_checkpoint),
                     initial_weights_sha256=state_hash(initial),physical_input_sha256=array_sha(image),
                     physical_label_sha256=array_sha(target),observed_statistics=stats,
                     tile_locations=[list(v) for v in locations],axis_starts=starts,all_parameters_trainable=True,
                     empty_tiles_retained=True,augmentation_used=False)
            r['arms'].append(arm); save(); arm_started=time.perf_counter()
            for step,pair in enumerate(stream):
                if step%16==0:guard()
                slabs=[tuple(slice(s,s+p) for s,p in zip(locations[i],PATCH)) for i in pair]
                x=torch.from_numpy(np.stack([image[sl] for sl in slabs])[:,None])
                y=torch.from_numpy(np.stack([target[sl] for sl in slabs])[:,None])
                optimizer.zero_grad(set_to_none=True); outputs=model(x); value=loss(outputs,y)
                assert torch.isfinite(value); value.backward()
                assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
                if step==0:
                    arm['first_update_branch_gradient_max']={name:max(float(p.grad.abs().max()) for p in module.parameters() if p.grad is not None)
                        for name,module in (('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads))}
                    assert all(v>0 for v in arm['first_update_branch_gradient_max'].values())
                optimizer.step(); arm['updates_completed']=step+1; r['actual_cpu_backbone_updates']+=1
                arm['history'].append(dict(update=step+1,tile_indices=pair,label_foreground=[int(v.sum()) for v in y],
                    loss=float(value.detach()),lr=.001,elapsed_seconds=time.perf_counter()-arm_started))
                if step==31:
                    arm['first32_seconds_per_update']=(time.perf_counter()-arm_started)/32
                    assert arm['first32_seconds_per_update']*2048<=5000,'Actual fixed-stream time projection exceeded 5000 sec training allowance'
                if (step+1)%32==0:
                    save(); print(json.dumps(dict(kind=kind,updates=step+1,loss=float(value.detach()),
                        elapsed_seconds=time.perf_counter()-arm_started)),flush=True)
            state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
            arm['changed_state_entries']=[k for k in state if not torch.equal(state[k],initial[k])]
            assert any(k.startswith('encoders.') for k in arm['changed_state_entries'])
            assert any(k.startswith('decoders.') for k in arm['changed_state_entries'])
            dest=OUT/(kind+'_last1024.pt')
            torch.save(dict(state_dict=state,kind=kind,updates=1024,seed=SEED,final_weights_sha256=state_hash(state),
                source_checkpoint_sha256=sha(source_checkpoint),protocol_sha256=sha(sources[3]),
                execution_addendum_sha256=sha(sources[4]),frozen_stream_sha256=r['frozen_stream_sha256']),dest)
            arm.update(complete=True,checkpoint_file=dest.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(dest),
                       final_weights_sha256=state_hash(state),training_elapsed_seconds=time.perf_counter()-arm_started)
            save(); del model,optimizer,state,initial,x,y,outputs,value,image,normalized
        r['both_last_checkpoints_frozen_utc']=datetime.now(timezone.utc).isoformat(); r['status']='evaluating'; save()
        for arm in r['arms']:
            guard(); normalized,stats=source_image(case,row,arm['kind']); image=physical_mr(normalized,grid)
            checkpoint=ROOT/arm['checkpoint_file']; assert sha(checkpoint)==arm['checkpoint_sha256']
            state=torch.load(checkpoint,map_location='cpu',weights_only=True)['state_dict']
            model=TaskUNet3D(); model.load_state_dict(state,strict=True); model.eval()
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED))
            with torch.inference_mode():patch_logits=model(x)[0].numpy()[:,0]
            arm['original_augmented_patch_metrics']=[logical_counts(p>=0,g>=.5) for p,g in zip(patch_logits,y.numpy()[:,0])]
            probability,inference=infer_full_fov(model,image,grid,case['native_shape'])
            prediction=probability>=.5; zs=np.arange(label.shape[2]); last=zs[zs%4==0][-1]
            domains=dict(full=np.ones(len(zs),bool),anchors=zs%4==0,missing=(zs<last)&(zs%4!=0),tail=zs>last)
            metrics={name:logical_counts(prediction[:,:,mask],label[:,:,mask]) for name,mask in domains.items()}
            full=metrics['full']; crop=arm['original_augmented_patch_metrics'][0]
            gate=dict(foreground_patch_dice=crop['dice'] is not None and crop['dice']>=.9,
                training_full_dice=full['dice'] is not None and full['dice']>=.9,
                training_full_recall=full['recall'] is not None and full['recall']>=.9,
                training_full_absRVE=full['absRVE'] is not None and full['absRVE']<=.25,training_tp_positive=full['tp']>0)
            dest=OUT/(arm['kind']+'_full_fov.npz'); np.savez_compressed(dest,probability_rcz=probability,prediction_rcz=prediction)
            arm.update(evaluation_complete=True,metrics=metrics,inference=inference,training_fit_gate=gate,
                       training_fit_gate_passed=all(gate.values()),prediction_file=dest.relative_to(ROOT).as_posix(),prediction_sha256=sha(dest))
            save(); print(json.dumps(dict(kind=arm['kind'],full_dice=full['dice'],fit_gate=gate)),flush=True)
            del model,state,x,y,patch_logits,probability,prediction,image,normalized
        r['cuda_initialized']=torch.cuda.is_initialized(); assert not r['cuda_initialized']
        r['resources_after']=guard(); r['saved_bytes']=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())
        assert r['saved_bytes']<=120_000_000
        r['complete']=r['actual_cpu_backbone_updates']==2048 and all(a['complete'] and a['evaluation_complete'] for a in r['arms'])
        r['both_original_fit_gates_passed']=all(a['training_fit_gate_passed'] for a in r['arms']); r['status']='completed'
    except Exception as e:
        r['status']='failed'; r['errors'].append(type(e).__name__+': '+str(e)); r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat(); r['elapsed_seconds']=time.perf_counter()-started; save()
    print(json.dumps({k:r.get(k) for k in ('status','complete','errors','actual_cpu_backbone_updates',
        'both_original_fit_gates_passed','cuda_initialized','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__': raise SystemExit(main())
