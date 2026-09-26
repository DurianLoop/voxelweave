"""Integrity verification and descriptive patient-paired reference comparison."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from pastnet_v2.common import PACKAGE as V2,write_json,sha256
from pastnet_v2.run import evaluate,seed_all
from pastnet_v2.data import IntervalDataset
from .model import Reference
from .run import DATA,hashes,finite_metrics

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--control',type=Path,default=V2.parent/'pastnet_series_integrity/runs/full_repair_seed3407_vram20')
    p.add_argument('--smoke',action='store_true');a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    manifest=json.loads((a.run/'manifest.json').read_text());done=json.loads((a.run/'completion.json').read_text())
    assert done['completed'] and done['smoke']==a.smoke and not done['test_used']
    assert manifest['code_hashes']==hashes() and manifest['data_sha256']==sha256(DATA)
    assert done['best_sha256']==sha256(a.run/'best.pth') and done['last_sha256']==sha256(a.run/'last.pth')
    seed_all(manifest['seed']);m=Reference().cuda().eval()
    ckpt=torch.load(a.run/'best.pth',map_location='cpu',weights_only=False);m.load_state_dict(ckpt['model_state_dict'])
    ds=IntervalDataset(DATA,'val',anchors=4,limit=1 if a.smoke else None,sample_limit=1 if a.smoke else None)
    fresh=evaluate(m,ds,torch.device('cuda'));finite_metrics(fresh)
    stored=json.loads((a.run/'validation/summary.json').read_text())
    errors={k:abs(fresh[k]-stored[k]) for k in fresh};assert max(errors.values())<1e-8
    result=dict(integrity_passed=True,smoke=a.smoke,best_epoch=ckpt['epoch'],best_sha256=done['best_sha256'],
        reevaluation_max_abs=max(errors.values()),summary=stored,completion=done,
        comparison_limit=manifest['comparison_limit'])
    if not a.smoke:
        cm=json.loads((a.control/'manifest.json').read_text());cd=json.loads((a.control/'completion.json').read_text())
        assert cm['seed']==manifest['seed'] and cm['data_sha256']==manifest['data_sha256']
        assert cd['completed'] and not cd['smoke'] and cd['best_sha256']==sha256(a.control/'best.pth')
        x=pd.read_csv(a.run/'validation/per_patient.csv',dtype={'patient_id':str}).set_index('patient_id').sort_index()
        y=pd.read_csv(a.control/'validation/per_patient.csv',dtype={'patient_id':str}).set_index('patient_id').sort_index()
        assert x.index.is_unique and y.index.is_unique and x.index.equals(y.index) and len(x)==23
        rng=np.random.default_rng(3407);draws=rng.integers(0,len(x),(10000,len(x)))
        metrics={}
        for key in stored:
            d=(x[key]-y[key]).to_numpy();higher=key in ('psnr','ssim','ncc','dice_proxy')
            metrics[key]=dict(i3net_mean=float(x[key].mean()),past_control_mean=float(y[key].mean()),
                delta_i3net_minus_past=float(d.mean()),ci95=np.quantile(d[draws].mean(1),[.025,.975]).tolist(),
                i3net_patient_wins=int(((d>0) if higher else (d<0)).sum()))
        hard=y.nsmallest(int(np.ceil(len(y)/4)),'psnr').index
        result.update(patients=len(x),paired_metrics=metrics,
            control_worst_quartile_delta=float((x.loc[hard,'psnr']-y.loc[hard,'psnr']).mean()),
            bootstrap='10000 patient resamples, one seed; no across-training-seed uncertainty',
            i3net_efficiency=json.loads((a.run/'efficiency.json').read_text()),
            control_efficiency=json.loads((a.control/'efficiency.json').read_text()),
            sota_claim=False)
    write_json(a.out,result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
