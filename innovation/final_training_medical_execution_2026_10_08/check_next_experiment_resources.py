"""Read-only resource forecast for prepared trials; never launches training or initializes CUDA."""
import hashlib,json,sys,subprocess
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');res=resource_guard()
    p=subprocess.run(['nvidia-smi','--query-gpu=index,memory.total,memory.used,memory.free','--format=csv,noheader,nounits'],
        capture_output=True,text=True,timeout=20,check=True)
    gpu=[dict(zip(['index','total_MiB','used_MiB','free_MiB'],map(int,line.split(',')))) for line in p.stdout.strip().splitlines()]
    margin=res['workspace_free_bytes']-8_000_000_000
    trials=[dict(name='same_capacity_paired_augmentation_short_pilot',forecast_saved_bytes=20_000_000,
        disk_forecast_fits=margin>=20_000_000,medical_capability_would_be_established=False),
        dict(name='STU_Net_S_transfer_same_architecture_scratch_control',published_parameters=14_600_000,
        two_FP32_weight_payload_forecast_bytes=116_800_000,disk_weight_forecast_fits=margin>=116_800_000,
        forecast_excludes_download_metadata_optimizer_resume_history=True,actual_checkpoint_size_not_measured=True),
        dict(name='Genesis_transfer_same_architecture_scratch_control',published_parameters=16_320_000,
        two_FP32_weight_payload_forecast_bytes=130_560_000,disk_weight_forecast_fits=margin>=130_560_000,
        forecast_excludes_download_metadata_optimizer_resume_history=True,actual_checkpoint_size_not_measured=True)]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],resources=res,GPU=gpu,
        GPU_authorization_present=True,GPU_start_free_MiB_gate=8192,GPU_free_start_gate_passed=any(x['free_MiB']>=8192 for x in gpu),
        second_GPU_interface_not_queried_when_first_start_gate_fails=True,CUDA_initialized=False,
        disk_above_reserve_bytes=margin,trials=trials,training_started=False,medical_arrays_loaded=0,GT_arrays_loaded=0,
        model_checkpoint_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,other_PIDs_enumerated=False,other_PIDs_modified=False,
        publication_claim_confirmed=False,goal_status='active')
    dest=HERE/'NEXT_EXPERIMENT_RESOURCE_READINESS.json'
    with dest.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(r,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
