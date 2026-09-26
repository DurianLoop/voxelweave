"""Objective selection followed by CPU float32 inference; no generated anatomy."""
import os
os.environ.setdefault('OMP_NUM_THREADS','2');os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from common import *
import sys,time
import nibabel as nib
import torch
from skimage.transform import resize
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'pre'),str(ROOT/'design')]
from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator,normalize_volume
def main():
 df=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN9_ARCH_GENERALIZATION/outputs/p9_disjoint_shared_per_plane_transformer_reference.csv')
 x=df[df.model=='swinir'].pivot(index=['case','target_z'],columns='condition',values='observable_error_fraction')
 x['gain']=x.disjoint-x.shared;means=x.groupby('case').gain.mean().sort_values(kind='stable')
 rank=means.reset_index().sort_values(['gain','case']);rank.to_csv(OUT/'qualitative_case_ranking.csv',index=False)
 c=rank.iloc[(len(rank)-1)//2]['case'];g=x.loc[c];z=int((g.gain-means[c]).abs().sort_index().idxmin())
 other=sorted(set(rank.case)-{c});rc=str(np.random.default_rng(SEED).choice(other))
 selection=[{'role':'main_median','case':c,'z':z},{'role':'supplement_seeded_random','case':rc,'z':7}]
 save('qualitative_selection_before_inference.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':sha(P/'PROTOCOL.md'),'model':'swinir','selection':selection})
 torch.set_num_threads(2);sp=specs()[('fastmri','swinir')];net=FastMRISwinIR2p5DInterpolator(ROOT/sp['checkpoint'],device='cpu')
 def predict(anchors,z):
  norm,lo,hi=normalize_volume(anchors);idx=z//4;offset=z%4;u=offset/4
  l=resize(norm[:,:,idx],net.input_size,preserve_range=True,anti_aliasing=True).astype(np.float32)
  r=resize(norm[:,:,idx+1],net.input_size,preserve_range=True,anti_aliasing=True).astype(np.float32)
  coarse=((1-u)*l+u*r).astype(np.float32)
  cond=np.stack([l,r,coarse,np.full(net.input_size,u,np.float32)])
  q=np.clip(coarse+net._predict_residual(cond),0,1)
  return resize(q,anchors.shape[:2],preserve_range=True,anti_aliasing=True)*(hi-lo)+lo
 results=[];t=time.perf_counter()
 for s in selection:
  path=ROOT/'dataset/fastMRI_brain_T2/processed/nifti'/(s['case']+'.nii.gz');v=nib.load(path).get_fdata(dtype=np.float32);z=s['z']
  a0=np.ascontiguousarray(v[:,:,[0,4,8,12]]);a2=np.ascontiguousarray(v[:,:,[2,6,10,14]])
  a=predict(a0,z);b=predict(np.ascontiguousarray(a0[::-1,:,:]),z)[::-1,:];d=predict(a2,z-2);y=v[:,:,z]
  stored=nib.load(ROOT/sp['stored_predictions']/('diff_'+path.name)).get_fdata(dtype=np.float32)[:,:,z]
  m=fg(y);rr={'selection':s,'source_sha256':sha(path),'checkpoint_sha256':sp['sha256'],'cpu_vs_stored_max_abs':float(abs(a-stored).max()),'cpu_vs_stored_mae':float(abs(a-stored).mean()),'shared':metrics(a,b,y,m),'disjoint':metrics(a,d,y,m)}
  for cond in ['shared','disjoint']:
   row=df[(df.case==s['case'])&(df.target_z==z)&(df.model=='swinir')&(df.condition==cond)].iloc[0]
   rr[cond]['historical_observable']=float(row.observable_error_fraction)
  np.savez_compressed(OUT/(s['role']+'_real_arrays.npz'),gt=y,a=a,b_shared=b,b_disjoint=d,mask=m)
  results.append(rr);print(s,rr['cpu_vs_stored_max_abs'],'elapsed',time.perf_counter()-t,flush=True)
 save('qualitative_inference.json',{'records':results,'precision':'CPU float32; historical GPU uses mixed precision','elapsed_seconds':time.perf_counter()-t,'protocol_sha256':sha(P/'PROTOCOL.md')})
if __name__=='__main__':main()
