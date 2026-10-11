"""All subset response diagnostic on one old certified observed-only model, never clinical benefit."""
import gc,itertools,json,sys,time,traceback
from datetime import datetime,timezone
from qualify_mc_rc_3d_local_edit_cache_2026_10_07 import (
    ROOT,PREVIOUS,read,sha,array_sha,resource_guard,fixed_cases,source_image,lattice,
    physical_mr,TaskUNet3D,torch,np,PATCH,tile_plan,infer_full_fov,
    aggregate,forward_batches,domains,difference,state_hash)
OUT=ROOT/'experiments/mc_rc_3d_action_composition_2026_10_07'
PROTOCOL=ROOT/'MC_RC_3D_ACTION_COMPOSITION_PROBE_PROTOCOL_2026-10-07.md'
def stamp():return datetime.now(timezone.utc).isoformat()
def entry(p):return dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p))
def summary(a):
    a=np.asarray(a,dtype=np.float64);ab=np.abs(a)
    return dict(voxels=int(a.size),nonzero_voxels=int(np.count_nonzero(a)),
                max_absolute=float(ab.max()),RMS=float(np.sqrt(np.mean(a*a))),
                mean_absolute=float(ab.mean()),signed_mean=float(a.mean()))
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt01.json';tick=time.perf_counter()
    result=dict(created_utc=stamp(),complete=False,errors=[],script_sha256=sha(__file__),protocol=entry(PROTOCOL),
        label_arrays_loaded=0,native_MRI_arrays_loaded=0,task_benefit_scored=False,training_updates=0,
        current19series_intermediate_model_read=False,GPU_updates=0,validation_pixels_loaded=0,
        confirmation_pixels_loaded=0,clinical_submodularity_tested=False,other_processes_modified=False,
        actual_model_forwards=0,actual_tiles=0,subsets=[])
    def save():path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    def guard():
        assert time.perf_counter()-tick<=900
        resources=resource_guard();assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
        assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<=10_000_000
        return resources
    def forward(model,image,locations,batches):
        # Account submitted calls even if a later numerical/resource check fails.
        def checking_guard():
            guard();result['actual_model_forwards']+=1;save()
        out,records,seconds=forward_batches(model,image,locations,batches,checking_guard)
        result['actual_tiles']+=sum(len(v['tile_ids']) for v in records)
        return out,records,seconds
    try:
        torch.set_num_threads(4);result['resources_before']=guard()
        old=read(PREVIOUS/'attempt01.json');proof=read(PREVIOUS/'independent_both1024_and_full_fov_attempt01.json')
        assert old['complete'] and proof['complete'] and not old['errors'] and not proof['errors']
        arm=next(a for a in old['arms'] if a['kind']=='raw_pchip');cp=ROOT/arm['checkpoint_file']
        assert sha(cp)==arm['checkpoint_sha256'];record=torch.load(cp,map_location='cpu',weights_only=True)
        assert record['updates']==1024 and state_hash(record['state_dict'])==arm['final_weights_sha256']
        selected=[x for x in fixed_cases() if x[1]['patient']=='VS-MC-RC-001' and x[1]['uid']==old['series_uid']]
        assert len(selected)==1;role,case,row=selected[0];assert role=='development' and case['uid'].endswith('369177')
        grid=lattice(case);normalized,statistics=source_image(case,row,'raw_pchip');base_image=physical_mr(normalized,grid)
        assert array_sha(base_image)==arm['physical_input_sha256'];shape=case['native_shape'];assert shape==[256,256,30]
        locations,axes=tile_plan(base_image.shape);assert len(locations)==16
        slices=[tuple(slice(s,s+p) for s,p in zip(start,PATCH)) for start in locations];batches=list(range(0,len(locations),2));masks=domains(shape)
        actions=[dict(name='A',rows=[125,132],columns=[125,132]),dict(name='B',rows=[141,148],columns=[125,132]),dict(name='C',rows=[16,23],columns=[16,23])]
        for a in actions:a.update(z=14,normalized_delta=.25,native_voxels=49)
        model=TaskUNet3D();model.load_state_dict(record['state_dict'],strict=True);model.eval()
        bindings=[PROTOCOL,cp,PREVIOUS/'attempt01.json',PREVIOUS/'independent_both1024_and_full_fov_attempt01.json',
                  ROOT/row['observed_package'],ROOT/'experiments/qualify_mc_rc_3d_local_edit_cache_2026_10_07.py',
                  ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py']
        result.update(source_bindings=[entry(p) for p in bindings],patient=case['patient'],uid=case['uid'],
            checkpoint=entry(cp),model_state_sha256=state_hash(model.state_dict()),actions=actions,observed_statistics=statistics,
            observed_statistics_reestimated=False,native_shape_rcz=shape,physical_shape_zrc=list(base_image.shape),
            tile_locations=[list(x) for x in locations],axis_starts=axes,baseline_initialization_forwards=8)
        base,baserecords,baseseconds=forward(model,base_image,locations,batches)
        phys0,p0,agg0=aggregate([base[i] for i in range(16)],base_image.shape,locations,grid,shape)
        probabilities={0:p0};supports={};gates=[];base_full_sha=array_sha(p0)
        result['subsets'].append(dict(mask=0,actions=[],native_probability_sha256=base_full_sha,physical_probability_sha256=array_sha(phys0),
            full_forward_count=8,cached_incremental_forward_count=0,batch_records_full=baserecords,full_forward_seconds=baseseconds,
            response_by_domain={k:summary(np.zeros(int(shape[0]*shape[1]*np.count_nonzero(m)),np.float64)) for k,m in masks.items()}))
        del phys0;save()
        repeated,reprecords,repseconds=forward(model,base_image,locations,batches)
        repphys,repprob,repagg=aggregate([repeated[i] for i in range(16)],base_image.shape,locations,grid,shape)
        repeat_equal=np.array_equal(repprob,p0) and all(np.array_equal(base[i],repeated[i]) for i in range(16))
        result['baseline_repeat']=dict(native_bitwise_equal=repeat_equal,native_sha256=array_sha(repprob),
            difference=difference(p0,repprob),forwards=8,seconds=repseconds,records=reprecords)
        assert repeat_equal,'baseline non-deterministic; refuse response-interaction interpretation'
        del repeated,repphys,repprob;gc.collect()
        for mask in range(1,8):
            guard();names=[a['name'] for j,a in enumerate(actions) if mask&(1<<j)]
            modified=normalized.copy()
            for j,a in enumerate(actions):
                if mask&(1<<j):modified[slice(*a['rows']),slice(*a['columns']),14]+=np.float32(.25)
            assert np.array_equal(modified[:,:,masks['anchors']],normalized[:,:,masks['anchors']])
            assert int(np.count_nonzero(modified!=normalized))==49*len(names)
            image=physical_mr(modified,grid);changed=image!=base_image
            affected=[i for i,sl in enumerate(slices) if changed[sl].any()];needed=sorted({i//2*2 for i in affected});supports[mask]=set(needed)
            full,records,seconds=forward(model,image,locations,batches)
            fullphys,fullnative,fullagg=aggregate([full[i] for i in range(16)],image.shape,locations,grid,shape)
            cachednew,cache_records,cache_seconds=forward(model,image,locations,needed)
            cached={i:cachednew.get(i,base[i]) for i in range(16)}
            cachephys,cachenative,cacheagg=aggregate([cached[i] for i in range(16)],image.shape,locations,grid,shape)
            tile_equal=all(np.array_equal(cached[i],full[i]) for i in range(16))
            equal=tile_equal and np.array_equal(cachephys,fullphys) and np.array_equal(cachenative,fullnative)
            unchanged_equal=all(np.array_equal(base[i],full[i]) for i in range(16) if i not in affected)
            gates.append(equal and unchanged_equal)
            response=fullnative.astype(np.float64)-p0
            subset=dict(mask=mask,actions=names,native_input_sha256=array_sha(modified),physical_input_sha256=array_sha(image),
                physical_changed_voxels=int(np.count_nonzero(changed)),affected_tile_ids=affected,recomputed_batch_starts=needed,
                full_forward_count=8,cached_incremental_forward_count=len(needed),area_proxy_voxels=49*len(names),
                native_probability_sha256=array_sha(fullnative),cached_native_probability_sha256=array_sha(cachenative),
                physical_probability_sha256=array_sha(fullphys),cached_physical_probability_sha256=array_sha(cachephys),
                all_tiles_equal=tile_equal,all_unaffected_tiles_equal=unchanged_equal,all_FOV_paths_bitwise_equal=equal,
                cached_difference=difference(fullnative,cachenative),threshold_prediction_difference_from_baseline=difference(p0,fullnative),
                response_by_domain={k:summary(response[:,:,m]) for k,m in masks.items()},
                batch_records_full=records,batch_records_cached=cache_records,full_forward_seconds=seconds,cached_forward_seconds=cache_seconds)
            probabilities[mask]=fullnative.copy();result['subsets'].append(subset);save()
            del full,cachednew,cached,fullphys,fullnative,cachephys,cachenative,modified,image,changed,response;gc.collect()
        pairs=[]
        for a,b in itertools.combinations((1,2,4),2):
            delta=probabilities[a|b].astype(np.float64)-probabilities[a]-probabilities[b]+probabilities[0]
            pairs.append(dict(masks=[a,b],union_mask=a|b,full_response_nonadditive=bool(np.any(delta)),
                mixed_response_by_domain={k:summary(delta[:,:,m]) for k,m in masks.items()},
                incremental_batch_union=sorted(supports[a]|supports[b]),
                actual_joint_batches=sorted(supports[a|b]),union_model_exact=supports[a|b]==supports[a]|supports[b],
                standalone_forward_sum=len(supports[a])+len(supports[b]),joint_forward_count=len(supports[a|b]),
                marginal_second_after_first=len(supports[a|b])-len(supports[a])))
        triples=probabilities[7].astype(np.float64)-probabilities[3]-probabilities[5]-probabilities[6]+probabilities[1]+probabilities[2]+probabilities[4]-probabilities[0]
        result.update(pair_interactions=pairs,third_order_mixed_response_by_domain={k:summary(triples[:,:,m]) for k,m in masks.items()},
            final_joint_actual_batches=sorted(supports[7]),final_joint_union_batches=sorted(supports[1]|supports[2]|supports[4]),
            response_nonadditivity_is_not_task_benefit=True)
        del triples;gc.collect();guard()
        unioninput=normalized.copy()
        for a in actions:unioninput[slice(*a['rows']),slice(*a['columns']),14]+=np.float32(.25)
        unionphysical=physical_mr(unioninput,grid)
        # Original production aggregation reference; fixed 8 forwards submitted inside this call.
        result['actual_model_forwards']+=8;result['actual_tiles']+=16;save()
        production,coverage=infer_full_fov(model,unionphysical,grid,shape)
        prod_equal=np.array_equal(production,probabilities[7])
        result['production_joint_reference']=dict(forwards=8,native_probability_sha256=array_sha(production),bitwise_equal=prod_equal,coverage=coverage)
        result['gates']=dict(all7_cached_subsets_bitwise_equal=all(gates),baseline_repeat_bitwise_equal=repeat_equal,
            production_ABC_bitwise_equal=prod_equal,checkpoint_SHA_unchanged=sha(cp)==arm['checkpoint_sha256'],
            model_state_unchanged=state_hash(model.state_dict())==arm['final_weights_sha256'],
            observed_source_unchanged=sha(ROOT/row['observed_package'])==row['observed_package_sha256'],
            all_inputs_source_bounded=all(sha(ROOT/b['file'])==b['sha256'] for b in result['source_bindings']),
            no_cuda=not torch.cuda.is_initialized(),no_GT_or_task_metrics=True)
        result['qualification_passed']=all(result['gates'].values());result['resources_after']=guard();result['complete']=True
    except Exception as e:result['errors'].append(f'{type(e).__name__}: {e}');result['traceback']=traceback.format_exc()
    result['elapsed_seconds']=time.perf_counter()-tick;result['finished_utc']=stamp();save()
    print(json.dumps({k:result.get(k) for k in ('complete','errors','qualification_passed','actual_model_forwards','actual_tiles','pair_interactions','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not result['complete'] or not result.get('qualification_passed',False))
if __name__=='__main__':raise SystemExit(main())
