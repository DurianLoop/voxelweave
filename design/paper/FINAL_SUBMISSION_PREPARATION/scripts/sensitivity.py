"""Bounded, post-hoc CPU analysis; immutable saved predictions only."""
from pathlib import Path
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
import json,hashlib,datetime
import numpy as np,pandas as pd,nibabel as nib
from scipy.stats import spearmanr,rankdata
P=Path(__file__).resolve().parents[1];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING';ROOT=P.parents[2];OUT=P/'outputs'
MODELS=['hat','swinir','i3net','saint','cycleinr'];PAIRS=[a+'__'+b for a in MODELS for b in MODELS if a!=b]
def guard():
 f=json.loads((P/'freeze.json').read_text());assert hashlib.sha256((P/'FINAL_SUBMISSION_PATCH_PROTOCOL.md').read_bytes()).hexdigest()==f['protocol_sha256']
def draws(ds,n):return np.random.default_rng(19001 if ds=='fastmri' else 19002).integers(0,n,(5000,n))
def sim(p,b):
 sd=b.std(0,ddof=1);z=np.divide(abs(b-p),sd,out=np.zeros_like(b),where=sd>0);r=np.quantile(z.max(1),.95)*sd
 return np.c_[p-r,p+r]
def observable(a,b,y,m):
 x=a[m].astype(float)-y[m].astype(float);v=b[m].astype(float)-y[m].astype(float)
 den=2*(np.sum(x*x)+np.sum(v*v));return np.sum((x-v)**2)/den if den>0 else np.nan
def extract():
 guard();rows=[];geometry=[]
 for i,r in enumerate(json.loads((B/'case_registry.json').read_text())):
  ds,c=r['dataset'],r['case'];v={}
  for model in MODELS:
   with np.load(B/'outputs/phase_arrays'/f'{ds}_{model}_{c}.npz') as f:
    a,b=f['p0'],f['p2'];v[model]=(np.moveaxis(a[:,:,r['targets']],2,0),np.moveaxis(b[:,:,np.array(r['targets'])-2],2,0)) if bool(f['full_arrays']) else (a,b)
  with np.load(B/r['cross_targets']) as f:y,original=f['gt'],f['mask']
  raw=nib.load(ROOT/r['source']).get_fdata(dtype=np.float32)
  for j,z in enumerate(r['targets']):
   p0=np.array(r['phase0']);p2=np.array(r['phase2']);left=p0[p0<z];right=p0[p0>z]
   anchor_valid=bool(len(left) and len(right));nearest=[];full=True
   for pp in [p0,p2]:
    ll=pp[pp<z];rr=pp[pp>z];nearest.append(sorted([z-int(ll[-1]),int(rr[0])-z]) if len(ll) and len(rr) else [])
    full=full and len(ll)>=2 and len(rr)>=2
   valid=np.isfinite(y[j])
   for values in v.values():valid=valid&np.isfinite(values[0][j])&np.isfinite(values[1][j])
   masks={'target_1pct':original[j]&valid,'full_common_valid':valid}
   if anchor_valid:
    lo,hi=raw[:,:,left[-1]],raw[:,:,right[0]]
    masks['acquired_union']=((abs(lo)>.01*abs(lo).max())|(abs(hi)>.01*abs(hi).max()))&np.isfinite(lo)&np.isfinite(hi)&valid
   geometry.append(dict(dataset=ds,case=c,z=z,residue=z%4,nearest_match=nearest==[[1,3],[1,3]],full_four_anchor=bool(full),acquired_valid=anchor_valid,common_valid_pixels=int(valid.sum()),total_pixels=int(valid.size)))
   for support,m in masks.items():
    assert m.any(),(ds,c,z,support)
    for pair in PAIRS:
     a,b=pair.split('__');s=observable(v[a][0][j],v[b][0][j],y[j],m);d=observable(v[a][0][j],v[b][1][j],y[j],m)
     rows.append(dict(dataset=ds,case=c,z=z,pair=pair,support=support,pixels=int(m.sum()),shared_O=s,disjoint_O=d,delta_O=d-s))
  if i%15==0:print('Support raw arrays',i,flush=True)
 pd.DataFrame(rows).to_csv(OUT/'sensitivity_per_plane.csv',index=False);pd.DataFrame(geometry).to_csv(OUT/'geometry_registry.csv',index=False)
