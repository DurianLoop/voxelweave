"""Recompute mask semantics, then compare all three pre-existing bank supports."""
from pathlib import Path
import os,sys,json,hashlib,collections
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import numpy as np
import pandas as pd
from scipy.stats import rankdata
P14=Path(__file__).resolve().parents[1]; ROOT=P14.parents[2]; PAPER=P14.parent; OUT=P14/'outputs'
sys.path.insert(0,str(ROOT/'design'))
from rasinet import nested_precompute as n
from rasinet.optimization_protocol import profile_sources,prediction_path,sparse_path,gt_path,analytical_path,ANALYTICAL

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def corr(a,b):
    a=rankdata(a,axis=-1); b=rankdata(b,axis=-1); a-=a.mean(-1,keepdims=True); b-=b.mean(-1,keepdims=True)
    with np.errstate(divide='ignore',invalid='ignore'): return (a*b).sum(-1)/np.sqrt((a*a).sum(-1)*(b*b).sum(-1))
def partial(x,y,z):
    a,b,c=corr(x,y),corr(x,z),corr(y,z)
    with np.errstate(divide='ignore',invalid='ignore'): return (a-b*c)/np.sqrt((1-b*b)*(1-c*c))
def ci(a): return np.nanquantile(a,[.025,.975]).tolist()
def bootstrap_indices(g,rng):
    groups=[np.flatnonzero(g.patient_cluster.eq(c).to_numpy()) for c in sorted(g.patient_cluster.unique())]
    records=collections.defaultdict(list)
    for draw in rng.integers(0,len(groups),(10000,len(groups))):
        idx=np.concatenate([groups[i] for i in draw]); records[len(idx)].append(idx)
    return [np.stack(a) for a in records.values()]

