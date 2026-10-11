import json,os
from pathlib import Path
from collections import OrderedDict
import nibabel as nib
import numpy as np
from skimage.transform import resize
from torch.utils.data import Dataset
from pastnet_v2.data import build_sample,device_batch
from pastnet_v2.prepare import geometry
from pastnet_v2.common import sha256,write_json
ROOT=Path(__file__).resolve().parent
MANIFEST=ROOT/'manifest.json'

class IXIDataset(Dataset):
    def __init__(self,manifest,split,image_size=256,anchors=4,limit=None,sample_limit=None,allow_locked_test=False):
        if split=='test' and not allow_locked_test:raise ValueError('Test requires frozen trained checkpoint')
        self.records=[r for r in json.loads(Path(manifest).read_text())['records'] if r['split']==split][:limit]
        self.split=split;self.items=[];self.anchors=anchors;self.paths={};self.mmaps=OrderedDict()
        if image_size!=256 or anchors!=4:raise ValueError('Fixed 256 x4 four-anchor contract')
        for i,r in enumerate(self.records):
            if 'geometry' not in r:r.update(geometry=geometry(r),shape=list(nib.load(r['path']).shape))
            self.items.extend((i,z) for z in range(0,r['shape'][2]-4,4))
        if sample_limit:self.items=self.items[:sample_limit]
        self.sample_count=min(4000,len(self.items)) if split=='train' and sample_limit is None else len(self.items)
        self.set_epoch(3407000)
    def set_epoch(self,seed):
        self.selection=np.random.default_rng(seed).choice(len(self.items),self.sample_count,replace=False) if self.split=='train' else np.arange(len(self.items))
    def __len__(self):return self.sample_count
    def volume(self,i):
        rec=self.records[i]
        if i not in self.paths:
            digest=sha256(Path(rec['path']));path=ROOT/'cache'/f"{rec['case_id']}_{digest[:16]}_obs0_f32.npy"
            path.parent.mkdir(exist_ok=True)
            if not path.exists() or not path.with_suffix('.json').exists():
                raw=nib.load(rec['path']).get_fdata(dtype=np.float32)
                observed=raw[:,:,::4];lo,hi=float(observed.min()),float(observed.max())
                v=resize((raw-lo)/max(hi-lo,1e-8),(256,256,raw.shape[2]),anti_aliasing=True,preserve_range=True).astype(np.float32)
                tmp=path.with_suffix('.tmp')
                with tmp.open('wb') as f:np.save(f,v)
                tmp.replace(path)
                write_json(path.with_suffix('.json'),dict(source_sha256=digest,lo=lo,hi=hi,grid=0,shape=list(v.shape),cache_sha256=sha256(path)))
            meta=json.loads(path.with_suffix('.json').read_text())
            if meta['source_sha256']!=digest or meta['cache_sha256']!=sha256(path):raise ValueError('Changed cache/source')
            self.paths[i]=path
        if i in self.mmaps:v=self.mmaps.pop(i)
        else:v=np.load(self.paths[i],mmap_mode='r')
        self.mmaps[i]=v
        while len(self.mmaps)>4:self.mmaps.popitem(last=False)
        return v
    def __getitem__(self,index):
        i,z=self.items[int(self.selection[index])]
        return build_sample(self.volume(i),self.records[i],z,256,4)
