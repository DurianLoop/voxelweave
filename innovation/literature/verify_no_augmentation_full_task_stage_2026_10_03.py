"""Authenticate this completed capability batch, reading provenance and future-only preparation."""
import ast,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'literature/no_augmentation_full_task_stage_manifest_2026-10-03.json'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
    return h.hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    sys.stdout.reconfigure(encoding='utf-8');files=set();errors=[]
    def check(value,message):
        if not value:errors.append(message)
    def include(path):
        p=Path(path);check(p.is_file(),'Missing '+str(p))
        if p.is_file():files.add(p)
    def bind(path,digest):
        include(path);check(Path(path).is_file() and sha(path)==digest,'SHA mismatch '+str(path))
    def complete(path):
        include(path);r=read(path);check(r['complete'] and not r['errors'],'Incomplete '+str(path));return r
    train=ROOT/'experiments/mc_rc_no_augmentation_all_development_cpu'
    t=complete(train/'attempt_01.json');tq=complete(train/'independent_all20000_draws_and_checkpoint_attempt_01.json')
    bind(train/'attempt_01.json',tq['result_sha256']);bind(ROOT/t['checkpoint_file'],t['checkpoint_sha256'])
    check(t['updates_completed']==t['updates_planned']==20000 and len(t['training_draws'])==20000,'20000 real training updates')
    check(tq['no_aug_reference_example_checks']==tq['original_aug_example_checks']==tq['same_rng_end_state_checks']==tq['primitive_metadata_sha_checks']==20000,'All20000 draw checks')
    check(tq['full_patch_source_mapping_checks']==40000 and tq['checkpoint_authenticated'],'All40000 source patches/final checkpoint')
    check(tq['network_forward_calls']==tq['training_updates']==0,'Zero-forward training verifier')
    check(t['device']=='cpu' and not t['gpu_initialized'] and not tq['gpu_initialized'],'Original CPU training contract retained')
    bind(ROOT/'experiments/run_mc_rc_no_augmentation_all_development_cpu.py',t['script_sha256'])
    bind(ROOT/'experiments/verify_mc_rc_no_augmentation_all_development_training_cpu.py',tq['script_sha256'])
    evaluation=ROOT/'experiments/mc_rc_no_augmentation_full_task_evaluation_gpu'
    r=complete(evaluation/'attempt_01.json');q=complete(evaluation/'independent_all37_metrics_and111_planes_attempt_01.json')
    bind(evaluation/'attempt_01.json',q['result_sha256'])
    check(len(r['evaluations'])==len(q['evaluations'])==37 and q['checkpoint_replayed_planes']==111,'All37 predictions/111 replayed planes')
    check(r['device']=='cuda:0' and r['gpu_initialized'] and q['gpu_initialized'],'Authorized GPU evaluations')
    check(q['capability_gate_passed']==r['capability_gate_passed'] and all(r['capability_gate_checks'].values())==r['capability_gate_passed'],'Unchanged independently checked gate')
    check(r['new_training_updates']==q['training_updates']==0,'No evaluator training')
    check(r['checkpoint_sha256']==t['checkpoint_sha256'],'Same final checkpoint')
    bind(ROOT/r['split_file'],r['split_sha256']);bind(ROOT/r['runtime_proof_file'],r['runtime_proof_sha256'])
    bind(ROOT/'experiments/verify_mc_rc_no_augmentation_full_task_gpu.py',q['script_sha256'])
    for e in r['evaluations']:bind(ROOT/e['prediction_file'],e['prediction_file_sha256'])
    spotdir=ROOT/'experiments/mc_rc_no_augmentation_checkpoint_device_spotcheck'
    spot=complete(spotdir/'attempt_01.json')
    check(len(spot['planes'])==6 and spot['label_arrays_read']==spot['training_updates']==0,'Fixed six-plane label-free device check')
    check(spot['cpu_global_forward_calls']==spot['gpu_global_forward_calls']==6,'Both devices actually replayed')
    check(spot['checkpoint_sha256']==t['checkpoint_sha256'],'Spotcheck same trained weights')
    for b in spot['source_bindings']+spot['code_bindings']:bind(ROOT/b['path'],b['sha256'])
    bind(ROOT/spot['protocol_file'],spot['protocol_sha256'])
    bind(ROOT/'experiments/audit_mc_rc_no_augmentation_checkpoint_cpu_gpu_spotcheck.py',spot['script_sha256'])
    partial=ROOT/'experiments/mc_rc_partial_augmentation_development_cpu_preflight'
    p=complete(partial/'attempt_01.json')
    check(len(p['series'])==19 and p['same_rng_end_state_checks']==p['legacy_aug_exact_input_checks']==p['legacy_none_exact_input_checks']==p['frozen_primitive_matches']==608,'All608 prepared draws')
    check(p['partial_arm_reference_input_checks']==p['full_patch_source_mapping_checks']==p['arm_target_identity_checks']==1216,'All1216 partial inputs/source maps')
    check(p['network_forward_calls']==p['training_updates']==0,'Prepared factor arms untrained')
    bind(ROOT/'experiments/prepare_mc_rc_partial_augmentation_development_cpu.py',p['script_sha256'])
    runtime=ROOT/'experiments/mc_rc_authorized_gpu_runtime_preflight'
    g=complete(runtime/'attempt_01.json');bind(ROOT/'experiments/mc_rc_authorized_gpu_adapter.py',g['adapter_sha256'])
    bind(ROOT/'experiments/audit_mc_rc_authorized_gpu_runtime.py',g['script_sha256'])
    check(g['patient_inputs_read']==g['label_inputs_read']==g['training_updates']==0,'Synthetic GPU preflight only')
    check(all(x['max_absolute_error']<=5e-4 and x['max_sigmoid_error']<=5e-5 and x['repeated_gpu_exactly_equal'] for x in g['synthetic_preflight']['comparisons']),'GPU numerical guard')
    for record in (t,tq,r,q,p,g):
        for b in record.get('source_bindings',[])+record.get('code_bindings',[]):bind(ROOT/b['path'],b['sha256'])
        if 'protocol_file' in record:bind(ROOT/record['protocol_file'],record['protocol_sha256'])
        check(not record['confirmation_patients_opened'] and not record['publication_claim_confirmed'] and record['scientific_confirmation_patients']==0,'No independent scientific confirmation')
    bodies=ROOT/'literature/source_cache/no_augmentation_task_fulltexts_2026-10-03'
    reading=read(bodies/'reading_provenance.json');include(bodies/'reading_provenance.json')
    bind(bodies/'attempt_01.json',reading['acquisition_sha256']);bind(ROOT/reading['report'],reading['report_sha256'])
    bind(ROOT/'literature/register_no_augmentation_task_reading_2026_10_03.py',reading['script_sha256'])
    check(reading['new_primary_bodies_read']==2 and reading['actual_body_text_blocks']==185,'Two primary bodies/185 actually read blocks')
    for paper in reading['papers']:
        for prefix in ('raw','block','text'):bind(bodies/paper[prefix+'_file'],paper[prefix+'_sha256'])
        blocks=read(bodies/paper['block_file'])
        check(paper['actual_read_block_ids']==list(range(len(blocks))) and paper['actual_read_blocks']==[dict(index=i,**b) for i,b in enumerate(blocks)],'Exact read block text '+paper['key'])
        check(not paper['visual_figures_reviewed'] and not paper['author_experiments_independently_reproduced'],'Reading boundaries')
    figures=ROOT/'figures/mc_rc_no_augmentation_full_task'
    report=read(figures/'provenance.json');include(figures/'provenance.json')
    for b in report['source_bindings']+report['outputs']:bind(ROOT/b['path'],b['sha256'])
    bind(ROOT/report['report_file'],report['report_sha256'])
    receipt=ROOT/'SESSION_EXECUTION_LEDGER_NO_AUGMENTATION_2026-10-03.json';include(receipt)
    ledger=read(receipt)
    check(all(s['actual_exit_code']==0 for s in ledger['completed_sessions']),'Recorded actual exits')
    failure=ROOT/'experiments/mc_rc_gpu_geometry_intensity_factorial/attempt_01.json'
    include(failure);failed=read(failure)
    check(not failed['complete'] and failed['errors'] and failed['total_updates_completed']==10,'Failed GPU resource attempt retained')
    bind(ROOT/failed['protocol_file'],failed['protocol_sha256'])
    bind(ROOT/'experiments/run_mc_rc_gpu_geometry_intensity_factorial.py',failed['script_sha256'])
    for b in failed['source_bindings']+failed['code_bindings']:bind(ROOT/b['path'],b['sha256'])
    failure2=ROOT/'experiments/mc_rc_gpu_geometry_intensity_factorial_attempt02/attempt_01.json'
    include(failure2);failed2=read(failure2)
    check(not failed2['complete'] and failed2['errors'] and failed2['total_updates_completed']==10,'Second resource failure retained')
    check(failed2['runtime_training_preflight']['projected_all80000_seconds']>3600,'Original resource gate retained')
    bind(ROOT/failed2['protocol_file'],failed2['protocol_sha256'])
    bind(ROOT/'experiments/run_mc_rc_gpu_geometry_intensity_factorial_attempt02.py',failed2['script_sha256'])
    for b in failed2['source_bindings']+failed2['code_bindings']:bind(ROOT/b['path'],b['sha256'])
    for directory in (train,evaluation,partial,runtime,bodies,figures,spotdir):
        for path in directory.rglob('*'):
            if path.is_file():include(path)
    for folder,pattern in ((ROOT,'*NO_AUGMENTATION*.md'),(ROOT,'*PARTIAL_AUGMENTATION*.md'),
        (ROOT/'experiments','*no_augmentation*.py'),(ROOT/'experiments','*partial_augmentation*.py'),
        (ROOT/'literature','*no_augmentation*.py'),(ROOT/'literature','*no_augmentation*.md')):
        for path in folder.glob(pattern):include(path)
    include(ROOT/'README.md');include(ROOT/'EXPERIMENT_QUEUE.md')
    include(ROOT/'experiments/no_augmentation_gpu_evaluation_preparation_2026-10-03.json')
    for name in ('NO_AUGMENTATION_CAPABILITY_DECISION_RULES_2026-10-03.md',
        'GPU_GEOMETRY_INTENSITY_NEXT_PREPARATION_2026-10-03.md',
        'MC_RC_GPU_FACTORIAL_ATTEMPT02_RUNTIME_PROTOCOL_2026-10-03.md',
        'MC_RC_INTENSITY_ONLY_GPU_CAPABILITY_PROTOCOL_2026-10-03.md',
        'experiments/run_mc_rc_gpu_geometry_intensity_factorial_attempt02.py',
        'experiments/run_mc_rc_intensity_only_gpu_capability.py',
        'experiments/mc_rc_full_gpu_training_support.py'):
        include(ROOT/name)
    for p in (ROOT/'literature/source_cache').glob('no_augmentation_*observation*.json'):include(p)
    for p in (ROOT/'literature/source_cache/no_augmentation_entry_snapshot_2026-10-03').rglob('*'):
        if p.is_file():include(p)
    for path in files:
        if path.suffix=='.py':
            try:ast.parse(path.read_text(encoding='utf-8'))
            except SyntaxError as e:errors.append('Syntax '+str(path)+': '+str(e))
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),
        scope='Completed new CPU20k training, GPU37 evaluation/111 implementation replay, two fulltexts, zero-forward future factor preparation.',
        files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)],
        capability_gate_passed=r['capability_gate_passed'],scientific_confirmation_patients=0,publication_claim_confirmed=False,errors=errors)
    OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(files=len(files),errors=errors),ensure_ascii=False));return int(bool(errors))


if __name__=='__main__':raise SystemExit(main())
