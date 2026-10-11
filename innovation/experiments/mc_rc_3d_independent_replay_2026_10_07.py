"""Functional checkpoint interpreter and independently constructed full-FOV tiling/resampling."""
import itertools
import numpy as np
import torch
from torch.nn import functional as F

def block(x,state,prefix):
    for conv,norm in ((0,1),(3,4)):
        x=F.conv3d(x,state[prefix+'.layers.'+str(conv)+'.weight'],padding=1)
        x=F.instance_norm(x,weight=state[prefix+'.layers.'+str(norm)+'.weight'],
                          bias=state[prefix+'.layers.'+str(norm)+'.bias'],use_input_stats=True,eps=1e-5)
        x=F.leaky_relu(x,negative_slope=.01)
    return x

def functional_forward(x,state):
    features=[]
    for level in range(4):
        if level:x=F.max_pool3d(x,kernel_size=2,stride=2)
        x=block(x,state,'encoders.'+str(level));features.append(x)
    heads=[]
    for depth,skip in enumerate(reversed(features[:-1])):
        x=F.conv_transpose3d(x,state['ups.'+str(depth)+'.weight'],state['ups.'+str(depth)+'.bias'],stride=2)
        assert x.shape[2:]==skip.shape[2:]
        x=block(torch.cat((x,skip),dim=1),state,'decoders.'+str(depth))
        heads.append(F.conv3d(x,state['heads.'+str(depth)+'.weight'],state['heads.'+str(depth)+'.bias']))
    return tuple(heads[::-1])

def independent_weight(patch):
    # Independent broadcast construction, same specified Gaussian and positive floor.
    functions=[np.exp(-((np.arange(n,dtype=float)-(n-1)/2)**2)/(2*(n/8)**2)) for n in patch]
    weight=functions[0][:,None,None]*functions[1][None,:,None]*functions[2][None,None,:]
    return np.maximum(weight/np.max(weight),1e-4).astype(np.float32)

def independent_starts(shape,patch):
    axes=[]
    for n,p in zip(shape,patch):
        assert n>=p
        values=[];at=0
        while at+p<=n:values.append(at);at+=p//2
        if values[-1]!=n-p:values.append(n-p)
        axes.append(values)
    return axes

def independent_native_resample(physical,shape_rcz):
    nz,nr,nc=physical.shape
    rows=(np.arange(shape_rcz[0],dtype=float)+.5)*nr/shape_rcz[0]-.5
    cols=(np.arange(shape_rcz[1],dtype=float)+.5)*nc/shape_rcz[1]-.5
    rows=np.clip(rows,0,nr-1);cols=np.clip(cols,0,nc-1)
    r0=np.floor(rows).astype(int);r1=np.minimum(r0+1,nr-1);rf=rows-r0
    c0=np.floor(cols).astype(int);c1=np.minimum(c0+1,nc-1);cf=cols-c0
    out=np.empty(shape_rcz,dtype=np.float32)
    for z in range(shape_rcz[2]):
        at=float(np.clip((z+.5)*nz/shape_rcz[2]-.5,0,nz-1));z0=int(np.floor(at));z1=min(z0+1,nz-1);zf=at-z0
        plane=np.zeros(shape_rcz[:2],float)
        for zi,wz in ((z0,1-zf),(z1,zf)):
            for ri,wr in ((r0,1-rf),(r1,rf)):
                for ci,wc in ((c0,1-cf),(c1,cf)):
                    plane+=physical[zi][np.ix_(ri,ci)]*(wz*wr[:,None]*wc[None,:])
        out[:,:,z]=plane
    return out

def independent_inference(state,image,grid,native_shape,patch=(64,128,128)):
    axes=independent_starts(image.shape,patch);locations=list(itertools.product(*axes));weight=independent_weight(patch)
    numerator=np.zeros(image.shape,dtype=np.float64);denominator=np.zeros_like(numerator)
    membership=[np.asarray([[s<=v<s+p for s in axis] for v in range(n)]).sum(axis=1)
                for n,p,axis in zip(image.shape,patch,axes)]
    assert all((m>0).all() for m in membership)
    with torch.inference_mode():
        for at in range(0,len(locations),2):
            group=locations[at:at+2];slices=[tuple(slice(s,s+p) for s,p in zip(start,patch)) for start in group]
            x=torch.from_numpy(np.stack([image[sl] for sl in slices])[:,None])
            prob=functional_forward(x,state)[0].sigmoid().numpy()[:,0]
            assert np.isfinite(prob).all()
            for sl,p in zip(slices,prob):numerator[sl]+=p*weight;denominator[sl]+=weight
    assert np.min(denominator)>0
    probability=numerator/denominator
    z0,r0,c0=[int(p[0]) for p in grid['padding']];nz,nr,nc=grid['unpadded_shape_zrc']
    probability=np.ascontiguousarray(probability[z0:z0+nz,r0:r0+nr,c0:c0+nc],dtype=np.float32)
    native=independent_native_resample(probability,native_shape)
    return native,dict(total_tiles=len(locations),axis_starts=axes,coverage_min=float(denominator.min()),
                       coverage_max=float(denominator.max()),all_voxel_membership_positive=True)

def logical_counts(p,g):
    tp=int(np.count_nonzero(p&g));fp=int(np.count_nonzero(p&~g));fn=int(np.count_nonzero(~p&g));tn=int(np.count_nonzero(~p&~g))
    s=tp+fp;n=tp+fn
    return dict(tn=tn,tp=tp,fp=fp,fn=fn,gt_foreground=n,pred_foreground=s,dice=2*tp/(s+n) if s+n else None,
                recall=tp/n if n else None,precision=tp/s if s else None,absRVE=abs(s-n)/n if n else None,
                empty_prediction=s==0,empty_ground_truth=n==0)
