"""Auditable from-scratch relocation, keeping frozen failed harnesses untouched."""
from pathlib import Path
import ast,json,hashlib,difflib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
old=ROOT/'full_real_intensity_v2_2026_10_09/qualify_full_real_pipeline.py';new=HERE/'qualify_full_real_pipeline.py';assert not new.exists()
before=old.read_text(encoding='utf-8');after=before
changes={
    "sys.path.insert(0,str(REPAIR))":"sys.path.insert(0,str(REPAIR))\nsys.path.insert(0,str(ROOT/'certified_resolution_rounding_2026_10_09'))",
    'from resolution_control import apply,baseline_patch':'from resolution_control import baseline_patch\nfrom certified_resolution import apply',
    'from independent_resolution import independent_apply':'from direct_numeric_adapter import independent_apply',
    'PATCH=(64,128,128);WALL=32400;JOURNAL_LIMIT=1_500_000':'PATCH=(64,128,128);WALL=64800;JOURNAL_LIMIT=1_500_000',
    "'valid_voxels','changed_voxels','pre_intensity_padding_disagreements']":"'valid_voxels','changed_voxels','pre_intensity_padding_disagreements',\n         'image_bitwise_disagreements','candidate_exact_fallback_voxels','reference_exact_fallback_voxels']",
    "assert res['workspace_free_bytes']-8_000_000_000>=4_800_000":"assert res['workspace_free_bytes']-8_000_000_000>=15_800_000",
    "previous=ROOT/'real_context_and_author_code_followup_2026_10_08'":"certified=ROOT/'certified_resolution_rounding_2026_10_09';fast=ROOT/'direct_oracle_efficiency_2026_10_09'\n    for stage in [certified,fast]:\n        terminal=read(stage/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json');assert terminal['exit_code']==0 and 'session_id' not in terminal\n        audit=read(stage/'all_patient_terminal_audit_attempt01/receipt.json');assert audit['complete'] and audit['all542_unique_field_identities_verified']\n        receipt=read(stage/'all_patient_stress_attempt01/receipt.json');assert receipt['complete'] and receipt['all542_full_fields_verified']\n        for b in receipt['source_bindings']:bind(b)\n        sources.update([stage/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json',stage/'all_patient_terminal_audit_attempt01/receipt.json',stage/'all_patient_stress_attempt01/receipt.json'])\n    admission=read(HERE/'compute_admission_attempt01/receipt.json');assert admission['complete'] and admission['admitted']\n    for b in admission['source_bindings']:bind(b)\n    sources.update([HERE/'compute_admission_attempt01/receipt.json',HERE/'direct_numeric_adapter.py',HERE/'build_full_harness.py',certified/'certified_resolution.py',certified/'direct_interval_reference.py',certified/'exact_tensor_reference.py',fast/'direct_separable_reference.py'])\n    previous=ROOT/'real_context_and_author_code_followup_2026_10_08'",
    "Path(__file__).parent/'build_relocated_harness.py'":"Path(__file__).parent/'build_full_harness.py'",
    'production_gamma_statistics_float64=True,old_reference_unchanged=True':'production_gamma_statistics_float64=True,exactly_rounded_resolution_candidate=True,independent_collapsed_reference=True',
    'previous_failed_session=74234,original_failed_fields_completed=6216':'previous_failed_session=90446,original_failed_fields_completed=14673,failed_prefix_inherited=False',
    "padding=int(np.count_nonzero(image[~domain]!=base[pi,0][~domain]))":"padding=int(np.count_nonzero(image[~domain].view(np.uint32)!=base[pi,0][~domain].view(np.uint32)))",
    "padding+=int(np.count_nonzero(other[~domain]!=base[pi,0][~domain]))":"padding+=int(np.count_nonzero(other[~domain].view(np.uint32)!=base[pi,0][~domain].view(np.uint32)))",
    'assert binary==0 and padding==0':'bits=int(np.count_nonzero(image.view(np.uint32)!=other.view(np.uint32)))\n                                assert bits==0 and binary==0 and padding==0',
    'record.extend([binary,valid,changed,padding])':'record.extend([binary,valid,changed,padding,bits,meta[\'exact_fallback_voxels\'],imeta[\'direct_exact_fallback_voxels\']])',
    "if r['fields_completed']%24==0:":"if r['fields_completed']%120==0:"
}
for a,b in changes.items():assert after.count(a)==1,(a,after.count(a));after=after.replace(a,b)
ast.parse(after)
with new.open('x',encoding='utf-8') as f:f.write(after)
with (HERE/'EXACT_HARNESS_DIFF.patch').open('x',encoding='utf-8') as f:f.writelines(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=str(old),tofile=str(new)))
with (HERE/'HARNESS_PREPARATION.json').open('x',encoding='utf-8') as f:json.dump(dict(complete=True,errors=[],old_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),new_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),
    exact_replacements=len(changes),syntax_parsed=True,runner_executed=False,full35904_qualified=False,training_ready=False,original_frozen_sources_unmodified=True),f,indent=2)
