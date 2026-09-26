"""Secondary non-core phase sensitivity, unchanged estimators and master x4 weights."""
from pathlib import Path
import sys,json,time,gc,datetime,importlib,argparse
P=Path(__file__).resolve().parents[1];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING';ROOT=P.parents[2]
sys.path.insert(0,str(B/'scripts'))
from common import read,write,sha,wrappers
import numpy as np,nibabel as nib,torch
from skimage.transform import resize
from ixi_diffusion.common import normalize_volume
from topcow_diffusion.baselines import _upsample_z
MODELS=['linear','cubic','acvtt','ressrdiff','arssr','resunet','gan_2p5d','smamba_unet']
def load(ds,m):
 if m in ['linear','cubic']:return None
 spec=next(r for r in read(P/'model_registry.json') if r['dataset']==ds and r['model']==m)
 assert sha(ROOT/spec['checkpoint'])==spec['sha256']
 mod,cls={'acvtt':('ixi_acvtt_2p5d.train','ACVTT2p5DInterpolator'),'ressrdiff':('ixi_ressrdiff_2p5d.train','ResSRDiff2p5DInterpolator'),'arssr':('ixi_arssr.inference','ArSSRInterpolator'),'resunet':('ixi_diffusion.resunet','ResUNetResidualInterpolator'),'gan_2p5d':('gan_2p5d.inference','GAN2p5DInterpolator'),'smamba_unet':('ixi_smamba_unet_2p5d.train','SMambaUNet2p5DInterpolator')}[m]
 return getattr(importlib.import_module(mod),cls)(ROOT/spec['checkpoint'],device='cuda')
def full(net,m,a):
 if m in ['linear','cubic']:return _upsample_z(a,4,m)
 if m=='gan_2p5d':return net.interpolate_sparse_volume(a,stride=4)
 return net.interpolate_volume(a,stride=4)
