"""608 real input draws, two pending factor arms, zero neural forwards or updates."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import copy,json,sys,traceback
from datetime import datetime,timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT,SEED,DEVELOPERS,read,sha,array_sha,load_authenticated_observed,sparse_image,
    physical_shape,resize_image,resize_training_label,training_example,context_plane,np,torch,F)
from mc_rc_task_metrics_cpu import independent_label
from mc_rc_coverage_augmentation_draw_cpu_support import (
    legacy_primitive,example_from_record,example_sha,record_sha)
from mc_rc_partial_augmentation_cpu_support import PARTIAL_ARMS,partial_example
from verify_mc_rc_coverage_augmentation_draw_cpu import spatial,digest,reference_example
OUT=ROOT/'experiments/mc_rc_partial_augmentation_development_cpu_preflight'


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def reference_partial(item,record,arm):
    geometric=arm=='geometry_only'
    raw=context_plane(item['image_zrc'],record['z'],item['zspacing'])
    label=item['label_zrc'][record['z']]
    plane=spatial(raw,record) if geometric else raw*record['scale']+record['shift']
    target=spatial(label,record) if geometric else label
    plane=np.ascontiguousarray(plane,dtype=np.float32)
    target=np.ascontiguousarray(target,dtype=np.float32)
    locations=[tuple(at) for at in record['legacy_'+('augmented' if geometric else 'native')+'_locations']]
    gx=F.interpolate(torch.from_numpy(plane)[None],size=(256,256),mode='bilinear',align_corners=False)
    gy=F.interpolate(torch.from_numpy(target)[None,None],size=(256,256),mode='area')
    patches=torch.from_numpy(np.stack([plane[:,r:r+128,c:c+128] for r,c in locations]))
    labels=torch.from_numpy(np.stack([target[r:r+128,c:c+128][None] for r,c in locations]))
    return gx,patches,labels,gy,locations,target.shape,dict(z=record['z'],foreground_plane=record['foreground_plane'])


def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate()
    sources=[ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json',
        ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json',
        ROOT/'experiments/mc_rc_development_training_input_cpu/independent_all19_observed_inputs_and_label_axes_attempt_01.json',
        ROOT/'experiments/mc_rc_no_augmentation_development_cpu_preflight/attempt_01.json']
    prep,prod,proof,old=[read(p) for p in sources]
    assert all(v['complete'] and not v['errors'] for v in (prep,prod,proof,old))
    assert proof['result_sha256']==sha(sources[1]) and len(prep['cases'])==19
    assert {c['patient'] for c in prep['cases']}==DEVELOPERS
    OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    protocol=ROOT/'MC_RC_PARTIAL_AUGMENTATION_PREFLIGHT_CPU_PROTOCOL_2026-10-03.md'
    code=('mc_rc_global_local_task_cpu_support.py','mc_rc_partial_augmentation_cpu_support.py',
          'mc_rc_coverage_augmentation_draw_cpu_support.py','verify_mc_rc_coverage_augmentation_draw_cpu.py',
          'mc_rc_task_metrics_cpu.py')
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],resources=resources,
        script_sha256=sha(__file__),protocol_file=protocol.relative_to(ROOT).as_posix(),protocol_sha256=sha(protocol),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources],
        code_bindings=[dict(path='experiments/'+s,sha256=sha(ROOT/'experiments'/s)) for s in code],
        series=[],seed=SEED,same_rng_end_state_checks=0,legacy_aug_exact_input_checks=0,
        legacy_none_exact_input_checks=0,partial_arm_reference_input_checks=0,
        frozen_primitive_matches=0,full_patch_source_mapping_checks=0,arm_target_identity_checks=0,
        network_forward_calls=0,training_updates=0,validation_patients_opened=False,
        confirmation_patients_opened=False,native_hidden_MR_pixels_decoded=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False,
        independence_limit='Primitive/context and interpolation libraries shared; original sampler, separate tensor assembly and numbered source pixels checked.')
    write(path,r)
    try:
        for binding in old['code_bindings']+old['source_bindings']:
            assert sha(ROOT/binding['path'])==binding['sha256']
        by={v['uid']:v for v in prod['series']};previous={v['uid']:v for v in old['series']}
        for case in prep['cases']:
            resource_gate();uid=case['uid'];row=by[uid];obs=load_authenticated_observed(case,row)
            native,stats=sparse_image(obs,'raw_pchip',row);label=independent_label(case)
            shape,spacing=physical_shape(case);image=resize_image(native,shape);target=resize_training_label(label,shape)
            values=dict(native_input_sha256=array_sha(native),native_label_sha256=array_sha(label),
                physical_image_sha256=array_sha(image),physical_label_sha256=array_sha(target))
            assert all(previous[uid][k]==v for k,v in values.items())
            item=dict(image_zrc=image,label_zrc=target,native_foreground=np.argwhere(label),zspacing=spacing)
            numbered=np.arange(shape[0]*shape[1],dtype=np.int32).reshape(shape)
            rng=np.random.default_rng(SEED);draws=[]
            for step in range(32):
                original_rng=np.random.default_rng();original_rng.bit_generator.state=copy.deepcopy(rng.bit_generator.state)
                original=training_example(item,original_rng);record=legacy_primitive(item,rng,step,{})
                assert rng.bit_generator.state==original_rng.bit_generator.state;r['same_rng_end_state_checks']+=1
                prior=previous[uid]['draws'][step]
                # Coverage cursors are reset in the previous no-augmentation wrapper as well.
                assert record==prior['augmentation'];r['frozen_primitive_matches']+=1
                both=example_from_record(item,record,'legacy_aug');none=example_from_record(item,record,'legacy_none')
                assert example_sha(original)==example_sha(both)==prior['old_aug_example_sha256'];r['legacy_aug_exact_input_checks']+=1
                assert example_sha(none)==digest(reference_example(item,record,'legacy_none'))==prior['new_none_example_sha256'];r['legacy_none_exact_input_checks']+=1
                aug_numbered=spatial(numbered,record)
                for (nr,nc),(ar,ac) in zip(record['legacy_native_locations'],record['legacy_augmented_locations']):
                    p=numbered[nr:nr+128,nc:nc+128];a=aug_numbered[ar:ar+128,ac:ac+128]
                    assert p.shape==a.shape==(128,128) and np.array_equal(spatial(p,record),a)
                    r['full_patch_source_mapping_checks']+=1
                arm_records={}
                for arm in PARTIAL_ARMS:
                    value=partial_example(item,record,arm);reference=reference_partial(item,record,arm)
                    assert example_sha(value)==digest(reference);r['partial_arm_reference_input_checks']+=1
                    baseline=both if arm=='geometry_only' else none
                    assert torch.equal(value[2],baseline[2]) and torch.equal(value[3],baseline[3])
                    assert value[4:]==baseline[4:];r['arm_target_identity_checks']+=1
                    arm_records[arm]=dict(example_sha256=example_sha(value),patch_foreground_mass=float(value[2].sum()))
                draws.append(dict(step=step,z=record['z'],primitive_sha256=record_sha(record),arms=arm_records))
            r['series'].append(dict(patient=case['patient'],uid=uid,**values,observed_statistics=stats,
                                   physical_shape=list(image.shape),zspacing_mm=spacing,draws=draws))
            write(path,r);print(json.dumps(dict(series_prepared=len(r['series']),draws=r['same_rng_end_state_checks'],partial_inputs=r['partial_arm_reference_input_checks'])),flush=True)
            del native,label,image,target,item,numbered,obs
        r['gpu_initialized']=torch.cuda.is_initialized();assert not r['gpu_initialized']
        r['complete']=(len(r['series'])==19 and r['same_rng_end_state_checks']==r['legacy_aug_exact_input_checks']==r['legacy_none_exact_input_checks']==r['frozen_primitive_matches']==608
            and r['partial_arm_reference_input_checks']==r['full_patch_source_mapping_checks']==r['arm_target_identity_checks']==1216)
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','same_rng_end_state_checks','partial_arm_reference_input_checks','full_patch_source_mapping_checks','network_forward_calls','training_updates')}),flush=True)
    return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
