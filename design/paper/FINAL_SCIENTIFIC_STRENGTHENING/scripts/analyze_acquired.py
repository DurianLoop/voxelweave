from common import *
from audit_statistics import rho,partial,weighted_partial,weighted_rho,bootstrap_indices,simultaneous

def main():
 guard();df=pd.read_csv(P/'acquired_only_influence.csv');assert len(df)==139*2*3*8*4
 stability=[];summaries=[];crosschecks=[]
 for (ds,model),g in df.groupby(['dataset','model']):
  base=g[(g.epsilon==.01)&(g.overlap_count==1)].sort_values(['case','z','context'])
  for eps in [.005,.02,-.01]:
   other=g[(g.epsilon==eps)&(g.overlap_count==1)].sort_values(['case','z','context']);value=float(rho(base.influence,other.influence))
   stability.append({'dataset':ds,'model':model,'epsilon':eps,'reference_epsilon':.01,'rank_stability':value,'threshold':.85,'status':'PASS' if value>=.85 else 'FAIL','below_historical_catastrophic_floor':value<.70,'original_six_stratum_gate':'NA_no_NingXia_acquired_replication','observations':len(base)})
 for ds in ['ixi','fastmri']:
  family_reps={};family_points={};family_rows={}
  for model in ['hat','swinir']:
   base=df[(df.dataset==ds)&(df.model==model)&(df.epsilon==.01)].sort_values(['case','z','context']).reset_index(drop=True)
   cases=sorted(base.case.unique());idx=bootstrap_indices(len(cases),18003 if ds=='ixi' else 18004);counts=np.stack([np.bincount(i,minlength=len(cases)) for i in idx])
   for endpoint in ['beyond_count','fixed_count']:
    g=base if endpoint=='beyond_count' else base[base.overlap_count==1].reset_index(drop=True)
    codes=pd.Categorical(g.case,categories=cases).codes;x=g.influence.to_numpy();y=g.alignment.to_numpy();cc=g.overlap_count.to_numpy();geo=g[['span','asymmetry']].to_numpy();case=g.case.to_numpy()
    point=abs(float(rho(x,y)))-abs(float(rho(cc,y))) if endpoint=='beyond_count' else partial(x,y,geo,case)
    reps=[]
    for start in range(0,5000,125):
     w=counts[start:start+125][:,codes]
     result=abs(weighted_rho(x,y,w))-abs(weighted_rho(cc,y,w)) if endpoint=='beyond_count' else weighted_partial(x,y,geo,case,w)
     reps.extend(result)
    reps=np.asarray(reps)
    for k in range(3):
     inds=np.concatenate([np.flatnonzero(codes==i) for i in idx[k]])
     newcase=np.concatenate([np.repeat(j,(codes==i).sum()) for j,i in enumerate(idx[k])])
     brute=abs(float(rho(x[inds],y[inds])))-abs(float(rho(cc[inds],y[inds]))) if endpoint=='beyond_count' else partial(x[inds],y[inds],geo[inds],newcase)
     diff=abs(brute-reps[k]);assert diff<1e-10,diff;crosschecks.append({'dataset':ds,'model':model,'endpoint':endpoint,'bootstrap':k,'absolute_difference':diff})
    row={'dataset':ds,'model':model,'endpoint':endpoint,'estimate':point,'rho_influence':float(rho(x,y)),'rho_count':float(rho(cc,y)) if endpoint=='beyond_count' else np.nan,'examinations':len(cases),'observations':len(g),'pointwise_low':np.nanquantile(reps,.025),'pointwise_high':np.nanquantile(reps,.975),'information_contract':'acquired-only'}
    family_points.setdefault(endpoint,[]).append(point);family_reps.setdefault(endpoint,[]).append(reps);family_rows.setdefault(endpoint,[]).append(row)
    print('ACQUIRED stats',ds,model,endpoint,point,flush=True)
  for ep,rows in family_rows.items():
   intervals,valid=simultaneous(family_points[ep],np.column_stack(family_reps[ep]))
   for j,row in enumerate(rows):row.update(simultaneous_low=intervals[j,0],simultaneous_high=intervals[j,1],family_size=2,joint_valid_bootstraps=valid);summaries.append(row)
 pd.DataFrame(stability).to_csv(P/'acquired_only_stability.csv',index=False);pd.DataFrame(summaries).to_csv(OUT/'acquired_only_summary.csv',index=False);pd.DataFrame(crosschecks).to_csv(OUT/'acquired_bootstrap_crosschecks.csv',index=False)
 print(pd.DataFrame(stability).to_string(index=False));print(pd.DataFrame(summaries).to_string(index=False))
if __name__=='__main__':main()
