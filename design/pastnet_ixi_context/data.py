from pathlib import Path
import json
import torch
from pastnet_ixi_wavelet.data import IXIDataset as SharedDataset,MANIFEST
from pastnet_v2.data import build_sample,device_batch
ROOT=Path(__file__).resolve().parent


class ContextDataset(SharedDataset):
    def __init__(self,manifest,split,anchors=6,**kwargs):
        if split not in ('train','val'):raise ValueError('Test is locked during development')
        if anchors!=6:raise ValueError('Six-slot input required in both arms')
        super().__init__(manifest,split,anchors=4,**kwargs)
        self.anchors=6
        self.intensity_scales={}

    def __getitem__(self,index):
        i,z=self.items[int(self.selection[index])]
        v=self.volume(i)
        if i not in self.intensity_scales:
            meta=json.loads(self.paths[i].with_suffix('.json').read_text())
            self.intensity_scales[i]=max(meta['hi']-meta['lo'],1e-8)
        sample=build_sample(v,self.records[i],z,256,6)
        sample['intensity_scale']=torch.tensor(self.intensity_scales[i],dtype=torch.float64)
        return sample
