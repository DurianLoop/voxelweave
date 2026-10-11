"""Observed-only intervention: preserve exact original batches and compare all FOV voxels."""
import gc, itertools, json, sys, time, traceback
from datetime import datetime, timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT, read, sha, array_sha, resource_guard, fixed_cases, source_image, lattice,
    physical_mr, TaskUNet3D, torch, np, F, PATCH, tile_plan, blending_weight, infer_full_fov)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash

OUT = ROOT / 'experiments/mc_rc_3d_local_edit_cache_2026_10_07'
PREVIOUS = ROOT / 'experiments/mc_rc_3d_backbone_context_low_lr_2026_10_07'
PROTOCOL = ROOT / 'MC_RC_3D_LOCAL_EDIT_CACHE_QUALIFICATION_PROTOCOL_2026-10-07.md'

def stamp(): return datetime.now(timezone.utc).isoformat()
def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def entry(path): return dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path))

def aggregate(probabilities, image_shape, locations, grid, native_shape):
    started = time.perf_counter(); weight = blending_weight(PATCH)
    numerator = np.zeros(image_shape, np.float64); denominator = np.zeros_like(numerator)
    for start, prob in zip(locations, probabilities):
        sl = tuple(slice(s,s+p) for s,p in zip(start,PATCH))
        numerator[sl] += prob * weight; denominator[sl] += weight
    assert denominator.min() > 0
    physical = numerator / denominator
    crop = tuple(slice(lo,lo+n) for n,(lo,hi) in zip(grid['unpadded_shape_zrc'],grid['padding']))
    unpadded = np.ascontiguousarray(physical[crop], dtype=np.float32)
    with torch.inference_mode():
        mapped = F.interpolate(torch.from_numpy(unpadded)[None,None],
                               size=(native_shape[2],native_shape[0],native_shape[1]),
                               mode='trilinear',align_corners=False)[0,0].numpy()
    native = np.ascontiguousarray(mapped.transpose(1,2,0))
    return physical, native, dict(coverage_sha256=array_sha(denominator),
        blend_weight_sha256=array_sha(weight), coverage_min=float(denominator.min()),
        coverage_max=float(denominator.max()), aggregation_and_mapping_seconds=time.perf_counter()-started)

def forward_batches(model, image, locations, at_indices, guard):
    probabilities = {}; records = []; started = time.perf_counter()
    with torch.inference_mode():
        for at in at_indices:
            guard(); tick = time.perf_counter(); ids = list(range(at,min(at+2,len(locations))))
            slabs = [tuple(slice(s,s+p) for s,p in zip(locations[i],PATCH)) for i in ids]
            x = torch.from_numpy(np.stack([image[sl] for sl in slabs])[:,None])
            prob = model(x)[0].sigmoid().numpy()[:,0]
            assert prob.shape[1:] == PATCH and np.isfinite(prob).all()
            for i,p in zip(ids,prob): probabilities[i] = p.copy()
            records.append(dict(batch_start=at, tile_ids=ids, input_array_sha256=array_sha(x.numpy()),
                tile_probability_sha256=[array_sha(p) for p in prob], elapsed_seconds=time.perf_counter()-tick))
    return probabilities, records, time.perf_counter()-started

def domains(shape):
    z=np.arange(shape[2]); anchors=z%4==0; last=int(z[anchors][-1])
    return dict(full=np.ones(shape[2],bool), anchors=anchors, missing=(z<last)&~anchors, tail=z>last)

def difference(first, second):
    delta=np.abs(first-second)
    return dict(voxels=int(delta.size), probability_changed_voxels=int(np.count_nonzero(delta)),
        max_absolute_probability_change=float(delta.max()),
        threshold05_changed_voxels=int(np.count_nonzero((first>=.5)!=(second>=.5))))

