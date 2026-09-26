import json,sys
from pathlib import Path
import torch
import pastnet_v2.run as trainer
from pastnet_v2.common import G086,PACKAGE,sha256,write_json
from .model import make_model,VARIANTS

ROOT=Path(__file__).resolve().parent
original_code_hashes=trainer.code_hashes
def code_hashes():
    result=original_code_hashes()
    result.update({'frame_context/'+p.name:sha256(p) for p in sorted(ROOT.glob('*.py'))})
    for name in ('PROTOCOL_ZH.md','full.ps1'):result['frame_context/'+name]=sha256(ROOT/name)
    return result
def load_model(variant,checkpoint=None):
    model=make_model(variant);payload=torch.load(checkpoint or G086,map_location='cpu',weights_only=False)
    if 'variant' in payload:
        if payload['variant']!=variant:raise ValueError('Wrong checkpoint variant')
        model.load_state_dict(payload['model_state_dict'],strict=True)
    else:model.load_g086(payload)
    return model
def main():
    args=sys.argv[1:]
    if '--lock' in args or ('--split' in args and args[args.index('--split')+1]=='test'):raise ValueError('External evaluation locked')
    if 'train' in args and '--smoke' not in args:
        variant=args[args.index('--variant')+1]
        for name in ('checks','capacity'):
            record=json.loads((ROOT/'results'/f'{name}.json').read_text())
            if not record['passed'] or record['code_hashes']!=code_hashes():raise ValueError(f'{name} stale or failed')
        if variant=='plain':
            gate=json.loads((ROOT/'results/gate_shared_seed3407.json').read_text())
            if not gate['promoted'] or gate['variant']!='shared':raise ValueError('Shared did not pass preregistered gate')
            for path,h in gate['candidate_runs'].items():
                if sha256(Path(path)/'best.pth')!=h:raise ValueError('Gate checkpoint changed')
    if '--preflight' in args:
        from pastnet_v2.data import IntervalDataset
        data=PACKAGE/'manifests/fastmri/fold_00.json'
        result=dict(passed=True,full_started=False,variant=args[args.index('--variant')+1],seed=int(args[args.index('--seed')+1]),
            train_intervals=len(IntervalDataset(data,'train')),val_intervals=len(IntervalDataset(data,'val')),
            recipe=trainer.RECIPE,code_hashes=code_hashes())
        write_json(ROOT/'results/full_preflight.json',result);print('Full preflight passed; no training started.');return
    if '--resume' in args:
        out=Path(args[args.index('--out')+1])
        if (out/'completion.json').exists():
            m=json.loads((out/'manifest.json').read_text());c=json.loads((out/'completion.json').read_text())
            if m['code_hashes']!=code_hashes() or sha256(out/'best.pth')!=c['best_sha256']:raise ValueError('Run changed')
            expected=dict(trainer.RECIPE)
            if '--smoke' in args:expected.update(epochs=1,effective_batch_size=2,freeze_epochs=0)
            if m['recipe']!=expected or m['smoke']!=('--smoke' in args):raise ValueError('Recipe mismatch')
            if m['seed']!=int(args[args.index('--seed')+1]) or m['variant']!=args[args.index('--variant')+1]:raise ValueError('Seed/variant mismatch')
            if m['execution']['micro_batch_size']!=int(args[args.index('--micro-batch-size')+1]) or m['execution']['checkpoint_blocks']!=int(args[args.index('--checkpoint-blocks')+1]):raise ValueError('Execution mismatch')
            if not c['completed'] or m['data_sha256']!=sha256(m['data_manifest']):raise ValueError('Completion/data mismatch')
            print('Completed run verified; no extra epoch.');return
    trainer.VARIANTS=VARIANTS;trainer.load_model=load_model;trainer.code_hashes=code_hashes
    trainer.main()
if __name__=='__main__':main()
