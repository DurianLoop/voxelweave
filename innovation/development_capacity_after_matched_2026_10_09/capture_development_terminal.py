"""Require real terminal then independently recount completed case/metric provenance."""
import sys,time,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'lossless_final_evaluation_entry_2026_10_08'))
import final_eval_lossless_v3 as g
import verify_final_lossless_v3 as independent
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();g.resource_guard()
    termpath=HERE/'ACTUAL_DEVELOPMENT_EVALUATION_TERMINAL_TOOL.json';term=g.read(termpath);session=g.read(HERE/'ACTUAL_DEVELOPMENT_EVALUATION_SESSION.json')
    assert term['exit_code']==0 and 'session_id' not in term and term['observed_unified_exec_session']==session['actual_unified_exec_session']==12652
    p=HERE/'evaluation_attempt01/receipt.json';r=g.read(p);configpath=HERE/'evaluation_attempt01/frozen_config.json';config=g.read(configpath)
    assert r['complete'] and not r['errors'] and r['all76_strict_numeric_gates_passed'] and r['frozen_config_sha256']==g.sha(configpath)
    assert r['training_updates']==0 and r['GPU_updates']==0 and r['threshold']==config['threshold']==.5
    assert r['expected_FOVs']==config['expected_FOVs']==76 and r['expected_development_series']==19 and r['expected_development_patients']==11
    assert not r['validation_image_or_GT_arrays_loaded'] and not r['confirmation_patients_opened'] and not r['lockedIXI_opened']
    expected={(v['patient'],v['uid']) for v in config['cases']};assert len(expected)==19 and {v['patient'] for v in config['cases']}==g.DEVELOPERS
    assert [a['name'] for a in r['arms']]==config['branch_names'] and len(r['arms'])==4
    for b in r['source_bindings']:assert g.sha(ROOT/b['path'])==b['sha256']
    for a in r['arms']:
        assert a['complete'] and len(a['series'])==19 and {(v['patient'],v['uid']) for v in a['series']}==expected
        assert all(v['role']=='development' and v['strict_gate_passed'] and v['max_probability_error']<=3e-6 and v['binary_disagreements']==0 and v['independent_inference']['float64_coordinate_gate_passed'] for v in a['series'])
        agg=independent.independent_aggregate(a['series'],g.DEVELOPERS);assert independent.trees_close(agg,a['development_aggregate'])
        for v in a['series']:assert g.sha(ROOT/v['prediction_file'])==v['prediction_file_sha256']
    out=dict(complete=True,errors=[],observed_tool_exit=0,observed_tool_session=12652,observed_tool_chunk=term['chunk_id'],
        result_file=p.relative_to(ROOT).as_posix(),result_sha256=g.sha(p),all76_complete_FOVs_and_exact_case_sets_verified=True,
        all11_patient_fraction_aggregates_verified=True,all76_strict_probability_coordinate_binary_gates_passed=True,
        model_arrays_loaded=0,GT_arrays_loaded=0,MRI_arrays_loaded=0,neural_forwards=0,new_training_updates=0,
        development_GT_seen_by_training=True,independent_patient_confirmation=False,independent_neural_reexecution_in_this_audit=False,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        elapsed_seconds=time.perf_counter()-started,source_bindings=[dict(path=v.relative_to(ROOT).as_posix(),sha256=g.sha(v)) for v in [Path(__file__),termpath,p,configpath,HERE/'PROTOCOL.md',Path(independent.__file__)]])
    g.dump_new(HERE/'ACTUAL_DEVELOPMENT_EVALUATION_EXIT.json',out);assert time.perf_counter()-started<60
    print(json.dumps({k:v for k,v in out.items() if k!='source_bindings'}),flush=True)
if __name__=='__main__':main()
