"""Full observed-only feature extraction plus 38 real heldout counterfactual checks."""
import gc
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from observed_holdout_feature_2026_10_08 import (
    torch, fold_plan, statistics, build_retained_source, predict_heldout,
    reference_projection_after_prediction, scores,
)
from common_projected_input_audit_2026_10_08 import ROOT, StageAudit, entry, read, sha, arrsha
SOURCE = ROOT/'experiments/common_projected_observed_qualification_2026_10_08/attempt01.json'
PRE = ROOT/'experiments/observed_holdout_feature_preregistration_2026_10_08.json'
OUT = ROOT/'experiments/observed_holdout_feature_qualification_2026_10_08'
DEVELOPERS = {'VS-MC-RC-'+s for s in ('001','002','004','005','006','007','009','010','011','012','013')}


def merged_scores(folds, kind):
    rows = [fold['scores'][kind] for fold in folds]
    count = sum(row['elements'] for row in rows)
    squared = sum(row['sum_squared_error'] for row in rows)
    return dict(elements=count, mean_error=sum(row['sum_error'] for row in rows)/count,
                MAE=sum(row['sum_abs_error'] for row in rows)/count, MSE=squared/count,
                RMSE=float(np.sqrt(squared/count)), max_abs_error=max(row['max_abs_error'] for row in rows))


