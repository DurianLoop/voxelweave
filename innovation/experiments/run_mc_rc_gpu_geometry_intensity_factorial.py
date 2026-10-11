"""Four fresh same-device20k arms; zero validation inference during training."""
from mc_rc_authorized_gpu_adapter import enable_authorized_gpu,CpuGeometryGpuBranches,gpu_resource_gate
import hashlib,json,math,sys,time,traceback
from datetime import datetime,timezone
from mc_rc_global_local_task_cpu_support import (
    ROOT,SEED,DEVELOPERS,GlobalLocalUNet,weight_hash,read,sha,array_sha,
    load_authenticated_observed,sparse_image,physical_shape,resize_image,resize_training_label,
    context_tiles,segmentation_loss,np,torch)
from mc_rc_task_metrics_cpu import independent_label
from mc_rc_coverage_augmentation_draw_cpu_support import legacy_primitive,record_sha,example_from_record,example_sha
from mc_rc_partial_augmentation_cpu_support import partial_example
OUT=ROOT/'experiments/mc_rc_gpu_geometry_intensity_factorial'
ARMS=('none','both','geometry_only','intensity_only')


def write(path,r):path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def state_hash(state):
    h=hashlib.sha256()
    for name,value in state.items():h.update(name.encode());h.update(array_sha(value.numpy()).encode())
    return h.hexdigest()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sources=[ROOT/'experiments/mc_rc_no_augmentation_all_development_cpu/attempt_01.json',
        ROOT/'experiments/mc_rc_no_augmentation_all_development_cpu/independent_all20000_draws_and_checkpoint_attempt_01.json',
        ROOT/'experiments/mc_rc_no_augmentation_full_task_evaluation_gpu/attempt_01.json',
        ROOT/'experiments/mc_rc_no_augmentation_full_task_evaluation_gpu/independent_all37_metrics_and111_planes_attempt_01.json',
        ROOT/'experiments/mc_rc_partial_augmentation_development_cpu_preflight/attempt_01.json',
        ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json',
        ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json',
        ROOT/'experiments/mc_rc_authorized_gpu_runtime_preflight/attempt_01.json']
    old,proof,evaluation,evproof,preflight,prep,prod,runtimeproof=[read(p) for p in sources]
    assert all(v['complete'] and not v['errors'] for v in (old,proof,evaluation,evproof,preflight,prep,prod,runtimeproof))
    assert proof['result_sha256']==sha(sources[0]) and proof['full_patch_source_mapping_checks']==40000
    assert evproof['result_sha256']==sha(sources[2]) and evproof['checkpoint_replayed_planes']==111
    assert not evaluation['capability_gate_passed'] and preflight['partial_arm_reference_input_checks']==1216
    assert runtimeproof['adapter_sha256']==sha(ROOT/'experiments/mc_rc_authorized_gpu_adapter.py')
    assert len(prep['cases'])==19 and {c['patient'] for c in prep['cases']}==DEVELOPERS
    for binding in old['source_bindings']+old['code_bindings']+preflight['source_bindings']+preflight['code_bindings']:
        assert sha(ROOT/binding['path'])==binding['sha256']
    OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    protocol=ROOT/'MC_RC_GPU_GEOMETRY_INTENSITY_FACTORIAL_PROTOCOL_2026-10-03.md'
    code=('mc_rc_authorized_gpu_adapter.py','mc_rc_global_local_task_cpu_support.py',
          'mc_rc_partial_augmentation_cpu_support.py','mc_rc_coverage_augmentation_draw_cpu_support.py',
          'mc_rc_task_metrics_cpu.py')
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        script_sha256=sha(__file__),protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources],
        code_bindings=[dict(path='experiments/'+s,sha256=sha(ROOT/'experiments'/s)) for s in code],
        seed=SEED,device='cuda:0',arms=[],arm_order=list(ARMS),inputs=[],planned_updates_per_arm=20000,
        planned_total_updates=80000,total_updates_completed=0,validation_neural_forwards_before_all_checkpoints=0,
        pretrained_weights_loaded=False,old_cpu_arms_reused_as_gpu_controls=False,
        native_hidden_MR_pixels_decoded=False,confirmation_patients_opened=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,r)
    try:
        r['runtime']=enable_authorized_gpu();gpu_resource_gate()
        by={v['uid']:v for v in prod['series']};frozen_inputs={v['uid']:v for v in old['inputs']};cache={}
        for case in prep['cases']:
            gpu_resource_gate();uid=case['uid'];obs=load_authenticated_observed(case,by[uid])
            native,stats=sparse_image(obs,'raw_pchip',by[uid]);label=independent_label(case)
            shape,spacing=physical_shape(case);image=resize_image(native,shape);target=resize_training_label(label,shape)
            values=dict(native_input_sha256=array_sha(native),native_label_sha256=array_sha(label),
                physical_image_sha256=array_sha(image),physical_label_sha256=array_sha(target))
            assert all(frozen_inputs[uid][key]==value for key,value in values.items())
            cache[uid]=dict(image_zrc=image,label_zrc=target,native_foreground=np.argwhere(label),zspacing=spacing)
            r['inputs'].append(dict(patient=case['patient'],uid=uid,**values,observed_statistics=stats,physical_shape=list(image.shape)))
        patients=sorted(DEVELOPERS);patient_cases={p:[c for c in prep['cases'] if c['patient']==p] for p in patients}
        r['cache_bytes']=sum(v['image_zrc'].nbytes+v['label_zrc'].nbytes+v['native_foreground'].nbytes for v in cache.values())
        for arm_name in ARMS:
            gpu_resource_gate();torch.manual_seed(SEED);raw=GlobalLocalUNet()
            initial=weight_hash(raw);assert initial==old['initial_weights_sha256']
            assert sum(p.numel() for p in raw.parameters())==981602
            model=CpuGeometryGpuBranches(raw);raw.train()
            opt=torch.optim.AdamW(raw.parameters(),lr=.001,weight_decay=.0001)
            rng=np.random.default_rng(SEED);stream=hashlib.sha256();losses=[]
            arm=dict(name=arm_name,complete=False,updates_completed=0,initial_weights_sha256=initial,
                example_sha256_by_step=[],primitive_matches_to_authenticated_cpu_stream=0,
                exact_existing_input_sha_checks=0,patient_sampling_counts={},series_sampling_counts={},training_history=[])
            r['arms'].append(arm);write(path,r);began=time.perf_counter()
            for step in range(20000):
                if step%100==0:gpu_resource_gate()
                patient=patients[int(rng.integers(len(patients)))];choices=patient_cases[patient]
                case=choices[int(rng.integers(len(choices)))];uid=case['uid'];item=cache[uid]
                primitive=legacy_primitive(item,rng,step,{});reference=old['training_draws'][step]
                assert reference['step']==step and reference['patient']==patient and reference['uid']==uid
                assert reference['z']==primitive['z'] and reference['native_patch_locations']==primitive['legacy_native_locations']
                assert reference['primitive_sha256']==record_sha(primitive);arm['primitive_matches_to_authenticated_cpu_stream']+=1
                example=(example_from_record(item,primitive,'legacy_none' if arm_name=='none' else 'legacy_aug')
                         if arm_name in ('none','both') else partial_example(item,primitive,arm_name))
                digest=example_sha(example);arm['example_sha256_by_step'].append(digest);stream.update(digest.encode())
                if arm_name in ('none','both'):
                    assert digest==reference['example_sha256' if arm_name=='none' else 'original_aug_example_sha256']
                    arm['exact_existing_input_sha_checks']+=1
                gv,x,y,gt,locations,fullshape,sample=example
                lr=.0001+.0009*(1+math.cos(math.pi*step/19999))/2
                for group in opt.param_groups:group['lr']=lr
                opt.zero_grad(set_to_none=True);features,coarse=model.global_forward(gv)
                logits=model.local_forward(x,context_tiles(features,locations,fullshape))
                local=segmentation_loss(logits,y);global_loss=segmentation_loss(coarse,gt);loss=local+.5*global_loss
                assert torch.isfinite(loss);loss.backward()
                grad_norms=torch.stack([p.grad.detach().abs().max() for p in raw.parameters() if p.grad is not None])
                assert torch.isfinite(grad_norms).all()
                if step==0:
                    arm['first_update_branch_gradients']={name:dict(parameters_with_gradient=sum(p.grad is not None for p in branch.parameters()),
                        maximum_absolute_gradient=max(float(p.grad.detach().abs().max()) for p in branch.parameters() if p.grad is not None))
                        for name,branch in (('global',raw.global_net),('local',raw.local_net))}
                    assert all(v['maximum_absolute_gradient']>0 for v in arm['first_update_branch_gradients'].values())
                opt.step();losses.append((float(loss.detach()),float(local.detach()),float(global_loss.detach())))
                arm['updates_completed']=step+1;r['total_updates_completed']+=1
                arm['patient_sampling_counts'][patient]=arm['patient_sampling_counts'].get(patient,0)+1
                arm['series_sampling_counts'][uid]=arm['series_sampling_counts'].get(uid,0)+1
                if step==9:
                    seconds=(time.perf_counter()-began)/10;arm['first10_seconds_per_update']=seconds
                    if arm_name=='none':
                        r['runtime_training_preflight']=dict(first10_real_updates_seconds_per_update=seconds,
                            projected_all80000_seconds=seconds*80000,maximum_projection_seconds=3600)
                        write(path,r);assert seconds*80000<=3600
                if (step+1)%100==0:
                    h=dict(update=step+1,mean_last100_loss=np.mean(losses[-100:],axis=0).tolist(),lr=lr,
                        elapsed_seconds=time.perf_counter()-began,resources=gpu_resource_gate())
                    arm['training_history'].append(h);write(path,r)
                    print(json.dumps(dict(arm=arm_name,update=step+1,total_updates=r['total_updates_completed'],mean_loss=h['mean_last100_loss'][0])),flush=True)
            cpu_state={key:value.detach().cpu().clone() for key,value in raw.state_dict().items()}
            final=state_hash(cpu_state);checkpoint=OUT/(arm_name+'_final_update_20000.pt')
            metadata=dict(state_dict=cpu_state,arm_name=arm_name,updates_completed=20000,seed=SEED,
                initial_weights_sha256=initial,final_weights_sha256=final,training_patient_ids=patients,
                training_series_uids=[c['uid'] for c in prep['cases']],protocol_sha256=r['protocol_sha256'],
                draw_stream_sha256=stream.hexdigest())
            torch.save(metadata,checkpoint)
            arm.update(final_weights_sha256=final,checkpoint_file=checkpoint.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(checkpoint),
                draw_stream_sha256=stream.hexdigest(),global_forward_calls=raw.global_calls,local_forward_calls=raw.local_calls,
                elapsed_seconds=time.perf_counter()-began)
            assert raw.global_calls==raw.local_calls==arm['primitive_matches_to_authenticated_cpu_stream']==20000
            assert arm['patient_sampling_counts']==old['training_sampling_counts'] and arm['series_sampling_counts']==old['training_series_counts']
            arm['complete']=True;write(path,r)
            del opt,model,raw,loss,local,global_loss,features,coarse,logits,grad_norms,cpu_state
            torch.cuda.empty_cache()
        r['gpu_initialized']=torch.cuda.is_initialized();r['resources_after']=gpu_resource_gate()
        assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<150000000
        r['complete']=r['total_updates_completed']==80000 and all(a['complete'] for a in r['arms'])
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','total_updates_completed','gpu_initialized')}),flush=True)
    return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
