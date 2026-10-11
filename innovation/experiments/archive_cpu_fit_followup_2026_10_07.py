"""Finalize this CPU-fit/literature stage after observed exits and complete replay."""
import hashlib,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'literature/cpu_fit_followup_stage_manifest_2026-10-07.json'
RECEIPT=ROOT/'SESSION_ARCHIVE_VERIFICATION_CPU_FIT_FOLLOWUP_2026-10-07.json'
LEDGER=ROOT/'SESSION_EXECUTION_LEDGER_CPU_FIT_FOLLOWUP_2026-10-07.json'
FIT=ROOT/'experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write_new(p,x):
    with p.open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not MANIFEST.exists() and not RECEIPT.exists()
    ledger=read(LEDGER);assert ledger['all_own_runs_terminal_from_observed_tool_exits'] and ledger['live_own_runs']==[]
    prod=read(FIT/'attempt_01.json');proof=read(FIT/'independent_both512_and_full_fov_2026_10_07.json')
    diag=read(ROOT/'experiments/mc_rc_3d_final_patch_diagnostic_2026_10_07/attempt01.json')
    audit=read(ROOT/'experiments/mc_rc_3d_development_supervision_2026_10_07/attempt_01.json')
    density=read(ROOT/'experiments/mc_rc_3d_supervision_density_2026_10_07/attempt01.json')
    for r in (prod,proof,diag,audit,density):assert r['complete'] and not r['errors']
    assert prod['total_updates_completed']==1024 and prod['actual_gpu_updates']==0 and not prod['cuda_initialized']
    assert proof['result_sha256']==diag['fit_result_sha256']==sha(FIT/'attempt_01.json')
    assert density['source_sha256']==sha(ROOT/'experiments/mc_rc_3d_development_supervision_2026_10_07/attempt_01.json')
    assert audit['draws_checked']==608 and audit['all_scaled_gt_voxels_replayed']==1454374912
    assert audit['forced_patch_zero_gt_by_scale']==[0,0,0] and audit['whole_batch_zero_gt_by_scale']==[0,0,0]
    assert density['uniform_fine_positive_coarse_zero']==[11,17] and density['empty_fine_patch_ratio_undefined']==[441,441]
    assert all(a['updates_completed']==512 and a['complete'] and a['evaluation_complete'] for a in prod['arms'])
    for arm in prod['arms']:
        assert len(arm['every_update_history'])==512
        assert sha(ROOT/arm['checkpoint_file'])==arm['checkpoint_sha256']
        assert sha(ROOT/arm['prediction_file'])==arm['prediction_sha256']
    tiny_dirs=['mc_rc_3d_tiny_gpu_numerical_2026_10_07']+[
        f'mc_rc_3d_tiny_gpu_numerical_attempt0{i}_2026_10_07' for i in (2,3,4)]
    tiny=[read(ROOT/'experiments'/d/'attempt01.json') for d in tiny_dirs]
    assert all(not p['complete'] and p['errors'] and p['actual_patient_training_updates']==0 for p in tiny)
    assert sum(p['actual_synthetic_gpu_updates'] for p in tiny)==3
    assert max(tiny[-1]['pre_update_numeric_observations'][0]['forward_probability_max_absolute_error_by_head'])<=3e-4
    assert tiny[-1]['pre_update_numeric_observations'][0]['forward_threshold_disagreements_by_head']==[0,0,0]
    assert tiny[-1]['resource_observations'][-1]['own_gpu_peak_reserved_bytes']==192937984
    prior_path=ROOT/'literature/native_reference_3d_stage_manifest_attempt02_2026-10-07.json';prior=read(prior_path)
    prior_stage={e['path'] for e in prior['stage_files']}
    candidates=set(ROOT.glob('*2026-10-07.md'))|set((ROOT/'experiments').glob('*2026_10_07.py'))
    candidates|=set((ROOT/'literature').glob('*2026_10_07.py'))|set((ROOT/'literature').glob('2026-10-07*.md'))
    stage={p for p in candidates if p.relative_to(ROOT).as_posix() not in prior_stage};stage.add(LEDGER)
    directories=['mc_rc_3d_cpu_fixed_fit_2026_10_07','mc_rc_3d_development_supervision_2026_10_07',
                 'mc_rc_3d_independent_interpreter_preflight_2026_10_07','mc_rc_3d_final_patch_diagnostic_2026_10_07',
                 'mc_rc_3d_supervision_density_2026_10_07','mc_rc_3d_19series_resource_planning_2026_10_07']+tiny_dirs
    for d in directories:stage|={p for p in (ROOT/'experiments'/d).rglob('*') if p.is_file()}
    cache_dirs=['3d_context_supervision_2026-10-07','small_target_fit_search_2026-10-07',
                'small_target_loss_routes_2026-10-07','dice_region_bias_fulltext_2026-10-07',
                'dice_followup_metadata_2026-10-07','dice_followup_fulltexts_2026-10-07']
    for d in cache_dirs:stage|={p for p in (ROOT/'literature/source_cache'/d).rglob('*') if p.is_file()}
    for d in ('mc_rc_3d_supervision_density_2026_10_07','mc_rc_3d_cpu_fixed_fit_2026_10_07'):
        stage|={p for p in (ROOT/'figures'/d).rglob('*') if p.is_file()}
    stage|={p for p in ROOT.glob('SESSION_*CPU_FIT*2026-10-07.json') if p!=RECEIPT}
    assert all(p.is_file() and p.is_relative_to(ROOT) for p in stage)
    assert sum(p.stat().st_size for p in stage)<=250_000_000
    evidence={ROOT/e['path'] for e in prior['evidence_files']}|stage|{prior_path}
    for e in prior['evidence_files']:assert sha(ROOT/e['path'])==e['sha256'], 'A prior immutable evidence file changed: '+e['path']
    scripts={sha(p) for p in evidence if p.suffix=='.py'}
    for p in stage:
        if p.suffix!='.json':continue
        obj=read(p)
        if not isinstance(obj,dict):continue
        for binding in obj.get('source_bindings',[]):
            dependency=ROOT/binding['path'];assert sha(dependency)==binding['sha256'];evidence.add(dependency)
        if obj.get('script_sha256'):assert obj['script_sha256'] in scripts,'Missing result source: '+p.name
    readings=[read(ROOT/'literature/source_cache'/d/'reading_provenance_2026_10_07.json') for d in
              ('3d_context_supervision_2026-10-07','dice_region_bias_fulltext_2026-10-07','dice_followup_fulltexts_2026-10-07')]
    assert len(readings[0]['papers'])==2 and readings[1]['actual_reading_completed'] and len(readings[2]['papers'])==2
    visual=read(ROOT/'SESSION_CPU_FIT_FIGURE_VISUAL_REVIEW_2026-10-07.json')
    assert visual['complete'] and len(visual['figures'])==2
    links=[]
    for p in stage:
        if p.suffix!='.md':continue
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            link=link.strip('<>')
            if re.match(r'https?://|app://',link):continue
            target=(p.parent/link.split('#',1)[0]).resolve()
            assert target.exists() and target.is_relative_to(ROOT),f'Broken or out-of-scope local link: {p.name}: {link}'
            links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix(),directory=target.is_dir()))
            if target.is_file():evidence.add(target)
    def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
                  stage_files=[entry(p) for p in sorted(stage)],evidence_files=[entry(p) for p in sorted(evidence)],
                  local_links=links,prior_manifest_sha256=sha(prior_path),
                  actual_patient_cpu_updates=1024,actual_synthetic_gpu_updates=3,actual_patient_gpu_updates=0,
                  publication_claim_confirmed=False,scientific_confirmation_patients=0,goal_status='active',
                  primary_texts_read=5,generalised_dice_svg_numerical_tables_not_visually_reviewed=True,
                  formal_19series_training_not_yet_run=True,full_batch_gpu_qualification_not_passed=True)
    write_new(MANIFEST,manifest)
    for group in ('stage_files','evidence_files'):
        for e in read(MANIFEST)[group]:assert sha(ROOT/e['path'])==e['sha256']
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
                manifest_file=MANIFEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(MANIFEST),
                stage_files=len(stage),evidence_files=len(evidence),local_links_verified=len(links),
                stage_saved_bytes=sum(p.stat().st_size for p in stage),all_files_rehashed=True,
                prior_immutable_evidence_rehashed=True,patient_cpu_updates=1024,synthetic_gpu_updates=3,
                patient_gpu_updates=0,both_training_fit_gates_passed=prod['both_training_fit_gates_passed'],
                independent_functional_full_fov_replay_complete=True,four_variant_diagnostic_complete=True,
                all_own_runs_terminal_from_observed_tool_exits=True,own_live_runs=[],
                original_capability_gate_changed=False,confirmation_patients_opened=False,
                scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active',
                user_processes_enumerated_or_modified=False)
    write_new(RECEIPT,result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
