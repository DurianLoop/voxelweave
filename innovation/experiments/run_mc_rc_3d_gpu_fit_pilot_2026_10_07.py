"""Two-arm fixed-example actual GPU fit diagnostic, totals-only startup guard and new attempts."""
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,lattice,physical_mr,physical_label,
    read_reference_label,TaskUNet3D,loss,sample_batch,infer_full_fov,torch,np,SEED,PATCH)

def state_hash(state):
    h=hashlib.sha256()
    for k,v in state.items(): h.update(k.encode());h.update(array_sha(v.detach().cpu().numpy()).encode())
    return h.hexdigest()

def count(p,g):
    # Exact count values are independently encoded, including all background.
    total=np.bincount((p.astype(np.uint8)+2*g.astype(np.uint8)).ravel(),minlength=4)
    tn,fp,fn,tp=map(int,total);s=tp+fp;n=tp+fn
    return dict(tn=tn,tp=tp,fp=fp,fn=fn,gt_foreground=n,pred_foreground=s,
                dice=2*tp/(s+n) if s+n else None,recall=tp/n if n else None,
                precision=tp/s if s else None,absRVE=abs(s-n)/n if n else None,
                empty_prediction=s==0,empty_ground_truth=n==0)

def totals_observation():
    result=subprocess.run(['nvidia-smi','--query-gpu=index,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=15)
    rows=[v.strip() for v in result.stdout.splitlines() if v.strip()];assert len(rows)==1
    index,name,total,free,util=[v.strip() for v in rows[0].split(',')]
    assert index=='0'
    return dict(observed_utc=datetime.now(timezone.utc).isoformat(),index=0,name=name,total_bytes=int(total)*1048576,
                free_bytes=int(free)*1048576,utilization_percent=int(util),pids_requested=False,pids_modified=False)

def gpu_guard():
    r=resource_guard();free,total=torch.cuda.mem_get_info(0);peak=torch.cuda.max_memory_reserved(0)
    assert free>=4_000_000_000 and peak<=2_500_000_000
    r.update(gpu_free_bytes=free,gpu_total_bytes=total,gpu_peak_reserved_bytes=peak)
    return r

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True)
    args=parser.parse_args();assert args.attempt.isdigit() and len(args.attempt)==2
    sys.stdout.reconfigure(encoding='utf-8')
    out=ROOT/'experiments'/('mc_rc_3d_gpu_fit_pilot_2026_10_07_attempt'+args.attempt);out.mkdir(exist_ok=False)
    path=out/'attempt_01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,status='preparing',errors=[],arms=[],
           total_updates_completed=0,scientific_confirmation_patients=0,publication_claim_confirmed=False,
           confirmation_patients_opened=False,user_gpu_authorization='可以用gpu',script_sha256=sha(__file__),
           final_method_not_frozen=True,seed=SEED,planned_updates_per_arm=512,planned_total_updates=1024,
           arm_order=['native_reference','raw_pchip'],source_bindings=[])
    sourcepaths=['MC_RC_3D_GPU_FIT_PILOT_PROTOCOL_2026-10-07.md','experiments/mc_rc_3d_baseline_2026_10_07.py',
                 'experiments/mc_rc_3d_baseline_v2_2026_10_07.py','experiments/mc_rc_reference_resources_2026_10_07.py',
                 'experiments/mc_rc_true_native_reference_2026_10_07.py','experiments/mc_rc_true_native_reference_v2_2026_10_07.py',
                 'experiments/mc_rc_observed_only_training_input.py',
                 'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json',
                 'experiments/mc_rc_true_native_reference_attempt02_2026_10_07/independent_all28_pixels_and_labels_2026_10_07.json',
                 'experiments/mc_rc_current_development_input_preparation/attempt_01.json',
                 'experiments/mc_rc_development_training_input_cpu/attempt_01.json']
    def save(): path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        for key in (7,8):
            proof=read(ROOT/sourcepaths[key]);assert proof['complete'] and not proof['errors']
        r['source_bindings']=[dict(path=p,sha256=sha(ROOT/p)) for p in sourcepaths]
        for binding in read(ROOT/sourcepaths[7])['source_bindings']: assert sha(ROOT/binding['path'])==binding['sha256']
        r['resources_before']=resource_guard();r['gpu_observation']=totals_observation()
        if r['gpu_observation']['free_bytes']<8_000_000_000:
            assert not torch.cuda.is_initialized()
            r.update(status='resource_deferred',reason='GPU free bytes below frozen 8GB startup floor',cuda_initialized=False,
                     finished_utc=datetime.now(timezone.utc).isoformat(),resources_after=resource_guard())
            save();print(json.dumps({k:r.get(k) for k in ('status','reason','total_updates_completed','cuda_initialized')}),flush=True)
            return 3
        os.environ['CUDA_VISIBLE_DEVICES']='0'
        assert torch.cuda.is_available()
        torch.cuda.set_per_process_memory_fraction(.1,0)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True
        r['gpu_runtime']=dict(torch_version=str(torch.__version__),gpu_name=torch.cuda.get_device_name(0),
                              allocator_fraction=.1,peak_limit_bytes=2_500_000_000,autocast=False,tf32=False,
                              cudnn_deterministic=True,all_kernels_bitwise_reproducible_not_asserted=True)
        gpu_guard();r['status']='running'
        role,case,row=fixed_cases()[0]
        assert role=='development' and case['patient']=='VS-MC-RC-001'
        assert case['uid']=='1.3.6.1.4.1.14519.5.2.1.10875952303942319530925289292568369177'
        grid=lattice(case);label=read_reference_label(case);target=physical_label(label,grid)
        certified={x['uid']:x for x in read(ROOT/sourcepaths[7])['series']}[case['uid']]
        assert array_sha(target)==certified['physical_label_sha256']
        reference_initial=None;reference_primitives=None;reference_targets=None
        r['training_patient_ids']=[case['patient']];r['training_series_uids']=[case['uid']];save()
        for kind in r['arm_order']:
            gpu_guard();normalized,st=source_image(case,row,kind);image=physical_mr(normalized,grid)
            assert array_sha(image)==certified['inputs'][kind]['physical_image_sha256']
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED))
            xsha,ysha=array_sha(x.numpy()),array_sha(y.numpy())
            torch.manual_seed(SEED);model=TaskUNet3D();initial=state_hash(model.state_dict())
            if reference_initial is None:reference_initial=initial;reference_primitives=primitive;reference_targets=ysha
            else:assert initial==reference_initial and primitive==reference_primitives and ysha==reference_targets
            model.to('cuda:0');model.train();x=x.to('cuda:0');y=y.to('cuda:0')
            opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
            arm=dict(kind=kind,complete=False,updates_completed=0,initial_weights_sha256=initial,
                     input_batch_sha256=xsha,label_batch_sha256=ysha,primitive=primitive,
                     physical_input_sha256=array_sha(image),observed_statistics=st,history=[])
            r['arms'].append(arm);save();started=time.perf_counter()
            for step in range(512):
                if step%16==0:gpu_guard()
                lr=.0001+.0009*(1+math.cos(math.pi*step/511))/2
                for group in opt.param_groups:group['lr']=lr
                opt.zero_grad(set_to_none=True);outputs=model(x);value=loss(outputs,y)
                assert torch.isfinite(value);value.backward()
                gradientmax={name:max(float(p.grad.abs().max()) for p in branch.parameters() if p.grad is not None)
                             for name,branch in (('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads))}
                assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
                if step==0:
                    assert all(v>0 for v in gradientmax.values());arm['first_real_update_gradients']=gradientmax
                opt.step();arm['updates_completed']=step+1;r['total_updates_completed']+=1
                if (step+1)%16==0:
                    h=dict(update=step+1,loss=float(value.detach()),lr=lr,elapsed_seconds=time.perf_counter()-started,resources=gpu_guard())
                    arm['history'].append(h);save();print(json.dumps(dict(arm=kind,update=step+1,loss=h['loss'])),flush=True)
                if step==31:
                    seconds=(time.perf_counter()-started)/32;arm['first32_seconds_per_update']=seconds
                    r['training_time_projection_seconds']=seconds*1024;save()
                    assert seconds*1024<=3600, 'Frozen 1024-update training time projection exceeded'
            state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
            checkpoint=out/(kind+'_last_512.pt');torch.save(dict(state_dict=state,kind=kind,updates=512,seed=SEED,
                initial_weights_sha256=initial,final_weights_sha256=state_hash(state),protocol_sha256=sha(ROOT/sourcepaths[0]),
                physical_input_sha256=arm['physical_input_sha256'],label_batch_sha256=ysha,primitive=primitive),checkpoint)
            model.eval()
            with torch.inference_mode():patch_predictions=model(x)[0].sigmoid().cpu().numpy()[:,0]>=.5
            truth=y.cpu().numpy()[:,0]>=.5;arm['patch_metrics']=[count(p,g) for p,g in zip(patch_predictions,truth)]
            probabilities,coverage=infer_full_fov(model,image,grid,case['native_shape'],device='cuda:0')
            prediction=probabilities>=.5;metrics=dict(full=count(prediction,label))
            z=np.arange(label.shape[2]);last=int(z[z%4==0][-1])
            for name,domain in (('anchors',z%4==0),('missing',(z<last)&(z%4!=0)),('tail',z>last)):
                metrics[name]=count(prediction[:,:,domain],label[:,:,domain])
            predpath=out/(kind+'_full_fov_prediction.npz')
            np.savez_compressed(predpath,prediction_rcz=prediction,probability_rcz=probabilities)
            full=metrics['full'];gate=dict(foreground_patch_dice=arm['patch_metrics'][0]['dice']>=.9,
                training_full_dice=full['dice'] is not None and full['dice']>=.9,
                training_full_recall=full['recall'] is not None and full['recall']>=.9,
                training_full_absRVE=full['absRVE'] is not None and full['absRVE']<=.25,training_tp_positive=full['tp']>0)
            arm.update(complete=True,checkpoint_file=checkpoint.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(checkpoint),
                       final_weights_sha256=state_hash(state),prediction_file=predpath.relative_to(ROOT).as_posix(),prediction_sha256=sha(predpath),
                       metrics=metrics,inference=coverage,training_fit_gate=gate,training_fit_gate_passed=all(gate.values()),
                       elapsed_seconds=time.perf_counter()-started,resources_after=gpu_guard())
            save();del model,opt,x,y,image,normalized,state,outputs,value,patch_predictions,probabilities,prediction
            torch.cuda.empty_cache()
        r['complete']=r['total_updates_completed']==1024 and all(a['complete'] for a in r['arms'])
        r['both_training_fit_gates_passed']=all(a['training_fit_gate_passed'] for a in r['arms'])
        r['saved_bytes']=sum(p.stat().st_size for p in out.iterdir() if p.is_file());assert r['saved_bytes']<=250_000_000
        r['status']='completed';r['resources_after']=gpu_guard()
    except Exception as e:
        r.update(status='failed');r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['cuda_initialized']=torch.cuda.is_initialized();r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({k:r.get(k) for k in ('status','complete','errors','total_updates_completed','both_training_fit_gates_passed','cuda_initialized')}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
