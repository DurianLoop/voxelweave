"""Fresh full-family forecast retains old80,156,359bytes and every new stage allowance."""
import sys,json,time,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard
def main():
    started=time.perf_counter();res=resource_guard()
    oldpath=ROOT/'six_resolution_training_preparation_2026_10_09/preflight_attempt01/receipt.json';old=read(oldpath)
    assert old['complete'] and old['required_above_reserve_bytes']==80_156_359
    added=dict(all19_optimizer_coverage_stage=2_000_000,full38_FOV_atomic_capture_stage=20_000_000,frozen_checkpoint_storage_stage=2_000_000)
    required=old['required_above_reserve_bytes']+sum(added.values());available=res['workspace_free_bytes']-8_000_000_000
    q=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
    gpu=[list(map(int,line.split(','))) for line in q.stdout.strip().splitlines()];assert len(gpu)==1 and gpu[0][0]==0
    def ended(path):
        if not path.exists():return False
        t=read(path);return t.get('exit_code')==0 and 'session_id' not in t
    flags=dict(disk_admitted=available>=required,GPU_aggregate_admitted=gpu[0][1]>=8192,
        full35904_actual_exit0=ended(ROOT/'full_certified_schedule_2026_10_09/ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json'),
        all19_optimizer_actual_exit0=ended(HERE/'ACTUAL_COVERAGE_TERMINAL_TOOL.json'),
        full38_FOV_actual_exit0=ended(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09/ACTUAL_FULL_FOV_TERMINAL_TOOL.json'))
    r=dict(complete=True,errors=[],forecast_only=True,previous_full_family_required_bytes=80_156_359,
        added_allowances=added,current_full_family_required_above_reserve_bytes=required,available_above_reserve_bytes=available,
        shortfall_bytes=max(0,required-available),current_flags=flags,GPU_aggregate=gpu,training_ready=False,new_training_launched=False,
        actual_checkpoint_API_storage_saved_bytes=read(ROOT/'frozen_checkpoint_storage_2026_10_09/compression_attempt01/receipt.json')['API_physical_bytes_saved'],
        original_allowances_or_reserve_reduced=False,MRI_or_GT_or_model_arrays_loaded=0,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(p) for p in [Path(__file__),oldpath,ROOT/'frozen_checkpoint_storage_2026_10_09/compression_attempt01/receipt.json']],resources=res,elapsed_seconds=time.perf_counter()-started)
    out=HERE/'fresh_forecast_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',r);print(json.dumps(r))
if __name__=='__main__':main()
