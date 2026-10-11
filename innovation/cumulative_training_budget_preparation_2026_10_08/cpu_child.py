"""Own CPU-only qualification subprocess; no model or medical import."""
import argparse,json,hashlib,os,sys,time
from pathlib import Path
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--journal',required=True);ap.add_argument('--step',type=int,required=True)
    ap.add_argument('--crash-after-journal',action='store_true');args=ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    destination=Path(args.journal).resolve()
    assert destination.is_relative_to(Path(__file__).resolve().parent) and 1<=args.step<=3
    rows=[]
    for arm in ('legacy_dense','direct','common_projected_dense'):
        token=f'synthetic-common-step-{args.step}'
        rows.append(dict(arm=arm,step=args.step,shared_token=token,work_kind='sha256_cpu_marker',
            digest=hashlib.sha256(token.encode('ascii')).hexdigest()))
    with destination.open('x',encoding='utf-8') as f:
        for row in rows:f.write(json.dumps(row,separators=(',',':'))+'\n')
        f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actual_CPU_work_units=3,neural_updates=0,MRI_arrays_loaded=0,
        torch_imported='torch' in sys.modules,numpy_imported='numpy' in sys.modules,planned_exit=17 if args.crash_after_journal else 0)),flush=True)
    return 17 if args.crash_after_journal else 0
if __name__=='__main__':raise SystemExit(main())

