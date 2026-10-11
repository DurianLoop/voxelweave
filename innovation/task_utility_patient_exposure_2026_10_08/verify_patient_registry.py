"""Independent metadata join/group/exposure replay; no production adapter imports."""
import hashlib,json,sys,time
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def load(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    sys.stdout.reconfigure(encoding='utf-8');out=HERE/'patient_registry_independent_attempt01';out.mkdir(exist_ok=False)
    tick=time.perf_counter();rp=HERE/'patient_registry_attempt03/receipt.json';r=load(rp)
    cfgp=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/frozen_config.json';cfg=load(cfgp)
    tabp=ROOT/'experiments/observed_holdout_feature_table_2026_10_08.json';tab=load(tabp)
    assert r['complete'] and not r['errors'] and len(r['negative_checks'])==11 and all(x['rejected'] for x in r['negative_checks'])
    byuid={row['series_uid']:row for row in tab['rows']};assert len(byuid)==len(tab['rows'])==19
    bypatient={p:[] for p in cfg['patient_ids']}
    for row in cfg['series']:
        uid=row['uid'];by=byuid[uid];assert by['patient']==row['patient'];bypatient[row['patient']].append(uid)
    assert sorted(bypatient)==r['registry']['patient_ids'] and len(bypatient)==11
    registryrows={v['series_uid']:v for v in r['registry']['series']};assert set(registryrows)==set(byuid)
    for uid,row in byuid.items():
        assert registryrows[uid]['features']==row['features']
        assert registryrows[uid]['observed_package_sha256']==row['observed_package_sha256']
        assert all(registryrows[uid][k] is None for k in ('MRI_task_labels','action_utility_labels','full_action_cost'))
    check=[];all_held=[]
    for fold in r['folds']:
        patient=fold['heldout_patient'];assert patient in bypatient
        assert fold['head_heldout_patients']==[patient]
        assert fold['head_training_patients']==sorted(set(bypatient)-{patient})
        testuids=[v['series_uid'] for v in fold['head_heldout_series']]
        trainuids=[v['series_uid'] for v in fold['head_training_series']]
        assert sorted(testuids)==sorted(bypatient[patient])
        assert sorted(trainuids)==sorted(uid for p,uu in bypatient.items() if p!=patient for uid in uu)
        assert set(testuids).isdisjoint(trainuids) and len(testuids)+len(trainuids)==19
        for v in fold['head_heldout_series']+fold['head_training_series']:
            assert v['patient']==byuid[v['series_uid']]['patient']
            assert v['observed_package_sha256']==byuid[v['series_uid']]['observed_package_sha256']
        assert patient in cfg['patient_ids'] and fold['task_model_patient_excluded'] is False
        assert fold['pipeline_patient_out'] is False and fold['label_scope']=='development_task_in_sample'
        assert fold['fitted_head'] is fold['feature_scaler'] is fold['selected_threshold'] is None
        all_held.extend(testuids);check.append(dict(patient=patient,training_series=len(trainuids),heldout_series=len(testuids),task_seen=True))
    assert len(check)==len({v['patient'] for v in check})==11 and sorted(all_held)==sorted(byuid)
    assert r['readiness']['ready'] is False and r['readiness']['actual_task_labels']==0
    for b in r['source_bindings']:
        p=ROOT/b['path'];assert entry(p)==b
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(rp),entry(cfgp),entry(tabp)],
        independently_rebuilt_patient_groups=check,all19_feature_values_and_sources_exact=True,
        independently_verified_head_folds=11,unique_patients=11,unique_series=19,task_seen_heldout_folds=11,
        pipeline_patient_out_folds=0,original_negative_branch_records_verified=True,
        negative_branches_reexecuted_by_this_verifier=False,medical_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,GPU_forwards=0,training_updates=0,head_fits=0,
        elapsed_seconds=time.perf_counter()-tick,publication_claim_confirmed=False,goal_status='active')
    assert result['elapsed_seconds']<=120
    with (out/'receipt.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:result[k] for k in ('complete','independently_verified_head_folds','unique_series',
        'task_seen_heldout_folds','pipeline_patient_out_folds','elapsed_seconds')},ensure_ascii=False),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
