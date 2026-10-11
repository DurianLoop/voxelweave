"""Generate v3 entry copies; retain all executed v2 artifacts and their actual forecasts."""
import ast,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
resource_guard();sources=[Path(__file__),HERE/'V3_PROTOCOL.md',HERE/'V2_PROTOCOL.md']
def copy(source,target,replacements):
 text=source.read_text(encoding='utf-8');before=entry(source)
 for old,new in replacements:
  assert old in text,old
  text=text.replace(old,new)
 ast.parse(text)
 with target.open('x',encoding='utf-8') as f:f.write(text)
 assert entry(source)==before;sources.append(source);return entry(target)
runner=copy(HERE/'run_six_resolution_training_v2.py',HERE/'run_six_resolution_training_v3.py',[
 ("entry(HERE/'V2_PROTOCOL.md')","entry(HERE/'V3_PROTOCOL.md'),entry(HERE/'V2_PROTOCOL.md'),entry(HERE/'prepare_v3_entries.py')"),
 ("FULL_GPU_DEPLOYMENT_QUALIFICATION_V2.json","FULL_GPU_DEPLOYMENT_QUALIFICATION_V3.json"),
 ("assert d['admitted_training_wall_seconds']>=d['complete_family_wall_forecast_seconds']",
  "assert d['admitted_training_wall_seconds']>0 and d['complete_family_wall_forecast_seconds']>=d['admitted_training_wall_seconds']"),
 ("preflight_v2_attempt01","preflight_v3_attempt01"),("training_v2_attempt01","training_v3_attempt01")])
builder=copy(HERE/'build_deployment_qualification_v2.py',HERE/'build_deployment_qualification_v3.py',[
 ("entry(HERE/'V2_PROTOCOL.md')","entry(HERE/'V3_PROTOCOL.md'),entry(HERE/'V2_PROTOCOL.md'),entry(HERE/'prepare_v3_entries.py')"),
 ("def ended(path,session):","def ended(path,session):\n if session is None:return False"),
 ("report=dict(complete=True,errors=[],forecast_only=not args.qualify", "report=dict(complete=True,errors=[],forecast_only=not args.qualify"),
 (" flags=dict(full35904_actual_exit0", " startpath=FOV/'ACTUAL_FULL_FOV_V2_START_TOOL.json'\n session=read(startpath).get('session_id') if startpath.exists() else None\n if startpath.exists():sources.append(startpath)\n flags=dict(full35904_actual_exit0"),
 ("ACTUAL_FULL_FOV_TERMINAL_TOOL.json","ACTUAL_FULL_FOV_V2_TERMINAL_TOOL.json"),
 ("',74453)","',session)"),
 ("terminal_audit_attempt01/receipt.json","terminal_audit_v2_attempt01/receipt.json"),
 ("COVER/'terminal_audit_v2_attempt01/receipt.json'","COVER/'terminal_audit_attempt01/receipt.json'"),
 ("full_fov_attempt01/receipt.json","full_fov_v2_attempt01/receipt.json"),
 ("FULL_GPU_DEPLOYMENT_QUALIFICATION_V2.json","FULL_GPU_DEPLOYMENT_QUALIFICATION_V3.json"),
 ("all19_cost_forecast_v2_attempt01","all19_cost_forecast_v3_attempt01")])
out=HERE/'v3_entries_preparation_attempt01';out.mkdir(exist_ok=False)
dump(out/'receipt.json',dict(complete=True,errors=[],new_runner=runner,new_builder=builder,
 source_bindings=[entry(p) for p in sources],previous_executed_files_modified=False,
 new_training_launched=False,MRI_or_GT_or_model_arrays_loaded=0,publication_claim_confirmed=False))
print('v3 AST parsed; prior entries preserved; training/family walls and prospective FOV session separated.')
