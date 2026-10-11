import json
import numpy as np
import torch
from torch.utils.data import DataLoader
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.common import sha256,write_json
from pastnet_v2.run import seed_all
from .data import IXIDataset,ROOT,MANIFEST
from .run import hashes,load_model,INIT

def main():
    seed_all(3407)
    assert sha256(INIT)=='6f9002aa41c90ecfab3038dddd65c1a43cd494affb417af14bed82fcdd642728'
    d=IXIDataset(MANIFEST,'val',limit=1,sample_limit=1)
    old=IntervalDataset(MANIFEST,'val',limit=1,sample_limit=1)
    a,b=d[0],old[0]
    for key in ('cond','anchors','physical','target','valid'):assert torch.equal(a[key],b[key]),key
    train=IXIDataset(MANIFEST,'train');assert len(train)==4000
    train.set_epoch(3407001);first=train.selection.copy();train.set_epoch(3407001);assert np.array_equal(first,train.selection)
    train.set_epoch(3407002);assert not np.array_equal(first,train.selection) and len(set(train.selection))==4000
    assert all(z%4==0 for i,z in train.items)
    groups={s:{r['patient_id'] for r in json.loads(MANIFEST.read_text())['records'] if r['split']==s} for s in ('train','val','test')}
    assert not any(groups[x]&groups[y] for x,y in [('train','val'),('train','test'),('val','test')])
    m=load_model('wavelet3').cuda().eval();batch=device_batch(next(iter(DataLoader(d,batch_size=1))),torch.device('cuda'))
    with torch.no_grad(),torch.autocast('cuda'):
        pred=m(batch);assert torch.isfinite(pred).all()
        assert torch.equal(pred,m(dict(batch,target=torch.full_like(batch['target'],float('nan')))))
    from .test import I3,i3net_volume
    from i3net_strict_reference.model import Reference
    p=torch.load(I3,map_location='cpu',weights_only=False);ref=Reference();ref.network.load_state_dict(p['model_state_dict'],strict=True)
    # Independent legacy network plus CPU overlap-add on two adjacent windows.
    import sys
    from argparse import Namespace
    from i3net_strict_reference.model import CONFIG
    sys.path.insert(0,str(ROOT.parents[1]/'external/I3Net'))
    from model_zoo.i3net.basic_model import I3Net
    legacy=I3Net(Namespace(**CONFIG)).cuda().eval();legacy.load_state_dict(p['model_state_dict'],strict=True)
    ref=ref.cuda().eval();v=d.volume(0)[:,:,:17];expected=np.zeros_like(v);counts=np.zeros_like(v)
    with torch.no_grad():
        for start in range(2):
            inp=torch.from_numpy(np.array(v[:,:,start*4:start*4+13:4],copy=True)).unsqueeze(0).cuda()
            out=legacy(inp).float().clamp(0,1)[0].cpu().numpy()
            expected[:,:,start*4:start*4+13]+=out;counts[:,:,start*4:start*4+13]+=1
        actual=i3net_volume(ref.network,v)
    parity_error=float(np.abs(actual-expected/counts).max());assert parity_error<1e-6,parity_error
    result=dict(passed=True,cache_bitwise_matches_original=True,epoch_sampling_reproducible=True,patient_disjoint=True,
        target_not_read=True,init_sha256=sha256(INIT),i3net_sha256=sha256(I3),i3net_weights_strict_load=True,
        i3net_legacy_clamped_overlap_max_error=parity_error,
        counts={s:len(v) for s,v in groups.items()},train_intervals_available=len(train.items),samples_per_epoch=len(train),code_hashes=hashes())
    write_json(ROOT/'results/checks.json',result);print(json.dumps({k:v for k,v in result.items() if k!='code_hashes'},indent=2))
if __name__=='__main__':main()
