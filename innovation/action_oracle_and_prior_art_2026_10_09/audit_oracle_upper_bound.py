"""Independent exact cross-product max and Decimal aggregate; no policy/model reproduction."""
import sys,time,json,decimal
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,read,entry,bind,dump
started=time.perf_counter();before=resource_guard();decimal.getcontext().prec=75;D=decimal.Decimal
rp=HERE/'existing_action_oracle_attempt01/receipt.json';r=read(rp);assert r['complete'] and not r['errors']
for b in r['source_bindings']:bind(b)
old=read(ROOT/'spatial_adaptation_matched_2026_10_08/evaluation_attempt01/receipt.json')
arms=[{s['uid']:s for s in a['series']} for n in ['raw_pchip_intensity','raw_pchip_spatial'] for a in old['arms'] if a['name']==n]
assert len(arms)==2 and len(arms[0])==len(arms[1])==9 and set(arms[0])==set(arms[1])
patients={};choices=[]
for uid in sorted(arms[0]):
    ratios=[]
    for a in arms:
        m=a[uid]['metrics']['full'];num=2*m['tp'];den=2*m['tp']+m['fp']+m['fn'];assert den>0
        ratios.append((num,den))
    winner=0 if ratios[0][0]*ratios[1][1]>=ratios[1][0]*ratios[0][1] else 1
    num,den=ratios[winner];p=arms[0][uid]['patient'];patients.setdefault(p,[]).append(D(num)/D(den));choices.append(winner)
assert len(patients)==4
upper=sum((sum(v)/len(v) for v in patients.values()),D(0))/len(patients)
claimed=r['cohorts'][0]['optimistic_series_fullDice_upper_bound']['means']['full_dice']
assert abs(upper-D(claimed['numerator'])/D(claimed['denominator']))<D('1e-70') and upper<D('.7')
assert r['cohorts'][0]['per_series_enumeration']['policies_enumerated']==512 and r['cohorts'][0]['per_series_enumeration']['all_six_gate_passing']==0
assert r['cohorts'][0]['patient_consistent_enumeration']['policies_enumerated']==16 and r['cohorts'][0]['patient_consistent_enumeration']['all_six_gate_passing']==0
result=dict(complete=True,errors=[],independent_decimal_upper_bound=str(upper),cross_product_winners=choices,
    no_whole_series_selector_over_these_two_existing_actions_can_meet_seen_validation_fullDice_gate=True,
    same_parent_same_budget_only_two_actions=True,new_SR_TTA_local_mixture_or_new_models_not_ruled_out=True,
    source_receipt_key_all_whole_series_selectors_can_meet_fullDice_gate_is_a_feasibility_flag_not_a_universal_claim=True,
    clinical_independent_confirmation=False,medical_arrays_loaded=0,training_updates=0,source_bindings=[entry(p) for p in [Path(__file__),rp,ROOT/'spatial_adaptation_matched_2026_10_08/evaluation_attempt01/receipt.json']],
    resources_before=before,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started,publication_claim_confirmed=False,goal_status='active')
out=HERE/'oracle_terminal_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result);print(json.dumps(result))
