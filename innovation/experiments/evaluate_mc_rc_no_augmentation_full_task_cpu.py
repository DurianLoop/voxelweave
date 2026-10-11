"""Frozen new20k checkpoint,19 development plus18 validator conditions, full affine metrics."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import json, sys, time, traceback
from datetime import datetime, timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT, DEVELOPERS, VALIDATORS, read, sha, array_sha, load_authenticated_observed,
    sparse_image, physical_shape, resize_image, infer_native, np, torch)
from mc_rc_task_roles_input_cpu import read_task_supervised_label
from mc_rc_full_affine_task_metrics_cpu import metrics
from mc_rc_no_augmentation_evaluation_binding_cpu import frozen_bindings,aggregate_group,validation_gates
OUT=ROOT/'experiments/mc_rc_no_augmentation_full_task_evaluation_cpu'


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate()
    model,records,bindings=frozen_bindings();training=records['training']
    OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    protocol=ROOT/'MC_RC_NO_AUGMENTATION_FULL_EVALUATION_CPU_PROTOCOL_2026-10-03.md'
    split=OUT/'frozen_capability_split.json'
    write(split,dict(created_utc=datetime.now(timezone.utc).isoformat(),
        kind='Development/validation capability check; scientific confirmation still closed.',
        training_patient_ids=training['training_patient_ids'],training_series_uids=training['training_series_uids'],
        validation_patient_ids=sorted(VALIDATORS),validation_series_uids=[c['uid'] for c in records['validation']['cases']],
        validation_neural_forwards_at_freeze=0,confirmation_patients_opened=False,
        final_scientific_split_activated=False,checkpoint_sha256=training['checkpoint_sha256'],source_bindings=bindings))
    code=('evaluate_mc_rc_no_augmentation_full_task_cpu.py','mc_rc_no_augmentation_evaluation_binding_cpu.py',
          'mc_rc_global_local_task_cpu_support.py','mc_rc_full_affine_task_metrics_cpu.py',
          'mc_rc_task_metrics_cpu.py','mc_rc_task_roles_input_cpu.py')
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],resources=resources,
        source_bindings=bindings,code_bindings=[dict(path='experiments/'+s,sha256=sha(ROOT/'experiments'/s)) for s in code],
        protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),
        split_file=split.relative_to(ROOT).as_posix(),split_sha256=sha(split),threshold=.5,device='cpu',
        checkpoint_file=training['checkpoint_file'],checkpoint_sha256=training['checkpoint_sha256'],
        final_weights_sha256=training['final_weights_sha256'],training_updates_completed=20000,
        new_training_updates=0,evaluations=[],planned_development_series=19,planned_validation_conditions=18,
        native_hidden_MR_pixels_decoded=False,confirmation_patients_opened=False,
        validation_is_independent_scientific_confirmation=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,r)
    try:
        jobs=[]
        for group,methods in (('development',('raw_pchip',)),('validation',('raw_pchip','raw_linear'))):
            for case in records[group]['cases']:
                for method in methods:jobs.append((group,case,method))
        assert len(jobs)==37
        totalplanes=sum(case['native_shape'][2] for _,case,_ in jobs)
        for index,(group,case,method) in enumerate(jobs):
            resource_gate();by={s['uid']:s for s in records[group+'_inputs']['series']}
            obs=load_authenticated_observed(case,by[case['uid']]);native,stats=sparse_image(obs,method,by[case['uid']])
            shape,spacing=physical_shape(case);image=resize_image(native,shape)
            before=(model.global_calls,model.local_calls);began=time.perf_counter()
            print(json.dumps(dict(group=group,patient=case['patient'],uid=case['uid'],method=method,inference_started=True)),flush=True)
            def progress(done,total):
                resource_gate();print(json.dumps(dict(group=group,patient=case['patient'],method=method,planes_done=done,planes_total=total)),flush=True)
            prediction,coverage=infer_native(model,image,spacing,case['native_shape'],progress)
            elapsed=time.perf_counter()-began
            label=read_task_supervised_label(case);assert array_sha(label)==by[case['uid']]['label_array_sha256']
            if group=='development':
                original=next(b for b in training['inputs'] if b['uid']==case['uid'])
                assert array_sha(native)==original['native_input_sha256'] and array_sha(image)==original['physical_image_sha256']
            pp=OUT/(group+'_'+case['patient']+'_'+case['uid']+'_'+method+'.npz')
            np.savez_compressed(pp,prediction_rcz=prediction)
            row=dict(group=group,patient=case['patient'],uid=case['uid'],method=method,
                input_sha256=array_sha(native),physical_input_sha256=array_sha(image),observed_statistics=stats,zspacing_mm=spacing,
                prediction_file=pp.relative_to(ROOT).as_posix(),prediction_file_sha256=sha(pp),prediction_array_sha256=array_sha(prediction),
                label_array_sha256=array_sha(label),coverage=coverage,metrics=metrics(prediction,label,obs),
                inference_elapsed_seconds=elapsed,global_forward_calls=model.global_calls-before[0],local_forward_calls=model.local_calls-before[1])
            r['evaluations'].append(row);write(path,r)
            if index==0:
                projection=elapsed/case['native_shape'][2]*totalplanes
                r['runtime_preflight']=dict(first_uid=case['uid'],first_full_input_seconds=elapsed,total_planned_planes=totalplanes,
                    projected_full_inference_seconds=projection,maximum_projection_seconds=3600)
                write(path,r);assert projection<=3600
            print(json.dumps(dict(group=group,patient=case['patient'],uid=case['uid'],method=method,
                full_dice=row['metrics']['full']['dice'],missing_dice=row['metrics']['missing']['dice'])),flush=True)
            del prediction,label,image,native,obs
        devrows=[e for e in r['evaluations'] if e['group']=='development'];valrows=[e for e in r['evaluations'] if e['group']=='validation']
        r['development_aggregate']=aggregate_group(devrows,DEVELOPERS,('raw_pchip',))
        r['validation_aggregate']=aggregate_group(valrows,VALIDATORS,('raw_pchip','raw_linear'))
        r['capability_gate_checks']=validation_gates(r['validation_aggregate']);r['capability_gate_passed']=all(r['capability_gate_checks'].values())
        r.update(global_forward_calls=model.global_calls,local_forward_calls=model.local_calls,gpu_initialized=torch.cuda.is_initialized())
        assert not r['gpu_initialized'] and len(devrows)==19 and len(valrows)==18
        assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())<100000000
        r['complete']=len(r['evaluations'])==37
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','capability_gate_passed','global_forward_calls','local_forward_calls','gpu_initialized')}),flush=True)
    return int(not r['complete'])


if __name__=='__main__':
    raise SystemExit(main())
