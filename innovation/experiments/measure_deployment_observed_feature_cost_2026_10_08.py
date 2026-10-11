"""One CPU production feature pass, separate from verification and counterfactual costs."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import gc
import json
import math
import sys
import time
import traceback
from datetime import datetime,timezone
from pathlib import Path
SCRIPT_STARTED=time.perf_counter()
from observed_holdout_feature_2026_10_08 import torch,fold_plan,build_retained_source,predict_heldout,reference_projection_after_prediction,scores
import numpy as np
from common_projected_input_audit_2026_10_08 import ROOT,StageAudit,entry,read,sha,arrsha
OUT=ROOT/'experiments/deployment_observed_feature_cost_2026_10_08'
PROD=ROOT/'experiments/observed_holdout_feature_qualification_2026_10_08/attempt01.json'
TABLE=ROOT/'experiments/observed_holdout_feature_table_2026_10_08.json'
PRE=ROOT/'experiments/deployment_observed_feature_cost_preregistration_2026_10_08.json'


def measured(fn):
    start=time.perf_counter()
    value=fn()
    return value,time.perf_counter()-start


def aggregate_features(original,folds):
    means={kind:sum(f['scores'][kind]['sum_squared_error'] for f in folds)/sum(f['scores'][kind]['elements'] for f in folds)
        for kind in ('linear','pchip')}
    maes={kind:sum(f['scores'][kind]['sum_abs_error'] for f in folds)/sum(f['scores'][kind]['elements'] for f in folds)
        for kind in ('linear','pchip')}
    gaps=[b-a for f in folds for a,b in zip(f['retained_positions_mm'],f['retained_positions_mm'][1:])]
    return dict(observed_adjacent_spacing_mm=original['observed_adjacent_spacing_mm'],
        retained_adjacent_spacing_min_mm=min(gaps),retained_adjacent_spacing_max_mm=max(gaps),
        observed_anchor_count=len(original['observed_indices']),
        heldout_observed_plane_count=sum(len(f['heldout_ordinals']) for f in folds),
        target_rows=original['target_rc'][0],target_cols=original['target_rc'][1],
        heldout_observed_pixel_count=sum(f['scores']['linear']['elements'] for f in folds),
        heldout_linear_MSE=means['linear'],heldout_pchip_MSE=means['pchip'],
        heldout_MSE_pchip_minus_linear=means['pchip']-means['linear'],
        heldout_linear_MAE=maes['linear'],heldout_pchip_MAE=maes['pchip'],
        retained_mean_min=min(f['retained_statistics']['mean'] for f in folds),
        retained_mean_max=max(f['retained_statistics']['mean'] for f in folds),
        retained_population_std_min=min(f['retained_statistics']['population_std'] for f in folds),
        retained_population_std_max=max(f['retained_statistics']['population_std'] for f in folds))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    OUT.mkdir(exist_ok=False)
    original,table,pre=read(PROD),read(TABLE),read(PRE)
    assert all(v['complete'] and not v['errors'] for v in (original,table,pre))
    for b in pre['source_bindings']:
        assert sha(ROOT/b['path'])==b['sha256']
    expected={(v['patient'],v['series_uid']):v for v in table['rows']}
    audit=StageAudit(OUT,torch,[v['observed_package'] for v in original['series']],SCRIPT_STARTED)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],
        source_bindings=[entry(Path(__file__)),entry(PROD),entry(TABLE),entry(PRE)],
        medical_observed_packages_loaded=0,real_folds_completed=0,
        neural_forwards=0,GPU_forwards=0,training_updates=0,model_arrays_loaded=0,
        MRI_task_scored=False,method_selected=False,confirmation_patients_opened=False,
        validation_data_read=False,locked_IXI_opened=False,
        repeats=1,warmups=0,counterfactuals_run=0,independent_Hermite_checks_repeated=0,
        previous_norm_MSE_is_not_task_benefit=True,cold_cache_state_controlled=False)
    try:
        r['resources_before']=audit.guard()
        for s in original['series']:
            series_started=time.perf_counter()
            audit.guard()
            path=ROOT/s['observed_package']
            digest,hash_seconds=measured(lambda:sha(path))
            assert digest==s['observed_package_sha256']
            def load():
                with np.load(path,allow_pickle=False) as package:
                    r['medical_observed_packages_loaded']+=1
                    return package['observed_rcz'].copy(),tuple(map(int,package['observed_indices'])),package['native_shape'].copy(),package['affine_rcz_ras'].copy()
            (a,indices,shape,affine),load_seconds=measured(load)
            check_started=time.perf_counter()
            assert arrsha(a)==s['observed_array_sha256'] and a.dtype==np.float32 and np.isfinite(a).all()
            assert list(indices)==s['observed_indices'] and shape.tolist()==s['native_shape_rcz']
            assert np.array_equal(affine,s['native_affine_rcz_ras'])
            input_validation_seconds=time.perf_counter()-check_started
            phases=dict(observed_package_hash_verification_seconds=hash_seconds,observed_IO_decode_seconds=load_seconds,
                input_array_metadata_verification_seconds=input_validation_seconds,source_construct_seconds=0.,
                two_interpolation_predictions_seconds=0.,reference_projection_seconds=0.,
                full_plane_scores_seconds=0.,feature_reduce_seconds=0.,feature_equality_verification_seconds=0.)
            positions=np.asarray(indices,float)*float(np.linalg.norm(affine[:3,2]))
            folds=[]
            for fold in (0,1):
                kept,held=fold_plan(indices,fold)
                source,elapsed=measured(lambda:build_retained_source(a[:,:,kept].copy(),positions[list(kept)],s['target_rc']))
                phases['source_construct_seconds']+=elapsed
                (predictions,definitions),elapsed=measured(lambda:predict_heldout(source,positions[list(held)]))
                phases['two_interpolation_predictions_seconds']+=elapsed
                reference,elapsed=measured(lambda:reference_projection_after_prediction(a[:,:,held],source))
                phases['reference_projection_seconds']+=elapsed
                scored,elapsed=measured(lambda:{kind:scores(value,reference) for kind,value in predictions.items()})
                phases['full_plane_scores_seconds']+=elapsed
                folds.append(dict(fold=fold,heldout_ordinals=list(held),retained_positions_mm=positions[list(kept)].tolist(),
                    retained_statistics=source.statistics,scores=scored))
                r['real_folds_completed']+=1
                del source,predictions,reference
            features,elapsed=measured(lambda:aggregate_features(s,folds))
            phases['feature_reduce_seconds']=elapsed
            check_started=time.perf_counter()
            assert len(features)==17 and features==expected[(s['patient'],s['uid'])]['features']
            assert all(math.isfinite(v) for v in features.values())
            for f,old in zip(folds,s['folds']):
                assert f['scores']==old['scores'] and f['retained_statistics']==old['retained_statistics']
            phases['feature_equality_verification_seconds']=time.perf_counter()-check_started
            deploy=sum(phases[k] for k in ('observed_IO_decode_seconds','source_construct_seconds',
                'two_interpolation_predictions_seconds','reference_projection_seconds','full_plane_scores_seconds','feature_reduce_seconds'))
            del a
            gc.collect()
            audit.guard()
            elapsed=time.perf_counter()-series_started
            r['series'].append(dict(patient=s['patient'],uid=s['uid'],features=features,phase_seconds=phases,
                summed_production_phases_seconds=deploy,measured_series_total_with_qualification_seconds=elapsed,
                unassigned_series_overhead_seconds=elapsed-sum(phases.values()),
                features_and_fold_scores_exactly_equal_to_frozen_qualification=True))
            print(json.dumps(dict(index=len(r['series']),patient=s['patient'],production_phase_seconds=deploy,
                measured_series_with_qualification_seconds=elapsed),ensure_ascii=False),flush=True)
        assert r['medical_observed_packages_loaded']==19 and r['real_folds_completed']==38
        patients=[]
        for patient in sorted({v['patient'] for v in r['series']}):
            cases=[v for v in r['series'] if v['patient']==patient]
            patients.append(dict(patient=patient,series=len(cases),
                production_phases_sum_seconds=math.fsum(v['summed_production_phases_seconds'] for v in cases),
                measured_series_with_qualification_sum_seconds=math.fsum(v['measured_series_total_with_qualification_seconds'] for v in cases)))
        r['patient_costs']=patients
        r['patient_equal_production_phase_seconds']=math.fsum(v['production_phases_sum_seconds'] for v in patients)/11
        r['total_production_phase_seconds']=math.fsum(v['summed_production_phases_seconds'] for v in r['series'])
        r['total_series_with_qualification_seconds']=math.fsum(v['measured_series_total_with_qualification_seconds'] for v in r['series'])
        r['phase_totals_seconds']={k:math.fsum(v['phase_seconds'][k] for v in r['series']) for k in r['series'][0]['phase_seconds']}
        r['io_audit']=audit.result()
        assert not audit.denied
        r['resources_after']=audit.guard()
        r['complete']=True
    except Exception as exc:
        r['errors'].append(type(exc).__name__+': '+str(exc))
        r['traceback']=traceback.format_exc()
        r['io_audit']=audit.result()
    r['child_elapsed_before_final_output_seconds']=time.perf_counter()-SCRIPT_STARTED
    r['finished_utc']=datetime.now(timezone.utc).isoformat()
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','medical_observed_packages_loaded','real_folds_completed',
        'total_production_phase_seconds','patient_equal_production_phase_seconds','child_elapsed_before_final_output_seconds')},ensure_ascii=False),flush=True)
    return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
