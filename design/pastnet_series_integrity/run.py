import json,sys
from pathlib import Path
import torch
import pastnet_v2.run as trainer
from pastnet_v2.common import G086,sha256,write_json
from .audit import ROOT
from .prepare import MANIFEST
from .model import make_model,VARIANTS
original_code_hashes=trainer.code_hashes
def code_hashes():
    result=original_code_hashes()
    result.update({'series_integrity/'+p.name:sha256(p) for p in sorted(ROOT.glob('*.py'))})
    for name in ('PROTOCOL_ZH.md','full.ps1','results/repair_mapping.json','manifests/fastmri_repaired.json'):
        result['series_integrity/'+name]=sha256(ROOT/name)
    for p in sorted((ROOT/'data').glob('*.nii.gz')):result['series_integrity/data/'+p.name]=sha256(p)
    return result
def load_model(variant,checkpoint=None):
    m=make_model(variant);payload=torch.load(checkpoint or G086,map_location='cpu',weights_only=False)
    if 'variant' in payload:
        if payload['variant']!=variant:raise ValueError('Checkpoint variant mismatch')
        m.load_state_dict(payload['model_state_dict'],strict=True)
    else:m.load_g086(payload)
    return m
def main():
    args=sys.argv[1:]
    if '--lock' in args or ('--split' in args and args[args.index('--split')+1]=='test'):raise ValueError('External evaluation locked')
    if '--manifest' in args:
        if Path(args[args.index('--manifest')+1]).resolve()!=MANIFEST.resolve():raise ValueError('Only registered repaired manifest')
    else:sys.argv.extend(['--manifest',str(MANIFEST)])
    if 'train' in args and '--smoke' not in args:
        check=json.loads((ROOT/'results/checks.json').read_text())
        if not check['passed'] or check['code_hashes']!=code_hashes():raise ValueError('Repair checks failed or stale')
    if '--preflight' in args:
        from pastnet_v2.data import IntervalDataset
        result=dict(passed=True,full_started=False,train_intervals=len(IntervalDataset(MANIFEST,'train')),
            val_intervals=len(IntervalDataset(MANIFEST,'val')),recipe=trainer.RECIPE,code_hashes=code_hashes())
        write_json(ROOT/'results/full_preflight.json',result);print('Full preflight passed; no training started.');return
    if '--resume' in args:
        out=Path(args[args.index('--out')+1])
        if (out/'completion.json').exists():
            m=json.loads((out/'manifest.json').read_text());c=json.loads((out/'completion.json').read_text())
            expected=dict(trainer.RECIPE)
            if '--smoke' in args:expected.update(epochs=1,effective_batch_size=2,freeze_epochs=0)
            assert m['recipe']==expected and m['smoke']==('--smoke' in args)
            assert m['code_hashes']==code_hashes() and m['data_sha256']==sha256(MANIFEST)
            assert c['completed'] and sha256(out/'best.pth')==c['best_sha256']
            assert m['seed']==int(args[args.index('--seed')+1]) and m['variant']=='repair'
            assert m['execution']['micro_batch_size']==int(args[args.index('--micro-batch-size')+1])
            assert m['execution']['checkpoint_blocks']==int(args[args.index('--checkpoint-blocks')+1])
            print('Completed run verified; no extra training.');return
    trainer.VARIANTS=VARIANTS;trainer.load_model=load_model;trainer.code_hashes=code_hashes
    trainer.main()
if __name__=='__main__':main()
