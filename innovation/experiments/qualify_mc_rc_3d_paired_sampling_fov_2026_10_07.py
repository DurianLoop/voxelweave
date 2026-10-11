"""Full PATCH synthetic qualification for paired sampler and target-free FOV execution."""
import copy,gc,hashlib,io,itertools,json,sys,time,traceback
from dataclasses import asdict
from datetime import datetime,timezone
from pathlib import Path
from mc_rc_3d_paired_sampling_fov_2026_10_07 import *
from mc_rc_3d_direct_observed_2026_10_07 import ROOT,sha,read,canonical_states,two_channel_model
from mc_rc_3d_baseline_v2_2026_10_07 import SEED,sample_batch,loss
from mc_rc_reference_resources_2026_10_07 import resource_guard
from mc_rc_3d_independent_replay_2026_10_07 import functional_forward,independent_starts,independent_weight,independent_native_resample

OUT=ROOT/'experiments/mc_rc_3d_paired_sampling_fov_qualification_2026_10_07'
PROTOCOL=ROOT/'MC_RC_3D_PAIRED_SAMPLING_FOV_PROTOCOL_2026-10-07.md'
PREVIOUS=ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json'

def statehash(state):
    h=hashlib.sha256()
    for k,v in state.items():h.update(k.encode());h.update(array_sha(v.detach().numpy()).encode())
    return h.hexdigest()
