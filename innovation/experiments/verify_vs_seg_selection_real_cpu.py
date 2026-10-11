"""Verify all 112 real secondary endpoints only after the whole original queue."""
import json,math,os,sys
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import numpy as np
from vs_seg_task_cpu_support import resource_gate
from vs_seg_selection_sensitivity import completion_gate,load_verified_records,sha,SEED,DRAWS
from verify_vs_seg_selection_sensitivity import scalar_bootstrap,scalar_mean,percentile_scalar
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/vs_seg_selection_sensitivity'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 sys.stdout.reconfigure(encoding='utf-8');resource_gate();gate,contract=completion_gate()
 if not gate['allowed']: raise ValueError('Entire original cohort must complete before any effect reading')
 path=OUT/'independent_real_all_endpoints_replay.json'
 if path.exists(): raise ValueError('Never overwrite real replay proof')
 successful=[(p,read(p)) for p in sorted(OUT.glob('attempt_*.json'))];successful=[(p,r) for p,r in successful if r.get('complete')]
 if len(successful)!=1: raise ValueError('Require one successful fixed secondary analysis, retain all incomplete gate attempts')
 result_path,result=successful[0];roster=contract['main_roster'];coverage={r['patient']:r for r in read(ROOT/'experiments/vs_seg_full_volume_coverage/attempt_01.json')['patients']};records,provenance=load_verified_records(roster,coverage);draws=np.random.default_rng(SEED).integers(0,45,size=(DRAWS,45));errors=[];rows=[]
 def close(a,b,why):
  if a is None or b is None:
   if a!=b: errors.append('Undefined endpoint differs '+why)
  elif abs(float(a)-float(b))>1e-12: errors.append('Numeric endpoint differs '+why)
 for row in result['analysis']['endpoints']:
  label=row['label_and_qualification'];model=row['model'];baseline=row['baseline'];eligible=[coverage[p]['labels'][label]['old_target_rule_eligible'] for p in roster];values=[];four=[];parts=row['endpoint'].split('/');image=row['kind']=='image'
  for patient,ok in zip(roster,eligible):
   pair=[records[patient][name] for name in (model,baseline)]
   if image:
    region,weighting=parts;full=[r['image_metrics'][region][weighting] for r in pair];chosen=[]
    if ok:
     indices=coverage[patient]['labels'][label]['selected_four_indices']
     if len(indices)!=4 or len(set(indices))!=4: raise ValueError('Four target identity differs')
     for record in pair:
      plane={x['z']:x[region] for x in record['per_plane_image_errors']};selected=[plane[z] for z in indices]
      if weighting=='target_equal_nmse': chosen.append(scalar_mean([x['nmse'] for x in selected if x['pixels']>0]))
      else: count=sum(x['pixels'] for x in selected);chosen.append(math.fsum(x['sse'] for x in selected)/count if count else None)
    four.append(chosen[0]-chosen[1] if chosen and all(x is not None for x in chosen) else None)
   else:
    domain,metric=parts;full=[r['task_metrics'][label][domain][metric] for r in pair];four.append(None)
   values.append(full[0]-full[1] if all(x is not None for x in full) else None)
  groups={'all':[i for i in range(45)],'eligible':[i for i in range(45) if eligible[i]],'excluded':[i for i in range(45) if not eligible[i]]};points={key:scalar_mean([values[i] for i in selected]) for key,selected in groups.items()}
  if image: groups['four_targets']=groups['eligible'];points['four_targets']=scalar_mean([four[i] for i in groups['eligible']])
  for key,selected in groups.items():
   data=four if key=='four_targets' else values;finite=sum(data[i] is not None for i in selected);expected=dict(planned_patients=len(selected),finite_patients=finite,undefined_patients=len(selected)-finite)
   if row['group_counts'][key]!=expected: errors.append('Finite-patient group count differs '+row['endpoint']+' '+key)
  for key,left,right in [('patient_selection_shift','eligible','all'),('eligible_minus_excluded','eligible','excluded')]+([('target_selection_shift','four_targets','eligible'),('total_four_target_shift','four_targets','all')] if image else []): points[key]=points[left]-points[right] if points[left] is not None and points[right] is not None else None
  sampled=scalar_bootstrap(values,eligible,four,draws)
  for key,expected in row['estimates'].items():
   close(points[key],expected['mean_difference'],row['endpoint']+' '+key);distribution=sampled[key]
   if len(distribution)!=expected['valid_bootstrap_draws'] or 5000-len(distribution)!=expected['undefined_bootstrap_draws']: errors.append('Bootstrap finite/undefined count differs '+key)
   interval=[percentile_scalar(distribution,p) for p in (2.5,97.5)] if distribution else None
   if interval is None: close(None,expected['ci95_percentile'],key+' interval')
   else:
    for a,b in zip(interval,expected['ci95_percentile']): close(a,b,key+' interval')
  fraction=row['group_counts']['eligible']['finite_patients']/row['group_counts']['all']['finite_patients'] if row['group_counts']['all']['finite_patients'] else None;close(fraction,row['composition_identity']['eligible_fraction_of_finite_all'],'Fraction')
  residual=points['all']-fraction*points['eligible']-(1-fraction)*points['excluded'] if all(points[k] is not None for k in ('all','eligible','excluded')) else None;close(residual,row['composition_identity']['residual'],'Composition identity')
  directions={'eligible_vs_all':points['all'] is not None and points['eligible'] is not None and points['all']*points['eligible']<0}
  if image:
   directions.update(four_targets_vs_all=points['all'] is not None and points['four_targets'] is not None and points['all']*points['four_targets']<0,four_targets_vs_eligible=points['eligible'] is not None and points['four_targets'] is not None and points['eligible']*points['four_targets']<0)
   if all(points[k] is not None for k in ('all','eligible','four_targets')): close((points['four_targets']-points['all'])-((points['eligible']-points['all'])+(points['four_targets']-points['eligible'])),row['shift_identity_residual'],'Total shift identity')
  if directions!=row['point_estimate_sign_changes']: errors.append('Point-estimate direction flag differs')
  rows.append(dict(label=label,model=model,baseline=baseline,endpoint=row['endpoint'],kind=row['kind'],estimates_replayed=len(row['estimates'])));print(json.dumps(dict(endpoint_verified=len(rows),endpoint=row['endpoint'])),flush=True)
 if len(rows)!=112 or len({tuple(x[k] for k in ('label','model','baseline','endpoint')) for x in rows})!=112: errors.append('All 112 unique fixed endpoints not covered')
 proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=not errors,verification_script_sha256=sha(__file__),result_file=result_path.relative_to(ROOT).as_posix(),result_sha256=sha(result_path),contract_sha256=result['contract_sha256'],plan_sha256=sha(ROOT/'VS_SEG_SELECTION_REAL_REPLAY_PLAN_2026-10-03.md'),patients=45,endpoints_replayed=len(rows),bootstrap_draws=5000,record_provenance=provenance,endpoints=rows,errors=errors,gpu_used=False,publication_claim_confirmed=False,scope='All saved real endpoint aggregation, patient groups, shared draw scalar bootstrap, manual percentile and identities; raw-loader/hash gates, RNG and previously synthetic-verified scalar helper reused; no neural inference')
 with path.open('x',encoding='utf-8') as f: json.dump(proof,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(complete=not errors,endpoints=len(rows),errors=errors)),flush=True);return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
