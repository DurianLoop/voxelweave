"""Artificial source/target fixture; no medical IO and no new worker import."""
import numpy as np
from mc_rc_observed_only_training_input import ObservedMRI

def fixture(which):
    assert which in (1,2)
    rng=np.random.default_rng(20261008+900+which)
    pixels=rng.lognormal(mean=2.,sigma=.5,size=(33,35,5)).astype(np.float32)
    pixels.flags.writeable=False
    observed=ObservedMRI(pixels,(0,4,8,12,16),17,tuple(map(tuple,np.eye(4))),(),())
    grid=dict(unpadded_shape_zrc=[65,129,133],native_shape_zrc=[17,33,35],padding=[(1,2),(2,1),(1,2)])
    target=np.zeros((65,129,133),dtype=np.float32)
    target[9:14,40:45,30:37]=1;target[54:57,118:121,122:125]=1
    target=np.pad(target,grid['padding'],mode='constant')
    return observed,grid,target
