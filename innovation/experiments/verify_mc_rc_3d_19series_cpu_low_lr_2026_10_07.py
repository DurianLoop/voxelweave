"""No-update replay of the qualified patient stream and actual augmented batch hashes."""
import collections,json,math,sys,time,traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,lattice,physical_mr,
    physical_label,read_reference_label,SEED,PATCH,torch,np)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07'
def independent_batch(image,target,step):
    rng=np.random.default_rng(np.random.SeedSequence([SEED,step]));foreground=np.transpose(np.nonzero(target>0))
    xs,ys,primitives=[],[],[]
    for forced in (True,False):
        if forced:center=foreground[int(rng.integers(len(foreground)))]
        else:center=np.array([rng.integers(n) for n in image.shape])
        start=np.minimum(np.maximum(center-np.array(PATCH)//2,0),np.array(image.shape)-np.array(PATCH)).astype(int)
        slices=tuple(slice(int(s),int(s)+p) for s,p in zip(start,PATCH))
        x,y=image[slices].copy(),target[slices].copy();flips=[]
        for axis in range(3):
            flag=bool(rng.random()<.5);flips.append(flag)
            if flag:x=np.flip(x,axis);y=np.flip(y,axis)
        scale,shift=float(rng.uniform(.9,1.1)),float(rng.uniform(-.1,.1));x=x*scale+shift
        xs.append(np.ascontiguousarray(x));ys.append(np.ascontiguousarray(y))
        primitives.append(dict(forced_foreground=forced,center=center.tolist(),start=start.tolist(),flips=flips,
                               intensity_scale=scale,intensity_shift=shift,target_foreground=int(y.sum())))
    return np.stack(xs)[:,None],np.stack(ys)[:,None],primitives
def main():
    sys.stdout.reconfigure(encoding='utf-8');source=OUT/'attempt01.json';q=read(source)
    assert q['complete'] and not q['errors'] and q['status']=='completed' and all(q['gate'].values())
    path=OUT/'independent_stream_and_batch_attempt01.json';assert not path.exists();started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
           source_file=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),arms=[],actual_training_updates=0,
           actual_gpu_updates=0,neural_forwards=0,gradient_finiteness_not_independently_retrained=True,
           validation_MR_or_GT_loaded=False,confirmation_patients_opened=False,publication_claim_confirmed=False)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-started<=900,'Frozen replay wall-clock limit exceeded'
        return resource_guard()
    save()
    try:
        torch.set_num_threads(4);guard()
        for b in q['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        cases=sorted([(c,row) for role,c,row in fixed_cases() if role=='development'],key=lambda pair:(pair[0]['patient'],pair[0]['uid']))
        assert len(cases)==19
        patient_uids={p:sorted(c['uid'] for c,row in cases if c['patient']==p) for p in sorted({c['patient'] for c,row in cases})}
        seeds=np.random.SeedSequence(SEED).spawn(1+len(patient_uids));order=np.random.default_rng(seeds[0])
        permuted={p:[uids[int(i)] for i in np.random.default_rng(seed).permutation(len(uids))]
                  for (p,uids),seed in zip(patient_uids.items(),seeds[1:])}
        reconstructed=[];patients=list(patient_uids)
        for round_index in range(max(len(uids) for uids in patient_uids.values())):
            for i in order.permutation(len(patients)):
                p=patients[int(i)];reconstructed.append(dict(step=len(reconstructed)+1,round_index=round_index,patient=p,
                    uid=permuted[p][round_index%len(permuted[p])]))
        assert reconstructed==q['frozen_stream'] and permuted==q['frozen_series_orders']
        assert len(reconstructed)==q['planned_updates_per_arm']
        for arm in q['arms']:
            guard();history=arm['history'];by_step={h['step']:h for h in history};cache_by={c['uid']:c for c in arm['cache_records']}
            assert len(by_step)==len(history)==len(reconstructed)==arm['updates']
            assert [{k:h[k] for k in ('step','round_index','patient','uid')} for h in history]==reconstructed
            assert all(math.isfinite(h['loss']) and h['lr']==.001 for h in history)
            assert all(h['warmup']==(h['step']<=2) for h in history)
            timings=[h['total_update_seconds'] for h in history if not h['warmup']]
            assert float(np.median(timings))==arm['median_timed_seconds'] and max(timings)==arm['max_timed_seconds']
            assert all(h['total_update_seconds']>=sum(h[k] for k in ('sample_and_hash_seconds','forward_and_loss_seconds',
                'backward_seconds','gradient_check_seconds','optimizer_step_seconds')) for h in history)
            cp=ROOT/arm['initial_checkpoint_file'];assert sha(cp)==arm['initial_checkpoint_sha256']
            initial=torch.load(cp,map_location='cpu',weights_only=True)['state_dict']
            assert state_hash(initial)==arm['initial_weights_sha256'];del initial
            replayed=0;records=[]
            for c,row in cases:
                guard();grid=lattice(c);native_gt=read_reference_label(c);target=physical_label(native_gt,grid)
                normalized,stats=source_image(c,row,arm['kind']);image=physical_mr(normalized,grid);record=cache_by[c['uid']]
                assert array_sha(image)==record['input_sha256'] and array_sha(target)==record['label_sha256']
                assert stats==record['observed_statistics'] and int(target.sum())==record['label_foreground']
                assert image.nbytes==record['image_bytes'] and target.nbytes==record['label_bytes']
                for item in reconstructed:
                    if item['uid']!=c['uid']:continue
                    h=by_step[item['step']];x,y,primitive=independent_batch(image,target,item['step'])
                    assert array_sha(x)==h['input_sha256'] and array_sha(y)==h['label_sha256']
                    assert primitive==h['augmentation_primitive'] and [int(g.sum()) for g in y]==h['label_foreground']
                    records.append(dict(step=item['step'],uid=c['uid'],input_sha256=array_sha(x),label_sha256=array_sha(y)))
                    replayed+=1;del x,y
                del image,target,native_gt,normalized;guard()
            assert replayed==len(reconstructed)
            r['arms'].append(dict(kind=arm['kind'],complete=True,series_cached_arrays_verified=19,
                actual_batches_independently_replayed=replayed,patient_balanced_stream_verified=True,cache_and_batch_hashes_verified=True,
                timing_aggregations_verified=True,gradient_finiteness_source='primary qualifier actual checks; not independently retrained',
                batch_records=sorted(records,key=lambda x:x['step'])));save()
        assert q['actual_resource_test_cpu_updates']==2*len(reconstructed)
        assert not list(OUT.glob('*.pt')) and not list(OUT.glob('*.npz'))
        assert sha(source)==r['source_sha256'];r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        r['resources_after']=guard();r['complete']=len(r['arms'])==2
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','neural_forwards','elapsed_seconds')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
