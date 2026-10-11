"""Fixed45 observed-only 2x2 bandwidth diagnostic; no neural model loading."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import json,math,sys,time,traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from vs_seg_task_cpu_support import ROOT,resource_gate
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_full_volume_runtime import decode_source,reconstruct,array_sha,sha
from vs_seg_selection_sensitivity import completion_gate
from remind_native_t2_ixi_pair import prepared
from vs_seg_resampling_order_cpu import post_resize
OUT=ROOT/'experiments/anchor_bandwidth_diagnostic_cpu'
ANALYTIC=ROOT/'experiments/vs_seg_resampling_order_cpu'
NAMES=('raw','raw_anchor_roundtrip','mixed_post','slab_roundtrip')
PAIRS=(('mixed_post','raw'),('slab_roundtrip','mixed_post'),('raw_anchor_roundtrip','raw'),('slab_roundtrip','raw_anchor_roundtrip'))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def support(a,b):return (np.abs(a)>.01*max(float(np.abs(a).max()),1e-6))|(np.abs(b)>.01*max(float(np.abs(b).max()),1e-6))
def energy(a,mask,span):
 a=a.astype(float);mx=mask[1:,:]&mask[:-1,:];my=mask[:,1:]&mask[:,:-1];dx=a[1:,:]-a[:-1,:];dy=a[:,1:]-a[:,:-1];nx=int(mx.sum());ny=int(my.sum());sx=float((dx[mx]**2).sum())/span**2;sy=float((dy[my]**2).sum())/span**2
 if nx+ny==0:raise ValueError('Empty fixed gradient-edge ROI')
 return dict(x_edges=nx,y_edges=ny,normalized_x_sse=sx,normalized_y_sse=sy,mean_normalized_gradient_energy=(sx+sy)/(nx+ny))
def summary(rows):
 e=[math.fsum(r['phases'][q]['mean_normalized_gradient_energy'] for r in rows)/len(rows) for q in range(4)];den=math.fsum(e[1:])/3
 return dict(phase_mean_energy=e,log_anchor_to_inserted_energy=math.log(e[0]/den) if e[0]>0 and den>0 else None)
def aggregate(records):
 result=[]
 for left,right in PAIRS:
  values=[r['summaries'][left]['log_anchor_to_inserted_energy']-r['summaries'][right]['log_anchor_to_inserted_energy'] for r in records if r['summaries'][left]['log_anchor_to_inserted_energy'] is not None and r['summaries'][right]['log_anchor_to_inserted_energy'] is not None];undefined=[r['patient'] for r in records if r['summaries'][left]['log_anchor_to_inserted_energy'] is None or r['summaries'][right]['log_anchor_to_inserted_energy'] is None]
  result.append(dict(comparison=left+'-'+right,original_denominator=45,included_patients=len(values),undefined_patients=undefined,patient_differences=values,mean=math.fsum(values)/len(values) if values else None,median=float(np.median(values)) if values else None,minimum=min(values) if values else None,maximum=max(values) if values else None,positive_patients=sum(x>0 for x in values),negative_patients=sum(x<0 for x in values),zero_patients=sum(x==0 for x in values),descriptive_only=True))
 return result
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();gate,original=completion_gate();assert gate['allowed'];analytic=read(ANALYTIC/'attempt_01.json');proof=read(ANALYTIC/'independent_replay_attempt_01.json');assert analytic['complete'] and proof['complete'] and not analytic['errors'] and not proof['errors'];assert proof['result_sha256']==sha(ANALYTIC/'attempt_01.json');OUT.mkdir(exist_ok=False)
 paths={Path(__file__),ROOT/'ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_PLAN_2026-10-03.md',ROOT/'experiments/verify_anchor_bandwidth_diagnostic_cpu.py',ROOT/'experiments/vs_seg_resampling_order_cpu.py',ROOT/'experiments/vs_seg_full_volume_runtime.py',ROOT/'experiments/vs_seg_full_volume_cohort.py',ROOT/'experiments/vs_seg_task_cpu_support.py',ROOT/'experiments/vs_seg_selection_sensitivity.py',ROOT/'experiments/remind_native_t2_ixi_pair.py',ANALYTIC/'attempt_01.json',ANALYTIC/'independent_replay_attempt_01.json',ANALYTIC/'run_contract.json',ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json'}
 for entry in analytic['patients']:paths.add(ROOT/entry['file'])
 contract=dict(created_utc=datetime.now(timezone.utc).isoformat(),main_roster=original['main_roster'],conditions=list(NAMES),files=[dict(path=p.relative_to(ROOT.parent).as_posix(),sha256=sha(p)) for p in sorted(paths)],new_neural_forwards=0,confirmation_patients=0,changes_observed_anchors_in_diagnostic_controls=True,deployable_sr_method=False)
 write(OUT/'run_contract.json',contract);result=dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),complete=False,patients=[],errors=[],gpu_used=False,new_neural_forwards=0,publication_claim_confirmed=False,new_method_confirmation_patients=0,post_task_results_read=False);write(OUT/'attempt_01.json',result);cases={r['patient']:r for r in cases_from_sources()}
 try:
  for patient in contract['main_roster']:
   started=time.perf_counter();resource_gate();native,_,refs=decode_source(cases[patient]);del refs;prep=prepared(native[:,:,::4]);span=prep[2]-prep[1];obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];raw=reconstruct('raw_pchip',native,prep,{});mixed,_=post_resize(raw,prep,targets);row=read(ANALYTIC/(patient+'.json'));assert array_sha(native)==row['native_array_sha256'] and array_sha(raw)==row['conditions']['raw_pchip']['array_sha256'] and array_sha(mixed)==row['conditions']['post_resize_pchip']['array_sha256'];anchor_raw,_=post_resize(raw,prep,obs);allpost,_=post_resize(mixed,prep,obs);arrays=dict(zip(NAMES,(raw,anchor_raw,mixed,allpost)))
   assert np.array_equal(anchor_raw[:,:,targets],raw[:,:,targets]) and np.array_equal(allpost[:,:,targets],mixed[:,:,targets]);assert np.array_equal(anchor_raw[:,:,obs],allpost[:,:,obs]);assert all(np.array_equal(a[:,:,obs[-1]+1:],raw[:,:,obs[-1]+1:]) for a in arrays.values());assert np.array_equal(mixed[:,:,obs],native[:,:,obs]);rows={k:[] for k in NAMES}
   for start in obs[:-1]:
    mask=support(native[:,:,start],native[:,:,start+4])
    for name,a in arrays.items():rows[name].append(dict(start_z=start,support_pixels=int(mask.sum()),phases=[energy(a[:,:,start+q],mask,span) for q in range(4)]))
   record=dict(patient=patient,shape=list(native.shape),span=span,observed_indices=obs,targets=targets,unsupported_tail_indices=list(range(obs[-1]+1,native.shape[2])),native_array_sha256=array_sha(native),array_sha256={k:array_sha(a) for k,a in arrays.items()},missing_slab_sha256={k:array_sha(a[:,:,targets]) for k,a in arrays.items()},tail_sha256={k:array_sha(a[:,:,obs[-1]+1:]) for k,a in arrays.items()},intervals=rows,summaries={k:summary(rows[k]) for k in NAMES},changed_anchor_pixels=int((anchor_raw[:,:,obs]!=raw[:,:,obs]).sum()),complete=True,task_dice_not_measured=True)
   path=OUT/(patient+'.json');write(path,record);result['patients'].append(dict(patient=patient,file=path.relative_to(ROOT).as_posix(),sha256=sha(path),intervals=len(obs)-1,seconds=time.perf_counter()-started));write(OUT/'attempt_01.json',result);print(json.dumps(dict(patient=patient,completed_patients=len(result['patients']))),flush=True);del native,raw,mixed,anchor_raw,allpost,arrays
  records=[read(ROOT/e['file']) for e in result['patients']];result.update(complete=True,analysis=aggregate(records),old_analytic_volumes_replayed=90,total_intervals=sum(e['intervals'] for e in result['patients']),total_missing_planes=sum(len(r['targets']) for r in records))
 except Exception as exc:result['errors'].append(type(exc).__name__+': '+str(exc));result['traceback']=traceback.format_exc()
 result['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',result);print(json.dumps({k:result.get(k) for k in ('complete','errors','old_analytic_volumes_replayed','total_intervals','total_missing_planes')}),flush=True)
 if not result['complete']:raise SystemExit(1)
if __name__=='__main__':main()
