from pathlib import Path
import sys,json
P=Path(__file__).resolve().parents[1];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING'
sys.path.insert(0,str(B/'scripts'))
from audit_statistics import rho,partial,weighted_partial,weighted_rho,bootstrap_indices,simultaneous
import numpy as np,pandas as pd

def main():
 df=pd.read_csv(P/'outputs/saint_acquired_observations.csv');assert len(df)==139*3*8*4
 stable=[];res=[];secondary=[];checks=[];family={}
 for ds in ['ixi','fastmri']:
  allg=df[df.dataset==ds];base=allg[allg.epsilon==.01].sort_values(['case','z','context']).reset_index(drop=True)
  for eps in [.005,.02,-.01]:
   x=base[base.overlap_count==1].influence.to_numpy();alt=allg[(allg.epsilon==eps)&(allg.overlap_count==1)].sort_values(['case','z','context']).influence.to_numpy()
   val=float(rho(x,alt));stable.append(dict(dataset=ds,model='saint',epsilon=eps,rank_stability=val,threshold=.90,status='PASS' if val>=.90 else 'FAIL'))
  cases=sorted(base.case.unique());idx=bootstrap_indices(len(cases),18003 if ds=='ixi' else 18004);counts=np.stack([np.bincount(i,minlength=len(cases)) for i in idx])
  for endpoint in ['beyond_count','fixed_count']:
   g=base if endpoint=='beyond_count' else base[base.overlap_count==1].reset_index(drop=True)
   codes=pd.Categorical(g.case,categories=cases).codes;x=g.influence.to_numpy();y=g.alignment.to_numpy();cc=g.overlap_count.to_numpy();geo=g[['span','asymmetry']].to_numpy();case=g.case.to_numpy()
   point=abs(float(rho(x,y)))-abs(float(rho(cc,y))) if endpoint=='beyond_count' else partial(x,y,geo,case);reps=[]
   for start in range(0,5000,125):
    w=counts[start:start+125][:,codes]
    vals=abs(weighted_rho(x,y,w))-abs(weighted_rho(cc,y,w)) if endpoint=='beyond_count' else weighted_partial(x,y,geo,case,w)
    reps.extend(vals)
   reps=np.asarray(reps)
   for k in range(3):
    inds=np.concatenate([np.flatnonzero(codes==i) for i in idx[k]]);newcase=np.concatenate([np.repeat(j,(codes==i).sum()) for j,i in enumerate(idx[k])])
    direct=abs(float(rho(x[inds],y[inds])))-abs(float(rho(cc[inds],y[inds]))) if endpoint=='beyond_count' else partial(x[inds],y[inds],geo[inds],newcase)
    error=abs(direct-reps[k]);assert error<1e-10;checks.append(dict(dataset=ds,endpoint=endpoint,draw=k,absolute_error=error))
   row=dict(dataset=ds,model='saint',endpoint=endpoint,estimate=point,rho_influence=float(rho(x,y)),rho_count=float(rho(cc,y)) if endpoint=='beyond_count' else np.nan,examinations=len(cases),observations=len(g),pointwise_low=np.quantile(reps,.025),pointwise_high=np.quantile(reps,.975),information_contract='acquired-only')
   family.setdefault(endpoint,[]).append((row,reps));print('SAINT STATS',ds,endpoint,point,flush=True)
  for (eps,),g in allg.groupby(['epsilon']):
   for metric in ['alignment','observable','disagreement','paired_error','reference_error','companion_error']:
    one=g[g.overlap_count==1]
    secondary.append(dict(dataset=ds,model='saint',epsilon=eps,endpoint=metric,rho_influence=float(rho(g.influence,g[metric])),rho_count=float(rho(g.overlap_count,g[metric])),beyond_count=abs(float(rho(g.influence,g[metric])))-abs(float(rho(g.overlap_count,g[metric]))),fixed_count=partial(one.influence.to_numpy(),one[metric].to_numpy(),one[['span','asymmetry']].to_numpy(),one.case.to_numpy()),inference='descriptive, no additional family'))
 for ep,items in family.items():
  ci,valid=simultaneous([v[0]['estimate'] for v in items],np.column_stack([v[1] for v in items]))
  for j,(r,reps) in enumerate(items):r.update(simultaneous_low=ci[j,0],simultaneous_high=ci[j,1],family_size=2,joint_valid_bootstraps=valid,inference_family='new SAINT replication: both cohorts, separately per endpoint');res.append(r)
 pd.DataFrame(res).to_csv(P/'outputs/saint_acquired_summary.csv',index=False)
 pd.DataFrame(stable).to_csv(P/'outputs/saint_acquired_stability.csv',index=False)
 pd.DataFrame(secondary).to_csv(P/'outputs/saint_secondary_signs.csv',index=False)
 pd.DataFrame(checks).to_csv(P/'outputs/saint_bootstrap_checks.csv',index=False)
 old=pd.read_csv(B/'outputs/acquired_only_summary.csv');new=pd.DataFrame(res);ss=pd.concat([pd.read_csv(B/'acquired_only_stability.csv'),pd.DataFrame(stable)],ignore_index=True)
 rows=[]
 for ds in ['fastmri','ixi']:
  for m in ['hat','swinir','saint','i3net','cycleinr']:
   row=dict(dataset=ds,model=m,information_contract='acquired-only formation; targets only for error evaluation',threshold=.85 if m in ['hat','swinir'] else .90)
   if m in ['i3net','cycleinr']:
    row.update(technical_eligibility='INELIGIBLE',reason='Exact two-anchor variable-spacing grid incompatible with frozen four-anchor x4 context contract',stability='NA',influence_claim='INELIGIBLE',historical_status='HISTORICAL ONLY: target-informed four-anchor stability FAIL; not imported as acquired-only')
   else:
    st=ss[(ss.dataset==ds)&(ss.model==m)];row.update(technical_eligibility='ELIGIBLE',stability='PASS' if (st.rank_stability>=row['threshold']).all() else 'FAIL',rank_stability_min=float(st.rank_stability.min()))
    for e,n in [(.005,'half'),(.02,'double'),(-.01,'negative')]:row['stability_'+n]=float(st[st.epsilon==e].rank_stability.iloc[0])
    g=(old if m!='saint' else new);g=g[(g.dataset==ds)&(g.model==m)]
    for ep in ['beyond_count','fixed_count']:
     r=g[g.endpoint==ep].iloc[0]
     for k in ['estimate','simultaneous_low','simultaneous_high']:row[ep+'_'+k]=r[k]
    row['inference_family']='original two models per cohort/endpoint unchanged' if m!='saint' else 'new SAINT both cohorts per endpoint'
    row['influence_claim']='SUPPORTED' if row['stability']=='PASS' and row['beyond_count_simultaneous_low']>0 else ('NUMERICAL FAIL' if row['stability']=='FAIL' else 'NULL/INCONCLUSIVE BEYOND COUNT')
   rows.append(row)
 out=pd.DataFrame(rows);out.to_csv(P/'FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.csv',index=False);out.to_csv(P/'UPDATED_MIRA_REPORT_CARD.csv',index=False)
 print(out.to_string(index=False),flush=True)
if __name__=='__main__':main()