def summarize(g,ds,label):
 g=g.groupby(['case','pair'])[['shared_O','disjoint_O','delta_O']].mean();cases=sorted(g.index.get_level_values('case').unique());mat=g.delta_O.unstack('pair').loc[cases,PAIRS].to_numpy();idx=draws(ds,len(cases));boot=mat[idx].mean(1);point=mat.mean(0);iv=sim(point,boot);rows=[]
 for j,pair in enumerate(PAIRS):
  v=g.xs(pair,level='pair').mean();rows.append(dict(dataset=ds,analysis=label,pair=pair,units=len(cases),shared_O=v.shared_O,disjoint_O=v.disjoint_O,delta_O=point[j],simultaneous_low=iv[j,0],simultaneous_high=iv[j,1],status='ESTIMATED',ci_family='20 ordered pairs / cohort / analysis'))
 lo,hi=np.quantile(boot.mean(1),[.025,.975]);rows.append(dict(dataset=ds,analysis=label,pair='equal_weight_family',units=len(cases),shared_O=g.shared_O.mean(),disjoint_O=g.disjoint_O.mean(),delta_O=point.mean(),simultaneous_low=lo,simultaneous_high=hi,status='DESCRIPTIVE_FAMILY',ci_family='family mean percentile'))
 return rows
