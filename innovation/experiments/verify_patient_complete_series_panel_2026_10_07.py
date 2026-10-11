"""Independent scalar Fraction aggregation, no production adapter imports."""
import hashlib,json,sys,time,traceback
from datetime import datetime,timezone
from decimal import Decimal
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/patient_complete_series_panel_qualification_2026_10_07'
ROUND=ROOT/'experiments/patient_complete_series_panel_rounding_qualification_2026_10_07/attempt01.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def value(x):return F(Decimal(str(x)))
def unpack(x):return F(x['numerator'],x['denominator'])
def replay(c,panel,eps,tau):
    expected=c['expected_series'];policies=c['policy_ids'];patients=list(expected)
    records=c['input_records'];shared=c['shared_costs'];base=c['baseline_id'];eps=value(eps);tau=value(tau)
    required={(p,u,k) for p in patients for u in expected[p] for k in policies}
    actual={(r['patient_id'],r['uid'],r['policy_id']) for r in records}
    assert required==actual and len(required)==len(records)
    assert panel['patient_ids']==patients and panel['policy_ids']==policies
    assert unpack(panel['cohort_patient_weight'])==F(1,len(patients))
    metrics={};count=0
    for p in patients:
        assert unpack(panel['patient_series_weights'][p]['each_series_weight'])==F(1,len(expected[p]))
        for k in policies:
            rows=[r for r in records if r['patient_id']==p and r['policy_id']==k]
            assert len(rows)==len(expected[p]) and all(r['full_fov'] and not r['label_used_for_inference'] for r in rows)
            stats={name:sum((value(r[name]) for r in rows),F(0))/len(rows) for name in ('full_dice','full_recall','full_absRVE')}
            share=[s for s in shared if s['patient_id']==p and s['policy_id']==k];assert len(share)==1
            extra=sum(map(value,share[0]['cost_components'].values()),F(0))
            stats['total_cost']=sum((value(v) for r in rows for v in r['cost_components'].values()),F(0))+extra
            metrics[(p,k)]=stats
            diagnostic=next(x for x in panel['diagnostics'] if x['patient_id']==p and x['policy_id']==k)
            assert diagnostic['series_uids']==expected[p] and diagnostic['series_count']==len(rows)
            assert {name:unpack(v) for name,v in diagnostic['exact_metrics'].items()}==stats
            assert unpack(diagnostic['shared_cost'])==extra
            count+=1
    for j,k in enumerate(policies):
        for i,p in enumerate(patients):
            v=metrics[(p,k)];drop=metrics[(p,base)]['full_dice']-v['full_dice']
            losses=dict(dice_loss=1-v['full_dice'],positive_dice_drop=max(F(0),drop),harm_event=F(int(drop>eps)),
                recall_loss=1-v['full_recall'],rve_tail=F(int(v['full_absRVE']>tau)))
            diagnostic=next(x for x in panel['diagnostics'] if x['patient_id']==p and x['policy_id']==k)
            assert {name:unpack(v) for name,v in diagnostic['exact_losses'].items()}==losses
            for name,exact in losses.items():
                rounded=value(panel['risks'][name][j][i]);assert exact<=rounded<=exact+F(1,10**29)
                if name in ('harm_event','rve_tail'):assert rounded==exact
            assert value(panel['objectives']['total_cost'][j][i])==v['total_cost']
    assert not panel['actual_MRI_risk_certificate_issued'];return count
def main():
    sys.stdout.reconfigure(encoding='utf-8');dest=OUT/'independent_attempt01.json';assert not dest.exists();at=time.perf_counter()
    source=OUT/'attempt01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        source_file=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),
        rounding_source_file=ROUND.relative_to(ROOT).as_posix(),rounding_source_sha256=sha(ROUND),
        production_adapter_imported=False,MRI_data_reads=0,model_forwards=0,GPU_forwards=0,
        actual_MRI_risk_certificates_issued=0,publication_claim_confirmed=False)
    try:
        c=json.loads(source.read_text(encoding='utf-8'));t=json.loads(ROUND.read_text(encoding='utf-8'))
        for parent,result in ((OUT,c),(ROUND.parent,t)):
            assert result['complete'] and not result['errors'] and result['synthetic_only']
            for b in result['source_bindings']:
                p=ROOT/b['path'];assert sha(p)==sha(parent/(p.name+'.source_snapshot'))==b['sha256']
        count=replay(c,c['panel'],c['epsilon'],c['rve_tau'])
        count+=replay(t,t['below_panel'],t['below_threshold'],t['below_threshold'])
        count+=replay(t,t['above_panel'],t['above_threshold'],t['above_threshold'])
        # The two means deliberately differ because A has two series and B has one.
        base=[F(4,5),F(1,5)];mid=[F(3,4),F(2,5)]
        assert sum(base)/2==F(1,2) and sum(mid)/2==F(23,40)
        assert (F(8,10)+F(7,10)+F(4,10))/3==F(19,30)
        assert c['patient_equal_mean_MID_Dice']=='0.575' and unpack(c['series_weighted_mean_MID_Dice_exact'])==F(19,30)
        assert count==8 and len(c['invalid_inputs_rejected'])==12 and all(x['rejected'] for x in c['invalid_inputs_rejected'])
        assert 'patient_complete_series_panel_2026_10_07' not in sys.modules and 'torch' not in sys.modules
        r.update(complete=True,patient_policy_rows_independently_replayed=count,panels_independently_replayed=3,
            unequal_series_means_costs_and_all_risks_exact=True,continuous_rounding_is_conservative=True,
            binary_events_before_rounding_exact=True,invalid_input_rejections_only_record_consistency_checked=True)
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-at
    with dest.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','patient_policy_rows_independently_replayed','panels_independently_replayed','elapsed_seconds')}))
    return 0 if r['complete'] and not r['errors'] else 1
if __name__=='__main__':raise SystemExit(main())
