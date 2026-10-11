"""Frozen CPU diagnostic: only real MR anchors and patient-excluded label moments."""
from __future__ import annotations
import hashlib,itertools,json,os,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'): os.environ[key]='1'
import nibabel as nib
import numpy as np
from scipy import ndimage
from vs_seg_task_cpu_support import resource_gate
from vs_seg_full_volume_runtime import sha,array_sha
from mc_rc_frozen_predicted_region_cpu import decode_observed,task_counts
from mc_rc_native_competence_cpu import truth,roi_summary
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_anchor_qda_cpu'
PLAN=ROOT/'MC_RC_ANCHOR_QDA_CPU_PLAN_2026-10-03.md'
NATIVE=ROOT/'experiments/mc_rc_native_competence_cpu'
METHODS={'joint_QDA':list(range(9)),'appearance_QDA':list(range(6)),'coordinates_QDA':[6,7,8],'joint_LDA':list(range(9))}
FEATURES=['intensity','Gaussian_mean_0.5mm','Gaussian_mean_2mm','residual_1mm','local_std_1mm','physical_gradient_1mm','RAS_relative_x','RAS_relative_y','RAS_relative_z']
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prerequisites():
 r=read(NATIVE/'attempt_01.json');p=read(NATIVE/'independent_native_model_and_roi_replay.json');q=read(ROOT/'experiments/mc_rc_native_competence_queue/attempt_01.json');c=read(NATIVE/'run_contract.json')
 if not r['complete'] or r['errors'] or p['errors'] or not q['complete'] or p['counts']['fresh_neural_replays']!=17 or p['result_sha256']!=sha(NATIVE/'attempt_01.json') or p['run_contract_sha256']!=sha(NATIVE/'run_contract.json'): raise ValueError('Complete native16 proof required')
 for item in c['files']:
  if sha(ROOT/item['path'])!=item['sha256']: raise ValueError('Native input lineage mutated')
 return c
def observed_truth(case):
 image=nib.load(ROOT/case['label_file']);m=np.asarray(case['dicom_rcz_from_label_xyz'],dtype=int);axis=int(np.argmax(abs(m[2,:3])));out=np.zeros((case['native_shape'][0],case['native_shape'][1],len(range(0,case['native_shape'][2],4))),dtype=bool);decoded=[]
 if sorted(abs(m[:3,:3]).sum(0).tolist())!=[1,1,1] or sorted(abs(m[:3,:3]).sum(1).tolist())!=[1,1,1]: raise ValueError('Label mapping not signed permutation')
 for j,z in enumerate(range(0,case['native_shape'][2],4)):
  index=(z-int(m[2,3]))*int(m[2,axis]);slices=[slice(None)]*3;slices[axis]=index
  if not 0<=index<image.shape[axis]: raise ValueError('Observed label index out of bounds')
  plane=np.asarray(image.dataobj[tuple(slices)])
  if plane.nbytes>32000000 or not np.isfinite(plane).all() or not np.isin(plane,[0,1]).all(): raise ValueError('Observed label plane invalid')
  other=[a for a in range(3) if a!=axis];positions=np.array(np.nonzero(plane));xyz=np.empty((3,positions.shape[1]),dtype=int);xyz[axis]=index;xyz[other]=positions;rcz=m[:3,:3]@xyz+m[:3,3,None]
  if rcz.shape[1] and ((rcz[2]!=z).any() or (rcz[:2]<0).any() or (rcz[:2]>=np.asarray(case['native_shape'][:2])[:,None]).any()): raise ValueError('Observed label coordinates differ')
  out[rcz[0],rcz[1],j]=True;decoded.append(dict(native_z=z,label_axis=axis,label_index=index))
 return out,decoded
def normalization(anchors):
 lo,hi=np.percentile(anchors,[1.,99.]);return dict(p1=float(lo),p99=float(hi),range=max(float(hi-lo),1e-6))
