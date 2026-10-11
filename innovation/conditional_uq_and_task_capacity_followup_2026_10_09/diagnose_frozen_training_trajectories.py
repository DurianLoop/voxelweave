"""Describe all frozen paired training records; no data or neural inference."""
import sys,json,gzip,time,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
import search_primary_candidates as h
HERE=Path(__file__).resolve().parent;ROOT=h.ROOT;FIT=ROOT/'spatial_adaptation_matched_2026_10_08'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def stats(values):
 vals=sorted(values);n=len(vals);assert n and all(math.isfinite(v) for v in vals)
 def q(p):
  t=(n-1)*p;i=int(t);j=min(i+1,n-1);return vals[i]+(vals[j]-vals[i])*(t-i)
 return dict(n=n,mean=statistics.fmean(vals),median=statistics.median(vals),min=vals[0],max=vals[-1],p10=q(.1),p90=q(.9),nonfinite=0)
def grouped(rows):
 d=defaultdict(list)
 for v in rows:d[v['patient']].append(v['loss'])
 return {k:stats(v) for k,v in sorted(d.items())}
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();h.guard();out=HERE/'training_trajectory_attempt01';out.mkdir(exist_ok=False)
 exit=read(FIT/'ACTUAL_TRAINING_EXIT.json');fit=read(FIT/'training_attempt01/receipt.json')
 assert exit['observed_tool_exit']==0 and exit['observed_tool_session']==29823 and exit['all11968_history_rows_verified'] and exit['all2992_paired_steps_verified']
 assert exit['result_sha256']==h.sha(FIT/'training_attempt01/receipt.json') and fit['complete'] and not fit['errors']
 config=read(FIT/'training_attempt01/frozen_config.json');assert fit['frozen_config_sha256']==h.sha(FIT/'training_attempt01/frozen_config.json')
 names=['native_reference_intensity','native_reference_spatial','raw_pchip_intensity','raw_pchip_spatial'];assert [a['name'] for a in fit['arms']]==names
 sources=[Path(__file__),HERE/'TRAINING_TRAJECTORY_DIAGNOSTIC_PROTOCOL.md',FIT/'ACTUAL_TRAINING_EXIT.json',FIT/'training_attempt01/receipt.json',FIT/'training_attempt01/frozen_config.json'];logs={};arms=[]
 for a in fit['arms']:
  p=ROOT/a['history_path'];assert h.sha(p)==a['history_sha256'];sources.append(p)
  with gzip.open(p,'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
  assert len(rows)==2992 and [v['step'] for v in rows]==list(range(1,2993));assert all(v['lr']==1e-4 for v in rows)
  logs[a['name']]=rows;counts=Counter(v['patient'] for v in rows);series=Counter((v['patient'],v['uid']) for v in rows)
  assert len(counts)==11 and set(counts.values())=={272} and len(series)==19
  blocks=[dict(start=b*272+1,stop_inclusive=(b+1)*272,loss=stats([v['loss'] for v in rows[b*272:(b+1)*272]])) for b in range(11)]
  arms.append(dict(name=a['name'],full=stats([v['loss'] for v in rows]),first544=stats([v['loss'] for v in rows[:544]]),last544=stats([v['loss'] for v in rows[-544:]]),
   all11_patient_stats=grouped(rows),first544_patient_stats=grouped(rows[:544]),last544_patient_stats=grouped(rows[-544:]),blocks272=blocks,patient_exposure=dict(sorted(counts.items())),series_exposure=[dict(patient=k[0],uid=k[1],n=v) for k,v in sorted(series.items())]))
 paired=[];matchfields=['step','patient','uid','mother_label_sha256','geometry','spatial_primitives','intensity_primitives','pivots_zrc','base_input_sha256']
 for kind in ['native_reference','raw_pchip']:
  left=logs[kind+'_intensity'];right=logs[kind+'_spatial'];diff=[];groups=defaultdict(list)
  for v,w in zip(left,right):
   assert all(v[k]==w[k] for k in matchfields);d=w['loss']-v['loss'];diff.append(d);groups[v['patient']].append(d)
  paired.append(dict(kind=kind,loss_difference='spatial_minus_intensity',all2992_steps=stats(diff),first544=stats(diff[:544]),last544=stats(diff[-544:]),positive=sum(v>0 for v in diff),negative=sum(v<0 for v in diff),zero=sum(v==0 for v in diff),all11_patient_means={k:stats(v) for k,v in sorted(groups.items())}))
 # Mother exposure and mother labels are common across native and raw inputs.
 for v,w in zip(logs[names[0]],logs[names[2]]):assert all(v[k]==w[k] for k in matchfields if k!='base_input_sha256')
 r=dict(complete=True,errors=[],arms=arms,paired_differences=paired,all11968_rows_used=True,all2992_paired_mother_exposures_verified=True,all11_patients_and19_series_retained=True,
  MRI_arrays_loaded=0,GT_arrays_loaded=0,neural_forwards=0,training_updates=0,validation_data_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,development_evaluation_not_yet_terminal=True,
  inference='descriptive optimization and exposure only; transformed losses do not establish FOV capacity or augmentation benefit',publication_claim_confirmed=False,goal_status='active',
  sources=[dict(path=p.relative_to(ROOT).as_posix(),sha256=h.sha(p),bytes=p.stat().st_size) for p in sources],elapsed_seconds=time.perf_counter()-started,resources=h.guard())
 data=(json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode('utf-8');assert len(data)<100000 and time.perf_counter()-started<60
 h.dump(out/'receipt.json',r);print(json.dumps(dict(complete=True,rows=11968,arms=[dict(name=a['name'],full_mean=a['full']['mean'],first544_mean=a['first544']['mean'],last544_mean=a['last544']['mean']) for a in arms],paired=[dict(kind=v['kind'],mean=v['all2992_steps']['mean'],first544=v['first544']['mean'],last544=v['last544']['mean']) for v in paired],elapsed_seconds=r['elapsed_seconds']),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
