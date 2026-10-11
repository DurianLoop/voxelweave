"""Fresh aggregate forecast from frozen six-arm plan and actual current resources, no tensors."""
import sys,json,time,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,entry,read,dump

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=resource_guard()
    path=ROOT/'resource_recovery_and_generalization_controls_2026_10_09/full_forecast_attempt01/receipt.json';old=read(path);assert old['complete']
    gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=20,check=True)
    free,util=map(int,gpu.stdout.strip().split(','));disk_available=before['workspace_free_bytes']-8_000_000_000
    # Keep the original complete-family forecast and allowances; additional stages have allowances too.
    unchanged=old['total_required_above_8GB_reserve_bytes'];additional=dict(new_author_stage_bytes=2_000_000,new_recovery_stage_bytes=2_000_000,new_faster_oracle_stage_bytes=2_000_000)
    required=unchanged+sum(additional.values());out=HERE/'fresh_forecast_attempt01';out.mkdir(exist_ok=False)
    result=dict(complete=True,errors=[],forecast_only=True,components=old['components'],original_other_allowances=old['other_existing_allowances'],
        original_complete_family_required_bytes=unchanged,additional_stage_allowances=additional,current_total_required_above_reserve_bytes=required,
        observed_available_above_8GB_reserve_bytes=disk_available,forecast_shortfall_bytes=max(0,required-disk_available),disk_admission_passed=disk_available>=required,
        GPU_free_MiB=free,GPU_utilization_percent=util,GPU_minimum_free_MiB=8192,GPU_admission_passed=free>=8192,
        full35904_qualification_passed=False,six_branch_training_runner_verified=False,training_ready=False,new_training_launched=False,
        MRI_or_model_arrays_loaded=0,confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(Path(__file__)),entry(path),entry(ROOT/'frozen_text_resource_recovery_v2_2026_10_09/compression_attempt01/receipt.json')],
        resources_before=before,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(out/'receipt.json',result);print(json.dumps({k:v for k,v in result.items() if k!='source_bindings'},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
