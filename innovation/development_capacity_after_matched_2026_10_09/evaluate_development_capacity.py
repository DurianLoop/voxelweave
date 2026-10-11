"""All19 development series, all four last2992 states; no new fit or validation data loading."""
import sys,json,time,gc,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;MATCHED=ROOT/'spatial_adaptation_matched_2026_10_08'
sys.path.insert(0,str(ROOT/'lossless_final_evaluation_entry_2026_10_08'))
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import final_eval_lossless_v3 as g
import verify_final_lossless_v3 as independent
from production_probability_mapping_v4 import infer_full_fov_v4
torch,np=g.torch,g.np
OUT=HERE/'evaluation_attempt01';MAX_BYTES=3_000_000;ALLOWANCE=2_800_000;NAMES=['native_reference_intensity','native_reference_spatial','raw_pchip_intensity','raw_pchip_spatial']
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(4);started=time.perf_counter();res=g.resource_guard()
    assert res['workspace_free_bytes']-ALLOWANCE-2_000_000-3_000_000>=8_000_000_000
    tex=g.read(MATCHED/'ACTUAL_TRAINING_EXIT.json');fit=g.read(MATCHED/'training_attempt01/receipt.json')
    mex=g.read(MATCHED/'ACTUAL_EVALUATION_EXIT.json');med=g.read(MATCHED/'evaluation_attempt01/receipt.json')
    term=g.read(MATCHED/'ACTUAL_EVALUATION_TERMINAL_TOOL.json')
    assert tex['observed_tool_exit']==0 and tex['observed_tool_session']==29823 and tex['all11968_history_rows_verified'] and tex['all2992_paired_steps_verified']
    assert tex['result_sha256']==g.sha(MATCHED/'training_attempt01/receipt.json') and fit['complete'] and not fit['errors']
    assert mex['observed_tool_exit']==0 and mex['observed_tool_session']==78123 and mex['all36_strict_numeric_gates_passed']
    assert mex['result_sha256']==g.sha(MATCHED/'evaluation_attempt01/receipt.json') and med['complete'] and not med['errors']
    assert all(not all(a['validation_gates'].values()) for a in med['arms'])
    assert term['exit_code']==0 and 'session_id' not in term and term['observed_unified_exec_session']==78123
    assert [a['name'] for a in fit['arms']]==NAMES and fit['new_cpu_updates']==11968 and fit['new_GPU_updates']==0
    sources={Path(__file__),HERE/'PROTOCOL.md',MATCHED/'ACTUAL_TRAINING_EXIT.json',MATCHED/'training_attempt01/receipt.json',
        MATCHED/'ACTUAL_EVALUATION_EXIT.json',MATCHED/'evaluation_attempt01/receipt.json',MATCHED/'ACTUAL_EVALUATION_TERMINAL_TOOL.json',
        MATCHED/'FINAL_MATCHED_COMPARISON.json',Path(g.__file__),Path(independent.__file__),ROOT/'final_training_medical_execution_2026_10_08/production_probability_mapping_v4.py'}
    for b in tex['source_bindings']+fit['source_bindings']+med['source_bindings']:
        p=ROOT/b['path'];assert g.sha(p)==b['sha256'];sources.add(p)
    cases=[(role,c,row) for role,c,row in g.roles() if role=='development']
    assert len(cases)==19 and {c['patient'] for role,c,row in cases}==g.DEVELOPERS and len(g.DEVELOPERS)==11
    assert {c['patient'] for role,c,row in cases}.isdisjoint(g.VALIDATORS)
    OUT.mkdir(exist_ok=False)
    config=dict(steps_per_branch=2992,branch_names=NAMES,development_patient_ids=sorted(g.DEVELOPERS),
        cases=[dict(patient=c['patient'],uid=c['uid'],role=role) for role,c,row in cases],expected_FOVs=76,expected_independent_FOVs=76,
        threshold=.5,probability_atol=3e-6,coordinate_atol=3e-12,binary_disagreement_allowance=0,CPU_threads=4,interop_threads=1,
        wall_seconds=5400,output_bytes=ALLOWANCE,stage_max_bytes=MAX_BYTES,no_training_or_checkpoint_selection=True,
        protocol_sha256=g.sha(HERE/'PROTOCOL.md'),runner_sha256=g.sha(Path(__file__)))
    g.dump_new(OUT/'frozen_config.json',config);sources.add(OUT/'frozen_config.json')
    initial=[dict(path=p.relative_to(ROOT).as_posix(),sha256=g.sha(p)) for p in sorted(sources)]
    receipt=OUT/'receipt.json';r=dict(created_utc=g.now(),complete=False,errors=[],arms=[],numeric_failures=[],expected_FOVs=76,
        expected_development_patients=11,expected_development_series=19,training_updates=0,GPU_updates=0,
        validation_image_or_GT_arrays_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        threshold=.5,intermediate_checkpoint_selection=False,publication_claim_confirmed=False,goal_status='active',
        inference_contract='original V4 full FOV, CPU FP32 neural / float64 coordinates',independent_cross_process_reexecution=False,
        initial_source_bindings=initial,frozen_config_sha256=g.sha(OUT/'frozen_config.json'))
    g.dump_new(receipt,r);before=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    def save():g.atomic_json(receipt,r)
    def check():
        assert time.perf_counter()-started<5400;res=g.resource_guard()
        assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
        size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());assert size<MAX_BYTES and size-before<ALLOWANCE
        assert res['workspace_free_bytes']-2_000_000-3_000_000>=8_000_000_000
        res.update(cpu_threads=4,stage_saved_bytes=size);return res
    try:
        r['resources_before']=check();save()
        for a in fit['arms']:
            check();assert a['complete'] and a['updates_completed']==2992
            path=ROOT/a['checkpoint_path'];assert g.sha(path)==a['checkpoint_sha256'];sources.add(path)
            cp=torch.load(path,map_location='cpu',weights_only=True);assert g.state_hash(cp['state_dict'])==a['final_weights_sha256'] and cp['updates']==2992
            model=g.TaskUNet3D();model.load_state_dict(cp['state_dict']);model.eval();wrapped=g.GuardedModel(model,check)
            arm=dict(name=a['name'],kind=a['kind'],augmentation=a['augmentation'],complete=False,series=[]);r['arms'].append(arm);save()
            for i,(role,c,row) in enumerate(cases):
                check();image,stats=g.source_image(c,row,a['kind']);grid=g.lattice(c);image=g.physical_mr(image,grid)
                probability,meta=infer_full_fov_v4(wrapped,image,grid,c['native_shape'])
                replay,imeta=independent.functional_fov(cp['state_dict'],image,grid,c['native_shape'],check)
                error=float(np.max(np.abs(probability-replay)));binary=int(np.count_nonzero((probability>=.5)!=(replay>=.5)))
                strict=error<=3e-6 and binary==0 and imeta['float64_coordinate_gate_passed']
                assert meta['total_tiles']==imeta['total_tiles'] and meta['axis_starts']==imeta['axis_starts']
                pred=probability>=.5;predfile=OUT/(a['name']+'_'+str(i).zfill(2)+'.npz');g.pack_prediction(predfile,pred)
                assert np.array_equal(g.unpack_prediction(predfile),pred)
                gt=g.read_reference_label(c);metrics=g.metrics(pred,gt);counts=independent.independent_counts(pred,gt);assert independent.trees_close(metrics,counts)
                record=dict(patient=c['patient'],uid=c['uid'],role=role,metrics=metrics,physical_input_sha256=g.array_sha(image),
                    probability_sha256=g.array_sha(probability),label_sha256=g.array_sha(gt),production_inference=meta,independent_inference=imeta,
                    strict_gate_passed=strict,max_probability_error=error,binary_disagreements=binary,
                    prediction_file=predfile.relative_to(ROOT).as_posix(),prediction_file_sha256=g.sha(predfile))
                if not strict:r['numeric_failures'].append(dict(branch=a['name'],uid=c['uid'],max_probability_error=error,binary=binary))
                arm['series'].append(record);sources.add(predfile);save()
                print(json.dumps(dict(branch=a['name'],series_done=len(arm['series']),expected_series=19,strict_gate_passed=strict)),flush=True)
                del image,probability,replay,pred,gt;gc.collect();check()
            agg=g.aggregate(arm['series'],g.DEVELOPERS);iagg=independent.independent_aggregate(arm['series'],g.DEVELOPERS);assert independent.trees_close(agg,iagg)
            arm.update(complete=True,development_aggregate=iagg)
            assert g.state_hash(model.state_dict())==a['final_weights_sha256'];del model,wrapped,cp;gc.collect();save()
        for b in initial:assert g.sha(ROOT/b['path'])==b['sha256']
        assert sum(len(a['series']) for a in r['arms'])==76 and len(r['arms'])==4
        r.update(complete=True,all76_strict_numeric_gates_passed=not r['numeric_failures'],source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=g.sha(p)) for p in sorted(sources)],resources_after=check())
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(finished_utc=g.now(),elapsed_seconds=time.perf_counter()-started);save()
    print(json.dumps({k:r.get(k) for k in ['complete','errors','all76_strict_numeric_gates_passed','elapsed_seconds']}),flush=True)
    return int(not r['complete'] or bool(r['errors']) or not r.get('all76_strict_numeric_gates_passed',False))
if __name__=='__main__':raise SystemExit(main())
