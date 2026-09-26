"""Check completed smokes, integrity and full entry without starting full."""
import json,sys
from pathlib import Path
from unittest.mock import patch
import torch
from pastnet_v2.common import PACKAGE,write_json
from . import run as entry
from . import report

ROOT=Path(__file__).resolve().parent


def main():
    capacity=json.loads((ROOT/'results/capacity.json').read_text())
    assert capacity['passed'] and capacity['code_hashes']==entry.code_hashes()
    for variant in ('global','local'):
        path=ROOT/'runs'/f'smoke_{variant}'
        m=json.loads((path/'manifest.json').read_text());c=json.loads((path/'completion.json').read_text())
        assert m['code_hashes']==entry.code_hashes() and m['smoke'] and c['completed']
        assert m['execution']['checkpoint_blocks']==5
        try:report.load_run(path)
        except ValueError:pass
        else:raise AssertionError('Smoke entered full gate')
    old=json.loads((PACKAGE/'runs/full_control_seed3407_vram20/manifest.json').read_text())
    assert old['code_hashes']==entry.original_code_hashes()
    seen=[]
    def stub():seen.append(tuple(sys.argv))
    arguments=['globalmatch.run','train','--variant','global','--seed','3407','--out',str(ROOT/'runs/full_global_seed3407_vram20'),
               '--micro-batch-size','2','--checkpoint-blocks','5']
    with patch.object(sys,'argv',arguments),patch.object(entry.trainer,'main',stub):entry.main()
    assert len(seen)==1
    denied=[]
    for extra in (['--split','test'],['--lock','unused']):
        with patch.object(sys,'argv',arguments+extra),patch.object(entry.trainer,'main',stub):
            try:entry.main()
            except ValueError:denied.append(extra[0])
            else:raise AssertionError('External gate bypassed')
    local_args=[x if x!='global' else 'local' for x in arguments]
    with patch.object(sys,'argv',local_args),patch.object(entry.trainer,'main',stub),patch.object(report,'candidate_report',return_value={'promoted':False}):
        try:entry.main()
        except ValueError:pass
        else:raise AssertionError('Local accepted failed E1')
    assert len(seen)==1 and not (ROOT/'runs/full_global_seed3407_vram20').exists()
    efficiencies={v:json.loads((ROOT/f'results/efficiency_{v}.json').read_text()) for v in ('global','local')}
    assert efficiencies['global']['parameters']==efficiencies['local']['parameters']
    assert efficiencies['global']['conv_linear_gflops_interval']==efficiencies['local']['conv_linear_gflops_interval']
    reference=json.loads((PACKAGE/'runs/full_control_seed3407_vram20/efficiency.json').read_text())
    assert all(e['contract']==reference['contract'] and e['device']==reference['device'] for e in efficiencies.values())
    ratios={v:dict(latency=e['latency_ms_interval_median']/reference['latency_ms_interval_median'],
                   memory=e['peak_forward_gib']/reference['peak_forward_gib']) for v,e in efficiencies.items()}
    assert all(r['latency']<=1.5 and r['memory']<=1.5 for r in ratios.values())
    write_json(ROOT/'results/final_verification.json',dict(capacity_and_hashes=True,
        smoke_both_completed=True,smoke_rejected_by_full_report=True,old_source_integrity=True,
        full_preflight_stub_only=True,external_blocked=denied,local_blocked_on_failed_E1=True,
        equal_parameters_and_dense_attention_flops=True,efficiency_contract_matched=True,
        efficiency_ratios=ratios,full_started=False,code_hashes=entry.code_hashes()))
    print(json.dumps(dict(passed=True,efficiency_ratios=ratios,full_started=False),indent=2))


if __name__=='__main__':main()