def analyze():
 guard();df=pd.read_csv(OUT/'sensitivity_per_plane.csv');geo=pd.read_csv(OUT/'geometry_registry.csv');rows=[]
 for (ds,support),g in df.groupby(['dataset','support']):rows+=summarize(g,ds,support)
 support=pd.DataFrame(rows);support.to_csv(P/'CROSS_ARCH_SUPPORT_SENSITIVITY.csv',index=False)
 lines=['# 支持区域敏感性（事后）','','同一冻结A0/B0/B2与目标；先目标均值、再检查均值；5000次联合检查bootstrap；每支持区域/数据集内20对 simultaneous 95% CI。家族行是描述性percentile CI，未对所有敏感性联合校正。排序比较的是20对效应量顺序，不是患者错误排序。','','| Cohort | Support | ΔO range (pp) | Positive effects / CI | Family ΔO [CI] (pp) | Pair-rank rho | Max rank movement | Material ordering change |','|---|---|---:|---|---|---:|---:|---|']
 for (ds,name),g in support.groupby(['dataset','analysis']):
  q=g[g.pair!='equal_weight_family'].set_index('pair').loc[PAIRS];ref=support[(support.dataset==ds)&(support.analysis=='target_1pct')&(support.pair!='equal_weight_family')].set_index('pair').loc[PAIRS];r=spearmanr(q.delta_O,ref.delta_O).statistic;move=max(abs(rankdata(q.delta_O)-rankdata(ref.delta_O)));f=g[g.pair=='equal_weight_family'].iloc[0]
  lines.append(f'| {ds} | {name} | {100*q.delta_O.min():.3f}–{100*q.delta_O.max():.3f} | {(q.delta_O>0).sum()}/20; {(q.simultaneous_low>0).sum()}/20 | {100*f.delta_O:.3f} [{100*f.simultaneous_low:.3f},{100*f.simultaneous_high:.3f}] | {r:.4f} | {move:.0f} | {r<.9 or move>=5} |')
 lines+=['','Acquired support uses only the two bracketing phase-0 anchors, each absolute intensity >1% its own maximum; unchanged historical union contract. It is intentionally held fixed across both conditions and all architectures. The full support uses the common finite pixel set, including background. All masks and eligibility counts are in outputs/geometry_registry.csv and sensitivity_per_plane.csv. No independence of model pairs is assumed.']
 (P/'CROSS_ARCH_SUPPORT_SENSITIVITY.md').write_text('\n'.join(lines),encoding='utf-8')
 original=df[df.support=='target_1pct'].merge(geo,on=['dataset','case','z'],validate='many_to_one');rows=[]
 for ds,g in original.groupby('dataset'):
  for res in [1,3]:rows+=summarize(g[g.residue==res],ds,f'residue_{res}')
  for label,sub in [('residue_balanced',g),('nearest_distance_matched_balanced',g[g.nearest_match]),('full_four_anchor_balanced',g[g.full_four_anchor])]:
   grouped=sub.groupby(['case','pair','residue'])[['shared_O','disjoint_O','delta_O']].mean();counts=grouped.groupby(['case','pair']).size();valid=counts[counts==2].index;subcase=grouped.reset_index().set_index(['case','pair']).loc[valid].reset_index() if len(valid) else pd.DataFrame()
   if subcase.empty:
    for pair in PAIRS+['equal_weight_family']:rows.append(dict(dataset=ds,analysis=label,pair=pair,units=0,status='NA: no examination has both residue classes with two anchors on each side in both phases'))
    continue
   balanced=subcase.groupby(['case','pair'])[['shared_O','disjoint_O','delta_O']].mean().reset_index();rows+=summarize(balanced,ds,label)
   if label=='residue_balanced':
    x=subcase.pivot(index=['case','pair'],columns='residue',values=['shared_O','disjoint_O','delta_O']);mirror=pd.DataFrame({k:x[(k,1)]-x[(k,3)] for k in ['shared_O','disjoint_O','delta_O']}).reset_index();rows+=summarize(mirror,ds,'mirror_residue1_minus_residue3')
 geometry=pd.DataFrame(rows);geometry.to_csv(P/'CROSS_ARCH_GEOMETRY_SENSITIVITY.csv',index=False)
 lines=['# 几何敏感性（事后）','','先在每检查每residue平均原先五个目标，再等权平衡residue。镜像差是两个反射类效应的差，不是重新执行镜像推理，不证明identity的纯因果效应。所有分析使用原target-1%支持。','','| Cohort | Analysis | Units | ΔO range (pp) | Positive effects / positive CI / negative CI | Family estimate [CI] (pp) |','|---|---|---:|---:|---|---|']
 for (ds,name),g in geometry.groupby(['dataset','analysis']):
  q=g[g.pair!='equal_weight_family'];f=g[g.pair=='equal_weight_family'].iloc[0]
  if f.units==0:lines.append(f'| {ds} | {name} | 0 | NA | NA | {f.status} |');continue
  lines.append(f'| {ds} | {name} | {int(f.units)} | {100*q.delta_O.min():.3f}–{100*q.delta_O.max():.3f} | {(q.delta_O>0).sum()}/20; {(q.simultaneous_low>0).sum()}/20; {(q.simultaneous_high<0).sum()}/20 | {100*f.delta_O:.3f} [{100*f.simultaneous_low:.3f},{100*f.simultaneous_high:.3f}] |')
 lines+=['','Nearest-distance matching requires the actual bracketing distances {1,3} in both phases. Full-four-anchor eligibility additionally requires at least two actual acquired anchors on either side in both phases and both residue classes within an examination. fastMRI depth16 only admits target7 for the latter contract, hence cannot form the two-residue estimate. No boundary anchors are imputed. Significant mirror differences remain orientation warnings; intervals containing zero do not establish equivalence. Residual full-context geometry, preprocessing and anatomical changes are not eliminated.']
 (P/'CROSS_ARCH_GEOMETRY_SENSITIVITY.md').write_text('\n'.join(lines),encoding='utf-8')
 rows=[]
 for ds,g in original.groupby('dataset'):
  mat=g.groupby(['case','pair']).delta_O.mean().unstack('pair')[PAIRS].to_numpy();idx=draws(ds,len(mat));boot=mat[idx].mean(1);point=mat.mean(0)
  for excluded in ['none']+MODELS:
   keep=[j for j,pair in enumerate(PAIRS) if excluded not in pair.split('__')];v=point[keep];b=boot[:,keep]
   for stat,fn in [('mean',np.mean),('median',np.median)]:
    lo,hi=np.quantile(fn(b,axis=1),[.025,.975]);rows.append(dict(dataset=ds,excluded_architecture=excluded,pairs=len(keep),statistic=stat,delta_O=fn(v),low=lo,high=hi))
 family=pd.DataFrame(rows);family.to_csv(P/'CROSS_ARCH_FAMILY_ROBUSTNESS.csv',index=False)
 lines=['# 模型对家族稳健性（事后描述）','','20对共享检查和架构，不是20个独立重复。所有pair列共同重采样检查；bootstrap内部先算各pair检查均值，再做家族mean/median。逐架构排除全部涉及该架构的方向对，剩余12对。区间为描述性95% percentile，不替代完整矩阵。','','| Cohort | Excluded | Pairs | Statistic | ΔO [95% CI] (pp) |','|---|---|---:|---|---|']
 for r in family.itertuples():lines.append(f'| {r.dataset} | {r.excluded_architecture} | {r.pairs} | {r.statistic} | {100*r.delta_O:.3f} [{100*r.low:.3f},{100*r.high:.3f}] |')
 (P/'CROSS_ARCH_FAMILY_ROBUSTNESS.md').write_text('\n'.join(lines),encoding='utf-8')
 print('Sensitivity summaries complete',flush=True)
if __name__=='__main__':extract();analyze()
