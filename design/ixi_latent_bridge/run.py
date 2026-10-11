import argparse,copy,hashlib,json,math,random,shutil,subprocess,time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from pastnet_v2.common import sha256,write_json
from pastnet_v2.run import seed_all
from .model import ROOT,Bridge,Teacher,I3,PAST,I3_SHA,PAST_SHA
from .data import Windows,MANIFEST,device_batch
from .metrics import evaluate

RECIPE=dict(epochs=80,min_epochs=30,patience=15,freeze_epochs=3,lr=2e-5,adapter_lr=1e-4,
    weight_decay=2e-5,betas=[.9,.99],warmup=5,ema=.999,clip=1.,effective_batch=16,
    loss='mean squared error + .05 Charbonnier, three missing queries; no output clamp in train',
    train_precision='BF16 autocast, FP32 loss; no GradScaler',validation_precision='FP32')


def hashes():
    local=[p for g in ('*.py','*.ps1','*.cmd') for p in ROOT.glob(g)]
    local.extend(p for p in [ROOT/'PROTOCOL_ZH.md',ROOT/'execution.json'] if p.exists())
    design=ROOT.parent;dependencies=[]
    for directory in ['pastnet_v2','i3net_strict_reference/vendor']:
        dependencies.extend((design/directory).rglob('*.py'))
    dependencies.extend(design/p for p in ['i3net_strict_reference/model.py','pastnet_wavelet_trunk/model.py',
        'pastnet_ixi_wavelet/data.py','pastnet_ixi_context/metrics.py','pastnet_ixi_context/data.py'])
    return dict(local={p.name:sha256(p) for p in sorted(local)},
        dependencies={str(p.relative_to(design)):sha256(p) for p in sorted(set(dependencies))})


def validate_sources():
    assert sha256(I3)==I3_SHA and sha256(PAST)==PAST_SHA,'Fixed prior changed'
    content=json.loads(MANIFEST.read_text());groups={s:{x['patient_id'] for x in content['records'] if x['split']==s} for s in ['train','val','test']}
    assert [len(groups[s]) for s in ['train','val','test']]==[404,58,115]
    assert not (groups['train']&groups['val'] or groups['train']&groups['test'] or groups['val']&groups['test'])
    for split in ['train','val','test']:
        recorded=set((ROOT.parents[1]/f'dataset/IXI/splits/seed3407/{split}_cases.txt').read_text().split())
        assert recorded==groups[split],'Historical I3Net and bridge patient splits differ'


def runtime():
    result=dict(torch=torch.__version__,cuda_build=torch.version.cuda,cudnn=torch.backends.cudnn.version(),
        gpu=torch.cuda.get_device_name(),matmul_tf32=torch.backends.cuda.matmul.allow_tf32,cudnn_tf32=torch.backends.cudnn.allow_tf32)
    try:
        r=subprocess.run(['nvidia-smi','--query-gpu=driver_version','--format=csv,noheader'],capture_output=True,text=True,timeout=10)
        result['driver_version']=r.stdout.strip();result['driver_query_exit_code']=r.returncode
    except Exception as exc:result['driver_query_error']=str(exc)
    return result


def atomic(payload,path):
    tmp=path.with_suffix('.tmp.pth');torch.save(payload,tmp);tmp.replace(path)


def loss_fn(pred,target):
    error=pred.float()-target.float()
    return error.square().mean()+.05*torch.sqrt(error.square()+1e-6).mean()


def baseline(smoke=False):
    lock=dict(i3_sha256=I3_SHA,data_sha256=sha256(MANIFEST),code_hashes=hashes(),smoke=smoke,test_used=False)
    identity=hashlib.sha256(json.dumps(lock,sort_keys=True).encode()).hexdigest()[:12]
    out=ROOT/'results'/('smoke_frozen_i3' if smoke else 'frozen_i3_validation')/identity
    if (out/'completion.json').exists():
        saved=json.loads((out/'completion.json').read_text());assert saved['lock']==lock and saved['completed']
        assert saved['per_patient_sha256']==sha256(out/'per_patient.csv');return out
    out.mkdir(parents=True,exist_ok=True);write_json(out/'lock.json',lock)
    teacher=Teacher().cuda();seed_all(3407)
    metrics=evaluate(None,teacher,Windows('val',limit=1 if smoke else None),out)
    write_json(out/'completion.json',dict(completed=True,lock=lock,metrics=metrics,
        per_patient_sha256=sha256(out/'per_patient.csv'),runtime=runtime(),test_used=False))
    del teacher;torch.cuda.empty_cache();return out


