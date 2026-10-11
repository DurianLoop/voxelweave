"""Fixed synthetic qualification for patient-level known-method strong controls."""
import copy,hashlib,json,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/patient_risk_cost_baseline_executor_qualification_2026_10_07'
PROTOCOL=ROOT/'PATIENT_RISK_COST_BASELINE_EXECUTOR_PROTOCOL_2026-10-07.md'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def fixture(role):
    ids=[f'SYNTHETIC_{role.upper()}_{i:03d}' for i in range(64)]
    binary_mid=6 if role=='optimization' else 8
    return dict(role=role,patient_ids=ids,policy_ids=['BASE','MID','CHEAP','DOMINATED'],
        risks=dict(harm=[[0]*64,[int(i<binary_mid) for i in range(64)],[int(i<24) for i in range(64)],[0]*64],
            bounded_loss=[['0']*64,['0.12']*64,['0.4']*64,['0']*64]),
        objectives=dict(total_cost=[['10']*64,['5']*64,['1']*64,['11']*64]))
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);at=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        synthetic_only=True,MRI_data_reads=0,GT_reads=0,neural_modules_imported=False,model_forwards=0,
        training_updates=0,GPU_forwards=0,actual_MRI_risk_certificates_issued=0,publication_claim_confirmed=False)
    denied=[];reads=set()
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        try:p=Path(args[0]).resolve()
        except (OSError,ValueError,TypeError):return
        mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT.parent):
            rel=p.relative_to(ROOT.parent).as_posix()
            if p.name.endswith(('.nii','.nii.gz','.npz','.npy','.pt','.zip')) or '/data/' in '/'+rel:
                denied.append(rel);raise PermissionError('Synthetic risk selector denies MRI/weight IO')
            reads.add(rel)
    sys.addaudithook(audit)
    try:
        import patient_risk_cost_baseline_executor_2026_10_07 as w
        from mc_rc_reference_resources_2026_10_07 import resource_guard
        r['resources_before']=resource_guard()
        paths=[Path(__file__),ROOT/'experiments/patient_risk_cost_baseline_executor_2026_10_07.py',PROTOCOL,
            ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py']
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths]
        for p in paths:(OUT/(p.name+'.source_snapshot')).write_bytes(p.read_bytes())
        opt,test=fixture('optimization'),fixture('testing');before=digest((opt,test))
        specs=dict(harm=dict(alpha='0.3',mode='binary'),bounded_loss=dict(alpha='0.3',mode='bounded'))
        r.update(fixture_optimization=opt,fixture_testing=test,risk_specs=specs,delta='0.1',selections=[])
        for method in ('bonferroni','split_fst','pareto'):
            result=w.select(opt,test,specs,'0.1',method)
            assert result['selected_primary_policy_id']=='MID'
            assert 'CHEAP' not in result['certified_policy_ids'] and {'BASE','MID'}<=set(result['certified_policy_ids'])
            if method=='pareto':assert result['frontier_policy_ids']==['BASE','MID','CHEAP']
            r['selections'].append(result)
        strict=w.select(opt,test,specs,'0.1','pareto',dominance_rule='all_strict')
        assert 'DOMINATED' in strict['frontier_policy_ids'];r['all_strict_variant']=strict
        blocked=copy.deepcopy(test);blocked['risks']['harm'][0]=[1]*64
        halt=w.select(opt,blocked,specs,'0.1','split_fst')
        assert halt['stopped_at']=='BASE' and halt['actual_tested_policy_ids']==['BASE'] and not halt['certified_policy_ids']
        assert halt['selected_primary_policy_id'] is None
        r['halt_fixture_testing']=blocked;r['halt_selection']=halt
        oneopt=dict(role='optimization',patient_ids=['SYNTHETIC_TIE_OPT'],policy_ids=['ONE'],risks=dict(harm=[['0']]),objectives=dict(total_cost=[['1']]))
        onetest=copy.deepcopy(oneopt);onetest.update(role='testing',patient_ids=['SYNTHETIC_TIE_TEST'])
        onespec=dict(harm=dict(alpha='0.9',mode='binary'))
        r['tie_checks']={method:w.select(oneopt,onetest,onespec,'0.1',method) for method in ('bonferroni','split_fst')}
        assert r['tie_checks']['bonferroni']['certified_policy_ids']==['ONE']
        assert not r['tie_checks']['split_fst']['certified_policy_ids']
        r.update(tie_fixture_optimization=oneopt,tie_fixture_testing=onetest,tie_specs=onespec)
        maxopt=copy.deepcopy(oneopt);maxtest=copy.deepcopy(onetest)
        maxopt['risks']['other']=[['0']];maxtest['risks']['other']=[['1']]
        maxspec=dict(onespec,other=dict(alpha='0.9',mode='binary'))
        maximum=w.select(maxopt,maxtest,maxspec,'0.2','split_fst')
        assert maximum['testing_risks'][0]['combined_pvalue']=='1' and not maximum['certified_policy_ids']
        r.update(max_risk_fixture_optimization=maxopt,max_risk_fixture_testing=maxtest,max_risk_specs=maxspec,max_risk_selection=maximum)
        multiopt=copy.deepcopy(opt);multitest=copy.deepcopy(test)
        for panel in (multiopt,multitest):panel['objectives']['auxiliary_loss']=[['0']*64,['0.5']*64,['1']*64,['0']*64]
        multi=w.select(multiopt,multitest,specs,'0.1','pareto')
        assert set(multi['selected_policy_ids'])=={'BASE','MID'}
        r.update(multi_objective_fixture_optimization=multiopt,multi_objective_fixture_testing=multitest,multi_objective_selection=multi)
        invalid=[]
        def reject(name,callback):
            try:callback()
            except ValueError as e:invalid.append(dict(name=name,rejected=True,error=str(e)))
            else:raise AssertionError('Invalid input accepted: '+name)
        overlap=copy.deepcopy(test);overlap['patient_ids'][0]=opt['patient_ids'][0]
        reject('optimization_testing_overlap',lambda:w.select(opt,overlap,specs,'0.1','pareto'))
        reject('seen_or_confirmation_testing_ID',lambda:w.select(opt,test,specs,'0.1','pareto',[test['patient_ids'][0]]))
        short=copy.deepcopy(test);short['risks']['harm'][0].pop()
        reject('missing_patient_outcome',lambda:w.select(opt,short,specs,'0.1','pareto'))
        duplicate=copy.deepcopy(test);duplicate['patient_ids'][1]=duplicate['patient_ids'][0]
        reject('duplicate_patient_ID',lambda:w.select(opt,duplicate,specs,'0.1','pareto'))
        reject('nonbinary_loss',lambda:w.pvalue(['0.12'],'0.3','binary'))
        reject('unbounded_loss',lambda:w.pvalue(['1.1'],'0.3','bounded'))
        reject('nonfinite_loss',lambda:w.pvalue(['NaN'],'0.3','bounded'))
        reject('invalid_alpha',lambda:w.pvalue(['0'],'1','bounded'))
        reject('invalid_delta',lambda:w.select(opt,test,specs,'0','pareto'))
        collision=copy.deepcopy(test);collision['objectives']['harm']=[['1']*64]*4
        reject('risk_objective_name_collision',lambda:w.select(opt,collision,specs,'0.1','pareto'))
        negative=copy.deepcopy(test);negative['objectives']['total_cost'][0][0]='-1'
        reject('negative_total_cost',lambda:w.select(opt,negative,specs,'0.1','pareto'))
        permuted=copy.deepcopy(test);permuted['policy_ids'].reverse()
        reject('candidate_order_changed',lambda:w.select(opt,permuted,specs,'0.1','pareto'))
        assert digest((opt,test))==before and 'torch' not in sys.modules and not denied
        r.update(complete=True,invalid_inputs_rejected=invalid,all_invalid_inputs_rejected=True,input_panels_not_mutated=True,
            selected_expected_MID_all_three_methods=True,full_policy_panel_coverage=True,patient_levels_not_tiles=True,
            all_strict_and_weak_variant_difference_recorded=True,first_nonrejection_halts=True,
            empty_certified_set_does_not_infer_fallback=True,multiple_risks_use_max=True,
            multi_free_objective_front_preserved=True,tie_boundary_conventions_verified=True,
            resources_after=resource_guard(),synthetic_patient_IDs_not_actual_MRI_calibration=True)
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r.update(finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-at,
        io_audit=dict(workspace_read_paths=sorted(reads),denied_read_attempts=denied))
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','selected_expected_MID_all_three_methods','elapsed_seconds')}))
    return 0 if r['complete'] and not r['errors'] else 1
if __name__=='__main__':raise SystemExit(main())
