"""Exact recurring thirds exercise conservative serialization and pre-rounding harm events."""
import hashlib,json,sys
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/patient_complete_series_panel_rounding_qualification_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    import patient_complete_series_panel_2026_10_07 as w
    from patient_risk_cost_baseline_executor_2026_10_07 import validate_panel
    costs={k:'0' for k in w.COST_PHASES};uids=['SYNTHETIC_THIRD_1','SYNTHETIC_THIRD_2','SYNTHETIC_THIRD_3']
    expected={'SYNTHETIC_THIRD_PATIENT':uids};records=[];shared=[];policies=['BASE','LOW']
    for policy in policies:
        for i,uid in enumerate(uids):
            records.append(dict(patient_id='SYNTHETIC_THIRD_PATIENT',uid=uid,policy_id=policy,
                full_fov=True,label_used_for_inference=False,full_dice='1' if policy=='BASE' and i==0 else '0',
                full_recall='1' if i==0 else '0',full_absRVE='1' if i==0 else '0',cost_components=dict(costs)))
        shared.append(dict(patient_id='SYNTHETIC_THIRD_PATIENT',policy_id=policy,cost_components=dict(costs)))
    below='0.333333333333333333333333333333';above='0.333333333333333333333333333334'
    low=w.complete_panel(records,expected,policies,'BASE',shared,'optimization',below,below)
    high=w.complete_panel(records,expected,policies,'BASE',shared,'optimization',above,above)
    for panel in (low,high):validate_panel(panel)
    one_third=F(1,3);up=F(low['risks']['positive_dice_drop'][1][0])
    assert 0<up-one_third<F(1,10**29)
    assert low['risks']['harm_event'][1][0]=='1' and high['risks']['harm_event'][1][0]=='0'
    assert low['risks']['rve_tail'][0][0]=='1' and high['risks']['rve_tail'][0][0]=='0'
    sources=[Path(__file__),ROOT/'experiments/patient_complete_series_panel_2026_10_07.py',
        ROOT/'experiments/patient_risk_cost_baseline_executor_2026_10_07.py',ROOT/'PATIENT_COMPLETE_SERIES_PANEL_PROTOCOL_2026-10-07.md']
    bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources]
    for p in sources:(OUT/(p.name+'.source_snapshot')).write_bytes(p.read_bytes())
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),source_bindings=bindings,
        synthetic_only=True,input_records=records,shared_costs=shared,expected_series=expected,policy_ids=policies,baseline_id='BASE',
        below_threshold=below,above_threshold=above,below_panel=low,above_panel=high,
        exact_event_comparison_before_rounding_verified=True,nonterminating_continuous_loss_rounds_up=True,
        serialized_panels_accepted_by_executor=True,MRI_data_reads=0,GT_reads=0,model_forwards=0,GPU_forwards=0,
        training_updates=0,actual_MRI_risk_certificates_issued=0,publication_claim_confirmed=False)
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as s:json.dump(r,s,indent=2);s.write('\n')
    print(json.dumps(dict(complete=True,exact_event_comparison_before_rounding_verified=True,nonterminating_continuous_loss_rounds_up=True)));return 0
if __name__=='__main__':raise SystemExit(main())
