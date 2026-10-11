"""Exact whole-series oracle upper bound for two existing observed-input pipelines, metadata only."""
import sys,time,json,itertools,collections
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,read,entry,bind,dump,sha
NAMES=['raw_pchip_intensity','raw_pchip_spatial']
def dice(m):
    tp,fp,fn=map(int,(m['tp'],m['fp'],m['fn']));assert tp+fn>0
    return F(2*tp,2*tp+fp+fn)
def recall(m):return F(int(m['tp']),int(m['tp'])+int(m['fn']))
def absrve(m):return F(abs(int(m['fp'])-int(m['fn'])),int(m['tp'])+int(m['fn']))
def pack(x):return dict(numerator=x.numerator,denominator=x.denominator,value=float(x))
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=resource_guard()
    assert before['workspace_free_bytes']-18_800_000>=8_000_000_000
    out=HERE/'existing_action_oracle_attempt01';out.mkdir(exist_ok=False)
    sources=[Path(__file__),HERE/'PROTOCOL.md'];cohorts=[]
    prior=ROOT/'acquisition_action_generalization_author_2026_10_09/APPEND_INDEX.json';pv=read(prior)
    assert sha(prior)=='8cfc6bc2738b05f1a530ea42af3f502c2ea9d100a54776d53d03b6a864332f52' and pv['cumulative_frozen_evidence_files']==7180
    frozen={}
    for b in pv['prior_chain']+[entry(prior)]:
        q=read(bind(b));frozen.update({v['path']:v for v in q.get('evidence_files',q.get('new_evidence_files',[]))})
    assert len(frozen)==7180;sources.append(prior)
    for role,rel,expected_patients,expected_series in [
        ('seen_validation','spatial_adaptation_matched_2026_10_08/evaluation_attempt01/receipt.json',4,9),
        ('training_development','development_capacity_after_matched_2026_10_09/evaluation_attempt01/receipt.json',11,19)]:
        path=bind(frozen[rel]);r=read(path);assert r['complete'] and not r['errors'];sources.append(path)
        arms={a['name']:a for a in r['arms'] if a['name'] in NAMES};assert set(arms)==set(NAMES)
        views=[{s['uid']:s for s in arms[n]['series']} for n in NAMES];assert set(views[0])==set(views[1])
        uids=sorted(views[0]);assert len(uids)==expected_series
        patients=sorted({views[0][u]['patient'] for u in uids});assert len(patients)==expected_patients
        members={p:[i for i,u in enumerate(uids) if views[0][u]['patient']==p] for p in patients}
        metrics=[]
        for u in uids:
            records=[]
            assert views[0][u]['patient']==views[1][u]['patient'] and views[0][u]['label_sha256']==views[1][u]['label_sha256']
            for view in views:
                s=view[u];assert s['role'] in (['validation'] if role=='seen_validation' else ['development'])
                f=s['metrics']['full'];m=s['metrics']['missing']
                for a in [f,m]:
                    assert all(isinstance(a[k],int) and a[k]>=0 for k in ['tn','tp','fp','fn'])
                    assert abs(float(dice(a))-a['dice'])<3e-15 and abs(float(recall(a))-a['recall'])<3e-15
                    assert abs(float(absrve(a))-a['absRVE'])<3e-15
                records.append(dict(full_dice=dice(f),missing_dice=dice(m),full_recall=recall(f),full_absRVE=absrve(f),zeroTP=int(f['tp'])==0))
            metrics.append(records)
        def score(policy):
            selected=[metrics[i][a] for i,a in enumerate(policy)];patient_values=[]
            for p in patients:
                patient_values.append({k:sum((selected[i][k] for i in members[p]),F(0))/len(members[p]) for k in ['full_dice','missing_dice','full_recall','full_absRVE']})
            means={k:sum((v[k] for v in patient_values),F(0))/len(patient_values) for k in ['full_dice','missing_dice','full_recall','full_absRVE']}
            gates=dict(fullDice=means['full_dice']>=F(7,10),missingDice=means['missing_dice']>=F(13,20),fullrecall=means['full_recall']>=F(7,10),
                fullabsRVE=means['full_absRVE']<=F(1,2),all_patient_full_missing_positive=all(v['full_dice']>0 and v['missing_dice']>0 for v in patient_values),
                no_series_zeroTP=not any(v['zeroTP'] for v in selected))
            return dict(policy=list(policy),means={k:pack(v) for k,v in means.items()},gates=gates,all_six_gates_pass=all(gates.values()))
        fixed=[score([i]*len(uids)) for i in range(2)]
        aggregate_key='validation_aggregate' if role=='seen_validation' else 'development_aggregate'
        for i,n in enumerate(NAMES):
            original=arms[n][aggregate_key]['patient_first_means']
            assert abs(fixed[i]['means']['full_dice']['value']-original['full']['dice'])<3e-15
            assert abs(fixed[i]['means']['missing_dice']['value']-original['missing']['dice'])<3e-15
        # This independently allows each series its own GT-chosen action; an optimistic necessary upper bound.
        max_policy=[max(range(2),key=lambda a:metrics[i][a]['full_dice']) for i in range(len(uids))]
        analytic=score(max_policy);patient_enum=None;series_enum=None
        if role=='seen_validation':
            plans=[score([actions[patients.index(views[0][u]['patient'])] for u in uids]) for actions in itertools.product(range(2),repeat=len(patients))]
            patient_enum=dict(policies_enumerated=len(plans),all_six_gate_passing=sum(p['all_six_gates_pass'] for p in plans),best_full_dice=max(plans,key=lambda p:p['means']['full_dice']['value']))
            seriesplans=[score(actions) for actions in itertools.product(range(2),repeat=len(uids))]
            series_enum=dict(policies_enumerated=len(seriesplans),all_six_gate_passing=sum(p['all_six_gates_pass'] for p in seriesplans),best_full_dice=max(seriesplans,key=lambda p:p['means']['full_dice']['value']))
            assert series_enum['best_full_dice']['means']['full_dice']==analytic['means']['full_dice']
        cohorts.append(dict(role=role,patients=patients,series=[dict(uid=u,patient=views[0][u]['patient']) for u in uids],fixed=fixed,
            optimistic_series_fullDice_upper_bound=analytic,patient_consistent_enumeration=patient_enum,per_series_enumeration=series_enum,
            all_whole_series_selectors_can_meet_fullDice_gate=analytic['gates']['fullDice']))
    result=dict(complete=True,errors=[],actions=NAMES,cohorts=cohorts,all_costs_optimistically_zero_for_bound=True,
        controller_trained=False,new_SR_or_local_fusion_actions_bounded=False,independent_medical_confirmation=False,
        MRI_arrays_loaded=0,GT_arrays_loaded=0,probability_arrays_loaded=0,model_arrays_loaded=0,training_updates=0,
        validation_result_JSON_read=True,validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        source_bindings=[entry(p) for p in sources],resources_before=before,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started,
        publication_claim_confirmed=False,goal_status='active')
    assert result['elapsed_seconds']<120 and sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    dump(out/'receipt.json',result)
    print(json.dumps(dict(complete=True,cohorts=[dict(role=c['role'],optimistic_fullDice=c['optimistic_series_fullDice_upper_bound']['means']['full_dice'],fullDice_gate=c['optimistic_series_fullDice_upper_bound']['gates']['fullDice'],
        enumerated_gate_passers=(c['per_series_enumeration'] or {}).get('all_six_gate_passing')) for c in cohorts],elapsed_seconds=result['elapsed_seconds'])),flush=True)
if __name__=='__main__':main()
