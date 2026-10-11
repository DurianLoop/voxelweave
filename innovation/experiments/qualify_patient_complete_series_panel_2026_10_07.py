"""Fixed unequal-series synthetic cohort, with complete cost and negative coverage checks."""
import copy,hashlib,json,sys,time,traceback
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/patient_complete_series_panel_qualification_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);at=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        synthetic_only=True,MRI_data_reads=0,GT_reads=0,model_forwards=0,GPU_forwards=0,training_updates=0,
        actual_MRI_risk_certificates_issued=0,publication_claim_confirmed=False)
    try:
        import patient_complete_series_panel_2026_10_07 as w
        from patient_risk_cost_baseline_executor_2026_10_07 import validate_panel
        from mc_rc_reference_resources_2026_10_07 import resource_guard
        r['resources_before']=resource_guard()
        sources=[Path(__file__),ROOT/'experiments/patient_complete_series_panel_2026_10_07.py',
            ROOT/'experiments/patient_risk_cost_baseline_executor_2026_10_07.py',ROOT/'PATIENT_COMPLETE_SERIES_PANEL_PROTOCOL_2026-10-07.md']
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources]
        for p in sources:(OUT/(p.name+'.source_snapshot')).write_bytes(p.read_bytes())
        expected={'SYNTHETIC_A':['SYNTHETIC_A1','SYNTHETIC_A2'],'SYNTHETIC_B':['SYNTHETIC_B1']};policies=['BASE','MID']
        metrics={'BASE':[('0.9','0.8','0.2'),('0.7','0.6','0.4'),('0.2','0.2','0.8')],
                 'MID':[('0.8','0.7','0.2'),('0.7','0.6','0.6'),('0.4','0.5','0.3')]}
        records=[];shared=[]
        for policy in policies:
            for (patient,uid),v in zip([(p,u) for p in expected for u in expected[p]],metrics[policy]):
                costs={name:'0' for name in w.COST_PHASES};costs['inference']='10' if policy=='BASE' else '3'
                records.append(dict(patient_id=patient,uid=uid,policy_id=policy,full_fov=True,label_used_for_inference=False,
                    full_dice=v[0],full_recall=v[1],full_absRVE=v[2],cost_components=costs))
            for patient in expected:
                costs={name:'0' for name in w.COST_PHASES};costs['feature']='1' if policy=='MID' else '0'
                shared.append(dict(patient_id=patient,policy_id=policy,cost_components=costs))
        r.update(expected_series=expected,policy_ids=policies,baseline_id='BASE',input_records=records,shared_costs=shared,
            role='optimization',epsilon='0.04',rve_tau='0.5')
        before=json.dumps((records,shared,expected),sort_keys=True)
        def run(rr=records,ee=expected,ss=shared):return w.complete_panel(rr,ee,policies,'BASE',ss,'optimization','0.04','0.5')
        panel=run();validate_panel(panel)
        assert panel['risks']['dice_loss']==[['0.2','0.8'],['0.25','0.6']]
        assert panel['risks']['positive_dice_drop']==[['0','0'],['0.05','0']]
        assert panel['risks']['harm_event']==[['0','0'],['1','0']]
        assert panel['risks']['recall_loss']==[['0.3','0.8'],['0.35','0.5']]
        assert panel['risks']['rve_tail']==[['0','1'],['0','0']]
        assert panel['objectives']['total_cost']==[['20','10'],['7','4']]
        r['panel']=panel;r['invalid_inputs_rejected']=[]
        def reject(name,callback):
            try:callback()
            except ValueError as e:r['invalid_inputs_rejected'].append(dict(name=name,rejected=True,error=str(e)))
            else:raise AssertionError('Invalid input accepted: '+name)
        reject('missing_complete_series',lambda:run(records[:-1]))
        reject('duplicate_series_record',lambda:run(records+[copy.deepcopy(records[0])]))
        changed=copy.deepcopy(records);changed[0]['uid']='SYNTHETIC_UNKNOWN'
        reject('extra_UID',lambda:run(changed))
        cropped=copy.deepcopy(records);cropped[0]['full_fov']=False
        reject('ROI_instead_of_full_FOV',lambda:run(cropped))
        label=copy.deepcopy(records);label[0]['label_used_for_inference']=True
        reject('GT_in_inference',lambda:run(label))
        partialcost=copy.deepcopy(records);del partialcost[0]['cost_components']['candidate_exploration']
        reject('missing_exploration_cost',lambda:run(partialcost))
        negative=copy.deepcopy(shared);negative[0]['cost_components']['feature']='-1'
        reject('negative_shared_cost',lambda:run(ss=negative))
        reject('missing_shared_cost',lambda:run(ss=shared[:-1]))
        reject('duplicate_shared_cost',lambda:run(ss=shared+[copy.deepcopy(shared[0])]))
        badrange=copy.deepcopy(records);badrange[0]['full_dice']='1.1'
        reject('Dice_out_of_range',lambda:run(badrange))
        badnumber=copy.deepcopy(records);badnumber[0]['full_dice']='NaN'
        reject('nonfinite_metric',lambda:run(badnumber))
        duid=copy.deepcopy(expected);duid['SYNTHETIC_B']=['SYNTHETIC_A1']
        reject('same_UID_in_two_patients',lambda:run(ee=duid))
        assert before==json.dumps((records,shared,expected),sort_keys=True) and 'torch' not in sys.modules
        r.update(complete=True,input_records_not_mutated=True,all12_invalid_inputs_rejected=True,
            patient_equal_mean_MID_Dice='0.575',series_weighted_mean_MID_Dice_exact=dict(numerator=19,denominator=30),
            patient_equal_mean_BASE_Dice='0.5',series_weighted_mean_BASE_Dice='0.6',
            unequal_series_patient_weighting_verified=True,total_costs_sum_all_series_and_shared_once=True,
            full_grid_coverage_verified=True,serialized_panel_accepted_by_executor=True,resources_after=resource_guard())
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-at
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','unequal_series_patient_weighting_verified','elapsed_seconds')}))
    return 0 if r['complete'] and not r['errors'] else 1
if __name__=='__main__':raise SystemExit(main())
