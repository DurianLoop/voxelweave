"""Small synthetic checks of label permutations and QDA/LDA mathematics."""
import json,os,sys
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'): os.environ[key]='1'
import nibabel as nib
import numpy as np
from mc_rc_anchor_qda_cpu import observed_truth,fit_model,decision,METHODS,feature_plane,normalization
from verify_mc_rc_anchor_qda_cpu import visible_labels,refit,classify
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_anchor_qda_preflight'
def main():
 sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);errors=[];rows=[]
 def check(ok,why):
  if not ok: errors.append(why)
 shape=(5,6,7);native=np.zeros(shape,dtype=np.uint8);native[1:4,2:5,::2]=1
 for index,perm in enumerate([(0,1,2),(2,0,1),(1,2,0)]):
  matrix=np.zeros((4,4),dtype=int);matrix[3,3]=1;labshape=tuple(shape[a] for a in perm)
  for labaxis,nativeaxis in enumerate(perm): matrix[nativeaxis,labaxis]=-1 if labaxis==index else 1;matrix[nativeaxis,3]=shape[nativeaxis]-1 if labaxis==index else 0
  label=np.zeros(labshape,dtype=np.uint8);xyz=np.array(np.indices(labshape)).reshape(3,-1);rcz=matrix[:3,:3]@xyz+matrix[:3,3,None];label[tuple(xyz)]=native[tuple(rcz)];p=OUT/('label_'+str(index)+'.nii');nib.save(nib.Nifti1Image(label,np.eye(4)),p);case=dict(label_file=p.relative_to(ROOT).as_posix(),native_shape=list(shape),dicom_rcz_from_label_xyz=matrix.tolist());a,planes=observed_truth(case);b,other=visible_labels(case);check(np.array_equal(a,native[:,:,::4]) and np.array_equal(a,b) and planes==other,'Signed-permutation observed label mismatch '+str(index));rows.append(dict(permutation=list(perm),observed_planes=[x['native_z'] for x in planes]))
 rng=np.random.default_rng(3162026);stats=[]
 for p,series in [('P',1),('Q',2),('R',1)]:
  for s in range(series):
   x=np.vstack([rng.normal(0,.3,(300,9)),rng.normal(1,.3,(30,9))]);mass=np.array([300,30])/330;first=np.stack([x[:300].sum(0),x[300:].sum(0)])/330;second=np.stack([x[:300].T@x[:300],x[300:].T@x[300:]])/330;stats.append(dict(patient=p,uid=p+str(s),moments=dict(mass=mass.tolist(),first=first.tolist(),second=second.tolist())))
 for method in METHODS:
  model=fit_model([r for r in stats if r['patient']!='P'],method);ref=refit(stats,'P',method)
  for k in ('priors','means','covariances'): check(np.allclose(model[k],ref[k],atol=1e-12,rtol=1e-12),'Independent fit math differs '+method+' '+k)
  check({r['patient'] for r in model['training_membership']}=={'Q','R'} and abs(sum(r['series_weight'] for r in model['training_membership'])-1)<1e-12,'Patient exclusion/weights differ');test=rng.normal(.5,1,(500,9));check(np.array_equal(decision(test,model)>=0,classify(test,model)),'Cholesky vs inverse classifications differ '+method)
 plane=rng.uniform(0,500,shape[:2]).astype(np.float32);case=dict(native_shape=list(shape),native_spacing_rcz_mm=[.5,.7,1.2],affine_rcz_ras=np.diag([.5,.7,1.2,1]).tolist());features=feature_plane(plane,0,case,normalization(plane[:,:,None]));check(features.shape==(30,9) and np.isfinite(features).all(),'Physical feature extraction differs');check(np.allclose(features[:,8],-1),'RAS z bound differs')
 with (OUT/'attempt_01.json').open('x',encoding='utf-8') as f: json.dump(dict(synthetic_only=True,patient_data_used=False,gpu_used=False,label_permutations=rows,methods=list(METHODS),errors=errors,scientific_claim_confirmed=False),f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(synthetic_only=True,errors=errors)));return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
