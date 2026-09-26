"""Separate experiment entry; reuse the frozen, measured trainer without edits."""
from pathlib import Path
import sys
import torch
import pastnet_v2.run as trainer
from pastnet_v2.common import G086,sha256
from pastnet_v2.model import PASTNetV2
from .model import CorrespondenceOnly

ROOT=Path(__file__).resolve().parent
original_code_hashes=trainer.code_hashes


def code_hashes():
    hashes=original_code_hashes()
    hashes.update({'independent/'+p.name:sha256(p) for p in sorted(ROOT.glob('*.py'))})
    hashes['independent/PROTOCOL_ZH.md']=sha256(ROOT/'PROTOCOL_ZH.md')
    return hashes


def load_model(variant,checkpoint=None):
    model=CorrespondenceOnly() if variant=='correspondence_only' else PASTNetV2('control')
    payload=torch.load(checkpoint or G086,map_location='cpu',weights_only=False)
    if 'variant' in payload:
        if payload['variant']!=variant:
            raise ValueError('Independent checkpoint variant mismatch')
        model.load_state_dict(payload['model_state_dict'],strict=True)
    else:
        model.load_g086(payload)
    return model


def configure():
    # This entry has its own two-arm design. It does not change the original
    # geometry gate or permit the stopped cumulative correspondence experiment.
    trainer.VARIANTS={'control':(False,False,False,False,4),
                      'correspondence_only':(False,True,False,False,4)}
    trainer.load_model=load_model
    trainer.code_hashes=code_hashes


def main():
    if '--lock' in sys.argv or ('--split' in sys.argv and sys.argv[sys.argv.index('--split')+1]=='test'):
        raise ValueError('This independent pilot supports train/validation only')
    configure()
    trainer.main()


if __name__=='__main__':
    main()
