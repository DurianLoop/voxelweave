"""Freeze new head/context/statistics/label evidence and rehash the preceding immutable stage."""
import hashlib,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'literature/head_context_stage_manifest_2026-10-07.json'
RECEIPT=ROOT/'SESSION_ARCHIVE_VERIFICATION_HEAD_CONTEXT_2026-10-07.json'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write_new(p,value):
    with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not MANIFEST.exists() and not RECEIPT.exists()
    ledger=read(ROOT/'SESSION_EXECUTION_LEDGER_HEAD_CONTEXT_2026-10-07.json')
    assert ledger['all_own_runs_terminal_from_observed_tool_exits'] and ledger['live_own_runs']==[]
    assert ledger['new_patient_cpu_head_parameter_updates']==6144 and ledger['new_patient_gpu_updates']==0
    direct=ROOT/'experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07';tiles=ROOT/'experiments/mc_rc_3d_all_tile_head_fit_2026_10_07'
    a,b=read(direct/'attempt01.json'),read(tiles/'attempt01.json')
    av,bv=read(direct/'module_full_fov_verification_attempt01.json'),read(tiles/'module_features_and_full_fov_verification_attempt01.json')
    norm=read(ROOT/'experiments/mc_rc_3d_reference_in_preflight_v3_2026_10_07/attempt01.json')
    label=read(ROOT/'experiments/mc_rc_3d_label_roundtrip_v3_2026_10_07/attempt01.json')
    for r in (a,b,av,bv,norm,label):assert r['complete'] and not r['errors'] and r['cuda_initialized'] is False
    assert a['actual_patient_cpu_head_parameter_updates']==4096 and b['actual_patient_cpu_head_parameter_updates']==2048
    assert av['result_sha256']==sha(direct/'attempt01.json') and bv['result_sha256']==sha(tiles/'attempt01.json')
    assert len(a['arms'])==4 and len(b['arms'])==2
    for r in (a,b):
        assert not any(x['training_fit_gate_passed'] for x in r['arms'])
        for arm in r['arms']:
            assert arm['updates_completed']==1024 and len(arm['history'])==1024
            assert sha(ROOT/arm['checkpoint_file'])==arm['checkpoint_sha256'] and sha(ROOT/arm['prediction_file'])==arm['prediction_sha256']
    for replay in (av,bv):assert all(x['prediction_disagreements']==0 and x['probability_max_absolute_error']<=3e-6 for x in replay['arms'])
    assert len(norm['primitive_checks'])==2 and len(norm['self_replays'])==3
    assert all(s['candidate_self_replay']['probability_max_absolute_error_by_head']==[0,0,0] for s in norm['self_replays'])
    assert not norm['ground_truth_pixels_opened'] and not norm['native_hidden_mri_pixels_opened'] and not norm['task_effect_endpoint_computed']
    assert len(label['series'])==19 and len(label['patients'])==11 and label['series_full_diagnostic_gates_passed']==18
    assert label['production_float32_strict_comparisons_passed']==14
    assert all(s['prediction_disagreements']==0 and s['float64_coordinate_verification']['prediction_disagreements']==0 for s in label['series'])
    failures=[ROOT/'experiments'/d/'attempt01.json' for d in (
        'mc_rc_3d_reference_in_preflight_2026_10_07','mc_rc_3d_reference_in_preflight_v2_2026_10_07',
        'mc_rc_3d_label_roundtrip_2026_10_07','mc_rc_3d_label_roundtrip_v2_2026_10_07')]
    assert all(not read(p)['complete'] and read(p)['errors'] for p in failures)
    priorpath=ROOT/'literature/cpu_fit_followup_stage_manifest_2026-10-07.json';prior=read(priorpath)
    assert prior['complete'] and not prior['errors'] and len(prior['evidence_files'])==283
    for entry in prior['evidence_files']:assert sha(ROOT/entry['path'])==entry['sha256'],'Prior immutable evidence changed: '+entry['path']
    priorreceipt=ROOT/'SESSION_ARCHIVE_VERIFICATION_CPU_FIT_FOLLOWUP_2026-10-07.json'
    assert read(priorreceipt)['manifest_sha256']==sha(priorpath)
    protected={e['path'] for e in prior['stage_files']+prior['evidence_files']}|{priorpath.relative_to(ROOT).as_posix(),priorreceipt.relative_to(ROOT).as_posix()}
    candidates=set(ROOT.glob('*2026-10-07.md'))|set(ROOT.glob('*HEAD_CONTEXT*2026-10-07.json'))
    candidates |= set((ROOT/'experiments').glob('*2026_10_07.py'))|set((ROOT/'literature').glob('*2026_10_07.py'))|set((ROOT/'literature').glob('2026-10-07*.md'))
    stage={p for p in candidates if p.relative_to(ROOT).as_posix() not in protected and p not in (MANIFEST,RECEIPT)}
    directories=['mc_rc_3d_frozen_feature_head_fit_2026_10_07','mc_rc_3d_all_tile_head_fit_2026_10_07',
        'mc_rc_3d_reference_in_preflight_2026_10_07','mc_rc_3d_reference_in_preflight_v2_2026_10_07','mc_rc_3d_reference_in_preflight_v3_2026_10_07',
        'mc_rc_3d_label_roundtrip_2026_10_07','mc_rc_3d_label_roundtrip_v2_2026_10_07','mc_rc_3d_label_roundtrip_v3_2026_10_07']
    for d in directories:stage|={p for p in (ROOT/'experiments'/d).rglob('*') if p.is_file()}
    for d in ('mc_rc_3d_frozen_feature_head_fit_2026_10_07','mc_rc_3d_all_tile_head_fit_2026_10_07'):
        stage|={p for p in (ROOT/'figures'/d).rglob('*') if p.is_file()}
    cache=ROOT/'literature/source_cache/feature_normalization_primary_2026-10-07'
    stage|={p for p in cache.rglob('*') if p.is_file()}
    assert all(p.is_relative_to(ROOT) and p.is_file() for p in stage)
    size=sum(p.stat().st_size for p in stage);assert size<=100_000_000
    evidence={ROOT/e['path'] for e in prior['evidence_files']}|stage|{priorpath,priorreceipt}
    scripts={sha(p) for p in evidence if p.suffix=='.py'}
    for p in stage:
        if p.suffix!='.json':continue
        obj=read(p)
        if not isinstance(obj,dict):continue
        if obj.get('script_sha256'):assert obj['script_sha256'] in scripts,'Missing source SHA for '+p.name
        for binding in obj.get('source_bindings',[]):
            target=ROOT/binding['path'];assert target.is_relative_to(ROOT) and sha(target)==binding['sha256'];evidence.add(target)
    reading=read(cache/'reading_provenance_2026_10_07.json');assert reading['complete'] and reading['primary_texts_read']==3 and reading['total_pdf_pages_textually_read']==33
    for p in reading['papers']:
        assert p['actual_reading_completed'] and sha(cache/p['pdf_file'])==p['pdf_sha256'] and sha(cache/p['text_file'])==p['text_sha256']
        visual=p['formula_visual_review'];assert visual['actual_view_image_completed'] and sha(cache/visual['image_file'])==visual['image_sha256']
    visual=read(ROOT/'SESSION_HEAD_CONTEXT_FIGURE_VISUAL_REVIEW_2026-10-07.json');assert visual['complete'] and len(visual['figures'])==2
    for fig in visual['figures']:assert fig['actual_view_image_completed'] and sha(ROOT/fig['path'])==fig['sha256']
    for s in label['series']:
        target=ROOT/s['label_file'];assert sha(target)==s['label_sha256'];evidence.add(target)
    links=[]
    for p in stage:
        if p.suffix!='.md':continue
        for url in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            url=url.strip('<>')
            if re.match(r'https?://|app://',url):continue
            target=(p.parent/url.split('#',1)[0]).resolve();assert target.exists() and target.is_relative_to(ROOT),f'Invalid link in {p.name}: {url}'
            links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
            if target.is_file():evidence.add(target)
    def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
                  stage_files=[entry(p) for p in sorted(stage)],evidence_files=[entry(p) for p in sorted(evidence)],
                  prior_manifest_sha256=sha(priorpath),local_links=links,new_cpu_head_parameter_updates=6144,new_gpu_updates=0,
                  new_primary_texts_read=3,new_pdf_pages_textually_read=33,new_formula_pages_visually_read=3,
                  original_failed_attempts_preserved=True,all_six_head_fit_gates_failed=True,
                  production_float32_label_probability_strict_failures_retained=5,developer_label_diagnostic_gate_failures_retained=1,
                  confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    write_new(MANIFEST,manifest)
    for k in ('stage_files','evidence_files'):
        for e in read(MANIFEST)[k]:assert sha(ROOT/e['path'])==e['sha256']
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest_file=MANIFEST.relative_to(ROOT).as_posix(),
                manifest_sha256=sha(MANIFEST),stage_files=len(stage),evidence_files=len(evidence),stage_saved_bytes=size,
                local_links_verified=len(links),prior_283_immutable_evidence_rehashed=True,all_files_rehashed=True,
                new_cpu_head_parameter_updates=6144,new_gpu_updates=0,new_primary_texts_read=3,
                all_six_original_head_fit_gates_failed=True,reference_in_implementation_preflight_complete=True,
                label_roundtrip_all19_complete=True,label_float32_strict_passed=14,label_diagnostic_gates_passed=18,
                own_live_runs=[],all_own_runs_terminal_from_observed_tool_exits=True,
                original_task_capability_gate_changed=False,confirmation_patients_opened=False,scientific_confirmation_patients=0,
                publication_claim_confirmed=False,goal_status='active',user_processes_enumerated_or_modified=False)
    write_new(RECEIPT,result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
