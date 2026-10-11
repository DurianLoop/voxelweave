"""All37 independent label/count/surface checks and111 complete native-plane replays."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import json, sys, traceback
from datetime import datetime, timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT, DEVELOPERS, VALIDATORS, read, sha, array_sha, load_authenticated_observed,
    sparse_image, physical_shape, resize_image, np, torch)
from mc_rc_task_metrics_cpu import independent_label,independent_counts,independent_surface
from verify_mc_rc_global_local_task_validation_cpu import replay_plane
from mc_rc_no_augmentation_evaluation_binding_cpu import frozen_bindings
OUT=ROOT/'experiments/mc_rc_no_augmentation_full_task_evaluation_cpu'


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def verify_aggregate(rows,published,patients,methods):
    fields=('dice','precision','recall','signed_relative_volume_error','absolute_relative_volume_error')
    output={}
    for method in methods:
        groups={}
        for patient in sorted(patients):
            entries=[e for e in rows if e['method']==method and e['patient']==patient];assert entries
            groups[patient]={}
            for domain in ('full','missing','anchors','tail'):
                groups[patient][domain]={}
                for field in fields:
                    data=[e['independent_counts'][domain][field] for e in entries]
                    expected=float(np.mean(data)) if all(v is not None for v in data) else None
                    p=published[method]['patients'][patient]['metrics'][domain]
                    if expected is None:assert p[field] is None
                    else:assert abs(p[field]-expected)<1e-12
                    assert p[field+'_defined_series']==sum(v is not None for v in data)
                    groups[patient][domain][field]=expected
            assert published[method]['patients'][patient]['series']==len(entries)
        means={}
        for domain in ('full','missing','anchors','tail'):
            means[domain]={}
            for field in fields:
                data=[g[domain][field] for g in groups.values()]
                expected=float(np.mean(data)) if all(v is not None for v in data) else None
                p=published[method]['patient_first_means'][domain]
                if expected is None:assert p[field] is None
                else:assert abs(p[field]-expected)<1e-12
                assert p[field+'_defined_patients']==sum(v is not None for v in data)
                means[domain][field]=expected
        misses=[e['uid'] for e in rows if e['method']==method and e['independent_counts']['full']['tp']==0]
        empties=[e['uid'] for e in rows if e['method']==method and e['independent_counts']['full']['empty_prediction']]
        assert misses==published[method]['complete_miss_series'] and empties==published[method]['empty_prediction_series']
        output[method]=dict(patients=groups,patient_first_means=means,complete_miss_series=misses)
    return output


def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate()
    source=OUT/'attempt_01.json';r=read(source)
    assert r['complete'] and not r['errors'] and len(r['evaluations'])==37
    path=OUT/'independent_all37_metrics_and111_planes_attempt_01.json'
    assert not path.exists()
    code=('mc_rc_task_metrics_cpu.py','verify_mc_rc_global_local_task_validation_cpu.py',
          'mc_rc_global_local_geometry_reference_cpu.py','mc_rc_no_augmentation_evaluation_binding_cpu.py')
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],result_sha256=sha(source),
        script_sha256=sha(__file__),code_bindings=[dict(path='experiments/'+s,sha256=sha(ROOT/'experiments'/s)) for s in code],
        evaluations=[],checkpoint_replayed_planes=0,same_architecture_replay=True,second_independently_trained_model=False,
        training_updates=0,native_hidden_MR_pixels_decoded=False,confirmation_patients_opened=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False,
        surface_reference='Different surface-mask construction; full affine coordinates; shared scipy KDTree distance library.')
    write(path,q)
    try:
        model,records,bindings=frozen_bindings();assert bindings==r['source_bindings']
        for item in r['code_bindings']:assert sha(ROOT/item['path'])==item['sha256']
        assert sha(ROOT/r['protocol_file'])==r['protocol_sha256'] and sha(ROOT/r['split_file'])==r['split_sha256']
        split=read(ROOT/r['split_file']);assert split['validation_neural_forwards_at_freeze']==0
        assert not split['confirmation_patients_opened'] and not split['final_scientific_split_activated']
        assert split['checkpoint_sha256']==r['checkpoint_sha256']==records['training']['checkpoint_sha256']
        assert r['threshold']==.5 and r['device']=='cpu' and r['new_training_updates']==0
        case_sets={group:{c['uid']:c for c in records[group]['cases']} for group in ('development','validation')}
        inputs={group:{s['uid']:s for s in records[group+'_inputs']['series']} for group in case_sets}
        expected=[(group,c['uid'],method) for group,methods in (('development',('raw_pchip',)),('validation',('raw_pchip','raw_linear')))
                  for c in records[group]['cases'] for method in methods]
        assert [(e['group'],e['uid'],e['method']) for e in r['evaluations']]==expected
        for e in r['evaluations']:
            resource_gate();group,uid,method=e['group'],e['uid'],e['method'];case=case_sets[group][uid]
            assert case['patient']==e['patient']
            label=independent_label(case);assert array_sha(label)==e['label_array_sha256']==inputs[group][uid]['label_array_sha256']
            pp=ROOT/e['prediction_file'];assert sha(pp)==e['prediction_file_sha256']
            with np.load(pp,allow_pickle=False) as data:
                assert data.files==['prediction_rcz'];pred=data['prediction_rcz'].copy()
            assert pred.dtype==bool and pred.shape==label.shape==tuple(case['native_shape']) and array_sha(pred)==e['prediction_array_sha256']
            n=pred.shape[2];last=(n-1)//4*4
            domains=dict(full=list(range(n)),anchors=list(range(0,n,4)),missing=[z for z in range(last) if z%4],tail=list(range(last+1,n)))
            counts={}
            for domain,zs in domains.items():
                values=independent_counts(pred[:,:,zs],label[:,:,zs])
                assert all(e['metrics'][domain][k]==v for k,v in values.items())
                if domain!='full':assert e['metrics'][domain]['planes']==len(zs)
                counts[domain]=values
            distances=independent_surface(pred,label,case['affine_rcz_ras'])
            for key,value in distances.items():
                if value is None:assert e['metrics']['full_surface'][key] is None
                else:assert abs(e['metrics']['full_surface'][key]-value)<.0001
            basis=np.asarray(case['affine_rcz_ras'])[:3,:3]
            assert abs(e['metrics']['voxel_volume_mm3']-abs(float(np.linalg.det(basis))))<1e-12
            obs=load_authenticated_observed(case,inputs[group][uid]);native,stats=sparse_image(obs,method,inputs[group][uid])
            assert array_sha(native)==e['input_sha256'] and stats==e['observed_statistics']
            shape,spacing=physical_shape(case);image=resize_image(native,shape)
            assert array_sha(image)==e['physical_input_sha256'] and spacing==e['zspacing_mm']
            cov=e['coverage'];assert cov['physical_input_shape']==list(image.shape) and cov['planes']==list(range(n))
            assert e['global_forward_calls']==n and e['local_forward_calls']==n*((cov['tiles_per_plane']+3)//4)
            planes=[]
            for z in (0,n//2,n-1):
                direct,coverage,axes=replay_plane(model,image,z,spacing,case['native_shape'])
                mismatch=int(np.count_nonzero(direct!=pred[:,:,z]));q['last_replay_check']=dict(group=group,uid=uid,method=method,z=z,mismatched_voxels=mismatch)
                write(path,q)
                assert mismatch==0 and array_sha(coverage)==cov['coverage_sha256']
                assert axes==[cov['row_starts'],cov['col_starts']] and coverage.min()==cov['coverage_min'] and coverage.max()==cov['coverage_max']
                planes.append(z);q['checkpoint_replayed_planes']+=1
            q['evaluations'].append(dict(group=group,patient=e['patient'],uid=uid,method=method,
                independent_counts=counts,independent_full_affine_surface=distances,
                checkpoint_replayed_planes=planes,all_replayed_voxels_equal=True))
            write(path,q);print(json.dumps(dict(group=group,patient=e['patient'],method=method,metrics_verified=True,complete_planes_replayed=3)),flush=True)
            del pred,label,image,native,obs
        dev=[e for e in q['evaluations'] if e['group']=='development'];val=[e for e in q['evaluations'] if e['group']=='validation']
        q['development_aggregate']=verify_aggregate(dev,r['development_aggregate'],DEVELOPERS,('raw_pchip',))
        q['validation_aggregate']=verify_aggregate(val,r['validation_aggregate'],VALIDATORS,('raw_pchip','raw_linear'))
        primary=q['validation_aggregate']['raw_pchip'];f=primary['patient_first_means']['full'];m=primary['patient_first_means']['missing']
        gates=dict(mean_full_dice_ge_070=f['dice'] is not None and f['dice']>=.70,
            mean_missing_dice_ge_065=m['dice'] is not None and m['dice']>=.65,
            mean_full_recall_ge_070=f['recall'] is not None and f['recall']>=.70,
            mean_full_absRVE_le_050=f['absolute_relative_volume_error'] is not None and f['absolute_relative_volume_error']<=.50,
            all_four_patient_full_missing_dice_positive=all(g[d]['dice'] is not None and g[d]['dice']>0 for g in primary['patients'].values() for d in ('full','missing')),
            no_series_complete_miss=all(e['independent_counts']['full']['tp']>0 for e in val if e['method']=='raw_pchip'))
        assert gates==r['capability_gate_checks'] and all(gates.values())==r['capability_gate_passed']
        assert r['global_forward_calls']==sum(e['global_forward_calls'] for e in r['evaluations'])
        assert r['local_forward_calls']==sum(e['local_forward_calls'] for e in r['evaluations'])
        assert sha(source)==q['result_sha256'] and q['checkpoint_replayed_planes']==111
        q.update(global_forward_calls=model.global_calls,local_forward_calls=model.local_calls,
                 capability_gate_passed=r['capability_gate_passed'],gpu_initialized=torch.cuda.is_initialized())
        assert not q['gpu_initialized'];q['complete']=len(q['evaluations'])==37
    except Exception as error:
        q['errors'].append(type(error).__name__+': '+str(error));q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,q)
    print(json.dumps({k:q.get(k) for k in ('complete','errors','capability_gate_passed','checkpoint_replayed_planes','global_forward_calls','local_forward_calls')}),flush=True)
    return int(not q['complete'])


if __name__=='__main__':
    raise SystemExit(main())
