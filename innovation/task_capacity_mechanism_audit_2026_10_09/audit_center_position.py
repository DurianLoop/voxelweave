"""Descriptive geometry of all2992 frozen foreground probes; no imaging or network arrays."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,json,time,gzip,math,itertools,collections,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,torch,np
from mc_rc_3d_baseline_2026_10_07 import tile_plan,blending_weight,PATCH
from mc_rc_reference_resources_2026_10_07 import resource_guard

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def dump(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def guard(started):
 r=resource_guard();assert time.perf_counter()-started<120
 assert r['workspace_free_bytes']-2_000_000-3_000_000-2_800_000-1_200_000>=8_000_000_000
 assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<1_200_000
 assert torch.get_num_threads()==torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
 return r
def summary(rows):
 keys=rows[0].keys();return {k:sum(r[k] for r in rows)/len(rows) for k in keys}
def position(local):
 d=min(min(int(v),p-1-int(v)) for v,p in zip(local,PATCH))
 return dict(boundary_distance_voxels=float(d),edge_lt8=float(d<8),edge_lt16=float(d<16),max_normalized_center_offset=max(abs(float(v)-(p-1)/2)/(p/2) for v,p in zip(local,PATCH)))
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();torch.set_num_threads(1);before=guard(started)
 fitp=ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01/receipt.json';fit=read(fitp)
 exitp=ROOT/'spatial_adaptation_matched_2026_10_08/ACTUAL_TRAINING_EXIT.json';ex=read(exitp)
 assert ex['observed_tool_exit']==0 and ex['all11968_history_rows_verified'] and ex['all2992_paired_steps_verified']
 assert sha(fitp)==ex['result_sha256'] and fit['complete'] and not fit['errors'] and len(fit['arms'])==4
 auditp=ROOT/'real_context_and_author_code_followup_2026_10_08/full_schedule_audit_attempt01/receipt.json';audit=read(auditp)
 assert audit['complete'] and not audit['errors'] and audit['all2992_original_sample_batch_geometry_and_mother_labels_matched']
 cases={c['uid']:c for c,row in development_cases()};assert len(cases)==19
 sources=[Path(__file__),HERE/'CENTER_POSITION_PROTOCOL.md',fitp,exitp,auditp]
 histories=[]
 for arm in fit['arms']:
  p=ROOT/arm['history_path'];assert sha(p)==arm['history_sha256'];sources.append(p)
  with gzip.open(p,'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
  assert len(rows)==2992 and [r['step'] for r in rows]==list(range(1,2993));histories.append(rows)
 grids={};plans={}
 for uid,c in cases.items():
  grid=lattice(c);shape=tuple(n+lo+hi for n,(lo,hi) in zip(grid['unpadded_shape_zrc'],grid['padding']))
  production,starts=tile_plan(shape)
  scalar_axes=[]
  for n,p in zip(shape,PATCH):
   a=[0]
   while a[-1]+p//2<=n-p:a.append(a[-1]+p//2)
   if a[-1]!=n-p:a.append(n-p)
   scalar_axes.append(a)
  assert starts==scalar_axes and production==list(itertools.product(*scalar_axes));grids[uid]=grid;plans[uid]=starts
 production_weights=blending_weight(PATCH);points=[];grouped=collections.defaultdict(list);max_weight_error=0.;max_sum_error=0.
 for ix,row in enumerate(histories[0]):
  if ix%400==0:guard(started)
  for rows in histories[1:]:
   other=rows[ix]
   for key in ('step','patient','uid','geometry','mother_label_sha256'):assert row[key]==other[key]
  uid=row['uid'];c=cases[uid];assert row['patient']==c['patient']
  g=row['geometry'][0];assert g['forced_foreground'] and not row['geometry'][1]['forced_foreground'] and g['target_foreground']>0
  point=np.array(g['center'],dtype=int);train_local=point-np.array(g['start']);assert all(0<=v<p for v,p in zip(train_local,PATCH))
  choices=[[s for s in a if s<=v<s+p] for v,p,a in zip(point,PATCH,plans[uid])];assert all(choices)
  starts=list(itertools.product(*choices));local=point[None,:]-np.array(starts)
  shift=local-(np.array(PATCH)-1)/2
  weights=np.maximum(np.exp(-.5*np.sum((shift/(np.array(PATCH)/8))**2,axis=1)+.5*sum((.5/(p/8))**2 for p in PATCH)),1e-4).astype(np.float32)
  oracle=[]
  for loc in local:
   scalar=math.exp(sum(-.5*((int(v)-(p-1)/2)/(p/8))**2+.5*(.5/(p/8))**2 for v,p in zip(loc,PATCH)))
   scalar=float(np.float32(max(scalar,1e-4)));oracle.append(scalar)
   max_weight_error=max(max_weight_error,abs(scalar-float(production_weights[tuple(loc)])))
  max_weight_error=max(max_weight_error,float(np.max(np.abs(weights-np.array(oracle)))))
  assert max_weight_error<=3e-6
  norm=weights.astype(np.float64)/float(weights.astype(np.float64).sum());max_sum_error=max(max_sum_error,abs(float(norm.sum())-1.))
  positions=[position(loc) for loc in local];deploy={k:sum(float(w)*v[k] for w,v in zip(norm,positions)) for k in positions[0]}
  same_phase=sum(float(w) for w,s in zip(norm,starts) if all((int(a)-int(b))%8==0 for a,b in zip(s,g['start'])))
  training=position(train_local);metrics={'train_'+k:v for k,v in training.items()}|{'deploy_'+k:v for k,v in deploy.items()}|dict(deploy_training_same_pooling_phase_weight=same_phase,contributing_tiles=float(len(starts)))
  grouped[(c['patient'],uid)].append(metrics)
  points.append(dict(step=row['step'],patient=c['patient'],uid=uid,probe_zrc=point.tolist(),training_local_zrc=train_local.tolist(),metrics=metrics))
 assert len(points)==2992 and len(grouped)==19 and max_sum_error<1e-12
 patient_rows=collections.defaultdict(list);series=[]
 for (patient,uid),rows in sorted(grouped.items()):
  m=summary(rows);series.append(dict(patient=patient,uid=uid,probes=len(rows),means=m));patient_rows[patient].append(m)
 patients=[dict(patient=p,series=len(rs),probes=sum(len(v) for (q,u),v in grouped.items() if p==q),means=summary(rs)) for p,rs in sorted(patient_rows.items())]
 assert len(patients)==11 and all(p['probes']==272 for p in patients)
 result=dict(complete=True,errors=[],all2992_probes_retained=True,all_four_arm_mother_geometries_matched=True,all19_tile_plans_independently_matched=True,all_probe_Gaussian_weights_independently_matched=True,max_weight_error=max_weight_error,max_weight_sum_error=max_sum_error,probe_count=2992,patient_count=11,series_count=19,patient_first_means=summary([p['means'] for p in patients]),patients=patients,series=series,scope='GT-foreground points selected by frozen training sampler, augmentation-before geometry, repeats retained; no volume-wide lesion coverage or medical outcomes',MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,CUDA_initialized=False,confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',source_bindings=[entry(p) for p in sources],resources_before=before,elapsed_seconds=time.perf_counter()-started)
 out=HERE/'center_position_attempt01';assert not out.exists();guard(started);out.mkdir()
 journal=out/'probes.jsonl.gz'
 with journal.open('xb') as raw:
  with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as f:
   for p in points:f.write((json.dumps(p,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8'))
 result['journal']=entry(journal);dump(out/'receipt.json',result)
 assert sum(p.stat().st_size for p in out.iterdir())<300_000;after=guard(started)
 print(json.dumps(dict(complete=True,probes=2992,patient_first_means=result['patient_first_means'],max_weight_error=max_weight_error,output_bytes=sum(p.stat().st_size for p in out.iterdir()),elapsed_seconds=time.perf_counter()-started),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
