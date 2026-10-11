"""Actual 2x512 CPU fit, all checkpoints before any full-FOV effect, no CUDA init."""
import hashlib
import json
import math
import sys
import time
import traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,lattice,physical_mr,physical_label,
    read_reference_label,TaskUNet3D,loss,sample_batch,infer_full_fov,torch,np,SEED,PATCH)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash,count
OUT=ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07'

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    began=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,status='preparing',errors=[],arms=[],
           total_updates_completed=0,actual_gpu_updates=0,device='cpu',seed=SEED,
           planned_updates_per_arm=512,planned_total_updates=1024,arm_order=['native_reference','raw_pchip'],
           scientific_confirmation_patients=0,publication_claim_confirmed=False,confirmation_patients_opened=False,
           script_sha256=sha(__file__),source_bindings=[],validation_full_fov_effects_computed=0,
           all_checkpoints_before_any_full_fov_effect=True,max_training_projection_seconds=7200,max_total_runtime_seconds=9000)
    sourcepaths=['MC_RC_3D_CPU_FIXED_FIT_PROTOCOL_2026-10-07.md','experiments/mc_rc_3d_baseline_2026_10_07.py',
                 'experiments/mc_rc_3d_baseline_v2_2026_10_07.py','experiments/mc_rc_reference_resources_2026_10_07.py',
                 'experiments/mc_rc_true_native_reference_2026_10_07.py','experiments/mc_rc_true_native_reference_v2_2026_10_07.py',
                 'experiments/mc_rc_observed_only_training_input.py','experiments/run_mc_rc_3d_gpu_fit_pilot_2026_10_07.py',
                 'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json',
                 'experiments/mc_rc_true_native_reference_attempt02_2026_10_07/independent_all28_pixels_and_labels_2026_10_07.json',
                 'experiments/mc_rc_3d_real_batch_cpu_2026_10_07/attempt_01.json',
                 'experiments/mc_rc_3d_sparse_source_isolation_2026_10_07/attempt_01.json']
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-began<=9000,'Frozen CPU total runtime bound exceeded'
        assert not torch.cuda.is_initialized(),'CPU diagnostic initialized CUDA'
        return resource_guard()
    save()
    try:
        for index in (8,9,10,11):
            p=read(ROOT/sourcepaths[index]);assert p['complete'] and not p['errors']
        r['source_bindings']=[dict(path=p,sha256=sha(ROOT/p)) for p in sourcepaths]
        for binding in read(ROOT/sourcepaths[8])['source_bindings']:assert sha(ROOT/binding['path'])==binding['sha256']
        r['resources_before']=guard()
        role,case,row=fixed_cases()[0];assert role=='development' and case['patient']=='VS-MC-RC-001'
        assert case['uid']=='1.3.6.1.4.1.14519.5.2.1.10875952303942319530925289292568369177'
        grid=lattice(case);label=read_reference_label(case);target=physical_label(label,grid)
        certified={x['uid']:x for x in read(ROOT/sourcepaths[8])['series']}[case['uid']]
        assert array_sha(target)==certified['physical_label_sha256']
        r.update(training_patient_ids=[case['patient']],training_series_uids=[case['uid']],native_shape=case['native_shape'],
                 physical_grid=grid,native_label_sha256=array_sha(label),physical_label_sha256=array_sha(target))
        cache={};reference_initial=None;reference_primitives=None;reference_targets=None
        real_cpu=read(ROOT/sourcepaths[10]);first_step_by={a['kind']:a for a in real_cpu['arms']}
        r['status']='training';save()
        for kind in r['arm_order']:
            guard();normalized,st=source_image(case,row,kind);image=physical_mr(normalized,grid)
            assert array_sha(image)==certified['inputs'][kind]['physical_image_sha256']
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED))
            xsha,ysha=array_sha(x.numpy()),array_sha(y.numpy())
            torch.manual_seed(SEED);model=TaskUNet3D();initial=state_hash(model.state_dict())
            if reference_initial is None:reference_initial=initial;reference_primitives=primitive;reference_targets=ysha
            else:assert initial==reference_initial and primitive==reference_primitives and ysha==reference_targets
            assert initial==first_step_by[kind]['initial_weights_sha256'] and xsha==first_step_by[kind]['input_batch_sha256']
            assert ysha==first_step_by[kind]['label_batch_sha256'] and primitive==first_step_by[kind]['primitive']
            opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001);model.train()
            arm=dict(kind=kind,complete=False,updates_completed=0,initial_weights_sha256=initial,
                     input_batch_sha256=xsha,label_batch_sha256=ysha,primitive=primitive,physical_input_sha256=array_sha(image),
                     observed_statistics=st,history=[],every_update_history=[])
            r['arms'].append(arm);save();started=time.perf_counter()
            for step in range(512):
                if step%16==0:guard()
                lr=.0001+.0009*(1+math.cos(math.pi*step/511))/2
                for group in opt.param_groups:group['lr']=lr
                opt.zero_grad(set_to_none=True);outputs=model(x);value=loss(outputs,y)
                assert torch.isfinite(value);value.backward()
                grads=[p.grad for p in model.parameters()];assert all(g is not None and torch.isfinite(g).all() for g in grads)
                if step==0:
                    branch={name:max(float(p.grad.abs().max()) for p in collection.parameters())
                            for name,collection in (('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads))}
                    assert all(v>0 for v in branch.values());arm['first_update_gradients']=branch
                    assert float(value.detach())==first_step_by[kind]['loss']
                opt.step();arm['updates_completed']=step+1;r['total_updates_completed']+=1
                if step==0:
                    assert state_hash(model.state_dict())==first_step_by[kind]['after_one_cpu_update_weights_sha256']
                    arm['first_update_matches_prior_authenticated_cpu_step']=True
                arm['every_update_history'].append(dict(update=step+1,loss=float(value.detach()),lr=lr))
                if (step+1)%8==0:
                    history=dict(update=step+1,loss=float(value.detach()),lr=lr,elapsed_seconds=time.perf_counter()-started,resources=guard())
                    arm['history'].append(history);save()
                    print(json.dumps(dict(arm=kind,update=step+1,total_updates=r['total_updates_completed'],loss=history['loss'],elapsed_seconds=history['elapsed_seconds'])),flush=True)
                if step==31:
                    seconds=(time.perf_counter()-started)/32;arm['first32_seconds_per_update']=seconds
                    arm['projected_1024_updates_seconds']=seconds*1024;save()
                    assert seconds*1024<=7200,'Frozen new CPU projection exceeded'
            state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
            checkpoint=OUT/(kind+'_last_512.pt')
            torch.save(dict(state_dict=state,kind=kind,updates=512,seed=SEED,initial_weights_sha256=initial,
                           final_weights_sha256=state_hash(state),protocol_sha256=sha(ROOT/sourcepaths[0]),
                           physical_input_sha256=arm['physical_input_sha256'],label_batch_sha256=ysha,primitive=primitive),checkpoint)
            arm.update(complete=True,checkpoint_file=checkpoint.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(checkpoint),
                       final_weights_sha256=state_hash(state),training_elapsed_seconds=time.perf_counter()-started)
            cache[kind]=(image,x,y);save();del model,opt,state,outputs,value,grads,normalized
        assert r['total_updates_completed']==1024 and all(a['complete'] for a in r['arms'])
        r['status']='full_fov_evaluation';r['all_checkpoints_frozen_before_full_fov_utc']=datetime.now(timezone.utc).isoformat();save()
        for arm in r['arms']:
            guard();kind=arm['kind'];image,x,y=cache[kind]
            checkpoint=ROOT/arm['checkpoint_file'];assert sha(checkpoint)==arm['checkpoint_sha256']
            stored=torch.load(checkpoint,map_location='cpu',weights_only=True);model=TaskUNet3D();model.load_state_dict(stored['state_dict'],strict=True);model.eval()
            assert state_hash(model.state_dict())==arm['final_weights_sha256']
            with torch.inference_mode():patch_predictions=model(x)[0].sigmoid().numpy()[:,0]>=.5
            truth=y.numpy()[:,0]>=.5;arm['patch_metrics']=[count(p,g) for p,g in zip(patch_predictions,truth)]
            probabilities,coverage=infer_full_fov(model,image,grid,case['native_shape'],device='cpu')
            prediction=probabilities>=.5;metrics=dict(full=count(prediction,label))
            z=np.arange(label.shape[2]);last=int(z[z%4==0][-1])
            for name,domain in (('anchors',z%4==0),('missing',(z<last)&(z%4!=0)),('tail',z>last)):
                metrics[name]=count(prediction[:,:,domain],label[:,:,domain])
            predpath=OUT/(kind+'_full_fov_prediction.npz');np.savez_compressed(predpath,prediction_rcz=prediction,probability_rcz=probabilities)
            full=metrics['full'];gate=dict(foreground_patch_dice=arm['patch_metrics'][0]['dice'] is not None and arm['patch_metrics'][0]['dice']>=.9,
                training_full_dice=full['dice'] is not None and full['dice']>=.9,training_full_recall=full['recall'] is not None and full['recall']>=.9,
                training_full_absRVE=full['absRVE'] is not None and full['absRVE']<=.25,training_tp_positive=full['tp']>0)
            arm.update(prediction_file=predpath.relative_to(ROOT).as_posix(),prediction_sha256=sha(predpath),metrics=metrics,
                       inference=coverage,training_fit_gate=gate,training_fit_gate_passed=all(gate.values()),evaluation_complete=True,resources_after=guard())
            save();print(json.dumps(dict(kind=kind,patch_dice=arm['patch_metrics'][0]['dice'],full=full,fit_gate=all(gate.values()))),flush=True)
            del model,stored,patch_predictions,probabilities,prediction
        r['both_training_fit_gates_passed']=all(a['training_fit_gate_passed'] for a in r['arms'])
        r['complete']=all(a['evaluation_complete'] for a in r['arms']) and r['total_updates_completed']==1024
        r['saved_bytes']=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file());assert r['saved_bytes']<=250_000_000
        r['status']='completed';r['resources_after']=guard()
    except Exception as e:
        r['status']='failed';r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['cuda_initialized']=torch.cuda.is_initialized();r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({k:r.get(k) for k in ('status','complete','errors','total_updates_completed','both_training_fit_gates_passed','cuda_initialized')}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
