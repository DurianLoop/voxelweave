from common import *
from audit_statistics import rho,bootstrap_indices,simultaneous

def main():
 guard();rows=[];array_sources=[];pairs=read(P/'pair_registry.json')
 for r in read(P/'case_registry.json'):
  ds,c=r['dataset'],r['case'];arr={}
  for m in MODELS:
   path=OUT/'phase_arrays'/f'{ds}_{m}_{c}.npz';meta=read(path.with_suffix('.json'));array_sources.append({'path':path.relative_to(P).as_posix(),'sha256':meta['sha256']})
   with np.load(path) as f:
    a,b=f['p0'],f['p2'];full=bool(f['full_arrays']);zs=r['targets']
    arr[m]=(np.stack([a[:,:,z] for z in zs]),np.stack([b[:,:,z-2] for z in zs])) if full else (a,b)
  with np.load(P/r['cross_targets']) as f:y,mask=f['gt'],f['mask']
  for pair in pairs:
   a=arr[pair['a']][0]
   for cond,idx in [('shared',0),('disjoint',1)]:
    b=arr[pair['b']][idx]
    for j,z in enumerate(r['targets']):rows.append({'dataset':ds,'case':c,**pair,'condition':cond,'z':z,'information_contract':'target-derived support','status':'VALID',**metrics(a[j],b[j],y[j],mask[j])})
  print('CROSS arrays',ds,c,flush=True)
 df=pd.DataFrame(rows);assert not df.duplicated(['dataset','case','pair','condition','z']).any();assert len(df)==139*20*2*5
 df.to_csv(P/'cross_arch_shared_disjoint.csv',index=False)
 ag=df.groupby(['dataset','case','pair','condition'],as_index=False)[['observable','alignment','disagreement','reference_error','paired_error']].mean();ag.to_csv(OUT/'cross_arch_per_examination.csv',index=False)
 result=[]
 for ds in ['fastmri','ixi']:
  g=ag[ag.dataset==ds];cases=sorted(g.case.unique());names=[p['pair'] for p in pairs];idx=bootstrap_indices(len(cases),18001 if ds=='fastmri' else 18002)
  def mat(ep,cond):return g[g.condition==cond].pivot(index='case',columns='pair',values=ep).loc[cases,names].to_numpy()
  endpoints={}
  for ep in ['observable','alignment','disagreement']:
   s,d=mat(ep,'shared'),mat(ep,'disjoint');gain=d-s;endpoints[ep+'_gap']=(gain.mean(axis=0),gain[idx].mean(axis=1),s.mean(axis=0),d.mean(axis=0))
  sd,dd=mat('disagreement','shared'),mat('disagreement','disjoint');es,ed=mat('paired_error','shared'),mat('paired_error','disjoint');ref=mat('reference_error','shared');assert np.array_equal(ref,mat('reference_error','disjoint'))
  for ep,x,y in [('fixed_reference_ranking',ref,ref),('paired_error_ranking',es,ed)]:
   s=rho(sd,x,0);d=rho(dd,y,0);reps=rho(dd[idx],y[idx],1)-rho(sd[idx],x[idx],1);endpoints[ep]=(d-s,reps,s,d)
  for ep,(point,reps,s,d) in endpoints.items():
   intervals,valid=simultaneous(point,reps)
   for j,pair in enumerate(pairs):
    lo,hi=np.nanquantile(reps[:,j],[.025,.975]);result.append({'dataset':ds,**pair,'endpoint':ep,'examinations':len(cases),'shared':s[j],'disjoint':d[j],'delta':point[j],'pointwise_low':lo,'pointwise_high':hi,'simultaneous_low':intervals[j,0],'simultaneous_high':intervals[j,1],'family_size':20,'joint_valid_bootstraps':valid,'status':'VALID' if np.isfinite(point[j]) else 'NA_constant_ranking'})
 pd.DataFrame(result).to_csv(P/'cross_arch_shared_disjoint_intervals.csv',index=False);write(OUT/'cross_arch_input_hashes.json',array_sources)
 print(pd.DataFrame(result).query("endpoint=='observable_gap'").to_string(index=False))
if __name__=='__main__':main()
