import json,sys
from pathlib import Path
import torch
import pastnet_v2.run as trainer
from pastnet_v2.common import G086,sha256
from .model import make_model,VARIANTS
from .losses import objective
ROOT=Path(__file__).resolve().parent
original_code_hashes=trainer.code_hashes
def code_hashes():
    result=original_code_hashes()
    result.update({'orientation/'+p.name:sha256(p) for p in sorted(ROOT.glob('*.py'))})
    for n in ('PROTOCOL_ZH.md','full.ps1'):result['orientation/'+n]=sha256(ROOT/n)
    return result
def load_model(variant,checkpoint=None):
    model=make_model(variant);payload=torch.load(checkpoint or G086,map_location='cpu',weights_only=False)
    if 'variant' in payload:
        if payload['variant']!=variant:raise ValueError('Checkpoint variant mismatch')
        model.load_state_dict(payload['model_state_dict'],strict=True)
    else:model.load_g086(payload)
    return model
def main():
    args=sys.argv[1:]
    if '--lock' in args or ('--split' in args and args[args.index('--split')+1]=='test'):raise ValueError('External evaluation locked')
    if 'train' in args and '--smoke' not in args:
        if args[args.index('--variant')+1]!='orientation':raise ValueError('Reuse existing control')
        for name in ('probe','checks'):
            check=json.loads((ROOT/'results'/f'{name}.json').read_text(encoding='utf-8'))
            if not check['passed'] or check['code_hashes']!=code_hashes():raise ValueError(f'{name} stale or failed')
    if '--preflight' in args:
        from pastnet_v2.common import PACKAGE,write_json
        from pastnet_v2.data import IntervalDataset
        data=PACKAGE/'manifests/fastmri/fold_00.json'
        variant=args[args.index('--variant')+1]
        model=load_model(variant)
        result=dict(passed=True,full_started=False,seed=int(args[args.index('--seed')+1]),variant=variant,
            train_intervals=len(IntervalDataset(data,'train')),val_intervals=len(IntervalDataset(data,'val')),
            parameters=sum(p.numel() for p in model.parameters()),recipe=trainer.RECIPE,
            micro_batch=int(args[args.index('--micro-batch-size')+1]),checkpoint_blocks=int(args[args.index('--checkpoint-blocks')+1]),
            code_hashes=code_hashes())
        write_json(ROOT/'results/full_preflight.json',result);print('Full preflight passed; no training started.');return
    if '--resume' in args:
        out=Path(args[args.index('--out')+1])
        if (out/'completion.json').exists():
            m=json.loads((out/'manifest.json').read_text());c=json.loads((out/'completion.json').read_text())
            if m['code_hashes']!=code_hashes() or sha256(out/'best.pth')!=c['best_sha256']:raise ValueError('Completed run changed')
            if m['seed']!=int(args[args.index('--seed')+1]) or m['variant']!=args[args.index('--variant')+1]:raise ValueError('Resume seed/variant mismatch')
            expected=dict(trainer.RECIPE)
            if '--smoke' in args:expected.update(epochs=1,effective_batch_size=2,freeze_epochs=0)
            if m['recipe']!=expected or m['smoke']!=('--smoke' in args):raise ValueError('Resume recipe/smoke mismatch')
            if m['execution']['micro_batch_size']!=int(args[args.index('--micro-batch-size')+1]) or m['execution']['checkpoint_blocks']!=int(args[args.index('--checkpoint-blocks')+1]):raise ValueError('Resume execution mismatch')
            if not c['completed'] or m['data_sha256']!=sha256(m['data_manifest']):raise ValueError('Completion/data changed')
            print('Completed run verified; no additional training.');return
    trainer.VARIANTS=VARIANTS;trainer.load_model=load_model;trainer.code_hashes=code_hashes;trainer.objective=objective
    trainer.main()
if __name__=='__main__':main()
