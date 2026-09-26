import numpy as np
from scipy.stats import rankdata
def corr(a,b):
    a=rankdata(a,axis=-1); b=rankdata(b,axis=-1)
    a-=a.mean(-1,keepdims=True); b-=b.mean(-1,keepdims=True)
    with np.errstate(divide='ignore',invalid='ignore'): return (a*b).sum(-1)/np.sqrt((a*a).sum(-1)*(b*b).sum(-1))
def partial(a,b,c):
    x,y,z=corr(a,b),corr(a,c),corr(b,c)
    with np.errstate(divide='ignore',invalid='ignore'): return (x-y*z)/np.sqrt((1-y*y)*(1-z*z))
def ci(a): return np.nanquantile(a,[.025,.975]).tolist()
def gain(y,x,budget):
    k=int(np.ceil(budget*x.shape[-1])); order=np.argsort(-x,axis=-1,kind='stable')[...,:k]
    return np.take_along_axis(y,order,axis=-1).mean(-1)-y.mean(-1)
def naurc(y,x):
    order=np.argsort(x,axis=-1,kind='stable'); ys=np.take_along_axis(y,order,axis=-1)
    div=np.arange(1,y.shape[-1]+1)
    auc=(np.cumsum(ys,axis=-1)/div).mean(-1)
    oracle=(np.cumsum(np.sort(y,axis=-1),axis=-1)/div).mean(-1)
    worst=(np.cumsum(np.sort(y,axis=-1)[...,::-1],axis=-1)/div).mean(-1)
    return (auc-oracle)/(worst-oracle)
