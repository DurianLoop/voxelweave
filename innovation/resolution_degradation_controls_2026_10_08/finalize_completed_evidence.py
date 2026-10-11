"""Write completed-stage provenance; never freezes the live full-MRI or training outputs."""
import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard


def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    pairs=[('geometry_and_synthetic_attempt01/receipt.json','ACTUAL_GEOMETRY_AND_SYNTHETIC_TERMINAL_TOOL.json'),
           ('real_stress_attempt01/receipt.json','ACTUAL_REAL_STRESS_TERMINAL_TOOL.json'),
           ('intensity_composition_attempt01/receipt.json','ACTUAL_INTENSITY_COMPOSITION_TERMINAL_TOOL.json'),
           ('independent_intensity_attempt01/receipt.json','ACTUAL_INDEPENDENT_INTENSITY_TERMINAL_TOOL.json')]
    completed=[];sources={Path(__file__),HERE/'README.md',HERE/'RESULTS.md',
        HERE/'RESEARCH_DECISIONS_AND_NEXT_STEPS.md',HERE/'VISIBLE_DIALOGUE_TURN28.md',
        HERE/'RECEIVED_HANDOFF_FACTS_TURN28.md',HERE/'ACTUAL_TOOL_OBSERVATIONS_PART01.json',
        HERE/'ACTUAL_TOOL_OBSERVATIONS_PART02.json',HERE/'full_real_pipeline_attempt01/frozen_config.json'}
    for rname,tname in pairs:
        receiptpath=HERE/rname;terminalpath=HERE/tname;r=read(receiptpath);t=read(terminalpath)
        assert r['complete'] and not r['errors']
        assert t['exit_code']==0 and 'session_id' not in t
        for b in r['source_bindings']:bind(b)
        sources.update([receiptpath,terminalpath])
        completed.append(dict(receipt=entry(receiptpath),actual_terminal=entry(terminalpath),
            actual_terminal_chunk=t['chunk_id'],observed_tool_exit=0,
            result_scalars={k:v for k,v in r.items() if isinstance(v,(int,float,bool,str))}))
    notes=[ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/PRIMARY_READING_AND_PROJECT_DECISIONS.md',
           ROOT/'real_context_and_author_code_followup_2026_10_08/AUTHOR_TRAINING_CHAIN_FINDINGS.md',
           ROOT/'augmentation_primary_followup_2026_10_08/QC_AND_ACTION_NEXT_TRIAL_PREPARATION.md',
           ROOT/'tumor_qc_strength_followup_2026_10_08/STRONG_QC_AND_ACTION_PREPARATION.md']
    sources.update(notes)
    roots=[]
    for name,expected in [('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        p=ROOT.parent/name;assert sha(p)==expected
        roots.append(dict(path='../'+name,bytes=p.stat().st_size,sha256=expected))
    result=dict(complete=True,errors=[],completed_checks=completed,root_file_bindings=roots,
        new_distinct_primary_maintexts_completed=0,new_author_source_lines_not_double_counted=0,
        existing_author_source_lines_from_prior_stage=4132,author_code_executed=False,
        existing_reading_notes_rechecked=[entry(p) for p in notes],
        actual_stage_completed_real_MRI_loads=76,actual_stage_completed_GT_loads=38,
        unique_development_series=19,unique_development_patients=11,
        repeated_stress_loads_not_independent_scans=True,
        full35904_pipeline_session=74234,full35904_actual_terminal_not_yet_observed=True,
        full35904_rolling_outputs_excluded=True,original_four_arm_session=29823,
        original_training_actual_terminal_not_yet_observed=True,
        training_ready=False,new_patient_neural_forwards=0,new_training_updates=0,
        new_patient_medical_effects=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),
        source_bindings=[entry(p) for p in sorted(sources)])
    dump(HERE/'READING_PROVENANCE.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['completed_checks','existing_reading_notes_rechecked','source_bindings','root_file_bindings']},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