sources=[ROOT/f'design/rasinet/outputs/nested_optimization/pair_features_per_case_{s}.csv' for s in ['development','ningxia']]
pair=pd.concat([pd.read_csv(p,keep_default_na=False) for p in sources],ignore_index=True)
old_path=PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_same_model_benefit_per_case.csv'
old=pd.read_csv(old_path,keep_default_na=False)
regpath=ROOT/'design/rasinet/model_bank_registry.csv'; reg=pd.read_csv(regpath)
bank=set(reg.loc[reg.candidate_bank_member.astype(bool),'model'])
masks=['target_0.01','input_derived','bank_union']; columns=['intensity_mean__'+s for s in masks]
pair=pair[pair.scale.eq(4)&pair.dataset.isin(['fastmri','ningxia'])].copy()
checks=[]; raw_inputs=[]
# One pre-specified lexicographically first case in each cohort; both I3Net and HAT targets.
for ds in ['fastmri','ningxia']:
    g=pair[pair.dataset.eq(ds)]; case=sorted(g.case.unique())[0]; rows=g[g.case.eq(case)]
    fold=str(rows.fold.iloc[0]); fold=None if fold=='none' else fold
    specs=profile_sources(ds,4); ref=specs['i3net']
    paths={name:prediction_path(src,fold,case) for name,src in specs.items()}
    paths.update({name:analytical_path(ref,fold,name,case) for name in ANALYTICAL})
    arrays={name:n.load_image(p)[0] for name,p in paths.items()}
    sparse_p=sparse_path(ref,fold,case); gt_p=gt_path(ref,fold,case)
    sparse=n.load_image(sparse_p)[0]; gt=n.load_image(gt_p)[0]; indices=n.generated(gt.shape[2],4)
    acquired=n.input_mask(sparse,gt.shape,indices,4)
    union=np.logical_or.reduce([n.threshold_mask(v,indices) for v in arrays.values()])
    for target in ['i3net','hat']:
        pred_mask=n.threshold_mask(arrays[target],indices); gt_mask=n.threshold_mask(gt,indices)
        for member in sorted(bank-{target}):
            raw=rows[rows.target_model.eq(target)&rows.member.eq(member)].iloc[0]
            diff=abs(arrays[target]-arrays[member])
            for mask_name,mask in [('target_0.01',pred_mask),('input_derived',acquired),('bank_union',union)]:
                value=n.pool_basic(diff,mask,indices,with_q90=False)['mean']; archived=float(raw['intensity_mean__'+mask_name])
                checks.append({'dataset':ds,'case':case,'target':target,'member':member,'mask':mask_name,'recomputed':value,'archived':archived,'absolute_difference':abs(value-archived),
                               'prediction_mask_differs_from_gt_voxels':int(np.count_nonzero(pred_mask!=gt_mask))})
    raw_inputs += [{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in list(paths.values())+[sparse_p,gt_p]]
    print('Raw bank mask verification',ds,case,flush=True)
check=pd.DataFrame(checks); check.to_csv(OUT/'bank_mask_raw_reproduction.csv',index=False)
assert check.absolute_difference.max()<1e-10

agg=pair[pair.member.isin(bank)].groupby(['dataset','fold','case','target_model'])[columns].median().reset_index().rename(columns={'target_model':'model'})
g=old.merge(agg,on=['dataset','fold','case','model'],how='inner',validate='one_to_one')
assert len(g)==506 and g.groupby('dataset').model.nunique().eq(11).all()
assert np.allclose(g.bank_median_disagreement.astype(float),g[columns[0]],atol=1e-12)
g.to_csv(OUT/'bank_mask_benefit_per_case.csv',index=False)
correlations=[]; budgets=[]; differences=[]; rng=np.random.default_rng(20260909)
for (ds,model),base in g.groupby(['dataset','model']):
    base=base.reset_index(drop=True); indices=bootstrap_indices(base,rng); y=base.benefit.to_numpy(float); z=base.mae_x4.to_numpy(float)
    rhos={}; allocations={}
    for mask,col in zip(masks,columns):
        x=base[col].to_numpy(float); raw=np.concatenate([corr(x[j],y[j]) for j in indices]); adj=np.concatenate([partial(x[j],y[j],z[j]) for j in indices])
        rhos[mask]=raw
        correlations.append({'dataset':ds,'model':model,'mask':mask,'cases':len(base),'clusters':base.patient_cluster.nunique(),'rho':float(corr(x,y)),'ci_low':ci(raw)[0],'ci_high':ci(raw)[1],
                             'partial_rho_given_x4':float(partial(x,y,z)),'partial_ci_low':ci(adj)[0],'partial_ci_high':ci(adj)[1],'valid_partial_bootstrap':int(np.isfinite(adj).sum())})
        for budget in [.2,.5]:
            k=int(np.ceil(budget*len(x))); order=np.argsort(-x,kind='stable')[:k]
            delta=float(y[order].mean()-y.mean()); samples=[]
            for j in indices:
                k2=int(np.ceil(budget*j.shape[1])); selected=np.argsort(-x[j],axis=1,kind='stable')[:,:k2]
                samples.append(np.take_along_axis(y[j],selected,axis=1).mean(1)-y[j].mean(1))
            samples=np.concatenate(samples); allocations[mask,budget]=samples
            budgets.append({'dataset':ds,'model':model,'mask':mask,'budget':budget,'gain_above_random':delta,'ci_low':ci(samples)[0],'ci_high':ci(samples)[1]})
    for mask in masks[1:]:
        d=rhos[mask]-rhos[masks[0]]
        differences.append({'dataset':ds,'model':model,'mask':mask,'endpoint':'rho_minus_prediction_mask','difference':float(corr(base['intensity_mean__'+mask],y)-corr(base[columns[0]],y)),'ci_low':ci(d)[0],'ci_high':ci(d)[1]})
pd.DataFrame(correlations).to_csv(OUT/'bank_mask_correlations.csv',index=False)
pd.DataFrame(budgets).to_csv(OUT/'bank_mask_budgets.csv',index=False)
pd.DataFrame(differences).to_csv(OUT/'bank_mask_paired_differences.csv',index=False)
(OUT/'bank_mask_manifest.json').write_text(json.dumps({'status':'COMPLETE','bootstrap':10000,'seed':20260909,'eligible_rows':len(g),'raw_verifications':len(check),'max_reproduction_difference':float(check.absolute_difference.max()),
    'semantics':'target_0.01 is target-model PREDICTION mask; GT mask only defines fidelity endpoint',
    'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sources+[old_path,regpath,ROOT/'design/rasinet/nested_precompute.py']]+raw_inputs,'protocol_sha256':sha(P14/'PROTOCOL.md')},indent=2))
print(pd.DataFrame(correlations).groupby(['dataset','mask'])[['rho','partial_rho_given_x4']].median().to_string(),flush=True)
