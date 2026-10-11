"""Independent precision-recall/Fraction reconstruction of archived paired labels."""
import ctypes,hashlib,json,sys,time
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'independent_attempt01'
SOURCE=ROOT/'experiments/mc_rc_intensity_only_full_task_evaluation_gpu/attempt_01.json'
OLD_PROOF=SOURCE.parent/'independent_all37_metrics_and111_planes_attempt_01.json'
CASES=ROOT/'experiments/mc_rc_validation_task_case_preparation/attempt_01.json'
INPUTS=ROOT/'experiments/mc_rc_validation_task_input_cpu/attempt_01.json'
QUAL=HERE/'qualification_attempt01'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def frac(v):return None if v is None else F(v['numerator'],v['denominator'])
def harmonic_dice(counts):
    gt=counts['gt_foreground'];pred=counts['pred_foreground'];tp=counts['tp']
    assert gt==tp+counts['fn'] and pred==tp+counts['fp']
    if not gt+pred:return None
    if not tp:return F(0)
    precision,recall=F(tp,pred),F(tp,gt)
    return 2*precision*recall/(precision+recall)

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);tick=time.perf_counter()
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=ctypes.c_void_p
    k.SetPriorityClass.argtypes=(ctypes.c_void_p,ctypes.c_uint32);assert k.SetPriorityClass(k.GetCurrentProcess(),0x00004000)
    allowed={p.resolve() for p in (SOURCE,OLD_PROOF,CASES,INPUTS,QUAL/'receipt.json',QUAL/'paired_task_labels.json',
                                 QUAL/'source_normalized_outcomes.json',QUAL/'failure_retention_metadata_injection.json',
                                 HERE/'PROTOCOL.md',HERE/'qualify_saved_real_pairs.py',HERE/'paired_outcome_adapter.py',
                                 ROOT/'experiments/observed_holdout_feature_table_2026_10_08.json',SOURCE.parent/'frozen_capability_split.json')}
    reads=set();denied=[]
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        p=Path(args[0]).resolve();mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT.parent) and not p.is_relative_to(HERE):
            if p not in allowed:
                denied.append(str(p));raise PermissionError('Independent scalar audit prohibits unlisted arrays')
            reads.add(p.relative_to(ROOT.parent).as_posix())
    sys.addaudithook(audit)
    source,oldproof,cases,inputs=map(read,(SOURCE,OLD_PROOF,CASES,INPUTS))
    q=read(QUAL/'receipt.json');labels=read(QUAL/'paired_task_labels.json');norm=read(QUAL/'source_normalized_outcomes.json')
    assert all(v['complete'] and not v['errors'] for v in (source,oldproof,cases,inputs,q))
    assert oldproof['result_sha256']==entry(SOURCE)['sha256'] and source['capability_gate_passed'] is False
    expected={p:[] for p in sorted({c['patient'] for c in cases['cases']})}
    for c in cases['cases']:expected[c['patient']].append(c['uid'])
    assert len(expected)==4 and sum(map(len,expected.values()))==9
    old={(e['patient'],e['uid'],e['method']):e for e in source['evaluations'] if e['group']=='validation'}
    ind={(e['patient'],e['uid'],e['method']):e for e in oldproof['evaluations'] if e['group']=='validation'}
    oi={e['uid']:e for e in inputs['series']}
    produced={(r['patient'],r['uid']):r for r in labels['series']};assert len(produced)==9
    seenkeys=set();expected_delta={};checked=[]
    for p,uids in expected.items():
        pairs=[]
        for uid in uids:
            a,b=old[p,uid,'raw_pchip'],old[p,uid,'raw_linear'];r=produced[p,uid]
            assert a['label_array_sha256']==b['label_array_sha256']==oi[uid]['label_array_sha256']
            assert a['observed_statistics']==b['observed_statistics']==oi[uid]['observed_stats']
            for e in (a,b):
                for domain in ('full','anchors','missing','tail'):
                    for name,value in ind[p,uid,e['method']]['independent_counts'][domain].items():
                        assert e['metrics'][domain][name]==value
                assert e['input_sha256']==oi[uid]['inputs'][e['method']+'_observed_shared']['normalized_rcz_sha256']
            aa,bb=harmonic_dice(a['metrics']['full']),harmonic_dice(b['metrics']['full']);assert aa is not None and bb is not None
            assert frac(r['Q_before'])==aa and frac(r['Q_after'])==bb and frac(r['delta_Q'])==bb-aa
            assert frac(r['quality_cost_before'])==1-aa and frac(r['quality_cost_after'])==1-bb
            assert frac(r['quality_cost_before'])-frac(r['quality_cost_after'])==frac(r['delta_Q'])
            assert r['full_action_cost'] is None and r['before_prediction_sha256']==a['prediction_file_sha256'] and r['after_prediction_sha256']==b['prediction_file_sha256']
            assert r['source_bindings']==dict(observed_package_sha256=oi[uid]['observed_package_sha256'],
                observed_array_sha256=oi[uid]['observed_array_sha256'],label_array_sha256=oi[uid]['label_array_sha256'],
                task_checkpoint_sha256=source['checkpoint_sha256'])
            assert r['before_input_sha256']==a['input_sha256'] and r['after_input_sha256']==b['input_sha256']
            seenkeys.add((p,uid));pairs.append((aa,bb));expected_delta[p,uid]=bb-aa
        patient=next(v for v in labels['patients'] if v['patient']==p)
        assert patient['series_uids']==uids and patient['series_count']==len(uids)
        aa=sum(v[0] for v in pairs)/len(pairs);bb=sum(v[1] for v in pairs)/len(pairs)
        assert frac(patient['Q_before'])==aa and frac(patient['Q_after'])==bb and frac(patient['delta_Q'])==bb-aa
        assert patient['task_model_training_exposed'] is False and patient['head_fitting_allowed'] is False
        assert patient['cohort_role']=='already_seen_validation_archival_qualification' and patient['full_action_cost'] is None
        assert patient['saved_inference_interval_sum_before']==sum(old[p,u,'raw_pchip']['inference_elapsed_seconds'] for u in uids)
        assert patient['saved_inference_interval_sum_after']==sum(old[p,u,'raw_linear']['inference_elapsed_seconds'] for u in uids)
        checked.append(dict(patient=p,series_count=len(uids),delta_Q=float(bb-aa),exact_fraction=str(bb-aa)))
    assert seenkeys==set(produced)
    for name in ('Q_before','Q_after','delta_Q'):
        assert frac(labels['patient_first_means'][name])==sum(frac(p[name]) for p in labels['patients'])/4
    assert sum(v>0 for v in expected_delta.values())==2 and sum(v<0 for v in expected_delta.values())==4 and sum(v==0 for v in expected_delta.values())==3
    assert len(q['metadata_negative_checks'])==13 and all(v['rejected'] for v in q['metadata_negative_checks'])
    injected=read(QUAL/'failure_retention_metadata_injection.json')
    assert injected['qualification_injection_only'] and not injected['actual_MRI_failure_observed']
    il=injected['result'];assert len(il['series'])==9 and len(il['patients'])==4 and il['patient_first_means']['delta_Q'] is None
    assert next(r for r in il['patients'] if r['patient']==injected['changed_patient'])['delta_Q'] is None
    assert labels['original_task_capability_gate_passed'] is False and labels['training_readiness'] is False
    for b in q['source_bindings']+q['output_bindings']:assert entry(ROOT/b['path'])==b
    # Wrong sample weighting is a descriptive diagnostic, never a new prespecified endpoint.
    series_mean=sum(expected_delta.values())/9;patient_mean=frac(labels['patient_first_means']['delta_Q'])
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(p) for p in (Path(__file__),SOURCE,OLD_PROOF,CASES,INPUTS,QUAL/'receipt.json',QUAL/'paired_task_labels.json',QUAL/'source_normalized_outcomes.json')],
        independently_replayed_real_pairs=9,patient_count=4,full_domain_saved_count_records_matched=72,
        independent_metric_formula='Harmonic mean of exact precision and recall, with explicit zero/undefined handling',
        patients=checked,patient_first_delta_Q=float(patient_mean),incorrect_series_equal_delta_Q=float(series_mean),
        exact_weighting_difference=str(patient_mean-series_mean),
        all_source_input_label_prediction_bindings_matched=True,all_exact_quality_cost_gain_relations_verified=True,
        negative_branch_records_checked=True,negative_branches_reexecuted=False,failure_retention_record_verified=True,
        production_adapter_imported=False,medical_arrays_loaded=0,prediction_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,GPU_forwards=0,training_updates=0,head_fits=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        audit_workspace_read_paths=sorted(reads),prohibited_reads=denied,elapsed_seconds=time.perf_counter()-tick,
        author_or_MRI_experiment_rerun=False,archived_metrics_only=True,new_primary_papers_read=0,
        publication_claim_confirmed=False,goal_status='active')
    assert result['elapsed_seconds']<=120 and not denied
    with (OUT/'receipt.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ('complete','independently_replayed_real_pairs','patient_count','patient_first_delta_Q',
        'incorrect_series_equal_delta_Q','elapsed_seconds')},ensure_ascii=False),flush=True)
    print(json.dumps(checked,ensure_ascii=False),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
