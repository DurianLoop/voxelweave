"""Prepared only: compare all four branches after the actual 76-FOV audit exists."""
import sys,json,time,hashlib
from pathlib import Path
from fractions import Fraction
import search_primary_candidates as h
HERE=Path(__file__).resolve().parent;ROOT=h.ROOT;DEV=ROOT/'development_capacity_after_matched_2026_10_09';MED=ROOT/'spatial_adaptation_matched_2026_10_08'
REGIONS=['full','anchors','missing','tail'];METRICS=['dice','precision','recall','signed_relative_volume_error','absolute_relative_volume_error']
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def mean(vals):return None if any(v is None for v in vals) else sum(vals,Fraction(0))/len(vals)
def counts_metrics(m):
 tp,fp,fn=[int(m[k]) for k in ['tp','fp','fn']];g=int(m['gt_foreground']);pred=int(m['pred_foreground']);assert g==tp+fn and pred==tp+fp
 r=Fraction(pred-g,g) if g else None
 return dict(dice=Fraction(2*tp,2*tp+fp+fn) if 2*tp+fp+fn else None,precision=Fraction(tp,pred) if pred else None,recall=Fraction(tp,g) if g else None,signed_relative_volume_error=r,absolute_relative_volume_error=abs(r) if r is not None else None)
