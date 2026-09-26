"""P6-E10: measured score and reconstruction cost on all three cohorts."""
from __future__ import annotations
import json,sys,time
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
import torch

HERE=Path(__file__).resolve();UP=HERE.parents[1];PAPER=HERE.parents[3];ROOT=PAPER.parents[1];OUT=UP/'outputs'
sys.path[:0]=[str(ROOT/'baseline'),str(ROOT/'design'),str(ROOT/'pre')]

def checkpoint(r,model):
 if r.dataset=='fastmri':return ROOT/'baseline'/f'fastmri_brain_{model}_2p5d'/'runs'/'full'/'checkpoints'/f'{model}_epoch_best.pth'
 if r.dataset=='ixi':
  p=ROOT/'baseline'/f'ixi_{model}_2p5d'/'runs'/'full_test115'/'checkpoints'/f'{model}_epoch_best.pth';return p if p.exists() else ROOT/'baseline'/f'ixi_{model}_2p5d'/'runs'/'full'/'checkpoints'/f'{model}_epoch_best.pth'
 return ROOT/'baseline'/f'ningxia_t2_{model}_2p5d_cv'/'runs'/str(r.split).replace('OOF_','')/'full'/'checkpoints'/f'{model}_epoch_best.pth'
def load_net(ds,model,ck):
 if ds=='fastmri':
  if model=='hat':from fastmri_brain_hat_2p5d.train import FastMRIHAT2p5DInterpolator as C
  else:from fastmri_brain_swinir_2p5d.train import FastMRISwinIR2p5DInterpolator as C
 elif model=='hat':from ixi_hat_2p5d.train import HAT2p5DInterpolator as C
 else:from ixi_swinir_2p5d.train import SwinIR2p5DInterpolator as C
 return C(ck,device='cuda')
def sync():
 if torch.cuda.is_available():torch.cuda.synchronize()
def timed(fn,reps=3):
 fn();sync();vals=[];peak=[]
 for _ in range(reps):
  if torch.cuda.is_available():torch.cuda.reset_peak_memory_stats()
  sync();t=time.perf_counter();fn();sync();vals.append((time.perf_counter()-t)*1000)
  peak.append(torch.cuda.max_memory_allocated()/2**20 if torch.cuda.is_available() else np.nan)
 return float(np.median(vals)),float(np.percentile(vals,95)),float(max(peak))
def cpu_timed(fn,reps=100):
 fn();vals=[]
 for _ in range(reps):t=time.perf_counter();fn();vals.append((time.perf_counter()-t)*1000)
 return float(np.median(vals)),float(np.percentile(vals,95))
def mask(v):return np.abs(v)>.01*max(float(np.max(np.abs(v))),1e-6)
def anchor_cv(v):
 a=list(range(0,v.shape[2],4));q=[]
 for j in range(1,len(a)-1):
  y=v[:,:,a[j]];m=mask(y);q.append(np.abs(.5*(v[:,:,a[j-1]]+v[:,:,a[j+1]])-y)[m].mean())
 return float(np.median(q))
def adjacent(v):
 a=list(range(0,v.shape[2],4));q=[]
 for l,r in zip(a[:-1],a[1:]):m=mask(v[:,:,l])|mask(v[:,:,r]);q.append(np.abs(v[:,:,l]-v[:,:,r])[m].mean())
 return float(np.median(q))
def pc_score(a,b):
 q=[]
 for z in range(min(a.shape[2],b.shape[2])):
  if z%4==0:continue
  m=mask(a[:,:,z]);q.append(np.abs(a[:,:,z]-b[:,:,z])[m].mean())
 return float(np.median(q))

