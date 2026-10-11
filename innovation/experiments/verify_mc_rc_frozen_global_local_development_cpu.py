"""All19 source-label/metric checks and57 full-plane replay, reusing recorded independent algorithms."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,sys,traceback
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import ROOT,read,sha,array_sha,np,torch,load_authenticated_observed,sparse_image,physical_shape,resize_image
from mc_rc_global_local_evaluation_binding_cpu import frozen_bindings
from mc_rc_task_metrics_cpu import independent_label,independent_counts,independent_surface
from mc_rc_task_metrics_cpu import surface_points
from scipy.spatial.distance import cdist
from verify_mc_rc_global_local_task_validation_cpu import replay_plane
OUT=ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02'
def brute_surface(pred,label,affine):
    a,b=surface_points(pred,affine),surface_points(label,affine)
    def distances(first,second):
        output=np.full(len(first),np.inf)
        for begin in range(0,len(first),512):
            block=first[begin:begin+512];nearest=np.full(len(block),np.inf)
            for other in range(0,len(second),4096):nearest=np.minimum(nearest,cdist(block,second[other:other+4096]).min(axis=1))
            output[begin:begin+len(block)]=nearest
        return output
    d=np.concatenate((distances(a,b),distances(b,a)))
    return dict(assd_mm=float(np.mean(d)),hd95_mm=float(np.quantile(d,.95)),pairwise_distance_algorithm='bounded full pairwise scipy.cdist, no KDTree')
def write(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();source=OUT/'attempt_01.json';r=read(source)
    assert r['complete'] and not r['errors'] and len(r['evaluations'])==19
    path=OUT/'independent_metrics_and_checkpoint_attempt_01.json';assert not path.exists()
    reused=[ROOT/'experiments'/f for f in ('mc_rc_task_metrics_cpu.py','mc_rc_global_local_geometry_reference_cpu.py','verify_mc_rc_global_local_task_validation_cpu.py')]
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        result_sha256=sha(source),reused_algorithm_sources=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in reused],
        evaluations=[],checkpoint_replayed_planes=0,same_architecture_replay=True,second_independently_trained_model=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False,native_hidden_MR_pixels_decoded=False,confirmation_patients_opened=False)
    write(path,q)
    try:
        model,records,_=frozen_bindings();cases={c['uid']:c for c in records['development']['cases']}
        for item in r['source_bindings']+r['code_bindings']:assert sha(ROOT/item['path'])==item['sha256']
        assert sha(ROOT/r['protocol_file'])==r['protocol_sha256']
        prod=read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json');by={x['uid']:x for x in prod['series']}
        assert {e['uid'] for e in r['evaluations']}==set(cases)
        for e in r['evaluations']:
            resource_gate();case=cases[e['uid']];assert case['patient']==e['patient']
            label=independent_label(case);assert array_sha(label)==e['label_array_sha256']
            p=ROOT/e['prediction_file'];assert sha(p)==e['prediction_file_sha256']
            with np.load(p,allow_pickle=False) as data:prediction=data['prediction_rcz'].copy()
            assert prediction.dtype==bool and prediction.shape==label.shape and array_sha(prediction)==e['prediction_array_sha256']
            n=prediction.shape[2];last=(n-1)//4*4
            domains=dict(full=list(range(n)),anchors=list(range(0,n,4)),missing=[z for z in range(last) if z%4],tail=list(range(last+1,n)))
            counts={}
            for domain,planes in domains.items():
                values=independent_counts(prediction[:,:,planes],label[:,:,planes]);assert all(values[k]==e['metrics'][domain][k] for k in values);counts[domain]=values
            surface=independent_surface(prediction,label,case['affine_rcz_ras'])
            for key,value in surface.items():
                assert (e['metrics']['full_surface'][key] is None) if value is None else abs(value-e['metrics']['full_surface'][key])<.0001
            basis=np.asarray(case['affine_rcz_ras'])[:3,:3];unit=basis/np.linalg.norm(basis,axis=0)
            residual=float(abs(unit.T@unit-np.eye(3)).max());brute=None
            if residual>1e-5 and prediction.any() and label.any():
                brute=brute_surface(prediction,label,case['affine_rcz_ras'])
                assert abs(brute['assd_mm']-surface['assd_mm'])<1e-7 and abs(brute['hd95_mm']-surface['hd95_mm'])<1e-7
            obs=load_authenticated_observed(case,by[e['uid']]);native,_=sparse_image(obs,'raw_pchip',by[e['uid']])
            assert array_sha(native)==e['input_sha256'];shape,spacing=physical_shape(case);physical=resize_image(native,shape)
            assert array_sha(physical)==e['physical_input_sha256'];replayed=[]
            for z in (0,n//2,n-1):
                direct,cov,axes=replay_plane(model,physical,z,spacing,case['native_shape'])
                mismatch=int(np.count_nonzero(direct!=prediction[:,:,z]));q['last_replay_check']=dict(uid=e['uid'],z=z,voxel_mismatches=mismatch);write(path,q)
                assert mismatch==0 and axes==[e['coverage']['row_starts'],e['coverage']['col_starts']]
                assert array_sha(cov)==e['coverage']['coverage_sha256'];replayed.append(z);q['checkpoint_replayed_planes']+=1
            q['evaluations'].append(dict(patient=e['patient'],uid=e['uid'],independent_counts=counts,
                independent_kdtree_surface=surface,nonorthogonal_bruteforce_surface=brute,
                maximum_axis_orthogonality_residual=residual,checkpoint_replayed_planes=replayed));write(path,q)
            print(json.dumps(dict(patient=e['patient'],uid=e['uid'],independent_metrics_passed=True,replayed_planes=3)),flush=True)
            del prediction,label,native,physical,obs
        for domain in ('full','missing','anchors','tail'):
            for field in ('dice','precision','recall','signed_relative_volume_error','absolute_relative_volume_error'):
                means=[]
                for patient,published in r['aggregate']['patients'].items():
                    values=[e['independent_counts'][domain][field] for e in q['evaluations'] if e['patient']==patient]
                    expected=float(np.mean(values)) if all(v is not None for v in values) else None
                    actual=published['metrics'][domain][field];assert (actual is None) if expected is None else abs(expected-actual)<1e-12;means.append(expected)
                expected=float(np.mean(means)) if all(v is not None for v in means) else None
                actual=r['aggregate']['patient_first_means'][domain][field];assert (actual is None) if expected is None else abs(expected-actual)<1e-12
        q['patient_first_aggregation_verified']=True;q['global_forward_calls']=model.global_calls;q['local_forward_calls']=model.local_calls
        q['gpu_initialized']=torch.cuda.is_initialized();assert not q['gpu_initialized']
        q['complete']=len(q['evaluations'])==19 and q['checkpoint_replayed_planes']==57
    except Exception as error:q['errors'].append(type(error).__name__+': '+str(error));q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,q)
    print(json.dumps({k:q.get(k) for k in ('complete','errors','checkpoint_replayed_planes','global_forward_calls','local_forward_calls')}),flush=True)
    return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
