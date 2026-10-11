import argparse,copy,json,math,random,shutil,time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from pastnet_v2.common import sha256,write_json
from pastnet_v2.run import seed_all,RECIPE as ORIGINAL_RECIPE
from pastnet_v2.losses import objective
from i3net_amp_recovery.run import amp_recovery
from .data import ContextDataset,ROOT,MANIFEST,device_batch
from .model import load_model,INIT,INIT_SHA
from .metrics import evaluate

RECIPE=dict(ORIGINAL_RECIPE,freeze_epochs=3,adapter_lr=1e-4)
CHECKPOINT_BLOCKS=5


def hashes():
    from pastnet_ixi_wavelet.run import hashes as old_hashes
    from pastnet_v2_context.run import code_hashes as context_hashes
    return dict(dependencies=old_hashes(),stc=context_hashes(),
        local={p.name:sha256(p) for p in sorted(list(ROOT.glob('*.py'))+list(ROOT.glob('*.ps1'))+[ROOT/'PROTOCOL_ZH.md'])})


def save_atomic(payload,path):
    tmp=path.with_suffix('.tmp.pth');torch.save(payload,tmp);tmp.replace(path)


def train(a):
    seed_all(a.seed)
    if not torch.cuda.is_available():raise RuntimeError('Measured full requires CUDA')
    device=torch.device('cuda');recipe=dict(RECIPE)
    if a.smoke:recipe.update(epochs=2,freeze_epochs=0)
    if a.stop_after_epoch and not a.smoke:raise ValueError('Interruption probe is smoke-only')
    ds=ContextDataset(MANIFEST,'train',limit=1 if a.smoke else None,sample_limit=16 if a.smoke else None)
    val=ContextDataset(MANIFEST,'val',limit=1 if a.smoke else None,sample_limit=1 if a.smoke else None)
    manifest=dict(variant=a.variant,seed=a.seed,recipe=recipe,smoke=a.smoke,code_hashes=hashes(),init_sha256=sha256(INIT),
        data_manifest=str(MANIFEST),data_sha256=sha256(MANIFEST),train_intervals=len(ds),val_intervals=len(val),
        test_used=False,initialization='same fixed IXI wavelet best plus zero STC projection; not independent scratch training',
        execution=dict(micro_batch=2,effective_batch=16,accumulation=8,checkpoint_blocks=CHECKPOINT_BLOCKS),
        metric='per-target-slice range PSNR/SSIM, both outputs clamp, equal patient mean; normalized MAE/MSE')
    if a.out.exists() and not a.resume:raise FileExistsError('Preserve existing run; use --resume')
    model=load_model(a.variant).cuda();model.base.single.checkpoint_blocks=CHECKPOINT_BLOCKS
    ema=copy.deepcopy(model).eval().requires_grad_(False)
    groups=[]
    for new in (False,True):
        params=[p for n,p in model.named_parameters() if n.startswith('trajectory_adapter.')==new]
        lr=recipe['adapter_lr'] if new else recipe['lr']
        groups.append(dict(params=params,lr=lr,initial_lr=lr))
    optimizer=torch.optim.AdamW(groups,weight_decay=recipe['weight_decay'],betas=recipe['betas'])
    scaler=torch.amp.GradScaler('cuda',init_scale=recipe['amp_init_scale'])
    start,best,wait,history=0,-math.inf,0,[]
    def commit(epoch):
        save_atomic(dict(model=model.state_dict(),ema=ema.state_dict(),optimizer=optimizer.state_dict(),scaler=scaler.state_dict(),
            epoch=epoch,best=best,wait=wait,history=history,best_payload=best_payload,best_sha256=sha256(a.out/'best.pth'),
            python_rng=random.getstate(),numpy_rng=np.random.get_state(),torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),a.out/'last.pth')
        if history:pd.DataFrame(history).to_csv(a.out/'history.csv',index=False)
    if a.resume:
        previous=json.loads((a.out/'manifest.json').read_text());assert previous==manifest,'Frozen manifest changed'
        if (a.out/'completion.json').exists():
            done=json.loads((a.out/'completion.json').read_text());assert done['completed'] and done['best_sha256']==sha256(a.out/'best.pth')
            print('Already completed; code/data/recipe/checkpoint verified.',flush=True);return
        saved=torch.load(a.out/'last.pth',map_location='cpu',weights_only=False)
        model.load_state_dict(saved['model']);ema.load_state_dict(saved['ema']);optimizer.load_state_dict(saved['optimizer']);scaler.load_state_dict(saved['scaler'])
        start,best,wait,history=saved['epoch'],saved['best'],saved['wait'],saved['history'];best_payload=saved['best_payload']
        if not (a.out/'best.pth').exists() or sha256(a.out/'best.pth')!=saved['best_sha256']:
            print('Restoring best to the committed epoch; discarding uncommitted writes.',flush=True)
            save_atomic(best_payload,a.out/'best.pth');rollback=load_model(a.variant,a.out/'best.pth').cuda()
            evaluate(rollback,val,device,a.out/'validation');del rollback
        if history:pd.DataFrame(history).to_csv(a.out/'history.csv',index=False)
        random.setstate(saved['python_rng']);np.random.set_state(saved['numpy_rng']);torch.set_rng_state(saved['torch_rng']);torch.cuda.set_rng_state_all(saved['cuda_rng']);del saved
    else:
        a.out.mkdir(parents=True);write_json(a.out/'manifest.json',manifest)
        print(f'{a.variant}: measuring fixed initialization on {len(val)} validation intervals...',flush=True)
        anchor=evaluate(ema,val,device,a.out/'initial_validation');best=anchor['psnr']
        best_payload=dict(variant=a.variant,model_state_dict={k:v.detach().cpu().clone() for k,v in ema.state_dict().items()},epoch=0)
        save_atomic(best_payload,a.out/'best.pth');shutil.copytree(a.out/'initial_validation',a.out/'validation');commit(0)
    generator=torch.Generator();loader=DataLoader(ds,batch_size=2,shuffle=True,num_workers=0,generator=generator)
    elapsed=history[-1]['elapsed_seconds'] if history else 0.;t0=time.perf_counter()
    print(f'{a.variant}: microbatch2 x accumulation8, {CHECKPOINT_BLOCKS}/10 checkpoint blocks',flush=True)
    for epoch in range(start,recipe['epochs']):
        if epoch>=recipe['min_epochs'] and wait>=recipe['patience']:break
        generator.manual_seed(a.seed*1000+epoch);ds.set_epoch(a.seed*1000+epoch)
        for name,param in model.named_parameters():param.requires_grad_(name.startswith('trajectory_adapter.') or epoch>=recipe['freeze_epochs'])
        model.train();optimizer.zero_grad(set_to_none=True);total=0.;attempts=0;applied=0;torch.cuda.reset_peak_memory_stats()
        progress=max(0.,(epoch+1-recipe['warmup'])/max(1,recipe['epochs']-recipe['warmup']))
        factor=min(1.,(epoch+1)/recipe['warmup'])*(.05+.95*.5*(1+math.cos(math.pi*progress)))
        for group in optimizer.param_groups:group['lr']=group['initial_lr']*factor
        for step,batch in enumerate(loader):
            data=device_batch(batch,device);samples=data['cond'].shape[0]
            group_start=(step//8)*8*2;group_samples=min(16,len(ds)-group_start)
            with torch.autocast('cuda'):loss,parts=objective(model,data,epoch+1,recipe['epochs'])
            if not torch.isfinite(loss):raise FloatingPointError('Nonfinite loss')
            total+=parts['loss']*samples;scaler.scale(loss*samples/group_samples).backward()
            if (step+1)%8==0 or step+1==len(loader):
                scaler.unscale_(optimizer);torch.nn.utils.clip_grad_norm_(model.parameters(),recipe['clip'],error_if_nonfinite=True)
                old_scale=scaler.get_scale();scaler.step(optimizer);scaler.update();optimizer.zero_grad(set_to_none=True);attempts+=1
                if scaler.get_scale()>=old_scale:
                    applied+=1
                    with torch.no_grad():
                        state=model.state_dict()
                        for name,value in ema.state_dict().items():value.lerp_(state[name],1-recipe['ema'])
            if not a.smoke and (step+1)%500==0:print(f'{a.variant} epoch{epoch+1}: {step+1}/{len(loader)} microbatches',flush=True)
        metrics=evaluate(ema,val,device)
        if metrics['psnr']>best:
            best=metrics['psnr'];wait=0
            best_payload=dict(variant=a.variant,model_state_dict={k:v.detach().cpu().clone() for k,v in ema.state_dict().items()},epoch=epoch+1)
            save_atomic(best_payload,a.out/'best.pth');evaluate(ema,val,device,a.out/'validation')
        else:wait+=1
        history.append(dict(epoch=epoch+1,train_loss=total/len(ds),validation_psnr=metrics['psnr'],best_psnr=best,attempts=attempts,applied=applied,
            elapsed_seconds=elapsed+time.perf_counter()-t0,peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30))
        commit(epoch+1);print(json.dumps(history[-1]),flush=True)
        if a.stop_after_epoch==epoch+1:print('Committed smoke interruption.',flush=True);return
    completed=history[-1]['epoch'] if history else start
    write_json(a.out/'completion.json',dict(completed=True,smoke=a.smoke,epochs=completed,best_psnr=best,best_sha256=sha256(a.out/'best.pth'),
        last_sha256=sha256(a.out/'last.pth'),test_used=False,stopped_early=completed<recipe['epochs']))


def main():
    p=argparse.ArgumentParser();p.add_argument('--variant',choices=['local','extended'],required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seed',type=int,choices=[3407,2027,9103],default=3407);p.add_argument('--smoke',action='store_true');p.add_argument('--resume',action='store_true')
    p.add_argument('--preflight',action='store_true');p.add_argument('--stop-after-epoch',type=int,default=0);a=p.parse_args()
    assert sha256(INIT)==INIT_SHA
    if not a.smoke:
        c=json.loads((ROOT/'results/checks.json').read_text());assert c['passed'] and c['code_hashes']==hashes(),'Checks stale'
    if a.preflight:
        write_json(ROOT/'results'/f'preflight_{a.variant}.json',dict(passed=True,code_hashes=hashes(),recipe=RECIPE,init_sha256=INIT_SHA,full_started=False));return
    log=ROOT/'results'/f'amp_{a.variant}_{time.strftime("%Y%m%d_%H%M%S")}.jsonl';log.parent.mkdir(exist_ok=True)
    with amp_recovery(log):train(a)


if __name__=='__main__':main()
