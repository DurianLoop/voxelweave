from pathlib import Path
import json,sys,hashlib
P=Path(__file__).resolve().parents[1];B=P.parent/'FINAL_SCIENTIFIC_STRENGTHENING';ROOT=P.parents[2]
sys.path.insert(0,str(B/'scripts'))
from common import sha,write
from audit_statistics import bootstrap_indices,simultaneous
import numpy as np,pandas as pd,nibabel as nib
def main():
 x=pd.read_csv(P/'outputs/expanded_per_plane.csv');ref=x.set_index(['dataset','case','model','z','support']);rows=[];maxerr=0.;bound=0
 cases=json.loads((B/'case_registry.json').read_text());models=['linear','cubic','acvtt','ressrdiff','arssr','resunet','gan_2p5d','smamba_unet']
 for i,r in enumerate(cases):
  ds,c=r['dataset'],r['case'];v=nib.load(ROOT/r['source']).get_fdata(dtype=np.float32)
  with np.load(B/r['cross_targets']) as f:gt=f['gt'];target_mask=f['mask']
  preds={}
  for m in models:
   path=P/'outputs/expanded_phase_arrays'/f'{ds}_{m}_{c}.npz';meta=json.loads(path.with_suffix('.json').read_text());assert sha(path)==meta['sha256'];bound+=1
   with np.load(path) as f:preds[m]=(f['p0'].astype(float),f['p2'].astype(float));assert np.array_equal(f['targets'],r['targets'])
  for j,z in enumerate(r['targets']):
   pp=r['phase0'];lo=max(k for k in pp if k<z);hi=min(k for k in pp if k>z)
   masks={'target_1pct':target_mask[j],'acquired_union':np.logical_or(np.abs(v[:,:,lo])>.01*np.max(np.abs(v[:,:,lo])),np.abs(v[:,:,hi])>.01*np.max(np.abs(v[:,:,hi]))),'full_common_valid':np.ones(gt[j].shape,bool)}
   # All saved arrays and targets are finite; validate instead of implicitly changing support.
   assert np.isfinite(gt[j]).all()
   for a,b in preds.values():assert np.isfinite(a[j]).all() and np.isfinite(b[j]).all()
   for m,(a,b) in preds.items():
    common=(a[j]+b[j])*.5-gt[j].astype(float);difference=(a[j]-b[j])*.5
    for support,mask in masks.items():
     invisible=np.sum(common[mask]**2);visible=np.sum(difference[mask]**2);o=visible/(invisible+visible);r0=ref.loc[(ds,c,m,z,support)]
     err=abs(o-r0.delta_O);maxerr=max(err,maxerr);assert err<1e-12 and r0.shared_O==0 and int(mask.sum())==r0.pixels
     rows.append(dict(dataset=ds,case=c,model=m,support=support,delta_O=o))
  if i%20==0:print('INDEPENDENT PHASE',i,flush=True)
 d=pd.DataFrame(rows);summary=pd.read_csv(P/'EXPANDED_PHENOMENON_BREADTH.csv');maxci=0.
 for (ds,support),g in d.groupby(['dataset','support']):
  arr=g.groupby(['case','model']).delta_O.mean().unstack('model')[models].to_numpy();idx=bootstrap_indices(len(arr),19001 if ds=='fastmri' else 19002);pt=arr.mean(0);ci,n=simultaneous(pt,arr[idx].mean(1))
  for k,m in enumerate(models):
   r=summary[(summary.dataset==ds)&(summary.model==m)&(summary.support==support)].iloc[0]
   diff=max(abs(pt[k]-r.delta_O),abs(ci[k,0]-r.simultaneous_low),abs(ci[k,1]-r.simultaneous_high));assert diff<1e-12;maxci=max(diff,maxci)
 write(P/'outputs/expanded_independent_checks.json',dict(status='PASS',array_hashes=bound,per_plane_rows=len(rows),summary_rows=len(summary),maximum_pixel_formula_difference=maxerr,maximum_summary_difference=maxci,note='Independent common/difference energy formula; same frozen joint-bootstrap implementation, all eight models retained.'))
 print('Expanded independent PASS',bound,len(rows),maxerr,maxci,flush=True)
if __name__=='__main__':main()
