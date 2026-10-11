import argparse,copy,json,subprocess,sys
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader
from pastnet_v2.common import sha256,write_json
from pastnet_v2.run import seed_all
from .run import hashes,validate_sources,ROOT
from .data import Windows,device_batch
from .model import Teacher,Bridge
from .metrics import interval_batch


def contracts():
    validate_sources();seed_all(3407);ds=Windows('val',limit=1)
    sample=ds.sample(0,4,1);original=ds.volume
    volume=np.array(original(0),copy=True);volume[:,:,1::4]+=7;volume[:,:,2::4]-=5;volume[:,:,3::4]=np.nan
    ds.volume=lambda _:volume
    try:changed=ds.sample(0,4,1)
    finally:ds.volume=original
    for key in ['cond','anchors','teacher_anchors','valid','physical','anchor_z','teacher_query','teacher_interval']:
        assert torch.equal(sample[key],changed[key]),f'Withheld slices leaked into {key}'
    batch=device_batch({k:v[None] for k,v in sample.items() if isinstance(v,torch.Tensor)},torch.device('cuda'))
    teacher=Teacher().cuda();seed_all(3407);blind=Bridge('blind').cuda().eval();seed_all(3407);latent=Bridge('latent').cuda().eval()
    assert all(torch.equal(blind.state_dict()[k],latent.state_dict()[k]) for k in blind.state_dict())
    with torch.no_grad():
        prediction,feature=teacher(batch['teacher_anchors'])
        legacy=teacher.reference.network(batch['teacher_anchors'][:,:,0].permute(0,2,3,1).contiguous()).float().clamp(0,1)
        assert torch.equal(prediction,legacy)
        target=prediction[...,5:8].permute(0,3,1,2).unsqueeze(2)
        assert torch.equal(blind(batch,prediction,feature),target) and torch.equal(latent(batch,prediction,feature),target)
        assert torch.equal(latent(dict(batch,target=torch.full_like(batch['target'],float('nan'))),prediction,feature),target)
        with torch.autocast('cuda',dtype=torch.bfloat16):
            assert torch.equal(latent(batch,prediction,feature),target)
        # Activate the correction to test the actual information path, not zero output.
        latent.readout[-1].weight.normal_(0,.01);blind.load_state_dict(latent.state_dict())
        b1=blind(batch,prediction,feature);b2=blind(batch,prediction,feature+.5)
        l1=latent(batch,prediction,feature);l2=latent(batch,prediction,feature+.5)
        assert torch.equal(b1,b2);effect=float((l1-l2).abs().max());assert effect>1e-6
        assert float((l1-target).abs().max())<=.050001
        batched=interval_batch(ds,0,4,torch.device('cuda'))
        joined=latent(batched,prediction.expand(3,-1,-1,-1),feature.expand(3,-1,-1,-1))
        separate=torch.cat([latent({k:v[j:j+1] for k,v in batched.items()},prediction,feature) for j in range(3)])
        batch_diff=float((joined-separate).abs().max());assert batch_diff<=2e-6
    assert all(p.grad is None and not p.requires_grad for p in teacher.parameters())
    from pastnet_ixi_wavelet.test import i3net_volume
    v=original(0);depth=4*((v.shape[2]-1)//4)+1
    total=np.zeros((256,256,depth),np.float32);count=np.zeros(depth,np.int32)
    with torch.no_grad():
        for start in range(0,depth-12,4):
            anchors=ds.sample(0,start,0)['teacher_anchors'][None].cuda();y,_=teacher(anchors)
            total[:,:,start:start+13]+=y[0].cpu().numpy();count[start:start+13]+=1
        total/=count[None,None,:]
        official=i3net_volume(teacher.reference.network,v)
    overlap_diff=float(np.max(np.abs(total-official)));assert overlap_diff<2e-7
    # Dataset epoch selection and supervision never depend on target intensities.
    train=Windows('train');train.set_epoch(3407001);indices=train.selection.copy();train.set_epoch(3407001);assert np.array_equal(indices,train.selection)
    result=dict(passed=True,initial_parameters_equal=True,initial_prediction_equals_legacy_i3_fp32_and_bf16=True,
        withheld_target_not_used=True,teacher_frozen=True,blind_latent_invariance=True,latent_feature_effect=effect,
        bounded_correction=True,full_volume_i3_overlap_max_error=overlap_diff,patient_splits_match_legacy=True,
        fp32_three_interval_batch_max_error=batch_diff,
        parameters=dict(trainable_bridge=sum(p.numel() for p in latent.parameters()),readout=sum(p.numel() for p in latent.readout.parameters()),
            frozen_i3=sum(p.numel() for p in teacher.parameters())),test_images_opened=False)
    write_json(ROOT/'results/contracts.json',dict(result,code_hashes=hashes()));print(json.dumps(result,indent=2),flush=True)


def tree_equal(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and torch.equal(a,b)
    if isinstance(a,np.ndarray):return isinstance(b,np.ndarray) and np.array_equal(a,b)
    if isinstance(a,dict):return a.keys()==b.keys() and all(tree_equal(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return len(a)==len(b) and all(tree_equal(x,y) for x,y in zip(a,b))
    return a==b


def smoke():
    stamp=sha256(ROOT/'run.py')[:10]+'_'+sha256(ROOT/'execution.json')[:8]
    root=ROOT/'results/smoke_runs'/stamp;root.mkdir(parents=True,exist_ok=True)
    jobs=[('blind',root/'blind',0),('latent',root/'continuous',0),('latent',root/'interrupted',1),('latent',root/'interrupted',0)]
    for variant,out,stop in jobs:
        command=[sys.executable,'-B','-u','-m','ixi_latent_bridge.run','--variant',variant,'--smoke','--out',str(out)]
        if (out/'manifest.json').exists():command.append('--resume')
        if stop:command+=['--stop-after-epoch',str(stop)]
        result=subprocess.run(command)
        if result.returncode:raise RuntimeError(f'Smoke failed: {variant} {out}, exit {result.returncode}')
    a=torch.load(root/'continuous/last.pth',map_location='cpu',weights_only=False)
    b=torch.load(root/'interrupted/last.pth',map_location='cpu',weights_only=False)
    keys=['model','ema','optimizer','epoch','best','wait','best_payload','python_rng','numpy_rng','torch_rng','cuda_rng']
    comparison={k:bool(tree_equal(a[k],b[k])) for k in keys};assert all(comparison.values()),comparison
    result=dict(passed=True,finite_training_both_variants=True,resume_bitwise_equal=comparison,
        continuous_best_sha256=sha256(root/'continuous/best.pth'),resumed_best_sha256=sha256(root/'interrupted/best.pth'),
        smoke_root=str(root),full_started=False,test_used=False,code_hashes=hashes())
    write_json(ROOT/'results/smoke.json',result);print('Both arms and interrupted/resumed smoke passed.',flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--contracts',action='store_true');p.add_argument('--smoke',action='store_true');a=p.parse_args()
    if a.contracts:contracts()
    if a.smoke:smoke()
    if not(a.contracts or a.smoke):
        c=json.loads((ROOT/'results/contracts.json').read_text());s=json.loads((ROOT/'results/smoke.json').read_text())
        assert c['passed'] and s['passed'] and c['code_hashes']==s['code_hashes']==hashes()
        execution=json.loads((ROOT/'execution.json').read_text());memory=json.loads((ROOT/'results'/f'memory_micro{execution["micro_batch"]}_cp{execution["checkpoint_blocks"]}.json').read_text())
        assert memory['passed'] and memory['peak_allocated_gib']<=21.2 and memory['peak_reserved_gib']<=22.5
        assert memory['model_sha256']==sha256(ROOT/'model.py') and memory['trainer_sha256']==sha256(ROOT/'run.py') and memory['dependencies']==hashes()['dependencies']
        write_json(ROOT/'results/checks.json',dict(passed=True,code_hashes=hashes(),contracts_sha256=sha256(ROOT/'results/contracts.json'),
            smoke_sha256=sha256(ROOT/'results/smoke.json'),memory_sha256=sha256(ROOT/'results'/f'memory_micro{execution["micro_batch"]}_cp{execution["checkpoint_blocks"]}.json'),
            execution=execution,full_started=False,test_used=False))
        print('Final frozen full-entry checks passed.',flush=True)


if __name__=='__main__':main()
