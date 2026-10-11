"""Reload the sealed ledger in a fresh interpreter; never start a work child."""
import argparse,json,sys
from pathlib import Path
import budget_ledger as core
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap=argparse.ArgumentParser();ap.add_argument('--directory',required=True);ap.add_argument('--contract',required=True)
    ap.add_argument('--expected-head',required=True);ap.add_argument('--reserve-ns',type=int);args=ap.parse_args()
    here=Path(__file__).resolve().parent
    assert Path(args.directory).resolve().is_relative_to(here) and Path(args.contract).resolve().is_relative_to(here)
    result=dict(accepted=False,rejected=False,actual_CPU_work_units=0,neural_imported=False,
        torch_imported='torch' in sys.modules,numpy_imported='numpy' in sys.modules)
    try:
        s=core.state(args.directory,args.contract,args.expected_head)
        if args.reserve_ns is not None:core.admit(s,args.reserve_ns)
        result.update(accepted=True,state={k:s[k] for k in ('head','paid_ns','counts','invocations')})
    except core.Rejected as e:result.update(rejected=True,reason=str(e))
    assert not result['torch_imported'] and not result['numpy_imported']
    print(json.dumps(result),flush=True);return 3 if result['rejected'] else 0
if __name__=='__main__':raise SystemExit(main())
