"""Independent folds/stats, nonuniform Hermite mathematics, and counterfactual reloads."""
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
import numpy as np
import torch
from torch.nn import functional as F
from scipy.interpolate import PchipInterpolator
from common_projected_input_audit_2026_10_08 import ROOT,StageAudit,entry,read,sha,arrsha
SOURCE=ROOT/'experiments/observed_holdout_feature_qualification_2026_10_08/attempt01.json'
PRE=ROOT/'experiments/observed_holdout_feature_layout_v2_preregistration_2026_10_08.json'
OUT=ROOT/'experiments/observed_holdout_feature_independent_layout_v2_2026_10_08'
ATOL=RTOL=3e-5


def original_arbitrary_layout_statistics(a):
    mean=float(a.mean(dtype=np.float64))
    std=float(a.std(dtype=np.float64,ddof=0))
    return dict(mean=mean,population_std=std,divisor=std if std>0 else 1.,zero_std=std==0,elements=int(a.size))


def own_statistics(a):
    return original_arbitrary_layout_statistics(np.array(a,copy=True,order='C'))


def statistics_mathematics(a,st):
    flat=np.ascontiguousarray(a,dtype=np.float64).ravel()
    pieces=[flat[i:i+65536] for i in range(0,flat.size,65536)]
    mean=math.fsum(float(piece.sum(dtype=np.float64)) for piece in pieces)/flat.size
    variance=math.fsum(float(np.square(piece-mean).sum(dtype=np.float64)) for piece in pieces)/flat.size
    std=math.sqrt(variance)
    assert math.isclose(mean,st['mean'],rel_tol=1e-12,abs_tol=1e-12)
    assert math.isclose(std,st['population_std'],rel_tol=1e-12,abs_tol=1e-12)
    return dict(mean_abs_error=abs(mean-st['mean']),std_abs_error=abs(std-st['population_std']),
                abs_tol=1e-12,rel_tol=1e-12,passed=True)


