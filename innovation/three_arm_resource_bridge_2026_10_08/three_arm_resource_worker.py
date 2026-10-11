"""Three observed representations sharing the certified paired update/FOV primitives."""
import copy,gc,io,time
from dataclasses import asdict
import numpy as np
import mc_rc_3d_paired_resource_worker_2026_10_07 as old
from mc_rc_common_projected_observed_2026_10_08 import shared_source,projected_pair_fields

torch=old.torch
ROOT=old.ROOT
PATCH=old.PATCH
SEED=old.SEED
array_sha=old.array_sha
ARMS=('legacy_dense','direct','common_projected_dense')
SELECT={'legacy_dense':('dense','dense'),'direct':('numerator','direct'),'common_projected_dense':('common_dense','dense')}
FIELDS=('dense','numerator','common_dense','availability','valid_grid','target')

def three_fields(observed,grid):
    legacy,st,native=old.physical_fields(observed,grid)
    source,normalized_hash=shared_source(observed,grid)
    projected,projected_native=projected_pair_fields(source,grid)
    assert source.observed_statistics==st
    assert np.array_equal(legacy['availability'],projected['availability'])
    assert np.array_equal(legacy['valid_grid'],projected['valid_grid'])
    fields=dict(legacy,common_dense=projected['dense'])
    return fields,st,dict(legacy_native_hashes=native,projected_native_hashes=projected_native,
        normalized_observed_sha256=normalized_hash,shared_projected_anchors_sha256=array_sha(source.anchors_rca),
        projected_numerator_sha256=array_sha(projected['numerator']),
        direct_projected_equal=np.array_equal(legacy['numerator'],projected['numerator']),
        direct_projected_max_difference=float(np.max(np.abs(legacy['numerator']-projected['numerator']))))

def arm_view(bundle,name):
    if name not in SELECT:raise ValueError('Unknown representation arm: '+str(name))
    field,semantic=SELECT[name]
    # Alias every shared field; old update chooses dense or numerator by semantic.
    view=dict(bundle)
    view['dense' if semantic=='dense' else 'numerator']=bundle[field]
    assert all(view[k] is bundle[k] for k in ('availability','valid_grid','target'))
    assert view['dense' if semantic=='dense' else 'numerator'] is bundle[field]
    return view,semantic,field

