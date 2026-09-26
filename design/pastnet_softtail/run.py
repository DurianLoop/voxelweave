import sys,json
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
    result.update({'softtail/'+p.name:sha256(p) for p in sorted(ROOT.glob('*.py'))})
    for n in ('PROTOCOL_ZH.md','full.ps1'):result['softtail/'+n]=sha256(ROOT/n)
    return result


def load_model(variant,checkpoint=None):
    model=make_model(variant);payload=torch.load(checkpoint or G086,map_location='cpu',weights_only=False)
    if 'variant' in payload:
        if payload['variant']!=variant:raise ValueError('Wrong checkpoint variant')
        model.load_state_dict(payload['model_state_dict'],strict=True)
    else:model.load_g086(payload)
    return model


def configure():
    trainer.VARIANTS=VARIANTS;trainer.load_model=load_model;trainer.code_hashes=code_hashes;trainer.objective=objective


def main():
    args=sys.argv[1:]
    if '--lock' in args or ('--split' in args and args[args.index('--split')+1]=='test'):raise ValueError('No external evaluation before candidate lock')
    if 'train' in args and '--smoke' not in args:
        if args[args.index('--variant')+1]!='soft_tail':raise ValueError('Reuse existing matched hard control full')
        for name in ('capacity','stability'):
            check=json.loads((ROOT/'results'/f'{name}.json').read_text(encoding='utf-8'))
            if not check['passed'] or check['code_hashes']!=code_hashes():raise ValueError(f'{name} evidence missing or stale')
    configure();trainer.main()


if __name__=='__main__':main()
