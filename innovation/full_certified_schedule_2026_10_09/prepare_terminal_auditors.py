"""Prepare independent ended-only auditors; do not execute or manufacture qualification."""
from pathlib import Path
import ast,json,hashlib,difflib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
jobs=[(ROOT/'certified_resolution_rounding_2026_10_09/audit_all_patient_terminal.py',ROOT/'direct_oracle_efficiency_2026_10_09/audit_all_patient_terminal.py',
    {"==43633":"==31883"}),
    (ROOT/'full_real_intensity_v2_2026_10_09/audit_full_real_terminal.py',HERE/'audit_full_real_terminal.py',
    {"assert v['binary_disagreements']==v['pre_intensity_padding_disagreements']==0":"assert v['binary_disagreements']==v['pre_intensity_padding_disagreements']==v['image_bitwise_disagreements']==0\n                assert 0<=v['candidate_exact_fallback_voxels']<=v['valid_voxels'] and 0<=v['reference_exact_fallback_voxels']<=v['valid_voxels']"})]
records=[]
for old,new,changes in jobs:
    assert not new.exists();before=old.read_text(encoding='utf-8');after=before
    for a,b in changes.items():assert after.count(a)==1,(a,after.count(a));after=after.replace(a,b)
    ast.parse(after)
    with new.open('x',encoding='utf-8') as f:f.write(after)
    records.append(dict(original_path=old.relative_to(ROOT).as_posix(),original_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),
        prepared_path=new.relative_to(ROOT).as_posix(),prepared_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),syntax_parsed=True,executed=False))
with (HERE/'AUDITOR_PREPARATION.json').open('x',encoding='utf-8') as f:json.dump(dict(complete=True,errors=[],auditors=records,qualification_passed=False,training_ready=False),f,indent=2)
