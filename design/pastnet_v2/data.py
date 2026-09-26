from __future__ import annotations

from collections import OrderedDict
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import torch
from skimage.transform import resize
from torch.utils.data import Dataset


def rich_condition(anchors, phase, valid):
    prev, left, right, next_ = anchors
    coarse = (1-phase)*left + phase*right
    fill = lambda x: np.full_like(left, x)
    dp = (left-prev)*valid[0]
    dn = (next_-right)*valid[3]
    return np.stack([prev,left,right,next_,coarse,fill(phase),right-left,np.abs(right-left),
                     fill(valid[0]),fill(valid[3]),dp,dn,dn-dp]).astype(np.float32)


def physical_vector(geo, original_shape, image_size, z, phase):
    spacing = np.array(geo['spacing'], dtype=np.float32)
    spacing[:2] *= np.array(original_shape[:2]) / image_size
    sk, ok = geo['spacing_known'], geo['orientation_known']
    dz = float(geo['z_mm'][z+4] - geo['z_mm'][z])
    query_mm = float(geo['z_mm'][z+int(round(phase*4))] - geo['z_mm'][z])
    return np.array([*(np.log2(np.maximum(spacing,1e-6))*sk),
                     *(np.array(geo['axes']).ravel()*ok), sk,ok,phase,
                     query_mm/20*sk,(dz-query_mm)/20*sk], dtype=np.float32)


def build_sample(v, rec, z, image_size=256, anchors_count=4):
    depth = v.shape[2]
    offsets = (-4,0,4,8) if anchors_count == 4 else (-8,-4,0,4,8,12)
    indices = [z+d for d in offsets]
    valid = np.array([0 <= k < depth for k in indices], dtype=np.float32)
    # Missing anchors repeat an observed endpoint and carry a strict zero mask.
    clipped = [min(max(k,z%4),(depth-1-z%4)//4*4+z%4) for k in indices]
    anchors = np.stack([v[:,:,k] for k in clipped]).astype(np.float32)
    center = slice(0,4) if anchors_count == 4 else slice(1,5)
    cond = np.stack([rich_condition(anchors[center], q, valid[center]) for q in (.25,.5,.75)])
    geo = rec['geometry']
    zpos = np.array(geo['z_mm'], dtype=np.float32)
    anchor_mm = (zpos[clipped]-zpos[z])*geo['spacing_known']
    # When geometry is missing use relative index distances only, with explicit mask.
    distance = anchor_mm if geo['spacing_known'] else np.array(offsets, np.float32)
    return dict(cond=torch.from_numpy(cond), anchors=torch.from_numpy(anchors[:,None]),
                valid=torch.from_numpy(valid), anchor_z=torch.from_numpy(distance.astype(np.float32)),
                physical=torch.from_numpy(np.stack([physical_vector(geo,rec['shape'],image_size,z,q) for q in (.25,.5,.75)])),
                target=torch.from_numpy(np.stack([v[:,:,z+j][None] for j in (1,2,3)])),
                case_id=rec['case_id'], patient_id=rec['patient_id'], z=z)


class IntervalDataset(Dataset):
    def __init__(self, manifest, split, image_size=256, anchors=4, limit=None, sample_limit=None,
                 allow_locked_test=False):
        if split == 'test' and not allow_locked_test:
            raise ValueError('Test requires locked external evaluation')
        content = json.loads(Path(manifest).read_text(encoding='utf-8'))
        self.records = [r for r in content['records'] if r['split']==split][:limit]
        self.image_size, self.anchors = image_size, anchors
        self.items=[]
        for i,r in enumerate(self.records):
            if 'geometry' not in r:
                from .prepare import geometry
                r['geometry'] = geometry(r)
                r['shape'] = list(nib.load(r['path']).shape)
            # Train shifts are separate simulated sparse grids. Validation uses the
            # acquisition grid z=0,4,..., identical across every experiment.
            step = 1 if split=='train' else 4
            self.items.extend((i,z) for z in range(0,r['shape'][2]-4,step))
        if sample_limit:
            self.items = self.items[:sample_limit]
        if not self.items:
            raise ValueError(f'Empty {split} dataset')
        self.cache = OrderedDict()

    def __len__(self):
        return len(self.items)

    def __getitem__(self,index):
        i,z = self.items[index]
        rec=self.records[i]
        key=(i,z%4)
        if key not in self.cache:
            raw=nib.load(rec['path']).get_fdata(dtype=np.float32)
            observed=raw[:,:,z%4::4]
            lo,hi=float(observed.min()),float(observed.max())
            # Never use withheld slice extrema to normalize model inputs.
            normalized=(raw-lo)/max(hi-lo,1e-8)
            v=resize(normalized,(self.image_size,self.image_size,raw.shape[2]),
                     anti_aliasing=True,preserve_range=True).astype(np.float32)
            self.cache[key]=v
            while len(self.cache)>4:
                self.cache.popitem(last=False)
        v=self.cache.pop(key)
        self.cache[key]=v
        return build_sample(v,rec,z,self.image_size,self.anchors)


def device_batch(batch, device):
    return {k:v.to(device) if isinstance(v,torch.Tensor) else v for k,v in batch.items()}
