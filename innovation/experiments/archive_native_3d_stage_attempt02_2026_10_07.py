"""New-stage SHA archive with bounded-scope completion audit; no claim-completion assertion."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'literature/native_reference_3d_stage_manifest_attempt02_2026-10-07.json'
RECEIPT=ROOT/'SESSION_ARCHIVE_VERIFICATION_NATIVE_3D_ATTEMPT02_2026-10-07.json'
LEDGER=ROOT/'SESSION_EXECUTION_LEDGER_NATIVE_3D_ATTEMPT02_2026-10-07.json'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write_new(p,value):
    with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not MANIFEST.exists() and not RECEIPT.exists() and not LEDGER.exists()
    dirs=['mc_rc_true_native_reference_2026_10_07','mc_rc_true_native_reference_attempt02_2026_10_07',
          'mc_rc_3d_baseline_inputs_2026_10_07','mc_rc_3d_baseline_inputs_attempt02_2026_10_07',
          'mc_rc_3d_gpu_fit_pilot_2026_10_07_attempt01','mc_rc_3d_real_batch_cpu_2026_10_07',
          'mc_rc_3d_sparse_source_isolation_2026_10_07']
    runs=[dict(command='audit_mc_rc_true_native_reference_2026_10_07.py',tool_exit=1,session_id=None,terminal=True,status='failed_label_memory_bound'),
          dict(command='audit_mc_rc_true_native_reference_attempt02_2026_10_07.py',tool_exit=0,session_id=20517,terminal=True,status='complete'),
          dict(command='verify_mc_rc_true_native_reference_2026_10_07.py',tool_exit=0,session_id=18139,terminal=True,status='complete'),
          dict(command='audit_mc_rc_3d_baseline_inputs_2026_10_07.py',tool_exit=1,session_id=59876,terminal=True,status='failed_label_pixel_center_tie'),
          dict(command='audit_mc_rc_3d_baseline_inputs_attempt02_2026_10_07.py',tool_exit=0,session_id=84139,terminal=True,status='complete'),
          dict(command='run_mc_rc_3d_gpu_fit_pilot_2026_10_07.py --attempt 01',tool_exit=1,script_logic_exit=3,session_id=None,terminal=True,status='resource_deferred_zero_updates'),
          dict(command='audit_mc_rc_3d_real_batch_cpu_2026_10_07.py',tool_exit=0,session_id=31245,terminal=True,status='complete'),
          dict(command='verify_mc_rc_3d_sparse_source_isolation_2026_10_07.py',tool_exit=0,session_id=76606,terminal=True,status='complete')]
    runs.append(dict(command='archive_native_3d_stage_2026_10_07.py',tool_exit=1,session_id=None,terminal=True,status='failed_json_array_binding_traversal'))
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),python='D:/conda/envs/MRI/python.exe -X utf8 -B',
                all_own_runs_terminal_from_observed_tool_exits=True,runs=runs,live_own_runs=[],
                actual_gpu_updates=0,actual_cpu_updates=2,publication_claim_confirmed=False,scientific_confirmation_patients=0,
                latest_totals_only_gpu_observation=dict(free_mib=1394,total_mib=24455,utilization_percent=46,
                    query='nvidia-smi --query-gpu=index,name,memory.total,memory.free,utilization.gpu --format=csv,noheader,nounits',pids_requested=False),
                next_gpu_attempt='02 only after a fresh >=8GB free observation; do not rerun prior completed/failed stages',
                before_stage_goal_turn_classification='progress',current_stage_goal_turn_classification='progress')
    write_new(LEDGER,ledger)
    stage=set(ROOT.glob('*2026-10-07.md'))
    stage.update((ROOT/'experiments').glob('*2026_10_07.py'))
    stage.add(ROOT/'literature/extract_strong_task_baseline_html_2026_10_07.py')
    stage.add(ROOT/'literature/2026-10-07_strong_task_baseline_fulltext_reading.md')
    stage.add(LEDGER)
    stage.add(ROOT/'SESSION_EXECUTION_LEDGER_NATIVE_3D_2026-10-07.json')
    stage.add(ROOT/'SESSION_ARCHIVE_FIRST_ATTEMPT_FAILURE_2026-10-07.json')
    stage.update((ROOT/'literature/source_cache/strong_task_baseline_2026-10-07').glob('*'))
    for dirname in dirs:stage.update((ROOT/'experiments'/dirname).glob('*'))
    assert all(p.is_file() and p.is_relative_to(ROOT) for p in stage)
    assert sum(p.stat().st_size for p in stage)<250_000_000
    evidence=set(stage)
    for p in stage:
        if p.suffix=='.json':
            obj=read(p)
            if not isinstance(obj,dict): continue
            for key in ('source_bindings','code_bindings'):
                for binding in obj.get(key,[]):
                    dependency=ROOT/binding['path'];assert sha(dependency)==binding['sha256'];evidence.add(dependency)
            script=obj.get('script_sha256')
            if script:
                assert any(sha(s)==script for s in stage if s.suffix=='.py'), 'A result script SHA has no archived source'
    for name in ('mc_rc_current_development_input_preparation','mc_rc_validation_task_case_preparation'):
        p=ROOT/'experiments'/name/'attempt_01.json';prep=read(p);evidence.add(p)
        for case in prep['cases']:
            for prefix in ('header','mr_zip','label'):
                dependency=ROOT/case[prefix+'_file'];assert sha(dependency)==case[prefix+'_sha256'];evidence.add(dependency)
    for name in ('mc_rc_development_training_input_cpu','mc_rc_validation_task_input_cpu'):
        p=ROOT/'experiments'/name/'attempt_01.json';evidence.add(p)
        for row in read(p)['series']:
            dependency=ROOT/row['observed_package'];assert sha(dependency)==row['observed_package_sha256'];evidence.add(dependency)
    native=read(ROOT/'experiments/mc_rc_true_native_reference_attempt02_2026_10_07/attempt_01.json')
    nativeproof=read(ROOT/'experiments/mc_rc_true_native_reference_attempt02_2026_10_07/independent_all28_pixels_and_labels_2026_10_07.json')
    grid=read(ROOT/'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json')
    batch=read(ROOT/'experiments/mc_rc_3d_real_batch_cpu_2026_10_07/attempt_01.json')
    sparse=read(ROOT/'experiments/mc_rc_3d_sparse_source_isolation_2026_10_07/attempt_01.json')
    gpu=read(ROOT/'experiments/mc_rc_3d_gpu_fit_pilot_2026_10_07_attempt01/attempt_01.json')
    for obj in (native,nativeproof,grid,batch,sparse):assert obj['complete'] and not obj['errors']
    assert nativeproof['result_sha256']==sha(ROOT/'experiments/mc_rc_true_native_reference_attempt02_2026_10_07/attempt_01.json')
    assert nativeproof['raw_pixels_checked']==nativeproof['label_voxels_replayed']==461967360
    assert nativeproof['actual_native_planes_checked']==1993
    assert len(native['series'])==len(grid['series'])==len(sparse['series'])==28
    assert batch['actual_cpu_updates']==2 and batch['actual_gpu_updates']==0 and not batch['cuda_initialized']
    assert gpu['status']=='resource_deferred' and gpu['total_updates_completed']==0 and not gpu['cuda_initialized']
    failed=[read(ROOT/'experiments'/dirname/'attempt_01.json') for dirname in (dirs[0],dirs[2])]
    assert all(not f['complete'] and f['errors'] for f in failed)
    links=[]
    for p in stage:
        if p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                target=target.strip('<>')
                if re.match(r'https?://|app://',target):continue
                target=target.split('#',1)[0];resolved=(p.parent/target).resolve()
                assert resolved.is_file(), f'Broken stage document link: {p.name}: {target}'
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=resolved.relative_to(ROOT).as_posix()))
                evidence.add(resolved)
    def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
                  stage_files=[entry(p) for p in sorted(stage)],evidence_files=[entry(p) for p in sorted(evidence)],local_links=links,
                  scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active',
                  scientific_scope='Native/reference and implementation eligibility, not trained task competence or reconstruction claim')
    write_new(MANIFEST,manifest)
    reopened=read(MANIFEST)
    for group in ('stage_files','evidence_files'):
        for v in reopened[group]:assert sha(ROOT/v['path'])==v['sha256']
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest_file=MANIFEST.relative_to(ROOT).as_posix(),
                 manifest_sha256=sha(MANIFEST),all_manifest_files_rehashed=True,stage_files=len(stage),evidence_files=len(evidence),
                 local_links_verified=len(links),stage_saved_bytes=sum(p.stat().st_size for p in stage),
                 native_source_certificate_complete=True,physical_input_certificate_complete=True,sparse_isolation_complete=True,
                 actual_cpu_updates=2,actual_gpu_updates=0,gpu_fit_completed=False,own_live_runs=[],
                 original_capability_gate_changed=False,confirmation_patients_opened=False,scientific_confirmation_patients=0,
                 publication_claim_confirmed=False,goal_status='active',user_processes_enumerated_or_modified=False)
    write_new(RECEIPT,receipt);print(json.dumps(receipt,ensure_ascii=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
