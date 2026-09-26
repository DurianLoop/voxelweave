"""Reproduce old headline inputs, not a new scientific hypothesis/analysis."""
from common import *
import nibabel as nib,torch,time,gc
from skimage.transform import resize

def legacy_residual(net,conditions):
 t=torch.from_numpy(np.stack(conditions)).float().to(net.device).contiguous(memory_format=torch.channels_last)
 with torch.no_grad(),torch.amp.autocast(device_type='cuda',enabled=True):q=net.model(t).float().clamp(-1,1)
 return q[:,0].cpu().numpy()

def legacy_responses(net,gt,z):
 lo=float(np.nanmin(gt));hi=float(np.nanmax(gt));norm=((gt-lo)/(hi-lo+1e-8)).astype(np.float32);y=gt[:,:,z];mask=abs(y)>.01*max(float(abs(y).max()),1e-6);pats=[]
 for s in SEEDS:
  x=np.random.default_rng(s).choice([-1.,1.],size=(256,256)).astype(np.float32);x-=x.mean();pats.append(x)
 preds=[];responses=[]
 for ctx in CONTEXTS:
  left=resize(norm[:,:,z+ctx[0]],(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32);right=resize(norm[:,:,z+ctx[1]],(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32);u=-ctx[0]/(ctx[1]-ctx[0])
  def cond(a,b):return np.stack([a,b,(1-u)*a+u*b,np.full((256,256),u,np.float32)])
  c=cond(left,right);res=legacy_residual(net,[c])[0];base=resize(np.clip(c[2]+res,0,1),gt.shape[:2],preserve_range=True,anti_aliasing=True)*(hi-lo)+lo;preds.append(base);rr=[]
  for ai in range(2):
   cs=[cond(np.clip(left+.01*p,0,1) if ai==0 else left,np.clip(right+.01*p,0,1) if ai==1 else right) for p in pats];predres=legacy_residual(net,cs);v=[]
   for cc,r in zip(cs,predres):
    q=resize(np.clip(cc[2]+r,0,1),gt.shape[:2],preserve_range=True,anti_aliasing=True)*(hi-lo)+lo;v.append((q-base)[mask].astype(np.float32))
   rr.append(np.stack(v))
  responses.append(np.stack(rr))
 return {'predictions':np.stack(preds),'responses':np.stack(responses),'target':y,'mask':mask,'contexts':np.array(CONTEXTS)}

def main():
 guard();torch.set_num_threads(2);legacy=load_module('legacy_p6_for_weights',PAPER/'CVPR/archive/CVPR_UPGRADE/scripts/plan6_neural_shared_influence.py');legacy.ROOT=ROOT
 phase=OUT/'legacy_control_arrays';phase.mkdir(exist_ok=True);resp=OUT/'legacy_influence_arrays';resp.mkdir(exist_ok=True)
 registry=pd.read_csv(P/'historical_case_registry.csv').sort_values(['dataset','architecture','split','case_id']);key=None;net=None;t=time.perf_counter()
 log_event('historical_array_reproduction_start',{'script_sha256':sha(Path(__file__)),'scientific_role':'repeat recorded analysis only, no new hypothesis or score'})
 for i,r in enumerate(registry.itertuples(),1):
  ck=legacy.checkpoint(r,r.architecture);k=(r.dataset,r.architecture,str(ck))
  if k!=key:
   if net is not None:del net;gc.collect();torch.cuda.empty_cache()
   net=legacy.load_net(r.dataset,r.architecture,ck,'cuda');key=k
  c=r.case_id.replace('.nii.gz','');stem=f'{r.dataset}_{r.architecture}_{c}';file=phase/(stem+'.npz');gt=nib.load(r.ground_truth_file).get_fdata(dtype=np.float32)
  if not file.exists():
   p0=nib.load(r.source_file).get_fdata(dtype=np.float32);pf=net.interpolate_volume(np.ascontiguousarray(gt[:,:,::4][::-1]),stride=4)[::-1];p2=net.interpolate_volume(np.ascontiguousarray(gt[:,:,2::4]),stride=4)
   np.savez_compressed(file,p0=p0,flip=pf,p2=p2,target=gt)
   write(file.with_suffix('.json'),{'sha256':sha(file),'dataset':r.dataset,'model':r.architecture,'case':r.case_id,'patient_cluster':r.patient_cluster,'checkpoint_sha256':sha(ck),'target_sha256':sha(Path(r.ground_truth_file))})
  zs=sorted(set(int(round(z)) for z in np.linspace(3,gt.shape[2]-4,5)[1:-1]))
  for z in zs:
   file=resp/f'{stem}_z{z}.npz'
   if file.exists():continue
   data=legacy_responses(net,gt,z);np.savez_compressed(file,**data);write(file.with_suffix('.json'),{'sha256':sha(file),'dataset':r.dataset,'model':r.architecture,'case':r.case_id,'patient_cluster':r.patient_cluster,'z':z,'checkpoint_sha256':sha(ck)})
  print('LEGACY ARRAYS',i,len(registry),stem,'elapsed',round(time.perf_counter()-t),flush=True)
 log_event('historical_array_reproduction_complete',{'cases_models':len(registry),'seconds':time.perf_counter()-t})
if __name__=='__main__':main()
