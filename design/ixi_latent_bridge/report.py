import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from pastnet_v2.common import sha256,write_json
from .model import ROOT,I3_SHA,PAST_SHA
from .run import hashes

LOWER={'mae','mse','hd95_proxy','tail10_mse'}


def compare(candidate,reference,draw):
    assert candidate.index.equals(reference.index)
    result={}
    for key in candidate:
        d=(candidate[key]-reference[key]).to_numpy();means=d[draw].mean(1)
        result[key]=dict(candidate=float(candidate[key].mean()),reference=float(reference[key].mean()),delta=float(d.mean()),
            ci95=np.quantile(means,[.025,.975]).tolist(),ci975=np.quantile(means,[.0125,.9875]).tolist(),
            wins=int(((d<0) if key in LOWER else (d>0)).sum()))
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,choices=[3407,2027,9103],default=3407);a=p.parse_args()
    frames={};cost={};memory={};identities={};manifests={}
    for variant in ['blind','latent']:
        path=ROOT/'runs'/f'full_{variant}_seed{a.seed}';m=json.loads((path/'manifest.json').read_text());c=json.loads((path/'completion.json').read_text())
        assert c['completed'] and not c['smoke'] and m['code_hashes']==hashes()
        assert sha256(path/'best.pth')==c['best_sha256'] and sha256(path/'last.pth')==c['last_sha256']
        assert m['i3_sha256']==I3_SHA and m['past_sha256']==PAST_SHA
        frames[variant]=pd.read_csv(path/'validation/per_patient.csv').set_index('patient_id').sort_index()
        hist=pd.read_csv(path/'history.csv');cost[variant]=float(hist.elapsed_seconds.iloc[-1]/len(hist));memory[variant]=float(hist.peak_allocated_gib.max())
        efficiency=pd.read_csv(path/'validation/efficiency.csv')
        best=torch.load(path/'best.pth',map_location='cpu',weights_only=False)
        identities[variant]=dict(best_sha256=c['best_sha256'],epochs=c['epochs'],best_epoch=best['epoch'],
            milliseconds_per_missing_slice=float(efficiency.seconds.sum()/efficiency.missing_slices.sum()*1000))
        manifests[variant]=m
    assert manifests['blind']['frozen_baseline_dir']==manifests['latent']['frozen_baseline_dir']
    base=Path(manifests['latent']['frozen_baseline_dir'])
    assert sha256(base/'per_patient.csv')==manifests['latent']['frozen_baseline_sha256']==manifests['blind']['frozen_baseline_sha256']
    frozen=pd.read_csv(base/'per_patient.csv').set_index('patient_id').sort_index()
    candidate,blind=frames['latent'],frames['blind'];assert len(candidate)==58 and candidate.index.equals(frozen.index)
    draw=np.random.default_rng(73019).integers(0,58,(10000,58))
    paired=compare(candidate,blind,draw);absolute=compare(candidate,frozen,draw)
    hard=lambda ref:float((candidate.loc[ref.nsmallest(15,'psnr').index,'psnr']-ref.nsmallest(15,'psnr').psnr).mean())
    quality=lambda r:all(v['delta']<=0 if k in LOWER else v['delta']>=0 for k,v in r.items() if k!='psnr')
    guards=dict(latent_effect=paired['psnr']['delta']>=.05,i3_effect=absolute['psnr']['delta']>=.10,
        both_adjusted_ci=paired['psnr']['ci975'][0]>0 and absolute['psnr']['ci975'][0]>0,
        both_win_rate=paired['psnr']['wins']/58>=.6 and absolute['psnr']['wins']/58>=.6,
        both_hard_quartiles=hard(blind)>=0 and hard(frozen)>=0,
        quality_against_both=quality(paired) and quality(absolute),
        training_time_ratio=cost['latent']/cost['blind']<=1.5,memory_ratio=memory['latent']/memory['blind']<=1.5)
    eff=pd.read_csv(base/'efficiency.csv');base_ms=float(eff.seconds.sum()/eff.missing_slices.sum()*1000)
    result=dict(passed=all(guards.values()),guards=guards,latent_vs_blind=paired,latent_vs_frozen_i3=absolute,
        hard_quartile_delta=dict(blind=hard(blind),frozen_i3=hard(frozen)),seconds_per_epoch=cost,peak_allocated_gib=memory,
        identities=identities,frozen_i3_ms_per_missing_slice=base_ms,
        inference_overhead_vs_i3=identities['latent']['milliseconds_per_missing_slice']/base_ms,
        code_hashes=hashes(),seed=a.seed,scope='validation screening from fixed historical priors; not independent scratch comparison',
        decision='Advance to two prespecified adaptation seeds' if all(guards.values()) else 'Stop this bridge mechanism; no extra seeds or test',test_used=False,sota_claim=False)
    write_json(ROOT/'results'/f'gate_seed{a.seed}.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='code_hashes'},indent=2),flush=True)


if __name__=='__main__':main()
