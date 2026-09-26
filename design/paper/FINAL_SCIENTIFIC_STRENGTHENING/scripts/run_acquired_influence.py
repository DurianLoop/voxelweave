from common import *
from acquired_probe import compute,influence
import torch,time,gc

def main():
 guard();torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 dest=OUT/'acquired_responses';dest.mkdir(exist_ok=True);t=time.perf_counter()
 log_event('acquired_probe_start',{'script_sha256':sha(Path(__file__)),'probe_sha256':sha(P/'scripts/acquired_probe.py'),'precision':'float32, no AMP/TF32'})
 for ds in ['ixi','fastmri']:
  cases=[r for r in read(P/'case_registry.json') if r['dataset']==ds]
  for model in ['hat','swinir']:
   net=load_net(ds,model)
   for i,r in enumerate(cases,1):
    for z in r['influence_targets']:
     path=dest/f'{ds}_{model}_{r["case"]}_z{z}.npz'
     if path.exists():continue
     data=compute(net,P/'inputs'/f'{ds}_{r["case"]}_z{z}.npz',z)
     assert np.isfinite(data['response']).all()
     np.savez_compressed(path,**data)
     # Output binding precedes opening separate retrospective target arrays.
     write(path.with_suffix('.json'),{'dataset':ds,'model':model,'case':r['case'],'z':z,'sha256':sha(path),'utc_before_target_access':datetime.datetime.now(datetime.timezone.utc).isoformat(),'information_contract':'acquired-only','input_sha256':sha(P/'inputs'/f'{ds}_{r["case"]}_z{z}.npz')})
    print('ACQUIRED',ds,model,i,r['case'],'elapsed',round(time.perf_counter()-t),flush=True)
   del net;gc.collect();torch.cuda.empty_cache()
 rows=[]
 for file in sorted(dest.glob('*.npz')):
  meta=read(file.with_suffix('.json'))
  with np.load(file) as f:
   # y first accessed after stored responses and provenance have been committed to disk.
   y=np.load(P/'targets'/f'{meta["dataset"]}_{meta["case"]}_z{meta["z"]}.npy');mask=f['mask'];base=f['base'];response=f['response']
   for ei,eps in enumerate(f['epsilons']):
    for ci,ctx in enumerate(CONTEXTS[1:],1):
     rows.append({k:meta[k] for k in ['dataset','model','case','z']}|{'epsilon':eps,'context':str(ctx),'span':ctx[1]-ctx[0],'asymmetry':abs(sum(ctx)),'overlap_count':len(set(REF)&set(ctx)),'influence':influence(response[ei],ci),'source_hash':meta['sha256'],**metrics(base[0],base[ci],y,mask)})
 pd.DataFrame(rows).to_csv(P/'acquired_only_influence.csv',index=False)
 log_event('acquired_probe_complete',{'response_files':len(list(dest.glob('*.npz'))),'rows':len(rows),'seconds':time.perf_counter()-t})
if __name__=='__main__':main()
