"""Qualify saved MRI score pairing on old seen validation; no arrays or head fit."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import copy,ctypes,hashlib,json,shutil,sys,time
from datetime import datetime,timezone
from pathlib import Path
import paired_outcome_adapter as adapter

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SOURCE=ROOT/'experiments/mc_rc_intensity_only_full_task_evaluation_gpu/attempt_01.json'
SOURCE_PROOF=SOURCE.parent/'independent_all37_metrics_and111_planes_attempt_01.json'
SPLIT=SOURCE.parent/'frozen_capability_split.json'
CASES=ROOT/'experiments/mc_rc_validation_task_case_preparation/attempt_01.json'
INPUTS=ROOT/'experiments/mc_rc_validation_task_input_cpu/attempt_01.json'
DEV_FEATURES=ROOT/'experiments/observed_holdout_feature_table_2026_10_08.json'
OUT=HERE/'qualification_attempt01'

def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,data):
    with p.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);tick=time.perf_counter()
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.GetCurrentProcess.restype=ctypes.c_void_p
    kernel.SetPriorityClass.argtypes=(ctypes.c_void_p,ctypes.c_uint32)
    assert kernel.SetPriorityClass(kernel.GetCurrentProcess(),0x00004000)
    allow={p.resolve() for p in (SOURCE,SOURCE_PROOF,SPLIT,CASES,INPUTS,DEV_FEATURES,Path(__file__),HERE/'paired_outcome_adapter.py',HERE/'PROTOCOL.md')}
    readpaths=set();denied=[]
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        p=Path(args[0]).resolve();mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT.parent) and not p.is_relative_to(HERE):
            if p not in allow:
                denied.append(str(p));raise PermissionError('Unlisted workspace read; no medical/GT/prediction/checkpoint arrays')
            readpaths.add(p.relative_to(ROOT.parent).as_posix())
    sys.addaudithook(audit)
    source,proof,split,cases,inputs=map(read,(SOURCE,SOURCE_PROOF,SPLIT,CASES,INPUTS))
    assert all(d['complete'] and not d['errors'] for d in (source,proof,cases,inputs))
    assert proof['result_sha256']==entry(SOURCE)['sha256'] and proof['checkpoint_replayed_planes']==111
    assert source['split_sha256']==entry(SPLIT)['sha256'] and source['checkpoint_sha256']==split['checkpoint_sha256']
    assert source['capability_gate_passed'] is False and not all(source['capability_gate_checks'].values())
    assert not split['confirmation_patients_opened'] and not split['final_scientific_split_activated']
    observed={r['uid']:r for r in inputs['series']};independent={(r['group'],r['patient'],r['uid'],r['method']):r for r in proof['evaluations']}
    cohort={p:[] for p in sorted(split['validation_patient_ids'])};metadata={}
    for c in cases['cases']:
        p,uid=c['patient'],c['uid'];i=observed[uid];assert p in cohort and p==i['patient'];cohort[p].append(uid)
        metadata[uid]=dict(patient=p,native_shape=c['native_shape'],observed_package_sha256=i['observed_package_sha256'],
            observed_array_sha256=i['observed_array_sha256'],label_array_sha256=i['label_array_sha256'],
            observed_statistics=i['observed_stats'],
            input_sha256_by_action={m:i['inputs'][m+'_observed_shared']['normalized_rcz_sha256'] for m in ('raw_pchip','raw_linear')})
    assert len(metadata)==9 and len(cohort)==4 and set(observed)==set(metadata)
    contract=dict(schema_version=1,patient_series=cohort,series_metadata=metadata,baseline_action='raw_pchip',candidate_action='raw_linear',
        current_state='whole_patient_raw_pchip_input',candidate_state='whole_patient_raw_linear_input',
        task_checkpoint_sha256=source['checkpoint_sha256'],task_training_patient_ids=split['training_patient_ids'],
        cohort_role='already_seen_validation_archival_qualification',task_capability_gate_passed=False,
        task_checkpoint_array_read=False,final_current19series_task_model=False,
        official_evaluation_file=entry(SOURCE),official_independent_proof=entry(SOURCE_PROOF))
    rows=[]
    for e in source['evaluations']:
        if e['group']!='validation':continue
        k=(e['group'],e['patient'],e['uid'],e['method']);q=independent[k]
        assert q['all_replayed_voxels_equal'] is True
        for domain in adapter.DOMAINS:
            for key,value in q['independent_counts'][domain].items():assert e['metrics'][domain][key]==value
        i=metadata[e['uid']]
        row=dict(patient=e['patient'],uid=e['uid'],action=e['method'],status='completed',
            task_checkpoint_sha256=source['checkpoint_sha256'],observed_package_sha256=i['observed_package_sha256'],
            observed_array_sha256=i['observed_array_sha256'],label_array_sha256=e['label_array_sha256'],
            input_sha256=e['input_sha256'],observed_statistics=e['observed_statistics'],
            full_fov=True,label_used_for_inference=False,native_planes=e['coverage']['planes'],coverage_min=e['coverage']['coverage_min'],
            independently_verified_counts=True,counts={d:e['metrics'][d] for d in adapter.DOMAINS},
            prediction_file_sha256=e['prediction_file_sha256'],saved_infer_native_interval_seconds=e['inference_elapsed_seconds'],
            full_action_cost=None)
        rows.append(row)
    assert len(rows)==18
    labels=adapter.paired_labels(rows,contract)
    write(OUT/'source_normalized_outcomes.json',dict(contract=contract,outcomes=rows,source_scores_already_seen=True,qualification_only=True))
    write(OUT/'paired_task_labels.json',labels)
    checks=[]
    def reject(name,fn):
        try:fn()
        except ValueError as e:checks.append(dict(name=name,rejected=True,reason=str(e)))
        else:raise AssertionError('Not rejected: '+name)
    def change(name,fn):
        edited=copy.deepcopy(rows);fn(edited);reject(name,lambda:adapter.paired_labels(edited,contract))
    change('missing_series_action',lambda r:r.pop())
    change('duplicate_series_action',lambda r:r.append(copy.deepcopy(r[0])))
    change('wrong_observed_source',lambda r:r[0].update(observed_package_sha256='0'*64))
    change('wrong_label_source',lambda r:r[0].update(label_array_sha256='0'*64))
    change('wrong_checkpoint',lambda r:r[0].update(task_checkpoint_sha256='0'*64))
    change('wrong_action_input',lambda r:r[0].update(input_sha256='0'*64))
    change('partial_native_planes',lambda r:r[0]['native_planes'].pop())
    change('GT_in_inference',lambda r:r[0].update(label_used_for_inference=True))
    change('changed_shared_statistics',lambda r:r[0]['observed_statistics'].update(mean=0))
    change('saved_scalar_count_mismatch',lambda r:r[0]['counts']['full'].update(dice=0))
    change('invented_full_action_cost',lambda r:r[0].update(full_action_cost=0))
    reject('already_seen_weak_model_labels_cannot_fit_head',lambda:adapter.require_fit_ready(labels))
    shuffled=copy.deepcopy(rows);shuffled.reverse();again=adapter.paired_labels(shuffled,contract)
    assert again==labels
    # Preserve a missing/failed action in a metadata-injection check, not in the actual MRI result table.
    failed=copy.deepcopy(rows);failed[0].update(status='failed',counts=None,saved_infer_native_interval_seconds=None)
    failedlabels=adapter.paired_labels(failed,contract)
    assert len(failedlabels['series'])==9 and len(failedlabels['patients'])==4
    patient=failed[0]['patient'];assert next(v for v in failedlabels['patients'] if v['patient']==patient)['delta_Q'] is None
    assert failedlabels['patient_first_means']['delta_Q'] is None
    write(OUT/'failure_retention_metadata_injection.json',dict(qualification_injection_only=True,actual_MRI_failure_observed=False,
        changed_patient=patient,changed_uid=failed[0]['uid'],changed_action=failed[0]['action'],result=failedlabels))
    features=read(DEV_FEATURES)
    devkeys={(r['patient'],r['series_uid']) for r in features['rows']};valkeys={(r['patient'],r['uid']) for r in labels['series']}
    assert not devkeys&valkeys
    def feature_join():
        if not valkeys<=devkeys:raise ValueError('Current17-feature development table does not cover archived validation label pairs')
    reject('incorrect_join_to_development17_feature_table',feature_join)
    summary={}
    for field in ('series','patients'):
        values=[adapter.unpack(r['delta_Q']) for r in labels[field]]
        summary[field]=dict(total=len(values),positive=sum(v is not None and v>0 for v in values),
            negative=sum(v is not None and v<0 for v in values),zero=sum(v==0 for v in values),undefined=sum(v is None for v in values))
    elapsed=time.perf_counter()-tick;free=shutil.disk_usage(ROOT).free
    assert free>=8_000_000_000 and elapsed<=120 and not denied
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(p) for p in (Path(__file__),HERE/'paired_outcome_adapter.py',HERE/'PROTOCOL.md',SOURCE,SOURCE_PROOF,SPLIT,CASES,INPUTS,DEV_FEATURES)],
        output_bindings=[entry(OUT/p) for p in ('source_normalized_outcomes.json','paired_task_labels.json','failure_retention_metadata_injection.json')],
        real_archived_series_pairs=9,real_archived_patient_pairs=4,real_archived_action_outcomes=18,
        outcome_sign_counts=summary,original_task_capability_gate_passed=False,head_fitting_readiness=False,
        complete_full_action_costs_available=False,real_new_final19series_action_labels=0,
        row_order_invariance_verified=True,metadata_negative_checks=checks,
        one_failure_injection_retains_all_series_patients_and_undefined=True,
        original_input_result_contains_development19_and_seen_validation18_metadata=True,
        only_validation18_rows_exported=True,archived_metrics_only_not_new_MRI_evaluation=True,
        medical_arrays_loaded=0,prediction_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,GPU_forwards=0,training_updates=0,head_fits=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        audit_workspace_read_paths=sorted(readpaths),prohibited_reads=denied,
        workspace_free_bytes=free,own_process_below_normal=True,elapsed_seconds=elapsed,
        new_primary_papers_read=0,publication_claim_confirmed=False,goal_status='active')
    write(OUT/'receipt.json',result)
    assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=True,real_pairs=9,patients=4,sign_counts=summary,negative_checks=len(checks),
        patient_first_means=labels['patient_first_means'],ready=False,elapsed_seconds=elapsed),ensure_ascii=False),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
