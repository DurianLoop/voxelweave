"""Acquired-only finite responses. This module never reads a missing target."""
from common import *
import torch
from skimage.transform import resize

def patterns():
 out=[]
 for seed in SEEDS:
  x=np.random.default_rng(seed).choice([-1.,1.],size=(256,256)).astype(np.float32);x-=x.mean();out.append(x)
 return out

def inputs(path):
 with np.load(path) as f:
  raw=f['anchors'];ids=f['anchor_ids'];lo=float(f['lo']);scale=float(f['scale']);mask=f['mask']
 pool={int(j):resize(np.clip((raw[:,:,k]-lo)/scale,0,1),(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32) for k,j in enumerate(ids)}
 return pool,lo,scale,mask

def conditions(pool,z,ctx,anchor=None,fields=None,epsilon=0.):
 left=pool[z+ctx[0]];right=pool[z+ctx[1]];u=-ctx[0]/(ctx[1]-ctx[0]);out=[]
 for field in ([None] if fields is None else fields):
  a=left if anchor!=ctx[0] else np.clip(left+epsilon*field,0,1)
  b=right if anchor!=ctx[1] else np.clip(right+epsilon*field,0,1)
  coarse=(1-u)*a+u*b;out.append(np.stack([a,b,coarse,np.full((256,256),u,np.float32)]))
 return out

def predict(net,conds,shape,lo,scale,batch=4):
 out=[]
 for start in range(0,len(conds),batch):
  cs=conds[start:start+batch];t=torch.from_numpy(np.stack(cs)).to(net.device)
  with torch.inference_mode():res=net.model(t).float().clamp(-1,1)[:,0].cpu().numpy()
  for c,r in zip(cs,res):
   q=np.clip(c[2]+r,0,1);out.append((resize(q,shape,preserve_range=True,anti_aliasing=True)*scale+lo).astype(np.float32))
 return np.stack(out)

def influence(response,ctx_index):
 ref=response[0].astype(np.float64);other=response[ctx_index].astype(np.float64);num=0.
 for a,off in enumerate(REF):
  if off in CONTEXTS[ctx_index]:num+=float(np.sum(ref[a]*other[CONTEXTS[ctx_index].index(off)]))
 den=np.sqrt(np.sum(ref*ref)*np.sum(other*other))
 return num/den if den>0 else np.nan

def compute(net,path,z):
 pool,lo,scale,mask=inputs(path);pats=patterns()
 base=predict(net,[conditions(pool,z,c)[0] for c in CONTEXTS],mask.shape,lo,scale)
 responses=[];epsilons=[.01,.005,.02,-.01]
 for eps in epsilons:
  result=[]
  for ci,ctx in enumerate(CONTEXTS):
   cs=[]
   for anchor in ctx:cs.extend(conditions(pool,z,ctx,anchor,pats,eps))
   q=predict(net,cs,mask.shape,lo,scale)
   result.append((q-base[ci])[...,mask].reshape(2,4,-1))
  responses.append(np.stack(result))
 return {'base':base,'response':np.stack(responses),'mask':mask,'epsilons':np.array(epsilons),'contexts':np.array(CONTEXTS),'lo':lo,'scale':scale}
