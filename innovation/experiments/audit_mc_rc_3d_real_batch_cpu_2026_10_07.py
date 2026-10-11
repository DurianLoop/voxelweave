"""Full-size actual first-case matched batches, NumPy replay and one CPU update per input."""
import json
import sys
import time
import traceback
from datetime import datetime,timezone
from mc_rc_3d_baseline_v2_2026_10_07 import (
    ROOT,read,sha,array_sha,resource_guard,fixed_cases,source_image,lattice,physical_mr,physical_label,
    read_reference_label,TaskUNet3D,loss,sample_batch,torch,np,SEED,PATCH)
from run_mc_rc_3d_gpu_fit_pilot_2026_10_07 import state_hash
OUT=ROOT/'experiments/mc_rc_3d_real_batch_cpu_2026_10_07'

def replay_batch(image,target,primitive):
    images=[];labels=[]
    for p in primitive:
        start=p['start'];slices=tuple(slice(s,s+n) for s,n in zip(start,PATCH))
        x=image[slices];y=target[slices]
        indices=[np.arange(n-1,-1,-1) if flip else np.arange(n) for n,flip in zip(PATCH,p['flips'])]
        x=np.take(np.take(np.take(x,indices[0],axis=0),indices[1],axis=1),indices[2],axis=2)
        y=np.take(np.take(np.take(y,indices[0],axis=0),indices[1],axis=1),indices[2],axis=2)
        x=x*p['intensity_scale']+p['intensity_shift']
        images.append(x);labels.append(y)
        assert p['target_foreground']==int(y.sum())
        expected=np.minimum(np.maximum(np.asarray(p['center'])-np.asarray(PATCH)//2,0),np.asarray(image.shape)-PATCH)
        assert np.array_equal(start,expected)
        if p['forced_foreground']:assert target[tuple(p['center'])]==1
    return np.stack(images)[:,None],np.stack(labels)[:,None]

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);path=OUT/'attempt_01.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],arms=[],
           script_sha256=sha(__file__),actual_gpu_updates=0,actual_cpu_updates=0,
           scientific_confirmation_patients=0,confirmation_patients_opened=False,
           publication_claim_confirmed=False,source_bindings=[])
    sources=['experiments/mc_rc_3d_baseline_2026_10_07.py','experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
             'experiments/run_mc_rc_3d_gpu_fit_pilot_2026_10_07.py','MC_RC_3D_GPU_FIT_PILOT_PROTOCOL_2026-10-07.md',
             'experiments/mc_rc_3d_baseline_inputs_attempt02_2026_10_07/attempt_01.json']
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        proof=read(ROOT/sources[-1]);assert proof['complete'] and not proof['errors']
        for b in proof['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
        r['source_bindings']=[dict(path=p,sha256=sha(ROOT/p)) for p in sources]
        r['resources_before']=resource_guard()
        role,case,row=fixed_cases()[0];assert role=='development'
        grid=lattice(case);gt=read_reference_label(case);target=physical_label(gt,grid)
        r['patient']=case['patient'];r['uid']=case['uid'];reference=None
        for kind in ('native_reference','raw_pchip'):
            resource_guard();normalized,st=source_image(case,row,kind);image=physical_mr(normalized,grid)
            x,y,primitive=sample_batch(image,target,np.random.default_rng(SEED));rx,ry=replay_batch(image,target,primitive)
            assert np.array_equal(x.numpy(),rx) and np.array_equal(y.numpy(),ry)
            assert list(x.shape)==[2,1,*PATCH] and np.isfinite(x.numpy()).all()
            torch.manual_seed(SEED);model=TaskUNet3D();initial=state_hash(model.state_dict())
            if reference is None:reference=(initial,primitive,array_sha(y.numpy()))
            else:assert (initial,primitive,array_sha(y.numpy()))==reference
            opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
            started=time.perf_counter();outputs=model(x);value=loss(outputs,y);assert torch.isfinite(value);value.backward()
            branches={}
            for name,collection in (('encoder',model.encoders),('decoder',model.decoders),('ups',model.ups),('heads',model.heads)):
                grads=[p.grad for p in collection.parameters()]
                assert all(g is not None and torch.isfinite(g).all() for g in grads)
                maximum=max(float(g.abs().max()) for g in grads);assert maximum>0
                branches[name]=dict(parameters_with_gradient=len(grads),max_absolute_gradient=maximum)
            opt.step();final=state_hash(model.state_dict());assert final!=initial
            arm=dict(kind=kind,shape=list(x.shape),initial_weights_sha256=initial,after_one_cpu_update_weights_sha256=final,
                     physical_image_sha256=array_sha(image),input_batch_sha256=array_sha(x.numpy()),label_batch_sha256=array_sha(y.numpy()),
                     primitive=primitive,full_patch_voxels_replayed=int(rx.size+ry.size),branch_gradients=branches,
                     loss=float(value.detach()),cpu_update_seconds=time.perf_counter()-started,
                     deep_supervision_shapes=[list(o.shape) for o in outputs],
                     deep_supervision_gt_foreground=[int(torch.nn.functional.interpolate(y,size=o.shape[2:],mode='nearest-exact').sum()) for o in outputs],
                     complete=True,diagnostic_checkpoint_saved=False)
            r['arms'].append(arm);r['actual_cpu_updates']+=1;save()
            print(json.dumps(dict(kind=kind,cpu_updates=1,full_patch_voxels_replayed=arm['full_patch_voxels_replayed'],loss=arm['loss'],seconds=arm['cpu_update_seconds'])),flush=True)
            del x,y,rx,ry,image,normalized,model,opt,outputs,value
        r['cuda_initialized']=torch.cuda.is_initialized();assert not r['cuda_initialized']
        r['complete']=len(r['arms'])==2 and r['actual_cpu_updates']==2
        r['resources_after']=resource_guard()
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','actual_cpu_updates','actual_gpu_updates','cuda_initialized')}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
