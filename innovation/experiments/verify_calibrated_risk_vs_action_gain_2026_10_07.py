"""Independent integer/Fraction verification of finite synthetic routing evidence."""
import hashlib,json,sys
from fractions import Fraction
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'experiments/calibrated_risk_vs_action_gain_2026_10_07/attempt01.json'
OUT=SOURCE.parent/'independent_attempt01.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parse(row):
    q=Fraction(row['numerator'],row['denominator']);assert float(q)==row['value'];return q
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not OUT.exists()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        source_bindings=[dict(path=SOURCE.relative_to(ROOT).as_posix(),sha256=sha(SOURCE))],
        MRI_arrays_loaded=0,model_forwards=0,training_updates=0,new_theorem_claimed=False)
    try:
        s=json.loads(SOURCE.read_text(encoding='utf-8'));assert s['complete'] and not s['errors']
        for b in s['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        assert [g['four_cell_counts'] for g in s['groups']]==[[0,10,5,85],[30,10,50,10],[60,0,30,10],[90,0,10,0]]
        base=[];alternative=[]
        for group in s['groups']:
            both_correct,only_action_wrong,only_base_wrong,both_wrong=group['four_cell_counts']
            n=both_correct+only_action_wrong+only_base_wrong+both_wrong;assert n==100
            a=only_base_wrong+both_wrong;b=only_action_wrong+both_wrong
            assert parse(group['baseline_risk'])==Fraction(a,n) and parse(group['action_risk'])==Fraction(b,n)
            assert parse(group['gain'])==Fraction(a-b,n)
            assert group['baseline_calibration_error']==group['action_calibration_error']==0
            base.append(a);alternative.append(b)
        for policy in s['policies']:
            chosen=[ord(c)-65 for c in policy['selected_groups']];assert len(set(chosen))==len(chosen)
            errors=sum(alternative[i] if i in chosen else base[i] for i in range(4))
            assert policy['action_calls']==100*len(chosen) and policy['total_errors']==errors
            assert parse(policy['system_error'])==Fraction(errors,400)
            assert policy['net_error_reduction']==sum(base)-errors
        curve=s['nested_acceptance_error_curve'];assert [p['total_errors'] for p in curve]==[200,205,165,135,125]
        for left,right in zip(curve,curve[1:]):assert set(left['selected_groups'])<set(right['selected_groups'])
        assert parse(s['random_one_group_expected_net_error_reduction'])==Fraction(75,4)
        for row in s['CRC_finite_n_arithmetic']:
            n=row['n'];alpha=parse(row['alpha']);bound=Fraction(1,n+1)
            assert parse(row['zero_empirical_corrected'])==bound
            assert row['zero_empirical_satisfies_corrected_inequality']==(bound<=alpha)
            assert parse(row['maximum_empirical_risk_for_corrected_inequality'])==(alpha*(n+1)-1)/n
            assert row['real_MRI_calibration_authorized'] is False
        assert s['gain_and_cost_routing_equivalent_permutations']==24 and all(s['gates'].values())
        r.update(complete=True,finite_groups_verified=4,policy_rows_verified=len(s['policies']),
            finite_n_rows_verified=len(s['CRC_finite_n_arithmetic']),exact_curve_errors=[200,205,165,135,125],
            calibration_does_not_imply_positive_correction_gain=True,nonmonotone_loss_not_a_CRC_guarantee=True)
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}')
    with OUT.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r));return 0 if r['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
