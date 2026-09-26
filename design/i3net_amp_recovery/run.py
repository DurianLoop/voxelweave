"""Keep frozen trainer/source manifest intact; record this runtime fix separately."""
import argparse
import contextlib
import datetime
import json
from pathlib import Path
import torch
import i3net_repaired_reference.run as trainer
from pastnet_v2.common import sha256,write_json

ROOT=Path(__file__).resolve().parent
DEFAULT=trainer.PACKAGE/'runs/full_i3net_repaired_seed3407_vram20'

def hashes():
    return {p.name:sha256(p) for p in sorted(list(ROOT.glob('*.py'))+list(ROOT.glob('*.ps1')))}

@contextlib.contextmanager
def amp_recovery(log,stop_after_attempts=0,reproduce=False):
    original_scaler=torch.amp.GradScaler
    original_clip=torch.nn.utils.clip_grad_norm_
    active={};events=[]
    class Scaler(original_scaler):
        def unscale_(self,optimizer):
            result=super().unscale_(optimizer)
            flags=self._found_inf_per_device(optimizer)
            if not flags:raise RuntimeError('AMP recovery requires enabled, unscaled CUDA gradients')
            active.update(scaler=self,optimizer=optimizer,overflow=any(float(x)>0 for x in flags.values()))
            return result
        def step(self,optimizer,*args,**kwargs):
            overflow=active.get('overflow',False)
            calls=[]
            handle=optimizer.register_step_post_hook(lambda *_:calls.append(True))
            try:result=super().step(optimizer,*args,**kwargs)
            finally:handle.remove()
            if len(calls)!=(0 if overflow else 1):raise RuntimeError('GradScaler optimizer skip contract violated')
            active['applied']=bool(calls)
            return result
        def update(self,*args,**kwargs):
            before=self.get_scale();super().update(*args,**kwargs);after=self.get_scale()
            event=dict(attempt=len(events)+1,overflow=active['overflow'],optimizer_applied=active['applied'],
                       scale_before=before,scale_after=after)
            if event['overflow']:
                if event['optimizer_applied'] or not after<before:raise RuntimeError('Unsafe overflow handling')
                print('AMP overflow: skipped optimizer update, scale '+str(before)+' -> '+str(after),flush=True)
            events.append(event)
            with log.open('a',encoding='utf-8') as f:f.write(json.dumps(event)+'\n')
            active.clear()
            if len(events)>=8 and all(e['overflow'] for e in events[-8:]):
                raise FloatingPointError('Eight consecutive AMP overflows: stop for diagnosis rather than silently skipping training')
            if stop_after_attempts and len(events)>=stop_after_attempts:raise ProbeFinished()
    def clip(parameters,*args,**kwargs):
        parameters=list(parameters)
        if active.get('overflow',False) and not reproduce:
            expected=[p for group in active['optimizer'].param_groups for p in group['params']]
            if {id(p) for p in parameters}!={id(p) for p in expected}:raise RuntimeError('Wrong optimizer gradient set')
            # unscale_ already detected Inf/NaN. Do not modify these gradients;
            # GradScaler.step must skip Adam, and update must reduce the scale.
            return torch.tensor(float('inf'),device=parameters[0].device)
        return original_clip(parameters,*args,**kwargs)
    torch.amp.GradScaler=Scaler;torch.nn.utils.clip_grad_norm_=clip
    try:yield events
    finally:torch.amp.GradScaler=original_scaler;torch.nn.utils.clip_grad_norm_=original_clip

class ProbeFinished(Exception):pass

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=DEFAULT)
    p.add_argument('--probe-attempts',type=int,default=0);p.add_argument('--reproduce',action='store_true')
    p.add_argument('--preflight',action='store_true');a=p.parse_args()
    if (a.probe_attempts or a.reproduce) and not a.out.resolve().is_relative_to((ROOT/'scratch').resolve()):
        raise ValueError('Diagnostics require an isolated checkpoint copy in recovery/scratch')
    m=json.loads((a.out/'manifest.json').read_text(encoding='utf-8'))
    if m['code_hashes']!=trainer.hashes() or m['data_sha256']!=sha256(trainer.DATA):raise ValueError('Frozen source/data mismatch')
    if m['recipe']!=trainer.RECIPE or m['smoke'] or m['seed']!=3407:raise ValueError('Unexpected training contract')
    args=argparse.Namespace(seed=m['seed'],out=a.out,micro_batch=m['execution']['micro_batch'],
        checkpoint_groups=m['execution']['checkpoint_groups'],smoke=False,resume=True,preflight=a.preflight,stop_after_epoch=0)
    if a.preflight:trainer.train(args);return
    if not a.probe_attempts and not a.reproduce:
        check=json.loads((ROOT/'results/checks.json').read_text())
        if not check['passed'] or check['recovery_hashes']!=hashes():raise ValueError('Recovery checks missing/stale')
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    session=a.out/'recovery_audit'/stamp;session.mkdir(parents=True)
    provenance=dict(recovery_hashes=hashes(),frozen_code_hashes=trainer.hashes(),
        last_sha256_before=sha256(a.out/'last.pth'),probe_attempts=a.probe_attempts,reproduce=a.reproduce,
        policy='finite gradients use original strict clipping; AMP-detected overflow skips Adam and halves scale; no bad-gradient update',
        update_count='history updates are attempted updates; applied updates exclude logged AMP skips; epochs/sampler/LR unchanged')
    write_json(session/'provenance.json',provenance)
    try:
        with amp_recovery(session/'updates.jsonl',a.probe_attempts,a.reproduce):trainer.train(args)
    except ProbeFinished:print('Isolated recovery probe completed; no epoch checkpoint committed.')
    if (a.out/'completion.json').exists():
        saved=torch.load(a.out/'last.pth',map_location='cpu',weights_only=False)
        counts=[int(v['step']) for v in saved['optimizer']['state'].values() if 'step' in v]
        attempted=sum(row['updates'] for row in saved['history'])
        write_json(a.out/'amp_recovery_summary.json',dict(completed_epochs=saved['epoch'],
            attempted_updates=attempted,applied_update_range=[min(counts),max(counts)],
            skipped_updates=attempted-max(counts),recovery_hashes=hashes(),
            source='committed final Adam step counters; excludes any abandoned partial epoch',
            note='history updates count attempts, not only applied optimizer steps'))

if __name__=='__main__':main()
