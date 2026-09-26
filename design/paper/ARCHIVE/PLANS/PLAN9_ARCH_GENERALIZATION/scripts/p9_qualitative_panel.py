"""Generate the frozen-rule Plan-9 qualitative P0 architecture panel."""
from __future__ import annotations
import gc
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import torch

HERE=Path(__file__).resolve();P9=HERE.parents[1];PAPER=P9.parent;ROOT=PAPER.parents[1];OUT=P9/'outputs';FIG=P9/'figures'
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'pre'),str(ROOT/'design'),str(ROOT)]
from p9_disjoint_shared import load_interpolator

def select():
 x=pd.read_csv(OUT/'p9_disjoint_shared_per_plane.csv');x=x[x.condition=='shared'].copy()
 x['error_percentile']=x.groupby('model').paired_error_mae.rank(pct=True)
 q=x.groupby(['case','target_z'],as_index=False).agg(stable_wrong_models=('stable_wrong','sum'),mean_error_percentile=('error_percentile','mean'))
 q=q.sort_values(['stable_wrong_models','mean_error_percentile','case','target_z'],ascending=[False,False,True,True])
 q.to_csv(OUT/'p9_qualitative_selection_ranking.csv',index=False)
 return q.iloc[0]

def main():
 s=select();case=str(s.case);z=int(s.target_z);fn=case+'.nii.gz'
 full=nib.load(str(ROOT/'dataset/fastMRI_brain_T2/processed/nifti'/fn)).get_fdata(dtype=np.float32)
 a0=np.ascontiguousarray(full[:,:,[0,4,8,12]]);a2=np.ascontiguousarray(full[:,:,[2,6,10,14]])
 target=full[:,:,z];mask=np.abs(target)>.01*max(float(np.max(np.abs(target))),1e-6)
 ys,xs=np.where(mask);pad=10;y0=max(0,ys.min()-pad);y1=min(target.shape[0],ys.max()+pad+1);x0=max(0,xs.min()-pad);x1=min(target.shape[1],xs.max()+pad+1)
 data={}
 for model in ['i3net','saint','cycleinr']:
  net=load_interpolator(model,'cuda');p0=net.interpolate_volume(a0,stride=4)[:,:,z]
  ps=net.interpolate_volume(np.ascontiguousarray(a0[::-1,:,:]),stride=4)[::-1,:,z]
  pdisjoint=net.interpolate_volume(a2,stride=4)[:,:,z-2]
  data[model]=(p0,np.abs(p0-target),np.abs(p0-ps),np.abs(p0-pdisjoint))
  del net;gc.collect();torch.cuda.empty_cache()
 vmax_img=float(np.percentile(target[mask],99.5));vmax_err=float(np.percentile(np.concatenate([v[1][mask] for v in data.values()]),99))
 vmax_dis=float(np.percentile(np.concatenate([v[j][mask] for v in data.values() for j in (2,3)]),99))
 fig,axs=plt.subplots(3,5,figsize=(11.2,6.6))
 for r,(model,vals) in enumerate(data.items()):
  panels=[target,vals[0],vals[1],vals[2],vals[3]];cmaps=['gray','gray','magma','viridis','viridis'];vmaxs=[vmax_img,vmax_img,vmax_err,vmax_dis,vmax_dis]
  for c,(im,cm,vm) in enumerate(zip(panels,cmaps,vmaxs)):
   axs[r,c].imshow(im[y0:y1,x0:x1],cmap=cm,vmin=0,vmax=vm);axs[r,c].axis('off')
  axs[r,0].set_ylabel({'i3net':'I3Net','saint':'SAINT','cycleinr':'CycleINR'}[model],fontsize=11)
 titles=['Target','Reference prediction','Reference |error|','Shared-control |difference|','Disjoint-context |difference|']
 for c,t in enumerate(titles):axs[0,c].set_title(t,fontsize=9)
 fig.suptitle(f'Frozen data-rule example: {case}, target z={z} (stable-wrong marks={int(s.stable_wrong_models)}/3)',fontsize=11)
 fig.tight_layout(rect=[0,0,1,.95]);FIG.mkdir(parents=True,exist_ok=True)
 fig.savefig(FIG/'p9_qualitative_generalization.pdf',bbox_inches='tight');fig.savefig(FIG/'p9_qualitative_generalization.png',dpi=300,bbox_inches='tight');plt.close(fig)
 pd.DataFrame([{'case':case,'target_z':z,'stable_wrong_models':int(s.stable_wrong_models),'mean_error_percentile':float(s.mean_error_percentile),
                'selection_rule':'QUALITATIVE_SELECTION_RULE.md'}]).to_csv(OUT/'p9_qualitative_selected_case.csv',index=False)
 print(case,z,int(s.stable_wrong_models),float(s.mean_error_percentile))
if __name__=='__main__':main()
