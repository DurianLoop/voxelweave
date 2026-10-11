"""Two exact full-tile cached-feature linear-head fits on one development series, CPU only."""
import json,sys,time,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,physical_mr,lattice,
    physical_label,read_reference_label,sample_batch,TaskUNet3D,tile_plan,PATCH,torch,np,F,SEED)
from mc_rc_3d_independent_replay_2026_10_07 import independent_inference,functional_forward,logical_counts
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_all_tile_head_fit_2026_10_07'
FIT=ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07'
PREFIX='heads.2.'
def objective(z,y):
    ce=F.binary_cross_entropy_with_logits(z,y);p=z.sigmoid();sd=(2*(p*y).sum()+1)/(p.sum()+y.sum()+1)
    return (ce+1-sd)*4/7,ce,sd
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt01.json';started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],arms=[],
           script_sha256=sha(__file__),source_bindings=[],actual_patient_cpu_head_parameter_updates=0,
           actual_patient_gpu_updates=0,validation_effects_opened=False,confirmation_patients_opened=False,
           scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-started<=3600,'Frozen wall-clock budget exceeded'
        return resource_guard()
    save()
    try:
        localfit=ROOT/'experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07/attempt01.json'
        localproof=ROOT/'experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07/module_full_fov_verification_attempt01.json'
        lf,lp=read(localfit),read(localproof);assert lf['complete'] and lp['complete'] and not lf['errors'] and not lp['errors']
        assert lp['result_sha256']==sha(localfit)
        prod=read(FIT/'attempt_01.json');assert prod['complete'] and not prod['errors']
        sources=[ROOT/'MC_RC_3D_ALL_TILE_HEAD_FIT_PROTOCOL_2026-10-07.md',localfit,localproof,
                 FIT/'attempt_01.json',ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py']
        sources += [ROOT/s['path'] for s in prod['source_bindings']]+[ROOT/a['checkpoint_file'] for a in prod['arms']]
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(sources))]
        for s in prod['source_bindings']:assert sha(ROOT/s['path'])==s['sha256']
        r['resources_before']=guard();role,case,row=fixed_cases()[0];assert role=='development' and case['patient']=='VS-MC-RC-001'
        r['training_patient_ids']=[case['patient']];r['series_uid']=case['uid'];grid=lattice(case)
        label_native=read_reference_label(case);target=physical_label(label_native,grid)
        assert array_sha(target)==prod['physical_label_sha256']
        vox=int(np.prod(PATCH))
        for base in prod['arms']:
            guard();normalized,stats=source_image(case,row,base['kind']);image=physical_mr(normalized,grid)
            assert array_sha(image)==base['physical_input_sha256'] and stats==base['observed_statistics']
            locations,starts=tile_plan(image.shape);assert len(locations)==16
            cp=ROOT/base['checkpoint_file'];assert sha(cp)==base['checkpoint_sha256']
            original=torch.load(cp,map_location='cpu',weights_only=True)['state_dict']
            model=TaskUNet3D();model.load_state_dict(original,strict=True);model.eval();model.requires_grad_(False)
            matrix=torch.empty((len(locations)*vox,16),dtype=torch.float32);truth=torch.empty(len(locations)*vox,dtype=torch.float32)
            cache=[];handle=model.heads[-1].register_forward_pre_hook(lambda module,args:cache.append(args[0].detach()))
            labels=[];initial_errors=[]
            for at in range(0,len(locations),2):
                guard();group=locations[at:at+2];slabs=[tuple(slice(s,s+p) for s,p in zip(start,PATCH)) for start in group]
                x=torch.from_numpy(np.stack([image[sl] for sl in slabs])[:,None]);y=torch.from_numpy(np.stack([target[sl] for sl in slabs])[:,None])
                with torch.inference_mode():out=model(x)
                assert len(cache)==1;features=cache.pop();m=features.permute(0,2,3,4,1).reshape(-1,16)
                matrix[at*vox:(at+len(group))*vox]=m;truth[at*vox:(at+len(group))*vox]=y.reshape(-1)
                w0=original[PREFIX+'weight'].reshape(1,16);b0=original[PREFIX+'bias']
                with torch.inference_mode():z0=F.linear(m,w0,b0).reshape_as(y)
                error=float((z0.sigmoid()-out[0].sigmoid()).abs().max());assert error<=3e-6 and torch.equal(z0>=0,out[0]>=0)
                initial_errors.append(error);labels.extend(int(t.sum()) for t in y)
                del x,y,out,features,m,z0
            handle.remove();del model,cache
            arm=dict(kind=base['kind'],complete=False,evaluation_complete=False,updates_completed=0,
                     source_checkpoint_file=base['checkpoint_file'],source_checkpoint_sha256=sha(cp),
                     physical_input_sha256=base['physical_input_sha256'],physical_label_sha256=prod['physical_label_sha256'],
                     tile_locations=[list(p) for p in locations],axis_starts=starts,tiles=16,
                     label_foreground_by_tile=labels,training_voxels_including_overlap=int(truth.numel()),
                     label_foreground_including_overlap=int(truth.sum()),feature_matrix_bytes=matrix.numel()*matrix.element_size(),
                     feature_matrix_sha256=array_sha(matrix.numpy()),label_vector_sha256=array_sha(truth.numpy()),
                     initial_linear_vs_conv_probability_max_error=max(initial_errors),initial_prediction_disagreements=0,
                     trainable_parameters=17,history=[])
            r['arms'].append(arm);save()
            w=original[PREFIX+'weight'].reshape(-1).clone().requires_grad_(True);b=original[PREFIX+'bias'][0].clone().requires_grad_(True)
            opt=torch.optim.AdamW([w,b],lr=.01,weight_decay=.0001);arm_started=time.perf_counter()
            for step in range(1024):
                if step%32==0:guard()
                opt.zero_grad(set_to_none=True);z=F.linear(matrix,w[None],b[None]).reshape(-1)
                loss,ce,sd=objective(z,truth);assert torch.isfinite(loss);loss.backward()
                assert torch.isfinite(w.grad).all() and torch.isfinite(b.grad);opt.step()
                arm['updates_completed']=step+1;r['actual_patient_cpu_head_parameter_updates']+=1
                h=dict(update=step+1,bce=float(ce.detach()),soft_dice=float(sd.detach()),weighted_loss=float(loss.detach()),lr=.01)
                arm['history'].append(h)
                if step==31:
                    seconds=(time.perf_counter()-arm_started)/32;arm['first32_seconds_per_update']=seconds
                    assert seconds*2048<=3600,'Frozen two-arm training projection exceeded'
                if (step+1)%64==0:
                    save();print(json.dumps(dict(kind=base['kind'],update=step+1,soft_dice=h['soft_dice'])),flush=True)
            with torch.inference_mode():
                z=F.linear(matrix,w[None],b[None]).reshape(-1);loss,ce,sd=objective(z,truth)
                arm['final_training_objective']=dict(bce=float(ce),soft_dice=float(sd),weighted_loss=float(loss))
                arm['last_all_tile_metrics']=[logical_counts(p>=0,g>=.5) for p,g in zip(z.numpy().reshape(16,*PATCH),truth.numpy().reshape(16,*PATCH))]
            final={k:v.clone() for k,v in original.items()};final[PREFIX+'weight']=w.detach().reshape_as(final[PREFIX+'weight']).clone()
            final[PREFIX+'bias']=b.detach().reshape_as(final[PREFIX+'bias']).clone()
            for k in final:
                if not k.startswith(PREFIX):assert torch.equal(final[k],original[k])
            dest=OUT/(base['kind']+'_last1024.pt');torch.save(dict(state_dict=final,kind=base['kind'],updates=1024,
                final_weights_sha256=state_hash(final),source_checkpoint_sha256=sha(cp),
                protocol_sha256=sha(ROOT/'MC_RC_3D_ALL_TILE_HEAD_FIT_PROTOCOL_2026-10-07.md')),dest)
            arm.update(complete=True,checkpoint_file=dest.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(dest),
                       final_weights_sha256=state_hash(final),fixed_backbone_state_entries=52,
                       training_elapsed_seconds=time.perf_counter()-arm_started,final_bias=float(b.detach()),final_weights=[float(v) for v in w.detach()])
            save();del matrix,truth,w,b,opt,z,loss,ce,sd,original,final,image,normalized
        r['all_checkpoints_frozen_before_evaluation_utc']=datetime.now(timezone.utc).isoformat();save()
        for arm in r['arms']:
            guard();normalized,stats=source_image(case,row,arm['kind']);image=physical_mr(normalized,grid)
            state=torch.load(ROOT/arm['checkpoint_file'],map_location='cpu',weights_only=True)['state_dict']
            assert state_hash(state)==arm['final_weights_sha256']
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED))
            with torch.inference_mode():outputs=functional_forward(x,state)
            arm['original_fixed_batch_patch_metrics']=[logical_counts(p>=0,g>=.5) for p,g in zip(outputs[0].numpy()[:,0],y.numpy()[:,0])]
            probability,inference=independent_inference(state,image,grid,case['native_shape']);prediction=probability>=.5
            zs=np.arange(label_native.shape[2]);last=zs[zs%4==0][-1]
            domains=dict(full=np.ones(len(zs),bool),anchors=zs%4==0,missing=(zs<last)&(zs%4!=0),tail=zs>last)
            metrics={k:logical_counts(prediction[:,:,mask],label_native[:,:,mask]) for k,mask in domains.items()}
            m=metrics['full'];gate=dict(foreground_patch_dice=arm['original_fixed_batch_patch_metrics'][0]['dice'] is not None and arm['original_fixed_batch_patch_metrics'][0]['dice']>=.9,
                training_full_dice=m['dice'] is not None and m['dice']>=.9,training_full_recall=m['recall'] is not None and m['recall']>=.9,
                training_full_absRVE=m['absRVE'] is not None and m['absRVE']<=.25,training_tp_positive=m['tp']>0)
            dest=OUT/(arm['kind']+'_full_fov.npz');np.savez_compressed(dest,probability_rcz=probability,prediction_rcz=prediction)
            arm.update(evaluation_complete=True,metrics=metrics,inference=inference,training_fit_gate=gate,training_fit_gate_passed=all(gate.values()),
                       prediction_file=dest.relative_to(ROOT).as_posix(),prediction_sha256=sha(dest))
            save();print(json.dumps(dict(kind=arm['kind'],original_patch_dice=arm['original_fixed_batch_patch_metrics'][0]['dice'],
                                        full_fov_dice=m['dice'],fit_gate_passed=arm['training_fit_gate_passed'])),flush=True)
            del normalized,image,state,x,y,outputs,probability,prediction
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        r['resources_after']=guard();r['saved_bytes']=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
        assert r['saved_bytes']<=60_000_000
        r['complete']=len(r['arms'])==2 and all(a['complete'] and a['evaluation_complete'] and a['updates_completed']==1024 for a in r['arms'])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','actual_patient_cpu_head_parameter_updates','cuda_initialized','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
