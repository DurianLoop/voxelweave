"""Freeze terminal-source metadata only after the supplied actual tool exit0."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=client.resource_guard()
    observed=read(HERE/'ACTUAL_TRAINING_TERMINAL_TOOL.json')
    tool=observed['actual_terminal_tool_result'];assert tool['exit_code']==0
    train=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07'
    qp=train/'invocation02.json';q=read(qp);cfgp=train/'frozen_config.json';cfg=read(cfgp)
    assert q['complete'] and q['status']=='completed_segment' and not q['errors']
    assert q['formal_final_budget_completed'] and q['all_last_weights_frozen']
    assert q['total_formal_updates_so_far']==39996 and q['new_cpu_backbone_updates']==39798 and q['stop_after']==19998
    assert q['paired_GT_and_augmentation_identical'] and q['both_last_checkpoints_frozen_utc']
    assert not q['task_effects_scored'] and not q['cuda_initialized']
    assert sha(cfgp)==q['frozen_config_sha256'] and cfg['planned_updates_per_arm']==19998
    oldp=train/'invocation01.json';assert read(oldp)['new_cpu_backbone_updates']==198
    files=[qp,cfgp,oldp,train/cfg['schedule_file'],ROOT/cfg['protocol_file']]
    assert sha(train/cfg['schedule_file'])==cfg['schedule_file_sha256']
    assert sha(ROOT/cfg['protocol_file'])==cfg['protocol_sha256']
    for b in cfg['source_bindings']:
        p=ROOT/b['path'];assert sha(p)==b['sha256'];files.append(p)
    arms=[]
    assert len(q['arms'])==2
    for kind in ('native_reference','raw_pchip'):
        a=next(x for x in q['arms'] if x['kind']==kind)
        assert a['updates_completed']==19998 and a['complete']
        cp=ROOT/a['final_checkpoint_file'];assert cp.name==kind+'_last19998.pt'
        assert sha(cp)==a['final_checkpoint_sha256']
        hist=train/(kind+'_history.jsonl');resume=train/(kind+'_resume.pt')
        assert hist.is_file() and resume.is_file()
        with hist.open(encoding='utf-8') as f:lines=sum(bool(line.strip()) for line in f)
        assert lines==19998;files.extend((cp,hist,resume))
        arms.append(dict(kind=kind,updates_completed=19998,checkpoint_path=cp.relative_to(ROOT).as_posix(),
            checkpoint_sha256=sha(cp),history_rows=lines,history_sha256=sha(hist),resume_sha256=sha(resume)))
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),training_observed_tool_exit=tool['exit_code'],
        observed_tool_chunk_id=tool['chunk_id'],observed_tool_session_id=99542,
        training_result_file=qp.relative_to(ROOT).as_posix(),training_result_sha256=sha(qp),
        formal_training_updates=q['total_formal_updates_so_far'],both_last19998_frozen=True,
        arms=arms,training_sources=[client.base.entry(p) for p in sorted(set(files))],
        actual_terminal_tool_observation=client.base.entry(HERE/'ACTUAL_TRAINING_TERMINAL_TOOL.json'),
        full_tensor_optimizer_schedule_and_paired_history_validation_pending_in_production_frozen_training=True,
        resource_snapshot=resources,medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,
        original_training_modified=False,publication_claim_confirmed=False,goal_status='active')
    dest=ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json'
    client.base.new(dest,receipt)
    print(json.dumps(dict(complete=True,receipt=client.base.entry(dest),arms=arms,
        formal_training_updates=receipt['formal_training_updates'],resources=resources),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
