"""Four fixed head-only fits on certified cached training features; CPU development diagnostic."""
import json,math,sys,time,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,physical_mr,
    lattice,physical_label,read_reference_label,sample_batch,TaskUNet3D,torch,np,F,SEED)
from mc_rc_3d_independent_replay_2026_10_07 import independent_inference,functional_forward,logical_counts
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
FIT=ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07'
OUT=ROOT/'experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07'
PROTOCOL=ROOT/'MC_RC_3D_FROZEN_FEATURE_HEAD_FIT_PROTOCOL_2026-10-07.md'
HEAD_PREFIX='heads.2.'
STEPS=1024

def head_loss(logits,truth):
    ce=F.binary_cross_entropy_with_logits(logits,truth)
    p=logits.sigmoid();sd=(2*(p*truth).sum()+1)/(p.sum()+truth.sum()+1)
    return ce+1-sd,ce,sd

def numpy_loss(logits,truth):
    z=logits.numpy().astype(np.float64);y=truth.numpy().astype(np.float64)
    p=1/(1+np.exp(-z));ce=float(np.mean(np.logaddexp(0,z)-y*z))
    sd=float((2*np.sum(p*y)+1)/(np.sum(p)+np.sum(y)+1))
    return dict(bce=ce,soft_dice=sd,loss=ce+1-sd)

