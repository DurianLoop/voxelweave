import argparse,copy,json,math,random,time,shutil
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from pastnet_v2.common import sha256,write_json
from pastnet_v2.run import seed_all,evaluate,is_new,RECIPE as ORIGINAL_RECIPE
from pastnet_v2.losses import objective
from pastnet_wavelet_trunk.run import load_model as wavelet_load,code_hashes as wavelet_hashes
from i3net_amp_recovery.run import amp_recovery
from .data import IXIDataset as IntervalDataset,device_batch,ROOT,MANIFEST
INIT=ROOT.parent/'pastnet_wavelet_trunk/runs/full_wavelet3_seed3407_vram20/best.pth'
RECIPE=dict(ORIGINAL_RECIPE,freeze_epochs=0,adapter_lr=2e-5)
VARIANTS={'wavelet3':(False,False,False,False,4)}
def load_model(variant,checkpoint=None):return wavelet_load(variant,checkpoint or INIT)
def hashes():
    from i3net_amp_recovery.run import hashes as recovery_hashes
    from i3net_strict_reference.run import hashes as reference_hashes
    return dict(wavelet=wavelet_hashes(),amp_recovery=recovery_hashes(),i3net=reference_hashes(),
        local={p.name:sha256(p) for p in sorted(list(ROOT.glob('*.py'))+list(ROOT.glob('*.ps1'))+[ROOT/'PROTOCOL_ZH.md',MANIFEST])})
def train(a):
    recipe=dict(RECIPE)
    if a.smoke:
        recipe.update(epochs=1,freeze_epochs=0)
    micro_batch=a.micro_batch_size
    if recipe['effective_batch_size']%micro_batch:
        raise ValueError('Micro batch must divide effective batch size')
    accumulation_steps=recipe['effective_batch_size']//micro_batch
    checkpoint_blocks=a.checkpoint_blocks if a.checkpoint_blocks is not None else (5 if a.variant in ('control','geometry') else 10)
    execution=dict(micro_batch_size=micro_batch,accumulation_steps=accumulation_steps,
                   checkpoint_blocks=checkpoint_blocks,target_allocated_gib=20)
    content=json.loads(a.manifest.read_text(encoding='utf-8'))
    if content['dataset']!='ixi':raise ValueError('IXI only')
    out=a.out
    if out.exists() and not a.resume:
        raise FileExistsError(f'Use --resume or a unique directory: {out}')
    seed_all(a.seed)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    anchors=VARIANTS[a.variant][-1]
    ds=IntervalDataset(a.manifest,'train',anchors=anchors,limit=1 if a.smoke else None,
                       sample_limit=16 if a.smoke else None)
    val=IntervalDataset(a.manifest,'val',anchors=anchors,limit=1 if a.smoke else None,
                        sample_limit=1 if a.smoke else None)
    manifest=dict(variant=a.variant,seed=a.seed,recipe=recipe,execution=execution,smoke=a.smoke,
        dataset=content['dataset'],fold=content['fold'],data_manifest=str(a.manifest.resolve()),
        data_sha256=sha256(a.manifest),init_sha256=sha256(INIT),code_hashes=hashes(),
        train_intervals=len(ds),val_intervals=len(val),test_selected=False,
        seed_scope='IXI fine-tuning from fixed fastMRI wavelet3 best; not scratch training',
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
        # Measure the fixed fastMRI wavelet initialization on IXI validation.
        baseline=evaluate(ema,val,device,out/'initial_validation')
        best=baseline['psnr']
        torch.save(dict(variant=a.variant,model_state_dict=ema.state_dict(),epoch=0),out/'best.pth')
        shutil.copytree(out/'initial_validation',out/'validation')
    sampling_generator=torch.Generator()
    loader=DataLoader(ds,batch_size=micro_batch,shuffle=True,num_workers=0,generator=sampling_generator)
    print(f'GPU execution: micro_batch={micro_batch}, accumulation={accumulation_steps}, '
          f'effective_batch={recipe["effective_batch_size"]}, checkpoint_blocks={checkpoint_blocks}/10',flush=True)
    previous_elapsed=history[-1]['elapsed_seconds'] if history else 0.
    t0=time.perf_counter()
    epoch=start-1
    if start and (out/'completion.json').exists():
        c=json.loads((out/'completion.json').read_text());assert c['completed'] and c['best_sha256']==sha256(out/'best.pth');return
    for epoch in range(start,recipe['epochs']):
        sampling_generator.manual_seed(a.seed*1000+epoch)
        ds.set_epoch(a.seed*1000+epoch)
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
                            best_psnr=best,elapsed_seconds=previous_elapsed+time.perf_counter()-t0,
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
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=int,default=3407,choices=[3407,2027,9103])
    p.add_argument('--smoke',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--preflight',action='store_true')
    a=p.parse_args();a.manifest=MANIFEST;a.variant='wavelet3';a.micro_batch_size=2;a.checkpoint_blocks=5;a.lock=None;a.gate=None
    if a.preflight:
        c=json.loads((ROOT/'results/checks.json').read_text());assert c['passed'] and c['code_hashes']==hashes()
        assert c['init_sha256']==sha256(INIT)
        write_json(ROOT/'results/preflight.json',dict(passed=True,recipe=RECIPE,init_sha256=sha256(INIT),code_hashes=hashes(),full_started=False));return
    if not a.smoke:
        c=json.loads((ROOT/'results/checks.json').read_text());assert c['passed'] and c['code_hashes']==hashes()
        assert c['init_sha256']==sha256(INIT)
    log=ROOT/'results'/('amp_'+time.strftime('%Y%m%d_%H%M%S')+'.jsonl');log.parent.mkdir(exist_ok=True)
    with amp_recovery(log):train(a)
if __name__=='__main__':main()
