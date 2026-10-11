"""Matched-draw, fixed-budget one-developer loss recipe comparison; no validation."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,sys,time,math,hashlib,traceback
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT,SEED,GlobalLocalUNet,weight_hash,read,sha,array_sha,load_authenticated_observed,
    sparse_image,physical_shape,resize_image,resize_training_label,training_example,
    context_tiles,segmentation_loss,infer_native,np,torch)
from mc_rc_observed_only_training_input import read_supervised_label
from mc_rc_full_affine_task_metrics_cpu import metrics
from unified_focal_binary_cpu_port import asymmetric_unified
OUT=ROOT/'experiments/mc_rc_global_local_single_case_loss_cpu'
UPDATES=4000
ARMS=('bce_batch_dice','asymmetric_unified_focal')

def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def sample_sha(example):
    gv,x,y,gt,locations,shape,record=example
    digest=hashlib.sha256()
    for tensor in (gv,x,y,gt):digest.update(array_sha(tensor.numpy()).encode())
    digest.update(json.dumps(dict(locations=locations,shape=shape,record=record),sort_keys=True).encode())
    return digest.hexdigest()

def fit_checks(value):
    return dict(full_dice=value['full']['dice']>=.9,missing_dice=value['missing']['dice']>=.9,
        full_recall=value['full']['recall']>=.9,full_absRVE=value['full']['absolute_relative_volume_error']<=.1)

def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();OUT.mkdir(exist_ok=False)
    path=OUT/'attempt_01.json';protocol=ROOT/'MC_RC_GLOBAL_LOCAL_SINGLE_CASE_LOSS_CPU_PROTOCOL_2026-10-03.md'
    sources=[ROOT/'experiments'/name for name in (
        'mc_rc_current_development_input_preparation/attempt_01.json',
        'mc_rc_development_training_input_cpu/attempt_01.json',
        'mc_rc_development_training_input_cpu/independent_all19_observed_inputs_and_label_axes_attempt_01.json',
        'mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02/attempt_01.json',
        'mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02/independent_metrics_and_checkpoint_attempt_01.json',
        'unified_focal_binary_cpu_port/attempt_01.json',
        'unified_focal_binary_cpu_port/output_bias_and_input_guards_attempt_01.json')]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],resources=resources,
        protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),
        script_sha256=sha(__file__),source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources],
        code_bindings=[dict(path='experiments/'+name,sha256=sha(ROOT/'experiments'/name)) for name in (
            'mc_rc_global_local_task_cpu_support.py','mc_rc_observed_only_training_input.py',
            'unified_focal_binary_cpu_port.py','mc_rc_full_affine_task_metrics_cpu.py','mc_rc_task_metrics_cpu.py')],
        training_patient_ids=['VS-MC-RC-012'],training_series_uids=[],seed=SEED,updates_per_arm=UPDATES,
        device='cpu',torch_version=str(torch.__version__),pretrained_weights_loaded=False,
        native_hidden_MR_pixels_decoded=False,validation_patients_opened=False,confirmation_patients_opened=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False,arms=[],synthetic_preflights=[])
    write(path,r)
    try:
        records=[read(p) for p in sources];assert all(v['complete'] and not v['errors'] for v in records)
        assert records[4]['result_sha256']==sha(sources[3]) and records[4]['checkpoint_replayed_planes']==57
        cases=[c for c in records[0]['cases'] if c['patient']=='VS-MC-RC-012'];assert len(cases)==1
        case=cases[0];row=next(e for e in records[1]['series'] if e['uid']==case['uid'])
        r['uid']=case['uid'];r['training_series_uids']=[case['uid']];r['case_binding']=case
        for arm in ARMS:
            loss_fn=segmentation_loss if arm==ARMS[0] else asymmetric_unified
            torch.manual_seed(SEED);probe=GlobalLocalUNet();opt=torch.optim.AdamW(probe.parameters(),lr=.001,weight_decay=.0001)
            gv=torch.randn(1,5,256,256);x=torch.randn(2,5,128,128);y=(torch.rand(2,1,128,128)>.9).float();gt=(torch.rand(1,1,256,256)>.9).float()
            began=time.perf_counter()
            for j in range(10):
                opt.zero_grad(set_to_none=True);f,c=probe.global_forward(gv);p=probe.local_forward(x,context_tiles(f,[(0,0),(128,128)],(384,384)))
                loss=loss_fn(p,y)+.5*loss_fn(c,gt);assert torch.isfinite(loss);loss.backward()
                assert all(v.grad is None or torch.isfinite(v.grad).all() for v in probe.parameters());opt.step()
            elapsed=(time.perf_counter()-began)/10
            r['synthetic_preflights'].append(dict(arm=arm,updates=10,seconds_per_update=elapsed,passed=elapsed<=2 and not torch.cuda.is_initialized(),real_MR_inputs=False))
            write(path,r);assert r['synthetic_preflights'][-1]['passed'];print(json.dumps(r['synthetic_preflights'][-1]),flush=True)
            del probe,opt,gv,x,y,gt
        obs=load_authenticated_observed(case,row);native,stats=sparse_image(obs,'raw_pchip',row)
        label=read_supervised_label(case);assert array_sha(label)==row['label_array_sha256']
        shape,zspacing=physical_shape(case);image=resize_image(native,shape);target=resize_training_label(label,shape)
        item=dict(image_zrc=image,label_zrc=target,native_foreground=np.argwhere(label),zspacing=zspacing)
        r['input_binding']=dict(observed_package=row['observed_package'],observed_package_sha256=row['observed_package_sha256'],
            native_input_sha256=array_sha(native),physical_input_sha256=array_sha(image),
            native_label_sha256=array_sha(label),physical_label_sha256=array_sha(target),
            physical_shape=list(image.shape),observed_statistics=stats,zspacing_mm=zspacing)
        write(path,r);baseline_draws=None;initial=None
        for arm in ARMS:
            resource_gate();torch.manual_seed(SEED);rng=np.random.default_rng(SEED)
            model=GlobalLocalUNet();model.train();opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
            a=dict(name=arm,complete=False,updates_completed=0,initial_weights_sha256=weight_hash(model),
                model_parameters=sum(v.numel() for v in model.parameters()),training_history=[],draw_sha256=[],
                training_started_utc=datetime.now(timezone.utc).isoformat())
            r['arms'].append(a);assert a['model_parameters']==981602
            if initial is None:initial=a['initial_weights_sha256']
            else:assert initial==a['initial_weights_sha256']
            loss_fn=segmentation_loss if arm==ARMS[0] else asymmetric_unified
            began=time.perf_counter();losses=[];stream=hashlib.sha256()
            for step in range(UPDATES):
                if step%100==0:resource_gate()
                rng.integers(1);rng.integers(1)  # same one-patient/one-series sampling calls
                example=training_example(item,rng);draw=sample_sha(example)
                if baseline_draws is not None:assert draw==baseline_draws[step]
                a['draw_sha256'].append(draw);stream.update(draw.encode())
                gv,x,y,gt,loc,fullshape,record=example
                lr=.0001+.0009*(1+math.cos(math.pi*step/(UPDATES-1)))/2
                for group in opt.param_groups:group['lr']=lr
                opt.zero_grad(set_to_none=True);features,coarse=model.global_forward(gv)
                prediction=model.local_forward(x,context_tiles(features,loc,fullshape))
                ll=loss_fn(prediction,y);gl=loss_fn(coarse,gt);loss=ll+.5*gl
                assert torch.isfinite(loss);loss.backward()
                assert all(v.grad is None or torch.isfinite(v.grad).all() for v in model.parameters());opt.step()
                losses.append((float(loss.detach()),float(ll.detach()),float(gl.detach())));a['updates_completed']=step+1
                if (step+1)%100==0:
                    h=dict(update=step+1,last100_loss_mean=np.mean(losses[-100:],axis=0).tolist(),lr=lr,
                        training_elapsed_seconds=time.perf_counter()-began,last_sample=record,resources=resource_gate())
                    a['training_history'].append(h);write(path,r)
                    print(json.dumps(dict(arm=arm,**h)),flush=True)
            if baseline_draws is None:baseline_draws=a['draw_sha256'].copy()
            a['draw_stream_sha256']=stream.hexdigest();a['final_weights_sha256']=weight_hash(model)
            a['training_finished_utc']=datetime.now(timezone.utc).isoformat()
            cp=OUT/(arm+'_final_update_4000.pt')
            torch.save(dict(state_dict=model.state_dict(),arm=arm,updates_completed=UPDATES,seed=SEED,
                training_patient_ids=r['training_patient_ids'],training_series_uids=r['training_series_uids'],
                protocol_sha256=r['protocol_sha256'],initial_weights_sha256=a['initial_weights_sha256'],
                final_weights_sha256=a['final_weights_sha256'],draw_stream_sha256=a['draw_stream_sha256']),cp)
            a.update(checkpoint_file=cp.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(cp));write(path,r)
            def progress(done,total):
                resource_gate();print(json.dumps(dict(arm=arm,inference_planes_done=done,planes_total=total)),flush=True)
            pred,coverage=infer_native(model,image,zspacing,case['native_shape'],progress)
            pp=OUT/(arm+'_native_prediction.npz');np.savez_compressed(pp,prediction_rcz=pred)
            value=metrics(pred,label,obs);checks=fit_checks(value)
            a['evaluation']=dict(patient=case['patient'],uid=case['uid'],prediction_file=pp.relative_to(ROOT).as_posix(),
                prediction_file_sha256=sha(pp),prediction_array_sha256=array_sha(pred),metrics=value,coverage=coverage,
                fit_gate_checks=checks,fit_gate_passed=all(checks.values()))
            a['global_forward_calls']=model.global_calls;a['local_forward_calls']=model.local_calls
            a['complete']=True;write(path,r);print(json.dumps(dict(arm=arm,full_dice=value['full']['dice'],missing_dice=value['missing']['dice'],fit_gate_passed=all(checks.values()))),flush=True)
            del model,opt,pred
        r['matched_initialization_verified']=all(a['initial_weights_sha256']==initial for a in r['arms'])
        r['all_4000_training_draws_matched']=r['arms'][0]['draw_sha256']==r['arms'][1]['draw_sha256']
        r['global_forward_calls']=sum(a['global_forward_calls'] for a in r['arms'])+20
        r['local_forward_calls']=sum(a['local_forward_calls'] for a in r['arms'])+20
        r['gpu_initialized']=torch.cuda.is_initialized();assert not r['gpu_initialized']
        assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<100000000
        r['complete']=all(a['complete'] for a in r['arms']) and r['all_4000_training_draws_matched'] and r['matched_initialization_verified']
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','global_forward_calls','local_forward_calls','gpu_initialized')}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
