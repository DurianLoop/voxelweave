"""Freeze full development metadata and pending denominators; never read image/GT arrays."""
import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
resource_guard();out=HERE/'gin19_metadata_preparation_attempt01';out.mkdir(exist_ok=False)
cp=ROOT/'development_optimizer_coverage_2026_10_09/coverage_attempt01/frozen_config.json'
ap=ROOT/'development_optimizer_coverage_2026_10_09/terminal_audit_attempt01/receipt.json'
cfg=read(cp);audit=read(ap)
assert audit['complete'] and not audit['errors'] and audit['all19_series11_patients_and114_branch_denominators_verified']
assert len(cfg['cases'])==19 and len({v['patient'] for v in cfg['cases']})==11 and cfg['kinds']==['native_reference','raw_pchip']
cases=[]
for ci,v in enumerate(cfg['cases']):
    assert v['case']==ci and len(v['scheduled_steps'])==len(v['original_fields'])==2
    for s,fields in zip(v['scheduled_steps'],v['original_fields']):
        assert len(fields)==2
        assert all(f['step']==s and f['uid']==v['uid'] and f['patient']==v['patient'] for f in fields)
        assert fields[0]['mother_label_sha256']==fields[1]['mother_label_sha256']
    cases.append(dict(case=ci,patient=v['patient'],uid=v['uid'],scheduled_steps=v['scheduled_steps'],
                      original_fields=v['original_fields'],
                      three_view_parameter_seeds=[[480000+ci*100+step*10+view for view in range(3)] for step in range(2)]))
manifest=dict(complete=True,errors=[],preparation_only=True,execution_ready=False,
              implementation_status='protocol_and_metadata_only_independent_CPU_gradient_runner_not_implemented',
              kinds=cfg['kinds'],cases=cases,unique_development_patients=11,unique_development_series=19,
              prospective_case_kind_branches=38,prospective_GPU_optimizer_updates=76,
              prospective_GPU_whole_model_forwards=228,prospective_CPU_reference_whole_model_forwards=228,
              prospective_patch_label_checks=152,actual_GPU_optimizer_updates=0,
              MRI_arrays_loaded=0,GT_arrays_loaded=0,parent_model_arrays_loaded=0,
              cold_initial_seed=20261009,patch=[64,128,128],batch_size=2,views=3,
              qualification_only_lambda=.1,probability_gradient_parameter_optimizer_gate=3e-6,
              coordinate_gate=3e-12,binary_gate=0,independent_CPU_FP32_reference_required=True,
              six_medical_gates_required=True,confirmation_patients_opened=False,lockedIXI_opened=False,
              publication_claim_confirmed=False,goal_status='active',
              source_bindings=[entry(p) for p in (Path(__file__),cp,ap,HERE/'GIN_19SERIES_PENDING_QUALIFICATION_ROUND48.md',
                                HERE/'gin_reference_adapter_v1.py',HERE/'three_view_offload_terminal_audit_attempt01/receipt.json')])
dump(out/'manifest.json',manifest)
print(json.dumps({k:manifest[k] for k in ('complete','preparation_only','execution_ready','unique_development_patients',
                   'unique_development_series','prospective_GPU_optimizer_updates','actual_GPU_optimizer_updates')}))
