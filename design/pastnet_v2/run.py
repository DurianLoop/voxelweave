"""Explicit train / validation / locked external evaluation. Never run_all(test)."""
from __future__ import annotations

import argparse
import copy
import json
import math
import random
import time
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from .common import G086, PACKAGE, sha256, write_json
from .data import IntervalDataset, device_batch
from .losses import objective
from .metrics import quality
from .model import PASTNetV2, VARIANTS

SEEDS=(3407,2027,9103)
RECIPE=dict(epochs=80,patience=15,min_epochs=30,lr=2e-5,adapter_lr=1e-4,
            weight_decay=2e-5,betas=[.9,.99],warmup=5,ema=.999,effective_batch_size=16,
            freeze_epochs=3,clip=1.,image_size=256,amp_init_scale=4096.)


def code_hashes():
    return {str(p.relative_to(PACKAGE)):sha256(p) for p in sorted(PACKAGE.rglob('*.py'))}


def seed_all(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.set_num_threads(4)
    torch.backends.cudnn.benchmark=False
    torch.use_deterministic_algorithms(True,warn_only=True)


def load_model(variant,checkpoint=None):
    model=PASTNetV2(variant)
    payload=torch.load(checkpoint or G086,map_location='cpu',weights_only=False)
    if 'variant' in payload:
        if payload['variant']!=variant:
            raise ValueError('Wrong variant checkpoint')
        model.load_state_dict(payload['model_state_dict'],strict=True)
    else:
        model.load_g086(payload)
    return model


@torch.no_grad()
def evaluate(model,dataset,device,out=None,amp=True):
    model.eval(); rows=[]
    for batch in DataLoader(dataset,batch_size=1,shuffle=False):
        data=device_batch(batch,device)
        with torch.autocast(device.type,enabled=amp and device.type=='cuda'):
            pred=model(data).float()[0,:,0].cpu().numpy()
        target=batch['target'][0,:,0].numpy()
        for j in range(3):
            spacing=np.exp2(batch['physical'][0,j,:2].numpy())
            rows.append(dict(case_id=batch['case_id'][0],patient_id=batch['patient_id'][0],
                             z=int(batch['z'][0])+j+1,phase=(j+1)/4,
                             **quality(pred[j],target[j],spacing)))
    df=pd.DataFrame(rows)
    cols=list(quality(np.zeros((8,8)),np.zeros((8,8))))
    case=df.groupby(['patient_id','case_id'])[cols].mean().reset_index()
    patient=case.groupby('patient_id')[cols].mean().reset_index()
    if out is not None:
        out=Path(out); out.mkdir(parents=True,exist_ok=True)
        df.to_csv(out/'per_slice.csv',index=False)
        case.to_csv(out/'per_case.csv',index=False)
        patient.to_csv(out/'per_patient.csv',index=False)
        write_json(out/'summary.json',dict(patient[cols].mean()))
        write_json(out/'metric_contract.json',dict(split=dataset.records[0]['split'],
            normalization='observed_sparse_minmax',range=1,clamp=False,
            aggregation='mean slice within series, mean series within patient, equal patient mean',
            included='missing slices only; grid starts at 0; terminal incomplete interval excluded',
            dice_hd95='intensity > 0.1 proxy only, not anatomical segmentation',
            hd95_units='mm when spacing_known, otherwise resized pixel units; inspect geometry mask'))
    return dict(patient[cols].mean())


def is_new(name):
    return 'adapter' in name or name.startswith('frequency_decoder.')


def check_lock(path,variant):
    lock=json.loads(Path(path).read_text(encoding='utf-8'))
    if variant not in (lock['variant'],'control') or lock['recipe']!=RECIPE or lock['code_hashes']!=code_hashes():
        raise ValueError('Lock does not match code / variant / recipe')
    for run,h in {**lock['validation_runs'],**lock['control_runs']}.items():
        if sha256(Path(run)/'best.pth')!=h:
            raise ValueError('Locked validation checkpoint changed')
    return lock


def train(a):
    recipe=dict(RECIPE)
    if a.smoke:
        recipe.update(epochs=1,effective_batch_size=2,freeze_epochs=0)
    micro_batch=a.micro_batch_size
    if recipe['effective_batch_size']%micro_batch:
        raise ValueError('Micro batch must divide effective batch size')
    accumulation_steps=recipe['effective_batch_size']//micro_batch
    checkpoint_blocks=a.checkpoint_blocks if a.checkpoint_blocks is not None else (5 if a.variant in ('control','geometry') else 10)
    execution=dict(micro_batch_size=micro_batch,accumulation_steps=accumulation_steps,
                   checkpoint_blocks=checkpoint_blocks,target_allocated_gib=20)
    content=json.loads(a.manifest.read_text(encoding='utf-8'))
    if content['dataset']!='fastmri' and not a.lock:
        raise ValueError('External training requires a locked fastMRI candidate')
    if a.lock:
        check_lock(a.lock,a.variant)
    elif not a.smoke and list(VARIANTS).index(a.variant)>1:
        if not a.gate:
            raise ValueError('This full stage requires --gate from the promoted preceding single-variable experiment')
        gate=json.loads(a.gate.read_text(encoding='utf-8'))
        expected=list(VARIANTS)[list(VARIANTS).index(a.variant)-1]
        if not gate['promoted'] or gate['variant']!=expected or gate.get('stage')!='gate':
            raise ValueError('Preceding variable did not pass its preregistered gate')
        for run,h in gate['candidate_runs'].items():
            if sha256(Path(run)/'best.pth')!=h:
                raise ValueError('Gate evidence changed')
    out=a.out
    if out.exists() and not a.resume:
        raise FileExistsError(f'Use --resume or a unique directory: {out}')
    seed_all(a.seed)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    anchors=VARIANTS[a.variant][-1]
    ds=IntervalDataset(a.manifest,'train',anchors=anchors,limit=1 if a.smoke else None,
                       sample_limit=2 if a.smoke else None)
    val=IntervalDataset(a.manifest,'val',anchors=anchors,limit=1 if a.smoke else None,
                        sample_limit=1 if a.smoke else None)
    manifest=dict(variant=a.variant,seed=a.seed,recipe=recipe,execution=execution,smoke=a.smoke,
        dataset=content['dataset'],fold=content['fold'],data_manifest=str(a.manifest.resolve()),
        data_sha256=sha256(a.manifest),init_sha256=sha256(G086),code_hashes=code_hashes(),
        train_intervals=len(ds),val_intervals=len(val),test_selected=False,
        seed_scope='independent v2 optimization from the same historical G086; not independent v1 pretraining',
        lock_sha256=sha256(a.lock) if a.lock else None,
        gate_sha256=sha256(a.gate) if a.gate else None,
        sampler='dedicated generator seeded by seed*1000+epoch; identical across architectures')
    model=load_model(a.variant).to(device)
    model.base.single.checkpoint_blocks=checkpoint_blocks
    ema=copy.deepcopy(model).eval().requires_grad_(False)
    groups=[]
    for new in (False,True):
        params=[p for n,p in model.named_parameters() if is_new(n)==new]
        if params:
            lr=recipe['adapter_lr'] if new else recipe['lr']
            groups.append(dict(params=params,lr=lr,initial_lr=lr))
    optimizer=torch.optim.AdamW(groups,weight_decay=recipe['weight_decay'],betas=recipe['betas'])
    scaler=torch.amp.GradScaler(device.type,enabled=device.type=='cuda',init_scale=recipe['amp_init_scale'])
    start,best,wait=0,-math.inf,0
    history=[]
    if a.resume:
        previous=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
        if previous!=manifest:
            raise ValueError('Resume manifest differs; no silent recipe/code/data changes')
        saved=torch.load(out/'last.pth',map_location='cpu',weights_only=False)
        model.load_state_dict(saved['model']); ema.load_state_dict(saved['ema'])
        optimizer.load_state_dict(saved['optimizer']); scaler.load_state_dict(saved['scaler'])
        start,best,wait=saved['epoch'],saved['best'],saved['wait']
        random.setstate(saved['python_rng']); np.random.set_state(saved['numpy_rng'])
        torch.set_rng_state(saved['torch_rng'])
        if device.type=='cuda':
            torch.cuda.set_rng_state_all(saved['cuda_rng'])
        history=pd.read_csv(out/'history.csv').to_dict('records')
    else:
        out.mkdir(parents=True)
        write_json(out/'manifest.json',manifest)
        # Frozen G086 with corrected input policy is a measured anchor, not an
        # optimizer continuation offered as the new research model.
        baseline=evaluate(ema,val,device,out/'initial_validation')
        best=baseline['psnr']
        torch.save(dict(variant=a.variant,model_state_dict=ema.state_dict(),epoch=0),out/'best.pth')
        shutil.copytree(out/'initial_validation',out/'validation')
    sampling_generator=torch.Generator()
    loader=DataLoader(ds,batch_size=micro_batch,shuffle=True,num_workers=0,generator=sampling_generator)
    print(f'GPU execution: micro_batch={micro_batch}, accumulation={accumulation_steps}, '
          f'effective_batch={recipe["effective_batch_size"]}, checkpoint_blocks={checkpoint_blocks}/10',flush=True)
    t0=time.perf_counter()
    epoch=start-1
    for epoch in range(start,recipe['epochs']):
        sampling_generator.manual_seed(a.seed*1000+epoch)
        if device.type=='cuda':
            torch.cuda.reset_peak_memory_stats()
        for name,param in model.named_parameters():
            param.requires_grad_(is_new(name) or epoch>=recipe['freeze_epochs'])
        model.train(); total=0.; optimizer.zero_grad(set_to_none=True)
        progress=max(0.,(epoch+1-recipe['warmup'])/max(1,recipe['epochs']-recipe['warmup']))
        factor=min(1.,(epoch+1)/recipe['warmup'])*(.05+.95*.5*(1+math.cos(math.pi*progress)))
        for group in optimizer.param_groups:
            group['lr']=group['initial_lr']*factor
        for step,batch in enumerate(loader):
            batch=device_batch(batch,device)
            group_start=(step//accumulation_steps)*accumulation_steps*micro_batch
            group_samples=min(recipe['effective_batch_size'],len(ds)-group_start)
            samples=batch['cond'].shape[0]
            with torch.autocast(device.type,enabled=device.type=='cuda'):
                loss,parts=objective(model,batch,epoch+1,recipe['epochs'],VARIANTS[a.variant][3])
            if not torch.isfinite(loss):
                raise FloatingPointError('Non-finite loss')
            total+=parts['loss']*samples
            if loss.requires_grad:
                scaler.scale(loss*samples/group_samples).backward()
                if (step+1)%accumulation_steps==0 or step+1==len(loader):
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(),recipe['clip'],error_if_nonfinite=True)
                    old_scale=scaler.get_scale()
                    scaler.step(optimizer); scaler.update(); optimizer.zero_grad(set_to_none=True)
                    if scaler.get_scale()>=old_scale:
                        with torch.no_grad():
                            state=model.state_dict()
                            for name,value in ema.state_dict().items():
                                value.lerp_(state[name],1-recipe['ema'])
        metrics=evaluate(ema,val,device)
        improved=metrics['psnr']>best
        if improved:
            best=metrics['psnr']; wait=0
            torch.save(dict(variant=a.variant,model_state_dict=ema.state_dict(),epoch=epoch+1),out/'best.pth')
            evaluate(ema,val,device,out/'validation')
        else:
            wait+=1
        history.append(dict(epoch=epoch+1,train_loss=total/len(ds),validation_psnr=metrics['psnr'],
                            best_psnr=best,elapsed_seconds=time.perf_counter()-t0,
                            peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30 if device.type=='cuda' else 0.,
                            peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30 if device.type=='cuda' else 0.))
        pd.DataFrame(history).to_csv(out/'history.csv',index=False)
        payload=dict(model=model.state_dict(),ema=ema.state_dict(),optimizer=optimizer.state_dict(),
                     scaler=scaler.state_dict(),epoch=epoch+1,best=best,wait=wait,
                     python_rng=random.getstate(),numpy_rng=np.random.get_state(),torch_rng=torch.get_rng_state(),
                     cuda_rng=torch.cuda.get_rng_state_all() if device.type=='cuda' else [])
        torch.save(payload,out/'last.tmp.pth'); (out/'last.tmp.pth').replace(out/'last.pth')
        print(f'epoch={epoch+1} loss={total/len(ds):.6f} val_psnr={metrics["psnr"]:.5f} best={best:.5f} '
              f'peak_allocated={history[-1]["peak_allocated_gib"]:.2f} GiB '
              f'peak_reserved={history[-1]["peak_reserved_gib"]:.2f} GiB',flush=True)
        if epoch+1>=recipe['min_epochs'] and wait>=recipe['patience']:
            break
    write_json(out/'completion.json',dict(smoke=a.smoke,epochs=epoch+1,best_psnr=best,
        completed=True,stopped_early=epoch+1<recipe['epochs'],test_used=False,best_sha256=sha256(out/'best.pth')))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=['train','evaluate'])
    p.add_argument('--manifest',type=Path,default=PACKAGE/'manifests/fastmri/fold_00.json')
    p.add_argument('--variant',choices=list(VARIANTS),default='correspondence')
    p.add_argument('--seed',type=int,choices=SEEDS,default=3407)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--checkpoint',type=Path)
    p.add_argument('--lock',type=Path)
    p.add_argument('--gate',type=Path)
    p.add_argument('--split',choices=['val','test'],default='val')
    p.add_argument('--smoke',action='store_true')
    p.add_argument('--resume',action='store_true')
    p.add_argument('--micro-batch-size',type=int,choices=[1,2,4,8,16],default=2)
    p.add_argument('--checkpoint-blocks',type=int,choices=range(11))
    a=p.parse_args()
    if a.action=='train':
        train(a); return
    content=json.loads(a.manifest.read_text(encoding='utf-8'))
    if content['dataset']!='fastmri':
        if not a.lock:
            raise ValueError('External validation/test metrics require the locked candidate protocol')
        check_lock(a.lock,a.variant)
    if a.split=='test':
        if content['dataset']=='fastmri':
            raise ValueError('fastMRI development test is deliberately unavailable for v2 selection')
        if not a.lock or not a.checkpoint:
            raise ValueError('External test requires lock and trained checkpoint')
        check_lock(a.lock,a.variant)
        run_manifest=json.loads((a.checkpoint.parent/'manifest.json').read_text(encoding='utf-8'))
        completion=json.loads((a.checkpoint.parent/'completion.json').read_text(encoding='utf-8'))
        if run_manifest['smoke'] or not completion['completed'] or run_manifest['data_sha256']!=sha256(a.manifest):
            raise ValueError('Invalid external checkpoint provenance')
        if run_manifest.get('lock_sha256')!=sha256(a.lock) or run_manifest['variant']!=a.variant:
            raise ValueError('External run was not trained under this lock')
        if run_manifest['code_hashes']!=code_hashes() or run_manifest['recipe']!=RECIPE:
            raise ValueError('External run code / recipe mismatch')
        if completion['best_sha256']!=sha256(a.checkpoint):
            raise ValueError('External checkpoint changed after completion')
        if a.checkpoint.name!='best.pth':
            raise ValueError('External test uses validation-selected best.pth only')
    if a.out.exists():
        raise FileExistsError(a.out)
    seed_all(a.seed)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model=load_model(a.variant,a.checkpoint).to(device)
    ds=IntervalDataset(a.manifest,a.split,anchors=VARIANTS[a.variant][-1],
        allow_locked_test=a.split=='test',limit=1 if a.smoke else None,sample_limit=1 if a.smoke else None)
    result=evaluate(model,ds,device,a.out)
    write_json(a.out/'evaluation_manifest.json',dict(split=a.split,dataset=content['dataset'],fold=content['fold'],
        seed=run_manifest['seed'] if a.split=='test' else a.seed,variant=a.variant,
        smoke=a.smoke,checkpoint_sha256=sha256(a.checkpoint or G086),data_sha256=sha256(a.manifest),
        lock_sha256=sha256(a.lock) if a.lock else None))
    print(result)


if __name__=='__main__':
    main()
