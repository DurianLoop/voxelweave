"""Independent sampled coordinate derivation and functional synthetic optimizer replay."""
import gc,hashlib,json,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from mc_rc_3d_baseline_v2_2026_10_07 import ROOT,torch,TaskUNet3D,SEED,physical_mr
from mc_rc_reference_resources_2026_10_07 import resource_guard
from mc_rc_3d_independent_replay_2026_10_07 import functional_forward
from torch.nn import functional as F
OUT=ROOT/'experiments/mc_rc_3d_direct_observed_independent_2026_10_07'
SOURCE=ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arrsha(a):
    a=np.ascontiguousarray(a);h=hashlib.sha256(json.dumps(dict(shape=list(a.shape),dtype=a.dtype.str),sort_keys=True).encode())
    h.update(memoryview(a).cast('B'));return h.hexdigest()
def statehash(state):
    h=hashlib.sha256()
    for k,v in state.items():h.update(k.encode());h.update(arrsha(v.detach().numpy()).encode())
    return h.hexdigest()
def equal(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.shape==b.shape and a.dtype==b.dtype and torch.equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return isinstance(b,type(a)) and len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b
def interpolate_at(field_rcz,coords_zrc,native_shape,physical_shape):
    old=np.asarray(native_shape)[[2,0,1]];new=np.asarray(physical_shape)
    at=np.clip((coords_zrc+.5)*old/new-.5,0,old-1)
    low=np.floor(at).astype(int);high=np.minimum(low+1,old-1);frac=at-low
    result=np.zeros(len(at),dtype=np.float64)
    for z in range(2):
        for r in range(2):
            for c in range(2):
                flags=np.asarray([z,r,c]);idx=np.where(flags,high,low)
                w=np.prod(np.where(flags,frac,1-frac),axis=1)
                result+=field_rcz[idx[:,1],idx[:,2],idx[:,0]]*w
    return result
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);start=time.perf_counter()
    q=json.loads(SOURCE.read_text(encoding='utf-8'));assert q['complete'] and not q['errors'] and all(q['gate'].values())
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],script_sha256=sha(__file__),
           source_sha256=sha(SOURCE),actual_MRI_forwards=0,actual_MRI_training_updates=0,actual_synthetic_updates=0,
           CUDA_initialized=False,confirmation_patients_opened=False,publication_claim_confirmed=False)
    path=OUT/'attempt01.json';reads=set();blocked=[]
    def audit(event,args):
        if event!='open' or not args or not isinstance(args[0],(str,bytes)):return
        try:p=Path(args[0]).resolve()
        except (OSError,ValueError,TypeError):return
        mode=args[1] if len(args)>1 else None
        if isinstance(mode,str) and 'r' not in mode and '+' not in mode:return
        if p.is_relative_to(ROOT):
            rel=p.relative_to(ROOT).as_posix()
            if p.name.endswith(('.zip','.nii','.nii.gz')) or any(x in rel for x in ('mc_rc_validation_task','mc_rc_true_native_reference_attempt','confirmation')):
                blocked.append(rel);raise PermissionError('Independent replay prohibits native/GT/validation reads: '+rel)
            reads.add(rel)
    sys.addaudithook(audit)
    def save():path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def guard():
        assert time.perf_counter()-start<=600
        result=resource_guard();assert torch.get_num_threads()==4 and torch.get_num_interop_threads()==1
        assert not torch.cuda.is_initialized() and sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<=5_000_000
        result['cpu_threads']=4;return result
    save()
    try:
        torch.set_num_threads(4);r['resources_before']=guard()
        r['source_bindings']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [SOURCE,
            ROOT/'MC_RC_3D_DIRECT_OBSERVED_INDEPENDENT_REPLAY_PROTOCOL_2026-10-07.md',
            ROOT/'experiments/mc_rc_3d_independent_replay_2026_10_07.py',
            ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',Path(__file__)]]
        for index,rec in enumerate(q['series']):
            guard();p=ROOT/rec['observed_package'];assert sha(p)==rec['observed_package_sha256']
            with np.load(p,allow_pickle=False) as obs:
                a=obs['observed_rcz'];idx=obs['observed_indices'].astype(int);shape=obs['native_shape'].astype(int)
                assert arrsha(a)==rec['observed_array_sha256']
                mean=np.mean(a,dtype=np.float64);std=np.std(a,dtype=np.float64);divisor=std if std else 1.
                vals=((a.astype(np.float64)-mean)/divisor).astype(np.float32)
                numerator=np.zeros(shape,dtype=np.float32);mask=np.zeros(shape,dtype=np.float32)
                numerator[:,:,idx]=vals;mask[:,:,idx]=1
            assert arrsha(numerator)==rec['native_numerator_sha256'] and arrsha(mask)==rec['native_binary_availability_sha256']
            g=rec['grid'];num_p=physical_mr(numerator,g);mask_p=physical_mr(mask,g)
            assert arrsha(num_p)==rec['physical_numerator_sha256'] and arrsha(mask_p)==rec['physical_availability_sha256']
            new=np.asarray(g['unpadded_shape_zrc']);coords=np.random.default_rng(np.random.SeedSequence([SEED,703,index])).integers(0,new,size=(512,3))
            special=[]
            for z in idx:
                at=int(np.rint((int(z)+.5)*new[0]/shape[2]-.5))
                for dz in (-1,0,1):
                    for rr,cc in ((0,0),(new[1]//2,new[2]//2),(new[1]-1,new[2]-1)):
                        special.append([np.clip(at+dz,0,new[0]-1),rr,cc])
            coords=np.unique(np.concatenate((coords,np.asarray(special,dtype=int))),axis=0)
            padded=coords+np.asarray([lo for lo,hi in g['padding']]);rows=[]
            for name,native,actual in [('numerator',numerator,num_p),('availability',mask,mask_p)]:
                expected=interpolate_at(native,coords,shape,new);samples=actual[tuple(padded.T)]
                error=float(np.max(np.abs(samples-expected)));assert np.allclose(samples,expected,atol=3e-5,rtol=3e-5)
                rows.append(dict(channel=name,samples=len(samples),max_abs_error=error,passed=True))
            r['series'].append(dict(patient=rec['patient'],uid=rec['uid'],native_hashes_equal=True,physical_hashes_equal=True,checks=rows))
            del a,vals,numerator,mask,num_p,mask_p;gc.collect();save()
        torch.manual_seed(SEED);base=TaskUNet3D();weights={k:v.detach().clone() for k,v in base.state_dict().items()};del base
        key='encoders.0.layers.0.weight';weights[key]=torch.cat((weights[key],torch.zeros_like(weights[key])),dim=1)
        assert statehash(weights)==q['model_checks']['canonical_two_state_sha256']
        parameters={k:torch.nn.Parameter(v) for k,v in weights.items()};opt=torch.optim.AdamW(parameters.values(),lr=.0001,weight_decay=.0001)
        original=next(a for a in q['synthetic_arms'] if a['kind']=='direct')
        cp=ROOT/original['checkpoint']['file'];assert sha(cp)==original['checkpoint']['sha256']
        saved=torch.load(cp,map_location='cpu',weights_only=False)
        # Per-step batches have their own NumPy seeds; functional replay consumes no torch RNG.
        torch.set_rng_state(saved['torch_rng']);losses=[]
        for step in (0,1):
            guard();gen=np.random.default_rng(SEED+700+step)
            signal=gen.normal(size=(2,16,32,32)).astype(np.float32)
            valid=(gen.random((2,16,32,32))<.25).astype(np.float32)
            inputs=torch.from_numpy(np.stack([signal*valid,valid],axis=1))
            truth=torch.from_numpy((gen.random((2,1,16,32,32))<.06).astype(np.float32))
            assert arrsha(inputs.numpy())==original['first' if step==0 else 'second']['input_sha256']
            outputs=functional_forward(inputs,parameters);parts=[]
            for o in outputs:
                y=F.interpolate(truth,size=o.shape[2:],mode='nearest-exact');prob=o.sigmoid()
                parts.append(F.binary_cross_entropy_with_logits(o,y)+1-(2*(prob*y).sum()+1)/(prob.sum()+y.sum()+1))
            # Preserve BCE+(1-Dice) grouping to avoid changing float32 rounding.
            terms=[]
            for o in outputs:
                y=F.interpolate(truth,size=o.shape[2:],mode='nearest-exact');prob=o.sigmoid()
                bce=F.binary_cross_entropy_with_logits(o,y);d=1-(2*(prob*y).sum()+1)/(prob.sum()+y.sum()+1)
                terms.append(bce+d)
            value=sum(v*w for v,w in zip(terms,(4/7,2/7,1/7)))
            assert float(value.detach())==original['first' if step==0 else 'second']['loss']
            opt.zero_grad(set_to_none=True);value.backward()
            assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in parameters.values())
            opt.step();r['actual_synthetic_updates']+=1;losses.append(float(value.detach()))
            if step==0:
                assert equal({k:v.detach() for k,v in parameters.items()},saved['model'])
                assert equal(opt.state_dict(),saved['optimizer']) and torch.equal(torch.get_rng_state(),saved['torch_rng'])
                assert saved['step']==1 and saved['synthetic_batch_seeds']==[SEED+700,SEED+701]
        finalhash=statehash(parameters);assert finalhash==original['final_model_sha256']
        r['synthetic_replay']=dict(functional_forward_used=True,canonical_initial_hash_equal=True,losses=losses,
                                   first_update_model_optimizer_tree_exact=True,checkpoint_rng_preserved_without_random_draw=True,
                                   final_model_sha256=finalhash,final_model_hash_equal=True)
        assert not blocked
        r['io_audit']=dict(workspace_read_paths=sorted(reads),prohibited_access_attempts=blocked,native_GT_validation_pixels_read=False)
        r['resources_after']=guard();r['complete']=True
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-start;r['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print(json.dumps(dict(complete=r['complete'],errors=r['errors'],series=len(r['series']),synthetic_updates=r['actual_synthetic_updates'],elapsed_seconds=r['elapsed_seconds']),ensure_ascii=False))
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
