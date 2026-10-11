"""Independent manual normalized-input hashes, all acquisition domains and Fraction contrasts."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import json,math,sys,traceback
from fractions import Fraction
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import nibabel as nib
from skimage.transform import resize
from vs_seg_task_cpu_support import ROOT,resource_gate
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_full_volume_runtime import decode_source,reconstruct,array_sha,sha
from remind_native_t2_ixi_pair import prepared
OUT=ROOT/'experiments/task_stats_swap_cpu_pilot'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def check(ok,msg):
 if not ok:raise ValueError(msg)
def close(a,b,msg):check(a==b if a is None or b is None else math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-12),msg)
def normalized(a,mu,sd):return np.divide(np.subtract(a,mu),sd)[None].astype(np.float32)
def fscore(m):return Fraction(2*m['tp'],2*m['tp']+m['fp']+m['fn']) if m['dice'] is not None else None
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();p=OUT/'independent_inputs_domains_and_all30_estimates.json';check(not p.exists(),'Proof already exists');r=read(OUT/'attempt_01.json');c=read(OUT/'run_contract.json');proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),contract_sha256=sha(OUT/'run_contract.json'),complete=False,errors=[],normalized_inputs_replayed=0,diagonal_input_hashes_verified=0,domain_confusion_cells_verified=0,paired_endpoints_verified=0,saved_prediction_proofs_verified=0,patients=[],new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False,independence='Manual NumPy normalization and independent post resize expression; exact Fraction Dice contrasts and direct acquisition-domain counts. Shared source/PCHIP/NumPy/resize; no independent cohort or model.')
 try:
  check(r['complete'] and not r['errors'] and len(r['patients'])==6 and len(r['analysis'])==30,'Whole6/all30 completion required')
  for x in c['files']:check(sha(ROOT.parent/x['path'])==x['sha256'],'Frozen source changed '+x['path'])
  records={}
  for e in r['patients']:
   check(sha(ROOT/e['file'])==e['sha256'] and sha(ROOT/e['verification_file'])==e['verification_sha256'],'Record/proof hash differs');x=read(ROOT/e['file']);v=read(ROOT/e['verification_file']);check(x['complete'] and not x['cuda_initialized'] and v['complete'] and not v['errors'] and v['record_sha256']==e['sha256'] and v['prediction_sha256']==x['prediction_sha256'],'Saved proof differs');records.setdefault(e['patient'],{})[e['condition']]=x;proof['saved_prediction_proofs_verified']+=1
  cases={x['patient']:x for x in cases_from_sources()};allcells={}
  for patient in c['roster']:
   resource_gate();native,affine,refs=decode_source(cases[patient]);prep=prepared(native[:,:,::4]);lo=prep[1];span=prep[2]-lo;obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];raw=reconstruct('raw_pchip',native,prep,{});post=raw.copy()
   for z in targets:
    small=resize(((raw[:,:,z]-lo)/(span+1e-8)).astype(np.float32),(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32);post[:,:,z]=(resize(np.clip(small,0,1),raw.shape[:2],preserve_range=True,anti_aliasing=True)*span+lo).astype(np.float32)
   orientation=nib.orientations.ornt_transform(nib.orientations.io_orientation(affine),nib.orientations.axcodes2ornt('RAS'));images={name:np.ascontiguousarray(nib.orientations.apply_orientation(v,orientation)) for name,v in [('raw',raw),('post',post)]};stats={name:(np.mean(a.ravel()),np.std(a.ravel())) for name,a in images.items()};stats={name:(mu,np.float32(1) if sd==0 else sd) for name,(mu,sd) in stats.items()};domains={}
   for name,indices in [('observed_anchors',obs),('supported_missing',targets),('unsupported_tail',list(range(obs[-1]+1,native.shape[2])))]:mask=np.zeros(native.shape,dtype=bool);mask[:,:,indices]=True;domains[name]=nib.orientations.apply_orientation(mask,orientation)
   check(np.all(sum(m.astype(np.uint8) for m in domains.values())==1),'Actual domains do not partition volume');refs={k:nib.orientations.apply_orientation(v,orientation) for k,v in refs.items()};cells={}
   for name in ('raw_poststats','post_rawstats'):
    x=records[patient][name];image,stat=x['image_baseline'],x['statistics_baseline'];a=normalized(images[image],*stats[stat]);check(array_sha(a)==x['normalized_input_array_sha256'],'Crossed full input SHA differs');check(array_sha(raw if image=='raw' else post)==x['reconstructed_array_sha256'],'Image source differs');close(stats[stat][0],x['normalization_mean'],'Mean differs');close(stats[stat][1],x['normalization_std'],'Std differs');proof['normalized_inputs_replayed']+=1;cells[name]=x
   reference=records[patient]['raw_poststats']['diagonals']
   check(reference==records[patient]['post_rawstats']['diagonals'],'Embedded diagonals differ')
   for name in ('raw','post'):
    d=reference[name];check(sha(ROOT/d['record_file'])==d['record_sha256'],'Original diagonal changed');check(array_sha(normalized(images[name],*stats[name]))==d['normalized_input_array_sha256'],'Diagonal input SHA differs');old=read(ROOT/d['record_file']);check(old['task_metrics']==d['task_metrics'],'Actual old diagonal metrics differ');cells[name+'_'+name+'stats']={**old,'domain_confusion':d['domain_confusion']};proof['diagonal_input_hashes_verified']+=1
   for name,x in cells.items():
    pp=ROOT/x['prediction_file'];check(sha(pp)==x['prediction_sha256'],'Prediction changed')
    with np.load(pp) as saved:pred=saved['prediction_ras']
    for ref,label in refs.items():
     totals={k:0 for k in ('tp','fp','fn')}
     for domain,mask in domains.items():
      a,b=pred[mask],label[mask];tp=int(np.count_nonzero(a&b));fp=int(a.sum())-tp;fn=int(b.sum())-tp;den=2*tp+fp+fn;reported=x['domain_confusion'][ref][domain]
      for key,value in [('tp',tp),('fp',fp),('fn',fn),('reference_voxels',tp+fn),('prediction_voxels',tp+fp)]:check(reported[key]==value,'Actual partition confusion differs')
      close(Fraction(2*tp,den) if den else None,reported['dice'],'Actual partition Dice differs');proof['domain_confusion_cells_verified']+=1
      for k,v in [('tp',tp),('fp',fp),('fn',fn)]:totals[k]+=v
     check(all(totals[k]==x['task_metrics'][ref]['full'][k] for k in totals),'Full does not sum from partitions')
   allcells[patient]=cells;proof['patients'].append(dict(patient=patient,all_four_cells_verified=True));write(p,proof)
  for e in r['analysis']:
   vals=[];undefined=[]
   for patient in c['roster']:
    v={name:fscore(x['task_metrics'][e['reference']][e['domain']]) for name,x in allcells[patient].items()}
    if e['comparison']=='normalization_image_interaction':delta=(v['post_poststats']-v['post_rawstats'])-(v['raw_poststats']-v['raw_rawstats']) if all(x is not None for x in v.values()) else None
    else:left,right=e['comparison'].split('-');delta=v[left]-v[right] if v[left] is not None and v[right] is not None else None
    if delta is None:undefined.append(patient)
    else:vals.append((patient,delta))
   check(undefined==e['undefined_patients'] and len(vals)==e['defined_n'],'Undefined roster differs');check([p for p,v in vals]==[x['patient'] for x in e['patient_differences']],'Paired roster differs')
   for (_,value),old in zip(vals,e['patient_differences']):close(value,old['difference'],'Fraction patient contrast differs')
   close(sum(v for p,v in vals)/len(vals) if vals else None,e['mean'],'Fraction mean differs');proof['paired_endpoints_verified']+=1
  proof.update(complete=True)
 except Exception as exc:proof['errors'].append(type(exc).__name__+': '+str(exc));proof['traceback']=traceback.format_exc()
 proof['finished_utc']=datetime.now(timezone.utc).isoformat();write(p,proof);print(json.dumps({k:v for k,v in proof.items() if k not in ('patients','traceback')},ensure_ascii=False))
 if not proof['complete']:raise SystemExit(1)
if __name__=='__main__':main()
