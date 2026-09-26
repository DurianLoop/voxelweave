import os
os.environ.setdefault('OMP_NUM_THREADS','2');os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from common import *
import nibabel as nib,time
from scipy.stats import rankdata
def corr(x,y,axis=0):
 x=rankdata(x,axis=axis);y=rankdata(y,axis=axis);x=x-x.mean(axis=axis,keepdims=True);y=y-y.mean(axis=axis,keepdims=True)
 den=np.sqrt((x*x).sum(axis=axis)*(y*y).sum(axis=axis));return np.divide((x*y).sum(axis=axis),den,out=np.full_like(den,np.nan),where=den>0)
def main():
 rows=[];times=[];excluded=[];t=time.perf_counter()
 for i,(ds,c,path) in enumerate(datasets(),1):
  im=nib.load(path);v=im.get_fdata(dtype=np.float32);fs=features(v[:,:,::4]);zs=[z for z in range(1,v.shape[2],2) if all(phase+((z-phase)//4)*4-4>=0 and phase+((z-phase)//4)*4+8<v.shape[2] for phase in [0,2])]
  if not zs or {z%4 for z in zs}!={1,3}:
   excluded.append({'dataset':ds,'case':c,'depth':v.shape[2],'eligible_targets':str(zs),'reason':'complete four-point support does not cover both residue classes'})
   continue
  for z in zs:
   l0=interpolate(v,z,0,'linear');c0=interpolate(v,z,0,'cubic');l2=interpolate(v,z,2,'linear');c2=interpolate(v,z,2,'cubic');left=(z//4)*4;m=fg(v[:,:,left])|fg(v[:,:,left+4]);y=v[:,:,z]
   for pair,cond,a,b in [('LC','shared',l0,c0),('LC','disjoint',l0,c2),('CL','shared',c0,l0),('CL','disjoint',c0,l2)]:
    r=metrics(a,b,y,m);rows.append({'dataset':ds,'case':c,'z':z,'residue':z%4,'pair':pair,'condition':cond,**r})
  if i%10==0:print(f'E03 proxy {i}/139 elapsed={time.perf_counter()-t:.1f}s',flush=True)
 pd.DataFrame(excluded).to_csv(OUT/'practical_proxy_geometry_exclusions.csv',index=False)
 df=pd.DataFrame(rows);df.to_csv(OUT/'practical_proxy_per_plane.csv',index=False)
 cols=['mae_a','error','disagreement','variance','observable','error_cosine']
 ag=df.groupby(['dataset','case','pair','condition','residue'])[cols].mean().groupby(['dataset','case','pair','condition']).mean().reset_index();ag.to_csv(OUT/'practical_proxy_per_case.csv',index=False)
 out=[]
 for ds,g in ag.groupby('dataset'):
  cases=sorted(g.case.unique());n=len(cases);idx=np.random.default_rng(SEED).integers(0,n,(5000,n));point=[];reps=[];keys=[]
  for pair in ['LC','CL']:
   gg=g[g.pair==pair]
   def arr(col,cond):return gg[gg.condition==cond].set_index('case').loc[cases,col].to_numpy()
   gain=arr('observable','disjoint')-arr('observable','shared');point.append(gain.mean());reps.append(gain[idx].mean(axis=1));keys.append((pair,'local_observable_gain',''))
   for score in ['disagreement','variance']:
    for endpoint in ['mae_a','error']:
     d=arr(score,'disjoint');s=arr(score,'shared');ed=arr(endpoint,'disjoint');es=arr(endpoint,'shared')
     pt=corr(d,ed)-corr(s,es);rp=corr(d[idx],ed[idx],1)-corr(s[idx],es[idx],1)
     point.append(pt);reps.append(rp);keys.append((pair,score+'_ranking_delta',endpoint))
  point=np.array(point);reps=np.column_stack(reps)
  for j,(pair,metric,endpoint) in enumerate(keys):
   fam=[k for k,v in enumerate(keys) if v[1:]==(metric,endpoint)];se=reps[:,fam].std(axis=0,ddof=1);q=np.quantile(np.max(abs((reps[:,fam]-point[fam])/se),axis=1),.95);k=fam.index(j)
   out.append({'dataset':ds,'pair':pair,'metric':metric,'endpoint':endpoint,'cases':n,'point':point[j],'simultaneous_low':point[j]-q*se[k],'simultaneous_high':point[j]+q*se[k],'family_size':2})
 pd.DataFrame(out).to_csv(OUT/'practical_proxy_summary.csv',index=False);save('practical_proxy_manifest.json',{'protocol_sha256':sha(P/'PROTOCOL.md'),'cases':ag[['dataset','case']].drop_duplicates().shape[0],'excluded_cases':len(excluded),'rows':len(df),'elapsed_seconds':time.perf_counter()-t,'model_training':False})
 print(pd.DataFrame(out).to_string(index=False),flush=True)
if __name__=='__main__':main()
