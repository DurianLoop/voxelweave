"""Metadata and in-memory compilation only; never imports evaluation or reads live journal/checkpoint."""
import ast,hashlib,json,sys,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_guard()
    files=[HERE/n for n in ['capture_training_terminal.py','evaluate_matched.py','capture_evaluation_terminal.py','summarize_matched.py','check_prepared_entry.py']]
    for p in files:compile(p.read_text(encoding='utf-8'),str(p),'exec')
    fit=json.loads((HERE/'training_attempt01/receipt.json').read_text(encoding='utf-8'))
    frozen=HERE/'training_attempt01/frozen_config.json';assert sha(frozen)=='cf0056b44bb0f353f59c7f25a4a9663b6eb5e3bd02455675cb0daff1158c6299'
    cfg=json.loads(frozen.read_text(encoding='utf-8'));assert cfg['steps_per_branch']==2992 and cfg['stage_save_bound_bytes']==45_000_000
    expected=['native_reference_intensity','native_reference_spatial','raw_pchip_intensity','raw_pchip_spatial'];assert cfg['branches']==expected
    for b in cfg['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    assert not (HERE/'evaluation_attempt01').exists(),'Use a new qualification receipt if evaluation has already run'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],all_five_entry_files_compile=True,
        prepared_for_branches=expected,prepared_updates_per_branch=2992,frozen_training_config_verified=True,
        evaluation_can_run_now=(HERE/'ACTUAL_TRAINING_EXIT.json').exists() and fit.get('complete',False),
        pending_reason='Requires actual managed-tool exit0 and full terminal four-branch checkpoint/journal audit',
        training_metadata_snapshot=dict(status=fit['status'],complete=fit['complete'],arms=[dict(name=a['name'],updates_observed=a['updates_completed'],complete=a['complete']) for a in fit['arms']]),
        live_receipt_or_journal_hash_frozen=False,model_arrays_loaded=0,medical_arrays_loaded=0,GT_arrays_loaded=0,neural_forwards=0,
        CUDA_initialized=False,evaluation_launched=False,resources=resources,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in files+[HERE/'EVALUATION_PROTOCOL.md',frozen]])
    with (HERE/'ENTRY_PREPARATION_CHECK.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r),flush=True)
if __name__=='__main__':main()
