"""Official architecture, explicitly local central-interval training contract."""
import argparse
import hashlib
import json
import math
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from pastnet_v2.common import PACKAGE as V2, sha256, write_json
from pastnet_v2.data import IntervalDataset, device_batch
from pastnet_v2.run import seed_all, evaluate, code_hashes as v2_hashes
from .model import Reference, CONFIG

PACKAGE=Path(__file__).resolve().parent
from pastnet_series_integrity.prepare import MANIFEST as DATA
from pastnet_series_integrity.run import code_hashes as repair_hashes
RECIPE=dict(epochs=300,min_epochs=300,patience=40,warmup=15,lr=3e-4,
            final_lr_ratio=.1,initial_lr_ratio=.01,effective_batch_size=16,
            optimizer='Adam',betas=[.9,.999],eps=1e-8,weight_decay=0.,
            loss='central_three_native_L1',ema=False,clip=1.,amp_init_scale=4096.)

def hashes():
    paths=set(PACKAGE.rglob('*.py'))|set((PACKAGE/'reference').glob('*'))
    paths.update([PACKAGE/'PROTOCOL_ZH.md',PACKAGE/'full.ps1'])
    return dict(local={str(p.relative_to(PACKAGE)):sha256(p) for p in sorted(paths) if p.is_file()},v2=v2_hashes(),repair=repair_hashes())

def state_hash(state):
    h=hashlib.sha256()
    for name,tensor in sorted(state.items()):
        h.update(name.encode());h.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()

def learning_rate(epoch,recipe):
    if epoch<recipe['warmup']:
        factor=recipe['initial_lr_ratio']+(1-recipe['initial_lr_ratio'])*epoch/max(1,recipe['warmup']-1)
    else:
        progress=(epoch+1-recipe['warmup'])/max(1,recipe['epochs']-recipe['warmup'])
        factor=recipe['final_lr_ratio']+(1-recipe['final_lr_ratio'])*.5*(1+math.cos(math.pi*progress))
    return recipe['lr']*factor

def finite_metrics(metrics):
    if not all(math.isfinite(float(x)) for x in metrics.values()):
        raise FloatingPointError('Nonfinite validation metric; no silent case exclusion')

def save_atomic(payload,path):
    tmp=path.with_suffix('.tmp.pth');torch.save(payload,tmp);tmp.replace(path)

