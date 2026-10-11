"""Record actual inherited qualifications, new reading, live observation and roots."""
import hashlib,json,sys,time,ctypes,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PROJECT=ROOT.parent
READING=ROOT/'task_adaptation_compute_prior_art_2026_10_08'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def own_priority():
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=ctypes.c_void_p
    k.SetPriorityClass.argtypes=(ctypes.c_void_p,ctypes.c_uint32)
    assert k.SetPriorityClass(k.GetCurrentProcess(),0x00004000)

def main():
    sys.stdout.reconfigure(encoding='utf-8');own_priority();tick=time.perf_counter()
    qual=read(HERE/'qualification_attempt01/receipt.json');ind=read(HERE/'independent_attempt01/receipt.json')
    assert qual['complete'] and ind['complete'] and not qual['errors'] and not ind['errors']
    assert qual['real_archived_series_pairs']==9 and ind['independently_replayed_real_pairs']==9
    assert qual['real_archived_patient_pairs']==4 and ind['patient_count']==4 and ind['full_domain_saved_count_records_matched']==72
    assert len(qual['metadata_negative_checks'])==13 and all(r['rejected'] for r in qual['metadata_negative_checks'])
    assert not qual['head_fitting_readiness'] and not qual['original_task_capability_gate_passed'] and not qual['complete_full_action_costs_available']
    assert ind['patient_first_delta_Q']==-0.003757069161363086
    for doc in (qual,ind):
        for b in doc['source_bindings']+doc.get('output_bindings',[]):
            p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256'],b
    source=read(READING/'primary_attempt01/receipt.json');render=read(READING/'visual_attempt01/receipt.json')
    assert source['complete'] and render['complete'];papers=[]
    full={'task_adapted':list(range(1,6))+list(range(13,29)),'tuning_free':list(range(1,9))}
    visual={'task_adapted':[17,20,22,24,26],'tuning_free':[4,5,6,7]}
    for row in source['records']:
        name=row['key'];allpages=list(range(1,row['physical_pages']+1));pages=full[name]
        texts=[r for r in row['page_texts'] if r['physical_page'] in pages]
        assert len(texts)==len(pages)
        for r in texts:assert sha(ROOT/r['path'])==r['sha256']
        v=[r for r in render['records'] if r['paper']==name]
        assert sorted(r['physical_page'] for r in v)==visual[name]
        papers.append(dict(key=name,title=row['indexed_record']['title'],authors=row['indexed_record']['authors'],
            identifier=row['indexed_record']['id'],PDF_source=row['file'],physical_pages=row['physical_pages'],
            complete_text_pages_actually_read=pages,complete_text_page_count=len(pages),
            page_text_bindings=texts,visual_pages_actually_reviewed=visual[name],visual_page_bindings=v,
            pages_not_read_in_full=[n for n in allpages if n not in pages],supplemental_separately_obtained=False))
    rp=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(READING/'PROTOCOL.md'),entry(READING/'PRIMARY_READING.md'),
            entry(READING/'INDEX_SCREEN.md'),entry(READING/'primary_attempt01/receipt.json'),entry(READING/'visual_attempt01/receipt.json')],
        papers=papers,new_independent_primary_papers_read=2,new_full_text_pages_read=sum(len(v) for v in full.values()),
        visual_pages_reviewed=sum(len(v) for v in visual.values()),all_extracted_pages=45,extraction_is_not_reading=True,
        complete_text_counts_exclude_repeated_pages=True,
        notes=['Task-adapted physical1-5/13-28 fully displayed;6-12/29-33 not read in full.',
            'Tuning-free physical1-8 fully displayed; initial combined output lost63tokens within p5, later full p5 reread, counted once.',
            'Tuning-free p9-12 first5lines only; reference pages not counted as complete reading.',
            'Local rg excerpt output was truncated; search snippets not counted as full-page reading.',
            'Task paper C direction conflict confirmed visually on17/20/22/24; not silently repaired.',
            'All nine rendered pages reviewed with actual view_image outputs; render receipt initial flags remain unchanged.'],
        index_records_returned=12,index_records_fully_read_as_primary_papers=2,
        expanded_TFPnP_not_counted_as_independent_primary_reading=True,
        author_code_or_MRI_reproduction_executed=False,new_medical_arrays_loaded=0,new_neural_forwards=0,
        new_GPU_forwards=0,new_training_updates=0,publication_claim_confirmed=False,goal_status='active')
    assert rp['new_full_text_pages_read']==29 and rp['visual_pages_reviewed']==9
    new(READING/'READING_PROVENANCE.json',rp)
    gpu=subprocess.run(['nvidia-smi','--query-gpu=timestamp,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader'],
        capture_output=True,text=True,timeout=15)
    assert gpu.returncode==0
    livepath=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/invocation02.json'
    payload=livepath.read_bytes();live=json.loads(payload)
    arms=[dict(kind=a.get('kind'),updates_completed=a.get('updates_completed'),complete=a.get('complete'),
        latest_committed_checkpoint=a.get('latest_committed_checkpoint'),keys_if_updates_missing=list(a) if 'updates_completed' not in a else [])
        for a in live.get('arms',[])]
    roots=[]
    for name,expected in [('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        p=PROJECT/name;assert sha(p)==expected;roots.append(dict(path=str(p),sha256=sha(p),previous_sha256=expected))
    observations=dict(observed_utc=datetime.now(timezone.utc).isoformat(),training_session_id=99542,
        observed_training_terminal_exit=None,original_training_process_modified=False,
        metadata_only_training_snapshot=True,live_file_excluded_from_frozen_sources=True,
        live_read_bytes_sha256=hashlib.sha256(payload).hexdigest(),live_status=live.get('status'),live_complete=live.get('complete'),
        live_errors=live.get('errors'),live_arms=arms,
        new_cpu_backbone_updates=live.get('new_cpu_backbone_updates'),actual_gpu_updates=live.get('actual_gpu_updates'),
        gpu_query_exit=gpu.returncode,gpu_csv=gpu.stdout.strip(),workspace_free_bytes=shutil.disk_usage(ROOT).free,
        disk_reserve_bytes=8_000_000_000,new_GPU_job_launched=False,
        gpu_authorization_retained=True,root_files_observed=roots,other_processes_enumerated=False,other_processes_modified=False)
    new(HERE/'TRAINING_RESOURCE_OBSERVATION.json',observations)
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md'),entry(HERE/'RESULT.md'),entry(HERE/'POSTFIT_EXECUTION_BRIDGE.md'),
            entry(HERE/'VISIBLE_DIALOGUE.md'),entry(HERE/'USER_PROVIDED_HANDOFF.md'),entry(HERE/'qualification_attempt01/receipt.json'),
            entry(HERE/'independent_attempt01/receipt.json'),entry(HERE/'TRAINING_RESOURCE_OBSERVATION.json'),entry(READING/'READING_PROVENANCE.json')],
        qualification_exits_from_user_handoff=[dict(chunk='47d1dd',exit_code=0,job='qualify_saved_real_pairs',rerun_in_this_continuation=False),
            dict(chunk='43b141',exit_code=0,job='verify_saved_real_pairs',rerun_in_this_continuation=False)],
        actual_continuation_tool_exits=[dict(chunk='c3a1cc',exit_code=1,job='index_attempt01',reason='Windows schannel SEC_E_NO_CREDENTIALS'),
            dict(chunk='1e905b',exit_code=1,job='index_attempt02',reason='default network connection refused'),
            dict(chunk='1f923e',exit_code=0,job='index_attempt03',public_GET_escalation_approved=True),
            dict(chunk='49385e',exit_code=0,job='two_primary_PDFs_and_extraction',public_GET_escalation_approved=True),
            dict(chunk='b086a5',exit_code=0,job='render_nine_pages')],
        actual_live_polls=[dict(chunk='1b279f',session_id=99542,terminal_exit=None,kind='raw_pchip',updates=297,new_updates=20097,cumulative_wall_seconds=46169.2732544),
            dict(chunk='559af1',session_id=99542,terminal_exit=None,kind='raw_pchip',updates=396,new_updates=20196,cumulative_wall_seconds=46395.38747449999)],
        ancillary_read_failures_retained=['Get-Item absent AGENTS paths produced exit1/no content; no applicable AGENTS found at root or innovation.',
            'First broad rg encountered access-denied retained tool tmp directories; later searches excluded innovation/tools.',
            'PowerShell wildcard passed literally to rg caused path syntax exit1; fixed by rg directory with -g, no file mutated.',
            'Get-PSDrive provider did not yield usable Free; real free bytes measured via shutil.disk_usage, no zero-disk claim.'],
        paired_real_archived_series=9,paired_real_archived_patients=4,paired_real_archived_action_outcomes=18,
        independent_original_full_domain_count_records=72,metadata_negative_checks_actually_executed=13,
        negative_branches_independently_reexecuted=False,patient_first_delta_Q=ind['patient_first_delta_Q'],
        original_weak_task_capability_gate_passed=False,full_action_costs_available=False,new_final_action_labels_generated=0,
        head_fitting_readiness=False,new_independent_primary_papers_read=2,new_full_text_pages_read=29,visual_pages_reviewed=9,
        medical_arrays_loaded=0,prediction_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        training_updates=0,head_fits=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        original56FOV_evaluation_launched=False,original_live_training_not_modified=True,new_agents_delegated=0,
        automatic_approval_review_rejections_received=0,root_files_observed=roots,
        actual_new_MRI_task_benefit_measured=False,publication_claim_confirmed=False,goal_status='active')
    new(HERE/'EXECUTION_LEDGER.json',ledger)
    print(json.dumps(dict(complete=True,paired_real_archived_series=9,paired_real_archived_patients=4,patient_first_delta_Q=ind['patient_first_delta_Q'],
        new_independent_primary_papers_read=2,new_full_text_pages_read=29,visual_pages_reviewed=9,
        training_observation=observations,elapsed_seconds=time.perf_counter()-tick),ensure_ascii=False),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
