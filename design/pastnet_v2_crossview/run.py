"""Reuse frozen training loop; source and preregistration are independently hashed."""
import sys,json
from pathlib import Path
import torch
import pastnet_v2.run as trainer
from pastnet_v2.common import G086,sha256
from .model import CrossViewPASTNet,VARIANTS

ROOT=Path(__file__).resolve().parent
original_code_hashes=trainer.code_hashes


def code_hashes():
    result=original_code_hashes()
    result.update({'crossview/'+p.name:sha256(p) for p in sorted(ROOT.glob('*.py'))})
    for n in ('PROTOCOL_ZH.md','full.ps1'):result['crossview/'+n]=sha256(ROOT/n)
    return result


def load_model(variant,checkpoint=None):
    model=CrossViewPASTNet(variant)
    payload=torch.load(checkpoint or G086,map_location='cpu',weights_only=False)
    if 'variant' in payload:
        if payload['variant']!=variant:raise ValueError('Wrong checkpoint variant')
        model.load_state_dict(payload['model_state_dict'],strict=True)
    else:model.load_g086(payload)
    return model


def configure():
    trainer.VARIANTS=VARIANTS;trainer.load_model=load_model;trainer.code_hashes=code_hashes


def main():
    args=sys.argv[1:]
    if '--lock' in args or ('--split' in args and args[args.index('--split')+1]=='test'):
        raise ValueError('Pilot is train/validation only')
    if 'train' in args and '--smoke' not in args:
        capacity=json.loads((ROOT/'results/capacity.json').read_text(encoding='utf-8'))
        if not capacity['passed'] or capacity['code_hashes']!=code_hashes():raise ValueError('Capacity / contract check missing or stale')
        variant=args[args.index('--variant')+1]
        if variant=='per_anchor':
            from .report import candidate_report
            seed=int(args[args.index('--seed')+1]) if '--seed' in args else 3407
            if not candidate_report(ROOT/'runs'/f'full_crossview_seed{seed}_vram20')['promoted']:
                raise ValueError('Crossview did not qualify for capacity-matched ablation')
    configure();trainer.main()


if __name__=='__main__':main()
