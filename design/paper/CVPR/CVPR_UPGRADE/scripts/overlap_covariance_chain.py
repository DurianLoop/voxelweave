"""C5-E002: paired overlap -> error alignment -> observability chain.

Case eligibility and source paths are read from DATA_MANIFEST.csv. Dense targets
are used only for evaluation. The reliability score remains prediction-only.
"""
from __future__ import annotations
import json,sys
import argparse
from pathlib import Path
import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats

HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];ROOT=PAPER.parents[1];OUT=UP/'outputs'
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'design'),str(ROOT/'pre')]

def make_model(dataset,target,checkpoint):
 if dataset=='fastmri':
  if target=='hat':
   from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator;return FastMRIHAT2p5DInterpolator(checkpoint)
  from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator;return FastMRISwinIR2p5DInterpolator(checkpoint)
 if target=='hat':
  from ixi_hat_2p5d.train import HAT2p5DInterpolator;return HAT2p5DInterpolator(checkpoint)
 from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator;return SwinIR2p5DInterpolator(checkpoint)

def rho(a,b):return float(stats.spearmanr(a,b).statistic) if len(a)>3 and np.std(a)>0 and np.std(b)>0 else float('nan')
def plane_metrics(a,b,y,mask):
 e1=(a-y)[mask].astype(np.float64);e2=(b-y)[mask].astype(np.float64);dot=float(e1@e2);n1=float(e1@e1);n2=float(e2@e2)
 total=.5*(n1+n2);shared=float(np.sum(((e1+e2)/2)**2));div=float(np.sum(((e1-e2)/2)**2))
 return {'error_cosine':dot/np.sqrt(n1*n2) if n1*n2>0 else np.nan,'error_covariance':float(np.mean((e1-e1.mean())*(e2-e2.mean()))),
  'mean_mse':total/len(e1),'shared_mse':shared/len(e1),'diversity_mse':div/len(e1),
  'shared_fraction':shared/total if total>0 else np.nan,'observable_fraction':div/total if total>0 else np.nan,
  'mae':float(.5*(np.abs(e1).mean()+np.abs(e2).mean())),'disagreement_mae':float(np.abs(e1-e2).mean())}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',default='all');a=ap.parse_args()
 OUT.mkdir(exist_ok=True);manifest=pd.read_csv(UP/'DATA_MANIFEST.csv');m=manifest[(manifest.factor.eq(4))&manifest.architecture.isin(['hat','swinir'])]
 if a.dataset!='all':m=m[m.dataset.eq(a.dataset)]
 rows=[]
 for (ds,model,split),group in m.groupby(['dataset','architecture','split']):
  if ds=='fastmri':checkpoint=ROOT/'baseline'/('fastmri_brain_'+('hat_2p5d' if model=='hat' else 'swinir_2p5d'))/'runs'/'full'/'checkpoints'/f'{model}_epoch_best.pth'
  elif ds=='ningxia':checkpoint=ROOT/'baseline'/f'ningxia_t2_{model}_2p5d_cv'/'runs'/split.replace('OOF_','')/'full'/'checkpoints'/f'{model}_epoch_best.pth'
  else:
   checkpoint=ROOT/'baseline'/f'ixi_{model}_2p5d'/'runs'/'full_test115'/'checkpoints'/f'{model}_epoch_best.pth'
   if not checkpoint.exists():checkpoint=ROOT/'baseline'/f'ixi_{model}_2p5d'/'runs'/'full'/'checkpoints'/f'{model}_epoch_best.pth'
  net=make_model(ds,model,checkpoint)
  for r in group.itertuples():
   gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32);p0=nib.load(r.source_file).get_fdata(dtype=np.float32)
   p2local=net.interpolate_volume(np.ascontiguousarray(gt[:,:,2::4]),stride=4)
   prev=net.interpolate_volume(np.ascontiguousarray(gt[:,:,::4][:,:,::-1]),stride=4)[:,:,::-1]
   usable=min(gt.shape[2],p0.shape[2],prev.shape[2],p2local.shape[2]+2)
   for z in range(2,usable):
    if z%4 not in (1,3):continue
    pred0=p0[:,:,z];y=gt[:,:,z];thr=.01*max(float(np.max(np.abs(pred0))),1e-6);mask=np.abs(pred0)>thr
    rows.append({'dataset':ds,'case_id':r.case_id,'patient_cluster':r.patient_cluster,'model':model,'z':z,'overlap':0,'condition':'disjoint_phase',**plane_metrics(pred0,p2local[:,:,z-2],y,mask)})
    rows.append({'dataset':ds,'case_id':r.case_id,'patient_cluster':r.patient_cluster,'model':model,'z':z,'overlap':2,'condition':'max_shared_reversal',**plane_metrics(pred0,prev[:,:,z],y,mask)})
   print('C5-E002',ds,model,r.case_id,flush=True)
 x=pd.DataFrame(rows);x.to_csv(OUT/(f'overlap_covariance_{a.dataset}_per_plane.csv' if a.dataset!='all' else 'overlap_covariance_per_plane.csv'),index=False)
 keys=['dataset','case_id','patient_cluster','model','z'];z=x[x.overlap.eq(0)].set_index(keys);h=x[x.overlap.eq(2)].set_index(keys);paired=z.join(h,lsuffix='_zero',rsuffix='_max').reset_index()
 rng=np.random.default_rng(20260813);summ=[]
 outcomes=['error_cosine','error_covariance','shared_fraction','observable_fraction','disagreement_mae']
 for ds,g in paired.groupby('dataset'):
  clusters=np.array(sorted(g.patient_cluster.unique()));by={c:g[g.patient_cluster.eq(c)] for c in clusters}
  rec={'dataset':ds,'cases':g.case_id.nunique(),'patient_clusters':len(clusters),'planes':len(g)}
  for v in outcomes:
   delta=float((g[f'{v}_max']-g[f'{v}_zero']).mean());boots=[]
   for _ in range(5000):
    b=pd.concat([by[c] for c in rng.choice(clusters,len(clusters),replace=True)],ignore_index=True);boots.append(float((b[f'{v}_max']-b[f'{v}_zero']).mean()))
   rec[v]={'max_minus_zero':delta,'cluster_95ci':[float(np.quantile(boots,.025)),float(np.quantile(boots,.975))],
           'zero_mean':float(g[f'{v}_zero'].mean()),'max_mean':float(g[f'{v}_max'].mean())}
  rec['reliability_rho_zero']=rho(g.disagreement_mae_zero,g.mae_zero);rec['reliability_rho_max']=rho(g.disagreement_mae_max,g.mae_max)
  rec['reliability_delta_zero_minus_max']=rec['reliability_rho_zero']-rec['reliability_rho_max']
  summ.append(rec)
 out={'experiment':'C5-E002','status':'EXPLORATORY MECHANISTIC','identity_max_abs_residual':float(np.max(np.abs(x.mean_mse-x.shared_mse-x.diversity_mse))),
      'causal_prediction':{'overlap_up':'error alignment/shared fraction up; observable fraction and reliability ranking down'},'rows':summ}
 (OUT/(f'overlap_covariance_{a.dataset}_summary.json' if a.dataset!='all' else 'overlap_covariance_summary.json')).write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