def feature_plane(plane,z,case,norm):
 rows,cols=plane.shape;sp=np.asarray(case['native_spacing_rcz_mm'][:2]);v=np.clip((plane.astype(np.float32)-norm['p1'])/norm['range'],0,1)
 g1=ndimage.gaussian_filter(v,sigma=1./sp,mode='reflect',truncate=4.);var=np.maximum(ndimage.gaussian_filter(v*v,sigma=1./sp,mode='reflect',truncate=4.)-g1*g1,0);gradient=np.gradient(g1,*sp)
 channels=[v,ndimage.gaussian_filter(v,sigma=.5/sp,mode='reflect',truncate=4.),ndimage.gaussian_filter(v,sigma=2./sp,mode='reflect',truncate=4.),v-g1,np.sqrt(var),np.sqrt(gradient[0]**2+gradient[1]**2)]
 rr,cc=np.indices((rows,cols),dtype=np.float32);aff=np.asarray(case['affine_rcz_ras']);corners=np.array(list(itertools.product(*[(0,n-1) for n in case['native_shape']]))).T;world=aff[:3,:3]@corners+aff[:3,3,None];low,span=world.min(1),np.maximum(np.ptp(world,axis=1),1e-6)
 for a in range(3): channels.append((2*(aff[a,0]*rr+aff[a,1]*cc+aff[a,2]*z+aff[a,3]-low[a])/span[a]-1).astype(np.float32))
 features=np.stack([x.ravel() for x in channels],axis=1)
 if features.nbytes>100000000 or not np.isfinite(features).all(): raise ValueError('Feature budget/finite gate failed')
 return features
def moments(anchors,label,case,norm):
 n=label.size;mass=np.zeros(2);first=np.zeros((2,9));second=np.zeros((2,9,9))
 for j,z in enumerate(range(0,case['native_shape'][2],4)):
  x=feature_plane(anchors[:,:,j],z,case,norm).astype(np.float64);yy=label[:,:,j].ravel()
  for k in (0,1):
   selected=x[yy==bool(k)];mass[k]+=len(selected)/n;first[k]+=selected.sum(0)/n;second[k]+=selected.T@selected/n
 return dict(mass=mass.tolist(),first=first.tolist(),second=second.tolist(),observed_pixels=n,observed_foreground=int(label.sum()))
def fit_model(training,method):
 people=sorted({x['patient'] for x in training});mass=np.zeros(2);first=np.zeros((2,9));second=np.zeros((2,9,9));weights=[]
 for p in people:
  group=[x for x in training if x['patient']==p]
  for x in group:
   weight=1./(len(people)*len(group));s=x['moments'];mass+=weight*np.asarray(s['mass']);first+=weight*np.asarray(s['first']);second+=weight*np.asarray(s['second']);weights.append(dict(patient=p,uid=x['uid'],series_weight=weight))
 indices=METHODS[method];means=first[:,indices]/mass[:,None];covariances=[]
 if not (mass>0).all(): raise ValueError('Training class empty')
 for k in (0,1):
  c=second[k][np.ix_(indices,indices)]/mass[k]-np.outer(means[k],means[k]);c=(c+c.T)/2;covariances.append(c)
 if method=='joint_LDA': pooled=mass[0]*covariances[0]+mass[1]*covariances[1];covariances=[pooled,pooled]
 stabilized=[.9*c+.1*np.diag(np.diag(c))+1e-4*np.eye(len(indices)) for c in covariances];signs,logdets=np.linalg.slogdet(np.stack(stabilized))
 if not (signs>0).all(): raise ValueError('Training covariance not positive definite')
 return dict(method=method,feature_indices=indices,priors=mass.tolist(),means=means.tolist(),covariances=np.stack(stabilized).tolist(),precisions=np.linalg.inv(np.stack(stabilized)).tolist(),log_determinants=logdets.tolist(),training_membership=weights)
def decision(features,model):
 x=features[:,model['feature_indices']].astype(np.float64);mu=np.asarray(model['means']);prec=np.asarray(model['precisions']);logdet=np.asarray(model['log_determinants']);prior=np.asarray(model['priors']);v=[]
 for k in (0,1):
  d=x-mu[k];v.append(np.log(prior[k])-.5*logdet[k]-.5*np.einsum('ij,ij->i',d@prec[k],d))
 return v[1]-v[0]
