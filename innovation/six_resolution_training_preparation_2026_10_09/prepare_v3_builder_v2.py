"""Repair only the uncreated v3 builder; preserve the ended first preparation failure."""
import ast,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard
resource_guard();source=HERE/'build_deployment_qualification_v2.py';before=entry(source)
text=source.read_text(encoding='utf-8')
replacements=[
 ("HERE/'V2_PROTOCOL.md'","HERE/'V3_PROTOCOL.md',HERE/'V2_PROTOCOL.md',HERE/'prepare_v3_builder_v2.py'"),
 ("def ended(path,session):","def ended(path,session):\n if session is None:return False"),
 (" flags=dict(full35904_actual_exit0", " startpath=FOV/'ACTUAL_FULL_FOV_V2_START_TOOL.json'\n session=read(startpath).get('session_id') if startpath.exists() else None\n if startpath.exists():sources.append(startpath)\n flags=dict(full35904_actual_exit0"),
 ("ACTUAL_FULL_FOV_TERMINAL_TOOL.json","ACTUAL_FULL_FOV_V2_TERMINAL_TOOL.json"),
 ("',74453)","',session)"),
 ("FOV/'terminal_audit_attempt01/receipt.json'","FOV/'terminal_audit_v2_attempt01/receipt.json'"),
 ("full_fov_attempt01/receipt.json","full_fov_v2_attempt01/receipt.json"),
 ("FULL_GPU_DEPLOYMENT_QUALIFICATION_V2.json","FULL_GPU_DEPLOYMENT_QUALIFICATION_V3.json"),
 ("all19_cost_forecast_v2_attempt01","all19_cost_forecast_v3_attempt01")]
for old,new in replacements:
 assert old in text,old
 text=text.replace(old,new)
ast.parse(text);target=HERE/'build_deployment_qualification_v3.py'
with target.open('x',encoding='utf-8') as f:f.write(text)
assert entry(source)==before
out=HERE/'v3_entries_preparation_attempt02';out.mkdir(exist_ok=False)
dump(out/'receipt.json',dict(complete=True,errors=[],new_runner=entry(HERE/'run_six_resolution_training_v3.py'),
 new_builder=entry(target),source_bindings=[entry(p) for p in [Path(__file__),source,HERE/'V3_PROTOCOL.md',HERE/'prepare_v3_entries.py']],
 original_files_modified=False,earlier_prepare_exit1_preserved=True,new_training_launched=False,medical_arrays_loaded=0))
print('v3 builder created and AST parsed; original v2 and failed generation retained.')
