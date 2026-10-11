"""Metadata-only matched-cost accounting with two explicitly different flows."""
import hashlib,json,sys
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'experiments/mc_rc_matched_anchor_oracle_2026_10_08/attempt01.json'
PROOF=SOURCE.parent/'independent_labels_disk_fraction_attempt01.json'
OUT=ROOT/'experiments/mc_rc_matched_oracle_budget_scenarios_2026_10_08'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def val(f):return dict(exact=str(f),value=float(f))
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);s=read(SOURCE);assert s['complete'] and not s['errors']
    proof=read(PROOF);assert proof['complete'] and not proof['errors'] and proof['checked_series']==19
    names=[x['method'] for x in s['summaries']];people=sorted({x['patient'] for x in s['series']});results=[]
    for name in names:
        rows=[]
        for c in s['series']:
            a=c['oracle'] if name==names[0] else c['frozen_predictions'][name];g=a['geometry_cost'];n=g['full_forward_calls'];k=g['recomputed_batch_pairs'];t=len(g['affected_tile_ids']);repacked=(t+1)//2
            assert k<=n and repacked<=k and k==len(g['recomputed_batch_pair_ids'])
            rows.append(dict(patient=c['patient'],uid=c['uid'],N=n,k=k,affected_tiles=t,hypothetical_repacked_k=repacked,
                strict_break_even_actions_scenario_A=n//(n-k)+1 if k<n else None,ROI_gates_passed=a['roi']['gate_passed'],
                scenario_A_ratios={str(m):val(Fraction(n+m*k,m*n)) for m in (1,2,5,10)},scenario_B_ratios={str(m):val(Fraction(n+m*k,(m+1)*n)) for m in (1,2,5,10)}))
        subjects=[]
        for p in people:
            a=[c for c in rows if c['patient']==p];subjects.append(dict(patient=p,N=sum(c['N'] for c in a),k=sum(c['k'] for c in a),repacked_k=sum(c['hypothetical_repacked_k'] for c in a)))
        ratios={}
        for scenario in ('A','B'):
            aggregates={}
            for m in (1,2,5,10):
                dense_multiplier=m if scenario=='A' else m+1
                legacy=sum(sum(Fraction(c['N']+m*c['k'],dense_multiplier*c['N']) for c in rows if c['patient']==p)/sum(c['patient']==p for c in rows) for p in people)/11
                patients=sum(Fraction(c['N']+m*c['k'],dense_multiplier*c['N']) for c in subjects)/11
                pooled=Fraction(sum(c['N']+m*c['k'] for c in rows),dense_multiplier*sum(c['N'] for c in rows))
                assert Fraction(sum(c['N']+m*c['k'] for c in subjects),dense_multiplier*sum(c['N'] for c in subjects))==pooled
                aggregates[str(m)]=dict(legacy_patient_series_equal=val(legacy),complete_patient_workload_equal=val(patients),pooled_workload=val(pooled))
            ratios[scenario]=aggregates
        n=sum(c['N'] for c in rows);k=sum(c['k'] for c in rows);repacked=sum(c['hypothetical_repacked_k'] for c in rows)
        results.append(dict(method=name,N_total=n,k_total=k,hypothetical_repacked_k_total=repacked,
            hypothetical_original_pair_packing_call_reduction=val(Fraction(k-repacked,k)) if k else None,
            hypothetical_patient_workload_equal_repacked_conditional_saving=val(sum(Fraction(c['N']-c['repacked_k'],c['N']) for c in subjects)/11),
            aggregate_cost_scenarios=ratios,series=rows,patient_workloads=subjects))
    labels={}
    for conn in ('6','26'):
        a=[c['label_components']['connectivity'][conn] for c in s['series']]
        labels[conn]=dict(full_GT_components=sum(x['count'] for x in a),components_with_missing=sum(x['components_with_missing'] for x in a),
            missing_components_without_observed_contact=sum(x['missing_components_without_observed_contact'] for x in a),foreground_voxels=sum(x['total_foreground_voxels'] for x in a))
    assert labels['6']['foreground_voxels']==labels['26']['foreground_voxels']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in (Path(__file__),SOURCE,PROOF,ROOT/'MC_RC_MATCHED_ANCHOR_ORACLE_PROTOCOL_2026-10-08.md')],
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,latency_measured=False,clinical_benefit_measured=False,publication_claim_confirmed=False,confirmation_patients_opened=False,
        scenarios=dict(A='cached initialization required, dense candidates do not require an additional baseline',B='both actual workflows require the same baseline; initialization paid equally'),
        hypothetical_repacking_not_executed_or_output_qualified=True,label_contact_is_not_MRI_detectability=True,component_counts=labels,models=results)
    (OUT/'attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(component_counts=labels,models=[dict(method=x['method'],N=x['N_total'],k=x['k_total'],hypothetical_repacked_k=x['hypothetical_repacked_k_total'],cold_A5_patient=x['aggregate_cost_scenarios']['A']['5']['complete_patient_workload_equal'],shared_B5_patient=x['aggregate_cost_scenarios']['B']['5']['complete_patient_workload_equal']) for x in results])),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
