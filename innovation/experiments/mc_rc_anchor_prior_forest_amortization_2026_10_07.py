"""Metadata-only exact call-count bounds; no new medical arrays or selection."""
import hashlib,json,sys
from fractions import Fraction
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07/attempt01.json'
OUT=ROOT/'experiments/mc_rc_anchor_prior_forest_amortization_2026_10_07'
METHODS=('joint_QDA_empirical_prior_19','joint_QDA_balanced_prior_19','joint_ExtraTrees_balanced_19')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(f):return dict(exact=str(f),value=float(f))
def minimum(n,k):return n//(n-k)+1 if k<n else None
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    source=json.loads(SOURCE.read_text(encoding='utf-8'));assert source['complete'] and not source['errors']
    assert source['all19_predictions_saved_before_full_GT_scoring'] and len(source['series'])==19
    patients=sorted({s['patient'] for s in source['series']});assert len(patients)==11
    result=[]
    for method in METHODS:
        series=[]
        for s in source['series']:
            v=s['methods'][method];q=v['roi']['metrics'];g=v['geometry_cost'];n=g['full_forward_calls'];k=g['recomputed_batch_pairs']
            assert len(g['recomputed_batch_pair_ids'])==k and 0<=k<=n
            gates=dict(foreground=q['foreground_recall']>=.99,boundary=q['boundary_recall']>=.99,tile_foreground=q['tile_foreground_recall']>=.995,area=q['roi_fraction']<=.05,tile_area=q['tile_fraction']<=.10)
            assert all(gates.values())==v['roi']['gate_passed']
            ratios={str(m):Fraction(n+m*k,m*n) for m in (1,2,5,10)}
            assert Fraction(n+5*k,5*n)==Fraction(1,5)+Fraction(k,n)
            series.append(dict(patient=s['patient'],uid=s['uid'],N=n,k=k,gates=gates,failed_gates=[key for key,passed in gates.items() if not passed],minimum_equal_support_actions_for_strict_forward_saving=minimum(n,k),cold_start_forward_count_ratios={key:record(value) for key,value in ratios.items()}))
        workload=[]
        for p in patients:
            rows=[s for s in series if s['patient']==p];n=sum(s['N'] for s in rows);k=sum(s['k'] for s in rows)
            workload.append(dict(patient=p,N=n,k=k,minimum_equal_support_actions_for_strict_forward_saving=minimum(n,k),cold_start_forward_count_ratios={str(m):record(Fraction(n+m*k,m*n)) for m in (1,2,5,10)}))
        n=sum(v['N'] for v in series);k=sum(v['k'] for v in series)
        legacy={};complete_patient={};pooled={}
        for m in (1,2,5,10):
            legacy[str(m)]=record(sum(sum(Fraction(s['N']+m*s['k'],m*s['N']) for s in series if s['patient']==p)/sum(s['patient']==p for s in series) for p in patients)/11)
            complete_patient[str(m)]=record(sum(Fraction(s['N']+m*s['k'],m*s['N']) for s in workload)/11)
            pooled[str(m)]=record(Fraction(n+m*k,m*n))
        result.append(dict(method=method,N_total=n,k_total=k,gate_pass_counts={key:sum(s['gates'][key] for s in series) for key in series[0]['gates']},all_gates_pass=sum(all(s['gates'].values()) for s in series),
            legacy_patient_series_equal_ratios=legacy,complete_patient_workload_equal_ratios=complete_patient,pooled_workload_ratios=pooled,
            pooled_minimum_equal_support_actions=minimum(n,k),series=series,complete_patient_workloads=workload))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in (Path(__file__),SOURCE,ROOT/'MC_RC_ANCHOR_PRIOR_FOREST_AMORTIZATION_PROTOCOL_2026-10-07.md')],
        medical_arrays_loaded=0,model_arrays_loaded=0,new_GT_arrays_loaded=0,model_forwards=0,GPU_forwards=0,training_updates=0,clinical_benefit_measured=False,real_latency_measured=False,publication_claim_confirmed=False,confirmation_patients_opened=False,
        source_independent_check_required_for_final_interpretation=True,models=result)
    (OUT/'attempt01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([dict(method=x['method'],N=x['N_total'],k=x['k_total'],gate_pass_counts=x['gate_pass_counts'],cold5_legacy=x['legacy_patient_series_equal_ratios']['5'],cold5_complete_patient=x['complete_patient_workload_equal_ratios']['5'],cold5_pooled=x['pooled_workload_ratios']['5']) for x in result]),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
