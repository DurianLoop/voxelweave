from pathlib import Path
import json,sys
P=Path(__file__).resolve().parents[1];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING';ROOT=P.parents[2]
sys.path.insert(0,str(B/'scripts'))
from audit_statistics import bootstrap_indices,simultaneous
import numpy as np,pandas as pd,nibabel as nib
MODELS=['linear','cubic','acvtt','ressrdiff','arssr','resunet','gan_2p5d','smamba_unet']
def main():
 cases=json.loads((B/'case_registry.json').read_text());rows=[];summ=[]
 for ds in ['fastmri','ixi']:
  registry=[r for r in cases if r['dataset']==ds];eligible=[m for m in MODELS if all((P/'outputs/expanded_phase_arrays'/f'{ds}_{m}_{r["case"]}.npz').exists() for r in registry)]
  for i,r in enumerate(registry):
   with np.load(B/r['cross_targets']) as f:y,original=f['gt'],f['mask']
   raw=nib.load(ROOT/r['source']).get_fdata(dtype=np.float32);pred={}
   for m in eligible:
    with np.load(P/'outputs/expanded_phase_arrays'/f'{ds}_{m}_{r["case"]}.npz') as f:
     assert np.array_equal(f['targets'],r['targets']);pred[m]=(f['p0'],f['p2'])
   for j,z in enumerate(r['targets']):
    valid=np.isfinite(y[j])
    for a,b in pred.values():valid &=np.isfinite(a[j])&np.isfinite(b[j])
    phase=np.array(r['phase0']);left=phase[phase<z][-1];right=phase[phase>z][0];a,b=raw[:,:,left],raw[:,:,right]
    union=((abs(a)>.01*abs(a).max())|(abs(b)>.01*abs(b).max()))&np.isfinite(a)&np.isfinite(b)
    masks={'target_1pct':original[j]&valid,'acquired_union':union&valid,'full_common_valid':valid}
    for support,mask in masks.items():
     assert mask.any()
     for m,(a,b) in pred.items():
      ea=a[j][mask].astype(float)-y[j][mask].astype(float);eb=b[j][mask].astype(float)-y[j][mask].astype(float)
      total=np.sum(ea*ea)+np.sum(eb*eb);value=np.sum((ea-eb)**2)/(2*total) if total>0 else np.nan
      # An exact same-output repeat has O=0 if its error is nonzero.
      shared=0. if np.sum(ea*ea)>0 else np.nan
      rows.append(dict(dataset=ds,case=r['case'],model=m,z=z,support=support,pixels=int(mask.sum()),shared_O=shared,disjoint_O=value,delta_O=value-shared,alignment=float(ea@eb/np.sqrt((ea@ea)*(eb@eb))),reference_error=abs(ea).mean(),companion_error=abs(eb).mean(),disagreement=abs(ea-eb).mean()))
   if i%20==0:print('EXPANDED ARRAY ANALYSIS',ds,i,flush=True)
  table=pd.DataFrame([r for r in rows if r['dataset']==ds])
  for support,g in table.groupby('support'):
   mat=g.groupby(['case','model']).delta_O.mean().unstack('model').loc[sorted(r['case'] for r in registry),eligible];assert np.isfinite(mat).all().all()
   arr=mat.to_numpy();idx=bootstrap_indices(len(arr),19001 if ds=='fastmri' else 19002);point=arr.mean(0);reps=arr[idx].mean(1);ci,n=simultaneous(point,reps)
   for k,m in enumerate(eligible):
    s=g[g.model==m].groupby('case')[['shared_O','disjoint_O']].mean().mean()
    summ.append(dict(dataset=ds,model=m,support=support,examinations=len(arr),targets_per_case=5,shared_O=s.shared_O,disjoint_O=s.disjoint_O,delta_O=point[k],simultaneous_low=ci[k,0],simultaneous_high=ci[k,1],family_size=len(eligible),valid_bootstraps=n,status='ELIGIBLE',interpretation='SECONDARY deterministic-self phase sensitivity; shared O=0 constructed, not an independent hidden-error test',cross_architecture='NOT RUN; primary five-model matrix unchanged'))
   for m in set(MODELS)-set(eligible):summ.append(dict(dataset=ds,model=m,support=support,status='INELIGIBLE',interpretation='Technical validation or complete-array coverage failed; see expanded_failures.json'))
 pd.DataFrame(rows).to_csv(P/'outputs/expanded_per_plane.csv',index=False)
 out=pd.DataFrame(summ);out.to_csv(P/'EXPANDED_PHENOMENON_BREADTH.csv',index=False)
 lines=['# 非核心基线的相位覆盖敏感性','','本表不是新增的跨模型主检验。shared 是同一冻结输出的确定性重复，故 O=0 是构造结果；正 ΔO 说明相位变化使预测改变，不能单独证明共享误差机制、TTA 鲁棒性或独立错误。该限制同样适用于所有八个模型，不挑选支持区域。','','| 队列 | 模型 | 支持 | ΔO [同时95%CI] pp |','|---|---|---|---|']
 for r in out.itertuples():
  val=f'{100*r.delta_O:.3f} [{100*r.simultaneous_low:.3f},{100*r.simultaneous_high:.3f}]' if r.status=='ELIGIBLE' else 'NA: technical failure'
  lines.append(f'| {r.dataset} | {r.model} | {r.support} | {val} |')
 lines+=['','原五架构 20 有向对/队列的主矩阵、目标、权重和同时区间全部不变。新增矩阵使用同一五个目标；每目标共同有限支持、每检查内均值、检查等权；5000次共同检查bootstrap，按队列/支持在八个非核心模型之间同时校正。','Res-SRDiff：固定外生 RNG seed20260914，保存完整原采样顺序，包括未用于统计的输出切片；这是条件于固定随机性的相位实验，不是重跑旧 PSNR 表。其随机扩散噪声不能借此被宣称通过 acquired-only 有限响应合同。','ArSSR：完整体积编码保留，仅省略未使用的输出坐标；与原 wrapper 的逐值一致性单列。其他目标选算也在各队列第一个注册病例和全 wrapper 比对后才能使用。IXI 保留输入 NIfTI staging；新预测以浮点 NPZ 保存，不冒称重现旧输出 NIfTI 的序列化量化。','目标支持、acquired-union、全共同有效支持均报告；没有按结果挑选 mask、模型或病例。']
 (P/'EXPANDED_PHENOMENON_BREADTH.md').write_text('\n'.join(lines),encoding='utf-8');print('EXPANDED SUMMARY',len(out),'rows')
if __name__=='__main__':main()
