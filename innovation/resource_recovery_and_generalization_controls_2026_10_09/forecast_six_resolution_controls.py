"""Forecast complete six-branch storage from finished metadata and file sizes, without tensors."""
import json
import subprocess
import sys
import time
from pathlib import Path
from inventory_frozen_text_storage import ROOT,HERE,entry,sha,dump,guard


def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resources=guard(started)
    stage=ROOT/'spatial_adaptation_matched_2026_10_08'
    terminalpath=stage/'ACTUAL_TRAINING_TERMINAL_TOOL.json'
    receiptpath=stage/'training_attempt01/receipt.json'
    terminal=json.loads(terminalpath.read_text(encoding='utf-8'))
    fit=json.loads(receiptpath.read_text(encoding='utf-8'))
    assert terminal['exit_code']==0 and 'session_id' not in terminal
    assert fit['complete'] and fit['status']=='completed' and not fit['errors'] and len(fit['arms'])==4
    files=[];checkpoints=[];histories=[]
    for arm in fit['arms']:
        assert arm['complete'] and arm['updates_completed']==2992
        paths=[(arm['checkpoint_path'],arm['checkpoint_sha256']),(arm['history_path'],arm['history_sha256'])]
        records=[]
        for path,digest in paths:
            file=ROOT/path;assert file.is_file() and sha(file)==digest
            row=entry(file);records.append(row);files.append(row)
        checkpoints.append(records[0]['bytes']);histories.append(records[1]['bytes'])
    gpu=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free','--format=csv,noheader,nounits'],
                       capture_output=True,text=True,timeout=20,check=True)
    gpurows=[dict(zip(['index','free_MiB'],map(int,line.split(',')))) for line in gpu.stdout.strip().splitlines()]
    assert len(gpurows)==1 and gpurows[0]['index']==0
    components=dict(six_final_weight_files_bytes=6*max(checkpoints),one_atomic_weight_temp_bytes=max(checkpoints),
        six_gzip_journals_allowance_bytes=max(12_000_000,6*max(histories)),
        training_metadata_allowance_bytes=3_000_000,evaluation_output_allowance_bytes=5_000_000,
        cost_qualification_allowance_bytes=1_000_000,terminal_audit_archive_allowance_bytes=1_000_000)
    other=dict(resource_stage_allowance_bytes=2_000_000,live_full_qualification_allowance_bytes=2_000_000,
               original_medical_allowance_bytes=3_000_000,completed_development_allowance_bytes=2_800_000)
    total=sum(components.values());required=total+sum(other.values())
    available=guard(started)['workspace_free_bytes']-8_000_000_000
    result=dict(complete=True,errors=[],forecast_only=True,
        branches=[kind+'_'+mode for kind in ['native_reference','raw_pchip'] for mode in ['throughplane','inplane','allaxes']],
        updates_per_branch=2992,completed_checkpoint_bytes=checkpoints,completed_gzip_history_bytes=histories,
        components=components,six_branch_forecast_bytes=total,other_existing_allowances=other,
        total_required_above_8GB_reserve_bytes=required,observed_available_above_reserve_bytes=available,
        forecast_shortfall_bytes=max(0,required-available),disk_admission_passed=available>=required,
        GPU_observations=gpurows,GPU_minimum_free_MiB=8192,GPU_admission_passed=gpurows[0]['free_MiB']>=8192,
        full35904_actual_terminal_and_independent_audit_observed=False,full_training_and_inference_cost_measured=False,
        six_branch_runner_verified=False,training_ready=False,new_training_launched=False,
        strict_LOPO_or_reliability_map_QC_gain_costs_included=False,
        checkpoint_or_MRI_arrays_loaded=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        new_medical_effects=0,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(Path(__file__)),entry(HERE/'FORECAST_PROTOCOL.md'),entry(terminalpath),entry(receiptpath)]+files,
        resources_before=resources,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
    out=HERE/'full_forecast_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings']},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
