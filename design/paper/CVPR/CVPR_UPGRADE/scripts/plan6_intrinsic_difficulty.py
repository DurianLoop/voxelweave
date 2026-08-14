"""P6-E08: architecture-independent case difficulty and held-out explanation."""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];OUT=UP/'outputs'

FEATURES={
 'anchor_cv_only':['anchor_cv'],
 'direct_acquired':['spacing_mm','adjacent_mae','adjacent_gradient_mae','adjacent_lowfreq_mae','adjacent_highfreq_mae','first_difference_variability'],
 'all_acquired':['anchor_cv','spacing_mm','adjacent_mae','adjacent_gradient_mae','adjacent_lowfreq_mae','adjacent_highfreq_mae','first_difference_variability'],
}

def rho(x,y):return float(stats.spearmanr(x,y).statistic)

def loco_ridge(g,features):
    # Freeze alpha=10; all preprocessing is fit inside each held-out cluster split.
    pred=np.full(len(g),np.nan);base=np.full(len(g),np.nan)
    for cl in g.patient_cluster.unique():
        te=g.patient_cluster==cl;tr=~te
        xtr=g.loc[tr,features].to_numpy(float);xte=g.loc[te,features].to_numpy(float);ytr=g.loc[tr,'mean_error'].to_numpy(float)
        med=np.nanmedian(xtr,axis=0);xtr=np.where(np.isfinite(xtr),xtr,med);xte=np.where(np.isfinite(xte),xte,med)
        mu=xtr.mean(axis=0);sd=xtr.std(axis=0);sd[sd<1e-9]=1
        xtr=np.column_stack([np.ones(tr.sum()),(xtr-mu)/sd]);xte=np.column_stack([np.ones(te.sum()),(xte-mu)/sd])
        penalty=np.eye(xtr.shape[1])*10.0;penalty[0,0]=0
        coef=np.linalg.solve(xtr.T@xtr+penalty,xtr.T@ytr)
        pred[te]=xte@coef;base[te]=ytr.mean()
    y=g.mean_error.to_numpy(float);sse=float(np.sum((y-pred)**2));sst=float(np.sum((y-base)**2))
    return {'loco_r2_vs_training_mean':1-sse/sst if sst else np.nan,'loco_spearman':rho(pred,y),'mae':float(np.mean(np.abs(pred-y))),'n':len(y)}

x=pd.read_csv(OUT/'plan6_anchor_cv_explanation_per_case.csv')
# Predict a case-level latent outcome rather than duplicating identical acquired features across architectures.
case=x.groupby(['dataset','case','patient_cluster'],as_index=False).agg(mean_error=('x4_error','mean'),**{c:(c,'first') for c in set(sum(FEATURES.values(),[]))})
rows=[];pred=[]
for ds,g in x.groupby('dataset'):
    wide=g.pivot(index='case',columns='model',values='x4_error').dropna()
    cross=rho(wide['hat'],wide['swinir'])
    # Fixed-effect sums of squares; case is entered before architecture.
    y=g.x4_error.to_numpy(float);grand=y.mean();ss_total=float(np.sum((y-grand)**2))
    case_mean=g.groupby('case').x4_error.transform('mean').to_numpy();ss_case=float(np.sum((case_mean-grand)**2))
    resid_after_case=y-case_mean
    arch_adjust=g.assign(resid_after_case=resid_after_case).groupby('model').resid_after_case.transform('mean').to_numpy()
    ss_arch=float(np.sum(arch_adjust**2));ss_res=max(0.,ss_total-ss_case-ss_arch)
    rows.append({'dataset':ds,'cases':wide.shape[0],'patient_clusters':g.patient_cluster.nunique(),'cross_architecture_spearman':cross,
                 'case_ss_fraction':ss_case/ss_total,'architecture_ss_fraction_after_case':ss_arch/ss_total,'residual_ss_fraction':ss_res/ss_total})
    cg=case[case.dataset==ds].reset_index(drop=True)
    for name,features in FEATURES.items():pred.append({'dataset':ds,'feature_block':name,**loco_ridge(cg,features)})

variance=pd.DataFrame(rows);prediction=pd.DataFrame(pred)
variance.to_csv(OUT/'plan6_intrinsic_difficulty_variance.csv',index=False);prediction.to_csv(OUT/'plan6_intrinsic_difficulty_loco.csv',index=False)
payload={'experiment':'P6-E08','status':'COMPLETE','coverage':['fastmri','ixi','ningxia'],'architectures':['hat','swinir'],
 'factor_scope':'x4 only because IXI has no completed definition-matched x2/x6 outputs at analysis time',
 'model':'leave-one-patient/examination-cluster-out ridge, frozen alpha=10; training-fold standardization',
 'variance_csv':'plan6_intrinsic_difficulty_variance.csv','prediction_csv':'plan6_intrinsic_difficulty_loco.csv'}
(OUT/'plan6_intrinsic_difficulty.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(variance.to_string(index=False));print(prediction.to_string(index=False));print(json.dumps(payload,indent=2))
