"""CPU arithmetic audit of visually checked paper summaries, not MRI experiments."""
import json,sys,time
from decimal import Decimal
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base

def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();tick=time.perf_counter()
    table=HERE/'PAPER_TABLE_TRANSCRIPTION.json'
    d=json.loads(table.read_text(encoding='utf-8'),parse_float=Decimal)
    doc=d['diagnostic'];comparisons=[]
    for metric in ('AUC','RECALL','SPECIFICITY'):
        policy=doc[metric]['Policy Classifier'];assert len(policy)==18
        for control in ('Policy Reconstruction','Undersampled'):
            values=doc[metric][control];assert len(values)==18
            rows=[]
            for i,(p,c) in enumerate(zip(policy,values)):
                rows.append(dict(center_fraction=doc['center_fractions'][i//6],
                    sample_rate_percent=doc['sample_rates_percent'][i%6],
                    policy=str(p),control=str(c),difference=str(p-c)))
            comparisons.append(dict(metric=metric,control=control,conditions=rows,
                positive=sum(p>c for p,c in zip(policy,values)),
                negative=sum(p<c for p,c in zip(policy,values)),
                ties=sum(p==c for p,c in zip(policy,values)),independent_patient_count=None))
    costs=d['l2sr'];ratios=[]
    for i,name in enumerate(costs['conditions']):
        ours=costs['L2S_and_L2SR'][i];pg=costs['PG_MRI'][i];rand=costs['Random_and_LOUPE'][i]
        ratios.append(dict(condition=name,L2S_L2SR_seconds=str(ours),PG_MRI_seconds=str(pg),
            Random_LOUPE_seconds=str(rand),PG_over_L2S_L2SR_ratio=str(pg/ours),
            L2S_L2SR_over_Random_LOUPE_ratio=str(ours/rand),
            scope='Reported algorithm inference only; no local MRI action-cost measurement.'))
    sourcepaths=[Path(__file__),table,HERE/'primary_attempt01/diagnostic.pdf',HERE/'primary_attempt01/l2sr.pdf',
        HERE/'primary_attempt01/diagnostic_page04.txt',HERE/'primary_attempt01/diagnostic_page11.txt',
        HERE/'primary_attempt01/l2sr_page18.txt',HERE/'primary_attempt01/l2sr_page29.txt',
        HERE/'visual_attempt01/diagnostic_page11.png',HERE/'visual_detail_attempt01/diagnostic_table2_detail.png',
        HERE/'visual_attempt01/l2sr_page18.png']
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[base.entry(p) for p in sourcepaths],comparisons=comparisons,reported_cost_ratios=ratios,
        split_slice_sum=sum(doc['split_slices'].values()),reported_total_slices=doc['reported_slices'],
        reported_slice_sum_agrees=sum(doc['split_slices'].values())==doc['reported_slices'],
        reported_values_do_not_prove_patient_split=True,reported_values_are_not_raw_patient_predictions=True,
        rounded_table_conditions_not_independent_replicates=True,statistical_significance_not_tested=True,
        model_or_medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,
        new_action_labels_generated=0,new_MRI_effect_measured=False,elapsed_seconds=time.perf_counter()-tick,
        publication_claim_confirmed=False,goal_status='active')
    out=HERE/'table_audit_attempt01';out.mkdir(exist_ok=False);base.new(out/'receipt.json',result)
    print(json.dumps(dict(complete=True,summary=[{k:r[k] for k in ('metric','control','positive','negative','ties')} for r in comparisons],
        reported_cost_ratios=ratios,split_slice_sum=result['split_slice_sum'],neural_forwards=0),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
