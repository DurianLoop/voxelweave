"""Predeclared single-case fit diagnostic; no generalization or new method claim."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import json,sys,math,time,traceback
from pathlib import Path
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_sparse_task_cpu_pilot_support import ROOT,SEED,PilotUNet,weight_hash,read,sha,array_sha,load_package,image_input,read_supervised_label,training_batch,loss_fn,infer,metrics,np,torch
OUT=ROOT/'experiments/mc_rc_single_developer_fit_diagnostic_cpu'
def write(p,r):Path(p).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json';protocol=ROOT/'MC_RC_SINGLE_DEVELOPER_FIT_DIAGNOSTIC_PLAN_2026-10-03.md'
    prep=read(ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json');chosen=[c for c in prep['cases'] if c['patient']=='VS-MC-RC-012'];assert len(chosen)==1;case=chosen[0]
    source=ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json';production=read(source);row=next(x for x in production['series'] if x['uid']==case['uid'])
    prior=ROOT/'experiments/mc_rc_sparse_task_training_cpu_pilot/attempt_01.json';previous=read(prior);assert previous['complete'] and not previous['errors'] and not previous['capability_gate_passed']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),resources=resources,complete=False,errors=[],protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),script_sha256=sha(__file__),support_sha256=sha(ROOT/'experiments/mc_rc_sparse_task_cpu_pilot_support.py'),preceding_result_file=prior.relative_to(ROOT).as_posix(),preceding_result_sha256=sha(prior),input_production_file=source.relative_to(ROOT).as_posix(),input_production_sha256=sha(source),patient=case['patient'],uid=case['uid'],training_patient_ids=[case['patient']],training_series_uids=[case['uid']],device='cpu',seed=SEED,pretrained_weights_loaded=False,updates_planned=4000,updates_completed=0,training_history=[],evaluations=[],native_hidden_MR_pixels_decoded=False,validation_or_confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,r)
    try:
        o=load_package(case,row);image,st=image_input(o,'raw_pchip',row);label=read_supervised_label(case);assert array_sha(label)==row['label_array_sha256'];item=dict(image=image,label=label,foreground=np.argwhere(label));r.update(input_sha256=array_sha(image),label_array_sha256=array_sha(label),statistics=st)
        torch.manual_seed(SEED);rng=np.random.default_rng(SEED);model=PilotUNet();model.train();opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001);r['initial_weights_sha256']=weight_hash(model);assert r['initial_weights_sha256']==previous['initial_weights_sha256'];r['model_parameters']=sum(p.numel() for p in model.parameters());write(path,r);losses=[];t=time.perf_counter()
        for step in range(4000):
            if step%100==0:resource_gate()
            xb,yb=training_batch(item,rng);lr=.0001+.0009*(1+math.cos(math.pi*step/3999))/2
            for group in opt.param_groups:group['lr']=lr
            opt.zero_grad(set_to_none=True);loss=loss_fn(model(xb),yb);assert torch.isfinite(loss);loss.backward();assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters());opt.step();losses.append(float(loss.detach()));r['updates_completed']=step+1
            if (step+1)%100==0:
                h=dict(update=step+1,last100_loss_mean=float(np.mean(losses[-100:])),lr=lr,training_elapsed_seconds=time.perf_counter()-t);r['training_history'].append(h);write(path,r);print(json.dumps(h),flush=True)
        r['final_weights_sha256']=weight_hash(model);checkpoint=OUT/'final_update_4000.pt';torch.save(dict(state_dict=model.state_dict(),updates_completed=4000,training_patient_ids=r['training_patient_ids'],training_series_uids=r['training_series_uids'],protocol_sha256=r['protocol_sha256'],initial_weights_sha256=r['initial_weights_sha256'],final_weights_sha256=r['final_weights_sha256'],seed=SEED),checkpoint);r.update(checkpoint_file=checkpoint.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(checkpoint));write(path,r)
        def progress(z,n):resource_gate();print(json.dumps(dict(patient=case['patient'],planes_done=z,planes_total=n)),flush=True)
        pred,coverage=infer(model,image,progress);dest=OUT/'VS-MC-RC-012_raw_pchip_prediction.npz';np.savez_compressed(dest,prediction_rcz=pred);m=metrics(pred,label,o)
        r['evaluations']=[dict(patient=case['patient'],uid=case['uid'],method='raw_pchip',input_sha256=array_sha(image),label_array_sha256=array_sha(label),prediction_file=dest.relative_to(ROOT).as_posix(),prediction_file_sha256=sha(dest),prediction_array_sha256=array_sha(pred),coverage=coverage,metrics=m,development_role='single_case_training_fit_only')]
        r['fit_gate_passed']=bool(m['full']['dice']>=.90 and m['missing']['dice']>=.90 and m['full']['recall']>=.90 and m['full']['absolute_relative_volume_error']<=.10);r['neural_forward_calls']=model.forward_calls;r['gpu_initialized']=torch.cuda.is_initialized();assert not r['gpu_initialized'];r['complete']=r['updates_completed']==4000 and len(r['evaluations'])==1
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r);print(json.dumps({k:r.get(k) for k in ('complete','errors','updates_completed','fit_gate_passed','neural_forward_calls','gpu_initialized')}),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
