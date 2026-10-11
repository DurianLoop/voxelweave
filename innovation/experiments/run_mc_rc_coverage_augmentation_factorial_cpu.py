"""Fixed4000/update three new arms plus exact authenticated historical baseline."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,sys,time,math,traceback,copy
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT,SEED,GlobalLocalUNet,weight_hash,read,sha,array_sha,load_authenticated_observed,
    sparse_image,physical_shape,resize_image,resize_training_label,context_tiles,segmentation_loss,infer_native,np,torch)
from mc_rc_observed_only_training_input import read_supervised_label
from mc_rc_full_affine_task_metrics_cpu import metrics
from mc_rc_coverage_augmentation_draw_cpu_support import ARMS,example_from_record,example_sha
OUT=ROOT/'experiments/mc_rc_coverage_augmentation_factorial_cpu'
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def checks(m):return dict(full_dice=m['full']['dice']>=.9,missing_dice=m['missing']['dice']>=.9,
    full_recall=m['full']['recall']>=.9,full_absRVE=m['full']['absolute_relative_volume_error']<=.1)
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate()
    dp=ROOT/'experiments/mc_rc_coverage_augmentation_draw_cpu/attempt_01.json'
    qp=dp.parent/'independent_all4000_geometry_and_inputs_attempt_01.json';d,q=read(dp),read(qp)
    assert d['complete'] and q['complete'] and not d['errors'] and not q['errors'] and q['result_sha256']==sha(dp)
    assert q['legacy_baseline_exact_reuse_verified'] and q['all_arm_real_input_sha_checks']==q['full_patch_geometry_checks']==16000
    oldp=ROOT/d['source_bindings'][0]['path'];old=read(oldp);baseline=old['arms'][0];assert baseline['name']=='bce_batch_dice'
    OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json';protocol=ROOT/'MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_PROTOCOL_2026-10-03.md'
    case=d['case_binding'];assert case['patient']=='VS-MC-RC-012'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],resources=resources,
        protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),script_sha256=sha(__file__),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (dp,qp,oldp)],
        code_bindings=[dict(path='experiments/'+s,sha256=sha(ROOT/'experiments'/s)) for s in (
            'mc_rc_global_local_task_cpu_support.py','mc_rc_coverage_augmentation_draw_cpu_support.py',
            'mc_rc_observed_only_training_input.py','mc_rc_full_affine_task_metrics_cpu.py','mc_rc_task_metrics_cpu.py')],
        case_binding=case,seed=SEED,training_patient_ids=['VS-MC-RC-012'],training_series_uids=[case['uid']],
        model_parameters=981602,updates_per_arm=4000,new_training_updates_planned=12000,new_training_updates_completed=0,
        pretrained_weights_loaded=False,device='cpu',torch_version=str(torch.__version__),arms=[],
        native_hidden_MR_pixels_decoded=False,validation_patients_opened=False,confirmation_patients_opened=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False)
    inherited=copy.deepcopy(baseline);inherited['name']='legacy_aug'
    inherited.update(reused_existing_arm=True,inherited_old_training_updates=4000,new_training_updates=0,
        new_global_forward_calls=0,new_local_forward_calls=0,origin_source_file=oldp.relative_to(ROOT).as_posix(),origin_source_sha256=sha(oldp))
    r['arms'].append(inherited);write(path,r)
    try:
        row=next(e for e in read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json')['series'] if e['uid']==case['uid'])
        obs=load_authenticated_observed(case,row);native,stats=sparse_image(obs,'raw_pchip',row);label=read_supervised_label(case)
        assert array_sha(label)==d['input_binding']['native_label_sha256'];shape,spacing=physical_shape(case)
        image=resize_image(native,shape);target=resize_training_label(label,shape)
        assert array_sha(image)==d['input_binding']['physical_input_sha256'] and array_sha(target)==d['input_binding']['physical_label_sha256']
        item=dict(image_zrc=image,label_zrc=target,zspacing=spacing)
        r['input_binding']=dict(**d['input_binding'],observed_statistics=stats);write(path,r)
        for arm in ARMS[1:]:
            resource_gate();torch.manual_seed(SEED);model=GlobalLocalUNet();model.train()
            opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
            a=dict(name=arm,complete=False,reused_existing_arm=False,updates_completed=0,new_training_updates=0,
                initial_weights_sha256=weight_hash(model),draw_sha256=[],training_history=[],
                training_started_utc=datetime.now(timezone.utc).isoformat())
            assert a['initial_weights_sha256']==baseline['initial_weights_sha256'] and sum(v.numel() for v in model.parameters())==981602
            r['arms'].append(a);write(path,r);began=time.perf_counter();losses=[]
            for step,record in enumerate(d['rows']):
                if step%100==0:resource_gate()
                example=example_from_record(item,record,arm);digest=example_sha(example)
                assert digest==record['example_sha256_by_arm'][arm];a['draw_sha256'].append(digest)
                gv,x,y,gt,loc,fullshape,sample=example;lr=.0001+.0009*(1+math.cos(math.pi*step/3999))/2
                for group in opt.param_groups:group['lr']=lr
                opt.zero_grad(set_to_none=True);features,coarse=model.global_forward(gv)
                p=model.local_forward(x,context_tiles(features,loc,fullshape));ll=segmentation_loss(p,y);gl=segmentation_loss(coarse,gt);loss=ll+.5*gl
                assert torch.isfinite(loss);loss.backward();assert all(v.grad is None or torch.isfinite(v.grad).all() for v in model.parameters());opt.step()
                losses.append((float(loss.detach()),float(ll.detach()),float(gl.detach())));a['updates_completed']=step+1;a['new_training_updates']=step+1;r['new_training_updates_completed']+=1
                if step==9:
                    a['first10_updates_seconds_per_update']=(time.perf_counter()-began)/10;write(path,r);assert a['first10_updates_seconds_per_update']<=2
                if (step+1)%100==0:
                    h=dict(update=step+1,last100_loss_mean=np.mean(losses[-100:],axis=0).tolist(),lr=lr,elapsed_seconds=time.perf_counter()-began,last_z=record['z'],resources=resource_gate())
                    a['training_history'].append(h);write(path,r);print(json.dumps(dict(arm=arm,**h)),flush=True)
            a['final_weights_sha256']=weight_hash(model);a['training_finished_utc']=datetime.now(timezone.utc).isoformat()
            cp=OUT/(arm+'_final_update_4000.pt')
            torch.save(dict(state_dict=model.state_dict(),arm=arm,updates_completed=4000,seed=SEED,
                training_patient_ids=r['training_patient_ids'],training_series_uids=r['training_series_uids'],
                initial_weights_sha256=a['initial_weights_sha256'],final_weights_sha256=a['final_weights_sha256'],
                protocol_sha256=r['protocol_sha256'],draw_file_sha256=sha(dp)),cp)
            a.update(checkpoint_file=cp.relative_to(ROOT).as_posix(),checkpoint_sha256=sha(cp));write(path,r)
            def progress(done,total):resource_gate();print(json.dumps(dict(arm=arm,inference_planes_done=done,planes_total=total)),flush=True)
            pred,coverage=infer_native(model,image,spacing,case['native_shape'],progress)
            pp=OUT/(arm+'_native_prediction.npz');np.savez_compressed(pp,prediction_rcz=pred);m=metrics(pred,label,obs);gate=checks(m)
            a['evaluation']=dict(patient=case['patient'],uid=case['uid'],prediction_file=pp.relative_to(ROOT).as_posix(),prediction_file_sha256=sha(pp),
                prediction_array_sha256=array_sha(pred),metrics=m,coverage=coverage,fit_gate_checks=gate,fit_gate_passed=all(gate.values()))
            a.update(new_global_forward_calls=model.global_calls,new_local_forward_calls=model.local_calls,complete=True)
            write(path,r);print(json.dumps(dict(arm=arm,full_dice=m['full']['dice'],missing_dice=m['missing']['dice'],fit_gate_passed=all(gate.values()))),flush=True)
            del model,opt,pred
        r['global_forward_calls']=sum(a['new_global_forward_calls'] for a in r['arms']);r['local_forward_calls']=sum(a['new_local_forward_calls'] for a in r['arms'])
        r['gpu_initialized']=torch.cuda.is_initialized();assert not r['gpu_initialized']
        assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<100000000
        r['complete']=all(a['complete'] for a in r['arms']) and r['new_training_updates_completed']==12000 and len(r['arms'])==4
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','new_training_updates_completed','global_forward_calls','local_forward_calls','gpu_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
