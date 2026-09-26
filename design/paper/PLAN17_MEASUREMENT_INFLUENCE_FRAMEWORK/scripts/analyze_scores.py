from common import *
from scipy.stats import rankdata,spearmanr
def reference_ap_auc(y,s):
 # Independent direct threshold and positive-negative pair definitions.
 ap=0.;p=int(y.sum())
 for threshold in np.unique(s):
  selected=s>=threshold;increment=int(((s==threshold)&(y==1)).sum())/p
  ap+=increment*y[selected].mean()
 a=s[y==1][:,None];b=s[y==0][None,:]
 return ap,float(np.mean((a>b)+.5*(a==b)))
BASE=['disagreement_norm','anchor_cv_norm','adjacent_mae_norm','adjacent_rmse_norm','acquired_range','spacing']
def cdf(train,x):return np.searchsorted(np.sort(train),x,side='right')/len(train)
def weighted_ap_auc(y,s,weights):
 # Scores are fixed; bootstrap resamples patients and multiplicities, preserving ties.
 _,idx=np.unique(s,return_inverse=True);k=idx.max()+1
 gp=np.zeros((len(weights),k));gn=gp.copy()
 for j in range(k):
  gp[:,j]=weights[:,(idx==j)&(y==1)].sum(axis=1);gn[:,j]=weights[:,(idx==j)&(y==0)].sum(axis=1)
 P_=gp.sum(axis=1);N_=gn.sum(axis=1);valid=(P_>0)&(N_>0)
 ap=np.full(len(weights),np.nan);auc=ap.copy()
 den=np.cumsum((gp+gn)[:,::-1],axis=1);num=np.cumsum(gp[:,::-1],axis=1)
 prec=np.divide(num,den,out=np.zeros_like(num),where=den>0)
 ap[valid]=(gp[:,::-1]*prec).sum(axis=1)[valid]/P_[valid]
 auc[valid]=(gp*(np.cumsum(gn,axis=1)-.5*gn)).sum(axis=1)[valid]/(P_*N_)[valid]
 return ap,auc
def main():
 df=pd.read_csv(OUT/'neural_pair_per_case.csv');split=json.loads((OUT/'development_freeze.json').read_text())
 params={};out=[];pred=[];deltas=[];integrity=[]
 for pair,g in df.groupby('pair'):
  dev=g[(g.dataset=='fastmri')&g.case.isin(split['development'])]
  assert len(dev)==12
  params[pair]={'error_q75':float(dev.both_error_norm.quantile(.75)),'disagreement_q25':float(dev.disagreement_norm.quantile(.25)),'cdf_d':dev.disagreement_norm.tolist(),'cdf_acv':dev.anchor_cv_norm.tolist()}
 save('score_formula_freeze.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formula':'max(F_dev(disagreement/acquired_range),F_dev(AnchorCV/acquired_range))','candidates_tried':1,'parameters':params,'protocol_sha256':sha(P/'PROTOCOL.md'),'no_test_tuning':True})
 for ds,names in [('fastmri',split['internal_evaluation']),('ixi',None)]:
  reps_by_pair={};point_by_pair={}
  for pair,g0 in df[df.dataset==ds].groupby('pair'):
   g=g0[g0.case.isin(names)].copy() if names else g0.copy();g=g.sort_values('case').reset_index(drop=True);par=params[pair]
   y=((g.both_error_norm>=par['error_q75'])&(g.disagreement_norm<=par['disagreement_q25'])).to_numpy(int)
   g['guard']=np.maximum(cdf(par['cdf_d'],g.disagreement_norm),cdf(par['cdf_acv'],g.anchor_cv_norm));g['stable_wrong']=y
   pred.extend(g.to_dict('records'));n=len(g);idx=np.random.default_rng(SEED).integers(0,n,(5000,n));counts=np.stack([np.bincount(a,minlength=n) for a in idx]);w=np.vstack([np.ones(n),counts])
   aps={}
   for score in ['guard']+BASE:
    s=g[score].to_numpy();ap,auc=weighted_ap_auc(y,s,w);aps[score]=ap
    if len(np.unique(y))==2:
     ra,ru=reference_ap_auc(y,s);integrity.append(abs(ap[0]-ra)<1e-12 and abs(auc[0]-ru)<1e-12)
     for kk in range(3):
      yy=y[idx[kk]];ss=s[idx[kk]]
      if len(np.unique(yy))==2:
       ra,ru=reference_ap_auc(yy,ss);integrity.append(abs(ap[kk+1]-ra)<1e-12 and abs(auc[kk+1]-ru)<1e-12)
    top=np.argsort(-s,kind='stable')[:max(1,int(np.ceil(.2*n)))];prev=y.mean()
    out.append({'dataset':ds,'pair':pair,'score':score,'cases':n,'positives':int(y.sum()),'auprc':ap[0],'auroc':auc[0],'auprc_low':np.nanquantile(ap[1:],.025) if np.isfinite(ap[1:]).any() else np.nan,'auprc_high':np.nanquantile(ap[1:],.975) if np.isfinite(ap[1:]).any() else np.nan,'valid_bootstraps':int(np.isfinite(ap[1:]).sum()),'error_rho':float(spearmanr(s,g.error_norm).statistic) if np.std(s)>0 else np.nan,'top20_enrichment':float(y[top].mean()/prev) if prev>0 else np.nan})
   point_by_pair[pair]=np.array([aps['guard'][0]-aps[b][0] for b in BASE]);reps_by_pair[pair]=np.column_stack([aps['guard'][1:]-aps[b][1:] for b in BASE])
  pairs=sorted(point_by_pair);point=np.concatenate([point_by_pair[p] for p in pairs]);reps=np.column_stack([reps_by_pair[p] for p in pairs]);valid=np.isfinite(reps).all(axis=1)
  se=np.std(reps[valid],axis=0,ddof=1) if valid.sum()>1 else np.full(len(point),np.nan)
  usable=np.isfinite(point)&(se>1e-12)
  # A family interval cannot be guaranteed if an entire pair has no labels.
  if np.isfinite(point).all() and valid.sum()>=100 and usable.any():
   q=np.quantile(np.max(abs((reps[valid][:,usable]-point[usable])/se[usable]),axis=1),.95);lo=point-q*np.nan_to_num(se);hi=point+q*np.nan_to_num(se)
  else:lo=hi=np.full(len(point),np.nan)
  for j,(pair,base) in enumerate((p,b) for p in pairs for b in BASE):deltas.append({'dataset':ds,'pair':pair,'baseline':base,'delta_auprc':point[j],'simultaneous_low':lo[j],'simultaneous_high':hi[j],'family_size':len(point),'joint_valid_bootstraps':int(valid.sum())})
 pd.DataFrame(out).to_csv(OUT/'score_evaluation.csv',index=False);pd.DataFrame(deltas).to_csv(OUT/'score_paired_deltas.csv',index=False);pd.DataFrame(pred).to_csv(OUT/'score_evaluation_predictions.csv',index=False)
 assert all(integrity)
 save('score_analysis_status.json',{'status':'COMPLETE; stop after one candidate','truly_untouched_holdout':False,'superiority_claim_permitted':False,'weighted_metric_checks':len(integrity),'checks_pass':all(integrity),'protocol_sha256':sha(P/'PROTOCOL.md')})
 print(pd.DataFrame(out)[['dataset','pair','score','cases','positives','auprc','error_rho']].to_string(index=False))
if __name__=='__main__':main()
