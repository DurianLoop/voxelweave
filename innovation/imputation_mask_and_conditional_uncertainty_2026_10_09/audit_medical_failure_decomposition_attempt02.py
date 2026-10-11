"""Exact arithmetic on every completed FOV, retain all patient signs and failure regions."""
import sys,json,time
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;S=ROOT/'spatial_adaptation_matched_2026_10_08'
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
METRICS=['dice','precision','recall','signed_relative_volume_error','absolute_relative_volume_error']
def ratio(a,b):return F(a,b) if b else None
def mean(values):
    return sum(values,F(0))/len(values) if values and all(v is not None for v in values) else None
def printable(v):return None if v is None else dict(fraction=str(v),decimal=float(v))
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    exitfile=S/'ACTUAL_EVALUATION_EXIT.json';ex=read(exitfile);rpath=S/'evaluation_attempt01/receipt.json';r=read(rpath)
    term=read(S/'ACTUAL_EVALUATION_TERMINAL_TOOL.json')
    assert term['exit_code']==0 and 'session_id' not in term and term['observed_unified_exec_session']==78123
    assert ex['observed_tool_exit']==0 and ex['result_sha256']==sha(rpath) and ex['all36_strict_numeric_gates_passed']
    assert r['complete'] and not r['errors'] and len(r['arms'])==4 and all(len(a['series'])==9 for a in r['arms'])
    for b in r['source_bindings']:bind(b)
    out=HERE/'medical_failure_decomposition_attempt02';out.mkdir(exist_ok=False);arms={};audit_errors=[];checked=0;maxerror=0.
    for arm in r['arms']:
        patients={};series=[]
        for item in arm['series']:
            assert item['strict_gate_passed'];full=item['metrics']['full']
            for count in ['tp','fp','fn','tn','gt_foreground','pred_foreground','voxels']:
                assert full[count]==sum(item['metrics'][part][count] for part in ['anchors','missing','tail'])
            fractions={}
            for part,v in item['metrics'].items():
                tp,fp,fn,tn=[v[k] for k in ['tp','fp','fn','tn']];g,p=v['gt_foreground'],v['pred_foreground']
                assert all(isinstance(x,int) and x>=0 for x in [tp,fp,fn,tn,g,p]) and g==tp+fn and p==tp+fp and v['voxels']==tp+fp+fn+tn
                metrics=dict(dice=ratio(2*tp,2*tp+fp+fn),precision=ratio(tp,p),recall=ratio(tp,g),signed_relative_volume_error=ratio(p-g,g),absolute_relative_volume_error=ratio(abs(p-g),g))
                for key,value in metrics.items():
                    assert (value is None)==(v[key] is None),(arm['name'],item['uid'],part,key)
                    if value is not None:maxerror=max(maxerror,abs(float(value)-v[key]));assert maxerror<=3e-12
                    checked+=1
                fractions[part]=metrics
            patient=item['patient'];patients.setdefault(patient,[]).append(fractions)
            series.append(dict(patient=patient,uid=item['uid'],full_counts={k:full[k] for k in ['tp','fp','fn','tn','gt_foreground','pred_foreground']},
                full_Dice=printable(fractions['full']['dice']),full_recall=printable(fractions['full']['recall']),
                predicted_to_GT_volume_ratio=printable(ratio(full['pred_foreground'],full['gt_foreground'])),
                tail_FP=item['metrics']['tail']['fp'],tail_FP_fraction_of_all_FP=printable(ratio(item['metrics']['tail']['fp'],full['fp']))))
        assert len(patients)==4
        pm={p:{part:{metric:mean([v[part][metric] for v in rows]) for metric in METRICS} for part in ['full','anchors','missing','tail']} for p,rows in patients.items()}
        aggregate={part:{metric:mean([v[part][metric] for v in pm.values()]) for metric in METRICS} for part in ['full','anchors','missing','tail']}
        for patient,v in pm.items():
            for part in v:
                for metric,value in v[part].items():
                    reported=arm['validation_aggregate']['patients'][patient]['metrics'][part][metric]
                    assert (value is None)==(reported is None)
                    if value is not None:maxerror=max(maxerror,abs(float(value)-reported));assert maxerror<=3e-12
        for part,v in aggregate.items():
            for metric,value in v.items():
                reported=arm['validation_aggregate']['patient_first_means'][part][metric]
                assert (value is None)==(reported is None)
                if value is not None:maxerror=max(maxerror,abs(float(value)-reported));assert maxerror<=3e-12
        gates=dict(mean_full_dice_ge_070=aggregate['full']['dice']>=F(7,10),mean_missing_dice_ge_065=aggregate['missing']['dice']>=F(13,20),
            mean_full_recall_ge_070=aggregate['full']['recall']>=F(7,10),mean_full_absRVE_le_050=aggregate['full']['absolute_relative_volume_error']<=F(1,2),
            all_four_patient_full_missing_dice_positive=all(v['full']['dice']>0 and v['missing']['dice']>0 for v in pm.values()),
            no_series_complete_miss=all(v['metrics']['full']['tp']>0 for v in arm['series']))
        assert gates==arm['validation_gates']
        arms[arm['name']]=dict(kind=arm['kind'],augmentation=arm['augmentation'],patient_metrics=pm,aggregate=aggregate,gates=gates,all9_series=series)
    comparisons=[]
    for kind in ['native_reference','raw_pchip']:
        b=arms[kind+'_intensity'];a=arms[kind+'_spatial'];deltas=[]
        for patient in sorted(a['patient_metrics']):
            am=a['patient_metrics'][patient];bm=b['patient_metrics'][patient]
            deltas.append(dict(patient=patient,full_Dice=am['full']['dice']-bm['full']['dice'],missing_Dice=am['missing']['dice']-bm['missing']['dice'],
                full_recall=am['full']['recall']-bm['full']['recall'],full_absRVE=am['full']['absolute_relative_volume_error']-bm['full']['absolute_relative_volume_error']))
        delta=mean([v['full_Dice'] for v in deltas]);leave=[dict(omitted=v['patient'],full_Dice_delta=printable(mean([x['full_Dice'] for x in deltas if x['patient']!=v['patient']]))) for v in deltas]
        comparisons.append(dict(kind=kind,contrast='spatial2992-minus-intensity2992',matched_budget=True,all4_patient_deltas=[{k:printable(v) if k!='patient' else v for k,v in row.items()} for row in deltas],
            exact_patient_first_full_Dice_delta=printable(delta),positive_Dice_patients=sum(v['full_Dice']>0 for v in deltas),negative_Dice_patients=sum(v['full_Dice']<0 for v in deltas),
            negative_recall_patients=sum(v['full_recall']<0 for v in deltas),all4_descriptive_leave_one_out_means=leave,leave_one_out_is_not_independent_test=True))
    serial_arms={name:dict(kind=a['kind'],augmentation=a['augmentation'],gates=a['gates'],patient_metrics={p:{part:{k:printable(v) for k,v in values.items()} for part,values in pm.items()} for p,pm in a['patient_metrics'].items()},
        aggregate={part:{k:printable(v) for k,v in values.items()} for part,values in a['aggregate'].items()},all9_series=a['all9_series']) for name,a in arms.items()}
    result=dict(complete=True,errors=[],all36_series_count_partitions_verified=True,all144_region_metric_trees_verified=True,metric_values_checked=checked,max_reported_metric_error=maxerror,
        all_patient_first_aggregates_and_six_gates_exactly_verified=True,all_four_medical_branches_failed=True,arms=serial_arms,matched_comparisons=comparisons,
        threshold_searched=False,postprocessing_added=False,case_or_checkpoint_selected=False,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,confirmation_patients_opened=False,lockedIXI_opened=False,independent_patient_confirmation=False,publication_claim_confirmed=False,goal_status='active',
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,source_bindings=[entry(p) for p in [Path(__file__),HERE/'MEDICAL_FAILURE_DECOMPOSITION_PROTOCOL.md',HERE/'NULL_AGGREGATION_RECOVERY_PROTOCOL.md',HERE/'audit_medical_failure_decomposition.py',HERE/'build_decomposition_null_recovery.py',
            rpath,exitfile,S/'ACTUAL_EVALUATION_TERMINAL_TOOL.json',S/'FINAL_MATCHED_COMPARISON.json']])
    assert all(not all(a['gates'].values()) for a in arms.values())
    dump(out/'receipt.json',result);assert time.perf_counter()-started<60 and (out/'receipt.json').stat().st_size<100000
    print(json.dumps({k:v for k,v in result.items() if k not in ['arms','source_bindings']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
