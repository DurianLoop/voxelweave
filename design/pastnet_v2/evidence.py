"""Recompute historical paired evidence, with development-test labels preserved."""
from pathlib import Path
import numpy as np
import pandas as pd
from .common import ROOT,PACKAGE,sha256,write_json


def main():
    runs=ROOT/'design/fastmri_brain_pastnet_2p5d/runs'
    names=dict(g078='full_pastnet_g078_latent_multiscale160',g079='full_pastnet_g079_tail_aware160',
               g084='full_pastnet_g084_dual_domain140',g086='full_pastnet_g086_dual_restart60')
    tables={};summary={}
    for key,name in names.items():
        directory=runs/name/'metrics'
        path=directory/'per_case_metrics.csv'
        df=pd.read_csv(path)
        # Existing files include interpolation baselines alongside PAST-Net.
        if 'method' in df:
            df=df[df.method.str.startswith('pastnet')]
        case_column=next(k for k in ('case','case_id','filename') if k in df.columns)
        tables[key]=df.set_index(case_column).sort_index()
        summary[key]=dict(path=str(directory),per_case_sha256=sha256(path),
                         summary=pd.read_csv(directory/'summary_metrics.csv').to_dict('records'))
    rng=np.random.default_rng(73019);paired={}
    for candidate,parent in (('g079','g078'),('g084','g079'),('g086','g084')):
        c,b=tables[candidate],tables[parent]
        if not c.index.equals(b.index):
            raise ValueError('Historical cases do not match')
        d=(c.psnr-b.psnr).to_numpy()
        draws=d[rng.integers(0,len(d),(10000,len(d)))].mean(1)
        paired[candidate+'_vs_'+parent]=dict(n=len(d),mean_delta=float(d.mean()),
            ci95=np.quantile(draws,[.025,.975]).tolist(),wins=int((d>0).sum()),
            mae_delta=float((c.mae-b.mae).mean()),mse_delta=float((c.mse-b.mse).mean()))
    out=PACKAGE/'results/historical_evidence.json'
    if out.exists():
        raise FileExistsError(out)
    write_json(out,dict(status='reused development test; descriptive evidence, not independent confirmation',
                        frozen_metrics=summary,paired=paired,
                        ixi_g086_full_checkpoint_exists=(ROOT/'design/ixi_pastnet_2p5d/runs/full_g086_dual_interval160_test115/checkpoints/pastnet_epoch_best.pth').exists()))
    print(paired)


if __name__=='__main__':
    main()
