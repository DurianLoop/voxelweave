"""Bind a supplied actual tool observation to current metadata; never control training."""
import sys,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;PREVIOUS=ROOT/'lossless_final_evaluation_entry_2026_10_08'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=client.resource_guard()
    assert len(sys.argv)==2;inp=Path(sys.argv[1]).resolve();assert inp.parent==HERE.resolve()
    a=read(inp);assert a['actual_live_poll']['session_id']==99542
    assert a['actual_live_poll']['terminal_exit'] is None and a['actual_live_poll']['tool_confirmed_session_live']
    assert a['actual_readiness_probe']['exit_code']==3 and a['actual_readiness_probe']['MR_or_GT_arrays_loaded']==0
    output=HERE/(inp.stem.replace('_input','_observation')+'.json');assert output!=inp and not output.exists()
    pm=PREVIOUS/'ARCHIVE_MANIFEST.json';pp=PREVIOUS/'ARCHIVE_PROOF.json';proof=read(pp)
    assert proof['complete'] and proof['cumulative_frozen_evidence_files']==5430
    assert sha(pm)==proof['manifest_sha256']=='d6481cf77e2e46303c4433969ac37804034ba0f70fbfa487570378abb696658e'
    assert sha(pp)=='258d257d14079cd721004cfe90d9fdf25c2e1373163d2a44c51147fe33d05241'
    qual=read(PREVIOUS/'compression_qualification_v3/receipt.json');assert qual['complete'] and not qual['errors']
    for b in qual['production_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    train=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07';q=read(train/'invocation02.json')
    metadata=dict(status=q.get('status'),complete=q.get('complete'),
        arms=[{k:r.get(k) for k in ['kind','updates_completed','complete']} for r in q['arms']],
        actual_terminal_exit_not_inferred_from_metadata=True)
    roots=[]
    for path,expected in [('D:/MRI/.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('D:/MRI/environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        assert sha(Path(path))==expected;roots.append(dict(path=path,sha256=expected))
    docs=[Path(__file__),HERE/'WATCH_PROTOCOL.md',inp,pm,pp]+[PREVIOUS/n for n in
        ['record_post_archive.py','POST_ARCHIVE_INPUT.json','POST_ARCHIVE_OBSERVATIONS.json','compression_qualification_v3/receipt.json',
         'evaluate_final_lossless_v3.py','verify_final_lossless_v3.py','final_eval_lossless_v3.py']]
    prior=sorted(HERE.glob('turn_*_observation.json'))
    if prior:docs.append(prior[-1])
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],turn_classification='verified_wait',
        previous_turn_classification=a['previous_turn_classification'],actual_tool_observations=a,
        current_training_metadata=metadata,source_bindings=[client.base.entry(p) for p in docs],
        root_files_observed=roots,resource_snapshot=resources,frozen_archive_evidence_files=5430,
        previous_archive_or_bound_files_modified=False,watch_records_pending_next_substantive_archive=True,
        original_training_modified=False,other_processes_enumerated=False,other_processes_modified=False,
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,GPU_forwards=0,
        new_medical_training_updates=0,head_fits=0,new_action_labels_generated=0,new_agents_delegated=0,
        new_primary_papers_read=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        publication_claim_confirmed=False,goal_status='active',automatic_approval_review_rejections_received=0)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<1_000_000
    client.base.new(output,result)
    print(json.dumps(dict(complete=True,turn_classification='verified_wait',observation=client.base.entry(output),
        current_training_metadata=metadata,resource_snapshot=resources,goal_status='active'),ensure_ascii=False),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
