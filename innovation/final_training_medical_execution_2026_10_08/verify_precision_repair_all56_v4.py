"""All56 V4 production, independent functional inference, coordinates, packing and count audit."""
import gc,json,sys,time,traceback
from pathlib import Path
from production_probability_mapping_v4 import infer_full_fov_v4
import final_eval_lossless_v3 as g
import verify_final_lossless_v3 as independent
torch,np=g.torch,g.np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'precision_v4_attempt01'

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(4);started=time.perf_counter()
    OUT.mkdir(exist_ok=False);dest=OUT/'receipt.json'
    r=dict(created_utc=g.now(),complete=False,errors=[],arms=[],numerical_failures=[],
        protocol='PRECISION_REPAIR_V4_PROTOCOL.md',actual_training_updates=0,actual_gpu_updates=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,scientific_confirmation_patients=0,
        publication_claim_confirmed=False,goal_status='active',cross_process_independent_reexecution=False)
    def save():g.atomic_json(dest,r)
    def check():
        assert time.perf_counter()-started<=3600,'V4 all56 wall3600s bound exceeded'
        res=g.guard(started)
        size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
        assert size<10_000_000,'V4 stage10MB bound exceeded';res['new_stage_saved_bytes']=size
        return res
    g.dump_new(dest,r)
    try:
        r['resources_before']=check();checkpoints,sources=g.frozen_training();cases=g.roles()
        oldpath=g.OUT/'evaluation_attempt01.json';old=g.read(oldpath)
        strictpath=g.OUT/'independent_all56_attempt01.json';oldstrict=g.read(strictpath)
        diagnosis=HERE/'PROBABILITY_MAPPING_STAGE_DIAGNOSIS.json';diag=g.read(diagnosis)
        assert old['complete'] and not old['errors'] and old['prediction_files_saved']==56
        assert oldstrict['complete'] and not oldstrict['errors'] and oldstrict['all56_prediction_files_and_metrics_verified']
        assert diag['complete'] and not diag['errors'] and diag['prototype_case_strict_gate_passed']
        sources.extend([oldpath,strictpath,diagnosis,Path(__file__),HERE/'production_probability_mapping_v4.py',
            HERE/'PRECISION_REPAIR_V4_PROTOCOL.md',Path(independent.__file__)])
        for b in old['source_bindings']:assert g.sha(ROOT/b['path'])==b['sha256'];sources.append(ROOT/b['path'])
        r['initial_source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=g.sha(p)) for p in sorted(set(sources))]
        save()
        for qa,cpbinding in zip(old['arms'],checkpoints):
            assert qa['kind']==cpbinding['kind'] and qa['checkpoint_sha256']==cpbinding['sha256'] and len(qa['series'])==28
            cp=torch.load(ROOT/cpbinding['path'],map_location='cpu',weights_only=True)
            model=g.TaskUNet3D();model.load_state_dict(cp['state_dict']);model.eval();wrapped=g.GuardedModel(model,check)
            arm=dict(kind=qa['kind'],checkpoint=cpbinding,complete=False,series=[]);r['arms'].append(arm);save()
            by={s['uid']:s for s in qa['series']}
            for index,(role,c,row) in enumerate(cases):
                check();tick=time.perf_counter();s=by[c['uid']]
                assert s['role']==role and s['patient']==c['patient']
                normalized,stats=g.source_image(c,row,qa['kind']);grid=g.lattice(c);image=g.physical_mr(normalized,grid)
                assert g.array_sha(image)==s['physical_input_sha256'] and stats==s['observed_statistics'];del normalized
                probability,meta=infer_full_fov_v4(wrapped,image,grid,c['native_shape'])
                assert probability.dtype==np.float32 and np.isfinite(probability).all() and meta==s['inference']
                pred=probability>=.5;predfile=OUT/(qa['kind']+'_'+str(index).zfill(2)+'.npz');g.pack_prediction(predfile,pred)
                assert np.array_equal(g.unpack_prediction(predfile),pred)
                ind,imeta=independent.functional_fov(cp['state_dict'],image,grid,c['native_shape'],check)
                assert imeta['total_tiles']==meta['total_tiles'] and imeta['axis_starts']==meta['axis_starts']
                error=float(np.max(np.abs(probability-ind)));binary=int(np.count_nonzero(pred!=(ind>=.5)))
                strict=error<=3e-6 and binary==0 and imeta['float64_coordinate_gate_passed']
                oldpredfile=ROOT/s['prediction_file'];assert g.sha(oldpredfile)==s['prediction_file_sha256']
                oldpred=g.unpack_prediction(oldpredfile);oldchanges=int(np.count_nonzero(pred!=oldpred));del oldpred
                gt=g.read_reference_label(c);assert g.array_sha(gt)==s['label_sha256']
                primary=g.metrics(pred,gt);counts=independent.independent_counts(pred,gt)
                assert independent.trees_close(primary,counts)
                record=dict(role=role,patient=c['patient'],uid=c['uid'],physical_input_sha256=s['physical_input_sha256'],
                    probability_sha256=g.array_sha(probability),independent_probability_sha256=g.array_sha(ind),
                    prediction_file=predfile.relative_to(ROOT).as_posix(),prediction_file_sha256=g.sha(predfile),
                    prediction_sha256=g.array_sha(pred),label_sha256=s['label_sha256'],metrics=primary,
                    strict_gate_passed=strict,float32_max_probability_error=error,float32_threshold_disagreements=binary,
                    independent_FOV_and_float64_coordinate=imeta,old_prediction_threshold_changes=oldchanges,
                    old_metrics_identical=independent.trees_close(counts,s['metrics']),
                    production_inference=meta,full_production_and_functional_seconds=time.perf_counter()-tick)
                arm['series'].append(record);sources.extend([oldpredfile,predfile])
                if not strict:r['numerical_failures'].append({k:record[k] for k in ('role','patient','uid','float32_max_probability_error','float32_threshold_disagreements')})
                save();print(json.dumps(dict(kind=qa['kind'],series_verified=len(arm['series']),strict_gate_passed=strict,
                    max_probability_error=error,old_threshold_changes=oldchanges)),flush=True)
                del image,probability,pred,ind,gt;gc.collect();check()
            for role,people in [('development',g.DEVELOPERS),('validation',g.VALIDATORS)]:
                rows=[s for s in arm['series'] if s['role']==role]
                aggregate=g.aggregate(rows,people);agg=independent.independent_aggregate(rows,people)
                assert independent.trees_close(aggregate,agg);arm[role+'_aggregate']=agg
            arm['validation_gates']=g.gates(arm['validation_aggregate'])
            arm['all_validation_gates_passed']=all(arm['validation_gates'].values())
            assert g.state_hash(model.state_dict())==cpbinding['state_hash'];arm['complete']=True
            del model,wrapped,cp;gc.collect();save()
        sources=sorted(set(sources));r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=g.sha(p)) for p in sources]
        for b in r['initial_source_bindings']:assert g.sha(ROOT/b['path'])==b['sha256']
        for b in old['source_bindings']:assert g.sha(ROOT/b['path'])==b['sha256']
        assert g.sha(oldpath)==next(b['sha256'] for b in r['source_bindings'] if b['path']==oldpath.relative_to(ROOT).as_posix())
        rows=[s for a in r['arms'] for s in a['series']]
        r.update(complete=len(rows)==56 and all(a['complete'] for a in r['arms']),
            all56_production_and_independent_FOVs_completed=len(rows)==56,all_strict_numeric_gates_passed=not r['numerical_failures'],
            all_arms_validation_gates_passed=all(a['all_validation_gates_passed'] for a in r['arms']),
            total_old_prediction_threshold_changes=sum(s['old_prediction_threshold_changes'] for s in rows),
            all_old_metrics_identical=all(s['old_metrics_identical'] for s in rows),
            max_probability_error=max(s['float32_max_probability_error'] for s in rows),resources_after=check(),
            CUDA_initialized=torch.cuda.is_initialized(),formal_training_completed_updates=39996)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=g.now();r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ['complete','errors','all56_production_and_independent_FOVs_completed',
        'all_strict_numeric_gates_passed','all_arms_validation_gates_passed','total_old_prediction_threshold_changes',
        'max_probability_error','elapsed_seconds']}),flush=True)
    return int(not r['complete'] or not r.get('all_strict_numeric_gates_passed',False))
if __name__=='__main__':raise SystemExit(main())
