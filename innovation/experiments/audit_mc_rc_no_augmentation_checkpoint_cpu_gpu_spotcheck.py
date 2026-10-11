"""Six fixed full planes, same trained weights, cross-device masks; no labels."""
from mc_rc_authorized_gpu_adapter import enable_authorized_gpu,CpuGeometryGpuBranches,gpu_resource_gate
import copy,json,sys,traceback
from datetime import datetime,timezone
from mc_rc_global_local_task_cpu_support import (
    ROOT,read,sha,array_sha,load_authenticated_observed,sparse_image,physical_shape,resize_image,infer_native,np,torch)
from mc_rc_no_augmentation_evaluation_binding_cpu import frozen_bindings


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    evaluation=ROOT/'experiments/mc_rc_no_augmentation_full_task_evaluation_gpu/attempt_01.json'
    verification=evaluation.parent/'independent_all37_metrics_and111_planes_attempt_01.json'
    source,proof=read(evaluation),read(verification)
    assert source['complete'] and not source['errors'] and proof['complete'] and not proof['errors']
    assert proof['result_sha256']==sha(evaluation) and proof['checkpoint_replayed_planes']==111
    out=ROOT/'experiments/mc_rc_no_augmentation_checkpoint_device_spotcheck';out.mkdir(exist_ok=False)
    path=out/'attempt_01.json';protocol=ROOT/'MC_RC_NO_AUGMENTATION_DEVICE_SPOTCHECK_PROTOCOL_2026-10-03.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        script_sha256=sha(__file__),protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (evaluation,verification)],
        code_bindings=[dict(path='experiments/'+s,sha256=sha(ROOT/'experiments'/s)) for s in (
            'mc_rc_authorized_gpu_adapter.py','mc_rc_global_local_task_cpu_support.py','mc_rc_no_augmentation_evaluation_binding_cpu.py')],
        planes=[],label_arrays_read=0,training_updates=0,confirmation_patients_opened=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False,
        scope='Fixed six-plane mask comparison only; not full37-volume probability equivalence.')
    def write():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    write()
    try:
        cpu,records,bindings=frozen_bindings();r['checkpoint_sha256']=records['training']['checkpoint_sha256']
        r['runtime']=enable_authorized_gpu();gpu=CpuGeometryGpuBranches(copy.deepcopy(cpu))
        for group in ('development','validation'):
            gpu_resource_gate();case=records[group]['cases'][0]
            row=next(v for v in records[group+'_inputs']['series'] if v['uid']==case['uid'])
            obs=load_authenticated_observed(case,row);native,stats=sparse_image(obs,'raw_pchip',row)
            shape,spacing=physical_shape(case);image=resize_image(native,shape);n=case['native_shape'][2]
            planes=(0,n//2,n-1)
            a,coverage_a=infer_native(cpu,image,spacing,case['native_shape'],only_planes=planes)
            b,coverage_b=infer_native(gpu,image,spacing,case['native_shape'],only_planes=planes)
            assert coverage_a==coverage_b
            for i,z in enumerate(planes):
                r['planes'].append(dict(group=group,patient=case['patient'],uid=case['uid'],z=z,
                    full_plane_shape=list(a[:,:,i].shape),cpu_mask_sha256=array_sha(a[:,:,i]),gpu_mask_sha256=array_sha(b[:,:,i]),
                    mismatched_voxels=int(np.count_nonzero(a[:,:,i]!=b[:,:,i])),cpu_foreground_voxels=int(a[:,:,i].sum()),
                    gpu_foreground_voxels=int(b[:,:,i].sum())))
            write();print(json.dumps(dict(group=group,patient=case['patient'],full_planes=3,mismatched_voxels=int(np.count_nonzero(a!=b)))),flush=True)
        r.update(cpu_global_forward_calls=cpu.global_calls,cpu_local_forward_calls=cpu.local_calls,
            gpu_global_forward_calls=gpu.global_calls,gpu_local_forward_calls=gpu.local_calls,
            mismatched_voxels=sum(v['mismatched_voxels'] for v in r['planes']),resources_after=gpu_resource_gate())
        assert sha(evaluation)==r['source_bindings'][0]['sha256'] and sha(verification)==r['source_bindings'][1]['sha256']
        r['complete']=len(r['planes'])==6
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','mismatched_voxels','cpu_global_forward_calls','cpu_local_forward_calls','gpu_global_forward_calls','gpu_local_forward_calls')}))
    return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