def value(v):return float(v) if v is not None else None
def summarize(arm,patients,aggregate_key):
 sets={p:[v for v in arm['series'] if v['patient']==p] for p in patients};assert all(sets.values());out={}
 for p,rows in sorted(sets.items()):
  out[p]=dict(series=len(rows),metrics={})
  for region in REGIONS:
   ms=[counts_metrics(v['metrics'][region]) for v in rows];out[p]['metrics'][region]={k:mean([v[k] for v in ms]) for k in METRICS}
   for k in METRICS:
    target=arm[aggregate_key]['patients'][p]['metrics'][region][k];actual=value(out[p]['metrics'][region][k])
    assert (actual is None and target is None) or (actual is not None and target is not None and abs(actual-target)<1e-12)
 means={region:{k:mean([out[p]['metrics'][region][k] for p in patients]) for k in METRICS} for region in REGIONS}
 for region in REGIONS:
  for k in METRICS:
   actual=value(means[region][k]);target=arm[aggregate_key]['patient_first_means'][region][k]
   assert (actual is None and target is None) or (actual is not None and target is not None and abs(actual-target)<1e-12)
 serial={p:dict(series=v['series'],metrics={r:{k:value(a) for k,a in m.items()} for r,m in v['metrics'].items()}) for p,v in out.items()}
 return dict(patient_count=len(patients),series_count=sum(len(v) for v in sets.values()),patient_first_means={r:{k:value(v) for k,v in m.items()} for r,m in means.items()},patients=serial)
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();h.guard()
 ex=read(DEV/'ACTUAL_DEVELOPMENT_EVALUATION_EXIT.json');terminal=read(DEV/'ACTUAL_DEVELOPMENT_EVALUATION_TERMINAL_TOOL.json');dev=read(DEV/'evaluation_attempt01/receipt.json');config=read(DEV/'evaluation_attempt01/frozen_config.json')
 assert ex['observed_tool_exit']==0 and ex['observed_tool_session']==12652 and ex['all76_complete_FOVs_and_exact_case_sets_verified'] and ex['all76_strict_probability_coordinate_binary_gates_passed']
 assert terminal['exit_code']==0 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==12652
 assert ex['result_sha256']==h.sha(DEV/'evaluation_attempt01/receipt.json') and dev['complete'] and not dev['errors']
 mex=read(MED/'ACTUAL_EVALUATION_EXIT.json');med=read(MED/'evaluation_attempt01/receipt.json');assert mex['observed_tool_exit']==0 and mex['observed_tool_session']==78123 and mex['all36_strict_numeric_gates_passed']
 assert mex['result_sha256']==h.sha(MED/'evaluation_attempt01/receipt.json') and med['complete'] and not med['errors']
 assert [a['name'] for a in dev['arms']]==[a['name'] for a in med['arms']]==config['branch_names'] and len(dev['arms'])==4
 dp=config['development_patient_ids'];vp=sorted({v['patient'] for a in med['arms'] for v in a['series']});assert len(dp)==11 and len(vp)==4 and set(dp).isdisjoint(vp)
 arms=[]
 for d,v in zip(dev['arms'],med['arms']):
  assert d['complete'] and v['complete'] and len(d['series'])==19 and len(v['series'])==9
  ds=summarize(d,dp,'development_aggregate');vs=summarize(v,vp,'validation_aggregate')
  delta={r:{k:(ds['patient_first_means'][r][k]-vs['patient_first_means'][r][k]) if ds['patient_first_means'][r][k] is not None and vs['patient_first_means'][r][k] is not None else None for k in METRICS} for r in REGIONS}
  dm=ds['patient_first_means'];reference=dict(full_dice=dm['full']['dice'] is not None and dm['full']['dice']>=.70,missing_dice=dm['missing']['dice'] is not None and dm['missing']['dice']>=.65,recall=dm['full']['recall'] is not None and dm['full']['recall']>=.70,absRVE=dm['full']['absolute_relative_volume_error'] is not None and dm['full']['absolute_relative_volume_error']<=.50)
  arms.append(dict(name=d['name'],development=ds,seen_validation=vs,development_minus_validation_descriptive=delta,development_reference_thresholds=reference,original_validation_six_gates=v['validation_gates']))
 assert sum(a['development']['series_count'] for a in arms)==76 and sum(a['seen_validation']['series_count'] for a in arms)==36
 sources=[Path(__file__),HERE/'COMPLETE_COMPARISON_PREPARATION.md',DEV/'ACTUAL_DEVELOPMENT_EVALUATION_EXIT.json',DEV/'ACTUAL_DEVELOPMENT_EVALUATION_TERMINAL_TOOL.json',DEV/'evaluation_attempt01/receipt.json',DEV/'evaluation_attempt01/frozen_config.json',MED/'ACTUAL_EVALUATION_EXIT.json',MED/'evaluation_attempt01/receipt.json']
 result=dict(complete=True,errors=[],arms=arms,all76_development_and36_seen_validation_FOVs_retained=True,null_policy='any undefined series or patient propagates null; full denominators retained',all_metrics_fraction_recounted=True,GT_arrays_loaded=0,MRI_arrays_loaded=0,neural_forwards=0,training_updates=0,confirmation_patients_opened=False,lockedIXI_opened=False,development_GT_seen_by_training=True,independent_patient_confirmation=False,causal_augmentation_effect_claimed=False,checkpoint_selected=False,publication_claim_confirmed=False,goal_status='active',source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=h.sha(p),bytes=p.stat().st_size) for p in sources],elapsed_seconds=time.perf_counter()-started)
 out=HERE/'complete_comparison_attempt01';assert not out.exists();encoded=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8');assert len(encoded)<200000
 assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+len(encoded)+15000<2_000_000;h.guard();out.mkdir();h.dump(out/'receipt.json',result)
 lines=['# 全四臂开发与已见验证描述性比较','', '开发GT用于过训练；两组采集/患者不同，差异不能判因果或泛化保证。','', '| 分支 | 开发Dice | 已见验证Dice | 开发recall | 已见验证recall | 开发4参考条件通过 |','| --- | ---: | ---: | ---: | ---: | ---: |']
 for a in arms:
  d=a['development']['patient_first_means']['full'];v=a['seen_validation']['patient_first_means']['full'];fmt=lambda x:'null' if x is None else f'{x:.6f}'
  lines.append('| '+a['name']+' | '+fmt(d['dice'])+' | '+fmt(v['dice'])+' | '+fmt(d['recall'])+' | '+fmt(v['recall'])+' | '+str(sum(a['development_reference_thresholds'].values()))+'/4 |')
 lines+=['','全部11开发/4已见验证患者、各19/9series、四region/五指标保留在receipt.json；没有挑分支、改阈值、重训或开确认集。']
 with (out/'RESULTS.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
 assert time.perf_counter()-started<60;print(json.dumps(dict(complete=True,development_FOVs=76,seen_validation_FOVs=36,out=out.relative_to(ROOT).as_posix(),elapsed_seconds=time.perf_counter()-started),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
