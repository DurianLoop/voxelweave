"""P6-E04: neural finite-difference shared influence, gate and confirmation."""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from skimage.transform import resize
import torch

HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];ROOT=PAPER.parents[1];OUT=UP/'outputs'
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'design'),str(ROOT/'pre')]
REF=(-2,2);CONTEXTS=[(-2,2),(-2,1),(-2,3),(-1,2),(-3,2),(-1,1),(-1,3),(-3,1),(-3,3)];SEEDS=(6101,6102,6103,6104)

def rho(a,b):
 a=np.asarray(a,float);b=np.asarray(b,float);ok=np.isfinite(a)&np.isfinite(b)
 return float(stats.spearmanr(a[ok],b[ok]).statistic) if ok.sum()>4 and np.std(a[ok])>0 and np.std(b[ok])>0 else float('nan')

def partial_spearman(x,y,controls):
 """Rank-residual correlation; controls may include numeric and dummy columns."""
 x=np.asarray(x,float);y=np.asarray(y,float);c=np.asarray(controls,float)
 ok=np.isfinite(x)&np.isfinite(y)&np.all(np.isfinite(c),axis=1)
 if ok.sum()<8:return float('nan')
 rx=stats.rankdata(x[ok]);ry=stats.rankdata(y[ok]);cc=c[ok]
 cc=np.column_stack([stats.rankdata(cc[:,j]) for j in range(cc.shape[1])])
 design=np.column_stack([np.ones(ok.sum()),cc])
 ex=rx-design@np.linalg.lstsq(design,rx,rcond=None)[0]
 ey=ry-design@np.linalg.lstsq(design,ry,rcond=None)[0]
 return float(np.corrcoef(ex,ey)[0,1]) if np.std(ex)>0 and np.std(ey)>0 else float('nan')

def checkpoint(r,model):
 if r.dataset=='fastmri':return ROOT/'baseline'/f'fastmri_brain_{model}_2p5d'/'runs'/'full'/'checkpoints'/f'{model}_epoch_best.pth'
 if r.dataset=='ixi':
  q=ROOT/'baseline'/f'ixi_{model}_2p5d'/'runs'/'full_test115'/'checkpoints'/f'{model}_epoch_best.pth'
  return q if q.exists() else ROOT/'baseline'/f'ixi_{model}_2p5d'/'runs'/'full'/'checkpoints'/f'{model}_epoch_best.pth'
 return ROOT/'baseline'/f'ningxia_t2_{model}_2p5d_cv'/'runs'/str(r.split).replace('OOF_','')/'full'/'checkpoints'/f'{model}_epoch_best.pth'

def load_net(ds,model,ck,device):
 if ds=='fastmri':
  if model=='hat':
   from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator as C
  else:
   from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator as C
 elif model=='hat':
  from ixi_hat_2p5d.train import HAT2p5DInterpolator as C
 else:
  from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator as C
 return C(ck,device=device)

def batch_residual(net,conds):
 t=torch.from_numpy(np.stack(conds)).float().to(net.device)
 if net.device.type=='cuda':t=t.contiguous(memory_format=torch.channels_last)
 with torch.no_grad(),torch.amp.autocast(device_type=net.device.type,enabled=net.device.type=='cuda'):
  q=net.model(t).float().clamp(-1,1)
 return q[:,0].cpu().numpy()

