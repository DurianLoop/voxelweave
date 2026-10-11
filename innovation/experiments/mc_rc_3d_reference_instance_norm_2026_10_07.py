"""Functional paired streams: candidate standardized with independently propagated reference moments."""
import torch
from torch.nn import functional as F

def paired_block(candidate,reference,state,prefix,trace):
    for conv,norm in ((0,1),(3,4)):
        weight=state[prefix+'.layers.'+str(conv)+'.weight']
        candidate=F.conv3d(candidate,weight,padding=1)
        reference=F.conv3d(reference,weight,padding=1)
        mean=reference.mean(dim=(2,3,4),keepdim=True)
        variance=reference.var(dim=(2,3,4),unbiased=False,keepdim=True)
        gamma=state[prefix+'.layers.'+str(norm)+'.weight']
        beta=state[prefix+'.layers.'+str(norm)+'.bias']
        if trace is not None:
            cm=candidate.mean(dim=(2,3,4),keepdim=True)
            cv=candidate.var(dim=(2,3,4),unbiased=False,keepdim=True)
            trace.append(dict(layer=prefix+'.layers.'+str(norm),shape=list(reference.shape),
                              mean_max_absolute_delta=float((cm-mean).abs().max()),
                              population_variance_max_absolute_delta=float((cv-variance).abs().max())))
        candidate=(candidate-mean)*torch.rsqrt(variance+1e-5)
        candidate=candidate*gamma[None,:,None,None,None]+beta[None,:,None,None,None]
        reference=F.instance_norm(reference,weight=gamma,bias=beta,use_input_stats=True,eps=1e-5)
        candidate=F.leaky_relu(candidate,negative_slope=.01)
        reference=F.leaky_relu(reference,negative_slope=.01)
    return candidate,reference

def reference_statistics_forward(candidate,reference,state,trace=None):
    assert candidate.shape==reference.shape and candidate.ndim==5
    cs=[];rs=[]
    for level in range(4):
        if level:candidate=F.max_pool3d(candidate,2);reference=F.max_pool3d(reference,2)
        candidate,reference=paired_block(candidate,reference,state,'encoders.'+str(level),trace)
        cs.append(candidate);rs.append(reference)
    ch=[];rh=[]
    for depth,(cskip,rskip) in enumerate(zip(reversed(cs[:-1]),reversed(rs[:-1]))):
        weight=state['ups.'+str(depth)+'.weight'];bias=state['ups.'+str(depth)+'.bias']
        candidate=F.conv_transpose3d(candidate,weight,bias,stride=2)
        reference=F.conv_transpose3d(reference,weight,bias,stride=2)
        candidate,reference=paired_block(torch.cat((candidate,cskip),dim=1),torch.cat((reference,rskip),dim=1),
                                         state,'decoders.'+str(depth),trace)
        weight=state['heads.'+str(depth)+'.weight'];bias=state['heads.'+str(depth)+'.bias']
        ch.append(F.conv3d(candidate,weight,bias));rh.append(F.conv3d(reference,weight,bias))
    return tuple(ch[::-1]),tuple(rh[::-1])