def equal(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return isinstance(b,type(a)) and len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b

def synthetic_fields():
    grid=dict(unpadded_shape_zrc=[65,129,133],padding=[(1,2),(2,1),(1,2)])
    shape=tuple(grid['unpadded_shape_zrc']);rng=np.random.default_rng(SEED+710)
    dense=rng.normal(size=shape).astype(np.float32)
    avail=np.broadcast_to(np.resize(np.asarray([0.,.25,.75,1.],dtype=np.float32),shape[0])[:,None,None],shape).copy()
    target=np.zeros(shape,dtype=np.float32);target[9:14,40:45,30:37]=1;target[54:57,118:121,122:125]=1
    fields={k:np.pad(v,grid['padding'],mode='constant') for k,v in dict(dense=dense,direct=dense*avail,
             availability=avail,valid=np.ones(shape,dtype=np.float32),target=target).items()}
    assert fields['dense'].shape==(68,132,136)
    return fields,grid

def scalar_apply(fields,draws,kind):
    """Independent crop/affine/flip order, never calls the new augment/apply helper."""
    images=[];labels=[]
    for d in draws:
        z,r,c=d.start;pz,pr,pc=PATCH;sl=np.s_[z:z+pz,r:r+pr,c:c+pc]
        signal=fields[kind][sl].copy();mask=fields['availability'][sl].copy();label=fields['target'][sl].copy()
        shift_support=mask if kind=='direct' else fields['valid'][sl]
        signal=np.float32(d.intensity_scale)*signal+np.float32(d.intensity_shift)*shift_support
        signal[fields['valid'][sl]==0]=0
        for axis,flag in enumerate(d.flips):
            if flag:
                signal=np.take(signal,np.arange(signal.shape[axis]-1,-1,-1),axis=axis)
                mask=np.take(mask,np.arange(mask.shape[axis]-1,-1,-1),axis=axis)
                label=np.take(label,np.arange(label.shape[axis]-1,-1,-1),axis=axis)
        images.append(np.stack((signal,mask)));labels.append(label[None])
    return np.stack(images),np.stack(labels)

def synthetic_update(model,opt,step,kind,fields):
    draws=draw_training_batch(fields['target'],np.random.default_rng(np.random.SeedSequence([SEED,711,step])))
    x,y=apply_training_draws(fields[kind],fields['availability'],fields['valid'],fields['target'],draws,kind)
    opt.zero_grad(set_to_none=True);outputs=model(x);v=loss(outputs,y);assert torch.isfinite(v)
    v.backward();groups={}
    for name,p in model.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()
        group=name.split('.')[0];groups[group]=max(groups.get(group,0.),float(p.grad.abs().max()))
    mask=float(model.encoders[0].layers[0].weight.grad[:,1].abs().max())
    assert all(groups[k]>0 for k in ('encoders','decoders','ups','heads')) and mask>0
    opt.step();assert all(torch.isfinite(p).all() for p in model.parameters())
    return dict(step=step,loss=float(v.detach()),draws=[asdict(d) for d in draws],input_sha256=array_sha(x.numpy()),
                label_sha256=array_sha(y.numpy()),gradient_groups=groups,mask_gradient_max=mask)

def snapshot(model,opt,step):
    return dict(model=copy.deepcopy(model.state_dict()),optimizer=copy.deepcopy(opt.state_dict()),
                torch_rng=torch.get_rng_state().clone(),step=step,batch_seed_recipe=[SEED,711,'step'])

def independent_fov(state,fields,kind,grid,native_shape,guard):
    image=fields[kind];mask=fields['availability'];axes=independent_starts(image.shape,PATCH)
    locations=list(itertools.product(*axes));weight=independent_weight(PATCH)
    numerator=np.zeros(image.shape,dtype=np.float64);coverage=np.zeros_like(numerator);tiles=[]
    with torch.inference_mode():
        for offset in range(0,len(locations),2):
            guard();starts=locations[offset:offset+2];items=[];cuts=[]
            for at in starts:
                sl=tuple(slice(a,a+p) for a,p in zip(at,PATCH));cuts.append(sl)
                items.append(np.concatenate((image[sl][None],mask[sl][None]),axis=0))
            x=torch.from_numpy(np.asarray(items,dtype=np.float32));p=functional_forward(x,state)[0].sigmoid().numpy()[:,0]
            assert np.isfinite(p).all()
            for at,sl,prob in zip(starts,cuts,p):
                numerator[sl]+=prob*weight;coverage[sl]+=weight
                tiles.append(dict(start=list(at),probability_sha256=array_sha(prob)))
    assert np.min(coverage)>0
    z,r,c=[v[0] for v in grid['padding']];nz,nr,nc=grid['unpadded_shape_zrc']
    physical=np.asarray((numerator/coverage)[z:z+nz,r:r+nr,c:c+nc],dtype=np.float32)
    return independent_native_resample(physical,native_shape),physical,dict(axes=axes,total_tiles=len(locations),
        forward_calls=(len(locations)+1)//2,coverage_sha256=array_sha(coverage),tiles=tiles)

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);start=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
           sampler_checks=[],training_checks=[],FOV_checks=[],synthetic_updates_completed=0,
           MRI_arrays_opened=False,MRI_forwards=0,MRI_training_updates=0,GPU_forwards=0,
           validation_or_confirmation_opened=False,publication_claim_confirmed=False)
    path=OUT/'attempt01.json';reads=set();denied=[]
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        try:p=Path(args[0]).resolve()
        except (ValueError,OSError,TypeError):return
        mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT):
            rel=p.relative_to(ROOT).as_posix()
            if rel.startswith('data/') or p.name.endswith(('.zip','.nii','.nii.gz')) or 'mc_rc_validation' in rel or 'confirmation' in rel:
                denied.append(rel);raise PermissionError('Synthetic stage prohibits MRI data reads: '+rel)
            reads.add(rel)
    sys.addaudithook(audit)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-start<=600
        v=resource_guard();assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
        size=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file());assert size<=25_000_000
        v.update(cpu_threads=4,stage_saved_bytes=size,stage_saved_limit=25_000_000);return v
    save()
    try:
        torch.set_num_threads(4);r['resources_before']=guard();previous=read(PREVIOUS)
        assert previous['complete'] and not previous['errors'] and all(previous['gate'].values())
        cp_record=next(a for a in previous['synthetic_arms'] if a['kind']=='direct')['checkpoint'];cp_path=ROOT/cp_record['file']
        assert sha(cp_path)==cp_record['sha256']
        sources=[PROTOCOL,Path(__file__),ROOT/'experiments/mc_rc_3d_paired_sampling_fov_2026_10_07.py',PREVIOUS,cp_path,
            ROOT/'experiments/mc_rc_3d_direct_observed_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',
            ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py',
            ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py']
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sources]
        fields,grid=synthetic_fields();original_hashes={k:array_sha(v) for k,v in fields.items()}
        r['synthetic_input']=dict(shape_zrc=list(fields['dense'].shape),grid=grid,native_shape_rcz=[33,35,17],
                                  patch=list(PATCH),batch_size=2,array_sha256=original_hashes,physical_slice_profile_simulated=False)
        flips=set();shifts=[]
        for step in range(24):
            guard();seed=np.random.SeedSequence([SEED,712,step])
            draws=draw_training_batch(fields['target'],np.random.default_rng(seed))
            oldx,oldy,old=sample_batch(np.zeros_like(fields['target']),fields['target'],np.random.default_rng(seed))
            serialized=[asdict(d) for d in draws]
            for d,v in zip(serialized,old):
                d={k:list(x) if isinstance(x,tuple) else x for k,x in d.items()};assert d==v
            batches=[]
            for kind in ('dense','direct'):
                x,y=apply_training_draws(fields[kind],fields['availability'],fields['valid'],fields['target'],draws,kind)
                independent_x,independent_y=scalar_apply(fields,draws,kind)
                assert np.array_equal(x.numpy(),independent_x) and np.array_equal(y.numpy(),independent_y)
                assert torch.equal(y,oldy)
                if kind=='direct':assert torch.all(x[:,0][x[:,1]==0]==0)
                batches.append((x,y))
            assert torch.equal(batches[0][1],batches[1][1]) and torch.equal(batches[0][0][:,1],batches[1][0][:,1])
            for d in draws:flips.add(d.flips);shifts.append(d.intensity_shift)
            r['sampler_checks'].append(dict(step=step,draws=serialized,same_legacy_draws=True,same_labels_and_masks=True,
                independent_batch_exact=True,dense_batch_sha256=array_sha(batches[0][0].numpy()),
                direct_batch_sha256=array_sha(batches[1][0].numpy()),label_sha256=array_sha(batches[0][1].numpy())))
            del oldx,oldy,batches,x,y,independent_x,independent_y
        assert all({v[axis] for v in flips}=={False,True} for axis in range(3)) and any(abs(s)>1e-6 for s in shifts)
        assert all(array_sha(fields[k])==h for k,h in original_hashes.items());r['input_arrays_not_mutated']=True
        _,initial=canonical_states();assert statehash(initial)==previous['model_checks']['canonical_two_state_sha256']
        for kind in ('dense','direct'):
            guard();model=two_channel_model(initial);opt=torch.optim.AdamW(model.parameters(),lr=.0001,weight_decay=.0001)
            first=synthetic_update(model,opt,0,kind,fields);r['synthetic_updates_completed']+=1
            saved=snapshot(model,opt,1);buffer=io.BytesIO();torch.save(saved,buffer)
            second=synthetic_update(model,opt,1,kind,fields);r['synthetic_updates_completed']+=1;final=snapshot(model,opt,2)
            resumed=two_channel_model(initial);resumed_opt=torch.optim.AdamW(resumed.parameters(),lr=.0001,weight_decay=.0001)
            restored=torch.load(io.BytesIO(buffer.getvalue()),map_location='cpu',weights_only=False);assert equal(saved,restored)
            resumed.load_state_dict(restored['model']);resumed_opt.load_state_dict(restored['optimizer']);torch.set_rng_state(restored['torch_rng'])
            again=synthetic_update(resumed,resumed_opt,1,kind,fields);r['synthetic_updates_completed']+=1
            assert second==again and equal(final,snapshot(resumed,resumed_opt,2))
            r['training_checks'].append(dict(kind=kind,first=first,second=second,actual_synthetic_updates=3,
                checkpoint_bytes=len(buffer.getvalue()),checkpoint_storage='memory_only',full_resume_tree_exact=True,
                final_weights_sha256=statehash(final['model']),updated_weights_saved=False))
            del model,opt,resumed,resumed_opt,saved,final,restored,buffer;gc.collect();save()
        assert r['training_checks'][0]['first']['draws']==r['training_checks'][1]['first']['draws']
        assert r['training_checks'][0]['second']['draws']==r['training_checks'][1]['second']['draws']
        cp=torch.load(cp_path,map_location='cpu',weights_only=False);state=cp['model'];model=two_channel_model(state)
        assert torch.count_nonzero(state['encoders.0.layers.0.weight'][:,1])>0
        native_shape=[33,35,17]
        for kind in ('dense','direct'):
            guard();native,physical,meta=infer_two_channel_full_fov(model,fields[kind],fields['availability'],grid,native_shape)
            native_i,physical_i,independent_meta=independent_fov(state,fields,kind,grid,native_shape,guard)
            assert meta['total_tiles']==independent_meta['total_tiles']==8 and meta['tiles']==independent_meta['tiles']
            assert meta['coverage_sha256']==independent_meta['coverage_sha256']
            pe=float(np.max(np.abs(physical-physical_i)));ne=float(np.max(np.abs(native-native_i)))
            assert np.allclose(physical,physical_i,atol=3e-6,rtol=1e-5) and np.allclose(native,native_i,atol=3e-6,rtol=1e-5)
            disagreements=int(np.count_nonzero((native>=.5)!=(native_i>=.5)));assert disagreements==0
            np.save(OUT/(kind+'_synthetic_native_probability.npy'),native,allow_pickle=False)
            r['FOV_checks'].append(dict(kind=kind,production=meta,independent=independent_meta,
                physical_max_abs_error=pe,native_max_abs_error=ne,threshold_disagreements=disagreements,
                probability_tolerance=dict(atol=3e-6,rtol=1e-5),complete_FOV_covered=True,
                synthetic_probability_file=(OUT/(kind+'_synthetic_native_probability.npy')).relative_to(ROOT).as_posix()))
            del native,physical,native_i,physical_i;gc.collect();save()
        cuts=tuple(slice(0,p) for p in PATCH);probe=torch.from_numpy(np.stack((fields['direct'][cuts],fields['availability'][cuts]))[None])
        absent=probe.clone();absent[:,1]=0
        with torch.inference_mode():
            present=model(probe)[0].sigmoid();missing=model(absent)[0].sigmoid()
        effect=float((present-missing).abs().max());assert effect>0
        r['mask_channel_usage_probe']=dict(source_checkpoint_sha256=sha(cp_path),mask_weights_nonzero=True,
                                          probability_max_difference_with_mask_zeroed=effect,synthetic_only=True)
        assert not denied
        r['io_audit']=dict(workspace_read_paths=sorted(reads),prohibited_access_attempts=denied,MRI_data_reads=0)
        r['resources_after']=guard();r['complete']=True
        r['synthetic_forward_counts']=dict(training_forward_calls=6,training_patches=12,
            complete_FOV_forward_calls=16,complete_FOV_tiles=32,mask_probe_forward_calls=2,mask_probe_patches=2)
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-start;save()
    print(json.dumps(dict(complete=r['complete'],errors=r['errors'],sampler_batches=len(r['sampler_checks']),
        synthetic_updates=r['synthetic_updates_completed'],FOV_arms=len(r['FOV_checks']),elapsed_seconds=r['elapsed_seconds']),ensure_ascii=False))
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
