from common import *
from acquired_probe import inputs,patterns,conditions,predict
from audit_statistics import bootstrap_indices,simultaneous
import torch,gc,time

def evaluate(base,pred):
 # pred: context x two anchor slots x eight balanced fields x foreground pixels.
 rows=[]
 for ci,ctx in enumerate(CONTEXTS[1:5],1):
  shared=next(iter(set(REF)&set(ctx)));ia=REF.index(shared);ib=ctx.index(shared)
  a=pred[0,ia].astype(float);b=pred[ci,ib].astype(float)
  coupled=float(np.mean((a-b)**2));independent=float(np.mean([np.mean((aa-bb)**2) for aa in a for bb in b]))
  ra=a-base[0];rb=b-base[ci];ca=ra-ra.mean(axis=0);cb=rb-rb.mean(axis=0);cov=float(np.mean(ca*cb))
  odd_a=(ra[:4]-ra[4:])/2;odd_b=(rb[:4]-rb[4:])/2;odd_cov=float(np.mean(odd_a*odd_b));cos=odd_cov/np.sqrt(np.mean(odd_a**2)*np.mean(odd_b**2))
  rows.append({'context':str(ctx),'coupled_disagreement_mse':coupled,'independent_disagreement_mse':independent,'observed_delta':coupled-independent,'matched_centered_kappa':cov,'closure_abs_error':abs((coupled-independent)+2*cov),'odd_kappa':odd_cov,'odd_response_cosine':cos})
 return rows

def main():
 guard();torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 dest=OUT/'proposition_arrays';dest.mkdir(exist_ok=True);names=read(P/'proposition_case_registry.json');cases={r['case']:r for r in read(P/'case_registry.json') if r['dataset']=='ixi'}
 epsilons=[.0025,.005,.01,.02];fields=patterns();fields=fields+[-x for x in fields];rows=[];t=time.perf_counter()
 log_event('proposition_neural_start',{'script_sha256':sha(Path(__file__)),'selection_hash':sha(P/'proposition_case_registry.json')})
 for model in ['hat','swinir']:
  net=load_net('ixi',model)
  for i,c in enumerate(names,1):
   r=cases[c];z=r['central_target'];path=dest/f'{model}_{c}.npz'
   if not path.exists():
    pool,lo,scale,mask=inputs(P/'inputs'/f'ixi_{c}_z{z}.npz');ctxs=CONTEXTS[:5]
    base=predict(net,[conditions(pool,z,ctx)[0] for ctx in ctxs],mask.shape,lo,scale)[:,mask];allpred=[]
    for eps in epsilons:
     contextpred=[]
     for ctx in ctxs:
      cs=[]
      for anchor in ctx:cs.extend(conditions(pool,z,ctx,anchor,fields,eps))
      q=predict(net,cs,mask.shape,lo,scale)[:,mask].reshape(2,8,-1);contextpred.append(q)
     allpred.append(np.stack(contextpred))
    np.savez_compressed(path,base=base,predictions=np.stack(allpred),epsilons=epsilons,mask=mask,contexts=np.array(ctxs))
    write(path.with_suffix('.json'),{'sha256':sha(path),'model':model,'case':c,'z':z,'contract':'no target read in this experiment'})
   with np.load(path) as f:
    baseline=None
    for ei,eps in enumerate(f['epsilons']):
     values=evaluate(f['base'],f['predictions'][ei])
     if baseline is None:baseline=values
     for j,value in enumerate(values):
      prediction=-2*baseline[j]['odd_kappa']*(eps/.0025)**2;observed=value['observed_delta'];cos=baseline[j]['odd_response_cosine']
      rows.append({'model':model,'case':c,'z':z,'epsilon':eps,**value,'linear_prediction':prediction,'approx_abs_error':abs(observed-prediction),'approx_relative_error':abs(observed-prediction)/abs(prediction) if prediction!=0 else np.nan,'reference_sensitivity_class':'aligned' if cos>=.1 else ('opposing' if cos<=-.1 else 'near_orthogonal'),'source_hash':read(path.with_suffix('.json'))['sha256']})
   print('PROPOSITION',model,i,c,'elapsed',round(time.perf_counter()-t),flush=True)
  del net;gc.collect();torch.cuda.empty_cache()
 df=pd.DataFrame(rows);df.to_csv(P/'proposition1_neural_validation.csv',index=False)
 ag=df.groupby(['case','model','epsilon'],as_index=False)[['observed_delta','linear_prediction','approx_abs_error','approx_relative_error']].mean();ag.to_csv(OUT/'proposition_per_examination.csv',index=False)
 cols=[(m,e) for m in ['hat','swinir'] for e in epsilons];mat=ag.pivot(index='case',columns=['model','epsilon'],values='observed_delta').loc[sorted(names),cols].to_numpy();idx=bootstrap_indices(len(names),18005);points=mat.mean(axis=0);reps=mat[idx].mean(axis=1);intervals,valid=simultaneous(points,reps);summ=[]
 for j,(m,e) in enumerate(cols):
  g=df[(df.model==m)&(df.epsilon==e)];summ.append({'model':m,'epsilon':e,'examples':len(g),'cases':12,'observed_delta_mean':points[j],'linear_prediction_mean':g.linear_prediction.mean(),'median_relative_error':g.approx_relative_error.median(),'mean_abs_approx_error':g.approx_abs_error.mean(),'simultaneous_low':intervals[j,0],'simultaneous_high':intervals[j,1],'family_size':8,'maximum_closure_error':g.closure_abs_error.max()})
 pd.DataFrame(summ).to_csv(OUT/'proposition_summary.csv',index=False);log_event('proposition_neural_complete',{'examples':len(df),'seconds':time.perf_counter()-t})
 print(pd.DataFrame(summ).to_string(index=False))
if __name__=='__main__':main()
