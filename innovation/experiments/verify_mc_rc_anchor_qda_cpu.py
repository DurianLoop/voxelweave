"""All anchors replay with independent label indexing, moments and Cholesky scores."""
import json,os,sys
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'): os.environ[key]='1'
import nibabel as nib
import numpy as np
from vs_seg_task_cpu_support import resource_gate
from vs_seg_full_volume_runtime import sha,array_sha
from mc_rc_anchor_qda_cpu import feature_plane,normalization,METHODS
from verify_mc_rc_frozen_predicted_region_cpu import independently_decode,raw_truth,explicit_boundary
from verify_mc_rc_native_competence_cpu import competence
from verify_mc_rc_observed_region_propagation import disk_dilation,measure,derived
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_anchor_qda_cpu'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def visible_labels(case):
 image=nib.load(ROOT/case['label_file']);inverse=np.rint(np.linalg.inv(np.asarray(case['dicom_rcz_from_label_xyz']))).astype(int);shape=case['native_shape'];rr,cc=np.indices(shape[:2]);coords=np.stack([rr.ravel(),cc.ravel(),np.zeros(rr.size,dtype=int)]);labels=[];indices=[]
 for z in range(0,shape[2],4):
  coords[2]=z;xyz=inverse[:3,:3]@coords+inverse[:3,3,None];fixed=[a for a in range(3) if np.ptp(xyz[a])==0]
  if len(fixed)!=1: raise ValueError('Independent observed plane mapping differs')
  axis=fixed[0];index=int(xyz[axis,0]);selection=[slice(None)]*3;selection[axis]=index;plane=np.asarray(image.dataobj[tuple(selection)])
  if not np.isfinite(plane).all() or not np.isin(plane,[0,1]).all() or plane.nbytes>32000000: raise ValueError('Independent observed label invalid')
  labels.append(plane[tuple(xyz[a] for a in range(3) if a!=axis)].reshape(shape[:2]).astype(bool));indices.append(dict(native_z=z,label_axis=axis,label_index=index))
 return np.stack(labels,axis=2),indices
def centered_moments(anchors,labels,case,norm):
 total=labels.size;mass=np.zeros(2);first=np.zeros((2,9));second=np.zeros((2,9,9))
 for j,z in enumerate(range(0,case['native_shape'][2],4)):
  x=feature_plane(anchors[:,:,j],z,case,norm).astype(np.float64);y=labels[:,:,j].ravel()
  for k in (0,1):
   sample=x[y==bool(k)];count=len(sample)
   if not count: continue
   avg=sample.mean(0);center=sample-avg;mass[k]+=count/total;first[k]+=count*avg/total;second[k]+=(center.T@center+count*np.outer(avg,avg))/total
 return dict(mass=mass.tolist(),first=first.tolist(),second=second.tolist(),observed_pixels=total,observed_foreground=int(labels.sum()))
def refit(stats,patient,method):
 train=[s for s in stats if s['patient']!=patient];people=sorted({s['patient'] for s in train});prior=np.zeros(2);first=np.zeros((2,9));second=np.zeros((2,9,9));membership=[]
 for s in train:
  w=1/(len(people)*sum(v['patient']==s['patient'] for v in train));m=s['moments'];prior+=w*np.asarray(m['mass']);first+=w*np.asarray(m['first']);second+=w*np.asarray(m['second']);membership.append(dict(patient=s['patient'],uid=s['uid'],series_weight=w))
 ix=METHODS[method];means=np.take(first,ix,axis=1)/prior[:,None];cov=[]
 for k in (0,1):
  c=np.take(np.take(second[k],ix,axis=0),ix,axis=1)/prior[k]-np.outer(means[k],means[k]);cov.append((c+c.T)/2)
 if method=='joint_LDA': common=sum(prior[k]*cov[k] for k in (0,1));cov=[common,common]
 covariance=np.stack([.9*c+.1*np.diag(np.diag(c))+1e-4*np.eye(len(ix)) for c in cov]);return dict(priors=prior,means=means,covariances=covariance,training_membership=membership)