def optimizer_for(model):
    return torch.optim.AdamW([
        dict(params=list(model.past.parameters()),lr=RECIPE['lr'],initial_lr=RECIPE['lr']),
        dict(params=list(model.readout.parameters()),lr=RECIPE['adapter_lr'],initial_lr=RECIPE['adapter_lr'])],
        weight_decay=RECIPE['weight_decay'],betas=RECIPE['betas'])


def memory_probe(a):
    seed_all(a.seed);ds=Windows('train',limit=1,sample_limit=max(16,a.micro))
    teacher=Teacher().cuda();model=Bridge('latent').cuda().train()
    model.past.base.single.checkpoint_blocks=a.checkpoint;ema=copy.deepcopy(model).eval().requires_grad_(False)
    optimizer=optimizer_for(model)
    b=device_batch(next(iter(DataLoader(ds,batch_size=a.micro,shuffle=False))),torch.device('cuda'))
    torch.cuda.reset_peak_memory_stats();started=time.perf_counter()
    for _ in range(3):
        optimizer.zero_grad(set_to_none=True);p,f=teacher(b['teacher_anchors'])
        with torch.autocast('cuda',dtype=torch.bfloat16):pred=model(b,p,f);loss=loss_fn(pred,b['target'])
        assert torch.isfinite(loss);loss.backward()
        norm=torch.nn.utils.clip_grad_norm_(model.parameters(),RECIPE['clip'],error_if_nonfinite=True)
        optimizer.step()
        with torch.no_grad():
            for name,v in ema.state_dict().items():v.lerp_(model.state_dict()[name],1-RECIPE['ema'])
    torch.cuda.synchronize()
    result=dict(passed=True,micro_batch=a.micro,checkpoint_blocks=a.checkpoint,steps=3,full_backbone_unfrozen=True,
        loss=float(loss.detach()),grad_norm=float(norm),seconds_per_microbatch=(time.perf_counter()-started)/3,
        peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
        teacher_and_ema_resident=True,precision='BF16 bridge, FP32 I3Net and loss',test_used=False,
        model_sha256=sha256(ROOT/'model.py'),trainer_sha256=sha256(ROOT/'run.py'),dependencies=hashes()['dependencies'],runtime=runtime())
    write_json(ROOT/'results'/f'memory_micro{a.micro}_cp{a.checkpoint}.json',result);print(json.dumps(result,indent=2),flush=True)


