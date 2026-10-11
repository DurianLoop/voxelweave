"""Zero-forward authentication of completed20k training, all draws and checkpoint.

Original sampler and numbered planes check all source patch pixels. Primitive
metadata generation is shared; tensor assembly and source support are separately
constructed. This verifies implementation, not unseen-patient generalization.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):
    os.environ[key]='1'
import copy, hashlib, json, math, sys, traceback
from datetime import datetime, timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT, SEED, DEVELOPERS, GlobalLocalUNet, weight_hash, read, sha, array_sha,
    load_authenticated_observed, sparse_image, physical_shape, resize_image,
    resize_training_label, training_example, np, torch)
from mc_rc_task_metrics_cpu import independent_label
from mc_rc_coverage_augmentation_draw_cpu_support import legacy_primitive, record_sha
from verify_mc_rc_coverage_augmentation_draw_cpu import digest, spatial, reference_example
OUT=ROOT/'experiments/mc_rc_no_augmentation_all_development_cpu'


def write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate()
    source=OUT/'attempt_01.json';r=read(source)
    assert r['complete'] and not r['errors'], 'Do not verify or restart a live/failed training run.'
    path=OUT/'independent_all20000_draws_and_checkpoint_attempt_01.json'
    assert not path.exists(), 'Keep previous verifier attempts.'
    code=('mc_rc_global_local_task_cpu_support.py','mc_rc_task_metrics_cpu.py',
          'verify_mc_rc_coverage_augmentation_draw_cpu.py','mc_rc_coverage_augmentation_draw_cpu_support.py')
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        result_file=source.relative_to(ROOT).as_posix(),result_sha256=sha(source),script_sha256=sha(__file__),
        code_bindings=[dict(path='experiments/'+s,sha256=sha(ROOT/'experiments'/s)) for s in code],
        original_aug_example_checks=0,no_aug_reference_example_checks=0,same_rng_end_state_checks=0,
        full_patch_source_mapping_checks=0,primitive_metadata_sha_checks=0,inputs=[],
        primitive_metadata_generator_shared_with_production=True,
        reference='Original training_example plus separate tensor builder and numbered-plane source support.',
        network_forward_calls=0,training_updates=0,native_hidden_MR_pixels_decoded=False,
        confirmation_patients_opened=False,validation_patients_opened=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(path,q)
    try:
        assert r['seed']==SEED and r['device']=='cpu' and not r['gpu_initialized']
        assert not r['pretrained_weights_loaded'] and r['updates_completed']==r['updates_planned']==20000
        assert r['global_forward_calls']==r['local_forward_calls']==20000
        assert r['same_rng_final_state_checks']==r['old_aug_input_sha_matches']==len(r['training_draws'])==20000
        assert r['validation_neural_forwards_before_final_checkpoint']==0 and not r['confirmation_patients_opened']
        assert set(r['training_patient_ids'])==DEVELOPERS and r['model_parameters']==981602
        assert sha(ROOT/r['protocol_file'])==r['protocol_sha256']
        assert sha(ROOT/'experiments/run_mc_rc_no_augmentation_all_development_cpu.py')==r['script_sha256']
        for binding in r['source_bindings']+r['code_bindings']:
            assert sha(ROOT/binding['path'])==binding['sha256']
        prep=read(ROOT/r['source_bindings'][3]['path']);prod=read(ROOT/r['source_bindings'][4]['path'])
        cases=prep['cases'];assert len(cases)==19 and {c['patient'] for c in cases}==DEVELOPERS
        assert r['training_series_uids']==[c['uid'] for c in cases]
        by={s['uid']:s for s in prod['series']};bound={v['uid']:v for v in r['inputs']}
        cache={};grids={};numbered={}
        for case in cases:
            resource_gate();uid=case['uid'];obs=load_authenticated_observed(case,by[uid])
            native,stats=sparse_image(obs,'raw_pchip',by[uid]);label=independent_label(case)
            shape,spacing=physical_shape(case);image=resize_image(native,shape);target=resize_training_label(label,shape)
            values=dict(native_input_sha256=array_sha(native),native_label_sha256=array_sha(label),
                        physical_image_sha256=array_sha(image),physical_label_sha256=array_sha(target))
            assert all(bound[uid][k]==v for k,v in values.items())
            assert bound[uid]['observed_statistics']==stats and bound[uid]['physical_shape']==list(image.shape)
            cache[uid]=dict(image_zrc=image,label_zrc=target,native_foreground=np.argwhere(label),zspacing=spacing)
            plain=np.arange(shape[0]*shape[1],dtype=np.int32).reshape(shape);numbered[uid]=plain;grids[uid]={}
            for fr in (False,True):
                for fc in (False,True):
                    for k in range(4):
                        grids[uid][(fr,fc,k)]=spatial(plain,dict(flip_rows=fr,flip_cols=fc,rot90=k))
            q['inputs'].append(dict(patient=case['patient'],uid=uid,**values));write(path,q)
        patients=sorted(DEVELOPERS);patient_cases={p:[c for c in cases if c['patient']==p] for p in patients}
        rng=np.random.default_rng(SEED);stream=hashlib.sha256();patient_counts={};series_counts={}
        for step,published in enumerate(r['training_draws']):
            if step%100==0:resource_gate()
            patient=patients[int(rng.integers(len(patients)))];choices=patient_cases[patient]
            case=choices[int(rng.integers(len(choices)))];uid=case['uid'];item=cache[uid]
            assert published['step']==step and published['patient']==patient and published['uid']==uid
            original_rng=np.random.default_rng();original_rng.bit_generator.state=copy.deepcopy(rng.bit_generator.state)
            original=training_example(item,original_rng);record=legacy_primitive(item,rng,step,{})
            assert rng.bit_generator.state==original_rng.bit_generator.state;q['same_rng_end_state_checks']+=1
            assert digest(original)==published['original_aug_example_sha256'];q['original_aug_example_checks']+=1
            assert record['z']==published['z'] and original[4]==[tuple(v) for v in record['legacy_augmented_locations']]
            assert record_sha(record)==published['primitive_sha256'];q['primitive_metadata_sha_checks']+=1
            grid=grids[uid][(record['flip_rows'],record['flip_cols'],record['rot90'])];plain=numbered[uid]
            locations=[]
            for at in original[4]:
                ar,ac=at;patch=grid[ar:ar+128,ac:ac+128]
                nr=int(patch.min()//plain.shape[1]);nc=int((patch%plain.shape[1]).min())
                native_patch=plain[nr:nr+128,nc:nc+128]
                assert native_patch.shape==patch.shape==(128,128) and np.array_equal(spatial(native_patch,record),patch)
                locations.append([nr,nc]);q['full_patch_source_mapping_checks']+=1
            assert locations==published['native_patch_locations']==record['legacy_native_locations']
            independent_record=dict(record,legacy_native_locations=locations)
            reference=reference_example(item,independent_record,'legacy_none');value=digest(reference)
            assert value==published['example_sha256'];q['no_aug_reference_example_checks']+=1;stream.update(value.encode())
            patient_counts[patient]=patient_counts.get(patient,0)+1;series_counts[uid]=series_counts.get(uid,0)+1
            if (step+1)%1000==0:
                write(path,q);print(json.dumps(dict(draws_verified=step+1,whole_patch_mappings=q['full_patch_source_mapping_checks'])),flush=True)
        assert stream.hexdigest()==r['draw_stream_sha256'] and patient_counts==r['training_sampling_counts'] and series_counts==r['training_series_counts']
        assert set(series_counts)==set(cache) and sum(patient_counts.values())==20000
        assert [h['update'] for h in r['training_history']]==list(range(100,20001,100))
        for h in r['training_history']:
            expected=.0001+.0009*(1+math.cos(math.pi*(h['update']-1)/19999))/2
            assert abs(h['lr']-expected)<1e-15 and np.isfinite(h['last100_loss_mean']).all()
            assert h['resources']['own_process_below_normal_priority'] and h['resources']['workspace_free_bytes_before']>=15000000000
            assert h['resources']['available_physical_memory_before_bytes']>=8000000000
        assert r['first10_updates_seconds_per_update']<=2
        torch.manual_seed(SEED);model=GlobalLocalUNet()
        assert weight_hash(model)==r['initial_weights_sha256'] and sum(p.numel() for p in model.parameters())==981602
        cp=ROOT/r['checkpoint_file'];assert sha(cp)==r['checkpoint_sha256']
        checkpoint=torch.load(cp,map_location='cpu',weights_only=True)
        for k in ('updates_completed','seed','initial_weights_sha256','final_weights_sha256',
                  'training_patient_ids','training_series_uids','protocol_sha256','draw_stream_sha256'):
            assert checkpoint[k]==r[k]
        model.load_state_dict(checkpoint['state_dict'],strict=True);assert weight_hash(model)==r['final_weights_sha256']
        assert model.global_calls==model.local_calls==0 and sha(source)==q['result_sha256']
        q['gpu_initialized']=torch.cuda.is_initialized();assert not q['gpu_initialized']
        q['training_sampling_counts']=patient_counts;q['training_series_counts']=series_counts
        q['checkpoint_authenticated']=True;q['complete']=q['no_aug_reference_example_checks']==20000 and q['full_patch_source_mapping_checks']==40000
    except Exception as error:
        q['errors'].append(type(error).__name__+': '+str(error));q['traceback']=traceback.format_exc()
    q['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,q)
    print(json.dumps({k:q.get(k) for k in ('complete','errors','no_aug_reference_example_checks',
        'full_patch_source_mapping_checks','network_forward_calls','training_updates','checkpoint_authenticated')}),flush=True)
    return int(not q['complete'])


if __name__=='__main__':
    raise SystemExit(main())