def main():
    sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(exist_ok=False)
    path=OUT/'attempt01.json'; started=time.perf_counter()
    result=dict(created_utc=stamp(), complete=False, errors=[], script_sha256=sha(__file__),
        protocol=entry(PROTOCOL), source_bindings=[], MR_source='observed_only_raw_PCHIP',
        label_arrays_loaded=0, native_reference_MRI_arrays_loaded=0, task_metrics_scored=False,
        training_updates=0, GPU_updates=0, validation_patients_opened=False, confirmation_patients_opened=False,
        scientific_confirmation_patients=0, publication_claim_confirmed=False, other_processes_modified=False)
    save(path,result)
    def guard():
        assert time.perf_counter()-started <= 900, '900s qualification bound exceeded'
        r=resource_guard(); r['cpu_threads']=torch.get_num_threads()
        assert r['cpu_threads']==4 and torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
        assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()) <= 10_000_000
        return r
    try:
        torch.set_num_threads(4); result['resources_before']=guard()
        prod=read(PREVIOUS/'attempt01.json'); independent=read(PREVIOUS/'independent_both1024_and_full_fov_attempt01.json')
        assert prod['complete'] and not prod['errors'] and independent['complete'] and not independent['errors']
        arm=next(a for a in prod['arms'] if a['kind']=='raw_pchip')
        checkpoint=ROOT/arm['checkpoint_file']; assert sha(checkpoint)==arm['checkpoint_sha256']
        record=torch.load(checkpoint,map_location='cpu',weights_only=True)
        assert record['updates']==arm['updates_completed']==1024 and state_hash(record['state_dict'])==arm['final_weights_sha256']
        selected=[v for v in fixed_cases() if v[1]['patient']=='VS-MC-RC-001' and v[1]['uid']==prod['series_uid']]
        assert len(selected)==1
        role,case,row=selected[0]; assert role=='development' and case['uid'].endswith('369177')
        result.update(patient=case['patient'],uid=case['uid'],model_final_weights_sha256=arm['final_weights_sha256'],
                      checkpoint=entry(checkpoint),preselected_ROI_without_GT=True)
        result['source_bindings']=[entry(p) for p in (PROTOCOL,PREVIOUS/'attempt01.json',
            PREVIOUS/'independent_both1024_and_full_fov_attempt01.json',checkpoint,
            ROOT/row['observed_package'],ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',
            ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py')]
        observed_before_sha=sha(ROOT/row['observed_package'])
        grid=lattice(case); normalized,statistics=source_image(case,row,'raw_pchip')
        image=physical_mr(normalized,grid); assert array_sha(image)==arm['physical_input_sha256']
        shape=case['native_shape']; masks=domains(shape); missing=np.flatnonzero(masks['missing'])
        z=min(map(int,missing),key=lambda v:(abs(v-(shape[2]-1)/2),v))
        r0,c0=shape[0]//2-3,shape[1]//2-3
        edited_normalized=normalized.copy(); edited_normalized[r0:r0+7,c0:c0+7,z] += np.float32(.25)
        assert z%4 and np.array_equal(edited_normalized[:,:,masks['anchors']],normalized[:,:,masks['anchors']])
        raw_change=edited_normalized!=normalized
        assert int(np.count_nonzero(raw_change))==49
        edited=physical_mr(edited_normalized,grid); changed=image!=edited
        coords=np.argwhere(changed); assert len(coords)>0
        locations,axes=tile_plan(image.shape); assert len(locations)==16
        slices=[tuple(slice(s,s+p) for s,p in zip(start,PATCH)) for start in locations]
        affected=[i for i,sl in enumerate(slices) if np.any(changed[sl])]
        all_batches=list(range(0,len(locations),2)); affected_batches=sorted({(i//2)*2 for i in affected})
        recomputed=sorted(i for at in affected_batches for i in range(at,min(at+2,len(locations))))
        assert 0<len(affected_batches)<len(all_batches)
        result.update(native_shape_rcz=shape,physical_shape_zrc=list(image.shape),physical_grid=grid,
            edit=dict(z=z,rows=[r0,r0+7],columns=[c0,c0+7],normalized_delta=.25,native_changed_voxels=49,
                physical_changed_voxels=int(len(coords)),physical_change_min_zrc=coords.min(axis=0).tolist(),
                physical_change_max_zrc=coords.max(axis=0).tolist(),observed_input_anchors_equal=True,
                observed_statistics=statistics,observed_statistics_reestimated=False),
            tile_locations=[list(v) for v in locations],axis_starts=axes,
            affected_tile_ids=affected,recomputed_tile_ids=recomputed,recomputed_batch_starts=affected_batches,
            baseline_cache_probability_bytes=len(locations)*int(np.prod(PATCH))*4)
        save(path,result)
        model=TaskUNet3D();model.load_state_dict(record['state_dict'],strict=True);model.eval()
        base,base_batches,base_seconds=forward_batches(model,image,locations,all_batches,guard)
        base_physical,base_native,base_aggregation=aggregate([base[i] for i in range(16)],image.shape,locations,grid,shape)
        full,full_batches,full_seconds=forward_batches(model,edited,locations,all_batches,guard)
        full_physical,full_native,full_aggregation=aggregate([full[i] for i in range(16)],image.shape,locations,grid,shape)
        cache_started=time.perf_counter()
        incremental,incremental_batches,incremental_seconds=forward_batches(model,edited,locations,affected_batches,guard)
        cached={i:incremental[i] if i in incremental else base[i] for i in range(16)}
        cached_physical,cached_native,cache_aggregation=aggregate([cached[i] for i in range(16)],image.shape,locations,grid,shape)
        cache_wall=time.perf_counter()-cache_started
        tile_records=[]
        for i,sl in enumerate(slices):
            tile_records.append(dict(tile=i,affected_by_changed_input=i in affected,recomputed=i in incremental,
                unchanged_input=np.array_equal(image[sl],edited[sl]),
                base_probability_sha256=array_sha(base[i]),full_probability_sha256=array_sha(full[i]),
                cached_probability_sha256=array_sha(cached[i]),cached_full_equal=np.array_equal(cached[i],full[i]),
                base_full_equal=np.array_equal(base[i],full[i])))
        assert all(t['unchanged_input']==(t['tile'] not in affected) for t in tile_records)
        untouched=[t for t in tile_records if t['unchanged_input']]
        union=np.zeros(image.shape,bool)
        for i in affected:union[slices[i]]=True
        result.update(batch_records=dict(baseline=base_batches,full_edited=full_batches,incremental_edited=incremental_batches),
            tiles=tile_records,forward_accounting=dict(baseline=len(base_batches),full_edited=len(full_batches),
                incremental_edited=len(incremental_batches),saved_edited_forwards=len(full_batches)-len(incremental_batches),
                baseline_tiles=len(base),full_edited_tiles=len(full),incremental_edited_tiles=len(incremental)),
            one_run_timing_not_benchmark=dict(baseline_forward_seconds=base_seconds,full_edited_forward_seconds=full_seconds,
                incremental_edited_forward_seconds=incremental_seconds,incremental_forward_plus_aggregation_seconds=cache_wall,
                baseline_aggregation=base_aggregation,full_aggregation=full_aggregation,cache_aggregation=cache_aggregation,
                simultaneous_other_training_load=True,cache_initialization_cost_included_in_baseline=True),
            native_probability_sha256=dict(baseline=array_sha(base_native),full_edited=array_sha(full_native),cached_edited=array_sha(cached_native)),
            physical_probability_sha256=dict(baseline=array_sha(base_physical),full_edited=array_sha(full_physical),cached_edited=array_sha(cached_physical)),
            cached_vs_full=difference(cached_native,full_native),
            intervention_response_without_GT={name:difference(base_native[:,:,mask],full_native[:,:,mask]) for name,mask in masks.items()},
            physical_output_change_outside_affected_tile_union=int(np.count_nonzero((base_physical!=full_physical)&~union)))
        save(path,result)
        del base,full,cached,incremental,base_physical,cached_physical;gc.collect();guard()
        # Original production function: independent reference for aggregation and native map.
        verification_started=time.perf_counter(); production,coverage=infer_full_fov(model,edited,grid,shape)
        result['production_reference']=dict(extra_reference_forwards=len(all_batches),extra_reference_tiles=len(locations),
            elapsed_seconds=time.perf_counter()-verification_started,native_probability_sha256=array_sha(production),
            full_edited_probability_equal=np.array_equal(production,full_native),coverage=coverage)
        result['gates']=dict(all_tile_probabilities_bitwise_equal=all(t['cached_full_equal'] for t in tile_records),
            physical_probabilities_SHA_equal=result['physical_probability_sha256']['full_edited']==result['physical_probability_sha256']['cached_edited'],
            native_probabilities_SHA_equal=result['native_probability_sha256']['full_edited']==result['native_probability_sha256']['cached_edited'],
            native_threshold_differences_zero=result['cached_vs_full']['threshold05_changed_voxels']==0,
            all_unaffected_tile_probabilities_equal=all(t['base_full_equal'] for t in untouched),
            cached_path_fewer_forwards=len(incremental_batches)<len(full_batches),
            production_reference_bitwise_equal=np.array_equal(production,full_native),
            production_coverage_SHA_equal=coverage['coverage_sha256']==full_aggregation['coverage_sha256'],
            changes_contained_in_affected_tile_union=result['physical_output_change_outside_affected_tile_union']==0,
            observed_package_SHA_unchanged=sha(ROOT/row['observed_package'])==observed_before_sha,
            checkpoint_SHA_unchanged=sha(checkpoint)==arm['checkpoint_sha256'])
        result['qualification_passed']=all(result['gates'].values());result['resources_after']=guard()
        result['cuda_initialized']=torch.cuda.is_initialized();result['complete']=True
    except Exception as e:
        result['errors'].append(type(e).__name__+': '+str(e));result['traceback']=traceback.format_exc()
    result['elapsed_seconds']=time.perf_counter()-started;result['finished_utc']=stamp();save(path,result)
    print(json.dumps({k:result.get(k) for k in ('complete','errors','qualification_passed','affected_tile_ids',
        'recomputed_tile_ids','forward_accounting','cached_vs_full','intervention_response_without_GT','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not result['complete'] or not result.get('qualification_passed',False))

if __name__=='__main__':raise SystemExit(main())
