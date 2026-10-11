"""Exact Decimal audits of published summaries, not MRI patient effects or p-values."""
import json,sys,time
from decimal import Decimal as D
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def dec(v):return D(str(v))
def diff(a,b):return float(dec(a)-dec(b))
def reduction(old,new):return float(100*(dec(old)-dec(new))/dec(old))

def main():
    sys.stdout.reconfigure(encoding='utf-8');tick=time.perf_counter();resource_guard();out=HERE/'table_audit_attempt01';out.mkdir(exist_ok=False)
    p=HERE/'PAPER_TABLE_TRANSCRIPTION.json';q=json.loads(p.read_text(encoding='utf-8'));compute=[];quality=[];fixed=[];penalty=[];mitigation=[];totals=[]
    t=q['tadt_table3']
    for i,s in enumerate(t['scales']):
        sw,b,ta=[t[k][i] for k in ('SwinIR_GFLOPs','Baseline_GFLOPs','TADT_GFLOPs')]
        assert dec(sw)-dec(ta)==(dec(sw)-dec(b))+(dec(b)-dec(ta))
        compute.append(dict(scale=s,total_vs_SwinIR_GFLOPs_reduction_percent=reduction(sw,ta),
            backbone_vs_SwinIR_GFLOPs_reduction_percent=reduction(sw,b),
            routing_vs_own_Baseline_GFLOPs_reduction_percent=reduction(b,ta),
            nonrouting_backbone_absolute_saved_GFLOPs=diff(sw,b),routing_absolute_saved_GFLOPs=diff(b,ta),
            same_measured_latency_not_implied=True,fully_matched_extra_training_not_established_by_table=True))
    t=q['tadt_table1_LIIF']
    for i,s in enumerate(t['scales']):
        quality.append(dict(scale=s,TADT_minus_own_Baseline_PSNR_dB=diff(t['TADT_PSNR_dB'][i],t['Baseline_PSNR_dB'][i]),
            TADT_minus_SwinIR_PSNR_dB=diff(t['TADT_PSNR_dB'][i],t['SwinIR_PSNR_dB'][i]),
            Baseline_minus_SwinIR_PSNR_dB=diff(t['Baseline_PSNR_dB'][i],t['SwinIR_PSNR_dB'][i])))
    t=q['tadt_table4']
    for i,s in enumerate(t['scales']):
        fixed.append(dict(scale=s,TARC_minus_fixed05_PSNR_dB=diff(t['TARC_PSNR_dB'][i],t['fixed_beta_05_PSNR_dB'][i]),
            TARC_minus_fixed025s_PSNR_dB=diff(t['TARC_PSNR_dB'][i],t['fixed_beta_025s_PSNR_dB'][i])))
    assert fixed[0]['TARC_minus_fixed05_PSNR_dB']==-.01
    t=q['tadt_table5']
    for i,s in enumerate(t['scales']):
        penalty.append(dict(scale=s,without_minus_with_penalty_PSNR_dB=diff(t['without_penalty_PSNR_dB'][i],t['with_penalty_PSNR_dB'][i]),
            without_minus_with_penalty_GFLOPs=diff(t['without_penalty_GFLOPs'][i],t['with_penalty_GFLOPs'][i]),
            penalty_GFLOPs_reduction_percent=reduction(t['without_penalty_GFLOPs'][i],t['with_penalty_GFLOPs'][i])))
    assert penalty[0]['without_minus_with_penalty_GFLOPs']==388.75
    t=q['medical_table3']
    for i,attr in enumerate(t['attributes']):
        mitigation.append(dict(attribute=attr,reweighted_minus_standard_percentage_points=diff(t['reweighted_percent_change'][i],t['standard_percent_change'][i]),
            EODD_minus_standard_percentage_points=diff(t['EODD_percent_change'][i],t['standard_percent_change'][i]),
            EODD_minus_reweighted_percentage_points=diff(t['EODD_percent_change'][i],t['reweighted_percent_change'][i]),
            differences_of_reported_medians_not_patient_paired_changes=True))
    assert mitigation[0]['EODD_minus_standard_percentage_points']==-16.54
    for key in ('medical_table5','medical_table6'):
        t=q[key];rows=[sum(r) for r in t['cells']];cols=[sum(r[j] for r in t['cells']) for j in range(len(t['cells'][0]))]
        totals.append(dict(table=key,cell_row_sums=rows,printed_row_totals=t['printed_row_totals'],
           row_residual_cell_minus_printed=[a-b for a,b in zip(rows,t['printed_row_totals'])],
           cell_column_sums=cols,printed_column_totals=t['printed_column_totals'],
           printed_grand_total=t['printed_grand_total'],sum_printed_row_totals=sum(t['printed_row_totals']),sum_cells=sum(rows),
           row_totals_match=rows==t['printed_row_totals'],column_totals_match=cols==t['printed_column_totals']))
    assert totals[0]['row_totals_match'] and totals[0]['column_totals_match']
    assert totals[1]['row_residual_cell_minus_printed']==[100,0] and totals[1]['column_totals_match']
    sources=[Path(__file__),p,HERE/'tadt_size_verified_attempt03/tadt.pdf',HERE/'primary_attempt02/medical_shift.pdf']
    sources += [HERE/'visual_attempt01'/name for name in ('tadt_page006.png','tadt_page007.png','medical_shift_page010.png','medical_shift_page028.png')]
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[base.entry(v) for v in sources],
        compute_comparisons=compute,PSNR_LIIF_comparisons=quality,fixed_intensity_comparisons=fixed,penalty_tradeoffs=penalty,
        medical_median_summary_differences=mitigation,medical_table_denominator_checks=totals,
        CPU_arithmetic_only=True,reported_summaries_not_independent_patients=True,patient_significance_not_recomputed=True,
        printed_anomalies_retained_without_repair=True,medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        training_updates=0,new_MRI_benefit_measured=False,publication_claim_confirmed=False,goal_status='active',
        resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-tick)
    base.new(out/'receipt.json',result)
    print(json.dumps(dict(complete=True,x2_routing_GFLOPs_reduction_percent=compute[0]['routing_vs_own_Baseline_GFLOPs_reduction_percent'],
         x2_total_vs_SwinIR_GFLOPs_reduction_percent=compute[0]['total_vs_SwinIR_GFLOPs_reduction_percent'],
         fixed_intensity_counterexample=fixed[0],medical_table6=totals[1])),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
