from pathlib import Path
import sys,importlib
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING';C=P.parent/'ARCHITECTURE_COVERAGE_CLOSURE'
sys.path.insert(0,str(B/'scripts'))
from common import read,sha,CONTEXTS,REF,metrics,write
from acquired_probe import inputs,patterns,conditions,influence
import numpy as np,torch
from skimage.transform import resize

MODELS=['linear','acvtt','resunet','smamba_unet','arssr']
def load(ds,m):
    if m=='linear':return None
    r=next(x for x in read(P/'model_registry.json') if x['dataset']==ds and x['model']==m)
    assert sha(ROOT/r['checkpoint'])==r['sha256']
    mod,cls={'acvtt':('ixi_acvtt_2p5d.train','ACVTT2p5DInterpolator'),'resunet':('ixi_diffusion.resunet','ResUNetResidualInterpolator'),'smamba_unet':('ixi_smamba_unet_2p5d.train','SMambaUNet2p5DInterpolator'),'arssr':('ixi_arssr.inference','ArSSRInterpolator')}[m]
    module=importlib.import_module(mod)
    # Native low-level wrapper comparison uses the inherited FP32 experiment,
    # never the mixed-precision reconstruction-benchmark contract.
    if hasattr(module,'_autocast_enabled'):module._autocast_enabled=lambda device:False
    net=getattr(module,cls)(ROOT/r['checkpoint'],device='cuda')
    assert all(torch.isfinite(x).all() for x in net.model.state_dict().values())
    return net

def normalized(net,m,conds,ctx):
    if m=='linear':return np.stack([c[2] for c in conds])
    out=[]
    if m=='arssr':
        from ixi_arssr.inference import _densify_sparse
        span=ctx[1]-ctx[0];z=-ctx[0]
        yy,xx=np.meshgrid(np.arange(256,dtype=np.float32),np.arange(256,dtype=np.float32),indexing='ij')
        coords=np.stack([xx.ravel()/255*2-1,yy.ravel()/255*2-1,np.full(65536,z,np.float32)/span*2-1],axis=1)
        c=torch.from_numpy(coords[None]).to(net.device)
        for condition in conds:
            dense=_densify_sparse(condition[:2],stride=span)
            t=torch.from_numpy(dense[None,None]).to(net.device)
            with torch.inference_mode():q=net.model(t,c).float().clamp(0,1)[0,:,0].cpu().numpy().reshape(256,256)
            out.append(q)
        return np.stack(out)
    for start in range(0,len(conds),4):
        cs=conds[start:start+4];t=torch.from_numpy(np.stack(cs)).to(net.device)
        if m in ['acvtt','smamba_unet']:t=t.contiguous(memory_format=torch.channels_last)
        with torch.inference_mode():q=net.model(t).float()
        if m=='acvtt':q=q.clamp(0,1)[:,0].cpu().numpy()
        else:
            residual=q.clamp(-1,1)[:,0].cpu().numpy();q=np.clip(np.stack([c[2] for c in cs])+residual,0,1)
        out.extend(q)
    return np.stack(out)

def predict(net,m,conds,ctx,shape,lo,scale):
    qs=normalized(net,m,conds,ctx)
    return np.asarray([(resize(q,shape,preserve_range=True,anti_aliasing=True)*scale+lo).astype(np.float32) for q in qs])

def validate(net,m,inp,z):
    pool,lo,scale,mask=inputs(inp);rows=[]
    for ctx in CONTEXTS:
        c=conditions(pool,z,ctx)[0];q=normalized(net,m,[c],ctx)[0]
        if m=='arssr':
            native=net._predict_hr128(np.moveaxis(c[:2],0,2),ctx[1]-ctx[0]+1)[-ctx[0]]
        elif m=='acvtt':native=net._predict(c)
        elif m=='resunet':native=np.clip(c[2]+net._predict_residual(torch.from_numpy(c[None]).to(net.device)),0,1)
        elif m=='smamba_unet':native=np.clip(c[2]+net._predict_residual(c),0,1)
        else:
            u=-ctx[0]/(ctx[1]-ctx[0]);native=(1-u)*c[0]+u*c[1]
        rep=normalized(net,m,[c,c,c,c] if m!='arssr' else [c],ctx)
        diff=float(abs(q-native).max());repeat=float(abs(rep-q).max())
        rows.append(dict(context=ctx,native_max_difference=diff,repeat_batch_max_difference=repeat,pass_check=diff<=1e-5 and repeat<=1e-6))
    return rows

def compute(net,m,path,z):
    pool,lo,scale,mask=inputs(path);pats=patterns();epsilons=[.01,.005,.02,-.01]
    base=np.stack([predict(net,m,conditions(pool,z,c),c,mask.shape,lo,scale)[0] for c in CONTEXTS])
    response=[]
    for eps in epsilons:
        arr=[]
        for ci,ctx in enumerate(CONTEXTS):
            cs=[]
            for anchor in ctx:cs.extend(conditions(pool,z,ctx,anchor,pats,eps))
            q=predict(net,m,cs,ctx,mask.shape,lo,scale)
            arr.append((q-base[ci])[...,mask].reshape(2,4,-1))
        response.append(np.stack(arr))
    return dict(base=base,response=np.stack(response),mask=mask,epsilons=np.array(epsilons),contexts=np.array(CONTEXTS),lo=lo,scale=scale)
