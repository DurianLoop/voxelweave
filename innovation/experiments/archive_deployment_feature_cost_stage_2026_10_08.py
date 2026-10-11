"""Verify prior3687 and freeze new measured costs, reading, and narrower claim preparation."""
import hashlib,json,os,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'literature/observed_holdout_stage_manifest_2026-10-08.json'
PRIOR_PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_OBSERVED_HOLDOUT_2026-10-08.json'
DEST=ROOT/'literature/deployment_feature_cost_stage_manifest_2026-10-08.json'
PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_DEPLOYMENT_FEATURE_COST_2026-10-08.json'


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not DEST.exists() and not PROOF.exists()
    prior,priorproof=read(PRIOR),read(PRIOR_PROOF)
    assert prior['complete'] and priorproof['complete'] and not prior['errors'] and not priorproof['errors']
    assert len(prior['evidence_files'])==3687 and sha(PRIOR)==priorproof['manifest_sha256']
    for v in prior['evidence_files']:
        p=ROOT/v['path'];assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
    stage=set()
    for pattern in ('*DEPLOYMENT_FEATURE_COST*','TASK_ADAPTED_ACTION_UTILITY_NEXT*','CONDITIONAL_VARIANCE_PROOF_CHECK*'):
        stage.update(p for p in ROOT.glob(pattern) if p.is_file())
    for pattern in ('*deployment*feature*cost*.py','deployment*feature*cost*.json','*conditional_variance_proof_step*.py'):
        stage.update(p for p in (ROOT/'experiments').glob(pattern) if p.is_file())
    for pattern in ('*downstream*feature*cost*.py','*prakash*primary*.py','*deferral_collision*.py',
        '2026-10-08_downstream_segmentation*.md','2026-10-08_relative_utility*.md','deployment_feature_cost_reading_provenance*.json'):
        stage.update(p for p in (ROOT/'literature').glob(pattern) if p.is_file())
    walk_errors=[]
    for rel in ('experiments/deployment_observed_feature_cost_2026_10_08',
        'experiments/deployment_observed_feature_cost_launch_2026_10_08',
        'experiments/deployment_observed_feature_cost_metadata_2026_10_08',
        'experiments/conditional_variance_proof_step_2026_10_08',
        'literature/source_cache/downstream_feature_cost_primary_2026-10-08'):
        folder=ROOT/rel;assert folder.is_dir()
        for current,dirs,files in os.walk(folder,onerror=lambda e:walk_errors.append(str(e))):
            dirs[:]=[d for d in dirs if d not in ('tmp','__pycache__')]
            stage.update(Path(current)/name for name in files if not name.endswith('.pyc'))
    assert not walk_errors
    stage.discard(DEST);stage.discard(PROOF)
    previous={v['path'] for v in prior['evidence_files']}
    assert all(p.relative_to(ROOT).as_posix() not in previous for p in stage)
    stagebytes=sum(p.stat().st_size for p in stage);assert stagebytes<30_000_000
    post=['SESSION_FINAL_TOOL_OBSERVATIONS_OBSERVED_HOLDOUT_2026-10-08.json',
        'SESSION_POST_ARCHIVE_OBSERVED_HOLDOUT_UPDATE_2026-10-08.md',
        'SESSION_CHECKPOINT_RECEIPT_OBSERVED_HOLDOUT_2026-10-08.json',
        'SESSION_OBSERVED_EXITS_FINALIZE_OBSERVED_HOLDOUT_2026-10-08.json',
        'SESSION_DELIVERY_OBSERVED_HOLDOUT_2026-10-08.md',
        'SESSION_PREPARED_FINAL_REPLY_OBSERVED_HOLDOUT_2026-10-08.md',
        'experiments/finalize_observed_holdout_checkpoint_2026_10_08.py']
    more=stage|{PRIOR,PRIOR_PROOF}|{ROOT/p for p in post}
    bindings=[];links=[]
    for p in sorted(stage|{ROOT/t for t in post}):
        if p.suffix=='.json':
            data=read(p)
            if isinstance(data,dict):
                for b in data.get('source_bindings',[]):
                    q=(ROOT/b['path']).resolve()
                    assert q.is_file() and q.is_relative_to(ROOT.resolve()) and sha(q)==b['sha256'],(p,b)
                    more.add(q);bindings.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
        elif p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                target=target.strip('<>')
                if re.match(r'https?://|app://',target):continue
                q=(Path(target) if re.match(r'^[A-Za-z]:[/\\]',target) else p.parent/target.split('#',1)[0]).resolve()
                if q!=DEST.resolve():
                    assert q.exists() and q.is_relative_to(ROOT.resolve()),(p,target)
                    if q.is_file():more.add(q)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=q.relative_to(ROOT).as_posix()))
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt',
        'native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden or p.suffix=='.pyc' for p in more)
    ledgerfile=ROOT/'SESSION_EXECUTION_LEDGER_DEPLOYMENT_FEATURE_COST_2026-10-08.json'
    ledger=read(ledgerfile)
    assert ledger['complete'] and not ledger['errors'] and ledger['goal_status']=='active'
    assert ledger['observed_package_load_events']==19 and ledger['feature_rows_exact']==19
    assert ledger['new_primary_papers_read']==1 and ledger['new_text_pages_read']==9 and ledger['visual_pages_reviewed']==4
    assert ledger['old_primary_method_pages_reread']==2 and ledger['two_path_cost_sensitive_defer_control_required']
    assert all(ledger[k]==0 for k in ('neural_forwards','GPU_forwards','training_updates','model_arrays_loaded'))
    for v in ledger['root_files_observed']:assert sha(Path(v['path']))==v['sha256']==v['previous_sha256']
    evidence={v['path']:v for v in prior['evidence_files']};additions=[]
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in evidence:
            value=entry(p);evidence[key]=value;additions.append(value)
    newbytes=sum(v['bytes'] for v in additions);assert newbytes<30_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(PRIOR),entry(PRIOR_PROOF),entry(ledgerfile)],
        prior_manifest_sha256=sha(PRIOR),previous_frozen_evidence_files_verified=3687,
        stage_files=[entry(p) for p in sorted(stage)],stage_bytes=stagebytes,new_evidence_files=additions,
        new_evidence_bytes=newbytes,evidence_files=[evidence[k] for k in sorted(evidence)],
        source_bindings_verified=bindings,local_links=links,scientific_evidence_enumeration_errors=walk_errors,
        previous_post_appendices_incorporated=True,previous_portable_runtime_remains_bound_and_verified=True,
        excluded_previous_retained_temporary_directories=prior['excluded_previous_retained_temporary_directories'],
        historical_failed_pip_temp_directories_retained_and_not_enumerated=True,
        stage_max_saved_bytes=30_000_000,medical_job_saved_limit_remains=20_000_000,
        observed_package_load_events=19,new_neural_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        new_primary_papers_read=1,new_supplemental_documents_read=1,new_text_pages_read=9,visual_pages_reviewed=4,
        old_primary_method_pages_reread=2,measured_cold_child_seconds=ledger['measured_cold_child_end_to_end_seconds'],
        full_action_cost_measured=False,actual_MRI_task_benefit_measured=False,complete_Noise2Same_theorem1_disproved=False,
        live_training_files_excluded=True,full_training_observed_tool_exit=None,goal_status='active',publication_claim_confirmed=False)
    new(DEST,result)
    for v in result['evidence_files']:assert (ROOT/v['path']).stat().st_size==v['bytes'] and sha(ROOT/v['path'])==v['sha256'],v['path']
    proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        manifest=DEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(DEST),
        previous3687_evidence_hashes_unchanged=True,all_final_evidence_hashes_verified=True,
        stage_files=len(stage),stage_bytes=stagebytes,newly_bound_files=len(additions),new_evidence_bytes=newbytes,
        cumulative_frozen_evidence_files=len(evidence),local_links_verified=True,all_source_bindings_verified=True,
        source_binding_count=len(bindings),local_link_count=len(links),automatic_approval_review_rejections_received=0,
        user_terminal_processes_controlled=False,actual_MRI_task_benefit_measured=False,goal_status='active',publication_claim_confirmed=False)
    new(PROOF,proof)
    print(json.dumps({k:proof[k] for k in ('complete','stage_files','stage_bytes','newly_bound_files','new_evidence_bytes',
        'cumulative_frozen_evidence_files','previous3687_evidence_hashes_unchanged','local_links_verified','goal_status')},ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