m=pd.read_csv(UP/'DATA_MANIFEST.csv');m=m[(m.factor==4)&m.architecture.isin(['hat','swinir'])];rows=[];hardware={'gpu':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,'torch':torch.__version__,'cuda':torch.version.cuda,'cpu_score_repetitions':100,'gpu_repetitions_after_warmup':3}
for ds,g in m.groupby('dataset'):
 case=sorted(g.case_id.unique())[len(g.case_id.unique())//2];q=g[g.case_id==case];rh=q[q.architecture=='hat'].iloc[0];rs=q[q.architecture=='swinir'].iloc[0]
 gt=nib.load(rh.ground_truth_file).get_fdata(dtype=np.float32);ph=nib.load(rh.source_file).get_fdata(dtype=np.float32);ps=nib.load(rs.source_file).get_fdata(dtype=np.float32);s0=np.ascontiguousarray(gt[:,:,::4]);s2=np.ascontiguousarray(gt[:,:,2::4])
 for name,fn,required_calls,stored in [('Anchor-CV',lambda:anchor_cv(gt),0,0),('Adjacent difference',lambda:adjacent(gt),0,0),('Output PC score',lambda:pc_score(ph,ps),2,ph.nbytes+ps.nbytes)]:
  med,p95=cpu_timed(fn);rows.append({'dataset':ds,'case':case,'stage':'score_only_cpu','method':name,'required_neural_calls':required_calls,'median_ms':med,'p95_ms':p95,'peak_allocated_mib':0.,'stored_output_mib':stored/2**20})
 hat=load_net(ds,'hat',checkpoint(rh,'hat'));swin=load_net(ds,'swinir',checkpoint(rs,'swinir'))
 cache={}
 def h0():cache['h0']=hat.interpolate_volume(s0,stride=4)
 def sw0():cache['sw0']=swin.interpolate_volume(s0,stride=4)
 def hflip():cache['hf']=hat.interpolate_volume(np.ascontiguousarray(s0[::-1,:,:]),stride=4)[::-1,:,:]
 def hphase():cache['hp']=hat.interpolate_volume(s2,stride=4)
 for name,fn in [('HAT standard reconstruction',h0),('SwinIR standard reconstruction',sw0),('HAT flipped TTA view',hflip),('HAT disjoint phase view',hphase)]:
  med,p95,peak=timed(fn);arr=list(cache.values())[-1];rows.append({'dataset':ds,'case':case,'stage':'gpu_component','method':name,'required_neural_calls':1,'median_ms':med,'p95_ms':p95,'peak_allocated_mib':peak,'stored_output_mib':arr.nbytes/2**20})
 # Derived strategy totals use measured sequential components and measured score-only cost.
 d=pd.DataFrame(rows);z=d[d.dataset==ds].set_index('method')
 strategies=[('Committee (HAT+SwinIR)',2,z.loc['HAT standard reconstruction','median_ms']+z.loc['SwinIR standard reconstruction','median_ms']+z.loc['Output PC score','median_ms'],z.loc['HAT standard reconstruction','stored_output_mib']+z.loc['SwinIR standard reconstruction','stored_output_mib'],max(z.loc['HAT standard reconstruction','peak_allocated_mib'],z.loc['SwinIR standard reconstruction','peak_allocated_mib'])),('HAT flip TTA pair',2,z.loc['HAT standard reconstruction','median_ms']+z.loc['HAT flipped TTA view','median_ms'],z.loc['HAT standard reconstruction','stored_output_mib']+z.loc['HAT flipped TTA view','stored_output_mib'],max(z.loc['HAT standard reconstruction','peak_allocated_mib'],z.loc['HAT flipped TTA view','peak_allocated_mib'])),('HAT disjoint phase pair',2,z.loc['HAT standard reconstruction','median_ms']+z.loc['HAT disjoint phase view','median_ms'],z.loc['HAT standard reconstruction','stored_output_mib']+z.loc['HAT disjoint phase view','stored_output_mib'],max(z.loc['HAT standard reconstruction','peak_allocated_mib'],z.loc['HAT disjoint phase view','peak_allocated_mib'])),('Anchor-CV acquired-only',0,z.loc['Anchor-CV','median_ms'],0.,0.)]
 for name,calls,med,store,peak in strategies:rows.append({'dataset':ds,'case':case,'stage':'strategy_total','method':name,'required_neural_calls':calls,'median_ms':med,'p95_ms':np.nan,'peak_allocated_mib':peak,'stored_output_mib':store})
 del hat,swin,cache;torch.cuda.empty_cache()

x=pd.DataFrame(rows);x.to_csv(OUT/'plan6_efficiency.csv',index=False);tot=x[x.stage=='strategy_total'];payload={'experiment':'P6-E10','status':'COMPLETE','coverage':['fastmri','ixi','ningxia'],'hardware':hardware,'scope':'one deterministic median-index case per cohort; medians over three timed GPU repetitions after warm-up; score-only CPU over 100 repetitions','strategy_interpretation':'Anchor-CV uses acquired anchors and zero neural calls. Output PC score-only is cheap only after two predictions exist; strategy totals include required inference components. GPU components were measured sequentially, so peak memory is maximum component allocation rather than simultaneous model residency.','outputs':['plan6_efficiency.csv']}
(OUT/'plan6_efficiency.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(x.to_string(index=False));print(json.dumps(payload,indent=2))
