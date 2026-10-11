import argparse,json
import numpy as np
import pandas as pd
from pastnet_v2.common import sha256,write_json
from .data import ROOT
from .run import hashes


def main():
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=3407);a=p.parse_args()
    runs={v:ROOT/'runs'/f'full_{v}_seed{a.seed}' for v in ('local','extended')}
    frames={};time={};memory={}
    for v,path in runs.items():
        m=json.loads((path/'manifest.json').read_text());done=json.loads((path/'completion.json').read_text())
        assert done['completed'] and not done['smoke'] and done['best_sha256']==sha256(path/'best.pth') and m['code_hashes']==hashes()
        frames[v]=pd.read_csv(path/'validation/per_patient.csv').set_index('patient_id').sort_index()
        hist=pd.read_csv(path/'history.csv');time[v]=float(hist.elapsed_seconds.iloc[-1]/len(hist));memory[v]=float(hist.peak_allocated_gib.max())
    l,e=frames['local'],frames['extended'];assert e.index.equals(l.index) and len(l)==58
    metrics=list(l.columns);rng=np.random.default_rng(73019);draw=rng.integers(0,len(l),(10000,len(l)));records={}
    lower={'mae','mse','hd95_proxy','tail10_mse'}
    for k in metrics:
        d=(e[k]-l[k]).to_numpy();records[k]=dict(local=float(l[k].mean()),extended=float(e[k].mean()),delta=float(d.mean()),
            ci95=np.quantile(d[draw].mean(1),[.025,.975]).tolist(),wins=int(((d<0) if k in lower else (d>0)).sum()))
    anchor=json.loads((runs['extended']/'initial_validation/summary.json').read_text())
    hard=l.nsmallest(int(np.ceil(len(l)*.25)),'psnr').index;hard_delta=float((e.loc[hard,'psnr']-l.loc[hard,'psnr']).mean())
    psnr=records['psnr'];guards=dict(effect=psnr['delta']>=.10,ci=psnr['ci95'][0]>0,win_rate=psnr['wins']/58>=.6,
        hard=hard_delta>=0,quality=all((r['delta']<=0 if k in lower else r['delta']>=0) for k,r in records.items() if k!='psnr'),
        anchor=float(e.psnr.mean())-anchor['psnr']>=.15,time=time['extended']/time['local']<=1.5,memory=memory['extended']/memory['local']<=1.5)
    result=dict(passed=all(guards.values()),guards=guards,metrics=records,hard_quartile_delta=hard_delta,
        anchor_psnr=anchor['psnr'],seconds_per_epoch=time,peak_gib=memory,code_hashes=hashes(),test_used=False,sota_claim=False)
    write_json(ROOT/'results'/f'gate_seed{a.seed}.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
