"""Exact auditable relocation of the cohort harness to the independently qualified faster oracle."""
from pathlib import Path
import json,difflib,hashlib,ast
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'certified_resolution_rounding_2026_10_09'
old=BASE/'qualify_all_patient_stress.py';new=HERE/'qualify_all_patient_stress.py';assert not new.exists()
before=old.read_text(encoding='utf-8');after=before
changes={
    'import torch\nimport certified_resolution as candidate':'import torch\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent/\'certified_resolution_rounding_2026_10_09\'))\nimport certified_resolution as candidate',
    'import direct_interval_reference as direct':'import direct_separable_reference as direct',
    'HERE=Path(__file__).resolve().parent;ROOT=HERE.parent':'HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;BASE=ROOT/\'certified_resolution_rounding_2026_10_09\'',
    "v['workspace_free_bytes']-2_000_000-3_000_000-2_800_000":"v['workspace_free_bytes']-15_800_000",
    "HERE/'certified_resolution.py'":"BASE/'certified_resolution.py'",
    "HERE/'direct_interval_reference.py'":"HERE/'direct_separable_reference.py',BASE/'direct_interval_reference.py',HERE/'qualification_attempt01/receipt.json',BASE/'all_patient_terminal_audit_attempt01/receipt.json'",
    "HERE/'exact_tensor_reference.py'":"BASE/'exact_tensor_reference.py'",
    "for p in [HERE/'synthetic_attempt01/receipt.json',HERE/'direct_oracle_synthetic_attempt01/receipt.json',HERE/'failed_full_field_regression_attempt01/receipt.json']:":"for p in [BASE/'synthetic_attempt01/receipt.json',BASE/'direct_oracle_synthetic_attempt01/receipt.json',BASE/'failed_full_field_regression_attempt01/receipt.json',HERE/'qualification_attempt01/receipt.json',BASE/'all_patient_terminal_audit_attempt01/receipt.json']:",
    "before=guard();out=HERE/'all_patient_stress_attempt01';out.mkdir(exist_ok=False)":"before=guard();terminal=read(BASE/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json');assert terminal['exit_code']==0 and 'session_id' not in terminal\n    newer=read(HERE/'ACTUAL_EFFICIENCY_TERMINAL_TOOL.json');assert newer['exit_code']==0 and 'session_id' not in newer\n    out=HERE/'all_patient_stress_attempt01';out.mkdir(exist_ok=False)"
}
for a,b in changes.items():assert after.count(a)==1,(a,after.count(a));after=after.replace(a,b)
ast.parse(after)
with new.open('x',encoding='utf-8') as f:f.write(after)
with (HERE/'ALL_PATIENT_HARNESS_DIFF.patch').open('x',encoding='utf-8') as f:f.writelines(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=str(old),tofile=str(new)))
with (HERE/'HARNESS_PREPARATION.json').open('x',encoding='utf-8') as f:json.dump(dict(complete=True,errors=[],original_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),new_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),
    exact_replacements=len(changes),syntax_parsed=True,runner_executed=False,training_ready=False,source_original_unmodified=True),f,indent=2)
