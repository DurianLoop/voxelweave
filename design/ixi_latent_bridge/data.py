import json
import numpy as np
import torch
from pastnet_ixi_wavelet.data import IXIDataset,MANIFEST
from pastnet_v2.data import build_sample,device_batch


class Windows(IXIDataset):
    def __init__(self,split,limit=None,sample_limit=None):
        if split not in ('train','val'):raise ValueError('Development is train/validation only')
        super().__init__(MANIFEST,split,limit=limit)
        self.items=[(i,z) for i,r in enumerate(self.records) for z in range(0,r['shape'][2]-12,4)]
        if sample_limit:self.items=self.items[:sample_limit]
        self.sample_count=min(4000,len(self.items)) if split=='train' and sample_limit is None else len(self.items)
        self.scales={};self.set_epoch(3407000)

    def set_epoch(self,seed):
        super().set_epoch(seed);self.epoch_seed=seed

    def sample(self,i,start,interval):
        volume=self.volume(i);window=volume[:,:,start:start+13];record=dict(self.records[i])
        record['geometry']=dict(record['geometry'],z_mm=record['geometry']['z_mm'][start:start+13])
        sample=build_sample(window,record,interval*4,256,4)
        sample['z']=start+interval*4
        sample['teacher_anchors']=torch.from_numpy(np.array(window[:,:,::4],copy=True).transpose(2,0,1)).unsqueeze(1)
        sample['teacher_interval']=torch.tensor(interval,dtype=torch.long)
        sample['teacher_query']=torch.tensor([(interval*4+j)/12 for j in (1,2,3)],dtype=torch.float32)
        return sample

    def __getitem__(self,index):
        i,start=self.items[int(self.selection[index])]
        # Epoch/index, never target intensity, selects one of the three intervals.
        return self.sample(i,start,(self.epoch_seed+int(index))%3)

    def intensity_scale(self,i):
        self.volume(i)
        if i not in self.scales:
            m=json.loads(self.paths[i].with_suffix('.json').read_text())
            self.scales[i]=max(m['hi']-m['lo'],1e-8)
        return self.scales[i]