def targets(net,m,a,zs):
 if m in ['linear','cubic','ressrdiff']:
  # Preserve the complete sampler draw order, including unused planes.
  torch.manual_seed(20260914);return np.moveaxis(full(net,m,a)[:,:,zs],2,0)
 norm,lo,hi=normalize_volume(a);out=[]
 if m=='arssr':
  from ixi_arssr.data import _resize_volume
  from ixi_arssr.inference import _densify_sparse
  dense=_densify_sparse(_resize_volume(norm,net.input_size),stride=4)
  t=torch.from_numpy(dense[None,None].astype(np.float32)).to(net.device)
  with torch.inference_mode():
   features=net.model.encoder(t)
   for z in zs:
    yy,xx=np.meshgrid(np.arange(256,dtype=np.float32),np.arange(256,dtype=np.float32),indexing='ij')
    c=np.stack([xx.ravel()/255*2-1,yy.ravel()/255*2-1,(np.full(65536,z,np.float32)/max(dense.shape[0]-1,1)*2.0-1.0)],axis=1)
    c=torch.from_numpy(c[None]).to(net.device);grid=c.view(1,-1,1,1,3)
    feat=torch.nn.functional.grid_sample(features,grid,mode='bilinear',padding_mode='border',align_corners=True).squeeze(-1).squeeze(-1).permute(0,2,1)
    base=torch.nn.functional.grid_sample(t,grid,mode='bilinear',padding_mode='border',align_corners=True).squeeze(-1).squeeze(-1).permute(0,2,1)
    q=(base+.05*torch.tanh(net.model.mlp(torch.cat([feat,base,c],dim=-1)))).clamp(0,1)[0,:,0].cpu().numpy().reshape(256,256)
    out.append(resize(q,a.shape[:2],preserve_range=True,anti_aliasing=True)*(hi-lo)+lo)
  return np.asarray(out,np.float32)
 for z in zs:
  j=int(z)//4;off=int(z)%4;u=float(off)/4
  left=resize(norm[:,:,j],(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32)
  right=resize(norm[:,:,j+1],(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32)
  coarse=((1-u)*left+u*right).astype(np.float32)
  if m=='gan_2p5d':
   cond=np.stack([left,right,np.full((256,256),(j+.5)/(a.shape[2]-1),np.float32),*[np.full((256,256),k/4,np.float32) for k in [1,2,3]]])
   with torch.inference_mode():q=net.generator(torch.from_numpy(cond[None]).to(net.device))[0][0,off-1].float().cpu().numpy()
   out.append(np.clip(resize(q,a.shape[:2],preserve_range=True,anti_aliasing=True),0,1)*(hi-lo)+lo);continue
  cond=np.stack([left,right,coarse,np.full((256,256),u,np.float32)])
  if m=='acvtt':q=net._predict(cond)
  elif m=='smamba_unet':q=np.clip(coarse+net._predict_residual(cond),0,1)
  else:q=np.clip(coarse+net._predict_residual(torch.from_numpy(cond[None]).to(net.device)),0,1)
  out.append(resize(q,a.shape[:2],preserve_range=True,anti_aliasing=True)*(hi-lo)+lo)
 return np.asarray(out,np.float32)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--models',nargs='+',choices=MODELS,default=MODELS);args=ap.parse_args()
 assert read(P/'outputs/frozen_array_verification.json')['status']=='PASS'
 torch.set_num_threads(2);dest=P/'outputs/expanded_phase_arrays';dest.mkdir(exist_ok=True)
 _,p11=wrappers();cases=read(B/'case_registry.json');t=time.perf_counter();validation=read(P/'outputs/expanded_wrapper_checks_arssr_v2.json') if (P/'outputs/expanded_wrapper_checks_arssr_v2.json').exists() else [];failures=[]
 for ds in ['fastmri','ixi']:
  for m in args.models:
   try:net=load(ds,m)
   except Exception as e:
    failures.append(dict(dataset=ds,model=m,stage='load',reason=repr(e)));write(P/'outputs/expanded_failures_arssr_v2.json',failures);print('LOAD FAILED',ds,m,repr(e),flush=True);continue
   for i,r in enumerate([r for r in cases if r['dataset']==ds],1):
    path=dest/f'{ds}_{m}_{r["case"]}.npz'
    if path.exists() and path.with_suffix('.json').exists():continue
    try:
     im=nib.load(ROOT/r['source']);v=im.get_fdata(dtype=np.float32);a0=np.ascontiguousarray(v[:,:,r['phase0']]);a2=np.ascontiguousarray(v[:,:,r['phase2']])
     rt=lambda a:p11.nifti_roundtrip(a,im.affine,im.header) if ds=='ixi' else a
     a0,a2=rt(a0),rt(a2);zs=np.array(r['targets'])
     q0=targets(net,m,a0,zs);q2=targets(net,m,a2,zs-2)
     if i==1:
      torch.manual_seed(20260914);original=full(net,m,a0)
      diff=float(abs(q0-np.moveaxis(original[:,:,zs],2,0)).max())
      repeat=targets(net,m,a0,zs);rep=float(abs(repeat-q0).max())
      # Native numerical tolerance fixed here before the first comparison.
      tolerance=1e-4;row=dict(dataset=ds,model=m,selected_plane_max_difference=diff,repeat_max_difference=rep,tolerance=tolerance)
      validation.append(row);write(P/'outputs/expanded_wrapper_checks_arssr_v2.json',validation)
      assert diff<=tolerance and rep<=tolerance,row
     # Same-model exact-repeat shared control is algebraically zero by design.
     assert np.isfinite(q0).all() and np.isfinite(q2).all()
     np.savez_compressed(path,p0=q0,p2=q2,targets=zs)
     write(path.with_suffix('.json'),dict(dataset=ds,model=m,case=r['case'],sha256=sha(path),source_sha256=sha(ROOT/r['source']),script_sha256=sha(Path(__file__)),fixed_rng_seed=20260914 if m=='ressrdiff' else None,shared_control='identical frozen output; deterministic-repeat check on first registry case',utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
     print('EXPANDED',ds,m,i,r['case'],'seconds',round(time.perf_counter()-t),flush=True)
    except Exception as e:
     failures.append(dict(dataset=ds,model=m,case=r['case'],stage='phase',reason=repr(e)));write(P/'outputs/expanded_failures_arssr_v2.json',failures);print('PHASE FAILED',ds,m,r['case'],repr(e),flush=True);break
   del net;gc.collect();torch.cuda.empty_cache()
 write(P/'outputs/expanded_failures_arssr_v2.json',failures);print('EXPANDED COMPLETE',len(list(dest.glob('*.npz'))),'failures',len(failures),flush=True)
if __name__=='__main__':main()
