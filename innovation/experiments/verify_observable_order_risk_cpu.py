"""Fresh all45 observable ROI arithmetic, rankings and random-budget replay."""
import json,math,os,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import numpy as np
from skimage.transform import resize
from vs_seg_task_cpu_support import ROOT,resource_gate
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_full_volume_runtime import decode_source,reconstruct,array_sha,sha
from vs_seg_selection_sensitivity import completion_gate,load_verified_records
from remind_native_t2_ixi_pair import prepared
from vs_seg_resampling_order_cpu import post_resize
OUT=ROOT/'experiments/observable_order_risk_cpu'
ANALYTIC=ROOT/'experiments/vs_seg_resampling_order_cpu'
FEATURES=('order_rms','order_max','raw_pipeline_rms','anchor_roundtrip_rms','pchip_linear_rms')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def check(ok,label):
 if not ok: raise ValueError(label)
def close(x,y,label): check(math.isclose(x,y,rel_tol=1e-10,abs_tol=1e-12),label)
def mask(a,b=None):
 m=np.greater(np.abs(a),.01*max(float(np.abs(a).max()),1e-6))
 return m if b is None else np.logical_or(m,np.greater(np.abs(b),.01*max(float(np.abs(b).max()),1e-6)))
def pair_stats(a,b,observed,targets,span,stored):
 check([r['z'] for r in stored]==targets,'Observable target rows differ');means=[]
 for z,row in zip(targets,stored):
  selected=mask(observed[z//4],observed[z//4+1]);d=np.subtract(a[:,:,z][selected],b[:,:,z][selected],dtype=float)/span;n=len(d);sse=float(np.dot(d,d));check(n==row['pixels'],'Observable ROI size differs');close(sse,row['normalized_difference_sse'],'Observable difference SSE differs');means.append(sse/n)
 return math.sqrt(math.fsum(means)/len(means))
def ranks(a):
 result=[None]*len(a);order=sorted(range(len(a)),key=lambda i:(a[i],i));start=0
 while start<len(order):
  end=start+1
  while end<len(order) and a[order[end]]==a[order[start]]: end+=1
  value=(start+1+end)/2
  for i in order[start:end]: result[i]=value
  start=end
 return result
def rho(a,b):
 a=ranks(a);b=ranks(b);mean_a=math.fsum(a)/len(a);mean_b=math.fsum(b)/len(b);x=[v-mean_a for v in a];y=[v-mean_b for v in b]
 return math.fsum(u*v for u,v in zip(x,y))/math.sqrt(math.fsum(u*u for u in x)*math.fsum(v*v for v in y))
def quantile(values,q):
 pos=(len(values)-1)*q;lo=math.floor(pos);hi=math.ceil(pos);return values[lo]+(pos-lo)*(values[hi]-values[lo])

def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();started=time.perf_counter();result=read(OUT/'attempt_01.json');contract=read(OUT/'run_contract.json');path=OUT/'independent_observables_and_rankings.json';check(not path.exists(),'First verification already exists');proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),run_contract_sha256=sha(OUT/'run_contract.json'),complete=False,patients=[],errors=[],gpu_used=False,new_neural_forwards=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,independence='Shared authenticated native decoder, observed min/max, exact analytic runtime and skimage/NumPy RNG. Fresh ROI dot products/math.fsum, separately normalized anchor roundtrip, fresh pipeline/post pair, explicit average ranks/correlation, independent fixed-budget ordering/guards/handwritten quantiles. No software-stack or scientific-cohort independence.')
 try:
  check(result['complete'] and not result['errors'],'Complete all45 producer required');check(result['run_contract_sha256']==sha(OUT/'run_contract.json'),'Contract binding differs')
  for f in contract['files']: check(sha(ROOT.parent/f['path'])==f['sha256'],'Frozen input changed '+f['path'])
  gate,original=completion_gate();check(gate['allowed'],'Original complete gate differs');coverage=read(ROOT/'experiments/vs_seg_full_volume_coverage/attempt_01.json');old,_=load_verified_records(contract['main_roster'],{r['patient']:r for r in coverage['patients']});cases={r['patient']:r for r in cases_from_sources()};fresh=[]
  for record in result['patients']:
   resource_gate();patient=record['patient'];check(sha(ROOT/record['file'])==record['sha256'],'Feature record hash differs');saved=read(ROOT/record['file']);native,_,_=decode_source(cases[patient]);prep=prepared(native[:,:,::4]);_,lo,hi=prep;span=hi-lo;obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];observed=[native[:,:,z] for z in obs];check(saved['observed_indices']==obs and saved['targets']==targets,'Fixed observable planes differ');close(saved['span'],span,'Observed range differs')
   arrays={name:reconstruct(name,native,prep,{}) for name in ('raw_linear','pipeline_linear','raw_pchip','pipeline_pchip')};analytic=read(ANALYTIC/(patient+'.json'))
   for name,array in arrays.items(): check(array_sha(array)==analytic['conditions'][name]['array_sha256'],'Old analytic content SHA differs '+name)
   raw,pipeline,linear=[arrays[k] for k in ('raw_pchip','pipeline_pchip','raw_linear')];observable=saved['per_plane_observable_differences'];features=dict(raw_pipeline_rms=pair_stats(raw,pipeline,observed,targets,span,observable['raw_pipeline']),pchip_linear_rms=pair_stats(raw,linear,observed,targets,span,observable['pchip_linear']));anchor_means=[]
   check([r['z'] for r in observable['anchor_roundtrip']]==obs,'Anchor row roster differs')
   for z,a,row in zip(obs,observed,observable['anchor_roundtrip']):
    norm=np.divide(np.subtract(a,lo),span+1e-8).astype(np.float32);coarse=resize(norm,(256,256),preserve_range=True,anti_aliasing=True).astype(np.float32);roundtrip=(resize(np.clip(coarse,0,1),native.shape[:2],preserve_range=True,anti_aliasing=True)*span+lo).astype(np.float32);selected=mask(a);d=np.subtract(roundtrip[selected],a[selected],dtype=float)/span;n=len(d);sse=float(np.dot(d,d));check(n==row['pixels'],'Observed anchor ROI differs');close(sse,row['normalized_difference_sse'],'Observed anchor SSE differs');anchor_means.append(sse/n)
   features['anchor_roundtrip_rms']=math.sqrt(math.fsum(anchor_means)/len(anchor_means));post,_=post_resize(raw,prep,targets);check(array_sha(post)==analytic['conditions']['post_resize_pchip']['array_sha256'],'Observable post construction differs');order_means=[];max_abs=0.
   for z in targets:
    selected=mask(observed[z//4],observed[z//4+1]);d=np.subtract(pipeline[:,:,z],post[:,:,z],dtype=float)/span;v=d[selected];order_means.append(float(np.dot(v,v))/len(v));max_abs=max(max_abs,float(np.abs(d).max()))
   features.update(order_rms=math.sqrt(math.fsum(order_means)/len(order_means)),order_max=max_abs)
   for k,v in features.items(): close(v,saved['features'][k],'Actual observable feature differs '+k)
   utility={ref:old[patient]['pipeline_pchip']['task_metrics'][ref]['full']['dice']-old[patient]['raw_pchip']['task_metrics'][ref]['full']['dice'] for ref in ('original_json','rtstruct')};utility['support_nmse']=old[patient]['pipeline_pchip']['image_metrics']['support']['target_equal_nmse']-old[patient]['raw_pchip']['image_metrics']['support']['target_equal_nmse']
   for k,v in utility.items(): close(v,saved['utility'][k],'Old real utility differs '+k)
   fresh.append(dict(patient=patient,features=features,utility=utility));proof['patients'].append(dict(patient=patient,old_analytic_volumes_replayed=4,observable_targets=len(targets),observed_anchor_rows=len(obs),actual_observables_recomputed=True));write(path,proof);print(json.dumps(dict(patient=patient,completed_patients=len(fresh))),flush=True);del native,arrays,raw,pipeline,linear,post
  check([r['patient'] for r in fresh]==contract['main_roster'] and len(fresh)==45,'All45 fixed roster differs')
  selections={feature:sorted(range(45),key=lambda i:(fresh[i]['features'][feature],i))[:15] for feature in FEATURES};selections['oracle']=sorted(range(45),key=lambda i:(-min(fresh[i]['utility'][r] for r in ('original_json','rtstruct')),i))[:15];policies={**result['policies'],'oracle':result['oracle']}
  for name,indices in selections.items():
   p=policies[name];check(indices==p['selected_indices'] and [fresh[i]['patient'] for i in indices]==p['selected_patients'],'Fixed budget selection differs '+name);check(len(indices)==len(set(indices))==15,'Budget/uniqueness differs');guard=all(fresh[i]['utility'][ref]>=-.01 for i in indices for ref in ('original_json','rtstruct'));check(guard==p['all_selected_both_label_guard'],'Per-patient guard differs')
   for ref in ('original_json','rtstruct'):
    values=[fresh[i]['utility'][ref] for i in indices];actual=dict(selected_mean_utility=math.fsum(values)/15,whole45_policy_minus_all_raw=math.fsum(values)/45,minimum_selected_utility=min(values),negative_selected_patients=sum(v<0 for v in values))
    for k,v in actual.items(): close(v,p['task'][ref][k],'Policy real utility summary differs')
   close(math.fsum(fresh[i]['utility']['support_nmse'] for i in indices)/15,p['selected_mean_support_nmse_change'],'Image benefit differs')
  rng=np.random.default_rng(20261102);draws=[rng.choice(45,size=15,replace=False).tolist() for _ in range(5000)];check(draws==result['random_indices'],'Random same-budget draw roster differs');random={}
  for ref in ('original_json','rtstruct'):
   means=[math.fsum(fresh[i]['utility'][ref] for i in draw)/15 for draw in draws];sorted_means=sorted(means);random[ref]=[quantile(sorted_means,q) for q in (.025,.975)];close(math.fsum(means)/5000,result['random_same_budget'][ref]['mean'],'Random budget mean differs')
   for a,b in zip(random[ref],result['random_same_budget'][ref]['ci95_percentile']): close(a,b,'Random budget quantile differs')
  for feature in FEATURES:
   for ref in ('original_json','rtstruct'): close(rho([r['features'][feature] for r in fresh],[r['utility'][ref] for r in fresh]),result['descriptive_spearman'][feature][ref],'Explicit average-rank correlation differs')
  c=result['policies']['order_rms'];beats={ref:all(c['task'][ref]['selected_mean_utility']>result['policies'][f]['task'][ref]['selected_mean_utility']+1e-12 for f in FEATURES[2:]) and c['task'][ref]['selected_mean_utility']>random[ref][1]+1e-12 for ref in ('original_json','rtstruct')};passed=c['all_selected_both_label_guard'] and all(beats.values());check(beats==result['main_candidate_beats_all_strong_and_random'] and passed==result['main_candidate_development_gate_passed'] and (not passed)==result['main_fixed_candidate_stopped'],'Fixed candidate gate differs');safe=sum(all(r['utility'][ref]>=-.01 for ref in ('original_json','rtstruct')) for r in fresh);check(safe==result['patients_meeting_both_label_guard'],'Oracle feasibility count differs')
  proof.update(complete=True,total_targets=sum(r['observable_targets'] for r in proof['patients']),old_analytic_volumes_replayed=180,policies_checked=6,random_same_budget_draws_checked=5000,main_candidate_development_gate_passed=passed,main_fixed_candidate_stopped=not passed,patients_meeting_both_label_guard=safe,new_post_task_results_read=False)
 except Exception as exc:
  proof['errors'].append(type(exc).__name__+': '+str(exc));proof['traceback']=traceback.format_exc()
 proof['finished_utc']=datetime.now(timezone.utc).isoformat();proof['elapsed_seconds']=time.perf_counter()-started;write(path,proof);print(json.dumps({k:proof.get(k) for k in ('complete','errors','old_analytic_volumes_replayed','main_candidate_development_gate_passed')}),flush=True)
 if not proof['complete']: raise SystemExit(1)
if __name__=='__main__': main()
