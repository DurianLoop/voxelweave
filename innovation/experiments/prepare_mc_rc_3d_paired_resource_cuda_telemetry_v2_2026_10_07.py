"""Derive a new entry, preserving the executed original byte-for-byte."""
import ast,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'experiments/run_mc_rc_3d_paired_real_resource_2026_10_07.py'
NEW=ROOT/'experiments/run_mc_rc_3d_paired_real_resource_v2_2026_10_07.py'
AMEND=ROOT/'MC_RC_3D_PAIRED_RESOURCE_CUDA_TELEMETRY_AMENDMENT_2026-10-07.md'
OUT=ROOT/'experiments/mc_rc_3d_paired_resource_cuda_telemetry_v2_preparation_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not NEW.exists();OUT.mkdir(exist_ok=False)
    oldsha=sha(BASE);snap=ROOT/'experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07/run_mc_rc_3d_paired_real_resource_2026_10_07.py.source_snapshot'
    assert sha(snap)==oldsha
    source=BASE.read_text(encoding='utf-8')
    old="out=ROOT/('experiments/mc_rc_3d_paired_real_resource_2026_10_07_'+args.device+'_attempt'+args.attempt)"
    new="out=ROOT/('experiments/mc_rc_3d_paired_real_resource_v2_2026_10_07_'+args.device+'_attempt'+args.attempt)"
    assert source.count(old)==1;source=source.replace(old,new)
    old="    save()\n    try:\n        readiness="
    new="    r['CUDA_telemetry_amendment_sha256']=sha(ROOT/'MC_RC_3D_PAIRED_RESOURCE_CUDA_TELEMETRY_AMENDMENT_2026-10-07.md')\n    r['entry_version']=2\n    save()\n    try:\n        readiness="
    assert source.count(old)==1;source=source.replace(old,new)
    old="    finally:\n        r['finished_utc']="
    new="""    finally:
        # Observes only this process, including failed GPU attempts; never initializes CUDA.
        try:
            own_torch=sys.modules.get('torch')
            r['CUDA_initialized']=bool(own_torch.cuda.is_initialized()) if own_torch is not None else False
            r['CUDA_initialization_observation_valid']=True
            r['CUDA_observation_stage']='finally_after_success_defer_or_error'
        except Exception as observation_error:
            r['CUDA_initialized']=None;r['CUDA_initialization_observation_valid']=False
            r['CUDA_observation_error']=f'{type(observation_error).__name__}: {observation_error}'
        r['finished_utc']="""
    assert source.count(old)==1;source=source.replace(old,new);ast.parse(source)
    with NEW.open('x',encoding='utf-8',newline='\n') as s:s.write(source)
    assert sha(BASE)==oldsha
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        original_file=BASE.relative_to(ROOT).as_posix(),original_sha256=oldsha,
        new_entry_file=NEW.relative_to(ROOT).as_posix(),new_entry_sha256=sha(NEW),
        amendment_sha256=sha(AMEND),original_executed_source_preserved=True,syntax_parse_passed=True,
        intended_changes=['new_output_directory','version_and_amendment_binding','finally_CUDA_observation'],
        real_GPU_training_not_run=True,GPU_exception_path_execution_not_claimed=True,MRI_reads=0)
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as s:json.dump(r,s,indent=2);s.write('\n')
    print(json.dumps(dict(complete=True,original_executed_source_preserved=True,syntax_parse_passed=True)));return 0
if __name__=='__main__':raise SystemExit(main())
