"""Audit real frozen metadata and refusal branches; never open medical arrays."""
import ast, copy, ctypes, hashlib, json, shutil, sys, time
from datetime import datetime, timezone
from pathlib import Path
import patient_exposure_registry as core

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/'patient_registry_attempt02'
TABLE=ROOT/'experiments/observed_holdout_feature_table_2026_10_08.json'
CONFIG=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/frozen_config.json'
ROLES=ROOT/'experiments/mc_rc_true_native_reference_2026_10_07.py'

def entry(p):return dict(path=p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def role_ids(tree,name):
    assign=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
    node=assign.value
    assert isinstance(node,ast.SetComp) and len(node.generators)==1
    gen=node.generators[0];assert not gen.ifs and not gen.is_async
    assert isinstance(node.elt,ast.BinOp) and isinstance(node.elt.op,ast.Add)
    assert isinstance(node.elt.left,ast.Constant) and isinstance(node.elt.right,ast.Name)
    assert node.elt.right.id==gen.target.id
    return {node.elt.left.value+x for x in ast.literal_eval(gen.iter)}

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);tick=time.perf_counter()
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=ctypes.c_void_p
    k.SetPriorityClass.argtypes=(ctypes.c_void_p,ctypes.c_uint32)
    assert k.SetPriorityClass(k.GetCurrentProcess(),0x00004000),'Cannot set own below-normal priority'
    read_paths=set();denied=[]
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        p=Path(args[0]).resolve();mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT.parent):
            if p.name.endswith(('.nii','.nii.gz','.npz','.npy','.pt','.zip','.dcm')):
                denied.append(str(p));raise PermissionError('Metadata audit prohibits MRI, GT and weight arrays')
            read_paths.add(p.relative_to(ROOT.parent).as_posix())
    sys.addaudithook(audit)
    table=json.loads(TABLE.read_text(encoding='utf-8'));config=json.loads(CONFIG.read_text(encoding='utf-8'))
    roles=ast.parse(ROLES.read_text(encoding='utf-8'));developers=role_ids(roles,'DEVELOPERS');validators=role_ids(roles,'VALIDATORS')
    assert len(developers)==11 and len(validators)==4 and not developers&validators
    assert developers==set(config['patient_ids'])
    registry=core.build_registry(table,config);folds=core.build_folds(registry,config['patient_ids'])
    assert len(registry['series'])==19 and len(folds)==11
    assert all(not f['task_model_patient_excluded'] and f['pipeline_patient_out'] is False for f in folds)
    assert not validators&set(registry['patient_ids'])
    negative=[]
    def rejects(name,fn):
        try:fn()
        except ValueError as e:negative.append(dict(name=name,rejected=True,reason=str(e)))
        else:raise AssertionError('Not rejected: '+name)
    def changed_fold(name,change):
        f=copy.deepcopy(folds[0]);change(f)
        rejects(name,lambda:core.validate_fold(registry,f,config['patient_ids']))
    changed_fold('incorrect_pipeline_patient_out',lambda f:f.update(pipeline_patient_out=True))
    changed_fold('incorrect_task_exclusion',lambda f:f.update(task_model_patient_excluded=True))
    changed_fold('heldout_patient_in_head_training',lambda f:f['head_training_patients'].append(f['heldout_patient']))
    changed_fold('missing_one_heldout_series',lambda f:f['head_heldout_series'].pop())
    changed_fold('duplicated_heldout_series',lambda f:f['head_heldout_series'].append(copy.deepcopy(f['head_heldout_series'][0])))
    changed_fold('changed_observed_source_sha',lambda f:f['head_heldout_series'][0].update(observed_package_sha256='0'*64))
    def changed_table(name,change):
        t=copy.deepcopy(table);change(t)
        rejects(name,lambda:core.build_registry(t,config))
    changed_table('missing_real_feature_series',lambda t:t['rows'].pop())
    changed_table('duplicate_real_feature_series',lambda t:t['rows'].append(copy.deepcopy(t['rows'][0])))
    changed_table('patient_identifier_as_predictor',lambda t:t['rows'][0]['features'].update(patient_code=1))
    changed_table('nonfinite_real_feature',lambda t:t['rows'][0]['features'].update(heldout_linear_MSE=float('nan')))
    # Reuse the actual unlabeled table as a forbidden adapter input, not invented MRI outcome labels.
    rejects('unqualified_label_bundle_cannot_bypass_task_gates',lambda:core.training_readiness(registry,table))
    ready=core.training_readiness(registry)
    bindings=[entry(p) for p in (Path(__file__),HERE/'patient_exposure_registry.py',HERE/'PROTOCOL.md',TABLE,CONFIG,ROLES)]
    for p in (Path(__file__),HERE/'patient_exposure_registry.py'):
        with (OUT/(p.name+'.source_snapshot')).open('xb') as f:f.write(p.read_bytes())
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=bindings,
        registry=registry,folds=folds,readiness=ready,negative_checks=negative,
        observed_task_training_arms=config['arm_order'],training_config_exposure_applies_to_each_arm=True,
        task_final_checkpoint_bytes_inspected=False,final_training_success_claimed=False,
        task_exposure_evidence='Frozen config patient_ids and complete series metadata, not a loaded final checkpoint',
        unique_patients=11,unique_series=19,head_fold_count=11,
        heldout_series_memberships=sum(len(f['head_heldout_series']) for f in folds),
        training_series_memberships=sum(len(f['head_training_series']) for f in folds),
        entire_pipeline_patient_out_folds=0,all_other_learned_components_exposure_resolved=False,
        real_action_task_labels=0,medical_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,GPU_forwards=0,training_updates=0,head_fits=0,
        own_priority_below_normal=True,workspace_free_bytes=shutil.disk_usage(ROOT).free,
        audit_read_paths=sorted(read_paths),denied_array_reads=denied,
        root_file_hashes=[entry(ROOT.parent/name) for name in ('.gitignore','environment.yml')],
        elapsed_seconds=time.perf_counter()-tick,publication_claim_confirmed=False,goal_status='active')
    assert result['workspace_free_bytes']>=8*1024**3 and result['elapsed_seconds']<=120 and not denied
    assert result['heldout_series_memberships']==19 and result['training_series_memberships']==190
    write(OUT/'receipt.json',result)
    print(json.dumps({k:result[k] for k in ('complete','unique_patients','unique_series','head_fold_count',
        'heldout_series_memberships','training_series_memberships','entire_pipeline_patient_out_folds',
        'real_action_task_labels','elapsed_seconds','workspace_free_bytes')},ensure_ascii=False),flush=True)
    print(json.dumps(dict(negative_checks=len(negative),readiness=ready),ensure_ascii=False),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