def prepare_cond(norm,z,ctx,perturb_anchor=None,patterns=None,eps=.01):
 l=resize(norm[:,:,z+ctx[0]],(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32)
 r=resize(norm[:,:,z+ctx[1]],(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32)
 rel=float(-ctx[0])/(ctx[1]-ctx[0]);out=[]
 pats=[None] if patterns is None else patterns
 for p in pats:
  ll=l.copy();rr=r.copy()
  if perturb_anchor==ctx[0]:ll=np.clip(ll+eps*p,0,1)
  if perturb_anchor==ctx[1]:rr=np.clip(rr+eps*p,0,1)
  coarse=(1-rel)*ll+rel*rr
  out.append(np.stack([ll,rr,coarse,np.full((256,256),rel,np.float32)]))
 return out

def metrics(a,b,y,mask):
 ea=(a-y)[mask].astype(float);eb=(b-y)[mask].astype(float);n1=ea@ea;n2=eb@eb;tot=.5*(n1+n2);sh=np.sum(((ea+eb)/2)**2);ob=np.sum(((ea-eb)/2)**2)
 return {'error_cosine':float(ea@eb/np.sqrt(n1*n2)),'shared_fraction':float(sh/tot),'observable_fraction':float(ob/tot),'disagreement_mae':float(np.abs(a-b)[mask].mean()),'paired_error_mae':float(.5*(np.abs(ea).mean()+np.abs(eb).mean()))}

def one_case(net,gt,z):
 lo=float(np.nanmin(gt));hi=float(np.nanmax(gt));norm=((gt-lo)/(hi-lo+1e-8)).astype(np.float32);y=gt[:,:,z];mask=np.abs(y)>.01*max(float(np.max(np.abs(y))),1e-6)
 patterns=[]
 for seed in SEEDS:
  p=np.random.default_rng(seed).choice([-1.,1.],size=(256,256)).astype(np.float32);p-=p.mean();patterns.append(p)
 preds={};responses={}
 for ctx in CONTEXTS:
  base_cond=prepare_cond(norm,z,ctx)[0];base_res=batch_residual(net,[base_cond])[0];coarse=base_cond[2];base=np.clip(coarse+base_res,0,1);preds[ctx]=resize(base,gt.shape[:2],preserve_range=True,anti_aliasing=True)*(hi-lo)+lo
  responses[ctx]={}
  for anchor in ctx:
   conds=prepare_cond(norm,z,ctx,perturb_anchor=anchor,patterns=patterns);rr=batch_residual(net,conds);vec=[]
   for cond,res in zip(conds,rr):
    q=np.clip(cond[2]+res,0,1);q=resize(q,gt.shape[:2],preserve_range=True,anti_aliasing=True)*(hi-lo)+lo;vec.append((q-preds[ctx])[mask].astype(np.float32))
   responses[ctx][z+anchor]=vec
 rows=[]
 for ctx in CONTEXTS:
  dots=0.;na=0.;nb=0.;common=0.
  for seed_i in range(len(SEEDS)):
   for v in responses[REF].values():na+=float(v[seed_i]@v[seed_i])
   for v in responses[ctx].values():nb+=float(v[seed_i]@v[seed_i])
   for pos in set(responses[REF])&set(responses[ctx]):
    a=responses[REF][pos][seed_i];b=responses[ctx][pos][seed_i];dots+=float(a@b);common+=min(float(np.linalg.norm(a)),float(np.linalg.norm(b)))
  influence=dots/np.sqrt(na*nb) if na*nb>0 else 0.;mass=common/(.5*(np.sqrt(na)+np.sqrt(nb))) if na+nb>0 else 0.
  rows.append({'context':str(ctx),'left_offset':ctx[0],'right_offset':ctx[1],'span':ctx[1]-ctx[0],'asymmetry':abs(ctx[0]+ctx[1]),'overlap_count':len(set(REF)&set(ctx)),'neural_influence_cosine':influence,'neural_common_response_mass':mass,**metrics(preds[REF],preds[ctx],y,mask)})
 return rows

def summarize(x):
 endpoints=['error_cosine','shared_fraction','observable_fraction','disagreement_mae'];out=[];rng=np.random.default_rng(20260813)
 for (ds,model),g in x.groupby(['dataset','model']):
  rec={'dataset':ds,'model':model,'cases':int(g.case.nunique()),'planes':int(g[['case','z']].drop_duplicates().shape[0]),'clusters':int(g.patient_cluster.nunique()),'associations':[]}
  case_dummies=pd.get_dummies(g.case,drop_first=True,dtype=float).to_numpy()
  geometry=np.column_stack([g.overlap_count,g.span,g.asymmetry,case_dummies])
  distance_case=np.column_stack([g.span,g.asymmetry,case_dummies])
  for y in endpoints:
   rec['associations'].append({'endpoint':y,'rho_overlap':rho(g.overlap_count,g[y]),'rho_neural_influence':rho(g.neural_influence_cosine,g[y]),'rho_common_response_mass':rho(g.neural_common_response_mass,g[y]),'partial_rho_overlap_given_distance_and_case':partial_spearman(g.overlap_count,g[y],distance_case),'partial_rho_influence_given_geometry_and_case':partial_spearman(g.neural_influence_cosine,g[y],geometry)})
  clusters=g.patient_cluster.unique();by={c:g[g.patient_cluster==c] for c in clusters};adv={y:[] for y in endpoints}
  for _ in range(2000):
   b=pd.concat([by[c] for c in rng.choice(clusters,len(clusters),replace=True)],ignore_index=True)
   for y in endpoints:adv[y].append(abs(rho(b.neural_influence_cosine,b[y]))-abs(rho(b.overlap_count,b[y])))
  rec['cluster_95ci_abs_rho_advantage']={y:[float(np.nanquantile(v,.025)),float(np.nanquantile(v,.975))] for y,v in adv.items()};out.append(rec)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--max-cases-per-dataset',type=int);ap.add_argument('--device',default='cuda');ap.add_argument('--suffix',default='');ap.add_argument('--dataset',default='all');ap.add_argument('--planes-per-case',type=int,default=1);a=ap.parse_args()
 m=pd.read_csv(UP/'DATA_MANIFEST.csv');m=m[(m.factor==4)&m.architecture.isin(['hat','swinir'])]
 if a.dataset!='all':m=m[m.dataset==a.dataset]
 if a.max_cases_per_dataset:m=m.groupby(['dataset','architecture'],group_keys=False).head(a.max_cases_per_dataset)
 nets={};rows=[];t0=time.perf_counter()
 for i,r in enumerate(m.itertuples(),1):
  ck=checkpoint(r,r.architecture);key=(r.dataset,r.architecture,str(ck));
  if key not in nets:nets[key]=load_net(r.dataset,r.architecture,ck,a.device)
  gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32);lo=3;hi=gt.shape[2]-4
  zs=sorted(set(int(round(v)) for v in np.linspace(lo,hi,a.planes_per_case+2)[1:-1]))
  tt=time.perf_counter()
  for z in zs:
   q=one_case(nets[key],gt,z)
   for v in q:rows.append({'dataset':r.dataset,'case':r.case_id,'patient_cluster':r.patient_cluster,'model':r.architecture,'z':z,**v})
  print(f'P6-E04 {i}/{len(m)} {r.dataset} {r.architecture} {r.case_id} planes={len(zs)} {time.perf_counter()-tt:.2f}s',flush=True)
 x=pd.DataFrame(rows);suffix=('_'+a.suffix) if a.suffix else '';x.to_csv(OUT/f'plan6_neural_shared_influence{suffix}_per_case_config.csv',index=False);status='PILOT' if a.max_cases_per_dataset else ('CENTRAL-PLANE GATE' if a.planes_per_case==1 else 'THREE-PLANE CONFIRMATION');payload={'experiment':'P6-E04','status':status,'device':a.device,'planes_per_case':a.planes_per_case,'elapsed_seconds':time.perf_counter()-t0,'rows':summarize(x)};(OUT/f'plan6_neural_shared_influence{suffix}_summary.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