def assert_fixed_backbone(original,new):
    assert set(original)==set(new)
    keys=[]
    for k in original:
        if not k.startswith(HEAD_PREFIX):assert torch.equal(original[k],new[k]);keys.append(k)
    return len(keys)

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt01.json';started=time.perf_counter()
    prod=read(FIT/'attempt_01.json');proof=read(FIT/'independent_both512_and_full_fov_2026_10_07.json')
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],arms=[],
           actual_patient_cpu_head_parameter_updates=0,actual_patient_gpu_updates=0,
           trainable_parameters_by_branch=dict(bias_only=1,full_head=17),planned_updates_per_branch=STEPS,
           total_planned_updates=4*STEPS,script_sha256=sha(__file__),protocol_sha256=sha(PROTOCOL),
           source_bindings=[],confirmation_patients_opened=False,validation_effects_opened=False,
           scientific_confirmation_patients=0,publication_claim_confirmed=False,
           second_independently_trained_task_network=False,goal_status='active')
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-started<=3600,'Frozen 3600-second wall limit exceeded'
        return resource_guard()
    save()
    try:
        sources=[PROTOCOL,FIT/'attempt_01.json',FIT/'independent_both512_and_full_fov_2026_10_07.json',
                 ROOT/'experiments/mc_rc_3d_final_patch_diagnostic_2026_10_07/attempt01.json',
                 ROOT/'SESSION_ARCHIVE_VERIFICATION_CPU_FIT_FOLLOWUP_2026-10-07.json',
                 ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',
                 ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
                 ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py',
                 ROOT/'experiments/run_mc_rc_3d_gpu_fit_pilot_2026_10_07.py']
        sources += [ROOT/b['path'] for b in prod['source_bindings']]+[ROOT/a['checkpoint_file'] for a in prod['arms']]
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(sources))]
        assert prod['complete'] and proof['complete'] and not prod['errors'] and not proof['errors']
        assert proof['result_sha256']==sha(FIT/'attempt_01.json') and prod['total_updates_completed']==1024
        for b in prod['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        r['resources_before']=guard();role,case,row=fixed_cases()[0]
        assert role=='development' and case['patient']=='VS-MC-RC-001'
        r['training_patient_ids']=[case['patient']];r['series_uid']=case['uid']
        grid=lattice(case);target=physical_label(read_reference_label(case),grid)
        assert array_sha(target)==prod['physical_label_sha256']
        for base in prod['arms']:
            guard();kind=base['kind'];image_normalized,stats=source_image(case,row,kind);image=physical_mr(image_normalized,grid)
            assert array_sha(image)==base['physical_input_sha256'] and stats==base['observed_statistics']
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED))
            assert primitive==base['primitive'] and array_sha(x.numpy())==base['input_batch_sha256'] and array_sha(y.numpy())==base['label_batch_sha256']
            cp=ROOT/base['checkpoint_file'];assert sha(cp)==base['checkpoint_sha256']
            stored=torch.load(cp,map_location='cpu',weights_only=True);original=stored['state_dict']
            assert state_hash(original)==base['final_weights_sha256']
            model=TaskUNet3D();model.load_state_dict(original,strict=True);model.eval();model.requires_grad_(False)
            cache=[]
            handle=model.heads[-1].register_forward_pre_hook(lambda module,args:cache.append(args[0].detach().clone()))
            with torch.no_grad():outputs=model(x)
            handle.remove();assert len(cache)==1
            feature=cache.pop();matrix=feature.permute(0,2,3,4,1).reshape(-1,16).contiguous();truth=y.reshape(-1)
            initial_w=original[HEAD_PREFIX+'weight'].reshape(-1).clone();initial_b=original[HEAD_PREFIX+'bias'][0].clone()
            with torch.no_grad():matrix_initial=F.linear(matrix,initial_w[None],initial_b[None]).reshape_as(y)
            initial_error=float((matrix_initial.sigmoid()-outputs[0].sigmoid()).abs().max())
            assert initial_error<=3e-6 and torch.equal(matrix_initial>=0,outputs[0]>=0)
            for gt,pred,metric in zip(y.numpy()[:,0]>=.5,outputs[0].sigmoid().numpy()[:,0]>=.5,base['patch_metrics']):
                assert logical_counts(pred,gt)==metric
            constant=0.
            for o,weight in zip(outputs[1:],(2/7,1/7)):
                t=F.interpolate(y,size=o.shape[2:],mode='nearest-exact');constant+=float(head_loss(o,t)[0])*weight
            feature_sha=array_sha(feature.numpy());del feature,outputs,matrix_initial,model,cache
            for branch in ('bias_only','full_head'):
                guard();w=initial_w.clone().requires_grad_(branch=='full_head');b=initial_b.clone().requires_grad_(True)
                params=[w,b] if branch=='full_head' else [b]
                opt=torch.optim.AdamW(params,lr=.01,weight_decay=.0001 if branch=='full_head' else 0)
                arm=dict(kind=kind,branch=branch,complete=False,evaluation_complete=False,updates_completed=0,
                         source_checkpoint_file=base['checkpoint_file'],source_checkpoint_sha256=sha(cp),
                         input_batch_sha256=base['input_batch_sha256'],label_batch_sha256=base['label_batch_sha256'],
                         feature_sha256=feature_sha,linear_vs_conv_probability_max_error=initial_error,
                         linear_vs_conv_prediction_disagreements=0,constant_auxiliary_contribution=constant,
                         trainable_parameters=sum(p.numel() for p in params),history=[])
                r['arms'].append(arm);save();arm_started=time.perf_counter()
                for step in range(STEPS):
                    if step%64==0:guard()
                    opt.zero_grad(set_to_none=True)
                    z=F.linear(matrix,w[None],b[None]).reshape(-1);fine,ce,sd=head_loss(z,truth);objective=fine*4/7
                    assert torch.isfinite(objective);objective.backward()
                    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in params)
                    if step==0:
                        with torch.no_grad():
                            probability=z.sigmoid();A=2*(probability*truth).sum()+1;B=probability.sum()+truth.sum()+1
                            gz=((probability-truth)/probability.numel()+(A-2*truth*B)/B.square()*probability*(1-probability))*4/7
                            db=gz.sum();assert torch.allclose(b.grad,db,rtol=2e-5,atol=1e-7)
                            errors=dict(bias=float((b.grad-db).abs()))
                            if branch=='full_head':
                                dw=matrix.T@gz;assert torch.allclose(w.grad,dw,rtol=2e-5,atol=1e-7)
                                errors['weight']=float((w.grad-dw).abs().max())
                            arm['first_step_closed_form_gradient_max_errors']=errors
                    opt.step();arm['updates_completed']=step+1;r['actual_patient_cpu_head_parameter_updates']+=1
                    h=dict(update=step+1,main_head_bce=float(ce.detach()),main_head_soft_dice=float(sd.detach()),
                           deep_supervision_loss=float(objective.detach())+constant,lr=.01)
                    arm['history'].append(h)
                    if step==31:
                        secs=(time.perf_counter()-arm_started)/32;arm['first32_seconds_per_update']=secs
                        assert secs*STEPS*4<=3600,'Four-branch update time projection exceeds frozen limit'
                    if (step+1)%128==0:
                        save();print(json.dumps(dict(kind=kind,branch=branch,update=step+1,soft_dice=h['main_head_soft_dice'])),flush=True)
                final={k:v.clone() for k,v in original.items()}
                final[HEAD_PREFIX+'weight']=w.detach().reshape_as(final[HEAD_PREFIX+'weight']).clone()
                final[HEAD_PREFIX+'bias']=b.detach().reshape_as(final[HEAD_PREFIX+'bias']).clone()
                fixed=assert_fixed_backbone(original,final)
                if branch=='bias_only':assert torch.equal(original[HEAD_PREFIX+'weight'],final[HEAD_PREFIX+'weight'])
                dest=OUT/(kind+'_'+branch+'_last1024.pt')
                torch.save(dict(state_dict=final,kind=kind,branch=branch,updates=STEPS,protocol_sha256=sha(PROTOCOL),
                                source_checkpoint_sha256=sha(cp),final_weights_sha256=state_hash(final)),dest)
                arm.update(complete=True,checkpoint_file=dest.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(dest),
                           final_weights_sha256=state_hash(final),fixed_backbone_state_entries=fixed,
                           training_elapsed_seconds=time.perf_counter()-arm_started,
                           final_weight=[float(v) for v in w.detach()],final_bias=float(b.detach()))
                save();del w,b,opt,params,z,fine,ce,sd,objective,final
            del x,y,matrix,truth,stored,original,image,image_normalized
        r['all_checkpoints_frozen_before_evaluation_utc']=datetime.now(timezone.utc).isoformat();save()
        # All four final states are now fixed. Functional network uses the same updated checkpoint independently.
        native_label=read_reference_label(case)
        for arm in r['arms']:
            guard();normalized,stats=source_image(case,row,arm['kind']);image=physical_mr(normalized,grid)
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED))
            assert array_sha(x.numpy())==arm['input_batch_sha256'] and array_sha(y.numpy())==arm['label_batch_sha256']
            cp=ROOT/arm['checkpoint_file'];assert sha(cp)==arm['checkpoint_sha256']
            state=torch.load(cp,map_location='cpu',weights_only=True)['state_dict'];assert state_hash(state)==arm['final_weights_sha256']
            with torch.inference_mode():patch_logits=functional_forward(x,state)[0];patch_p=patch_logits.sigmoid()
            _,ce,sd=head_loss(patch_logits,y);independent_loss=numpy_loss(patch_logits,y)
            assert abs(float(ce)-independent_loss['bce'])<=3e-6 and abs(float(sd)-independent_loss['soft_dice'])<=3e-6
            arm['final_main_head_numpy_loss']=independent_loss
            arm['patch_metrics']=[logical_counts(p>=.5,g>=.5) for p,g in zip(patch_p.numpy()[:,0],y.numpy()[:,0])]
            arm['background_probability_mean']=float(patch_p[~y.bool()].mean())
            arm['foreground_probability_mean']=float(patch_p[y.bool()].mean())
            probability,inference=independent_inference(state,image,grid,case['native_shape'])
            prediction=probability>=.5;zs=np.arange(native_label.shape[2]);last=zs[zs%4==0][-1]
            domains=dict(full=np.ones(len(zs),bool),anchors=zs%4==0,missing=(zs<last)&(zs%4!=0),tail=zs>last)
            arm['metrics']={k:logical_counts(prediction[:,:,mask],native_label[:,:,mask]) for k,mask in domains.items()}
            dest=OUT/(arm['kind']+'_'+arm['branch']+'_full_fov.npz')
            np.savez_compressed(dest,probability_rcz=probability,prediction_rcz=prediction)
            m=arm['metrics']['full'];gate=dict(foreground_patch_dice=arm['patch_metrics'][0]['dice'] is not None and arm['patch_metrics'][0]['dice']>=.9,
                training_full_dice=m['dice'] is not None and m['dice']>=.9,training_full_recall=m['recall'] is not None and m['recall']>=.9,
                training_full_absRVE=m['absRVE'] is not None and m['absRVE']<=.25,training_tp_positive=m['tp']>0)
            arm.update(prediction_file=dest.relative_to(ROOT).as_posix(),prediction_sha256=sha(dest),inference=inference,
                       training_fit_gate=gate,training_fit_gate_passed=all(gate.values()),evaluation_complete=True)
            save();print(json.dumps(dict(kind=arm['kind'],branch=arm['branch'],patch_dice=arm['patch_metrics'][0]['dice'],
                                        full_fov_dice=m['dice'],fit_gate_passed=arm['training_fit_gate_passed'])),flush=True)
            del normalized,image,x,y,state,patch_logits,patch_p,probability,prediction
        assert not torch.cuda.is_initialized();r['cuda_initialized']=False
        r['complete']=len(r['arms'])==4 and all(a['updates_completed']==STEPS and a['evaluation_complete'] for a in r['arms'])
        r['resources_after']=guard();r['saved_bytes']=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
        assert r['saved_bytes']<=100_000_000
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','actual_patient_cpu_head_parameter_updates','cuda_initialized','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
