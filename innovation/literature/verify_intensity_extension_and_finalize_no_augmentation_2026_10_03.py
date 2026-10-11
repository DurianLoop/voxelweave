"""Keep first receipt; authenticate completed intensity extension and save final manifest."""
import ast,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SESSION_ARCHIVE_FINAL_VERIFICATION_NO_AUGMENTATION_2026-10-03.json'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as s:
        for c in iter(lambda:s.read(1048576),b''):h.update(c)
    return h.hexdigest()


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not OUT.exists()
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],checks=[],
        original_pre_extension_receipt='SESSION_ARCHIVE_VERIFICATION_NO_AUGMENTATION_2026-10-03.json',
        scope='Completed40k capability updates,74 complete evaluations,222 implementation replay, two retained resource failures, all public dialogue and source/reading provenance. No publication claim.')
    def save():OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    import verify_no_augmentation_full_task_stage_2026_10_03 as stage
    # Preserve the first136-file manifest/receipt rather than overwriting it.
    final_manifest=ROOT/'literature/no_augmentation_full_task_final_manifest_2026-10-03.json'
    stage.OUT=final_manifest;code=stage.main()
    receipt['checks'].append(dict(name='original_core_and_preparation_recheck',exit_code=code));save()
    if code:receipt['errors'].append('Original core recheck failed');save();return code
    manifest=read(final_manifest);files={ROOT/f['path'] for f in manifest['files']};errors=[]
    def check(v,text):
        if not v:errors.append(text)
    def bind(path,digest):
        p=Path(path);files.add(p);check(p.is_file() and sha(p)==digest,'SHA mismatch '+str(p))
    train=ROOT/'experiments/mc_rc_intensity_only_gpu_capability';evaluation=ROOT/'experiments/mc_rc_intensity_only_full_task_evaluation_gpu'
    t=read(train/'attempt_01.json');tq=read(train/'independent_all20000_draws_and_checkpoint_attempt_01.json')
    r=read(evaluation/'attempt_01.json');q=read(evaluation/'independent_all37_metrics_and111_planes_attempt_01.json')
    check(all(v['complete'] and not v['errors'] for v in (t,tq,r,q)),'Intensity extension complete')
    bind(train/'attempt_01.json',tq['result_sha256']);bind(evaluation/'attempt_01.json',q['result_sha256'])
    check(t['arm_order']==['intensity_only'] and t['total_updates_completed']==20000,'Single20k, no full80k claim')
    check(tq['intensity_reference_example_checks']==tq['original_aug_example_checks']==tq['same_rng_end_state_checks']==20000 and tq['full_patch_source_mapping_checks']==40000,'New all20000 reference/source checks')
    check(tq['checkpoint_authenticated'] and tq['network_forward_calls']==tq['training_updates']==0,'Authenticated terminal weights without neural forwards')
    check(len(r['evaluations'])==len(q['evaluations'])==37 and q['checkpoint_replayed_planes']==111,'New37/111 checks')
    check(q['capability_gate_passed']==r['capability_gate_passed'] and all(r['capability_gate_checks'].values())==r['capability_gate_passed'],'Unchanged gate')
    for v in (t,tq,r,q):
        for b in v.get('source_bindings',[])+v.get('code_bindings',[]):bind(ROOT/b['path'],b['sha256'])
        if 'protocol_file' in v:bind(ROOT/v['protocol_file'],v['protocol_sha256'])
        check(not v['confirmation_patients_opened'] and v['scientific_confirmation_patients']==0 and not v['publication_claim_confirmed'],'No scientific confirmation')
    bind(ROOT/'experiments/run_mc_rc_intensity_only_gpu_capability.py',t['script_sha256'])
    bind(ROOT/'experiments/verify_mc_rc_intensity_only_gpu_training_cpu.py',tq['script_sha256'])
    bind(ROOT/'experiments/verify_mc_rc_intensity_only_full_task_gpu.py',q['script_sha256'])
    arm=t['arms'][0];bind(ROOT/arm['checkpoint_file'],arm['checkpoint_sha256'])
    for e in r['evaluations']:bind(ROOT/e['prediction_file'],e['prediction_file_sha256'])
    bind(ROOT/r['split_file'],r['split_sha256']);bind(ROOT/r['runtime_proof_file'],r['runtime_proof_sha256'])
    figdir=ROOT/'figures/mc_rc_intensity_only_full_task';plot=read(figdir/'provenance.json')
    bind(ROOT/plot['report_file'],plot['report_sha256'])
    bind(ROOT/'experiments/report_mc_rc_intensity_only_full_task_2026_10_03.py',plot['script_sha256'])
    for b in plot['source_bindings']+plot['outputs']:bind(ROOT/b['path'],b['sha256'])
    for directory in (train,evaluation,figdir):
        files.update(p for p in directory.rglob('*') if p.is_file())
    files.update((ROOT/'experiments').glob('*intensity_only*.py'))
    files.update(ROOT.glob('*INTENSITY*.md'))
    for name in ('SESSION_EXECUTION_LEDGER_INTENSITY_EXTENSION_2026-10-03.json',
        'SESSION_FINAL_RECEIPT_NO_AUGMENTATION_2026-10-03.md'):
        path=ROOT/name;check(path.is_file(),'Missing '+name);files.add(path)
    for p in files:
        if p.suffix=='.py':
            try:ast.parse(p.read_text(encoding='utf-8'))
            except SyntaxError as e:errors.append('Syntax '+str(p)+': '+str(e))
    manifest.update(files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)],
        scope=receipt['scope'],intensity_capability_gate_passed=r['capability_gate_passed'],errors=errors,
        completed_capability_training_updates=40000,retained_resource_failed_updates=20,
        complete_evaluation_conditions=74,independently_replayed_planes=222)
    final_manifest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    row=dict(name='intensity_extension',files=len(files),errors=errors,exit_code=int(bool(errors)))
    receipt['checks'].append(row);receipt['errors'].extend(errors);save();print(json.dumps(row,ensure_ascii=False))
    if errors:return 1
    for name,args in [('final_global_write',[str(ROOT/'verify_archive.py'),'--write']),('final_global_read',[str(ROOT/'verify_archive.py')])]:
        p=subprocess.run([sys.executable,'-X','utf8','-B',*args],cwd=ROOT.parent,capture_output=True,text=True,encoding='utf-8')
        row=dict(name=name,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr)
        try:row['parsed_stdout']=json.loads(p.stdout)
        except ValueError:pass
        receipt['checks'].append(row)
        if p.returncode:receipt['errors'].append(name+' failed')
        save();print(json.dumps(row,ensure_ascii=False))
        if p.returncode:return p.returncode
    mismatches=[f['path'] for f in manifest['files'] if sha(ROOT/f['path'])!=f['sha256'] or (ROOT/f['path']).stat().st_size!=f['bytes']]
    row=dict(name='final_all_file_rehash',files=len(files),mismatches=mismatches,exit_code=int(bool(mismatches)))
    receipt['checks'].append(row)
    if mismatches:receipt['errors'].append('Final stage hash changed')
    receipt.update(complete=not receipt['errors'],finished_utc=datetime.now(timezone.utc).isoformat(),
        stage_manifest_file=final_manifest.relative_to(ROOT).as_posix(),stage_manifest_sha256=sha(final_manifest),
        global_manifest_sha256=sha(ROOT/'literature/archive_manifest.json'))
    save();print(json.dumps(row,ensure_ascii=False));return int(not receipt['complete'])


if __name__=='__main__':raise SystemExit(main())
