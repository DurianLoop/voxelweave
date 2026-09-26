"""Own two-arm registration, frozen original training loop and recipe."""
import sys
import json
from pathlib import Path
import torch
import pastnet_v2.run as trainer
from pastnet_v2.common import G086,sha256
from .model import TrajectoryPASTNet,VARIANTS

ROOT=Path(__file__).resolve().parent
original_code_hashes=trainer.code_hashes


def code_hashes():
    result=original_code_hashes()
    result.update({'trajectory/'+p.name:sha256(p) for p in sorted(ROOT.glob('*.py'))})
    for name in ('PROTOCOL_ZH.md','full.ps1'):
        result['trajectory/'+name]=sha256(ROOT/name)
    return result


def load_model(variant,checkpoint=None):
    model=TrajectoryPASTNet(variant)
    payload=torch.load(checkpoint or G086,map_location='cpu',weights_only=False)
    if 'variant' in payload:
        if payload['variant']!=variant:raise ValueError('Checkpoint variant mismatch')
        model.load_state_dict(payload['model_state_dict'],strict=True)
    else:model.load_g086(payload)
    return model


def configure():
    trainer.VARIANTS=VARIANTS
    trainer.load_model=load_model
    trainer.code_hashes=code_hashes


def main():
    args=sys.argv[1:]
    if '--lock' in args or ('--split' in args and args[args.index('--split')+1]=='test'):
        raise ValueError('This pilot permits fastMRI train/validation only')
    if 'train' in args and '--smoke' not in args and '--variant' in args:
        variant=args[args.index('--variant')+1]
        if variant=='trajectory_extended':
            seed=int(args[args.index('--seed')+1]) if '--seed' in args else 3407
            parent=ROOT/'runs'/f'full_trajectory_local_seed{seed}_vram20'
            from .report import local_health
            health=local_health(parent)
            if not health['eligible']:raise ValueError(f'Local capacity control failed: {health}')
    configure();trainer.main()


if __name__=='__main__':main()
