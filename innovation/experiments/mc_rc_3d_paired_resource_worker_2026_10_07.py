"""Shared resource workflow: paired updates, in-memory resume, and target-free FOV."""
import copy,gc,hashlib,io,time
from dataclasses import asdict
import numpy as np
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,SEED,PATCH,torch,loss,array_sha,tile_plan,physical_label,read_reference_label
from mc_rc_3d_direct_observed_2026_10_07 import (read,sha,canonical_states,two_channel_model,
    development_observed_cases,load_development_observed,physical_fields)
from mc_rc_3d_paired_sampling_fov_2026_10_07 import draw_training_batch,apply_training_draws,infer_two_channel_full_fov

def statehash(state):
    h=hashlib.sha256()
    for k,v in state.items():h.update(k.encode());h.update(array_sha(v.detach().cpu().numpy()).encode())
    return h.hexdigest()
def cpu_tree(x):
    if isinstance(x,torch.Tensor):return x.detach().cpu().clone()
    if isinstance(x,dict):return {k:cpu_tree(v) for k,v in x.items()}
    if isinstance(x,list):return [cpu_tree(v) for v in x]
    if isinstance(x,tuple):return tuple(cpu_tree(v) for v in x)
    return copy.deepcopy(x)
def exact(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a==b
def snapshot(model,opt,step,device):
    r=dict(model=cpu_tree(model.state_dict()),optimizer=cpu_tree(opt.state_dict()),step=step,
        torch_rng=torch.get_rng_state().clone(),batch_seed_recipe=[SEED,813,'step'])
    if device!='cpu':r['cuda_rng']=torch.cuda.get_rng_state(0).cpu().clone()
    return r
def sync(device):
    if device!='cpu':torch.cuda.synchronize(0)
def update(model,opt,bundle,draws,kind,device,guard,r):
    before=guard();tick=time.perf_counter();key='dense' if kind=='dense' else 'numerator'
    x,y=apply_training_draws(bundle[key],bundle['availability'],bundle['valid_grid'],bundle['target'],draws,kind)
    xsha,ysha=array_sha(x.numpy()),array_sha(y.numpy());sample=time.perf_counter()-tick
    at=time.perf_counter();x=x.to(device);y=y.to(device);sync(device);transfer=time.perf_counter()-at
    at=time.perf_counter();model.train();opt.zero_grad(set_to_none=True)
    r['attempted_model_forward_calls']+=1;outputs=model(x);r['completed_model_forward_calls']+=1;value=loss(outputs,y)
    assert torch.isfinite(value);numeric_loss=float(value.detach());sync(device);forward=time.perf_counter()-at
    at=time.perf_counter();value.backward();sync(device);backward=time.perf_counter()-at
    at=time.perf_counter();groups={}
    for name,p in model.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()
        key=name.split('.')[0];groups[key]=max(groups.get(key,0.),float(p.grad.detach().abs().max()))
    mask=float(model.encoders[0].layers[0].weight.grad[:,1].abs().max());assert mask>0
    assert all(groups[k]>0 for k in ('encoders','decoders','ups','heads'))
    checking=time.perf_counter()-at;at=time.perf_counter();opt.step();r['actual_resource_updates']+=1;sync(device);optim=time.perf_counter()-at
    assert all(torch.isfinite(p).all() for p in model.parameters())
    total=time.perf_counter()-tick;after=guard()
    return dict(loss=numeric_loss,input_batch_sha256=xsha,label_batch_sha256=ysha,
        label_foreground=[int(v.sum()) for v in y],gradient_groups=groups,mask_gradient_max=mask,
        sample_and_hash_seconds=sample,host_to_device_seconds=transfer,forward_and_loss_seconds=forward,
        backward_seconds=backward,gradient_check_seconds=checking,optimizer_seconds=optim,total_update_seconds=total,
        resources_before=before,resources_after=after)

class GuardedInferenceModel:
    def __init__(self,model,device,guard,r):self.model=model;self.device=device;self.guard=guard;self.r=r
    def eval(self):self.model.eval();return self
    def __call__(self,x):
        self.guard();self.r['attempted_model_forward_calls']+=1;output=self.model(x)
        self.r['completed_model_forward_calls']+=1;sync(self.device);self.guard();return output

def run_workflow(cache,stream,device,guard,save,r,representative_uid):
    assert len(stream)>=2 and set(x['uid'] for x in stream)==set(cache)
    for b in cache.values():
        arrays=[b[k] for k in ('dense','numerator','availability','valid_grid','target')]
        assert all(x.dtype==np.float32 and x.shape==arrays[0].shape for x in arrays)
        assert all(n>=p for n,p in zip(arrays[0].shape,PATCH))
    begin=time.perf_counter();draws=[]
    for step,item in enumerate(stream):
        guard();d=draw_training_batch(cache[item['uid']]['target'],np.random.default_rng(np.random.SeedSequence([SEED,813,step])))
        draws.append(d)
    r['draw_materialization_seconds']=time.perf_counter()-begin
    r['shared_training_draws']=[dict(**item,draws=[asdict(d) for d in ds]) for item,ds in zip(stream,draws)]
    r['parameter_count_expected']=1401795;_,initial=canonical_states();initsha=statehash(initial)
    previous=read(ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json')
    assert initsha==previous['model_checks']['canonical_two_state_sha256']
    r['canonical_two_channel_state_sha256']=initsha;r['arms']=[];r['actual_resource_updates']=0
    r['attempted_model_forward_calls']=0;r['completed_model_forward_calls']=0;save()
    for kind in ('dense','direct'):
        guard();model=two_channel_model(initial).to(device);opt=torch.optim.AdamW(model.parameters(),lr=.0001,weight_decay=.0001)
        assert sum(p.numel() for p in model.parameters())==r['parameter_count_expected']
        assert statehash(model.state_dict())==initsha
        arm=dict(kind=kind,complete=False,history=[],initial_weights_sha256=initsha,planned_updates=len(stream),
            checkpoint_storage='memory_only',updated_weights_saved=False,FOV_passes=[])
        r['arms'].append(arm);checkpoint=None;continuous_after2=None;save()
        for step,(item,ds) in enumerate(zip(stream,draws)):
            h=update(model,opt,cache[item['uid']],ds,kind,device,guard,r)
            h.update({**item,'step':step+1,'warmup':step<2});arm['history'].append(h)
            if step==0:
                first=snapshot(model,opt,1,device);buffer=io.BytesIO();torch.save(first,buffer);checkpoint=buffer.getvalue()
                arm['checkpoint_bytes']=len(checkpoint);del first,buffer
            if step==1:
                continuous_after2=snapshot(model,opt,2,device);restored=torch.load(io.BytesIO(checkpoint),map_location='cpu',weights_only=True)
                resumed=two_channel_model(initial).to(device);resumed_opt=torch.optim.AdamW(resumed.parameters(),lr=.0001,weight_decay=.0001)
                resumed.load_state_dict(restored['model']);resumed_opt.load_state_dict(restored['optimizer']);torch.set_rng_state(restored['torch_rng'])
                if device!='cpu':torch.cuda.set_rng_state(restored['cuda_rng'],0)
                again=update(resumed,resumed_opt,cache[item['uid']],ds,kind,device,guard,r)
                for key in ('loss','input_batch_sha256','label_batch_sha256','label_foreground','gradient_groups','mask_gradient_max'):
                    assert h[key]==again[key],(kind,key)
                assert exact(continuous_after2,snapshot(resumed,resumed_opt,2,device))
                arm['resume_check']=dict(full_model_optimizer_RNG_tree_exact=True,replayed_step=2,
                    replay_input_batch_sha256=again['input_batch_sha256'],replay_label_batch_sha256=again['label_batch_sha256'],
                    replay_loss=again['loss'],extra_resource_updates=1,replay_total_update_seconds=again['total_update_seconds'])
                del resumed,resumed_opt,restored,continuous_after2;continuous_after2=None;gc.collect()
            save()
        b=cache[representative_uid];key='dense' if kind=='dense' else 'numerator'
        wrapped=GuardedInferenceModel(model,device,guard,r)
        for repeat in range(2):
            guard();at=time.perf_counter();native,physical,meta=infer_two_channel_full_fov(wrapped,b[key],b['availability'],b['grid'],b['native_shape_rcz'],device=device)
            elapsed=time.perf_counter()-at;guard();assert np.isfinite(native).all() and np.isfinite(physical).all()
            arm['FOV_passes'].append(dict(repeat=repeat+1,uid=representative_uid,elapsed_seconds=elapsed,metadata=meta,
                probability_arrays_saved=False,task_effects_scored=False))
            del native,physical;gc.collect();save()
        assert arm['FOV_passes'][0]['metadata']==arm['FOV_passes'][1]['metadata']
        arm.update(complete=True,original_stream_updates=len(stream),actual_resource_updates=len(stream)+1,
            FOV_repeat_exact=True,discarded_final_weights_sha256=statehash(model.state_dict()))
        assert arm['discarded_final_weights_sha256']!=initsha
        del model,opt,checkpoint,wrapped;gc.collect()
        if device!='cpu':torch.cuda.empty_cache()
        guard();save()
    a,b=r['arms']
    keys=('step','patient','uid','label_batch_sha256','label_foreground')
    assert [[h[k] for k in keys] for h in a['history']]==[[h[k] for k in keys] for h in b['history']]
    assert all(a['input_batch_sha256']!=b['input_batch_sha256'] for a,b in zip(a['history'],b['history']))
    r['gate']=dict(shared_draws_and_supervision=True,equal_initialization_capacity=True,
        all_branch_and_mask_gradients_finite_nonzero=True,both_memory_checkpoint_resumes_exact=True,
        complete_representative_FOV_and_repeat_exact=True,planned_resource_updates_completed=r['actual_resource_updates']==2*(len(stream)+1),
        no_updated_weights_saved=True,no_task_effects_scored=True)
    assert all(r['gate'].values());save()

def load_real_development(guard,save,r):
    from qualify_mc_rc_3d_19series_cpu_low_lr_2026_10_07 import stream_for
    cases=development_observed_cases();assert len(cases)==19 and len({c['patient'] for c,row in cases})==11
    old_fields={x['uid']:x for x in read(ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json')['series']}
    target_cert=read(ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json')
    old_targets={x['uid']:x for x in next(a for a in target_cert['arms'] if a['kind']=='raw_pchip')['cache_records']}
    cache={};records=[];at=time.perf_counter()
    for case,row in cases:
        guard();tick=time.perf_counter();uid=case['uid'];grid=old_fields[uid]['grid']
        observed=load_development_observed(case,row);r['MRI_observed_packages_loaded']+=1
        fields,st,native_hashes=physical_fields(observed,grid)
        for key,cert_key in [('dense','physical_dense_sha256'),('numerator','physical_numerator_sha256'),('availability','physical_availability_sha256')]:
            assert array_sha(fields[key])==old_fields[uid][cert_key]
        gt=read_reference_label(case);r['development_GT_loaded']+=1;target=physical_label(gt,grid)
        assert array_sha(target)==old_targets[uid]['label_sha256'] and int(target.sum())==old_targets[uid]['label_foreground']
        bundle=dict(**fields,target=target,grid=grid,native_shape_rcz=case['native_shape']);cache[uid]=bundle
        locations,axes=tile_plan(fields['dense'].shape)
        records.append(dict(patient=case['patient'],uid=uid,shape_zrc=list(target.shape),grid=grid,
            array_bytes={k:int(bundle[k].nbytes) for k in ('dense','numerator','availability','valid_grid','target')},
            array_sha256={k:array_sha(bundle[k]) for k in ('dense','numerator','availability','valid_grid','target')},
            total_tiles=len(locations),forward_calls=(len(locations)+1)//2,axis_starts=axes,load_seconds=time.perf_counter()-tick,
            observed_statistics=st,observed_package=row['observed_package'],observed_package_sha256=row['observed_package_sha256'],
            label_file=case['label_file'],label_file_sha256=case['label_sha256']))
        del observed,gt;guard();r['cache_records']=records;save()
    total=sum(sum(x['array_bytes'].values()) for x in records);assert total==4774280000
    stream,orders=stream_for(cases);assert len(stream)==33
    representative=sorted(records,key=lambda x:(-x['total_tiles'],x['uid']))[0]['uid']
    r.update(cache_records=records,actual_cache_array_bytes=total,cache_load_elapsed_seconds=time.perf_counter()-at,
        training_patient_ids=sorted({c['patient'] for c,row in cases}),development_series_uids=sorted(cache),
        frozen_stream=stream,frozen_series_orders=orders,representative_FOV_uid=representative,
        representative_selection='maximum_fixed_tile_count_then_UID',all19_FOV_scored=False,
        max_volume_shape_zrc=max(records,key=lambda x:np.prod(x['shape_zrc']))['shape_zrc'])
    save();return cache,stream,representative
