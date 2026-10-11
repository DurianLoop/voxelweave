"""Fixed final pilot weights, all 9 already-opened validation FOVs for each branch."""
import gc,json,sys,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'lossless_final_evaluation_entry_2026_10_08'))
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import final_eval_lossless_v3 as g
import verify_final_lossless_v3 as independent
from production_probability_mapping_v4 import infer_full_fov_v4
torch,np=g.torch,g.np;TRAIN=HERE/'attempt01';OUT=HERE/'evaluation_attempt01'

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(4);started=time.perf_counter()
    OUT.mkdir(exist_ok=False);dest=OUT/'receipt.json'
    r=dict(created_utc=g.now(),complete=False,errors=[],arms=[],numerical_failures=[],new_training_updates=0,
        new_GPU_updates=0,confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,
        goal_status='active',cross_process_independent_reexecution=False,development_series_scored_this_stage=0)
    def save():g.atomic_json(dest,r)
    def check():
        assert time.perf_counter()-started<=3600;res=g.resource_guard()
        assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
        size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());assert size<40_000_000
        res.update(cpu_threads=4,pilot_saved_bytes=size);return res
    g.dump_new(dest,r)
    try:
        r['resources_before']=check();ex=g.read(HERE/'ACTUAL_PILOT_EXIT.json');fit=g.read(TRAIN/'receipt.json')
        assert ex['observed_tool_exit']==0 and ex['result_sha256']==g.sha(TRAIN/'receipt.json')
        assert fit['complete'] and not fit['errors'] and len(fit['arms'])==4
        assert fit['new_cpu_updates']+fit['new_GPU_updates']==396
        for b in fit['source_bindings']:assert g.sha(ROOT/b['path'])==b['sha256']
        cases=[(role,c,row) for role,c,row in g.roles() if role=='validation']
        assert len(cases)==9 and {c['patient'] for role,c,row in cases}==g.VALIDATORS
        sources=[Path(__file__),HERE/'EVALUATION_PROTOCOL.md',HERE/'ACTUAL_PILOT_EXIT.json',TRAIN/'receipt.json',
            Path(g.__file__),Path(independent.__file__),ROOT/'final_training_medical_execution_2026_10_08/production_probability_mapping_v4.py']
        sources.extend(ROOT/b['path'] for b in fit['source_bindings'])
        initial_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=g.sha(p)) for p in sorted(set(sources))]
        r['initial_source_bindings']=initial_bindings;save()
        for a in fit['arms']:
            assert a['complete'] and a['updates_completed']==99
            cpfile=ROOT/a['checkpoint_path'];assert g.sha(cpfile)==a['checkpoint_sha256'];sources.append(cpfile)
            cp=torch.load(cpfile,map_location='cpu',weights_only=True);assert g.state_hash(cp['state_dict'])==a['final_weights_sha256']
            assert cp['history_sha256']==g.sha(ROOT/a['history_path'])==a['history_sha256'];sources.append(ROOT/a['history_path'])
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
                gt=g.read_reference_label(c);metrics=g.metrics(pred,gt);counts=independent.independent_counts(pred,gt)
                assert independent.trees_close(metrics,counts)
                record=dict(patient=c['patient'],uid=c['uid'],role=role,metrics=metrics,physical_input_sha256=g.array_sha(image),
                    probability_sha256=g.array_sha(probability),label_sha256=g.array_sha(gt),production_inference=meta,
                    independent_inference=imeta,strict_gate_passed=strict,max_probability_error=error,binary_disagreements=binary,
                    prediction_file=predfile.relative_to(ROOT).as_posix(),prediction_file_sha256=g.sha(predfile))
                if not strict:r['numerical_failures'].append(dict(branch=a['name'],uid=c['uid'],max_probability_error=error,binary=binary))
                arm['series'].append(record);sources.append(predfile);save()
                print(json.dumps(dict(branch=a['name'],series_done=len(arm['series']),strict_gate_passed=strict)),flush=True)
                del image,probability,replay,pred,gt;gc.collect();check()
            agg=g.aggregate(arm['series'],g.VALIDATORS);iagg=independent.independent_aggregate(arm['series'],g.VALIDATORS)
            assert independent.trees_close(agg,iagg);arm.update(complete=True,validation_aggregate=iagg,validation_gates=g.gates(iagg))
            assert g.state_hash(model.state_dict())==a['final_weights_sha256'];del model,wrapped,cp;gc.collect();save()
        for b in initial_bindings:assert g.sha(ROOT/b['path'])==b['sha256']
        r.update(complete=True,all36_strict_gates_passed=not r['numerical_failures'],
            all_four_branches_medical_gates_passed=all(all(a['validation_gates'].values()) for a in r['arms']),
            source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=g.sha(p)) for p in sorted(set(sources))],resources_after=check())
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r.update(finished_utc=g.now(),elapsed_seconds=time.perf_counter()-started);save()
    print(json.dumps({k:r.get(k) for k in ['complete','errors','all36_strict_gates_passed','all_four_branches_medical_gates_passed','elapsed_seconds']}),flush=True)
    return int(not r['complete'] or bool(r['errors']) or not r.get('all36_strict_gates_passed',False))
if __name__=='__main__':raise SystemExit(main())