def train(a):
    recipe=dict(RECIPE)
    if a.smoke:recipe.update(epochs=2,min_epochs=2,freeze_epochs=0)
    if a.stop_after_epoch and not a.smoke:raise ValueError('Interruption checks are smoke-only')
    execution=json.loads((ROOT/'execution.json').read_text());micro=execution['micro_batch'];accum=recipe['effective_batch']//micro
    assert micro*accum==recipe['effective_batch']
    base=baseline(a.smoke);seed_all(a.seed)
    ds=Windows('train',limit=1 if a.smoke else None,sample_limit=16 if a.smoke else None)
    val=Windows('val',limit=1 if a.smoke else None)
    manifest=dict(variant=a.variant,seed=a.seed,smoke=a.smoke,recipe=recipe,execution=execution,
        code_hashes=hashes(),data_sha256=sha256(MANIFEST),i3_sha256=I3_SHA,past_sha256=PAST_SHA,
        frozen_baseline_dir=str(base),frozen_baseline_sha256=sha256(base/'per_patient.csv'),train_windows_available=len(ds.items),train_windows_per_epoch=len(ds),
        val_patients=len(val.records),initial_prediction='exact frozen I3Net before overlap fusion; zero bridge readout',
        sampler='4000 complete observed-grid four-anchor windows; one of 3 intervals chosen by epoch seed + index, not labels',
        seed_scope='adaptation seeds from fixed historical I3Net and PAST checkpoints, not independent scratch pretraining',test_used=False)
    if a.out.exists():
        assert a.resume,'Use --resume; preserve existing run'
        assert json.loads((a.out/'manifest.json').read_text())==manifest,'Resume contract changed'
        if (a.out/'completion.json').exists():
            done=json.loads((a.out/'completion.json').read_text())
            assert done['completed'] and done['best_sha256']==sha256(a.out/'best.pth') and done['last_sha256']==sha256(a.out/'last.pth')
            print(f'{a.variant}: completed, verified and skipped.',flush=True);return
    else:a.out.mkdir(parents=True);write_json(a.out/'manifest.json',manifest)
    write_json(a.out/'runtime_sessions'/f'{time.time_ns()}.json',dict(runtime=runtime(),resume_requested=a.resume,
        note='Environment recorded separately; changed driver does not silently change the frozen recipe or manifest'))
    teacher=Teacher().cuda();model=Bridge(a.variant).cuda();model.past.base.single.checkpoint_blocks=execution['checkpoint_blocks']
    ema=copy.deepcopy(model).eval().requires_grad_(False);optimizer=optimizer_for(model)
    start,best,wait,history=0,float(json.loads((base/'summary.json').read_text())['psnr']),0,[]
    best_payload=dict(variant=a.variant,model_state_dict={k:v.detach().cpu().clone() for k,v in ema.state_dict().items()},epoch=0)
    def commit(epoch):
        atomic(dict(model=model.state_dict(),ema=ema.state_dict(),optimizer=optimizer.state_dict(),epoch=epoch,best=best,wait=wait,
            history=history,best_payload=best_payload,best_sha256=sha256(a.out/'best.pth'),python_rng=random.getstate(),
            numpy_rng=np.random.get_state(),torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all()),a.out/'last.pth')
        if history:pd.DataFrame(history).to_csv(a.out/'history.csv',index=False)
    if (a.out/'last.pth').exists():
        saved=torch.load(a.out/'last.pth',map_location='cpu',weights_only=False)
        model.load_state_dict(saved['model']);ema.load_state_dict(saved['ema']);optimizer.load_state_dict(saved['optimizer'])
        start,best,wait,history=saved['epoch'],saved['best'],saved['wait'],saved['history'];best_payload=saved['best_payload']
        if not (a.out/'best.pth').exists() or sha256(a.out/'best.pth')!=saved['best_sha256']:
            print('Discarding uncommitted best write; restoring last committed best.',flush=True)
            atomic(best_payload,a.out/'best.pth');restored=Bridge(a.variant).cuda();restored.load_state_dict(best_payload['model_state_dict'])
            evaluate(restored,teacher,val,a.out/'validation');del restored
        random.setstate(saved['python_rng']);np.random.set_state(saved['numpy_rng']);torch.set_rng_state(saved['torch_rng']);torch.cuda.set_rng_state_all(saved['cuda_rng']);del saved
        if history:pd.DataFrame(history).to_csv(a.out/'history.csv',index=False)
    else:
        print('Committing exact I3Net initialization.',flush=True);atomic(best_payload,a.out/'best.pth')
        shutil.copytree(base,a.out/'validation',dirs_exist_ok=True);commit(0)
    generator=torch.Generator();loader=DataLoader(ds,batch_size=micro,shuffle=True,num_workers=0,generator=generator)
    elapsed=history[-1]['elapsed_seconds'] if history else 0.;started=time.perf_counter()
    print(f'{a.variant}: micro{micro} x accumulation{accum}; checkpoint{execution["checkpoint_blocks"]}/10; frozen FP32 I3Net + BF16 bridge',flush=True)
    for epoch in range(start,recipe['epochs']):
        if epoch>=recipe['min_epochs'] and wait>=recipe['patience']:break
        generator.manual_seed(a.seed*1000+epoch);ds.set_epoch(a.seed*1000+epoch)
        model.past.requires_grad_(epoch>=recipe['freeze_epochs']);model.readout.requires_grad_(True)
        model.train();optimizer.zero_grad(set_to_none=True);total=0.;updates=0;torch.cuda.reset_peak_memory_stats()
        progress=max(0.,(epoch+1-recipe['warmup'])/max(1,recipe['epochs']-recipe['warmup']))
        factor=min(1.,(epoch+1)/recipe['warmup'])*(.05+.95*.5*(1+math.cos(math.pi*progress)))
        for group in optimizer.param_groups:group['lr']=group['initial_lr']*factor
        for step,batch in enumerate(loader):
            b=device_batch(batch,torch.device('cuda'));samples=b['cond'].shape[0]
            p,f=teacher(b['teacher_anchors'])
            with torch.autocast('cuda',dtype=torch.bfloat16):pred=model(b,p,f);loss=loss_fn(pred,b['target'])
            if not torch.isfinite(loss):
                write_json(a.out/'failure.json',dict(epoch=epoch+1,microbatch=step,patients=batch['patient_id'],exception='Nonfinite loss'))
                raise FloatingPointError('Nonfinite loss; no skipped data or precision retry')
            group_samples=min(recipe['effective_batch'],len(ds)-(step//accum)*accum*micro)
            (loss*samples/group_samples).backward();total+=float(loss.detach())*samples
            if (step+1)%accum==0 or step+1==len(loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(),recipe['clip'],error_if_nonfinite=True)
                optimizer.step();optimizer.zero_grad(set_to_none=True);updates+=1
                with torch.no_grad():
                    state=model.state_dict()
                    for name,value in ema.state_dict().items():value.lerp_(state[name],1-recipe['ema'])
            if (step+1)%100==0:print(f'{a.variant} epoch{epoch+1}: {step+1}/{len(loader)} microbatches',flush=True)
        allocated=torch.cuda.max_memory_allocated()/2**30;reserved=torch.cuda.max_memory_reserved()/2**30
        # Capture TRAIN memory before validation resets its own counters.
        metrics=evaluate(ema,teacher,val,a.out/'validation_current')
        if metrics['psnr']>best:
            best=metrics['psnr'];wait=0
            best_payload=dict(variant=a.variant,model_state_dict={k:v.detach().cpu().clone() for k,v in ema.state_dict().items()},epoch=epoch+1)
            atomic(best_payload,a.out/'best.pth')
            shutil.copytree(a.out/'validation_current',a.out/'validation',dirs_exist_ok=True)
        else:wait+=1
        history.append(dict(epoch=epoch+1,train_loss=total/len(ds),validation_psnr=metrics['psnr'],best_psnr=best,
            applied_updates=updates,elapsed_seconds=elapsed+time.perf_counter()-started,peak_allocated_gib=allocated,peak_reserved_gib=reserved))
        commit(epoch+1);print(json.dumps(history[-1]),flush=True)
        if a.stop_after_epoch==epoch+1:print('Committed isolated smoke interruption.',flush=True);return
    epochs=history[-1]['epoch'] if history else start
    if best_payload['epoch']==0:
        # Even an unchanged I3 prediction still executes the bridge at deployment.
        # Replace initial teacher-only efficiency with actual best-model inference cost.
        restored=Bridge(a.variant).cuda();restored.load_state_dict(best_payload['model_state_dict'])
        evaluate(restored,teacher,val,a.out/'validation');del restored
    write_json(a.out/'completion.json',dict(completed=True,smoke=a.smoke,epochs=epochs,best_psnr=best,
        best_sha256=sha256(a.out/'best.pth'),last_sha256=sha256(a.out/'last.pth'),stopped_early=epochs<recipe['epochs'],test_used=False))


def main():
    p=argparse.ArgumentParser();p.add_argument('--variant',choices=['blind','latent'],default='latent')
    p.add_argument('--seed',type=int,choices=[3407,2027,9103],default=3407);p.add_argument('--out',type=Path)
    p.add_argument('--resume',action='store_true');p.add_argument('--smoke',action='store_true');p.add_argument('--preflight',action='store_true')
    p.add_argument('--baseline',action='store_true');p.add_argument('--memory-probe',action='store_true')
    p.add_argument('--micro',type=int,default=4);p.add_argument('--checkpoint',type=int,default=5);p.add_argument('--stop-after-epoch',type=int,default=0)
    a=p.parse_args();validate_sources();assert torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    if a.memory_probe:memory_probe(a);return
    if a.baseline:baseline(a.smoke);return
    if not a.smoke:
        checks=json.loads((ROOT/'results/checks.json').read_text());assert checks['passed'] and checks['code_hashes']==hashes(),'Checks missing or stale'
        if a.seed!=3407:
            gate=json.loads((ROOT/'results/gate_seed3407.json').read_text())
            assert gate['passed'] and gate['code_hashes']==hashes(),'Additional seeds require seed3407 gate'
    if a.preflight:
        write_json(ROOT/'results/preflight.json',dict(passed=True,code_hashes=hashes(),execution=json.loads((ROOT/'execution.json').read_text()),full_started=False));print('Read-only preflight passed.',flush=True);return
    a.out=a.out or ROOT/'runs'/f'{"smoke" if a.smoke else "full"}_{a.variant}_seed{a.seed}'
    train(a)


if __name__=='__main__':main()
