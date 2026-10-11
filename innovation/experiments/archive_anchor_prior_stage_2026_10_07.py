"""Verify prior1708 and freeze current scientific records, without live files."""
import hashlib,json,os,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'literature/observed_roi_stage_manifest_2026-10-07.json'
DEST=ROOT/'literature/anchor_prior_stage_manifest_2026-10-07.json'
PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_ANCHOR_PRIOR_2026-10-07.json'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def new(p,r):
    with p.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not DEST.exists() and not PROOF.exists()
    prior=read(PRIOR);assert prior['complete'] and not prior['errors'] and len(prior['evidence_files'])==1708
    for v in prior['evidence_files']:
        p=ROOT/v['path'];assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
    ledgerpath=ROOT/'SESSION_EXECUTION_LEDGER_ANCHOR_PRIOR_2026-10-07.json';ledger=read(ledgerpath)
    assert ledger['complete'] and not ledger['errors'] and ledger['goal_status']=='active' and not ledger['publication_claim_confirmed']
    stage={p for p in ROOT.glob('*ANCHOR_PRIOR*') if p.is_file()}|{p for p in ROOT.glob('MC_RC_ANCHOR_PRIOR_FOREST*') if p.is_file()}
    for pattern in ('*anchor_prior_forest*.py','install_anchor_forest_runtime*.py','record_anchor_prior_stage*.py'):
        stage|={p for p in (ROOT/'experiments').glob(pattern) if p.is_file()}
    stage.add(Path(__file__))
    for pattern in ('2026-10-07_prior_balance*.md','fetch_prior_balance*.py','prior_balance_reading_provenance*.json'):
        stage|={p for p in (ROOT/'literature').glob(pattern) if p.is_file()}
    folders=[
        'experiments/mc_rc_anchor_prior_forest_diagnostic_2026_10_07',
        'experiments/mc_rc_anchor_prior_forest_diagnostic_v2_2026_10_07',
        'experiments/mc_rc_anchor_prior_forest_diagnostic_v3_2026_10_07',
        'experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07',
        'experiments/mc_rc_anchor_prior_forest_amortization_2026_10_07',
        'tools/anchor_forest_runtime_2026_10_07','tools/anchor_forest_runtime_v2_2026_10_07',
        'tools/anchor_forest_runtime_v3_2026_10_07','tools/anchor_forest_runtime_v4_2026_10_07',
        'tools/anchor_forest_joblib_tls12_2026_10_07',
        'literature/source_cache/prior_balance_primary_2026-10-07',
        'literature/source_cache/prior_balance_primary_attempt02_2026-10-07',
        'literature/source_cache/prior_balance_visual_2026-10-07']
    skipped=[];walk_errors=[]
    for folder in folders:
        assert (ROOT/folder).is_dir()
        for current,dirs,files in os.walk(ROOT/folder,onerror=lambda e:walk_errors.append(str(e))):
            for name in list(dirs):
                if name in ('tmp','__pycache__'):
                    skipped.append(dict(path=(Path(current)/name).relative_to(ROOT).as_posix(),reason='failed installer temporary/cache directory retained; excluded from evidence hashes'))
                    dirs.remove(name)
            stage|={Path(current)/name for name in files if not name.endswith('.pyc')}
    assert not walk_errors,walk_errors
    stagebytes=sum(p.stat().st_size for p in stage);assert stagebytes<250_000_000
    protected={v['path'] for v in prior['evidence_files']};assert not any(p.relative_to(ROOT).as_posix() in protected for p in stage)
    post=['SESSION_ARCHIVE_VERIFICATION_OBSERVED_ROI_2026-10-07.json','SESSION_FINAL_TOOL_OBSERVATIONS_OBSERVED_ROI_2026-10-07.json',
        'SESSION_POST_ARCHIVE_OBSERVED_ROI_UPDATE_2026-10-07.md','SESSION_CHECKPOINT_RECEIPT_OBSERVED_ROI_2026-10-07.json',
        'SESSION_OBSERVED_EXITS_FINALIZE_OBSERVED_ROI_2026-10-07.json','experiments/finalize_observed_roi_checkpoint_2026_10_07.py']
    more=stage|{PRIOR}|{ROOT/p for p in post};bindings=[];links=[]
    for p in sorted(stage):
        if p.suffix=='.json':
            d=read(p)
            if isinstance(d,dict):
                for b in d.get('source_bindings',[]):
                    q=(ROOT/b['path']).resolve();assert q.is_file() and q.is_relative_to(ROOT.resolve()) and sha(q)==b['sha256'],(p,b)
                    more.add(q);bindings.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
        elif p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                target=target.strip('<>')
                if re.match(r'https?://|app://',target):continue
                q=(Path(target) if re.match(r'^[A-Za-z]:[/\\]',target) else p.parent/target.split('#',1)[0]).resolve()
                if q==DEST.resolve():links.append(dict(document=p.relative_to(ROOT).as_posix(),target=DEST.relative_to(ROOT).as_posix()));continue
                assert q.exists() and q.is_relative_to(ROOT.resolve()),(p,target)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=q.relative_to(ROOT).as_posix()))
                if q.is_file():more.add(q)
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden or p.suffix=='.pyc' for p in more)
    prod=read(ROOT/'experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07/attempt01.json')
    verify=read(ROOT/'experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07/independent_label_models_roi_attempt01.json')
    assert prod['complete'] and verify['complete'] and not prod['errors'] and not verify['errors'] and verify['checked_series']==19
    for v in prod['prediction_receipts']:assert sha(ROOT/v['prediction_file']['path'])==v['prediction_file']['sha256']
    for v in prod['folds']:assert sha(ROOT/v['model']['path'])==v['model']['sha256']
    for v in prod['series_statistics']:assert sha(ROOT/v['training_sample_file']['path'])==v['training_sample_file']['sha256']
    for doc in (prod,):
        for v in doc['source_snapshots']:assert sha(ROOT/v['snapshot']['path'])==v['snapshot']['sha256']==sha(ROOT/v['source_path'])
    for v in ledger['root_files_observed']:assert sha(Path(v['path']))==v['sha256']==v['previous_sha256']
    proof=read(ROOT/'SESSION_ARCHIVE_VERIFICATION_OBSERVED_ROI_2026-10-07.json');assert proof['complete'] and sha(PRIOR)==proof['manifest_sha256']
    evidence={v['path']:v for v in prior['evidence_files']}
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in evidence:evidence[key]=entry(p)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[entry(Path(__file__)),entry(PRIOR),entry(ledgerpath)],
        prior_manifest_sha256=sha(PRIOR),previous_frozen_evidence_files_verified=1708,stage_files=[entry(p) for p in sorted(stage)],stage_bytes=stagebytes,
        evidence_files=[evidence[key] for key in sorted(evidence)],source_bindings_verified=bindings,local_links=links,excluded_retained_temporary_directories=skipped,
        scientific_evidence_enumeration_errors=walk_errors,previous_post_appendices_incorporated=True,failed_versions_and_receipts_preserved=True,
        checked_series=19,checked_supports=57,checked_missing_plane_records=3015,forest_trees_compared=704,
        actual_medical_array_counts=ledger['actual_medical_array_counts_including_failed_preparation'],new_primary_papers_read=2,text_pages_read=21,visual_pages_reviewed=4,
        live_training_files_excluded=True,full_training_observed_tool_exit=None,new_GPU_forwards=0,new_neural_training_updates=0,publication_claim_confirmed=False,goal_status='active')
    new(DEST,result)
    for v in read(DEST)['evidence_files']:
        p=ROOT/v['path'];assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
    assert all((ROOT/v['target']).exists() for v in links)
    new(PROOF,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest_file=DEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(DEST),
        stage_files_frozen=len(stage),stage_bytes=stagebytes,cumulative_frozen_evidence_files=len(evidence),previous1708_evidence_hashes_unchanged=True,
        all_final_evidence_hashes_verified=True,live_training_files_excluded=True,goal_status='active',publication_claim_confirmed=False))
    print(json.dumps(dict(complete=True,new_stage_files=len(stage),cumulative_frozen_evidence_files=len(evidence),stage_bytes=stagebytes,previous1708_hashes_unchanged=True,excluded_retained_temp_directories=len(skipped),goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
