"""All19 training-matched full-FOV developer inputs; frozen weights, no optimization."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,sys,time,traceback,copy,shutil
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT,DEVELOPERS,read,sha,array_sha,np,torch,load_authenticated_observed,sparse_image,
    physical_shape,resize_image,infer_native)
from mc_rc_global_local_evaluation_binding_cpu import frozen_bindings
from mc_rc_observed_only_training_input import read_supervised_label
from mc_rc_full_affine_task_metrics_cpu import metrics
FAILED=ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu'
OUT=ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02'
def write(path,r):path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def summarize(rows):
    fields=('dice','precision','recall','signed_relative_volume_error','absolute_relative_volume_error')
    patients={}
    for patient in sorted(DEVELOPERS):
        group=[r for r in rows if r['patient']==patient];assert group
        patients[patient]=dict(series=len(group),metrics={})
        for domain in ('full','missing','anchors','tail'):
            patients[patient]['metrics'][domain]={}
            for field in fields:
                values=[r['metrics'][domain][field] for r in group]
                patients[patient]['metrics'][domain][field]=sum(values)/len(values) if all(v is not None for v in values) else None
    means={}
    for domain in ('full','missing','anchors','tail'):
        means[domain]={}
        for field in fields:
            values=[p['metrics'][domain][field] for p in patients.values()]
            means[domain][field]=sum(values)/11 if all(v is not None for v in values) else None
            means[domain][field+'_defined_patients']=sum(v is not None for v in values)
    return dict(patients=patients,patient_first_means=means,
                complete_miss_series=[r['uid'] for r in rows if r['metrics']['full']['tp']==0])
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate()
    model,records,bindings=frozen_bindings();train=records['training']
    prodfile=ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json'
    prooffile=prodfile.parent/'independent_all19_observed_inputs_and_label_axes_attempt_01.json'
    validationfile=ROOT/'experiments/mc_rc_global_local_task_validation_cpu/attempt_01.json'
    valproof=validationfile.parent/'independent_metrics_and_checkpoint_attempt_01.json'
    production,proof,val,q=[read(p) for p in (prodfile,prooffile,validationfile,valproof)]
    assert all(r['complete'] and not r['errors'] for r in (production,proof,val,q))
    assert proof['result_sha256']==sha(prodfile) and q['result_sha256']==sha(validationfile)
    assert proof['sparse_inputs_verified']==76 and proof['labels_verified']==19
    cases=records['development']['cases'];assert len(cases)==19 and {c['patient'] for c in cases}==DEVELOPERS
    by={r['uid']:r for r in production['series']};OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    protocol=ROOT/'MC_RC_FROZEN_GLOBAL_LOCAL_DEVELOPMENT_DIAGNOSIS_CPU_PROTOCOL_2026-10-03.md'
    code=[ROOT/'experiments'/name for name in ('diagnose_mc_rc_frozen_global_local_development_attempt02_cpu.py','mc_rc_full_affine_task_metrics_cpu.py',
        'mc_rc_global_local_task_cpu_support.py','mc_rc_global_local_evaluation_binding_cpu.py',
        'mc_rc_observed_only_training_input.py','mc_rc_task_metrics_cpu.py')]
    bindings += [dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (prodfile,prooffile,validationfile,valproof)]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],resources=resources,
        source_bindings=bindings,code_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in code],
        protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),evaluations=[],
        checkpoint_file=train['checkpoint_file'],checkpoint_sha256=train['checkpoint_sha256'],
        final_weights_sha256=train['final_weights_sha256'],training_updates=0,developer_patients=11,
        planned_series=19,method='raw_pchip',threshold=.5,confirmation_patients_opened=False,
        native_hidden_MR_pixels_decoded=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    failedpath=FAILED/'attempt_01.json';failed=read(failedpath)
    assert not failed['complete'] and failed['errors']==['AssertionError: ']
    assert 'surface_metrics' in failed['traceback'] and len(failed['evaluations'])==3
    for item in failed['code_bindings']:assert sha(ROOT/item['path'])==item['sha256']
    r['source_bindings'].append(dict(path=failedpath.relative_to(ROOT).as_posix(),sha256=sha(failedpath)))
    r['retained_failed_attempt']='experiments/mc_rc_frozen_global_local_development_diagnosis_cpu/attempt_01.json'
    r['reused_complete_predictions']=0
    r['runtime_preflight']=failed['runtime_preflight']
    r['affine_metrics_resume_protocol_sha256']=sha(ROOT/'MC_RC_FROZEN_DEVELOPMENT_AFFINE_RESUME_PROTOCOL_2026-10-03.md')
    write(path,r)
    try:
        totalplanes=sum(c['native_shape'][2] for c in cases)
        for index,case in enumerate(cases):
            if index<3:
                old=failed['evaluations'][index];assert old['uid']==case['uid'] and old['patient']==case['patient']
                oldfile=ROOT/old['prediction_file'];assert sha(oldfile)==old['prediction_file_sha256']
                with np.load(oldfile,allow_pickle=False) as data:pred=data['prediction_rcz'].copy()
                assert array_sha(pred)==old['prediction_array_sha256']
                obs=load_authenticated_observed(case,by[case['uid']]);label=read_supervised_label(case)
                assert array_sha(label)==old['label_array_sha256']
                row=copy.deepcopy(old);newfile=OUT/oldfile.name;shutil.copyfile(oldfile,newfile)
                row['prediction_file']=newfile.relative_to(ROOT).as_posix();row['metrics']=metrics(pred,label,obs)
                row['reused_from_failed_attempt_complete_row']=True
                row['new_global_forward_calls']=0;row['new_local_forward_calls']=0
                r['evaluations'].append(row);r['reused_complete_predictions']+=1;write(path,r)
                print(json.dumps(dict(patient=case['patient'],uid=case['uid'],completed_prediction_reused=True)),flush=True)
                del pred,label,obs
                continue
            resource_gate();obs=load_authenticated_observed(case,by[case['uid']])
            native,st=sparse_image(obs,'raw_pchip',by[case['uid']]);shape,spacing=physical_shape(case)
            physical=resize_image(native,shape);before=(model.global_calls,model.local_calls);start=time.perf_counter()
            print(json.dumps(dict(patient=case['patient'],uid=case['uid'],inference_started=True)),flush=True)
            def progress(done,total):
                resource_gate();print(json.dumps(dict(patient=case['patient'],planes_done=done,planes_total=total)),flush=True)
            pred,cov=infer_native(model,physical,spacing,case['native_shape'],progress)
            elapsed=time.perf_counter()-start
            label=read_supervised_label(case);assert array_sha(label)==by[case['uid']]['label_array_sha256']
            prediction=OUT/(case['patient']+'_'+case['uid']+'.npz');np.savez_compressed(prediction,prediction_rcz=pred)
            row=dict(patient=case['patient'],uid=case['uid'],method='raw_pchip',input_sha256=array_sha(native),
                physical_input_sha256=array_sha(physical),zspacing_mm=spacing,observed_statistics=st,
                prediction_file=prediction.relative_to(ROOT).as_posix(),prediction_file_sha256=sha(prediction),
                prediction_array_sha256=array_sha(pred),label_array_sha256=array_sha(label),coverage=cov,
                metrics=metrics(pred,label,obs),inference_elapsed_seconds=elapsed,
                global_forward_calls=model.global_calls-before[0],local_forward_calls=model.local_calls-before[1])
            r['evaluations'].append(row);write(path,r)
            if index==0:
                r['runtime_preflight']=dict(first_uid=case['uid'],actual_first_full_input_seconds=elapsed,
                    seconds_per_plane=elapsed/case['native_shape'][2],total_planned_planes=totalplanes,
                    projected_full_inference_seconds=elapsed/case['native_shape'][2]*totalplanes,
                    maximum_projection_seconds=3600)
                write(path,r);assert r['runtime_preflight']['projected_full_inference_seconds']<=3600
            print(json.dumps(dict(patient=case['patient'],uid=case['uid'],full_dice=row['metrics']['full']['dice'],
                                 missing_dice=row['metrics']['missing']['dice'])),flush=True)
            del pred,label,physical,native,obs
        r['aggregate']=summarize(r['evaluations']);r['global_forward_calls']=model.global_calls;r['local_forward_calls']=model.local_calls
        r['gpu_initialized']=torch.cuda.is_initialized();assert not r['gpu_initialized']
        assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<100000000
        r['complete']=len(r['evaluations'])==19
    except Exception as error:r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','global_forward_calls','local_forward_calls','gpu_initialized')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
