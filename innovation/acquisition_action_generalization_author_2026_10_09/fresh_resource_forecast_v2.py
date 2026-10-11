"""Fresh family admission includes the new1MB GPU diagnostic without reducing earlier allowances."""
import sys,time,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard
started=time.perf_counter();res=resource_guard();old=read(HERE/'fresh_forecast_attempt01/receipt.json')
assert old['complete'] and old['current_total_required_above_reserve_bytes']==77_156_359
required=old['current_total_required_above_reserve_bytes']+1_000_000
query=subprocess.run(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=20)
gpu=[list(map(int,line.split(','))) for line in query.stdout.strip().splitlines()];assert len(gpu)==1 and gpu[0][0]==0
available=res['workspace_free_bytes']-8_000_000_000
r=dict(complete=True,errors=[],forecast_only=True,original_family_and_three_stage_allowances_bytes=77_156_359,
    added_GPU_graph_stage_allowance_bytes=1_000_000,current_total_required_above_reserve_bytes=required,
    available_above_reserve_bytes=available,shortfall_bytes=max(0,required-available),disk_admitted=available>=required,
    GPU_free_MiB=gpu[0][1],GPU_utilization_percent=gpu[0][2],GPU_admitted=gpu[0][1]>=8192,
    complete_training_family_admitted=False,full35904_qualification_passed=False,training_ready=False,new_training_launched=False,
    sources=[entry(p) for p in [Path(__file__),HERE/'fresh_forecast_attempt01/receipt.json',ROOT/'gpu_graph_cost_smoke_2026_10_09/terminal_audit_attempt01/receipt.json']],
    resources=res,elapsed_seconds=time.perf_counter()-started,publication_claim_confirmed=False,goal_status='active')
out=HERE/'fresh_forecast_attempt02';out.mkdir(exist_ok=False);dump(out/'receipt.json',r);print(json.dumps(r))