def main():
 sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();native_contract=prerequisites();cases=native_contract['cases'];OUT.mkdir(exist_ok=False)
 paths=[PLAN,Path(__file__),NATIVE/'attempt_01.json',NATIVE/'run_contract.json',NATIVE/'independent_native_model_and_roi_replay.json',ROOT/'experiments/mc_rc_native_competence_cpu.py',ROOT/'experiments/mc_rc_frozen_predicted_region_cpu.py',ROOT/'experiments/mc_rc_observed_region_propagation.py',ROOT/'experiments/vs_seg_task_cpu_support.py',ROOT/'experiments/vs_seg_full_volume_runtime.py']+[ROOT/x['path'] for x in native_contract['files']]
 write(OUT/'run_contract.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),cases=cases,methods=METHODS,features=FEATURES,primary='joint_QDA',files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(paths))],native_MR_hidden_pixels_used=False,label_training_planes='0,4,... only',patient_exclusion='all series of held-out patient excluded',scientific_independent_validation_patients=0))
 result=dict(started_utc=datetime.now(timezone.utc).isoformat(),complete=False,active_stage='moments',resources=resources,series_statistics=[],folds=[],series=[],errors=[],gpu_used=False,hidden_MR_pixel_arrays_decoded=False,missing_label_used_for_training=False,scientific_independent_validation_patients=0,publication_claim_confirmed=False,run_contract_sha256=sha(OUT/'run_contract.json'));write(OUT/'attempt_01.json',result)
 try:
  for case in cases:
   resource_gate();anchors,sops=decode_observed(case);labels,decoded=observed_truth(case);norm=normalization(anchors);row=dict(patient=case['patient'],uid=case['uid'],observed_array_sha256=array_sha(anchors),observed_sop_uids=sops,observed_label_array_sha256=array_sha(labels),label_decoded_planes=decoded,normalization=norm,moments=moments(anchors,labels,case,norm));result['series_statistics'].append(row);write(OUT/'attempt_01.json',result);print(json.dumps(dict(stage='moments',patient=case['patient'],uid=case['uid'])),flush=True);del anchors,labels
  result['active_stage']='patient_excluded_prediction';stats={x['uid']:x for x in result['series_statistics']}
  for p in sorted({x['patient'] for x in cases}):
   training=[x for x in result['series_statistics'] if x['patient']!=p];models={method:fit_model(training,method) for method in METHODS};fold_path=OUT/(p+'_models.json');write(fold_path,models);result['folds'].append(dict(patient=p,training_patients=sorted({x['patient'] for x in training}),model_file=fold_path.relative_to(ROOT).as_posix(),model_sha256=sha(fold_path)))
   for case in [x for x in cases if x['patient']==p]:
    resource_gate();start=time.perf_counter();anchors,sops=decode_observed(case);s=stats[case['uid']]
    if array_sha(anchors)!=s['observed_array_sha256'] or sops!=s['observed_sop_uids']: raise ValueError('Prediction anchor lineage differs')
    pred={method:np.zeros(anchors.shape,dtype=bool) for method in METHODS};margins={method:float('inf') for method in METHODS}
    for j,z in enumerate(range(0,case['native_shape'][2],4)):
     features=feature_plane(anchors[:,:,j],z,case,s['normalization'])
     for method in METHODS:
      score=decision(features,models[method]);pred[method][:,:,j]=(score>=0).reshape(anchors.shape[:2]);margins[method]=min(margins[method],float(np.min(abs(score))))
    path=OUT/(case['uid']+'_anchor_predictions.npz');np.savez_compressed(path,**pred);row=dict(patient=p,uid=case['uid'],description=case['description'],prediction_file=path.relative_to(ROOT).as_posix(),prediction_sha256=sha(path),prediction_array_sha256={k:array_sha(v) for k,v in pred.items()},minimum_absolute_log_likelihood_ratio=margins,predictions_saved_before_full_label_scoring=True);write(OUT/(case['uid']+'_predictions_before_full_label.json'),row);del anchors
    ref=truth(case);edge=ref&~ndimage.binary_erosion(ref,structure=ndimage.generate_binary_structure(3,1),border_value=0);n=case['native_shape'][2];targets=[z for z in range(1,(n-1)//4*4) if z%4];row.update(missing_targets=len(targets),methods={})
    for method in METHODS:
     full=np.zeros(case['native_shape'],dtype=bool);full[:,:,::4]=pred[method];row['methods'][method]=dict(observed_task=task_counts(full,ref,np.arange(0,n,4)),roi=roi_summary(full,ref,edge,case,targets));del full
    row.update(complete=True,seconds=time.perf_counter()-start);result['series'].append(row);write(OUT/'attempt_01.json',result);print(json.dumps(dict(stage='predicted_and_scored',patient=p,uid=case['uid'],primary_gate_passed=row['methods']['joint_QDA']['roi']['gate_passed'],seconds=row['seconds'])),flush=True);del ref,edge,pred
  result['complete']=len(result['series'])==16;result['summary']={method:dict(roi_gate_passed=sum(x['methods'][method]['roi']['gate_passed'] for x in result['series']),series=16,patient_equal_observed_dice=float(np.mean([np.mean([x['methods'][method]['observed_task']['dice'] for x in result['series'] if x['patient']==p]) for p in sorted({x['patient'] for x in cases})]))) for method in METHODS};result['active_stage']='complete'
 except Exception as exc: result.update(active_stage='failed',traceback=traceback.format_exc());result['errors'].append(type(exc).__name__+': '+str(exc))
 result['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',result);print(json.dumps(dict(complete=result['complete'],errors=result['errors'],summary=result.get('summary'))),flush=True);return int(not result['complete'])
if __name__=='__main__': raise SystemExit(main())
