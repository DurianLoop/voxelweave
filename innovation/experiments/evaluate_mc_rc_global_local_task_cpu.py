"""All nine validation series; two frozen observed-only inputs, full native-grid outputs."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[name]='1'
import json
import sys
import traceback
from datetime import datetime, timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT, read, sha, array_sha, np, torch, load_authenticated_observed,
    sparse_image, physical_shape, resize_image, infer_native)
from mc_rc_task_roles_input_cpu import read_task_supervised_label
from mc_rc_task_metrics_cpu import metrics
from mc_rc_global_local_evaluation_binding_cpu import frozen_bindings, aggregate


def write(path, record):
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resources=resource_gate()
    model, records, bindings=frozen_bindings()
    out=ROOT/'experiments/mc_rc_global_local_task_validation_cpu'
    out.mkdir(exist_ok=False)
    path=out/'attempt_01.json'
    training=records['training']
    split=out/'frozen_diagnostic_split.json'
    write(split,dict(created_utc=datetime.now(timezone.utc).isoformat(),
        kind='task capability diagnostic split; final scientific confirmation still closed',
        training_patient_ids=training['training_patient_ids'],
        training_series_uids=training['training_series_uids'],
        validation_patient_ids=sorted({x['patient'] for x in records['preparation']['cases']}),
        validation_series_uids=[x['uid'] for x in records['preparation']['cases']],
        checkpoint_sha256=training['checkpoint_sha256'], final_weights_sha256=training['final_weights_sha256'],
        validation_neural_forwards_at_freeze=0, confirmation_patients_opened=False,
        final_scientific_split_activated=False, source_bindings=bindings))
    evaluation_protocol=ROOT/'MC_RC_GLOBAL_LOCAL_EVALUATION_CPU_PLAN_2026-10-03.md'
    sources=[ROOT/'experiments'/f for f in (
        'evaluate_mc_rc_global_local_task_cpu.py','mc_rc_global_local_evaluation_binding_cpu.py',
        'mc_rc_task_metrics_cpu.py','mc_rc_task_metrics_cpu_sources.json',
        'mc_rc_task_roles_input_cpu.py','mc_rc_global_local_geometry_reference_cpu.py')]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],resources=resources,
        device='cpu',threshold=.5,evaluations=[],source_bindings=bindings,
        code_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources],
        evaluation_protocol=evaluation_protocol.relative_to(ROOT).as_posix(),
        evaluation_protocol_sha256=sha(evaluation_protocol),diagnostic_split_file=split.relative_to(ROOT).as_posix(),
        diagnostic_split_sha256=sha(split),training_updates_completed=20000,
        checkpoint_file=training['checkpoint_file'],checkpoint_sha256=training['checkpoint_sha256'],
        final_weights_sha256=training['final_weights_sha256'],validation_conditions_planned=18,
        validation_effects_are_independent_scientific_confirmation=False,
        confirmation_patients_opened=False,native_hidden_MR_pixels_decoded=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,r)
    try:
        by={x['uid']:x for x in records['production']['series']}
        for case in records['preparation']['cases']:
            for method in ('raw_pchip','raw_linear'):
                resource_gate()
                obs=load_authenticated_observed(case,by[case['uid']])
                native,statistics=sparse_image(obs,method,by[case['uid']])
                shape,spacing=physical_shape(case)
                physical=resize_image(native,shape)
                before=(model.global_calls,model.local_calls)
                print(json.dumps(dict(patient=case['patient'],uid=case['uid'],method=method,
                                      inference_started=True,physical_shape=list(physical.shape))),flush=True)
                def progress(done,total):
                    resource_gate()
                    print(json.dumps(dict(patient=case['patient'],method=method,planes_done=done,
                                          planes_total=total)),flush=True)
                prediction,coverage=infer_native(model,physical,spacing,case['native_shape'],progress)
                # Evaluation GT is first loaded here, after the full prediction exists.
                label=read_task_supervised_label(case)
                assert array_sha(label)==by[case['uid']]['label_array_sha256']
                predfile=out/(case['patient']+'_'+case['uid']+'_'+method+'.npz')
                np.savez_compressed(predfile,prediction_rcz=prediction)
                row=dict(patient=case['patient'],uid=case['uid'],method=method,
                    input_sha256=array_sha(native),physical_input_sha256=array_sha(physical),
                    observed_statistics=statistics,zspacing_mm=spacing,
                    prediction_file=predfile.relative_to(ROOT).as_posix(),prediction_file_sha256=sha(predfile),
                    prediction_array_sha256=array_sha(prediction),label_array_sha256=array_sha(label),
                    coverage=coverage,metrics=metrics(prediction,label,obs),
                    global_forward_calls=model.global_calls-before[0],local_forward_calls=model.local_calls-before[1])
                r['evaluations'].append(row)
                write(path,r)
                print(json.dumps(dict(patient=case['patient'],uid=case['uid'],method=method,
                    full_dice=row['metrics']['full']['dice'],missing_dice=row['metrics']['missing']['dice'])),flush=True)
                del prediction,label,physical,native,obs
        r['aggregate'],r['capability_gate_checks'],r['capability_gate_passed']=aggregate(r['evaluations'])
        r['global_forward_calls']=model.global_calls
        r['local_forward_calls']=model.local_calls
        r['gpu_initialized']=torch.cuda.is_initialized()
        assert not r['gpu_initialized']
        r['new_training_and_validation_file_bytes']=sum(p.stat().st_size
            for folder in (out,ROOT/'experiments/mc_rc_global_local_task_training_cpu')
            for p in folder.iterdir() if p.is_file())
        assert r['new_training_and_validation_file_bytes']<100000000
        r['complete']=len(r['evaluations'])==18
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error))
        r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat()
    write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','capability_gate_passed',
                    'global_forward_calls','local_forward_calls','gpu_initialized')},ensure_ascii=False),flush=True)
    return int(not r['complete'])


if __name__=='__main__':
    raise SystemExit(main())