def train(a):
    seed_all(a.seed)
    if not torch.cuda.is_available():raise RuntimeError('CUDA required for this measured recipe')
    device=torch.device('cuda');recipe=dict(RECIPE)
    if a.smoke:recipe.update(epochs=2)
    if recipe['effective_batch_size']%a.micro_batch:raise ValueError('Microbatch must divide effective batch')
    content=json.loads(DATA.read_text(encoding='utf-8'))
    if content['dataset']!='fastmri':raise ValueError('fastMRI validation only')
    ds=IntervalDataset(DATA,'train',anchors=4,limit=2 if a.smoke else None,sample_limit=16 if a.smoke else None)
    val=IntervalDataset(DATA,'val',anchors=4,limit=1 if a.smoke else None,sample_limit=1 if a.smoke else None)
    if set(r['patient_id'] for r in ds.records)&set(r['patient_id'] for r in val.records):raise ValueError('Patient overlap')
    model=Reference(a.checkpoint_groups).to(device)
    manifest=dict(variant='i3net_repaired',seed=a.seed,smoke=a.smoke,recipe=recipe,model=CONFIG,
        execution=dict(micro_batch=a.micro_batch,checkpoint_groups=a.checkpoint_groups,amp=True,num_workers=0),
        initialization='official random initialization; no pretrained checkpoint; no EMA',
        initial_state_sha256=state_hash(model.state_dict()),data_manifest=str(DATA),data_sha256=sha256(DATA),
        code_hashes=hashes(),train_intervals=len(ds),val_intervals=len(val),test_used=False,
        comparison_limit='PAST control has historical G086 pretraining; not matched initialization or total compute',
        torch=torch.__version__,gpu=torch.cuda.get_device_name(0))
    if a.preflight:
        if not a.smoke:
            checks=json.loads((PACKAGE/'results/checks.json').read_text(encoding='utf-8'))
            if not checks['passed'] or checks['code_hashes']!=hashes():raise ValueError('Checks stale')
        print(json.dumps(manifest,indent=2));return
    if a.out.exists() and not a.resume:raise FileExistsError(a.out)
    if a.stop_after_epoch and not a.smoke:raise ValueError('Interruption test is smoke-only')
    if not a.smoke:
        checks=json.loads((PACKAGE/'results/checks.json').read_text(encoding='utf-8'))
        if not checks['passed'] or checks['code_hashes']!=hashes():raise ValueError('Checks stale')
    optimizer=torch.optim.Adam(model.parameters(),lr=recipe['lr'],betas=tuple(recipe['betas']),eps=recipe['eps'])
    scaler=torch.amp.GradScaler('cuda',init_scale=recipe['amp_init_scale'])
    start=0;best=-math.inf;wait=0;history=[];elapsed=0.
    if a.resume:
        previous=json.loads((a.out/'manifest.json').read_text(encoding='utf-8'))
        if previous!=manifest:raise ValueError('Resume code/data/recipe/execution mismatch')
        if (a.out/'completion.json').exists():
            done=json.loads((a.out/'completion.json').read_text())
            if not done['completed'] or sha256(a.out/'best.pth')!=done['best_sha256']:raise ValueError('Completion mismatch')
            print('Already completed; verified checkpoint and frozen manifest.');return
        saved=torch.load(a.out/'last.pth',map_location='cpu',weights_only=False)
        model.load_state_dict(saved['model']);optimizer.load_state_dict(saved['optimizer']);scaler.load_state_dict(saved['scaler'])
        start,best,wait=saved['epoch'],saved['best'],saved['wait'];history=saved['history']
        elapsed=history[-1]['elapsed_seconds'] if history else 0.
        random.setstate(saved['python_rng']);np.random.set_state(saved['numpy_rng']);torch.set_rng_state(saved['torch_rng'])
        torch.cuda.set_rng_state_all(saved['cuda_rng'])
        del saved
        # last.pth is the epoch commit. Roll back an uncommitted best write.
        if (a.out/'best.pth').exists():
            chk=torch.load(a.out/'best.pth',map_location='cpu',weights_only=False)
            if chk['epoch']>start:
                import shutil
                backup=a.out/'best.previous.pth'
                previous_best=torch.load(backup,map_location='cpu',weights_only=False)
                if previous_best['epoch']>start:raise RuntimeError('Best backup does not match epoch commit')
                shutil.copy2(backup,a.out/'best.pth')
                current={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
                model.load_state_dict(previous_best['model_state_dict'])
                evaluate(model,val,device,a.out/'validation')
                model.load_state_dict(current);del current,previous_best
            del chk
    else:
        a.out.mkdir(parents=True);write_json(a.out/'manifest.json',manifest)
    accumulation=recipe['effective_batch_size']//a.micro_batch
    generator=torch.Generator()
    loader=DataLoader(ds,batch_size=a.micro_batch,shuffle=True,num_workers=0,generator=generator)
    t0=time.perf_counter()
    print(f'I3Net: {len(ds)} train, {len(val)} val; microbatch {a.micro_batch} x {accumulation}; checkpoint {a.checkpoint_groups}/8',flush=True)
    for epoch in range(start,recipe['epochs']):
        if epoch>=recipe['min_epochs'] and wait>=recipe['patience']:break
        generator.manual_seed(a.seed*1000+epoch);model.train();optimizer.zero_grad(set_to_none=True)
        torch.cuda.reset_peak_memory_stats();total=0.;updates=0
        for group in optimizer.param_groups:group['lr']=learning_rate(epoch,recipe)
        for step,batch in enumerate(loader):
            batch=device_batch(batch,device);samples=batch['anchors'].shape[0]
            group_start=(step//accumulation)*accumulation*a.micro_batch
            group_samples=min(recipe['effective_batch_size'],len(ds)-group_start)
            with torch.autocast('cuda'):
                pred=model(batch);loss=torch.nn.functional.l1_loss(pred.float(),batch['target'].float())
            if not torch.isfinite(loss):raise FloatingPointError('Nonfinite loss')
            total+=loss.item()*samples;scaler.scale(loss*samples/group_samples).backward()
            if (step+1)%accumulation==0 or step+1==len(loader):
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(),recipe['clip'],error_if_nonfinite=True)
                scaler.step(optimizer);scaler.update();optimizer.zero_grad(set_to_none=True);updates+=1
        metrics=evaluate(model,val,device);finite_metrics(metrics)
        if metrics['psnr']>best:
            best=float(metrics['psnr']);wait=0
            if (a.out/'best.pth').exists():
                import shutil
                shutil.copy2(a.out/'best.pth',a.out/'best.previous.pth')
            save_atomic(dict(variant='i3net_repaired',epoch=epoch+1,model_state_dict=model.state_dict(),config=CONFIG),a.out/'best.pth')
            persisted=evaluate(model,val,device,a.out/'validation');finite_metrics(persisted)
            if abs(persisted['psnr']-best)>1e-9:raise ValueError('Validation rerun mismatch')
        else:wait+=1
        row=dict(epoch=epoch+1,train_loss=total/len(ds),validation_psnr=metrics['psnr'],best_psnr=best,
            lr=optimizer.param_groups[0]['lr'],updates=updates,elapsed_seconds=elapsed+time.perf_counter()-t0,
            peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30)
        history.append(row)
        save_atomic(dict(model=model.state_dict(),optimizer=optimizer.state_dict(),scaler=scaler.state_dict(),
            epoch=epoch+1,best=best,wait=wait,history=history,python_rng=random.getstate(),numpy_rng=np.random.get_state(),
            torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),a.out/'last.pth')
        pd.DataFrame(history).to_csv(a.out/'history.csv',index=False)
        print(json.dumps(row),flush=True)
        if a.stop_after_epoch and epoch+1==a.stop_after_epoch:
            print('Smoke interrupted at committed epoch, before completion.');return
    completed_epoch=history[-1]['epoch']
    growth=best-history[max(0,len(history)-31)]['best_psnr']
    write_json(a.out/'completion.json',dict(completed=True,smoke=a.smoke,epochs=completed_epoch,
        stopped_early=completed_epoch<recipe['epochs'],best_psnr=best,best_sha256=sha256(a.out/'best.pth'),
        last_sha256=sha256(a.out/'last.pth'),last_30_best_gain_db=growth,
        budget_limited=bool(completed_epoch==recipe['epochs'] and growth>.03),test_used=False))

def main():
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,choices=[3407,2027,9103],default=3407)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--micro-batch',type=int,default=2)
    p.add_argument('--checkpoint-groups',type=int,choices=range(9),default=0)
    p.add_argument('--smoke',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--preflight',action='store_true')
    p.add_argument('--stop-after-epoch',type=int,default=0,help='smoke-only recovery test')
    train(p.parse_args())

if __name__=='__main__':main()
