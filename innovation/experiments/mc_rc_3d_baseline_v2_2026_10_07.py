"""Exact pixel-center nearest label lattice; preserved first-attempt network/MR support."""
from mc_rc_3d_baseline_2026_10_07 import *

def physical_label(label_rcz,grid):
    source=np.ascontiguousarray(label_rcz.transpose(2,0,1),dtype=bool)
    indices=[]
    for n,m in zip(source.shape,grid['unpadded_shape_zrc']):
        index=((2*np.arange(m,dtype=np.int64)+1)*n)//(2*m)
        assert index.min()>=0 and index.max()<n
        indices.append(index)
    target=source[np.ix_(*indices)].astype(np.float32)
    return np.pad(target,grid['padding'],mode='constant',constant_values=0)
