from common import *
from scipy.stats import spearmanr
def wrank(x,w):
 order=np.argsort(x,kind='stable');xs=x[order];ends=np.r_[np.flatnonzero(np.diff(xs)!=0),len(xs)-1]
 cum=np.cumsum(w[:,order],axis=1)[:,ends];mass=np.diff(np.column_stack([np.zeros(len(w)),cum]),axis=1)
 mid=cum-.5*mass;inv=np.searchsorted(np.unique(x),x)
 return mid[:,inv]
def wcorr(x,y,w):
 rx=wrank(x,w);ry=wrank(y,w);den=w.sum(axis=1,keepdims=True)
 rx-=np.sum(w*rx,axis=1,keepdims=True)/den;ry-=np.sum(w*ry,axis=1,keepdims=True)/den
 return np.sum(w*rx*ry,axis=1)/np.sqrt(np.sum(w*rx*rx,axis=1)*np.sum(w*ry*ry,axis=1))
def main():
 path=PAPER/'CVPR/archive/CVPR_UPGRADE/outputs/plan6_neural_shared_influence_confirm3_per_case_config.csv';df=pd.read_csv(path);rows=[];reps=[]
 for (ds,model),allg in df.groupby(['dataset','model']):
  g=allg[allg.overlap_count<2].reset_index(drop=True);cl=sorted(g.patient_cluster.unique());n=len(cl);codes=pd.Categorical(g.patient_cluster,categories=cl).codes
  # Same draws within a cohort across architectures; independent streams across cohorts.
  stream=np.random.SeedSequence([SEED,{'fastmri':0,'ixi':1,'ningxia':2}[ds]])
  idx=np.random.default_rng(stream).integers(0,n,(5000,n));weights=np.stack([np.bincount(a,minlength=n) for a in idx])[:,codes]
  x=g.neural_influence_cosine.to_numpy();c=g.overlap_count.to_numpy();y=g.error_cosine.to_numpy();point=abs(spearmanr(x,y).statistic)-abs(spearmanr(c,y).statistic)
  rp=[]
  for start in range(0,5000,250):
   w=weights[start:start+250];rp.extend(abs(wcorr(x,y,w))-abs(wcorr(c,y,w)))
  rp=np.asarray(rp);reps.append(rp)
  # Cross-check weighted ranks against direct duplicated observations.
  for k in range(3):
   ii=np.repeat(np.arange(len(g)),weights[k]);brute=abs(spearmanr(x[ii],y[ii]).statistic)-abs(spearmanr(c[ii],y[ii]).statistic);assert abs(brute-rp[k])<1e-12
  rows.append({'dataset':ds,'model':model,'rows_retained':len(g),'self_rows_removed':len(allg)-len(g),'clusters':n,'rho_count':spearmanr(c,y).statistic,'rho_influence':spearmanr(x,y).statistic,'advantage':point,'pointwise_low':np.quantile(rp,.025),'pointwise_high':np.quantile(rp,.975)})
  print(ds,model,point,flush=True)
 reps=np.column_stack(reps);pt=np.array([r['advantage'] for r in rows]);se=reps.std(axis=0,ddof=1);q=np.quantile(np.max(abs((reps-pt)/se),axis=1),.95)
 for j,r in enumerate(rows):r.update(simultaneous_low=pt[j]-q*se[j],simultaneous_high=pt[j]+q*se[j],family_size=6)
 pd.DataFrame(rows).to_csv(OUT/'nonself_influence_summary.csv',index=False);save('nonself_influence_manifest.json',{'source_sha256':sha(path),'addendum_sha256':sha(P/'INTEGRITY_ADDENDUM.md'),'status':'post-hoc integrity sensitivity','bootstrap':5000,'simultaneous_family':6,'weighted_rank_crosschecks':18})
 print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__':main()