def run_workflow(cache,stream,device,guard,save,r,representative_uid):
    assert len(stream)>=2 and {x['uid'] for x in stream}==set(cache)
    for bundle in cache.values():
        arrays=[bundle[k] for k in FIELDS]
        assert all(x.dtype==np.float32 and x.shape==arrays[0].shape for x in arrays)
        assert all(n>=p for n,p in zip(arrays[0].shape,PATCH))
    tick=time.perf_counter();draws=[]
    for step,item in enumerate(stream):
        guard();draws.append(old.draw_training_batch(cache[item['uid']]['target'],np.random.default_rng(np.random.SeedSequence([SEED,813,step]))))
    r['draw_materialization_seconds']=time.perf_counter()-tick
    r['shared_training_draws']=[dict(**item,draws=[asdict(d) for d in ds]) for item,ds in zip(stream,draws)]
    _,initial=old.canonical_states();initsha=old.statehash(initial)
    previous=old.read(ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json')
    assert initsha==previous['model_checks']['canonical_two_state_sha256']
    r.update(parameter_count_expected=1401795,canonical_two_channel_state_sha256=initsha,arms=[],
        actual_resource_updates=0,attempted_model_forward_calls=0,completed_model_forward_calls=0)
    save()
    for name in ARMS:
        guard();model=old.two_channel_model(initial).to(device)
        opt=torch.optim.AdamW(model.parameters(),lr=.0001,weight_decay=.0001)
        assert sum(p.numel() for p in model.parameters())==r['parameter_count_expected']
        assert old.statehash(model.state_dict())==initsha
        arm=dict(kind=name,complete=False,history=[],initial_weights_sha256=initsha,planned_updates=len(stream),
            checkpoint_storage='memory_only',updated_weights_saved=False,FOV_passes=[],parameter_count=1401795)
        r['arms'].append(arm);checkpoint=None;save()
        for step,(item,ds) in enumerate(zip(stream,draws)):
            view,semantic,field=arm_view(cache[item['uid']],name)
            h=old.update(model,opt,view,ds,semantic,device,guard,r)
            h.update({**item,'step':step+1,'warmup':step<2,'selected_field':field,'augmentation_semantic':semantic,
                'selected_full_field_sha256':array_sha(cache[item['uid']][field])})
            arm['history'].append(h)
            if step==0:
                state=old.snapshot(model,opt,1,device);buffer=io.BytesIO();torch.save(state,buffer)
                checkpoint=buffer.getvalue();arm['checkpoint_bytes']=len(checkpoint);del state,buffer
            if step==1:
                continuous=old.snapshot(model,opt,2,device)
                restored=torch.load(io.BytesIO(checkpoint),map_location='cpu',weights_only=True)
                resumed=old.two_channel_model(initial).to(device)
                resumed_opt=torch.optim.AdamW(resumed.parameters(),lr=.0001,weight_decay=.0001)
                resumed.load_state_dict(restored['model']);resumed_opt.load_state_dict(restored['optimizer'])
                torch.set_rng_state(restored['torch_rng'])
                if device!='cpu':torch.cuda.set_rng_state(restored['cuda_rng'],0)
                again=old.update(resumed,resumed_opt,view,ds,semantic,device,guard,r)
                for key in ('loss','input_batch_sha256','label_batch_sha256','label_foreground','gradient_groups','mask_gradient_max'):
                    assert h[key]==again[key],(name,key)
                assert old.exact(continuous,old.snapshot(resumed,resumed_opt,2,device))
                arm['resume_check']=dict(full_model_optimizer_RNG_tree_exact=True,replayed_step=2,
                    replay_input_batch_sha256=again['input_batch_sha256'],replay_label_batch_sha256=again['label_batch_sha256'],
                    replay_loss=again['loss'],extra_resource_updates=1,replay_total_update_seconds=again['total_update_seconds'])
                del resumed,resumed_opt,restored,continuous;gc.collect()
            save()
        bundle=cache[representative_uid];field,semantic=SELECT[name]
        wrapped=old.GuardedInferenceModel(model,device,guard,r)
        for repeat in range(2):
            guard();tick=time.perf_counter()
            native,physical,meta=old.infer_two_channel_full_fov(wrapped,bundle[field],bundle['availability'],bundle['grid'],bundle['native_shape_rcz'],device=device)
            elapsed=time.perf_counter()-tick;guard()
            assert np.isfinite(native).all() and np.isfinite(physical).all()
            arm['FOV_passes'].append(dict(repeat=repeat+1,uid=representative_uid,selected_field=field,
                selected_full_field_sha256=array_sha(bundle[field]),elapsed_seconds=elapsed,metadata=meta,
                probability_arrays_saved=False,task_effects_scored=False))
            del native,physical;gc.collect();save()
        assert arm['FOV_passes'][0]['metadata']==arm['FOV_passes'][1]['metadata']
        arm.update(complete=True,original_stream_updates=len(stream),actual_resource_updates=len(stream)+1,
            FOV_repeat_exact=True,discarded_final_weights_sha256=old.statehash(model.state_dict()))
        assert arm['discarded_final_weights_sha256']!=initsha
        del model,opt,checkpoint,wrapped;gc.collect()
        if device!='cpu':torch.cuda.empty_cache()
        guard();save()
    keys=('step','patient','uid','label_batch_sha256','label_foreground')
    histories=[[[h[k] for k in keys] for h in a['history']] for a in r['arms']]
    assert histories[0]==histories[1]==histories[2]
    r['gate']=dict(shared_draws_and_supervision=True,equal_initialization_capacity=True,
        all_branch_and_mask_gradients_finite_nonzero=True,three_memory_checkpoint_resumes_exact=True,
        complete_representative_FOV_and_repeat_exact=True,
        planned_resource_updates_completed=r['actual_resource_updates']==3*(len(stream)+1),
        explicit_three_representation_dispatch=True,no_updated_weights_saved=True,no_task_effects_scored=True)
    assert all(r['gate'].values());save()

def load_real_development(guard,save,r):
    from qualify_mc_rc_3d_19series_cpu_low_lr_2026_10_07 import stream_for
    cases=old.development_observed_cases();assert len(cases)==19 and len({c['patient'] for c,row in cases})==11
    cert={x['uid']:x for x in old.read(ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json')['series']}
    projected={x['uid']:x for x in old.read(ROOT/'experiments/common_projected_observed_qualification_2026_10_08/attempt01.json')['series']}
    target_cert=old.read(ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json')
    targets={x['uid']:x for x in next(a for a in target_cert['arms'] if a['kind']=='raw_pchip')['cache_records']}
    cache={};records=[];tick=time.perf_counter()
    for case,row in cases:
        guard();at=time.perf_counter();uid=case['uid'];grid=cert[uid]['grid']
        observed=old.load_development_observed(case,row);r['MRI_observed_packages_loaded']+=1
        fields,st,metadata=three_fields(observed,grid)
        for key in ('dense','numerator','availability'):assert array_sha(fields[key])==cert[uid]['physical_'+key+'_sha256']
        assert array_sha(fields['common_dense'])==projected[uid]['physical_dense_sha256']
        assert array_sha(fields['valid_grid'])==projected[uid]['physical_valid_grid_sha256']
        assert metadata['projected_numerator_sha256']==projected[uid]['physical_numerator_sha256']==array_sha(fields['numerator'])
        assert metadata['direct_projected_equal']
        gt=old.read_reference_label(case);r['development_GT_loaded']+=1;target=old.physical_label(gt,grid)
        assert array_sha(target)==targets[uid]['label_sha256'] and int(target.sum())==targets[uid]['label_foreground']
        bundle=dict(**fields,target=target,grid=grid,native_shape_rcz=case['native_shape']);cache[uid]=bundle
        locations,axes=old.tile_plan(target.shape)
        records.append(dict(patient=case['patient'],uid=uid,shape_zrc=list(target.shape),grid=grid,
            array_bytes={k:int(bundle[k].nbytes) for k in FIELDS},array_sha256={k:array_sha(bundle[k]) for k in FIELDS},
            total_tiles=len(locations),forward_calls=(len(locations)+1)//2,axis_starts=axes,load_seconds=time.perf_counter()-at,
            input_factory_metadata=metadata,observed_statistics=st,observed_package=row['observed_package'],
            observed_package_sha256=row['observed_package_sha256'],label_file=case['label_file'],label_file_sha256=case['label_sha256']))
        del observed,gt;guard();r['cache_records']=records;save()
    total=sum(sum(v['array_bytes'].values()) for v in records);assert total==5729136000
    stream,orders=stream_for(cases);assert len(stream)==33
    representative=sorted(records,key=lambda v:(-v['total_tiles'],v['uid']))[0]['uid']
    r.update(cache_records=records,actual_cache_array_bytes=total,cache_load_elapsed_seconds=time.perf_counter()-tick,
        training_patient_ids=sorted({c['patient'] for c,row in cases}),development_series_uids=sorted(cache),
        frozen_stream=stream,frozen_series_orders=orders,representative_FOV_uid=representative,
        representative_selection='maximum_fixed_tile_count_then_UID',all19_FOV_scored=False,
        max_volume_shape_zrc=max(records,key=lambda v:np.prod(v['shape_zrc']))['shape_zrc'])
    save();return cache,stream,representative