def classify(x,model):
 values=[];features=x[:,METHODS[model['method']]].astype(np.float64)
 for k in (0,1):
  chol=np.linalg.cholesky(np.asarray(model['covariances'])[k]);whiten=np.linalg.solve(chol,(features-np.asarray(model['means'])[k]).T);values.append(np.log(model['priors'][k])-np.log(np.diag(chol)).sum()-.5*(whiten*whiten).sum(0))
 return values[1]-values[0]>=0
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();result=read(OUT/'attempt_01.json');contract=read(OUT/'run_contract.json');path=OUT/'independent_anchor_qda_replay.json'
 if path.exists() or not result['complete'] or result['errors'] or len(result['series'])!=16 or len(result['folds'])!=8: raise ValueError('Require completed all16/eightfold result; never overwrite proof')
 errors=[];statistics=[];records=[];source={x['uid']:x for x in result['series_statistics']};by={x['uid']:x for x in result['series']}
 def check(ok,why):
  if not ok: errors.append(why)
 def close(a,b,why): check(np.allclose(np.asarray(a),np.asarray(b),rtol=1e-10,atol=1e-11),'Numeric replay differs '+why)
 check(sha(OUT/'run_contract.json')==result['run_contract_sha256'],'Result contract differs')
 for f in contract['files']: check(sha(ROOT/f['path'])==f['sha256'],'Frozen input changed '+f['path'])
 for case in contract['cases']:
  resource_gate();anchors,sops,headers=independently_decode(case);labels,indices=visible_labels(case);stored=source[case['uid']];norm=normalization(anchors)
  check(array_sha(anchors)==stored['observed_array_sha256'] and sops==stored['observed_sop_uids'],'Observed raw MR differs '+case['uid']);check(array_sha(labels)==stored['observed_label_array_sha256'] and indices==stored['label_decoded_planes'],'Observed-only label mapping differs '+case['uid']);check(norm==stored['normalization'],'Observed normalization differs '+case['uid']);m=centered_moments(anchors,labels,case,norm)
  for key in m: close(m[key],stored['moments'][key],case['uid']+' '+key)
  statistics.append(dict(patient=case['patient'],uid=case['uid'],moments=m));del anchors,labels;print(json.dumps(dict(stage='independent_moments',patient=case['patient'],uid=case['uid'])),flush=True)
 for fold in result['folds']:
  p=fold['patient'];models=read(ROOT/fold['model_file']);check(sha(ROOT/fold['model_file'])==fold['model_sha256'],'Model hash differs '+p);check(len(fold['training_patients'])==7 and p not in fold['training_patients'],'Patient exclusion differs '+p)
  for method,model in models.items():
   ref=refit(statistics,p,method);check(sorted(model['training_membership'],key=lambda r:r['uid'])==sorted(ref['training_membership'],key=lambda r:r['uid']),'Entire-patient model membership differs '+p+' '+method)
   for key in ('priors','means','covariances'): close(ref[key],model[key],p+' '+method+' '+key)
   check(model['feature_indices']==METHODS[method] and model['method']==method,'Frozen model feature selection differs');cov=np.asarray(model['covariances']);precision=np.asarray(model['precisions']);close(cov@precision,np.broadcast_to(np.eye(cov.shape[1]),cov.shape),p+' '+method+' inverse');close(np.linalg.slogdet(cov)[1],model['log_determinants'],p+' '+method+' logdet')
  for case in [c for c in contract['cases'] if c['patient']==p]:
   resource_gate();stored=by[case['uid']];anchors,sops,headers=independently_decode(case);pack=np.load(ROOT/stored['prediction_file']);check(sha(ROOT/stored['prediction_file'])==stored['prediction_sha256'],'Prediction file differs');pred={method:np.zeros(anchors.shape,dtype=bool) for method in models}
   for j,z in enumerate(range(0,case['native_shape'][2],4)):
    features=feature_plane(anchors[:,:,j],z,case,source[case['uid']]['normalization'])
    for method,model in models.items(): pred[method][:,:,j]=classify(features,model).reshape(anchors.shape[:2])
   for method in models: check(np.array_equal(pred[method],pack[method]) and array_sha(pred[method])==stored['prediction_array_sha256'][method],'Fresh Cholesky prediction differs '+case['uid']+' '+method)
   pack.close();del anchors;ref=raw_truth(case,dict(grid=dict(dicom_rcz_from_label_xyz=case['dicom_rcz_from_label_xyz'])));edge=explicit_boundary(ref);n=case['native_shape'][2];targets=[z for z in range(1,(n-1)//4*4) if z%4]
   for method in models:
    full=np.zeros(case['native_shape'],dtype=bool);full[:,:,::4]=pred[method];task=competence(full,ref,range(0,n,4));check(task==stored['methods'][method]['observed_task'],'Observed task counts differ');roi=stored['methods'][method]['roi'];sums={k:0 for k in roi['target_records'][0]['counts']};fg=0;boundary=0
    for index,z in enumerate(targets):
     left=z//4*4;mask=disk_dilation(full[:,:,left]|full[:,:,left+4],case['native_spacing_rcz_mm'][:2],2.);counts=measure(mask,ref[:,:,z],edge[:,:,z]);check(roi['target_records'][index]['z']==z and counts==roi['target_records'][index]['counts'],'All-target physical disk ROI differs '+case['uid']+' '+method+' '+str(z))
     for k,v in counts.items(): sums[k]+=v
     fg+=int(ref[:,:,z].sum());boundary+=int(edge[:,:,z].sum())
    metrics=derived(sums,fg,boundary,len(targets)*ref.shape[0]*ref.shape[1]);check(metrics==roi['metrics'],'Derived ROI rates differ');gate=bool(metrics['foreground_recall']>=.99 and metrics['boundary_recall']>=.99 and metrics['tile_foreground_recall']>=.995 and metrics['roi_fraction']<=.05 and metrics['tile_fraction']<=.1);check(gate==roi['gate_passed'],'Frozen ROI gate differs');del full
   records.append(dict(patient=p,uid=case['uid'],observed_planes=len(range(0,n,4)),original_DICOM_headers=headers,missing_targets=len(targets),methods_replayed=len(models)));print(json.dumps(dict(stage='independent_prediction_ROI',**records[-1])),flush=True);del ref,edge,pred
 for method in METHODS:
  check(sum(x['methods'][method]['roi']['gate_passed'] for x in result['series'])==result['summary'][method]['roi_gate_passed'],'All-source gate total differs');people=sorted({x['patient'] for x in records});mean=sum(sum(x['methods'][method]['observed_task']['dice'] for x in result['series'] if x['patient']==p)/sum(x['patient']==p for x in records) for p in people)/len(people);close(mean,result['summary'][method]['patient_equal_observed_dice'],'Patient-equal task mean')
 proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),verification_script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),run_contract_sha256=sha(OUT/'run_contract.json'),counts=dict(series=len(records),patients=8,methods=4,fresh_anchor_classifications=sum(x['observed_planes']*4 for x in records),missing_targets=sum(x['missing_targets'] for x in records)),series=records,errors=errors,gpu_used=False,scientific_independent_validation_patients=0,publication_claim_confirmed=False,scope='Raw DICOM header ordering and observed-only decode; independent label-plane inverse indexing and centered moments; patient-excluded refit; Cholesky classification; raw-label/full-target disk ROI replay. Shared feature extractor, SciPy filters and library codecs are explicitly reused.')
 with path.open('x',encoding='utf-8') as f: json.dump(proof,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(counts=proof['counts'],errors=errors)),flush=True);return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
