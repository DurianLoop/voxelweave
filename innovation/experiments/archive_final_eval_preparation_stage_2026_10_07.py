"""Freeze executable preparation and all failures; keep ongoing training outside the archive."""
import ctypes,hashlib,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'literature/final_eval_preparation_stage_manifest_2026-10-07.json'
RECEIPT=ROOT/'SESSION_ARCHIVE_VERIFICATION_FINAL_EVAL_PREPARATION_2026-10-07.json'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def new(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not MANIFEST.exists() and not RECEIPT.exists()
    kernel=ctypes.windll.kernel32;kernel.GetCurrentProcess.restype=ctypes.c_void_p
    kernel.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong];assert kernel.SetPriorityClass(kernel.GetCurrentProcess(),0x4000)
    previous=ROOT/'literature/common_init_segment99_checkpoint_manifest_2026-10-07.json';prior=read(previous)
    receiptpath=ROOT/'SESSION_CHECKPOINT_RECEIPT_19SERIES_COMMON_INIT_2026-10-07.json';old=read(receiptpath)
    assert prior['complete'] and old['complete'] and old['immutable_checkpoint_archive_observed_tool_exit']==0
    assert old['manifest_sha256']==sha(previous) and old['archive_sha256']==sha(ROOT/old['archive_file'])
    for r in prior['evidence_files']:assert sha(ROOT/r['path'])==r['sha256'],'Prior frozen evidence changed: '+r['path']
    protected={r['path'] for r in prior['evidence_files']}
    stage=set(ROOT.glob('*FINAL_EVAL*2026-10-07.md'))|set(ROOT.glob('*FINAL_EVAL*2026-10-07.json'))
    stage|=set(ROOT.glob('*THICKSLICE_AVAILABILITY*2026-10-07.json'))
    stage.update(ROOT/p for p in ('SESSION_HANDOFF_19SERIES_COMMON_INIT_LIVE_2026-10-07.md',
        'MC_RC_3D_19SERIES_COMMON_INIT_FINAL_EVALUATION_EXECUTION_PROTOCOL_2026-10-07.md'))
    for pat in ('*final_eval*2026_10_07.py','*common_init_final*2026_10_07.py','*final_evaluation*2026_10_07.py',
                '*final*2026_10_07.py.failed_float64*','mc_rc_final_eval*2026_10_07.json'):
        stage|=set((ROOT/'experiments').glob(pat))
    stage|=set((ROOT/'literature').glob('*recent_thickslice*2026_10_07.py'))
    stage|=set((ROOT/'literature').glob('2026-10-07_recent_thickslice*.md'))
    for name in ('mc_rc_3d_19series_final_evaluation_preflight_2026_10_07','mc_rc_3d_19series_final_evaluation_preflight_attempt02_2026_10_07'):
        stage|={p for p in (ROOT/'experiments'/name).rglob('*') if p.is_file()}
    for name in ('recent_thickslice_primary_availability_2026-10-07','recent_thickslice_primary_availability_attempt02_2026-10-07'):
        stage|={p for p in (ROOT/'literature/source_cache'/name).rglob('*') if p.is_file()}
    stage|={Path(__file__),receiptpath}
    stage={p for p in stage if p.relative_to(ROOT).as_posix() not in protected and p not in (MANIFEST,RECEIPT)}
    assert sum(p.stat().st_size for p in stage)<=250000000
    proofpath=ROOT/'experiments/mc_rc_3d_19series_final_evaluation_preflight_attempt02_2026_10_07/attempt01.json'
    p=read(proofpath);ex=read(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_FINAL_EVAL_PREFLIGHT_2026-10-07.json')
    overlap=read(ROOT/'experiments/mc_rc_final_eval_overlap_synthetic_2026_10_07.json')
    oe=read(ROOT/'SESSION_OBSERVED_EXITS_FINAL_EVAL_OVERLAP_SYNTHETIC_2026-10-07.json')
    assert p['complete'] and not p['errors'] and overlap['complete'] and not overlap['errors']
    assert ex['preflight_observed_tool_exit']==oe['overlap_observed_tool_exit']==0 and ex['preflight_result_sha256']==sha(proofpath)
    assert p['actual_readiness_probe']['exit_code']==3 and p['real_MRI_or_GT_pixel_arrays_loaded']==0
    assert p['planned_total56_tiles']==3016 and p['two_arm_56_packed_bytes']==115491840
    assert not (ROOT/'experiments/mc_rc_3d_19series_common_init_final_eval_2026_10_07_attempt01').exists()
    progress=read(ROOT/'SESSION_EXECUTION_PROGRESS_FINAL_EVAL_PREPARATION_2026-10-07.json')
    assert progress['own_live_runs']==[99542] and progress['active_tool_exit'] is None
    evidence={ROOT/r['path'] for r in prior['evidence_files']}|stage|{previous,ROOT/old['archive_file']}
    links=[];bindings=[]
    for path in sorted(stage):
        if path.suffix=='.json':
            d=read(path)
            for b in d.get('source_bindings',[]):
                target=ROOT/b['path'];assert target.is_file() and target.is_relative_to(ROOT) and sha(target)==b['sha256']
                evidence.add(target);bindings.append(dict(document=path.relative_to(ROOT).as_posix(),**b))
        elif path.suffix=='.md':
            for url in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                url=url.strip('<>')
                if re.match(r'https?://|app://',url):continue
                target=(path.parent/url.split('#',1)[0]).resolve();assert target.exists() and target.is_relative_to(ROOT)
                links.append(dict(document=path.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
                if target.is_file():evidence.add(target)
    assert not any(p.name in ('invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt',
        'native_reference_history.jsonl','raw_pchip_history.jsonl') for p in evidence)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        stage_files=[entry(p) for p in sorted(stage)],evidence_files=[entry(p) for p in sorted(evidence)],
        stage_bytes=sum(p.stat().st_size for p in stage),local_links=links,source_bindings_verified=bindings,
        previous_frozen_evidence_files_verified=len(prior['evidence_files']),prior_manifest_sha256=sha(previous),
        new_primary_papers_read=0,new_abstracts_read=0,DOI_metadata_records_checked=3,real_MRI_final_effects_scored=False,
        new_training_updates_in_preparation_scripts=0,new_GPU_updates=0,expected_failures_preserved=True,
        own_live_runs_at_checkpoint=[99542],final_execution_closed=False,full_training_exit=None,
        scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    new(MANIFEST,r)
    for row in read(MANIFEST)['evidence_files']:assert sha(ROOT/row['path'])==row['sha256']
    d=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        manifest_file=MANIFEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(MANIFEST),stage_files=len(r['stage_files']),
        evidence_files=len(r['evidence_files']),stage_bytes=r['stage_bytes'],previous_frozen_evidence_files_verified=len(prior['evidence_files']),
        own_live_runs_at_checkpoint=[99542],final_execution_closed=False,full_training_exit=None,goal_status='active',publication_claim_confirmed=False)
    new(RECEIPT,d);print(json.dumps({k:d[k] for k in ('complete','stage_files','evidence_files','stage_bytes','previous_frozen_evidence_files_verified','own_live_runs_at_checkpoint')}))
    return 0
if __name__=='__main__':raise SystemExit(main())
