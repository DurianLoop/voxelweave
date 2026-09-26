"""Analysis 1 inputs and historical replication arrays; never select pairs."""
from common import *
import nibabel as nib,torch,gc,time
import torch.nn.functional as F
guard();torch.set_num_threads(2)
ARR=P/'outputs/phase_arrays';ARR.mkdir(exist_ok=True)

def cache_cycle_encoder(net):
 original=net.model.forward;cached={};verified=[False]
 def forward(volume,coords):
  # Exact common-subexpression reuse for a fixed input; no model change.
  key=(volume.data_ptr(),tuple(volume.shape))
  if cached.get('key')!=key:
   cached.clear();cached['key']=key;cached['volume']=volume;cached['features']=net.model.encoder(volume)
  grid=coords.view(coords.shape[0],coords.shape[1],1,1,3)
  features=F.grid_sample(cached['features'],grid,mode='bilinear',padding_mode='border',align_corners=True).squeeze(-1).squeeze(-1).permute(0,2,1)
  base=F.grid_sample(volume,grid,mode='bilinear',padding_mode='border',align_corners=True).squeeze(-1).squeeze(-1).permute(0,2,1)
  out=base+.05*torch.tanh(net.model.mlp(torch.cat([features,base,coords],dim=-1)))
  if not verified[0]:
   ref=original(volume,coords);diff=float((ref-out).abs().max());assert diff==0,diff
   log_event('cycle_encoder_cache_equivalence',{'maximum_difference':diff});verified[0]=True
  return out
 net.model.forward=forward

def main():
 p9,p11=wrappers();cases=read(P/'case_registry.json');specs={(r['dataset'],r['model']):r for r in read(P/'model_registry.json')}
 log_event('phase_inference_start',{'script_sha256':sha(Path(__file__)),'common_sha256':sha(P/'scripts/common.py'),'protocol_sha256':sha(P/'FINAL_ITERATION_PROTOCOL.md')})
 validations=[];t=time.perf_counter()
 for ds in ['fastmri','ixi']:
  for name in MODELS:
   net=(p9 if ds=='fastmri' else p11).load_interpolator(name,'cuda')
   if name=='cycleinr':cache_cycle_encoder(net)
   for i,r in enumerate([r for r in cases if r['dataset']==ds],1):
    c=r['case'];dst=ARR/f'{ds}_{name}_{c}.npz'
    if dst.exists():continue
    try:
     im=nib.load(ROOT/r['source']);v=im.get_fdata(dtype=np.float32);a0=np.ascontiguousarray(v[:,:,r['phase0']]);a2=np.ascontiguousarray(v[:,:,r['phase2']])
     rt=lambda a:p11.nifti_roundtrip(a,im.affine,im.header) if ds=='ixi' else a
     a0=rt(a0);a2=rt(a2)
     stored=nib.load(ROOT/specs[(ds,name)]['stored_predictions']/('diff_'+Path(r['source']).name)).get_fdata(dtype=np.float32)
     reg=rt(net.interpolate_volume(a0,stride=4));diff=float(abs(stored-reg).max());mae=float(abs(stored-reg).mean())
     validation={'dataset':ds,'model':name,'case':c,'max_abs':diff,'mae':mae,'tolerance':1e-4,'pass':diff<=1e-4}
     validations.append(validation)
     if not validation['pass']:
      log_event('phase0_reproduction_mismatch',validation)
      # Preserve arrays and report mismatch; never silently adopt a new baseline.
     pf=rt(net.interpolate_volume(np.ascontiguousarray(a0[::-1]),stride=4)[::-1])
     if name=='saint':
      p0=rt(p11.saint_interpolate_with_physical_origin(net,a0,4,0,r['depth']))
      p2=rt(p11.saint_interpolate_with_physical_origin(net,a2,4,2,r['depth']))
      p2legacy=rt(net.interpolate_volume(a2,stride=4)) if ds=='fastmri' else p2
     else:p0=stored;p2=rt(net.interpolate_volume(a2,stride=4));p2legacy=p2
     zs=np.array(r['targets']);n=p0.shape[2]
     assert np.isfinite(p0).all() and np.isfinite(p2).all() and p0.shape[:2]==p2.shape[:2]==v.shape[:2]
     # Complete HAT/SwinIR fields allow all historical target supports to be audited.
     if name in ['hat','swinir']:
      np.savez_compressed(dst,p0=p0,p0_legacy=stored,p0_regenerated=reg,flip=pf,p2=p2,p2_legacy=p2legacy,targets=zs,full_arrays=True)
     else:
      np.savez_compressed(dst,p0=np.stack([p0[:,:,z] for z in zs]),p0_legacy=np.stack([stored[:,:,z] for z in zs]),p0_regenerated=np.stack([reg[:,:,z] for z in zs]),flip=np.stack([pf[:,:,z] for z in zs]),p2=np.stack([p2[:,:,z-2] for z in zs]),p2_legacy=np.stack([p2legacy[:,:,z-2] for z in zs]),targets=zs,full_arrays=False)
     write(dst.with_suffix('.json'),{'dataset':ds,'model':name,'case':c,'sha256':sha(dst),'validation':validation,'full_shape':list(p0.shape),'saint_coordinate_correction':name=='saint','protocol_sha256':sha(P/'FINAL_ITERATION_PROTOCOL.md')})
     print('PHASE',ds,name,i,c,'check',diff,'elapsed',round(time.perf_counter()-t),flush=True)
    except Exception as e:
     log_event('phase_array_failure',{'dataset':ds,'model':name,'case':c,'reason':repr(e)})
     raise
   del net;gc.collect();torch.cuda.empty_cache()
 pd.DataFrame([read(f)['validation'] for f in ARR.glob('*.json')]).to_csv(P/'outputs/phase_wrapper_verification.csv',index=False)
 log_event('phase_inference_complete',{'files':len(list(ARR.glob('*.npz'))),'seconds':time.perf_counter()-t})
if __name__=='__main__':main()
