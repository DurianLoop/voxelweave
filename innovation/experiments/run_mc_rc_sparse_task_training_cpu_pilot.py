"""One predeclared 4000-update sparse-input task model; development diagnosis only."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import time,json,sys,traceback,math
from pathlib import Path
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_sparse_task_cpu_pilot_support import ROOT,SEED,PilotUNet,weight_hash,read,sha,array_sha,load_package,image_input,training_batch,loss_fn,infer,metrics,read_supervised_label,np,torch
OUT=ROOT/'experiments/mc_rc_sparse_task_training_cpu_pilot'
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    prepfile=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json';inputfile=ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json';proof=ROOT/'experiments/mc_rc_development_training_input_cpu/independent_all19_observed_inputs_and_label_axes_attempt_01.json'
    prep=read(prepfile);production=read(inputfile);independent=read(proof);assert all(x['complete'] and not x['errors'] for x in (prep,production,independent))
    by={x['uid']:x for x in production['series']};cases=prep['cases'];train=[x for x in cases if x['patient']!='VS-MC-RC-013'];assert len(train)==18 and len({x['patient'] for x in train})==10
    protocol=ROOT/'MC_RC_SPARSE_TASK_TRAINING_CPU_PILOT_PLAN_2026-10-03.md';support=ROOT/'experiments/mc_rc_sparse_task_cpu_pilot_support.py'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),resources=resources,complete=False,errors=[],protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),script_sha256=sha(__file__),support_sha256=sha(support),torch_version=str(torch.__version__),seed=SEED,device='cpu',gpu_initialized=False,threads=1,updates_planned=4000,updates_completed=0,pretrained_weights_loaded=False,training_patient_ids=sorted({x['patient'] for x in train}),training_series_uids=[x['uid'] for x in train],development_holdout_patient='VS-MC-RC-013',training_diagnostic_patient='VS-MC-RC-012',training_sampling_counts={},training_history=[],inputs=[],evaluations=[],source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (prepfile,inputfile,proof)],native_hidden_MR_pixels_decoded=False,validation_or_confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,r)
    try:
        torch.manual_seed(SEED);probe=PilotUNet();opt=torch.optim.AdamW(probe.parameters(),lr=.001);x=torch.randn(4,5,96,96);y=(torch.rand(4,1,96,96)>.9).float();t=time.perf_counter()
        for i in range(10):opt.zero_grad(set_to_none=True);loss=loss_fn(probe(x),y);assert torch.isfinite(loss);loss.backward();opt.step()
        sec=(time.perf_counter()-t)/10;r['synthetic_preflight']=dict(updates=10,seconds_per_update=sec,passed=sec<=2 and not torch.cuda.is_initialized(),real_MR_inputs=False);write(path,r);assert r['synthetic_preflight']['passed'];del probe,opt,x,y
        print(json.dumps(dict(synthetic_preflight=r['synthetic_preflight']),ensure_ascii=False),flush=True)
        cache={}
        for case in train:
            resource_gate();row=by[case['uid']];o=load_package(case,row);image,st=image_input(o,'raw_pchip',row);label=read_supervised_label(case);assert array_sha(label)==row['label_array_sha256'];foreground=np.argwhere(label);assert len(foreground)>0
            cache[case['uid']]=dict(image=image,label=label,foreground=foreground)
            r['inputs'].append(dict(patient=case['patient'],uid=case['uid'],image_sha256=array_sha(image),label_sha256=array_sha(label),observed_package_sha256=row['observed_package_sha256'],statistics=st));write(path,r)
        resource_gate();torch.manual_seed(SEED);rng=np.random.default_rng(SEED);model=PilotUNet();model.train();optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
        r['model_parameters']=sum(p.numel() for p in model.parameters());r['initial_weights_sha256']=weight_hash(model);r['cache_image_bytes']=sum(x['image'].nbytes for x in cache.values());r['training_started_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
        patients=r['training_patient_ids'];patient_cases={p:[c for c in train if c['patient']==p] for p in patients};losses=[];t=time.perf_counter()
        for step in range(4000):
            if step%100==0:resource_gate()
            patient=patients[int(rng.integers(len(patients)))];cs=patient_cases[patient];case=cs[int(rng.integers(len(cs)))];xb,yb=training_batch(cache[case['uid']],rng)
            lr=.0001+.0009*(1+math.cos(math.pi*step/3999))/2
            for g in optimizer.param_groups:g['lr']=lr
            optimizer.zero_grad(set_to_none=True);loss=loss_fn(model(xb),yb);assert torch.isfinite(loss);loss.backward();assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters());optimizer.step();losses.append(float(loss.detach()))
            r['training_sampling_counts'][patient]=r['training_sampling_counts'].get(patient,0)+1;r['updates_completed']=step+1
            if (step+1)%100==0:
                h=dict(update=step+1,last100_loss_mean=float(np.mean(losses[-100:])),last_loss=losses[-1],lr=lr,training_elapsed_seconds=time.perf_counter()-t);r['training_history'].append(h);write(path,r);print(json.dumps(h),flush=True)
        r['training_finished_utc']=datetime.now(timezone.utc).isoformat();r['final_weights_sha256']=weight_hash(model);checkpoint=OUT/'final_update_4000.pt';torch.save(dict(state_dict=model.state_dict(),updates_completed=4000,initial_weights_sha256=r['initial_weights_sha256'],final_weights_sha256=r['final_weights_sha256'],protocol_sha256=r['protocol_sha256'],training_patient_ids=patients,training_series_uids=r['training_series_uids'],seed=SEED),checkpoint)
        r['checkpoint_file']=checkpoint.relative_to(ROOT).as_posix();r['checkpoint_sha256']=sha(checkpoint);assert all(p.device.type=='cpu' for p in model.parameters());write(path,r)
        del cache
        for patient in ('VS-MC-RC-012','VS-MC-RC-013'):
            chosen=[c for c in cases if c['patient']==patient];assert len(chosen)==1;case=chosen[0];row=by[case['uid']];o=load_package(case,row);label=read_supervised_label(case);assert array_sha(label)==row['label_array_sha256']
            for method in ('raw_pchip','raw_linear'):
                resource_gate();image,st=image_input(o,method,row)
                def progress(z,n):resource_gate();print(json.dumps(dict(patient=patient,method=method,planes_done=z,planes_total=n)),flush=True)
                pred,coverage=infer(model,image,progress);dest=OUT/(patient+'_'+method+'_prediction.npz');np.savez_compressed(dest,prediction_rcz=pred)
                result=dict(patient=patient,uid=case['uid'],method=method,statistics=st,input_sha256=array_sha(image),prediction_file=dest.relative_to(ROOT).as_posix(),prediction_file_sha256=sha(dest),prediction_array_sha256=array_sha(pred),label_array_sha256=array_sha(label),coverage=coverage,metrics=metrics(pred,label,o),development_role='training_diagnostic' if patient=='VS-MC-RC-012' else 'held_out_development_diagnostic')
                r['evaluations'].append(result);write(path,r);print(json.dumps(dict(patient=patient,method=method,full=result['metrics']['full'],missing=result['metrics']['missing'])),flush=True);del image,pred
        r['capability_cases']=[]
        for e in r['evaluations']:
            if e['method']=='raw_pchip':
                f=e['metrics']['full'];m=e['metrics']['missing'];passed=f['dice'] is not None and f['dice']>=.70 and m['dice'] is not None and m['dice']>=.65 and f['recall'] is not None and f['recall']>=.70 and f['absolute_relative_volume_error']<=.50;r['capability_cases'].append(dict(patient=e['patient'],passed=bool(passed)))
        r['capability_gate_passed']=all(x['passed'] for x in r['capability_cases']);r['neural_forward_calls']=model.forward_calls+10;r['gpu_initialized']=torch.cuda.is_initialized();assert not r['gpu_initialized'];assert sum(x.stat().st_size for x in OUT.iterdir() if x.is_file())<50000000;r['complete']=r['updates_completed']==4000 and len(r['evaluations'])==4
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r);print(json.dumps({k:r.get(k) for k in ('complete','errors','updates_completed','capability_gate_passed','neural_forward_calls','gpu_initialized','scientific_confirmation_patients')}),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
