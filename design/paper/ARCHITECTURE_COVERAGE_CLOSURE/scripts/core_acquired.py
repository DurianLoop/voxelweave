"""Exact acquired-only contract, SAINT interface; target access only after file binding."""
from pathlib import Path
import sys,json,datetime,time,gc
P=Path(__file__).resolve().parents[1];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING'
sys.path.insert(0,str(B/'scripts'))
from common import read,write,sha,load_net,CONTEXTS,SEEDS,REF,metrics
from acquired_probe import inputs,patterns,influence
import numpy as np,pandas as pd,torch
from skimage.transform import resize

def conditions(net,pool,z,depth,ctx,anchor=None,fields=None,epsilon=0):
 u=-ctx[0]/(ctx[1]-ctx[0]);out=[]
 for field in ([None] if fields is None else fields):
  aa=[pool[z+o] if o!=anchor else np.clip(pool[z+o]+epsilon*field,0,1) for o in ctx]
  out.append(np.stack([*aa,np.full((256,256),u,np.float32),np.full((256,256),z/(depth-1),np.float32),net.y_map,net.x_map]))
 return out
def predict(net,conds,shape,lo,scale,batch=8):
 out=[]
 for i in range(0,len(conds),batch):
  x=torch.from_numpy(np.stack(conds[i:i+batch])).to(net.device)
  with torch.inference_mode():qs=net.model(x).float().clamp(0,1)[:,0].cpu().numpy()
  out.extend([(resize(q,shape,preserve_range=True,anti_aliasing=True)*scale+lo).astype(np.float32) for q in qs])
 return np.stack(out)
def compute(net,path,z,depth):
 pool,lo,scale,mask=inputs(path);pats=patterns();epsilons=[.01,.005,.02,-.01]
 cs=[conditions(net,pool,z,depth,c)[0] for c in CONTEXTS]
 base=predict(net,cs,mask.shape,lo,scale);responses=[]
 for eps in epsilons:
  arr=[]
  for ci,ctx in enumerate(CONTEXTS):
   cs=[]
   for anchor in ctx:cs.extend(conditions(net,pool,z,depth,ctx,anchor,pats,eps))
   q=predict(net,cs,mask.shape,lo,scale)
   arr.append((q-base[ci])[...,mask].reshape(2,4,-1))
  responses.append(np.stack(arr))
 return dict(base=base,response=np.stack(responses),mask=mask,epsilons=np.array(epsilons),contexts=np.array(CONTEXTS),lo=lo,scale=scale)
def main():
 assert read(P/'outputs/frozen_array_verification.json')['status']=='PASS'
 assert read(P/'freeze.json')['protocol_sha256']==sha(P/'PROTOCOL.md')
 torch.set_num_threads(2);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 dest=P/'outputs/acquired_responses';dest.mkdir(exist_ok=True);t=time.perf_counter();cases=read(B/'case_registry.json')
 for ds in ['ixi','fastmri']:
  net=load_net(ds,'saint')
  for i,r in enumerate([x for x in cases if x['dataset']==ds],1):
   for z in r['influence_targets']:
    path=dest/f'{ds}_saint_{r["case"]}_z{z}.npz'
    if path.exists() and path.with_suffix('.json').exists():
     assert read(path.with_suffix('.json'))['sha256']==sha(path);continue
    inp=B/'inputs'/f'{ds}_{r["case"]}_z{z}.npz';d=compute(net,inp,z,r['depth'])
    assert np.isfinite(d['base']).all() and np.isfinite(d['response']).all()
    np.savez_compressed(path,**d)
    write(path.with_suffix('.json'),{'dataset':ds,'model':'saint','case':r['case'],'z':z,'depth':r['depth'],'sha256':sha(path),'input_sha256':sha(inp),'utc_before_target_access':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':sha(Path(__file__)),'information_contract':'acquired-only','threshold':.90})
   print('SAINT ACQUIRED',ds,i,r['case'],'seconds',round(time.perf_counter()-t),flush=True)
  del net;gc.collect();torch.cuda.empty_cache()
 rows=[]
 for path in sorted(dest.glob('*.npz')):
  meta=read(path.with_suffix('.json'))
  assert sha(path)==meta['sha256']
  with np.load(path) as f:
   y=np.load(B/'targets'/f'{meta["dataset"]}_{meta["case"]}_z{meta["z"]}.npy')
   for ei,eps in enumerate(f['epsilons']):
    for ci,ctx in enumerate(CONTEXTS[1:],1):
     rows.append({k:meta[k] for k in ['dataset','model','case','z']}|dict(epsilon=eps,context=str(ctx),span=ctx[1]-ctx[0],asymmetry=abs(sum(ctx)),overlap_count=len(set(REF)&set(ctx)),influence=influence(f['response'][ei],ci),source_hash=meta['sha256'],**metrics(f['base'][0],f['base'][ci],y,f['mask'])))
 pd.DataFrame(rows).to_csv(P/'outputs/saint_acquired_observations.csv',index=False)
 print('SAINT COMPLETE',len(rows),flush=True)
if __name__=='__main__':main()
