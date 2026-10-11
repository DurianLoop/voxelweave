"""Fixed observable signals and real old task-utility scoring, development only."""
import json,math,os,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import numpy as np
from scipy.stats import spearmanr
from skimage.transform import resize
from vs_seg_task_cpu_support import ROOT,resource_gate
from vs_seg_full_volume_cohort import cases_from_sources
from vs_seg_full_volume_runtime import decode_source,reconstruct,array_sha,sha
from vs_seg_selection_sensitivity import completion_gate,load_verified_records
from remind_native_t2_ixi_pair import prepared
OUT=ROOT/'experiments/observable_order_risk_cpu'
PLAN=ROOT/'OBSERVABLE_ORDER_RISK_CPU_PLAN_2026-10-03.md'
ANALYTIC=ROOT/'experiments/vs_seg_resampling_order_cpu'
FEATURES=('order_rms','order_max','raw_pipeline_rms','anchor_roundtrip_rms','pchip_linear_rms')

def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def support(left,right=None):
    mask=np.abs(left)>.01*max(float(np.max(abs(left))),1e-6)
    return mask if right is None else mask|(np.abs(right)>.01*max(float(np.max(abs(right))),1e-6))
def paired_rows(a,b,anchors,targets,span):
    rows=[]
    for z in targets:
        mask=support(anchors[z//4],anchors[z//4+1]);difference=(a[:,:,z].astype(float)-b[:,:,z].astype(float))/span;values=difference[mask]
        rows.append(dict(z=z,pixels=len(values),normalized_difference_sse=float(np.sum(values**2))))
    return rows
def rms(rows): return math.sqrt(math.fsum(r['normalized_difference_sse']/r['pixels'] for r in rows)/len(rows))
def policy(rows,indices):
    selected=[rows[i] for i in indices]
    task={ref:dict(selected_mean_utility=math.fsum(r['utility'][ref] for r in selected)/15,whole45_policy_minus_all_raw=math.fsum(r['utility'][ref] for r in selected)/45,minimum_selected_utility=min(r['utility'][ref] for r in selected),negative_selected_patients=sum(r['utility'][ref]<0 for r in selected)) for ref in ('original_json','rtstruct')}
    return dict(selected_indices=[int(i) for i in indices],selected_patients=[r['patient'] for r in selected],task=task,selected_mean_support_nmse_change=math.fsum(r['utility']['support_nmse'] for r in selected)/15,all_selected_both_label_guard=all(r['utility'][ref]>=-.01 for r in selected for ref in ('original_json','rtstruct')))

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();gate,original=completion_gate()
    if not gate['allowed']: raise ValueError('Original queue incomplete')
    analytic=read(ANALYTIC/'attempt_01.json');proof=read(ANALYTIC/'independent_replay_attempt_01.json')
    if not analytic['complete'] or not proof['complete'] or proof['errors'] or proof['result_sha256']!=sha(ANALYTIC/'attempt_01.json'): raise ValueError('Complete all45 analytic proof required')
    OUT.mkdir(exist_ok=False);coverage=read(ROOT/'experiments/vs_seg_full_volume_coverage/attempt_01.json');old,provenance=load_verified_records(original['main_roster'],{r['patient']:r for r in coverage['patients']});cases={r['patient']:r for r in cases_from_sources()}
    paths={PLAN,Path(__file__).resolve(),ANALYTIC/'attempt_01.json',ANALYTIC/'independent_replay_attempt_01.json',ANALYTIC/'run_contract.json',ROOT/'experiments/vs_seg_full_volume_runtime.py',ROOT/'experiments/vs_seg_full_volume_cohort.py',ROOT/'experiments/vs_seg_selection_sensitivity.py',ROOT/'experiments/vs_seg_task_cpu_support.py',ROOT/'experiments/remind_native_t2_ixi_pair.py'}
    for item in original['files']: paths.add(ROOT.parent/item['path'])
    for item in analytic['patients']: paths.add(ROOT/item['file'])
    for item in provenance: paths.add(ROOT/item['file'])
    contract=dict(created_utc=datetime.now(timezone.utc).isoformat(),main_roster=original['main_roster'],features=list(FEATURES),main_feature='order_rms',budget=15,random_seed=20261102,random_draws=5000,post_result_development=True,new_method_confirmation_patients=0,original_contract_sha256=sha(ROOT/'experiments/vs_seg_full_volume_cohort/run_contract.json'),files=[dict(path=p.relative_to(ROOT.parent).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(paths)])
    write(OUT/'run_contract.json',contract);result=dict(created_utc=datetime.now(timezone.utc).isoformat(),run_contract_sha256=sha(OUT/'run_contract.json'),complete=False,patients=[],errors=[],gpu_used=False,new_neural_forwards=0,new_method_confirmation_patients=0,publication_claim_confirmed=False,post_result_development=True,new_post_task_results_read=False)
    try:
        for patient in contract['main_roster']:
            resource_gate();start=time.perf_counter();native,_,_=decode_source(cases[patient]);prep=prepared(native[:,:,::4]);planes,lo,hi=prep;span=hi-lo;obs=list(range(0,native.shape[2],4));targets=[z for z in range(1,obs[-1]) if z%4];anchors=[native[:,:,z] for z in obs];saved=read(ANALYTIC/(patient+'.json'));raw=reconstruct('raw_pchip',native,prep,{});pipeline=reconstruct('pipeline_pchip',native,prep,{});linear=reconstruct('raw_linear',native,prep,{})
            for name,a in [('raw_pchip',raw),('pipeline_pchip',pipeline),('raw_linear',linear)]:
                if array_sha(a)!=saved['conditions'][name]['array_sha256']: raise ValueError('Old analytic array differs '+name)
            rp=paired_rows(raw,pipeline,anchors,targets,span);pl=paired_rows(raw,linear,anchors,targets,span);anchor_rows=[]
            for z,coarse,a in zip(obs,planes,anchors):
                roundtrip=(resize(np.clip(coarse,0,1),native.shape[:2],preserve_range=True,anti_aliasing=True)*span+lo).astype(np.float32);mask=support(a);diff=(roundtrip.astype(float)-a.astype(float))/span;values=diff[mask];anchor_rows.append(dict(z=z,pixels=len(values),normalized_difference_sse=float(np.sum(values**2))))
            features=dict(order_rms=math.sqrt(saved['kernels']['pchip']['order']['regions']['support']['target_equal_difference_nmse']),order_max=saved['kernels']['pchip']['order']['max_abs_normalized_difference_full_image'],raw_pipeline_rms=rms(rp),anchor_roundtrip_rms=rms(anchor_rows),pchip_linear_rms=rms(pl))
            # No target intensity or label enters the feature/ranking expressions above.
            utility={ref:old[patient]['pipeline_pchip']['task_metrics'][ref]['full']['dice']-old[patient]['raw_pchip']['task_metrics'][ref]['full']['dice'] for ref in ('original_json','rtstruct')};utility['support_nmse']=old[patient]['pipeline_pchip']['image_metrics']['support']['target_equal_nmse']-old[patient]['raw_pchip']['image_metrics']['support']['target_equal_nmse']
            row=dict(patient=patient,targets=targets,observed_indices=obs,span=span,features=features,per_plane_observable_differences=dict(raw_pipeline=rp,pchip_linear=pl,anchor_roundtrip=anchor_rows),utility=utility);path=OUT/(patient+'.json');write(path,row);result['patients'].append(dict(patient=patient,file=path.relative_to(ROOT).as_posix(),sha256=sha(path),seconds=time.perf_counter()-start));write(OUT/'attempt_01.json',result);print(json.dumps(dict(patient=patient,completed_patients=len(result['patients']),seconds=time.perf_counter()-start)),flush=True);del native,raw,pipeline,linear
        rows=[read(ROOT/r['file']) for r in result['patients']];policies={feature:policy(rows,sorted(range(45),key=lambda i:(rows[i]['features'][feature],i))[:15]) for feature in FEATURES};oracle=policy(rows,sorted(range(45),key=lambda i:(-min(rows[i]['utility'][ref] for ref in ('original_json','rtstruct')),i))[:15]);rng=np.random.default_rng(20261102);random_indices=[rng.choice(45,size=15,replace=False).tolist() for _ in range(5000)];random_results={ref:np.array([math.fsum(rows[i]['utility'][ref] for i in selected)/15 for selected in random_indices]) for ref in ('original_json','rtstruct')};random_summary={ref:dict(mean=float(v.mean()),ci95_percentile=[float(x) for x in np.percentile(v,[2.5,97.5])]) for ref,v in random_results.items()}
        candidate=policies['order_rms'];beats={ref:all(candidate['task'][ref]['selected_mean_utility']>policies[f]['task'][ref]['selected_mean_utility']+1e-12 for f in FEATURES[2:]) and candidate['task'][ref]['selected_mean_utility']>random_summary[ref]['ci95_percentile'][1]+1e-12 for ref in ('original_json','rtstruct')};passed=candidate['all_selected_both_label_guard'] and all(beats.values());correlation={feature:{ref:float(spearmanr([r['features'][feature] for r in rows],[r['utility'][ref] for r in rows]).statistic) for ref in ('original_json','rtstruct')} for feature in FEATURES}
        result.update(complete=True,policies=policies,oracle=oracle,random_indices=random_indices,random_same_budget=random_summary,descriptive_spearman=correlation,patients_meeting_both_label_guard=sum(all(r['utility'][ref]>=-.01 for ref in ('original_json','rtstruct')) for r in rows),main_candidate_beats_all_strong_and_random=beats,main_candidate_development_gate_passed=passed,main_fixed_candidate_stopped=not passed,total_targets=sum(len(r['targets']) for r in rows))
    except Exception as exc:
        result['errors'].append(type(exc).__name__+': '+str(exc));result['traceback']=traceback.format_exc()
    result['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',result);print(json.dumps({k:result.get(k) for k in ('complete','errors','main_candidate_development_gate_passed','patients_meeting_both_label_guard')}),flush=True)
    if not result['complete']: raise SystemExit(1)
if __name__=='__main__': main()
