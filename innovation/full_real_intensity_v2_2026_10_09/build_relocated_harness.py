"""Build explicit new full-scope harnesses; old script bytes and running sources stay unchanged."""
import ast,sys,json,difflib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OLD=ROOT/'resolution_degradation_controls_2026_10_08'
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import sha,entry,dump,resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    source=OLD/'qualify_full_real_pipeline.py';assert sha(source)=='b27c5ed516fca0a4cb9e5cc194b7987cc1ffc51689e518d63780203d3671e403'
    text=source.read_text(encoding='utf-8');replacements=[]
    def replace(before,after,count=1):
        nonlocal text
        assert text.count(before)==count,(before,text.count(before));text=text.replace(before,after);replacements.append(dict(old=before,new=after,occurrences=count))
    replace('HERE=Path(__file__).resolve().parent;ROOT=HERE.parent','HERE=Path(__file__).resolve().parent;ROOT=HERE.parent\nOLD=ROOT/\'resolution_degradation_controls_2026_10_08\'\nREPAIR=ROOT/\'intensity_precision_failure_diagnosis_2026_10_09\'')
    replace("sys.path.insert(0,str(ROOT/'adaptation_paired_pilot_2026_10_08'))\nimport augmentation as intensity","sys.path.insert(0,str(OLD))\nsys.path.insert(0,str(REPAIR))\nimport intensity_float64_stats as intensity")
    replace("terminal=read(HERE/name)","terminal=read(OLD/name)")
    for name in ['resolution_control.py','independent_resolution.py','independent_intensity.py','qualify_synthetic_and_schedule_v2.py']:
        replace("HERE/'"+name+"'","OLD/'"+name+"'")
    replace('sources.update(HERE/name for name in','sources.update(OLD/name for name in')
    replace('p=HERE/name;q=read(p)','p=OLD/name;q=read(p)')
    replace('assert read(HERE/prerequisites[-1])','assert read(OLD/prerequisites[-1])')
    replace('>=1_800_000','>=4_800_000')
    replace('<5_000_000','<2_000_000',2)
    replace('stage_limit_bytes=5_000_000','stage_limit_bytes=2_000_000')
    hook="""    repaired_terminal=REPAIR/'ACTUAL_REPAIRED_STRESS_TERMINAL_TOOL.json'
    repaired_observation=read(repaired_terminal)
    assert repaired_observation['exit_code']==0 and 'session_id' not in repaired_observation
    assert repaired_observation['observed_unified_exec_session']==47298
    repaired_path=REPAIR/'repaired_stress_attempt01/receipt.json';repaired=read(repaired_path)
    assert repaired['complete'] and repaired['status']=='completed' and not repaired['errors']
    assert repaired['all40_synthetic228_real3_failed_regressions_verified']
    assert repaired['all11_patients19_series_two_inputs_three_modes_verified']
    assert len(repaired['fields'])==271 and repaired['MRI_input_arrays_loaded']==38
    for b in repaired['source_bindings']:bind(b)
    assert sha(OLD/'independent_intensity.py')=='11f3946b80d7c687acb03fedc607881b6813a2982290e9588431ad96cc63c81e'
    assert sha(OLD/'qualify_full_real_pipeline.py')=='b27c5ed516fca0a4cb9e5cc194b7987cc1ffc51689e518d63780203d3671e403'
    failed_terminal=OLD/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json';failed=read(failed_terminal)
    assert failed['exit_code']==1 and 'session_id' not in failed and failed['observed_unified_exec_session']==74234
    sources.update([repaired_terminal,repaired_path,REPAIR/'repaired_stress_attempt01/frozen_config.json',
        Path(intensity.legacy.__file__),Path(__file__).parent/'build_relocated_harness.py',
        failed_terminal,OLD/'full_real_pipeline_attempt01/receipt.json',OLD/'full_real_pipeline_attempt01/frozen_config.json',
        OLD/'qualify_full_real_pipeline.py'])
"""
    replace("    previous=ROOT/'real_context_and_author_code_followup_2026_10_08'",hook+"    previous=ROOT/'real_context_and_author_code_followup_2026_10_08'")
    replace("shared_numpy_seeded_normal_convention=True,","shared_numpy_seeded_normal_convention=True,\n           production_gamma_statistics_float64=True,old_reference_unchanged=True,\n           previous_failed_session=74234,original_failed_fields_completed=6216,")
    old_loop=source.read_text(encoding='utf-8').split("        with journal.open('xb')",1)[1].split('    except Exception as exc:',1)[0]
    new_loop=text.split("        with journal.open('xb')",1)[1].split('    except Exception as exc:',1)[0]
    assert new_loop==old_loop,'Inherited full-field loop changed'
    ast.parse(text);target=HERE/'qualify_full_real_pipeline.py';assert not target.exists()
    with target.open('x',encoding='utf-8') as f:f.write(text)
    delta=''.join(difflib.unified_diff(source.read_text(encoding='utf-8').splitlines(keepends=True),text.splitlines(keepends=True),fromfile='frozen_legacy_full',tofile='new_full_v2'))
    with (HERE/'EXACT_HARNESS_DIFF.patch').open('x',encoding='utf-8') as f:f.write(delta)
    original_audit=OLD/'audit_full_real_terminal.py';audit=original_audit.read_text(encoding='utf-8')
    audit=audit.replace('HERE=Path(__file__).resolve().parent;ROOT=HERE.parent','HERE=Path(__file__).resolve().parent;ROOT=HERE.parent\nOLD=ROOT/\'resolution_degradation_controls_2026_10_08\'')
    audit=audit.replace("terminal['observed_unified_exec_session']==74234","terminal['observed_unified_exec_session']==read(HERE/'ACTUAL_FULL_REAL_PIPELINE_SESSION.json')['actual_unified_exec_session']")
    audit=audit.replace("metapath=HERE/'geometry_and_synthetic_attempt01/receipt.json'","metapath=OLD/'geometry_and_synthetic_attempt01/receipt.json'")
    audit=audit.replace("HERE/'FULL_REAL_TERMINAL_AUDIT_PROTOCOL.md'","HERE/'FULL_REAL_PIPELINE_PROTOCOL.md'")
    audit=audit.replace("receiptpath,configpath,journal,oldpath,original,metapath,controlpath]","receiptpath,configpath,journal,oldpath,original,metapath,controlpath,HERE/'ACTUAL_FULL_REAL_PIPELINE_SESSION.json']")
    audit=audit.replace('<5_000_000','<2_000_000');ast.parse(audit)
    with (HERE/'audit_full_real_terminal.py').open('x',encoding='utf-8') as f:f.write(audit)
    assert sha(source)=='b27c5ed516fca0a4cb9e5cc194b7987cc1ffc51689e518d63780203d3671e403'
    receipt=dict(complete=True,errors=[],old_source_unchanged=True,new_harness_parses=True,new_audit_parses=True,
        inherited_field_loop_unchanged=True,expected_fields=35904,repaired_prerequisite_session=47298,
        full_pipeline_executed=False,MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        training_updates=0,new_patient_medical_effects=0,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[entry(p) for p in [Path(__file__),source,original_audit,HERE/'FULL_REAL_PIPELINE_PROTOCOL.md',target,
            HERE/'EXACT_HARNESS_DIFF.patch',HERE/'audit_full_real_terminal.py']],replacement_records=replacements)
    dump(HERE/'HARNESS_PREPARATION.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['source_bindings','replacement_records']}),flush=True)
if __name__=='__main__':main()