def synthetic_check():
    a = np.full((6,6,8), 7, dtype=np.float32)
    idx = tuple(range(0,32,4))
    records = []
    for fold in (0,1):
        kept, held = fold_plan(idx, fold)
        positions = np.asarray(idx, float)
        source = build_retained_source(a[:,:,kept].copy(), positions[list(kept)], (5,5))
        predictions, details = predict_heldout(source, positions[list(held)])
        reference = reference_projection_after_prediction(a[:,:,held], source)
        assert source.statistics['zero_std'] and source.statistics['divisor'] == 1
        assert all(np.count_nonzero(p)==0 and scores(p,reference)['MSE']==0 for p in predictions.values())
        altered = a.copy()
        altered[:,:,held] += np.float32(10000)
        again = build_retained_source(altered[:,:,kept].copy(), positions[list(kept)], (5,5))
        newpred, _ = predict_heldout(again, positions[list(held)])
        changed_reference = reference_projection_after_prediction(altered[:,:,held], again)
        assert again.statistics == source.statistics and arrsha(again.projected_rca) == arrsha(source.projected_rca)
        assert all(arrsha(newpred[k])==arrsha(predictions[k]) and scores(newpred[k],changed_reference)['MSE']>0
                   for k in predictions)
        records.append(dict(fold=fold, zero_std_divisor_one=True, original_MSE_zero=True,
                            counterfactual_source_and_predictions_exact=True,
                            changed_reference_MSE={key:scores(newpred[key],changed_reference)['MSE'] for key in newpred}))
    return records


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    OUT.mkdir(exist_ok=False)
    start = time.perf_counter()
    old, pre = read(SOURCE), read(PRE)
    assert old['complete'] and pre['complete'] and not old['errors'] and not pre['errors']
    audit = StageAudit(OUT, torch, [s['observed_package'] for s in old['series']], start)
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[], series=[],
             medical_observed_packages_loaded=0, actual_real_folds_completed=0,
             real_counterfactuals_completed=0, synthetic_folds_completed=0,
             model_arrays_loaded=0, neural_forwards=0, GPU_forwards=0, training_updates=0,
             interpolation_method_selected=False, task_effects_scored=False,
             validation_data_read=False, confirmation_patients_opened=False, locked_IXI_opened=False,
             theoretical_risk_certificate_issued=False, publication_claim_confirmed=False)
    path = OUT/'attempt01.json'

    def save():
        path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    save()
    try:
        for b in pre['source_bindings']:
            assert sha(ROOT/b['path']) == b['sha256'], b['path']
        r['source_bindings'] = [entry(PRE),entry(SOURCE),entry(Path(__file__)),
            entry(ROOT/'experiments/observed_holdout_feature_2026_10_08.py'),
            entry(ROOT/'experiments/common_projected_input_audit_2026_10_08.py'),
            entry(ROOT/'OBSERVED_HOLDOUT_FEATURE_PROTOCOL_2026-10-08.md')]
        r['resources_before'] = audit.guard()
        assert len(old['series'])==19 and {s['patient'] for s in old['series']}==DEVELOPERS
        r['synthetic_checks'] = synthetic_check()
        r['synthetic_folds_completed'] = 2
        for index, original in enumerate(old['series']):
            audit.guard()
            p = ROOT/original['observed_package']
            assert sha(p)==original['observed_package_sha256']
            with np.load(p,allow_pickle=False) as package:
                a=package['observed_rcz'].copy()
                r['medical_observed_packages_loaded'] += 1
                idx=tuple(map(int,package['observed_indices']))
                shape=package['native_shape'].astype(int)
                affine=package['affine_rcz_ras'].copy()
            assert a.dtype==np.float32 and np.isfinite(a).all() and arrsha(a)==original['observed_array_sha256']
            assert idx==tuple(original['observed_indices'])==tuple(range(0,int(shape[2]),4))
            assert shape.tolist()==original['native_shape_rcz'] and np.array_equal(affine,original['native_affine_rcz_ras'])
            spacing=float(np.linalg.norm(affine[:3,2]))
            positions=np.asarray(idx,dtype=float)*spacing
            target_rc=original['grid']['unpadded_shape_zrc'][1:]
            folds=[]
            for fold in (0,1):
                kept,held=fold_plan(idx,fold)
                source=build_retained_source(a[:,:,kept].copy(),positions[list(kept)],target_rc)
                predictions,definitions=predict_heldout(source,positions[list(held)])
                sourcehash=arrsha(source.projected_rca)
                predhash={key:arrsha(value) for key,value in predictions.items()}
                # Target references enter only after the prediction arrays are complete.
                reference=reference_projection_after_prediction(a[:,:,held],source)
                result_scores={key:scores(value,reference) for key,value in predictions.items()}
                per_plane=[dict(observed_ordinal=int(ordinal),native_z=int(idx[ordinal]),position_mm=float(positions[ordinal]),
                    scores={key:scores(value[:,:,j],reference[:,:,j]) for key,value in predictions.items()})
                    for j,ordinal in enumerate(held)]
                altered=a.copy()
                altered[:,:,held] += np.float32(10000)
                assert np.isfinite(altered).all() and np.array_equal(altered[:,:,kept],a[:,:,kept])
                counter=build_retained_source(altered[:,:,kept].copy(),positions[list(kept)],target_rc)
                counterpred,counterdefinitions=predict_heldout(counter,positions[list(held)])
                assert counter.statistics==source.statistics and arrsha(counter.projected_rca)==sourcehash
                assert all(arrsha(counterpred[key])==predhash[key] for key in predictions)
                assert counterdefinitions==definitions
                unmasked_stats=statistics(a)
                altered_unmasked=statistics(altered)
                assert altered_unmasked['mean']!=unmasked_stats['mean']
                assert arrsha(source.projected_rca)==sourcehash and not source.projected_rca.flags.writeable
                counterref=reference_projection_after_prediction(altered[:,:,held],counter)
                assert arrsha(counterref)!=arrsha(reference)
                assert all(scores(counterpred[key],counterref)['MSE']!=result_scores[key]['MSE'] for key in predictions)
                folds.append(dict(fold=fold,retained_ordinals=list(kept),heldout_ordinals=list(held),
                    retained_native_z=[idx[i] for i in kept],heldout_native_z=[idx[i] for i in held],
                    retained_positions_mm=positions[list(kept)].tolist(),heldout_positions_mm=positions[list(held)].tolist(),
                    retained_statistics=source.statistics,shared_source_sha256=sourcehash,
                    shared_source_shape_rca=list(source.projected_rca.shape),prediction_sha256=predhash,
                    reference_sha256=arrsha(reference),reference_projection_after_predictions=True,
                    definitions=definitions,scores=result_scores,per_plane_scores=per_plane,
                    counterfactual=dict(heldout_offset=10000,retained_values_exact=True,retained_statistics_exact=True,
                        shared_source_exact=True,predictions_exact=True,definitions_exact=True,
                        heldout_reference_changed=True,heldout_scores_changed=True,
                        unmasked_full_statistics_changed=True,original_full_mean=unmasked_stats['mean'],
                        counterfactual_full_mean=altered_unmasked['mean'])))
                r['actual_real_folds_completed']+=1
                r['real_counterfactuals_completed']+=1
                del source,predictions,reference,altered,counter,counterpred,counterref
                gc.collect()
                audit.guard()
            heldsets=[set(f['heldout_ordinals']) for f in folds]
            assert not heldsets[0]&heldsets[1] and heldsets[0]|heldsets[1]==set(range(1,len(idx)-1))
            merged={key:merged_scores(folds,key) for key in ('linear','pchip')}
            r['series'].append(dict(patient=original['patient'],uid=original['uid'],observed_package=original['observed_package'],
                observed_package_sha256=original['observed_package_sha256'],observed_array_sha256=arrsha(a),
                observed_indices=list(idx),native_shape_rcz=shape.tolist(),native_affine_rcz_ras=affine.tolist(),
                observed_adjacent_spacing_mm=4*spacing,native_z_spacing_mm=spacing,target_rc=target_rc,
                folds=folds,merged_scores=merged,
                observed_MSE_difference_pchip_minus_linear=merged['pchip']['MSE']-merged['linear']['MSE']))
            print(json.dumps(dict(index=index+1,patient=original['patient'],folds_passed=2,
                                  observed_MSE_difference_pchip_minus_linear=r['series'][-1]['observed_MSE_difference_pchip_minus_linear']),ensure_ascii=False),flush=True)
            del a
            gc.collect()
            save()
        patients=[]
        for patient in sorted(DEVELOPERS):
            series=[s for s in r['series'] if s['patient']==patient]
            values={kind:float(np.mean([s['merged_scores'][kind]['MSE'] for s in series])) for kind in ('linear','pchip')}
            patients.append(dict(patient=patient,series=len(series),series_equal_mean_MSE=values,
                                 MSE_difference_pchip_minus_linear=values['pchip']-values['linear']))
        r['patient_features']=patients
        r['patient_equal_observed_MSE']={kind:float(np.mean([p['series_equal_mean_MSE'][kind] for p in patients])) for kind in ('linear','pchip')}
        assert r['actual_real_folds_completed']==r['real_counterfactuals_completed']==38
        assert not audit.denied
        r['io_audit']=audit.result()
        r['gate']=dict(all19_development_observed_packages=True,all38_folds=True,
            holdout_before_statistics_and_projection=True,pure_prediction_API_has_no_target_pixels=True,
            every_interior_observed_layer_exactly_one_holdout=True,full_plane_observed_reference_scored=True,
            all38_counterfactual_predictions_exact=True,unmasked_statistics_dependency_recorded=True,
            synthetic_zero_std_and_changed_reference=True,no_native_GT_or_neural_IO=True)
        r['resources_after']=audit.guard()
        r['complete']=True
    except Exception as exc:
        r['errors'].append(type(exc).__name__+': '+str(exc))
        r['traceback']=traceback.format_exc()
        r['io_audit']=audit.result()
    r['elapsed_seconds']=time.perf_counter()-start
    r['finished_utc']=datetime.now(timezone.utc).isoformat()
    save()
    print(json.dumps(dict(complete=r['complete'],errors=r['errors'],series=len(r['series']),
        real_folds=r['actual_real_folds_completed'],medical_observed_packages_loaded=r['medical_observed_packages_loaded'],
        elapsed_seconds=r['elapsed_seconds']),ensure_ascii=False),flush=True)
    return int(not r['complete'])


if __name__=='__main__':
    raise SystemExit(main())
