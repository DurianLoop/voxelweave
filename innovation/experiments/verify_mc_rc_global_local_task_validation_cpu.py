"""Independent counts and physical distances; alternate geometry with the same architecture."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[name]='1'
import json
import sys
import traceback
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT,read,sha,array_sha,np,torch,load_authenticated_observed,sparse_image,physical_shape,resize_image)
from mc_rc_global_local_geometry_reference_cpu import (
    physical_context_reference,resize_reference,tile_locations,grid_context_reference)
from mc_rc_task_metrics_cpu import independent_label,independent_counts,independent_surface
from mc_rc_global_local_evaluation_binding_cpu import frozen_bindings


def replay_plane(model,image,z,spacing,native_shape):
    axes,locations=tile_locations(image.shape[1:])
    coverage=np.zeros(image.shape[1:],np.uint16)
    plane=physical_context_reference(image,z,spacing)
    # The global image resize is already independently checked by pixel-center formulas.
    global_input=torch.nn.functional.interpolate(torch.from_numpy(plane)[None],
                    size=(256,256),mode='bilinear',align_corners=False)
    scores=np.zeros(image.shape[1:],np.float64)
    with torch.inference_mode():
        features,_=model.global_forward(global_input)
        features=features.numpy()[0]
        for start in range(0,len(locations),4):
            chunk=locations[start:start+4]
            context=np.stack([grid_context_reference(features,at,plane.shape[1:]) for at in chunk])
            patches=np.stack([plane[:,r:r+128,c:c+128] for r,c in chunk])
            output=model.local_forward(torch.from_numpy(patches),torch.from_numpy(context)).sigmoid().numpy()[:,0]
            assert np.isfinite(output).all()
            for (rr,cc),p in zip(chunk,output):
                scores[rr:rr+128,cc:cc+128]+=p
                coverage[rr:rr+128,cc:cc+128]+=1
    assert coverage.min()>0
    mapped=resize_reference(scores/coverage,native_shape[:2])
    return mapped>=.5,coverage,axes


def write(path,result):
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resource_gate()
    out=ROOT/'experiments/mc_rc_global_local_task_validation_cpu'
    source=out/'attempt_01.json'
    result=read(source)
    assert result['complete'] and not result['errors'] and len(result['evaluations'])==18
    path=out/'independent_metrics_and_checkpoint_attempt_01.json'
    assert not path.exists()
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        script_sha256=sha(__file__),result_sha256=sha(source),evaluations=[],
        checkpoint_replayed_planes=0,same_architecture_replay=True,
        second_independently_trained_model=False,native_hidden_MR_pixels_decoded=False,
        confirmation_patients_opened=False,scientific_confirmation_patients=0,
        publication_claim_confirmed=False)
    write(path,q)
    try:
        model,records,bindings=frozen_bindings()
        assert bindings==result['source_bindings']
        for item in result['code_bindings']:
            assert sha(ROOT/item['path'])==item['sha256']
        assert sha(ROOT/result['evaluation_protocol'])==result['evaluation_protocol_sha256']
        assert sha(ROOT/result['diagnostic_split_file'])==result['diagnostic_split_sha256']
        split=read(ROOT/result['diagnostic_split_file'])
        assert split['checkpoint_sha256']==result['checkpoint_sha256']
        assert split['validation_neural_forwards_at_freeze']==0
        assert not split['final_scientific_split_activated']
        cases={x['uid']:x for x in records['preparation']['cases']}
        by={x['uid']:x for x in records['production']['series']}
        seen=set()
        for evaluation in result['evaluations']:
            resource_gate()
            uid,method=evaluation['uid'],evaluation['method']
            assert (uid,method) not in seen and uid in cases and method in ('raw_pchip','raw_linear')
            seen.add((uid,method))
            case=cases[uid]
            assert case['patient']==evaluation['patient']
            label=independent_label(case)
            assert array_sha(label)==evaluation['label_array_sha256']
            prediction_file=ROOT/evaluation['prediction_file']
            assert sha(prediction_file)==evaluation['prediction_file_sha256']
            with np.load(prediction_file,allow_pickle=False) as data:
                assert data.files==['prediction_rcz']
                prediction=data['prediction_rcz'].copy()
            assert prediction.dtype==bool and prediction.shape==label.shape
            assert array_sha(prediction)==evaluation['prediction_array_sha256']
            n=prediction.shape[2]
            last=((n-1)//4)*4
            domains=dict(full=list(range(n)),anchors=list(range(0,n,4)),
                         missing=[z for z in range(last) if z%4],tail=list(range(last+1,n)))
            checks={}
            for domain,zs in domains.items():
                values=independent_counts(prediction[:,:,zs],label[:,:,zs])
                assert all(values[k]==evaluation['metrics'][domain][k] for k in values)
                checks[domain]=values
            distances=independent_surface(prediction,label,case['affine_rcz_ras'])
            original=evaluation['metrics']['full_surface']
            for key,value in distances.items():
                if value is None:
                    assert original[key] is None
                else:
                    assert abs(value-original[key])<.0001
            obs=load_authenticated_observed(case,by[uid])
            native,_=sparse_image(obs,method,by[uid])
            assert array_sha(native)==evaluation['input_sha256']
            shape,spacing=physical_shape(case)
            physical=resize_image(native,shape)
            assert array_sha(physical)==evaluation['physical_input_sha256']
            replay=[]
            for z in (0,n//2,n-1):
                direct,coverage,axes=replay_plane(model,physical,z,spacing,case['native_shape'])
                mismatches=int(np.count_nonzero(direct!=prediction[:,:,z]))
                q['last_replay_check']=dict(patient=case['patient'],uid=uid,method=method,z=z,
                                           thresholded_prediction_voxel_mismatches=mismatches)
                write(path,q)
                assert mismatches==0
                assert axes==[evaluation['coverage']['row_starts'],evaluation['coverage']['col_starts']]
                assert array_sha(coverage)==evaluation['coverage']['coverage_sha256']
                replay.append(z)
                q['checkpoint_replayed_planes']+=1
            q['evaluations'].append(dict(patient=case['patient'],uid=uid,method=method,
                independent_counts=checks,independent_kdtree_surface=distances,
                checkpoint_replayed_planes=replay,all_thresholded_replay_voxels_equal=True,
                tile_coverage_verified=True))
            write(path,q)
            print(json.dumps(dict(patient=case['patient'],uid=uid,method=method,
                    independent_counts_and_distances_passed=True,replayed_planes=len(replay))),flush=True)
            del prediction,label,native,physical,obs
        # Rebuild patient means from independent counts, without the producer aggregator.
        fields=('dice','recall','precision','absolute_relative_volume_error')
        for method in ('raw_pchip','raw_linear'):
            patients=sorted({e['patient'] for e in q['evaluations'] if e['method']==method})
            assert len(patients)==4
            for domain in ('full','missing','anchors','tail'):
                for field in fields:
                    means=[]
                    for patient in patients:
                        values=[e['independent_counts'][domain][field] for e in q['evaluations']
                                if e['method']==method and e['patient']==patient]
                        expected=float(np.mean(values)) if all(v is not None for v in values) else None
                        published=result['aggregate'][method]['patients'][patient]['metrics'][domain][field]
                        assert (published is None) if expected is None else abs(expected-published)<1e-12
                        means.append(expected)
                    expected=float(np.mean(means)) if all(v is not None for v in means) else None
                    published=result['aggregate'][method]['patient_first_means'][domain][field]
                    assert (published is None) if expected is None else abs(expected-published)<1e-12
        primary=[e for e in q['evaluations'] if e['method']=='raw_pchip']
        group_means={}
        for patient in sorted({e['patient'] for e in primary}):
            group=[e for e in primary if e['patient']==patient]
            group_means[patient]={d:{f:float(np.mean([e['independent_counts'][d][f] for e in group]))
                if all(e['independent_counts'][d][f] is not None for e in group) else None
                for f in fields} for d in ('full','missing')}
        mean=lambda d,f: (float(np.mean([g[d][f] for g in group_means.values()]))
                         if all(g[d][f] is not None for g in group_means.values()) else None)
        full_dice,missing_dice,recall,volume=[mean(d,f) for d,f in (
            ('full','dice'),('missing','dice'),('full','recall'),('full','absolute_relative_volume_error'))]
        gates=dict(mean_full_dice_ge_070=full_dice is not None and full_dice>=.70,
            mean_missing_dice_ge_065=missing_dice is not None and missing_dice>=.65,
            mean_full_recall_ge_070=recall is not None and recall>=.70,
            mean_full_absRVE_le_050=volume is not None and volume<=.50,
            all_four_patient_full_missing_dice_positive=all(g[d]['dice'] is not None and g[d]['dice']>0
                for g in group_means.values() for d in ('full','missing')),
            no_series_complete_miss=all(e['independent_counts']['full']['tp']>0 for e in primary))
        assert gates==result['capability_gate_checks']
        passed=all(gates.values())
        assert passed==result['capability_gate_passed']
        q['patient_first_aggregation_verified']=True
        q['capability_gate_passed']=passed
        q['global_forward_calls']=model.global_calls
        q['local_forward_calls']=model.local_calls
        q['gpu_initialized']=torch.cuda.is_initialized()
        assert not q['gpu_initialized'] and q['checkpoint_replayed_planes']==54 and len(seen)==18
        q['complete']=True
    except Exception as error:
        q['errors'].append(type(error).__name__+': '+str(error))
        q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat()
    write(path,q)
    print(json.dumps({k:q.get(k) for k in ('complete','errors','checkpoint_replayed_planes',
                    'global_forward_calls','local_forward_calls','gpu_initialized')}),flush=True)
    return int(not q['complete'])


if __name__=='__main__':
    raise SystemExit(main())
