"""Generate a new guarded runner without modifying the frozen v1 source."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,dump,resource_guard
resource_guard()
old=HERE/'run_six_resolution_training.py';text=old.read_text(encoding='utf-8')
index=read(ROOT/'action_oracle_and_prior_art_2026_10_09/APPEND_INDEX.json')
binding=next(b for b in index['new_evidence_files'] if b['path']==old.relative_to(ROOT).as_posix())
assert sha(old)==binding['sha256'] and old.stat().st_size==binding['bytes']
replacements={
 'OTHER_BYTES=18_800_000':'OTHER_BYTES=42_800_000',
 "entry(HERE/'PROTOCOL.md')":"entry(HERE/'V2_PROTOCOL.md'),entry(HERE/'PROTOCOL.md'),entry(HERE/'prepare_runner_v2.py'),entry(HERE/'run_six_resolution_training.py')",
 "FULL_GPU_DEPLOYMENT_QUALIFICATION.json":"FULL_GPU_DEPLOYMENT_QUALIFICATION_V2.json",
 "out=HERE/'preflight_attempt01'":"out=HERE/'preflight_v2_attempt01'",
 "out=HERE/'training_attempt01'":"out=HERE/'training_v2_attempt01'"
}
for before,after in replacements.items():
 assert before in text,before
 text=text.replace(before,after)
needle="    deployment=HERE/'FULL_GPU_DEPLOYMENT_QUALIFICATION_V2.json'"
addition="""    coverage=ROOT/'development_optimizer_coverage_2026_10_09'
    flags['all19_optimizer_actual_terminal']=terminal(coverage/'ACTUAL_COVERAGE_TERMINAL_TOOL.json',78758)
    flags['all19_optimizer_independent_terminal_audit']=flags['all19_optimizer_actual_terminal'] and completed(
        coverage/'terminal_audit_attempt01/receipt.json',['all228_unique_updates_and456_patch_fields_verified',
        'all19_series11_patients_and114_branch_denominators_verified',
        'all_optimizer_step1_step2_parameter_moment_and_memory_capture_records_verified'])
"""
assert needle in text;text=text.replace(needle,addition+needle)
text=text.replace('"""Guarded prospective six-arm runner; default preflight loads no medical/model arrays."""',
 '"""New v2: latest104,156,359-byte family and all19 optimizer admission; v1 remains immutable."""')
import ast;ast.parse(text)
target=HERE/'run_six_resolution_training_v2.py'
with target.open('x',encoding='utf-8') as f:f.write(text)
out=HERE/'runner_v2_preparation_attempt01';out.mkdir(exist_ok=False)
dump(out/'receipt.json',dict(complete=True,errors=[],source_bindings=[entry(p) for p in [Path(__file__),old,HERE/'V2_PROTOCOL.md']],
 new_runner=entry(target),original_runner_modified=False,latest_complete_family_required_bytes=104_156_359,
 new_training_launched=False,medical_arrays_loaded=0,publication_claim_confirmed=False))
print('New runner v2 created; old source preserved; no CUDA or medical arrays loaded.')
