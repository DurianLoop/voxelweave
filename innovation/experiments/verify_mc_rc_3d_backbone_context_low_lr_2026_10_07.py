"""Verify complete histories and replay both final networks with independent counts/coordinates."""
import itertools,json,math,sys,time,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,lattice,physical_mr,
    physical_label,read_reference_label,sample_batch,TaskUNet3D,PATCH,SEED,torch,np,F)
from mc_rc_3d_independent_replay_2026_10_07 import (
    functional_forward,independent_weight,independent_starts,independent_native_resample)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_backbone_context_low_lr_2026_10_07'
def counts(p,g):
    bins=np.bincount((p.astype(np.uint8)+2*g.astype(np.uint8)).reshape(-1),minlength=4)
    tn,fp,fn,tp=map(int,bins);n=tp+fn;s=tp+fp
    return dict(tn=tn,tp=tp,fp=fp,fn=fn,gt_foreground=n,pred_foreground=s,
        dice=2*tp/(n+s) if n+s else None,recall=tp/n if n else None,
        precision=tp/s if s else None,absRVE=abs(s-n)/n if n else None,
        empty_prediction=s==0,empty_ground_truth=n==0)
def replay(state,image,grid,native_shape):
    axes=independent_starts(image.shape,PATCH);positions=list(itertools.product(*axes));weight=independent_weight(PATCH)
    numerator=np.zeros(image.shape,np.float64);denominator=np.zeros_like(numerator)
    model=TaskUNet3D();model.load_state_dict(state,strict=True);model.eval();errors=[]
    with torch.inference_mode():
        for at in range(0,len(positions),2):
            slabs=[tuple(slice(s,s+p) for s,p in zip(start,PATCH)) for start in positions[at:at+2]]
            x=torch.from_numpy(np.stack([image[sl] for sl in slabs])[:,None])
            functional=functional_forward(x,state);module=model(x)
            for first,second in zip(functional,module):
                error=float((first.sigmoid()-second.sigmoid()).abs().max())
                assert error<=3e-6 and torch.equal(first>=0,second>=0);errors.append(error)
            probability=functional[0].sigmoid().numpy()[:,0]
            for sl,p in zip(slabs,probability):numerator[sl]+=p*weight;denominator[sl]+=weight
    assert denominator.min()>0
    physical=numerator/denominator
    crop=tuple(slice(p[0],p[0]+n) for n,p in zip(grid['unpadded_shape_zrc'],grid['padding']))
    physical=np.ascontiguousarray(physical[crop],dtype=np.float32)
    numpy_probability=independent_native_resample(physical,native_shape)
    shape=(native_shape[2],native_shape[0],native_shape[1])
    with torch.inference_mode():
        production=F.interpolate(torch.from_numpy(physical)[None,None],size=shape,mode='trilinear',align_corners=False)[0,0].numpy().transpose(1,2,0)
        double=F.interpolate(torch.from_numpy(physical.astype(np.float64))[None,None],size=shape,mode='trilinear',align_corners=False)[0,0].numpy().transpose(1,2,0).astype(np.float32)
    return production,numpy_probability,double,dict(tiles=len(positions),axis_starts=axes,coverage_min=float(denominator.min()),
        coverage_max=float(denominator.max()),all_three_head_tile_probability_max_error=max(errors))
