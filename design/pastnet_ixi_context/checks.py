import json
import numpy as np
import torch
from torch.utils.data import DataLoader
from pastnet_v2.run import seed_all
from pastnet_v2.common import sha256,write_json
from pastnet_ixi_wavelet.run import load_model as original_model
from pastnet_ixi_wavelet.data import IXIDataset
from .data import ContextDataset,ROOT,MANIFEST,device_batch
from .model import load_model,INIT,INIT_SHA
from .run import hashes
from .metrics import measure


def main():
    assert sha256(INIT)==INIT_SHA
    content=json.loads(MANIFEST.read_text());probe={}
    for split in ('train','val'):
        counts=[]
        for r in content['records']:
            if r['split']!=split:continue
            for z in range(0,r['shape'][2]-4,4):counts.append(sum(0<=z+d<r['shape'][2] for d in (-8,-4,0,4,8,12)))
        probe[split]=dict(intervals=len(counts),mean_real_anchors=float(np.mean(counts)),fraction_all_six=float(np.mean(np.array(counts)==6)))
    ds=ContextDataset(MANIFEST,'val',limit=1,sample_limit=4);old=IXIDataset(MANIFEST,'val',limit=1,sample_limit=4)
    for i in range(4):
        a,b=ds[i],old[i]
        assert torch.equal(a['cond'],b['cond']) and torch.equal(a['target'],b['target'])
        assert torch.equal(a['anchors'][1:5],b['anchors']) and torch.equal(a['valid'][1:5],b['valid'])
    tr=ContextDataset(MANIFEST,'train');tr.set_epoch(3407001);selection=tr.selection.copy();tr.set_epoch(3407001);assert np.array_equal(selection,tr.selection)
    seed_all(3407);local=load_model('local').cuda().eval();seed_all(3407);extended=load_model('extended').cuda().eval()
    assert all(torch.equal(local.state_dict()[k],extended.state_dict()[k]) for k in local.state_dict())
    b=device_batch(next(iter(DataLoader(ds,batch_size=1))),torch.device('cuda'))
    base=original_model('wavelet3',INIT).cuda().eval();central=dict(b)
    for k in ('anchors','valid','anchor_z'):central[k]=b[k][:,1:5]
    with torch.no_grad(),torch.autocast('cuda'):
        initial=base(central);assert torch.equal(initial,local(b)) and torch.equal(initial,extended(b))
        assert torch.equal(initial,extended(dict(b,target=torch.full_like(b['target'],float('nan')))))
    # Make the context path active to verify its information contract.
    b=device_batch({k:v[None] for k,v in ds[2].items() if isinstance(v,torch.Tensor)},torch.device('cuda'))
    with torch.no_grad():
        local.trajectory_adapter.project.weight.normal_(0,.01)
        extended.load_state_dict(local.state_dict())
        changed=dict(b);changed['anchors']=b['anchors'].clone();changed['anchors'][:,[0,5]]+=1.
        with torch.autocast('cuda'):
            l1=local(b);l2=local(changed);e1=extended(b);e2=extended(changed)
        assert torch.equal(l1,l2),'Far input leaked into local'
        effect=float((e1-e2).abs().max());assert effect>1e-6,'Extended cannot consume far anchors'
    rng=np.random.default_rng(4);target=rng.random((32,32)).astype(np.float32)*.4;pred=target+rng.normal(0,.01,target.shape)
    measured=measure(pred,target,(1.,1.));expected=20*np.log10(float(target.max()-target.min()))-10*np.log10(np.mean((pred-target)**2))
    assert abs(measured['psnr']-expected)<1e-9
    cases={s:{x['patient_id'] for x in content['records'] if x['split']==s} for s in ('train','val','test')}
    assert not (cases['train']&cases['val'] or cases['train']&cases['test'] or cases['val']&cases['test'])
    result=dict(passed=True,code_hashes=hashes(),init_sha256=INIT_SHA,initial_parameters_identical=True,
        initial_predictions_equal_fixed_wavelet=True,target_not_used=True,central_input_bitwise_matches_old=True,
        local_far_invariance=True,extended_far_effect=effect,main_table_psnr_formula_verified=True,patient_disjoint=True,
        train_validation_information=probe,test_images_opened=False,parameters=sum(p.numel() for p in local.parameters()))
    write_json(ROOT/'results/checks.json',result);print(json.dumps({k:v for k,v in result.items() if k!='code_hashes'},indent=2))


if __name__=='__main__':main()
