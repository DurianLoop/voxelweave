"""Verify prior3201 and freeze the projection-information stage within 20MB."""
import hashlib
import json
import os
import re
import sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'literature/matched_oracle_stage_manifest_2026-10-08.json'
PRIOR_PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_MATCHED_ORACLE_2026-10-08.json'
DEST=ROOT/'literature/projection_info_stage_manifest_2026-10-08.json'
PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_PROJECTION_INFO_2026-10-08.json'


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def read(p):return json.loads(p.read_text(encoding='utf-8'))


def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))


def new(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not DEST.exists() and not PROOF.exists()
    prior,priorproof=read(PRIOR),read(PRIOR_PROOF)
    assert prior['complete'] and priorproof['complete'] and not prior['errors'] and not priorproof['errors']
    assert len(prior['evidence_files'])==3201 and sha(PRIOR)==priorproof['manifest_sha256']
    for v in prior['evidence_files']:
        p=ROOT/v['path'];assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
    stage=set()
    for pattern in ('*PROJECTION_INFO*','PROJECTION_AND_SELFSUPERVISED*'):
        stage.update(p for p in ROOT.glob(pattern) if p.is_file())
    for pattern in ('*observed_projection_information*.py','*projection_info_stage*.py'):
        stage.update(p for p in (ROOT/'experiments').glob(pattern) if p.is_file())
    for pattern in ('2026-10-08_selfsupervised*.md','*selfsupervised_selection_primary*.py','selfsupervised_selection_reading_provenance*.json'):
        stage.update(p for p in (ROOT/'literature').glob(pattern) if p.is_file())
    stage.add(Path(__file__))
    walk_errors=[]
    for rel in ('experiments/observed_projection_information_2026_10_08','literature/source_cache/selfsupervised_selection_primary_2026-10-08'):
        folder=ROOT/rel;assert folder.is_dir()
        for current,dirs,files in os.walk(folder,onerror=lambda e:walk_errors.append(str(e))):
            dirs[:]=[d for d in dirs if d not in ('tmp','__pycache__')]
            stage.update(Path(current)/name for name in files if not name.endswith('.pyc'))
    assert not walk_errors
    previous={v['path'] for v in prior['evidence_files']}
    assert not any(p.relative_to(ROOT).as_posix() in previous for p in stage)
    stagebytes=sum(p.stat().st_size for p in stage);assert stagebytes<20_000_000
    post=['SESSION_FINAL_TOOL_OBSERVATIONS_MATCHED_ORACLE_2026-10-08.json',
        'SESSION_POST_ARCHIVE_MATCHED_ORACLE_UPDATE_2026-10-08.md',
        'SESSION_CHECKPOINT_RECEIPT_MATCHED_ORACLE_2026-10-08.json',
        'SESSION_OBSERVED_EXITS_FINALIZE_MATCHED_ORACLE_2026-10-08.json',
        'SESSION_DELIVERY_MATCHED_ORACLE_2026-10-08.md',
        'experiments/finalize_matched_oracle_checkpoint_2026_10_08.py']
    more=stage|{PRIOR,PRIOR_PROOF}|{ROOT/p for p in post};links=[];bindings=[]
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
                if q!=DEST.resolve():
                    assert q.exists() and q.is_relative_to(ROOT.resolve()),(p,target)
                    if q.is_file():more.add(q)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=q.relative_to(ROOT).as_posix()))
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden or p.suffix=='.pyc' for p in more)
    ledgerfile=ROOT/'SESSION_EXECUTION_LEDGER_PROJECTION_INFO_2026-10-08.json';ledger=read(ledgerfile)
    assert ledger['complete'] and not ledger['errors'] and ledger['goal_status']=='active' and not ledger['publication_claim_confirmed']
    assert ledger['medical_arrays_loaded']==ledger['neural_forwards']==ledger['GPU_forwards']==ledger['training_updates']==0
    for v in ledger['root_files_observed']:assert sha(Path(v['path']))==v['sha256']==v['previous_sha256']
    evidence={v['path']:v for v in prior['evidence_files']};additions=[]
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in evidence:
            value=entry(p);evidence[key]=value;additions.append(value)
    newbytes=sum(v['bytes'] for v in additions);assert newbytes<20_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(PRIOR),entry(PRIOR_PROOF),entry(ledgerfile)],
        prior_manifest_sha256=sha(PRIOR),previous_frozen_evidence_files_verified=3201,
        stage_files=[entry(p) for p in sorted(stage)],stage_bytes=stagebytes,new_evidence_files=additions,
        new_evidence_bytes=newbytes,evidence_files=[evidence[key] for key in sorted(evidence)],
        source_bindings_verified=bindings,local_links=links,scientific_evidence_enumeration_errors=walk_errors,
        previous_post_appendices_incorporated=True,historical_failed_pip_temp_directories_retained_and_not_enumerated=True,
        excluded_previous_retained_temporary_directories=prior['excluded_previous_retained_temporary_directories'],
        protocol_v1_retained_and_not_executed=True,protocol_v2_pre_execution_contract_correction=True,
        checked_series=19,checked_axis_maps=22,exact_rank_independent_modular_certificates=True,
        synthetic_same_statistics_direct_input_witness_verified=True,new_medical_arrays_loaded=0,
        new_neural_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        new_primary_papers_read=2,text_pages_read=41,visual_pages_reviewed=6,
        actual_MRI_task_benefit_measured=False,float32_inverse_or_condition_number_certified=False,
        stage_max_saved_bytes=20_000_000,live_training_files_excluded=True,
        full_training_observed_tool_exit=None,goal_status='active',publication_claim_confirmed=False)
    new(DEST,result)
    for v in read(DEST)['evidence_files']:
        p=ROOT/v['path'];assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
    assert all((ROOT/v['target']).exists() for v in links)
    new(PROOF,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        manifest_file=DEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(DEST),stage_files_frozen=len(stage),
        stage_bytes=stagebytes,newly_bound_files=len(additions),new_evidence_bytes=newbytes,
        cumulative_frozen_evidence_files=len(evidence),previous3201_evidence_hashes_unchanged=True,
        all_final_evidence_hashes_verified=True,local_links_verified=True,live_training_files_excluded=True,
        goal_status='active',publication_claim_confirmed=False))
    print(json.dumps(dict(complete=True,new_stage_files=len(stage),newly_bound_files=len(additions),
        cumulative_frozen_evidence_files=len(evidence),stage_bytes=stagebytes,new_evidence_bytes=newbytes,
        previous3201_hashes_unchanged=True,all_final_evidence_hashes_verified=True,
        goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
