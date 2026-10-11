"""Archive only immutable short-segment evidence while full training remains explicitly live."""
import ctypes,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
MANIFEST=ROOT/'literature/common_init_segment99_checkpoint_manifest_2026-10-07.json'
RECEIPT=ROOT/'SESSION_ARCHIVE_VERIFICATION_19SERIES_COMMON_INIT_CHECKPOINT_2026-10-07.json'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,value):
    with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not MANIFEST.exists() and not RECEIPT.exists()
    kernel=ctypes.windll.kernel32;kernel.GetCurrentProcess.restype=ctypes.c_void_p
    kernel.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
    assert kernel.SetPriorityClass(kernel.GetCurrentProcess(),0x4000)
    previous=ROOT/'literature/low_lr_context_stage_manifest_2026-10-07.json';prior=read(previous)
    closepath=ROOT/'SESSION_CLOSING_RECEIPT_LOW_LR_CONTEXT_2026-10-07.json';close=read(closepath)
    assert prior['complete'] and close['complete'] and close['archive_observed_tool_exit']==0
    assert close['manifest_sha256']==sha(previous) and close['archive_sha256']==sha(ROOT/close['archive_file'])
    for row in prior['evidence_files']:assert sha(ROOT/row['path'])==row['sha256'],'Prior frozen evidence changed: '+row['path']
    q=read(OUT/'invocation01.json');p=read(OUT/'independent_segment99_attempt01.json')
    ex=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_SEGMENT99_2026-10-07.json')
    ve=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_SEGMENT99_VERIFIER_2026-10-07.json')
    assert q['complete'] and p['complete'] and not q['errors'] and not p['errors'] and p['all198_batches_verified']
    assert ex['training_observed_tool_exit']==ve['verifier_observed_tool_exit']==0
    assert ex['training_result_sha256']==sha(OUT/'invocation01.json') and ve['verifier_result_sha256']==sha(OUT/'independent_segment99_attempt01.json')
    progress=read(ROOT/'SESSION_EXECUTION_PROGRESS_19SERIES_COMMON_INIT_2026-10-07.json')
    assert progress['own_live_runs']==[99542] and progress['active_tool_exit'] is None and not progress['formal_final_budget_completed']
    stage=set(ROOT.glob('*COMMON_INIT*2026-10-07*.md'))|set(ROOT.glob('*COMMON_INIT*2026-10-07*.json'))
    stage|=set((ROOT/'experiments').glob('*common_init*2026_10_07.py'))
    names=['common_random_initial.pt','synthetic_resume_after6.pt','frozen_schedule.npy','frozen_config.json','preflight_attempt01.json',
        'invocation01.json','native_reference_segment99.pt','native_reference_segment99_history.jsonl',
        'raw_pchip_segment99.pt','raw_pchip_segment99_history.jsonl','independent_segment99_attempt01.json']
    stage.update(OUT/n for n in names);stage.add(closepath)
    protected={r['path'] for r in prior['evidence_files']}
    stage={s for s in stage if s.relative_to(ROOT).as_posix() not in protected and s not in (MANIFEST,RECEIPT)}
    assert all(s.exists() for s in stage) and sum(s.stat().st_size for s in stage)<=250000000
    assert not any(s.name.endswith('_resume.pt') or s.name=='invocation02.json' or s.name.endswith('_history.jsonl') and '_segment99_' not in s.name for s in stage)
    evidence={ROOT/r['path'] for r in prior['evidence_files']}|stage|{previous,ROOT/close['archive_file']}
    links=[];bindings=[]
    for path in sorted(stage):
        if path.suffix=='.json':
            d=read(path)
            for b in d.get('source_bindings',[]):
                s=ROOT/b['path'];assert s.is_relative_to(ROOT) and s.is_file() and sha(s)==b['sha256']
                evidence.add(s);bindings.append(dict(document=path.relative_to(ROOT).as_posix(),**b))
        elif path.suffix=='.md':
            for url in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                url=url.strip('<>')
                if re.match(r'https?://|app://',url):continue
                s=(path.parent/url.split('#',1)[0]).resolve();assert s.exists() and s.is_relative_to(ROOT)
                links.append(dict(document=path.relative_to(ROOT).as_posix(),target=s.relative_to(ROOT).as_posix()))
                if s.is_file():evidence.add(s)
    # Mutable training checkpoint/history and live result are excluded even if a future link is added.
    assert not any(s==OUT/'invocation02.json' or s.name in ('native_reference_resume.pt','raw_pchip_resume.pt',
        'native_reference_history.jsonl','raw_pchip_history.jsonl') for s in evidence)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        archive_scope='Immutable segment99 and preparation only; ongoing full training is not archived or declared terminal.',
        prior_manifest_sha256=sha(previous),previous_frozen_evidence_files_verified=len(prior['evidence_files']),
        stage_files=[entry(s) for s in sorted(stage)],evidence_files=[entry(s) for s in sorted(evidence)],
        stage_bytes=sum(s.stat().st_size for s in stage),local_links=links,source_bindings_verified=bindings,
        immutable_formal_updates_verified=198,planned_formal_updates=39996,formal_final_budget_completed=False,
        own_live_runs_at_checkpoint=[99542],full_training_exit=None,final_execution_closed=False,
        new_gpu_updates=0,scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    new(MANIFEST,r)
    for row in read(MANIFEST)['evidence_files']:assert sha(ROOT/row['path'])==row['sha256']
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        scope=r['archive_scope'],manifest_file=MANIFEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(MANIFEST),
        stage_files=len(r['stage_files']),evidence_files=len(r['evidence_files']),stage_bytes=r['stage_bytes'],
        previous_frozen_evidence_files_verified=len(prior['evidence_files']),own_live_runs_at_checkpoint=[99542],
        final_execution_closed=False,full_training_exit=None,publication_claim_confirmed=False,goal_status='active')
    new(RECEIPT,receipt)
    print(json.dumps({k:receipt[k] for k in ('complete','stage_files','evidence_files','stage_bytes','previous_frozen_evidence_files_verified','own_live_runs_at_checkpoint')}))
    return 0
if __name__=='__main__':raise SystemExit(main())
