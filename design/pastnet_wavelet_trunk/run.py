import json,sys
from pathlib import Path
import torch
import pastnet_v2.run as trainer
from pastnet_v2.common import G086,sha256,write_json
from pastnet_series_integrity.prepare import MANIFEST
from pastnet_series_integrity.run import code_hashes as repair_code_hashes
from .model import make_model,VARIANTS
ROOT=Path(__file__).resolve().parent
def code_hashes():
    result=repair_code_hashes()
    result.update({'wavelet_trunk/'+p.name:sha256(p) for p in sorted(ROOT.glob('*.py'))})
    for n in ('PROTOCOL_ZH.md','full.ps1'):result['wavelet_trunk/'+n]=sha256(ROOT/n)
    return result
def load_model(variant,checkpoint=None):
    m=make_model(variant);payload=torch.load(checkpoint or G086,map_location='cpu',weights_only=False)
    if 'variant' in payload:
        if payload['variant']!=variant:raise ValueError('Checkpoint mismatch')
        m.load_state_dict(payload['model_state_dict'],strict=True)
    else:m.load_g086(payload)
    return m
def main():
    args=sys.argv[1:]
    if '--lock' in args or ('--split' in args and args[args.index('--split')+1]=='test'):raise ValueError('External evaluation locked')
    if '--manifest' in args:
        if Path(args[args.index('--manifest')+1]).resolve()!=MANIFEST.resolve():raise ValueError('Use repaired data')
    else:sys.argv.extend(['--manifest',str(MANIFEST)])
    if 'train' in args and '--smoke' not in args:
        for n in ('checks','capacity'):
            r=json.loads((ROOT/'results'/f'{n}.json').read_text())
            if not r['passed'] or r['code_hashes']!=code_hashes():raise ValueError(f'{n} failed or stale')
        if args[args.index('--variant')+1]=='wavelet1':
            gate=json.loads((ROOT/'results/gate_wavelet3_seed3407.json').read_text())
            if not gate['promoted'] or gate['variant']!='wavelet3':raise ValueError('J3 did not pass screen')
            for path,h in gate['candidate_runs'].items():
                if sha256(Path(path)/'best.pth')!=h:raise ValueError('Gate weights changed')
    if '--preflight' in args:
        from pastnet_v2.data import IntervalDataset
        write_json(ROOT/'results/full_preflight.json',dict(passed=True,full_started=False,train_intervals=len(IntervalDataset(MANIFEST,'train')),
            val_intervals=len(IntervalDataset(MANIFEST,'val')),recipe=trainer.RECIPE,code_hashes=code_hashes()))
        print('Full preflight passed; no training.');return
    if '--resume' in args:
        out=Path(args[args.index('--out')+1])
        if (out/'completion.json').exists():
            m=json.loads((out/'manifest.json').read_text());c=json.loads((out/'completion.json').read_text())
            expected=dict(trainer.RECIPE)
            if '--smoke' in args:expected.update(epochs=1,effective_batch_size=2,freeze_epochs=0)
            assert m['recipe']==expected and m['smoke']==('--smoke' in args) and m['code_hashes']==code_hashes()
            assert m['data_sha256']==sha256(MANIFEST) and c['completed'] and c['best_sha256']==sha256(out/'best.pth')
            assert m['variant']==args[args.index('--variant')+1] and m['seed']==int(args[args.index('--seed')+1])
            assert m['execution']['micro_batch_size']==int(args[args.index('--micro-batch-size')+1])
            assert m['execution']['checkpoint_blocks']==int(args[args.index('--checkpoint-blocks')+1])
            print('Completed run verified; no additional epoch.');return
    trainer.VARIANTS=VARIANTS;trainer.load_model=load_model;trainer.code_hashes=code_hashes;trainer.main()
if __name__=='__main__':main()
