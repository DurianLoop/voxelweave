"""Standalone audit figures, fixed validation case; no case cherry-picking."""
import json
import numpy as np
import pandas as pd
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from .common import PACKAGE
from .data import IntervalDataset,device_batch
from .run import load_model,seed_all


def main():
    out=PACKAGE/'results/figures';out.mkdir(exist_ok=True)
    df=pd.read_csv(PACKAGE/'results/audit_validation/per_slice.csv')
    g=df[df.method=='g086']
    fig,axs=plt.subplots(1,3,figsize=(13,3.7),layout='constrained')
    axs[0].boxplot([g[g.phase==q].groupby('case_id').psnr.mean() for q in (.25,.5,.75)],tick_labels=['0.25','0.50','0.75'])
    axs[0].set(title='G086 phase error (23 validation series)',xlabel='Query phase',ylabel='PSNR (dB)')
    energies=g[['low_mse','mid_mse','high_mse']].mean().to_numpy()
    axs[1].bar(['Low','Mid','High'],100*energies/energies.sum(),color=['#275dad','#e6a141','#5b9e72'])
    axs[1].set(title='Orthogonal FFT error energy',ylabel='Share (%)')
    tail=g.groupby('case_id').tail10_energy_share.mean()
    axs[2].hist(100*tail,bins=8,color='#275dad');axs[2].set(title='Worst 10% pixel contribution',xlabel='MSE energy share (%)',ylabel='Series count')
    fig.savefig(out/'validation_error_distribution.png',dpi=180);plt.close(fig)
    seed_all(3407);device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    ds=IntervalDataset(PACKAGE/'manifests/fastmri/fold_00.json','val',limit=1)
    batch=device_batch(next(iter(DataLoader(ds,batch_size=1))),device)
    model=load_model('control').to(device).eval()
    with torch.no_grad(),torch.autocast(device.type,enabled=device.type=='cuda'):
        pred=model(batch).float()[0,1,0].cpu().numpy()
    target=batch['target'][0,1,0].cpu().numpy();coarse=batch['cond'][0,1,4].cpu().numpy()
    error=pred-target
    fig,axs=plt.subplots(1,4,figsize=(13,3.6),layout='constrained')
    for ax,x,title,cmap in zip(axs,[target,coarse,pred,np.abs(error)],['Target','Observed linear coarse','Frozen G086','Absolute error'],['gray']*3+['magma']):
        ax.imshow(x,cmap=cmap,vmin=0,vmax=.3 if cmap=='magma' else 1);ax.set_title(title);ax.axis('off')
    fig.suptitle('Fixed first validation series, z=2; observed-only normalization')
    fig.savefig(out/'fixed_validation_case.png',dpi=180);plt.close(fig)


if __name__=='__main__':
    main()