def library_projection(a,target,st):
    normalized=((a.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
    x=torch.from_numpy(np.ascontiguousarray(normalized.transpose(2,0,1)))[:,None]
    with torch.no_grad():
        y=F.interpolate(x,size=target,mode='bilinear',align_corners=False)[:,0].numpy()
    return np.ascontiguousarray(y.transpose(1,2,0)),normalized


def mathematical_projection_samples(a,target,index,fold):
    rng=np.random.default_rng(np.random.SeedSequence([20261008,812,index,fold]))
    coords=rng.integers(0,np.asarray(target),size=(512,2))
    coords=np.unique(np.concatenate((coords,[[0,0],np.asarray(target)//2,np.asarray(target)-1])),axis=0)
    scale=np.asarray(a.shape[:2],np.float32)/np.asarray(target,np.float32)
    at=np.clip((coords.astype(np.float32)+np.float32(.5))*scale-np.float32(.5),
               0,np.asarray(a.shape[:2])-1).astype(np.float32)
    lo=np.floor(at).astype(int)
    hi=np.minimum(lo+1,np.asarray(a.shape[:2])-1)
    fraction=at-lo
    result=np.zeros((len(coords),a.shape[2]),float)
    for row in (0,1):
        for col in (0,1):
            rr=hi[:,0] if row else lo[:,0]
            cc=hi[:,1] if col else lo[:,1]
            weight=(fraction[:,0] if row else 1-fraction[:,0])*(fraction[:,1] if col else 1-fraction[:,1])
            result+=weight[:,None]*a[rr,cc,:]
    return coords,result


def predictions(anchors,positions,query):
    exact_linear=np.zeros((*anchors.shape[:2],len(query)),np.float32)
    exact_pchip=np.zeros_like(exact_linear)
    mathematical_linear=np.zeros_like(exact_linear,dtype=np.float64)
    mathematical_pchip=np.zeros_like(mathematical_linear)
    a=anchors.astype(np.float64)
    definitions=[]
    for j,z in enumerate(query):
        i=int(np.searchsorted(positions,z)-1)
        h=positions[i+1]-positions[i]
        t=(z-positions[i])/h
        exact_linear[:,:,j]=(1-float(t))*anchors[:,:,i]+float(t)*anchors[:,:,i+1]
        mathematical_linear[:,:,j]=(1-t)*a[:,:,i]+t*a[:,:,i+1]
        internal=i>=1 and i+2<len(positions)
        if internal:
            ix=np.arange(i-1,i+3)
            exact_pchip[:,:,j]=PchipInterpolator(positions[ix],anchors[:,:,ix],axis=2)(z)
            hprev=positions[i]-positions[i-1]
            hnext=positions[i+2]-positions[i+1]
            dprev=(a[:,:,i]-a[:,:,i-1])/hprev
            dcurr=(a[:,:,i+1]-a[:,:,i])/h
            dnext=(a[:,:,i+2]-a[:,:,i+1])/hnext
            slopes=[]
            for dl,dr,hl,hr in ((dprev,dcurr,hprev,h),(dcurr,dnext,h,hnext)):
                slope=np.zeros_like(dl)
                same=(dl*dr)>0
                w1,w2=2*hr+hl,hr+2*hl
                slope[same]=(w1+w2)/(w1/dl[same]+w2/dr[same])
                slopes.append(slope)
            mathematical_pchip[:,:,j]=((2*t**3-3*t**2+1)*a[:,:,i]+(t**3-2*t**2+t)*h*slopes[0]+
                (-2*t**3+3*t**2)*a[:,:,i+1]+(t**3-t**2)*h*slopes[1])
        else:
            exact_pchip[:,:,j]=exact_linear[:,:,j]
            mathematical_pchip[:,:,j]=mathematical_linear[:,:,j]
        definitions.append(dict(query_position_mm=float(z),bracket_mm=positions[i:i+2].tolist(),
            local_PCHIP=internal,source_ordinals=list(range(i-1,i+3)) if internal else [i,i+1]))
    return dict(linear=exact_linear,pchip=exact_pchip),dict(linear=mathematical_linear,pchip=mathematical_pchip),definitions


def score(a,b):
    difference=np.subtract(a.astype(float),b.astype(float))
    absolute=np.abs(difference)
    square=difference*difference
    mse=float(square.mean())
    return dict(elements=int(difference.size),sum_error=float(difference.sum()),sum_abs_error=float(absolute.sum()),
        sum_squared_error=float(square.sum()),mean_error=float(difference.mean()),MAE=float(absolute.mean()),
        MSE=mse,RMSE=float(np.sqrt(mse)),max_abs_error=float(absolute.max()))


def check(actual,expected,name):
    error=float(np.max(np.abs(actual-expected)))
    assert np.allclose(actual,expected,atol=ATOL,rtol=RTOL),(name,error)
    return dict(name=name,elements=int(actual.size),max_abs_error=error,atol=ATOL,rtol=RTOL,passed=True)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    OUT.mkdir(exist_ok=False)
    start=time.perf_counter()
    q,pre=read(SOURCE),read(PRE)
    assert q['complete'] and pre['complete'] and not q['errors'] and all(q['gate'].values())
    audit=StageAudit(OUT,torch,[s['observed_package'] for s in q['series']],start)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],
        medical_observed_packages_loaded=0,real_folds_verified=0,real_counterfactuals_verified=0,
        model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,
        original_v1_failure_retained=True,statistics_C_copy_replay_explicit=True,
        validation_data_read=False,confirmation_patients_opened=False,locked_IXI_opened=False,
        task_effects_scored=False,theoretical_risk_certificate_issued=False,publication_claim_confirmed=False)
    path=OUT/'attempt01.json'

    def save():
        path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    save()
    try:
        for b in pre['source_bindings']:
            assert sha(ROOT/b['path'])==b['sha256'],b['path']
        r['source_bindings']=[entry(SOURCE),entry(PRE),entry(Path(__file__)),
            entry(ROOT/'OBSERVED_HOLDOUT_FEATURE_LAYOUT_V2_PROTOCOL_2026-10-08.md'),
            entry(ROOT/'experiments/common_projected_input_audit_2026_10_08.py')]
        r['resources_before']=audit.guard()
        for index,rec in enumerate(q['series']):
            audit.guard()
            p=ROOT/rec['observed_package']
            assert sha(p)==rec['observed_package_sha256']
            with np.load(p,allow_pickle=False) as package:
                a=package['observed_rcz'].copy()
                r['medical_observed_packages_loaded']+=1
                idx=package['observed_indices'].astype(int).tolist()
                shape=package['native_shape'].astype(int)
                affine=package['affine_rcz_ras'].copy()
            assert arrsha(a)==rec['observed_array_sha256']
            assert idx==rec['observed_indices']==list(range(0,int(shape[2]),4))
            assert shape.tolist()==rec['native_shape_rcz'] and np.array_equal(affine,rec['native_affine_rcz_ras'])
            spacing=float(np.linalg.norm(affine[:3,2]))
            assert spacing==rec['native_z_spacing_mm']
            assert abs(math.sqrt(math.fsum(float(x*x) for x in affine[:3,2]))-spacing)<=1e-12
            positions=np.asarray(idx,float)*spacing
            target=rec['target_rc']
            fold_records=[]
            for fold in (0,1):
                recorded=rec['folds'][fold]
                held=[i for i in range(1,len(idx)-1) if i%2==fold]
                kept=[i for i in range(len(idx)) if i not in held]
                assert held==recorded['heldout_ordinals'] and kept==recorded['retained_ordinals']
                assert [idx[i] for i in kept]==recorded['retained_native_z']
                assert positions[kept].tolist()==recorded['retained_positions_mm']
                assert positions[held].tolist()==recorded['heldout_positions_mm']
                st=own_statistics(a[:,:,kept])
                assert st==recorded['retained_statistics']
                previous_layout=original_arbitrary_layout_statistics(a[:,:,kept])
                if index==2 and fold==1:
                    assert previous_layout!=recorded['retained_statistics']
                layout_diagnostic=dict(previous_layout_matches_production=previous_layout==st,
                    mean_difference=previous_layout['mean']-st['mean'],
                    std_difference=previous_layout['population_std']-st['population_std'],
                    canonical_C_copy_matches_production=True)
                statistics_check=statistics_mathematics(a[:,:,kept],st)
                anchors,norm=library_projection(a[:,:,kept],target,st)
                assert arrsha(anchors)==recorded['shared_source_sha256']
                rc,expected=mathematical_projection_samples(norm,target,index,fold)
                projection_check=check(anchors[rc[:,0],rc[:,1],:],expected,'sampled_float32_coordinate_bilinear')
                replay,independent,definitions=predictions(anchors,positions[kept],positions[held])
                assert definitions==recorded['definitions']
                mathematical_checks=[]
                for kind in ('linear','pchip'):
                    assert arrsha(replay[kind])==recorded['prediction_sha256'][kind]
                    mathematical_checks.append(check(replay[kind],independent[kind],'full_nonuniform_'+kind))
                reference,_=library_projection(a[:,:,held],target,st)
                assert arrsha(reference)==recorded['reference_sha256']
                for kind in replay:
                    assert score(replay[kind],reference)==recorded['scores'][kind]
                for j,ordinal in enumerate(held):
                    plane=recorded['per_plane_scores'][j]
                    assert plane['observed_ordinal']==ordinal and plane['native_z']==idx[ordinal]
                    for kind in replay:
                        assert score(replay[kind][:,:,j],reference[:,:,j])==plane['scores'][kind]
                altered=a.copy()
                altered[:,:,held]+=np.float32(10000)
                counter_st=own_statistics(altered[:,:,kept])
                counter,_=library_projection(altered[:,:,kept],target,counter_st)
                counterpred,countermath,counterdefs=predictions(counter,positions[kept],positions[held])
                assert st==counter_st and arrsha(counter)==arrsha(anchors) and counterdefs==definitions
                assert all(arrsha(counterpred[k])==arrsha(replay[k]) for k in replay)
                newreference,_=library_projection(altered[:,:,held],target,counter_st)
                assert arrsha(newreference)!=arrsha(reference)
                assert all(score(counterpred[k],newreference)['MSE']!=recorded['scores'][k]['MSE'] for k in replay)
                old_all=own_statistics(a)
                altered_all=own_statistics(altered)
                assert old_all['mean']==recorded['counterfactual']['original_full_mean']
                assert altered_all['mean']==recorded['counterfactual']['counterfactual_full_mean']
                assert old_all['mean']!=altered_all['mean']
                fold_records.append(dict(fold=fold,source_and_prediction_library_hash_replay_exact=True,
                    source_projection_check=projection_check,independent_full_heldout_checks=mathematical_checks,
                    previous_layout_diagnostic=layout_diagnostic,independent_statistics_mathematics=statistics_check,
                    full_plane_scores_exact=True,per_plane_scores_exact=True,counterfactual_predictions_exact=True,
                    target_reference_and_scores_changed=True))
                r['real_folds_verified']+=1
                r['real_counterfactuals_verified']+=1
                del anchors,norm,replay,independent,reference,altered,counter,counterpred,countermath,newreference
                gc.collect()
                audit.guard()
            combined={}
            for kind in ('linear','pchip'):
                fold_scores=[f['scores'][kind] for f in rec['folds']]
                count=sum(s['elements'] for s in fold_scores)
                combined[kind]=math.fsum(s['sum_squared_error'] for s in fold_scores)/count
                assert abs(combined[kind]-rec['merged_scores'][kind]['MSE'])<=1e-12
            r['series'].append(dict(patient=rec['patient'],uid=rec['uid'],folds=fold_records,
                                    independently_aggregated_observed_MSE=combined))
            print(json.dumps(dict(index=index+1,patient=rec['patient'],real_folds_verified=2),ensure_ascii=False),flush=True)
            del a
            gc.collect()
            save()
        patients=[]
        for patient in sorted({s['patient'] for s in r['series']}):
            rows=[s for s in r['series'] if s['patient']==patient]
            mse={kind:math.fsum(s['independently_aggregated_observed_MSE'][kind] for s in rows)/len(rows) for kind in ('linear','pchip')}
            original=next(p for p in q['patient_features'] if p['patient']==patient)
            assert all(abs(mse[k]-original['series_equal_mean_MSE'][k])<=1e-12 for k in mse)
            patients.append(dict(patient=patient,series=len(rows),MSE=mse))
        assert len(patients)==11 and r['real_folds_verified']==r['real_counterfactuals_verified']==38
        overall={kind:math.fsum(p['MSE'][kind] for p in patients)/11 for kind in ('linear','pchip')}
        assert all(abs(overall[k]-q['patient_equal_observed_MSE'][k])<=1e-12 for k in overall)
        r['independent_patient_features']=patients
        r['independent_patient_equal_observed_MSE']=overall
        assert not audit.denied
        r['io_audit']=audit.result()
        r['gate']=dict(all19_package_reloads=True,all38_folds=True,independent_folds_and_retained_statistics=True,
            full_library_hash_replay_exact=True,independent_float32_coordinate_bilinear_samples=True,
            independent_nonuniform_Hermite_covers_all_heldout_pixels=True,all38_counterfactual_predictions_exact=True,
            whole_plane_and_per_plane_scores_exact=True,independent_patient_aggregation=True,no_native_GT_or_neural_IO=True,
            original_series3_fold1_layout_difference_reproduced=True,independent_statistics_mathematics=True)
        r['resources_after']=audit.guard()
        r['complete']=True
    except Exception as exc:
        r['errors'].append(type(exc).__name__+': '+str(exc))
        r['traceback']=traceback.format_exc()
        r['io_audit']=audit.result()
    r['elapsed_seconds']=time.perf_counter()-start
    r['finished_utc']=datetime.now(timezone.utc).isoformat()
    save()
    print(json.dumps(dict(complete=r['complete'],errors=r['errors'],series=len(r['series']),folds=r['real_folds_verified'],
        medical_observed_packages_loaded=r['medical_observed_packages_loaded'],elapsed_seconds=r['elapsed_seconds']),ensure_ascii=False),flush=True)
    return int(not r['complete'])


if __name__=='__main__':
    raise SystemExit(main())
