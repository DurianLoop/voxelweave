"""Separate gradient dot-products and full-volume intervention identity replay."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import math,json,sys,traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from skimage.transform import resize
from vs_seg_task_cpu_support import ROOT,resource_gate
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_full_volume_runtime import decode_source,reconstruct,array_sha,sha
from remind_native_t2_ixi_pair import prepared
OUT=ROOT/'experiments/anchor_bandwidth_diagnostic_cpu'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def check(ok,text):
 if not ok:raise ValueError(text)
def close(a,b,text):check(math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12),text)
def roundtrip(plane,prep):
 _,lo,hi=prep;norm=np.divide(np.subtract(plane,lo),hi-lo+1e-8).astype(np.float32);coarse=resize(norm,(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32);return (resize(np.clip(coarse,0,1),plane.shape,preserve_range=True,anti_aliasing=True)*(hi-lo)+lo).astype(np.float32)
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();r=read(OUT/'attempt_01.json');c=read(OUT/'run_contract.json');path=OUT/'independent_gradient_and_identities.json';check(not path.exists(),'First verification already exists');proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),contract_sha256=sha(OUT/'run_contract.json'),complete=False,patients=[],errors=[],new_neural_forwards=0,publication_claim_confirmed=False,independence='Shared native decoder, raw PCHIP, and resize implementation; separately normalized and constructed interventions, difference dot products and math.fsum, independent fixed45 aggregation. No independent cohort or software stack.');cases={x['patient']:x for x in cases_from_sources()};fresh=[]
 try:
  check(r['complete'] and not r['errors'],'All45 complete producer required')
  for f in c['files']:check(sha(ROOT.parent/f['path'])==f['sha256'],'Frozen input changed '+f['path'])
  for e in r['patients']:
   resource_gate();check(sha(ROOT/e['file'])==e['sha256'],'Patient record SHA differs');saved=read(ROOT/e['file']);patient=e['patient'];native,_,refs=decode_source(cases[patient]);del refs;prep=prepared(native[:,:,::4]);span=prep[2]-prep[1];obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];close(span,saved['span'],'Observed span differs');check(obs==saved['observed_indices'] and targets==saved['targets'],'Anchor/target roster differs');raw=reconstruct('raw_pchip',native,prep,{});mixed=raw.copy()
   for z in targets:mixed[:,:,z]=roundtrip(raw[:,:,z],prep)
   anchor_raw=raw.copy();full=mixed.copy()
   for z in obs:anchor_raw[:,:,z]=full[:,:,z]=roundtrip(native[:,:,z],prep)
   arrays=dict(raw=raw,raw_anchor_roundtrip=anchor_raw,mixed_post=mixed,slab_roundtrip=full);check(np.array_equal(anchor_raw[:,:,targets],raw[:,:,targets]) and np.array_equal(full[:,:,targets],mixed[:,:,targets]),'Control changes missing pixels');check(np.array_equal(anchor_raw[:,:,obs],full[:,:,obs]) and np.array_equal(mixed[:,:,obs],native[:,:,obs]),'Anchor intervention differs');check(all(np.array_equal(a[:,:,obs[-1]+1:],raw[:,:,obs[-1]+1:]) for a in arrays.values()),'Tail changed');check(int((anchor_raw[:,:,obs]!=raw[:,:,obs]).sum())==saved['changed_anchor_pixels'],'Changed anchor count differs');summaries={}
   for name,a in arrays.items():
    check(array_sha(a)==saved['array_sha256'][name] and array_sha(a[:,:,targets])==saved['missing_slab_sha256'][name] and array_sha(a[:,:,obs[-1]+1:])==saved['tail_sha256'][name],'Fresh control volume SHA differs');phase=[[] for _ in range(4)]
    for start,stored in zip(obs[:-1],saved['intervals'][name]):
     left,right=native[:,:,start],native[:,:,start+4];mask=np.logical_or(np.greater(np.abs(left),.01*max(float(np.abs(left).max()),1e-6)),np.greater(np.abs(right),.01*max(float(np.abs(right).max()),1e-6)));mx=mask[:-1,:]&mask[1:,:];my=mask[:,:-1]&mask[:,1:];check(stored['start_z']==start and stored['support_pixels']==int(mask.sum()),'Fixed common ROI differs')
     for q,p in enumerate(stored['phases']):
      plane=np.asarray(a[:,:,start+q],dtype=float);dx=np.diff(plane,axis=0)[mx]/span;dy=np.diff(plane,axis=1)[my]/span;sx=float(np.dot(dx,dx));sy=float(np.dot(dy,dy));n=len(dx)+len(dy);check(len(dx)==p['x_edges'] and len(dy)==p['y_edges'],'Gradient edge count differs');close(sx,p['normalized_x_sse'],'Gradient x SSE differs');close(sy,p['normalized_y_sse'],'Gradient y SSE differs');value=(sx+sy)/n;close(value,p['mean_normalized_gradient_energy'],'Real phase energy differs');phase[q].append(value)
    means=[math.fsum(p)/len(p) for p in phase];den=math.fsum(means[1:])/3;log=math.log(means[0]/den) if means[0]>0 and den>0 else None
    for x,y in zip(means,saved['summaries'][name]['phase_mean_energy']):close(x,y,'Patient phase mean differs')
    expected=saved['summaries'][name]['log_anchor_to_inserted_energy'];check((log is None)==(expected is None),'Undefined energy differs')
    if log is not None:close(log,expected,'Patient log ratio differs')
    summaries[name]=log
   fresh.append(dict(patient=patient,summaries=summaries));proof['patients'].append(dict(patient=patient,intervals=len(obs)-1,old_raw_and_post_replayed=True,all_four_volume_identity_checks=True,gradient_dot_products_recomputed=True));write(path,proof);print(json.dumps(dict(patient=patient,completed_patients=len(fresh))),flush=True);del native,raw,mixed,anchor_raw,full,arrays
  check([x['patient'] for x in fresh]==c['main_roster'] and len(fresh)==45,'Fixed all45 roster differs')
  for row in r['analysis']:
   left,right=row['comparison'].split('-');values=[x['summaries'][left]-x['summaries'][right] for x in fresh if x['summaries'][left] is not None and x['summaries'][right] is not None];undefined=[x['patient'] for x in fresh if x['summaries'][left] is None or x['summaries'][right] is None];check(undefined==row['undefined_patients'] and len(values)==row['included_patients'],'Undefined denominator differs')
   for x,y in zip(values,row['patient_differences']):close(x,y,'Paired log ratio differs')
   if values:
    ordered=sorted(values);median=(ordered[(len(values)-1)//2]+ordered[len(values)//2])/2
    for key,value in dict(mean=math.fsum(values)/len(values),median=median,minimum=min(values),maximum=max(values),positive_patients=sum(x>0 for x in values),negative_patients=sum(x<0 for x in values),zero_patients=sum(x==0 for x in values)).items():close(value,row[key],'All45 statistic differs '+key)
  proof.update(complete=True,old_analytic_volumes_replayed=90,total_intervals=sum(x['intervals'] for x in proof['patients']),paired_descriptive_endpoints=4,task_dice_measured=False)
 except Exception as exc:proof['errors'].append(type(exc).__name__+': '+str(exc));proof['traceback']=traceback.format_exc()
 proof['finished_utc']=datetime.now(timezone.utc).isoformat();write(path,proof);print(json.dumps({k:proof.get(k) for k in ('complete','errors','old_analytic_volumes_replayed','total_intervals')}),flush=True)
 if not proof['complete']:raise SystemExit(1)
if __name__=='__main__':main()
