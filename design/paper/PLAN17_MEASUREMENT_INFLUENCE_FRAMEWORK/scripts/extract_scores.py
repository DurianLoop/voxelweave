"""New acquired-only paired scores from four stored frozen neural estimators."""
import os
os.environ.setdefault('OMP_NUM_THREADS','2');os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from common import *
import nibabel as nib
import time
def main():
 specs_=specs();sources=[];rows=[];case_rows=[];t=time.perf_counter()
 old=pd.read_csv(PAPER/'ARCHIVE/PLANS/PLAN11_CLAIM_STRENGTHENING/outputs/p11_ixi_clean_per_plane_full.csv')
 targetmap=old.groupby('case').target_z.unique().to_dict()
 for i,(ds,c,path) in enumerate(datasets(),1):
  im=nib.load(path);v=im.get_fdata(dtype=np.float32);anchors=v[:,:,::4];fs=features(anchors)
  fs['spacing']=float(im.header.get_zooms()[2]);preds={}
  sources.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
  for model in ['hat','swinir','i3net','cycleinr']:
   pp=ROOT/specs_[(ds,model)]['stored_predictions']/('diff_'+path.name)
   pi=nib.load(pp);preds[model]=pi.get_fdata(dtype=np.float32)
   assert preds[model].shape[:2]==v.shape[:2] and np.allclose(pi.affine,im.affine,atol=1e-5)
   sources.append({'path':str(pp.relative_to(ROOT)),'sha256':sha(pp)})
  zs=[3,5,7,9,11] if ds=='fastmri' else sorted(map(int,targetmap[c]))
  for a,b in [('hat','swinir'),('i3net','cycleinr')]:
   pair=a+'_'+b;local=[]
   for z in zs:
    assert z%4 and all(z<pred.shape[2] for pred in preds.values())
    left=(z//4)*4;m=fg(v[:,:,left])|fg(v[:,:,left+4])
    r={'dataset':ds,'case':c,'pair':pair,'z':z,'mask_pixels':int(m.sum()),**metrics(preds[a][:,:,z],preds[b][:,:,z],v[:,:,z],m)}
    rows.append(r);local.append(r)
   ag=pd.DataFrame(local)[['mae_a','mae_b','error','disagreement','variance','observable','error_cosine']].median().to_dict()
   rr={'dataset':ds,'case':c,'pair':pair,**fs,**ag};rr['both_error']=min(rr['mae_a'],rr['mae_b'])
   for key in ['disagreement','error','both_error','anchor_cv','adjacent_mae','adjacent_rmse']:rr[key+'_norm']=rr[key]/fs['acquired_range']
   case_rows.append(rr)
  if i%10==0 or i==1:print(f'E02 {i}/139 {ds} elapsed={time.perf_counter()-t:.1f}s',flush=True)
 pd.DataFrame(rows).to_csv(OUT/'neural_pair_per_plane.csv',index=False);pd.DataFrame(case_rows).to_csv(OUT/'neural_pair_per_case.csv',index=False)
 save('neural_score_manifest.json',{'inputs':sources,'protocol_sha256':sha(P/'PROTOCOL.md'),'script_sha256':sha(__file__),'elapsed_seconds':time.perf_counter()-t,'target_access_for_scores':False,'source_count':len(sources)})
 print('E02 feature extraction complete',flush=True)
if __name__=='__main__':main()

