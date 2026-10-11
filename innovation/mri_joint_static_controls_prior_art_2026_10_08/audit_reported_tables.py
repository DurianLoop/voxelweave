"""CPU audit of metric-specific static baselines and reported ranking reversals."""
import json,sys,time
from decimal import Decimal
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();tick=time.perf_counter()
    source=HERE/'PAPER_TABLE_TRANSCRIPTION.json';data=json.loads(source.read_text(encoding='utf-8'),parse_float=Decimal)
    m=data['masc'];results=[]
    for cohort in ('hip10','hip5','fastMRI10'):
        d=m[cohort]
        for i,(metric,maximize) in enumerate(zip(m['metrics'],m['maximize'])):
            values={k:v[i] for k,v in d['static_with_MAR'].items()}
            best=(max if maximize else min)(values.values());best_names=[k for k,v in values.items() if v==best]
            ours=d['MASC'][i];benefit=(ours-best) if maximize else (best-ours)
            assert benefit>0
            results.append(dict(cohort=cohort,metric=metric,best_static_methods=best_names,best_static_value=str(best),
                MASC_value=str(ours),absolute_benefit=str(benefit),
                relative_benefit_percent=None if metric=='PSNR' else str(Decimal(100)*benefit/best),
                static_set_only=True,paired_significance_recomputed=False))
    t=data['thesis'];changes=[]
    for i,c in enumerate(t['conditions']):
        final=t['table6_2_final25_SSIM']['RL'][i]-t['table6_2_final25_SSIM']['LBCS'][i]
        auc=t['table6_3_sampling_rate_SSIM_AUC']['RL'][i]-t['table6_3_sampling_rate_SSIM_AUC']['LBCS'][i]
        changes.append(dict(condition=c,RL_minus_LBCS_final_SSIM=str(final),RL_minus_LBCS_SSIM_AUC=str(auc),
            strict_sign_reversal=final*auc<0,rounded_endpoint_tie=final==0,rounded_AUC_tie=auc==0))
    ddqn=[]
    for name in ('DS-DDQN','SS-DDQN'):
        ddqn.append(dict(policy=name,differences=[dict(metric=metric,policy_minus_LBCS=str(p-c))
            for metric,p,c in zip(t['table6_4_metrics'],t['table6_4'][name],t['table6_4']['LBCS'])]))
    frozen=[]
    for i,metric in enumerate(m['metrics']):
        ours=m['hip10']['MASC'][i];old=m['frozen_metal_PPO_pretrained_MAR'][i]
        gain=(ours-old) if m['maximize'][i] else (old-ours)
        frozen.append(dict(metric=metric,absolute_benefit=str(gain),
            relative_benefit_percent=None if metric=='PSNR' else str(Decimal(100)*gain/old)))
    assert [v*m['slices_per_subject'] for v in m['hip_split_subjects']]==m['hip_split_slices']
    bindings=[Path(__file__),source,HERE/'primary_attempt01/masc.pdf',HERE/'thesis_size_verified_attempt02/cartesian_thesis.pdf']
    bindings += [HERE/'visual_attempt01'/f'masc_page{n:03d}.png' for n in (10,11,12,18)]
    bindings += [HERE/'visual_attempt01'/f'thesis_page{n:03d}.png' for n in (110,112)]
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[base.entry(p) for p in bindings],metric_specific_static_comparisons=results,
        thesis_endpoint_aggregation_comparisons=changes,thesis_DDQN_LBCS_differences=ddqn,
        MASC_frozen_comparison=frozen,hip_subject_slice_counts_agree=True,
        independent_patient_or_repeat_count_not_inferred=True,rounded_reported_means_only=True,
        statistical_significance_not_recomputed=True,model_or_medical_arrays_loaded=0,
        neural_forwards=0,GPU_forwards=0,training_updates=0,new_action_labels_generated=0,
        new_MRI_effect_measured=False,publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-tick)
    out=HERE/'table_audit_attempt01';out.mkdir(exist_ok=False);base.new(out/'receipt.json',result)
    print(json.dumps(dict(complete=True,hip10_best_static=results[:5],thesis_rank_changes=changes,
        hip_counts_agree=True,neural_forwards=0),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
