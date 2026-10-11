"""Equal-capacity observed-only representation utilities. No GT/native loader API."""
import numpy as np
from mc_rc_3d_baseline_v2_2026_10_07 import (ROOT,read,sha,array_sha,lattice,physical_mr,TaskUNet3D,torch,nn,SEED)
from mc_rc_observed_only_training_input import ObservedMRI,reconstruct,stats,DEVELOPERS

def development_observed_cases():
    prep=read(ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json')
    cert=read(ROOT/'experiments/mc_rc_development_training_input_cpu/attempt_01.json')
    assert prep['complete'] and cert['complete'] and not prep['errors'] and not cert['errors']
    assert len(prep['cases'])==len(cert['series'])==19
    assert {c['patient'] for c in prep['cases']}==DEVELOPERS
    rows={r['uid']:r for r in cert['series']}
    return sorted([(c,rows[c['uid']]) for c in prep['cases']],key=lambda cr:(cr[0]['patient'],cr[0]['uid']))

def load_development_observed(case,row):
    assert case['patient'] in DEVELOPERS
    p=ROOT/row['observed_package'];assert sha(p)==row['observed_package_sha256']
    with np.load(p,allow_pickle=False) as q:
        values=q['observed_rcz'].copy();indices=tuple(map(int,q['observed_indices']))
        affine=q['affine_rcz_ras'].copy();shape=q['native_shape'].copy()
    assert values.dtype==np.float32 and np.isfinite(values).all()
    assert array_sha(values)==row['observed_array_sha256']
    assert np.array_equal(shape,case['native_shape']) and np.array_equal(affine,case['affine_rcz_ras'])
    assert indices==tuple(range(0,int(shape[2]),4))
    assert list(values.shape)==[int(shape[0]),int(shape[1]),len(indices)]
    values.flags.writeable=False
    return ObservedMRI(values,indices,int(shape[2]),tuple(map(tuple,affine)),(),())

def native_fields(observed):
    """Return normalized PCHIP, weighted sparse numerator, binary availability, statistics."""
    st=stats(observed.pixels)
    raw=reconstruct(observed,'raw_pchip')
    dense=((raw.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
    values=((observed.pixels.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
    numerator=np.zeros_like(dense);mask=np.zeros_like(dense)
    numerator[:,:,observed.indices]=values;mask[:,:,observed.indices]=1
    assert np.array_equal(dense[:,:,observed.indices],values)
    return raw,dense,numerator,mask,st

def physical_fields(observed,grid):
    raw,dense,numerator,mask,st=native_fields(observed)
    fields=dict(dense=physical_mr(dense,grid),numerator=physical_mr(numerator,grid),availability=physical_mr(mask,grid))
    valid=np.ones(grid['unpadded_shape_zrc'],dtype=np.float32)
    fields['valid_grid']=np.pad(valid,grid['padding'],mode='constant')
    return fields,st,dict(raw=array_sha(raw),normalized=array_sha(dense),numerator=array_sha(numerator),mask=array_sha(mask))

def augment_pair(values,availability,valid_grid,scale,shift,kind,flips=(False,False,False)):
    assert kind in ('dense','direct') and scale>0 and np.isfinite([scale,shift]).all()
    assert values.shape==availability.shape==valid_grid.shape
    out=scale*values+shift*(availability if kind=='direct' else valid_grid)
    out=np.where(valid_grid>0,out,np.float32(0)).astype(np.float32)
    mask=availability
    for axis,flag in enumerate(flips):
        if flag:out=np.flip(out,axis);mask=np.flip(mask,axis)
    return np.stack([out,mask]).astype(np.float32,copy=False)

def canonical_states():
    torch.manual_seed(SEED);base=TaskUNet3D()
    one={k:v.detach().clone() for k,v in base.state_dict().items()}
    two={k:v.clone() for k,v in one.items()};key='encoders.0.layers.0.weight'
    two[key]=torch.cat((one[key],torch.zeros_like(one[key])),dim=1)
    return one,two

def two_channel_model(state):
    model=TaskUNet3D()
    model.encoders[0].layers[0]=nn.Conv3d(2,16,3,padding=1,bias=False)
    model.load_state_dict(state,strict=True)
    return model
