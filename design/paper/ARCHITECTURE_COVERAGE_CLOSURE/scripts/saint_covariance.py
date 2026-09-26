from core_acquired import *
from run_proposition_validation import evaluate
from audit_statistics import bootstrap_indices,simultaneous

def main():
 stability=pd.read_csv(P/'outputs/saint_acquired_stability.csv');s=stability[stability.dataset=='ixi']
 assert len(s)==3 and (s.rank_stability>=.90).all(),'No covariance inference permitted after stability failure'
 torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 dest=P/'outputs/proposition_arrays';dest.mkdir(exist_ok=True);names=read(B/'proposition_case_registry.json');cases={r['case']:r for r in read(B/'case_registry.json') if r['dataset']=='ixi'}
 net=load_net('ixi','saint');epsilons=[.0025,.005,.01,.02];fields=patterns();fields+= [-x for x in fields];rows=[];t=time.perf_counter()
 for i,c in enumerate(names,1):
  r=cases[c];z=r['central_target'];path=dest/f'saint_{c}.npz'
  if not path.exists():
   pool,lo,scale,mask=inputs(B/'inputs'/f'ixi_{c}_z{z}.npz');ctxs=CONTEXTS[:5]
   base=predict(net,[conditions(net,pool,z,r['depth'],ctx)[0] for ctx in ctxs],mask.shape,lo,scale)[:,mask];allpred=[]
   for eps in epsilons:
    contextpred=[]
    for ctx in ctxs:
     cs=[]
     for anchor in ctx:cs.extend(conditions(net,pool,z,r['depth'],ctx,anchor,fields,eps))
     q=predict(net,cs,mask.shape,lo,scale)[:,mask].reshape(2,8,-1);contextpred.append(q)
    allpred.append(np.stack(contextpred))
   np.savez_compressed(path,base=base,predictions=np.stack(allpred),epsilons=epsilons,mask=mask,contexts=np.array(ctxs))
   write(path.with_suffix('.json'),dict(sha256=sha(path),model='saint',case=c,z=z,contract='No target is opened in this experiment',script_sha256=sha(Path(__file__))))
  with np.load(path) as f:
   baseline=None
   for ei,eps in enumerate(f['epsilons']):
    values=evaluate(f['base'],f['predictions'][ei])
    if baseline is None:baseline=values
    for j,value in enumerate(values):
     prediction=-2*baseline[j]['odd_kappa']*(eps/.0025)**2;observed=value['observed_delta'];cos=baseline[j]['odd_response_cosine']
     rows.append(dict(model='saint',case=c,z=z,epsilon=eps,**value,linear_prediction=prediction,approx_abs_error=abs(observed-prediction),approx_relative_error=abs(observed-prediction)/abs(prediction) if prediction!=0 else np.nan,reference_sensitivity_class='aligned' if cos>=.1 else ('opposing' if cos<=-.1 else 'near_orthogonal'),source_hash=sha(path)))
  print('SAINT COVARIANCE',i,c,'seconds',round(time.perf_counter()-t),flush=True)
 df=pd.DataFrame(rows);df.to_csv(P/'outputs/saint_covariance_observations.csv',index=False)
 ag=df.groupby(['case','epsilon']).observed_delta.mean().unstack('epsilon').loc[sorted(names),epsilons];mat=ag.to_numpy();idx=bootstrap_indices(len(names),18005);points=mat.mean(0);ci,valid=simultaneous(points,mat[idx].mean(1));summ=[]
 for j,e in enumerate(epsilons):
  g=df[df.epsilon==e];summ.append(dict(model='saint',epsilon=e,examples=len(g),cases=12,observed_delta_mean=points[j],linear_prediction_mean=g.linear_prediction.mean(),median_relative_error=g.approx_relative_error.median(),max_relative_error=g.approx_relative_error.max(),simultaneous_low=ci[j,0],simultaneous_high=ci[j,1],family_size=4,joint_valid_bootstraps=valid,maximum_closure_error=g.closure_abs_error.max()))
 pd.DataFrame(summ).to_csv(P/'outputs/saint_covariance_summary.csv',index=False);print(pd.DataFrame(summ).to_string(index=False),flush=True)
if __name__=='__main__':main()