def main():
    sys.stdout.reconfigure(encoding='utf-8');path=OUT/'independent_both1024_and_full_fov_attempt01.json';assert not path.exists()
    source=OUT/'attempt01.json';prod=read(source);started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],arms=[],script_sha256=sha(__file__),
        result_file=source.relative_to(ROOT).as_posix(),result_sha256=sha(source),actual_training_updates=0,actual_gpu_updates=0,
        validation_effects_opened=False,confirmation_patients_opened=False,scientific_confirmation_patients=0,
        second_independently_trained_task_network=False,publication_claim_confirmed=False)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        assert prod['complete'] and prod['status']=='completed' and not prod['errors'] and prod['actual_cpu_backbone_updates']==2048
        r['source_bindings']=prod['source_bindings']+[dict(path='MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_CONTROL_PROTOCOL_2026-10-07.md',
            sha256=sha(ROOT/'MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_CONTROL_PROTOCOL_2026-10-07.md'))]
        for binding in r['source_bindings']:assert sha(ROOT/binding['path'])==binding['sha256']
        torch.set_num_threads(4);resource_guard();role,case,row=fixed_cases()[0]
        assert role=='development' and case['patient']=='VS-MC-RC-001' and case['uid']==prod['series_uid']
        grid=lattice(case);gt=read_reference_label(case);target=physical_label(gt,grid)
        assert array_sha(target)==prod['physical_label_sha256']
        rng=np.random.default_rng(SEED);stream=[]
        for epoch in range(128):
            indices=rng.permutation(16).tolist();stream.extend(indices[a:a+2] for a in range(0,16,2))
        assert stream==prod['frozen_tile_pair_stream'] and array_sha(np.asarray(stream,dtype=np.int64))==prod['frozen_stream_sha256']
        for arm in prod['arms']:
            resource_guard();assert arm['complete'] and arm['evaluation_complete'] and arm['updates_completed']==1024
            history=arm['history'];assert len(history)==1024 and [h['update'] for h in history]==list(range(1,1025))
            assert [h['tile_indices'] for h in history]==stream
            assert all(h['lr']==.0001 and math.isfinite(h['loss']) for h in history)
            normalized,stats=source_image(case,row,arm['kind']);image=physical_mr(normalized,grid)
            assert array_sha(image)==arm['physical_input_sha256'] and stats==arm['observed_statistics']
            positions=list(itertools.product(*independent_starts(image.shape,PATCH)))
            assert [list(v) for v in positions]==arm['tile_locations']
            labelcounts=[int(target[tuple(slice(s,s+p) for s,p in zip(start,PATCH))].sum()) for start in positions]
            assert all(h['label_foreground']==[labelcounts[i] for i in pair] for h,pair in zip(history,stream))
            checkpoint=ROOT/arm['checkpoint_file'];initial_checkpoint=ROOT/arm['source_checkpoint_file']
            assert sha(checkpoint)==arm['checkpoint_sha256'] and sha(initial_checkpoint)==arm['source_checkpoint_sha256']
            record=torch.load(checkpoint,map_location='cpu',weights_only=True);state=record['state_dict']
            initial=torch.load(initial_checkpoint,map_location='cpu',weights_only=True)['state_dict']
            assert state_hash(state)==arm['final_weights_sha256']==record['final_weights_sha256']
            assert state_hash(initial)==arm['initial_weights_sha256']
            assert record['updates']==1024 and record['frozen_stream_sha256']==prod['frozen_stream_sha256']
            changed=[k for k in state if not torch.equal(state[k],initial[k])];assert changed==arm['changed_state_entries']
            assert any(k.startswith('encoders.') for k in changed) and any(k.startswith('decoders.') for k in changed)
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED))
            with torch.inference_mode():outputs=functional_forward(x,state)
            crop_metrics=[counts(p>=0,g>=.5) for p,g in zip(outputs[0].numpy()[:,0],y.numpy()[:,0])]
            assert crop_metrics==arm['original_augmented_patch_metrics']
            production,numpy_probability,double,coverage=replay(state,image,grid,case['native_shape'])
            predpath=ROOT/arm['prediction_file'];assert sha(predpath)==arm['prediction_sha256']
            with np.load(predpath,allow_pickle=False) as stored:
                saved=stored['probability_rcz'].copy();saved_prediction=stored['prediction_rcz'].copy()
            output_error=float(np.max(np.abs(production-saved)));output_diff=int(np.count_nonzero((production>=.5)!=saved_prediction))
            assert output_error<=3e-6 and output_diff==0,'Independent network+production-coordinate replay differs'
            assert np.array_equal(saved_prediction,saved>=.5)
            float32_error=float(np.max(np.abs(production-numpy_probability)))
            float32_diff=int(np.count_nonzero((production>=.5)!=(numpy_probability>=.5)))
            float64_error=float(np.max(np.abs(double-numpy_probability)))
            float64_diff=int(np.count_nonzero((double>=.5)!=(numpy_probability>=.5)))
            assert float64_error<=3e-6 and float64_diff==0,'Independent float64 coordinate implementations differ'
            zs=np.arange(gt.shape[2]);last=zs[zs%4==0][-1]
            domains=dict(full=np.ones(len(zs),bool),anchors=zs%4==0,missing=(zs<last)&(zs%4!=0),tail=zs>last)
            metrics={name:counts(saved_prediction[:,:,mask],gt[:,:,mask]) for name,mask in domains.items()}
            numpy_metrics={name:counts(numpy_probability[:,:,mask]>=.5,gt[:,:,mask]) for name,mask in domains.items()}
            assert metrics==arm['metrics']
            m=metrics['full'];crop=crop_metrics[0]
            gate=dict(foreground_patch_dice=crop['dice'] is not None and crop['dice']>=.9,
                training_full_dice=m['dice'] is not None and m['dice']>=.9,
                training_full_recall=m['recall'] is not None and m['recall']>=.9,
                training_full_absRVE=m['absRVE'] is not None and m['absRVE']<=.25,training_tp_positive=m['tp']>0)
            assert gate==arm['training_fit_gate'] and all(gate.values())==arm['training_fit_gate_passed']
            result=dict(kind=arm['kind'],complete=True,history_rows_verified=1024,full_tile_stream_and_labels_verified=True,
                changed_state_entries_verified=len(changed),full_native_voxels_replayed=int(saved_prediction.size),
                original_crop_gate_and_four_native_domains_verified=True,production_coordinate_replay_max_probability_error=output_error,
                production_coordinate_replay_threshold_disagreements=output_diff,coverage=coverage,
                production_float32_vs_numpy_coordinate=dict(max_probability_error=float32_error,
                    threshold_disagreements=float32_diff,original_strict_gate_passed=float32_error<=3e-6 and float32_diff==0),
                independent_float64_coordinate=dict(max_probability_error=float64_error,threshold_disagreements=float64_diff,gate_passed=True),
                production_metrics=metrics,numpy_coordinate_metrics=numpy_metrics,original_training_fit_gate=gate)
            r['arms'].append(result);save();print(json.dumps({k:result[k] for k in ('kind','complete','production_float32_vs_numpy_coordinate','independent_float64_coordinate')}),flush=True)
            del state,record,initial,normalized,image,x,y,outputs,production,numpy_probability,double,saved,saved_prediction
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        r['complete']=len(r['arms'])==2 and sha(source)==r['result_sha256'];r['resources_after']=resource_guard()
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started;r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','cuda_initialized','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
