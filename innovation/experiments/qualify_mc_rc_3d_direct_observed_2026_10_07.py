"""Stream 19 developer observed packages; synthetic-only model/gradient/resume checks."""
import copy,gc,hashlib,io,json,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
from mc_rc_3d_direct_observed_2026_10_07 import *
from mc_rc_reference_resources_2026_10_07 import resource_guard
from mc_rc_3d_baseline_v2_2026_10_07 import loss
from mc_rc_3d_independent_replay_2026_10_07 import functional_forward

OUT=ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07'
PROTOCOL=ROOT/'MC_RC_3D_DIRECT_OBSERVED_REPRESENTATION_PROTOCOL_2026-10-07.md'

def state_hash(state):
    h=hashlib.sha256()
    for k,v in state.items():h.update(k.encode());h.update(array_sha(v.detach().numpy()).encode())
    return h.hexdigest()

def equal_tree(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(equal_tree(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return isinstance(b,type(a)) and len(a)==len(b) and all(equal_tree(x,y) for x,y in zip(a,b))
    return a==b

def optimizer(model):return torch.optim.AdamW(model.parameters(),lr=.0001,weight_decay=.0001)

def snapshot(model,opt,step):
    return dict(model=copy.deepcopy(model.state_dict()),optimizer=copy.deepcopy(opt.state_dict()),
                torch_rng=torch.get_rng_state().clone(),step=step,synthetic_batch_seeds=[SEED+700,SEED+701])

def synthetic_batch(step,kind):
    rng=np.random.default_rng(SEED+700+step)
    values=rng.normal(size=(2,16,32,32)).astype(np.float32)
    availability=(rng.random((2,16,32,32))<.25).astype(np.float32)
    if kind=='direct':values*=availability
    x=torch.from_numpy(np.stack((values,availability),axis=1))
    target=torch.from_numpy((rng.random((2,1,16,32,32))<.06).astype(np.float32))
    return x,target

def synthetic_step(model,opt,step,kind):
    x,y=synthetic_batch(step,kind);opt.zero_grad(set_to_none=True)
    outputs=model(x);value=loss(outputs,y);assert torch.isfinite(value)
    value.backward();groups={}
    for name,p in model.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()
        group=name.split('.')[0];groups[group]=max(groups.get(group,0.),float(p.grad.abs().max()))
    mask=float(model.encoders[0].layers[0].weight.grad[:,1].abs().max())
    assert all(groups[k]>0 for k in ('encoders','decoders','ups','heads')) and mask>0
    opt.step();assert all(torch.isfinite(p).all() for p in model.parameters())
    return dict(loss=float(value.detach()),group_gradient_max=groups,mask_channel_gradient_max=mask,
                input_sha256=array_sha(x.numpy()),target_sha256=array_sha(y.numpy()))

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);started=time.perf_counter()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
           series=[],synthetic_arms=[],actual_MRI_forwards=0,actual_MRI_training_updates=0,actual_GPU_forwards=0,
           native_or_GT_pixels_opened=False,validation_pixels_opened=False,confirmation_patients_opened=False,
           publication_claim_confirmed=False,task_effects_scored=False,synthetic_updates_completed=0)
    path=OUT/'attempt01.json';audit_reads=set();denied=[]
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        try:p=Path(args[0]).resolve()
        except (ValueError,OSError,TypeError):return
        mode=args[1] if len(args)>1 else None
        reading=not isinstance(mode,str) or 'r' in mode or '+' in mode
        if reading and p.is_relative_to(ROOT):
            rel=p.relative_to(ROOT).as_posix()
            if p.name.endswith(('.zip','.nii','.nii.gz')) or any(t in rel for t in ('mc_rc_validation_task','mc_rc_true_native_reference_attempt','confirmation')):
                denied.append(rel);raise PermissionError('Qualification prohibits MRI GT/native/validation file access: '+rel)
            audit_reads.add(rel)
    sys.addaudithook(audit)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-started<=600,'Qualification 600s limit exceeded'
        result=resource_guard();assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1
        assert not torch.cuda.is_initialized();saved=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
        assert saved<=25_000_000;result.update(cpu_threads=4,stage_saved_bytes=saved,stage_saved_limit=25_000_000)
        return result
    save()
    try:
        torch.set_num_threads(4);r['resources_before']=guard();cases=development_observed_cases()
        previous=read(ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json')
        previous=next(a for a in previous['arms'] if a['kind']=='raw_pchip')
        old={x['uid']:x for x in previous['cache_records']}
        sourcepaths=[PROTOCOL,Path(__file__),ROOT/'experiments/mc_rc_3d_direct_observed_2026_10_07.py',
                     ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
                     ROOT/'experiments/mc_rc_observed_only_training_input.py',ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py',
                     ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py',
                     ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json',
                     ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json',
                     ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json']
        sourcepaths.extend(ROOT/row['observed_package'] for c,row in cases)
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sourcepaths]
        for c,row in cases:
            guard();obs=load_development_observed(c,row);grid=lattice(c)
            raw,dense,numerator,mask,st=native_fields(obs)
            assert array_sha(raw)==row['inputs']['raw_pchip_observed_shared']['raw_reconstruction_sha256']
            assert array_sha(dense)==row['inputs']['raw_pchip_observed_shared']['normalized_rcz_sha256']
            idx=list(obs.indices);unobserved=np.ones(obs.native_planes,dtype=bool);unobserved[idx]=False
            assert np.array_equal(dense[:,:,idx],numerator[:,:,idx])
            assert np.count_nonzero(numerator[:,:,unobserved])==0 and np.count_nonzero(mask[:,:,unobserved])==0
            assert np.all(mask[:,:,idx]==1)
            dense_p=physical_mr(dense,grid);num_p=physical_mr(numerator,grid);mask_p=physical_mr(mask,grid)
            mask_again=physical_mr(mask,grid);assert np.array_equal(mask_p,mask_again)
            assert array_sha(dense_p)==old[c['uid']]['input_sha256']
            assert st==old[c['uid']]['observed_statistics']
            assert np.isfinite(dense_p).all() and np.isfinite(num_p).all() and np.isfinite(mask_p).all()
            assert float(mask_p.min())>=0 and float(mask_p.max())<=1
            n=obs.native_planes;m=grid['unpadded_shape_zrc'][0]
            z=np.clip((np.arange(m,dtype=float)+.5)*n/m-.5,0,n-1)
            z0=np.floor(z).astype(int);zf=z-z0;anchor=np.zeros(n);anchor[idx]=1
            expected=(1-zf)*anchor[z0]+zf*anchor[np.minimum(z0+1,n-1)]
            crop=tuple(slice(lo,lo+size) for size,(lo,hi) in zip(grid['unpadded_shape_zrc'],grid['padding']))
            core=mask_p[crop];err=float(np.max(np.abs(core-expected[:,None,None])))
            assert err<=1e-5
            rec=dict(patient=c['patient'],uid=c['uid'],observed_package=row['observed_package'],
                     observed_package_sha256=row['observed_package_sha256'],observed_array_sha256=array_sha(obs.pixels),
                     native_normalized_sha256=array_sha(dense),native_numerator_sha256=array_sha(numerator),
                     native_binary_availability_sha256=array_sha(mask),physical_dense_sha256=array_sha(dense_p),
                     physical_numerator_sha256=array_sha(num_p),physical_availability_sha256=array_sha(mask_p),
                     observed_indices=idx,native_shape_rcz=c['native_shape'],physical_shape_zrc=list(dense_p.shape),
                     each_physical_channel_bytes=dense_p.nbytes,grid=grid,statistics=st,
                     frozen_dense_hash_matched=True,observed_values_preserved=True,missing_values_zero=True,
                     same_availability_bitwise=True,independent_z_availability_max_abs_error=err,
                     availability_nonzero_voxels=int(np.count_nonzero(mask_p)),availability_sum=float(mask_p.sum(dtype=np.float64)))
            r['series'].append(rec);save();print(json.dumps(dict(kind='observed_representation',completed=len(r['series']),patient=c['patient'],uid=c['uid'],mask_error=err)))
            del obs,raw,dense,numerator,mask,dense_p,num_p,mask_p,mask_again,core;gc.collect();guard()
        # Independent synthetic commutation check for the specified interpolation kernel.
        rng=np.random.default_rng(SEED+702);pixels=rng.normal(size=(7,9,3)).astype(np.float32)
        obs=ObservedMRI(pixels,(0,4,8),10,tuple(map(tuple,np.eye(4))),(),())
        g=dict(unpadded_shape_zrc=[13,11,15],padding=[(1,2),(2,1),(1,1)])
        fields,st,hashes=physical_fields(obs,g);raw,dense,num,mask,st=native_fields(obs)
        s,t=1.07,-.08;checks=[]
        for kind,native in [('dense',dense),('direct',num)]:
            native_shift=s*native+t*(np.ones_like(mask) if kind=='dense' else mask)
            expected=physical_mr(native_shift,g)
            pair=augment_pair(fields['dense' if kind=='dense' else 'numerator'],fields['availability'],fields['valid_grid'],s,t,kind)
            err=float(np.max(np.abs(pair[0]-expected)));assert err<=1e-5
            assert np.array_equal(pair[1],fields['availability'])
            assert np.all(pair[0][fields['valid_grid']==0]==0)
            if kind=='direct':assert np.all(pair[0][fields['availability']==0]==0)
            flipped=augment_pair(fields['dense' if kind=='dense' else 'numerator'],fields['availability'],fields['valid_grid'],s,t,kind,(True,False,True))
            assert np.array_equal(flipped,np.flip(np.flip(pair,axis=1),axis=3))
            checks.append(dict(kind=kind,physical_vs_native_affine_transform_max_error=err,mask_unchanged=True,padding_zero=True,flip_equivalent=True))
        r['augmentation_checks']=checks
        one,two=canonical_states();m1=TaskUNet3D();m1.load_state_dict(one);m2=two_channel_model(two)
        p1=sum(p.numel() for p in m1.parameters());p2=sum(p.numel() for p in m2.parameters());assert p2-p1==432
        x,y=synthetic_batch(0,'dense')
        with torch.inference_mode():
            a=m1(x[:,:1]);b=m2(x);functional=functional_forward(x,two)
            errors=[float((u-v).abs().max()) for u,v in zip(a,b)]
            assert all(torch.allclose(u,v,atol=1e-5,rtol=1e-5) for u,v in zip(a,b))
            ferrors=[float((u-v).abs().max()) for u,v in zip(b,functional)]
            assert all(torch.allclose(u,v,atol=1e-5,rtol=1e-5) for u,v in zip(b,functional))
        r['model_checks']=dict(one_channel_parameters=p1,two_channel_parameters=p2,extra_parameters=p2-p1,
                               initial_mask_weights_zero=True,canonical_one_state_sha256=state_hash(one),
                               canonical_two_state_sha256=state_hash(two),one_vs_two_output_max_errors=errors,
                               functional_replay_output_max_errors=ferrors,atol=1e-5,rtol=1e-5)
        del m1,m2,a,b,functional,x,y;gc.collect()
        for kind in ('dense','direct'):
            guard();model=two_channel_model(two);opt=optimizer(model)
            before=state_hash(model.state_dict());first=synthetic_step(model,opt,0,kind);r['synthetic_updates_completed']+=1
            after1=snapshot(model,opt,1);buffer=io.BytesIO();torch.save(after1,buffer)
            if kind=='direct':
                checkpoint=OUT/'synthetic_direct_after1.pt';checkpoint.write_bytes(buffer.getvalue())
                checkpoint_evidence=dict(file=checkpoint.relative_to(ROOT).as_posix(),sha256=sha(checkpoint),bytes=checkpoint.stat().st_size)
            else:checkpoint_evidence=dict(storage='in_memory_roundtrip',bytes=len(buffer.getvalue()))
            second=synthetic_step(model,opt,1,kind);r['synthetic_updates_completed']+=1
            final=snapshot(model,opt,2);resumed=two_channel_model(two);ropt=optimizer(resumed)
            restored=torch.load(checkpoint if kind=='direct' else io.BytesIO(buffer.getvalue()),map_location='cpu',weights_only=False)
            assert equal_tree(after1,restored)
            resumed.load_state_dict(restored['model']);ropt.load_state_dict(restored['optimizer']);torch.set_rng_state(restored['torch_rng'])
            again=synthetic_step(resumed,ropt,1,kind);r['synthetic_updates_completed']+=1
            resumedfinal=snapshot(resumed,ropt,2);assert equal_tree(final,resumedfinal) and second==again
            r['synthetic_arms'].append(dict(kind=kind,initial_weights_sha256=before,first=first,second=second,
                                           checkpoint=checkpoint_evidence,checkpoint_tree_exact=True,resumed_final_tree_exact=True,
                                           final_model_sha256=state_hash(final['model']),synthetic_updates_executed=3))
            del model,opt,resumed,ropt,after1,final,resumedfinal,restored,buffer;gc.collect();guard()
        assert len({a['initial_weights_sha256'] for a in r['synthetic_arms']})==1
        r['io_audit']=dict(workspace_read_paths=sorted(audit_reads),prohibited_access_attempts=denied,
                          native_MR_zip_reads=0,GT_NIfTI_reads=0,validation_data_or_metadata_reads=0)
        assert not denied
        r['gate']=dict(all19_developer_observed_inputs=True,all19_frozen_dense_hashes_equal=True,
                       native_observed_and_missing_values_contract=True,independent_fractional_availability=True,
                       augmentation_mask_and_padding_contract=True,equal_capacity_and_initialization=True,
                       synthetic_gradients_all_branches_finite_nonzero=True,synthetic_full_checkpoint_resume_exact=True,
                       no_MRI_forward_or_label_read=True)
        r['resources_after']=guard();r['cuda_initialized']=torch.cuda.is_initialized();r['complete']=True
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();r['elapsed_seconds']=time.perf_counter()-started;save()
    print(json.dumps(dict(complete=r['complete'],errors=r['errors'],series=len(r['series']),synthetic_updates=r['synthetic_updates_completed'],elapsed_seconds=r['elapsed_seconds']),ensure_ascii=False))
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
