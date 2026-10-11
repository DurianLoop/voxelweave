"""Metadata-only eligibility audit; no MRI arrays, checkpoints, CUDA, or training control."""
import argparse,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TRAIN=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
EVAL=ROOT/'experiments/mc_rc_3d_19series_common_init_final_eval_2026_10_07_attempt01'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    out=(ROOT/args.output).resolve();assert out.is_relative_to(ROOT) and not out.exists()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),ready=False,complete=False,errors=[],checks={},missing_files=[],failed_conditions=[],
        script_sha256=sha(__file__),MRI_arrays_loaded=0,model_checkpoints_loaded=0,CUDA_initialized=False,
        actual_training_updates=0,other_processes_modified=False,publication_claim_confirmed=False,goal_status='active')
    read_files=[];mutable_read_observations=[]
    def load(relative):
        p=ROOT/relative
        if not p.is_file():r['missing_files'].append(relative);return None
        payload=p.read_bytes();record=dict(path=relative,sha256=hashlib.sha256(payload).hexdigest())
        if relative=='experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/invocation02.json':
            mutable_read_observations.append(record)
        else:read_files.append(record)
        return json.loads(payload)
    def condition(name,value):
        value=bool(value);r['checks'][name]=value
        if not value:r['failed_conditions'].append(name)
    def check_receipt(relative,result_relative,field):
        e=load(relative);p=ROOT/result_relative
        return bool(e and e.get(field+'_observed_tool_exit')==0 and p.is_file() and
            e.get(field+'_result_sha256')==sha(p) and e.get(field+'_result_file',result_relative if field=='evaluation' else None)==result_relative)
    try:
        t=load('experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/invocation02.json')
        condition('original_training_terminal_result',t and t.get('complete') and t.get('status')=='completed_segment' and not t.get('errors'))
        condition('both_original_last19998_frozen',t and t.get('formal_final_budget_completed') and t.get('all_last_weights_frozen') and
            all((TRAIN/(k+'_last19998.pt')).is_file() for k in ('native_reference','raw_pchip')))
        training_receipt=load('SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json')
        condition('actual_training_exit_receipt_bound',training_receipt and training_receipt.get('training_observed_tool_exit')==0 and
            training_receipt.get('formal_training_updates')==39996 and
            training_receipt.get('training_result_file')=='experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/invocation02.json' and
            training_receipt.get('training_result_sha256')==sha(TRAIN/'invocation02.json'))
        q=load('experiments/mc_rc_3d_19series_common_init_final_eval_2026_10_07_attempt01/evaluation_attempt01.json')
        condition('original_all56_evaluation_complete',q and q.get('complete') and q.get('status')=='completed' and not q.get('errors') and q.get('prediction_files_saved')==56)
        condition('actual_original_evaluation_exit_receipt_bound',check_receipt('SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_EVALUATION_2026-10-07.json',
            'experiments/mc_rc_3d_19series_common_init_final_eval_2026_10_07_attempt01/evaluation_attempt01.json','evaluation'))
        names={'mean_full_dice_ge_070','mean_missing_dice_ge_065','mean_full_recall_ge_070','mean_full_absRVE_le_050',
            'all_four_patient_full_missing_dice_positive','no_series_complete_miss'}
        arms=q.get('arms',[]) if q else []
        condition('both_original_arms_six_validation_gates',len(arms)==2 and {a.get('kind') for a in arms}=={'native_reference','raw_pchip'} and
            all(a.get('complete') and set(a.get('validation_gates',{}))==names and all(a['validation_gates'].values()) and
                len(a.get('series',[]))==28 and sum(s.get('role')=='development' for s in a['series'])==19 and
                sum(s.get('role')=='validation' for s in a['series'])==9 for a in arms))
        v=load('experiments/mc_rc_3d_19series_common_init_final_eval_2026_10_07_attempt01/independent_all56_attempt01.json')
        condition('original_all56_independent_and_strict',v and v.get('complete') and not v.get('errors') and not v.get('numerical_failures') and
            v.get('all56_prediction_files_and_metrics_verified') and v.get('all_strict_numeric_gates_passed') and q and v.get('source_sha256')==sha(EVAL/'evaluation_attempt01.json'))
        condition('actual_original_verifier_exit_receipt_bound',check_receipt('SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_VERIFIER_2026-10-07.json',
            'experiments/mc_rc_3d_19series_common_init_final_eval_2026_10_07_attempt01/independent_all56_attempt01.json','verifier'))
        p=load('experiments/mc_rc_3d_paired_sampling_fov_qualification_2026_10_07/attempt01.json')
        condition('paired_sampler_and_full_patch_FOV_complete',p and p.get('complete') and not p.get('errors') and len(p.get('sampler_checks',[]))==24 and
            p.get('synthetic_updates_completed')==6 and len(p.get('FOV_checks',[]))==2 and all(a.get('threshold_disagreements')==0 and a.get('complete_FOV_covered') for a in p['FOV_checks']))
        c=load('experiments/mc_rc_3d_two_channel_coordinate_diagnostic_2026_10_07/attempt01.json')
        condition('separate_two_channel_coordinate_interpreters',c and c.get('complete') and not c.get('errors') and c.get('all_float32_and_float64_coordinate_replays_passed'))
        e=load('SESSION_OBSERVED_EXITS_PAIRED_SAMPLING_FOV_2026-10-07.json')
        condition('actual_new_synthetic_exits_bound',e and e.get('paired_qualification_observed_tool_exit')==0 and e.get('coordinate_diagnostic_observed_tool_exit')==0 and
            e.get('paired_result_sha256')==sha(ROOT/'experiments/mc_rc_3d_paired_sampling_fov_qualification_2026_10_07/attempt01.json') and
            e.get('coordinate_result_sha256')==sha(ROOT/'experiments/mc_rc_3d_two_channel_coordinate_diagnostic_2026_10_07/attempt01.json'))
        r['source_bindings']=read_files;r['mutable_read_observations_not_frozen']=mutable_read_observations
        r['original_ideal_coordinate_absolute_gates_passed']=c.get('all_original_ideal_absolute_gates_passed') if c else None
        r['original_ideal_absolute_failure_not_overridden']=True;r['ready']=all(r['checks'].values());r['complete']=True
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}')
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:r[k] for k in ('complete','ready','errors','missing_files','failed_conditions','MRI_arrays_loaded','model_checkpoints_loaded')},ensure_ascii=False))
    return 1 if not r['complete'] else (0 if r['ready'] else 3)
if __name__=='__main__':raise SystemExit(main())
