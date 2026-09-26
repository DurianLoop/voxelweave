import json
import numpy as np
import nibabel as nib
import torch
from torch.utils.data import DataLoader,Subset
from skimage.transform import resize
from pastnet_v2.common import PACKAGE,sha256,write_json
from pastnet_v2.data import IntervalDataset,device_batch
from pastnet_v2.run import seed_all,load_model as old_load
from pastnet_v2.losses import objective
from .audit import ROOT,SOURCE
from .prepare import MANIFEST,validation_hash
from .run import load_model,code_hashes

def main():
    original=json.loads(SOURCE.read_text(encoding='utf-8'));fixed=json.loads(MANIFEST.read_text(encoding='utf-8'))
    mapping=json.loads((ROOT/'results/repair_mapping.json').read_text())
    headers=json.loads((ROOT/'results/header_audit.json').read_text())
    assert headers['mixed_cases']==[mapping['case_id']] and len(headers['records'])==135
    assert sha256(mapping['original_nifti'])==mapping['original_sha256']
    assert fixed['training_repair']['original_manifest_sha256']==sha256(SOURCE)
    assert fixed['training_repair']['repair_mapping_sha256']==sha256(ROOT/'results/repair_mapping.json')
    other=[r for r in original['records'] if r['case_id']!=mapping['case_id']]
    assert fixed['records'][:len(other)]==other and validation_hash(original)==validation_hash(fixed)
    for split in ('train','val'):
        assert {r['patient_id'] for r in original['records'] if r['split']==split}=={r['patient_id'] for r in fixed['records'] if r['split']==split}
    train=IntervalDataset(MANIFEST,'train',anchors=4);val=IntervalDataset(MANIFEST,'val',anchors=4)
    assert len(train)==1356 and len(val)==69 and len(train.records)==113
    assert not ({r['patient_id'] for r in train.records}&{r['patient_id'] for r in val.records})
    raw=nib.load(mapping['original_nifti']).get_fdata(dtype=np.float32)
    for group,rec in zip(mapping['groups'],fixed['records'][-2:]):
        volume=nib.load(rec['path']).get_fdata(dtype=np.float32)
        assert np.array_equal(volume,raw[:,:,[r['old_index'] for r in group['slices']]])
        assert sha256(rec['path'])==fixed['training_repair']['data_hashes'][str(__import__('pathlib').Path('data')/__import__('pathlib').Path(rec['path']).name)]
        z=np.array(rec['geometry']['z_mm']);assert np.all(np.diff(z)>0)
        for start in range(12):
            phase=(z[start+np.array([1,2,3])]-z[start])/(z[start+4]-z[start])
            assert np.allclose(phase,[.25,.5,.75],atol=1e-6)
        # Check all simulated sparse grids normalize from observed slices only.
        for start in range(4):
            idx=next(j for j,(i,z) in enumerate(train.items) if train.records[i]['case_id']==rec['case_id'] and z==start)
            sample=train[idx];obs=volume[:,:,start%4::4];lo,hi=obs.min(),obs.max()
            norm=resize((volume-lo)/max(float(hi-lo),1e-8),(256,256,16),anti_aliasing=True,preserve_range=True).astype(np.float32)
            expected=np.stack([norm[:,:,start+j][None] for j in (1,2,3)])
            assert np.array_equal(sample['target'].numpy(),expected)
            clipped=[min(max(start+d,start%4),(15-start%4)//4*4+start%4) for d in (-4,0,4,8)]
            assert np.array_equal(sample['anchors'].numpy(),np.stack([norm[:,:,j][None] for j in clipped]))
    seed_all(3407)
    ids=[j for j,(i,z) in enumerate(train.items) if train.records[i]['case_id'].startswith(mapping['case_id']+'_uid_') and z==4]
    assert len(ids)==2
    batch=device_batch(next(iter(DataLoader(Subset(train,ids),batch_size=2))),torch.device('cuda'))
    model=load_model('repair').cuda().eval();control=old_load('control').cuda().eval()
    with torch.no_grad(),torch.autocast('cuda'):assert torch.equal(model(batch),control(batch))
    del control;torch.cuda.empty_cache();model.train();model.base.single.checkpoint_blocks=5
    optimizer=torch.optim.AdamW(model.parameters(),lr=2e-5,weight_decay=2e-5,betas=(.9,.99))
    scaler=torch.amp.GradScaler('cuda',init_scale=4096.);torch.cuda.reset_peak_memory_stats();losses=[]
    for step in range(3):
        optimizer.zero_grad(set_to_none=True)
        with torch.autocast('cuda'):loss,_=objective(model,batch,4,80,False)
        scaler.scale(loss).backward();scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True);scaler.step(optimizer);scaler.update()
        losses.append(loss.item())
    result=dict(passed=True,all_32_raw_slices_match=True,only_one_training_record_replaced=True,
        unchanged_other_records=True,validation_sha256=validation_hash(fixed),patients_unchanged=True,
        train_series=113,train_patients=111,train_intervals=1356,val_intervals=69,phase_and_uid_verified=True,
        observed_only_normalization_verified=True,initial_model_bitwise_equal=True,repaired_batch_finite_updates=losses,
        peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
        code_hashes=code_hashes())
    write_json(ROOT/'results/checks.json',result);print(json.dumps({k:v for k,v in result.items() if k!='code_hashes'},indent=2))
if __name__=='__main__':main()
