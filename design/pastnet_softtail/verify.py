import json,sys
from pathlib import Path
from unittest.mock import patch
from pastnet_v2.common import PACKAGE,write_json
from . import run as entry
from . import report

ROOT=Path(__file__).resolve().parent


def main():
    for name in ('capacity','stability'):
        result=json.loads((ROOT/'results'/f'{name}.json').read_text())
        assert result['passed'] and result['code_hashes']==entry.code_hashes()
    for variant in ('hard_tail','soft_tail'):
        path=ROOT/'runs'/f'smoke_{variant}'
        m=json.loads((path/'manifest.json').read_text());c=json.loads((path/'completion.json').read_text())
        assert m['smoke'] and c['completed'] and m['code_hashes']==entry.code_hashes()
        try:report.load_run(path)
        except ValueError:pass
        else:raise AssertionError('Smoke accepted by full report')
    report.load_run(PACKAGE/'runs/full_control_seed3407_vram20')
    arguments=['softtail.run','train','--variant','soft_tail','--seed','3407',
               '--out',str(ROOT/'runs/full_soft_tail_seed3407_vram20'),'--micro-batch-size','2','--checkpoint-blocks','5']
    seen=[]
    def stub():seen.append(tuple(sys.argv))
    with patch.object(sys,'argv',arguments),patch.object(entry.trainer,'main',stub):entry.main()
    assert len(seen)==1
    for args in (arguments+['--split','test'],arguments+['--lock','unused'],[s.replace('soft_tail','hard_tail') for s in arguments]):
        with patch.object(sys,'argv',args),patch.object(entry.trainer,'main',stub):
            try:entry.main()
            except ValueError:pass
            else:raise AssertionError('Forbidden full/test accepted')
    assert len(seen)==1 and not (ROOT/'runs/full_soft_tail_seed3407_vram20').exists()
    efficiency=json.loads((ROOT/'results/efficiency_soft_tail.json').read_text())
    base=json.loads((PACKAGE/'runs/full_control_seed3407_vram20/efficiency.json').read_text())
    assert efficiency['contract']==base['contract'] and efficiency['device']==base['device']
    assert efficiency['parameters']==base['parameters']
    assert efficiency['conv_linear_gflops_interval']==base['conv_linear_gflops_interval']
    ratios=dict(latency=efficiency['latency_ms_interval_median']/base['latency_ms_interval_median'],
                memory=efficiency['peak_forward_gib']/base['peak_forward_gib'])
    assert all(v<=1.5 for v in ratios.values())
    write_json(ROOT/'results/final_verification.json',dict(passed=True,source_and_recipe_integrity=True,
        smoke_both_completed=True,full_report_rejects_smoke=True,registered_checks_passed=True,
        same_parameter_count_and_forward_flops=True,efficiency_ratios=ratios,
        full_preflight_stub_only=True,external_and_redundant_hard_full_blocked=True,
        full_started=False,code_hashes=entry.code_hashes()))
    print(json.dumps(dict(passed=True,efficiency_ratios=ratios,full_started=False),indent=2))


if __name__=='__main__':main()
