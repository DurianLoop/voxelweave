"""Bound to inspected primary tables; Decimal differences, no inferred paired tests."""
import gzip,json,time
from decimal import Decimal as D
from pathlib import Path
from resource_guard_v1 import HERE,guard,entry,dump
started=time.perf_counter();before=guard(started);out=HERE/'primary_table_arithmetic_attempt01';out.mkdir(exist_ok=False)
sources=[]
def text(name,index):
 p=HERE/'primary_html_attempt01'/name/'blocks.json.gz';sources.append(entry(p));return json.loads(gzip.decompress(p.read_bytes()))[index]['text']
ot=text('openmasc',99);gt=text('greedy',160);ct=text('greedy',112);ft=text('active_fewshot',49)
for s in ('0.776','27.53','0.768','27.09','0.710','21.45','27.55','0.777','27.62'):assert s in ot
full=(D('.777'),D('27.62'))
open_results=[]
for label,s,p in [('same_architecture_VD_random','.776','27.53'),('same_architecture_equispaced','.768','27.09'),('without_DCR','.710','21.45'),('without_PPO_DCR_cotrain','.776','27.55')]:
 open_results.append(dict(comparator=label,delta_SSIM=str(full[0]-D(s)),delta_PSNR_dB=str(full[1]-D(p))))
greedy=list(map(D,['.7230','.7442','.9106','.8917']));na=list(map(D,['.7213','.7421','.9099','.8909']));g09=list(map(D,['.7232','.7449','.9106','.8921']))
for v in greedy+na+g09:assert format(v,'f') in gt
gr=[dict(setting=label,greedy_minus_test_GT_NA_oracle=str(g-n),gamma09_minus_greedy=str(h-g)) for label,g,n,h in zip(['knee_base','knee_long','brain_base','brain_long'],greedy,na,g09)]
costs=[]
for dataset,horizon,gwall,ngwall,nggpus in [('knee','base','1.0','1.5',1),('knee','long','1.5','2.0',2),('brain','base','2.0','3.0',2),('brain','long','4.5','5.0',4)]:
 assert gwall in ct and ngwall in ct
 costs.append(dict(dataset=dataset,horizon=horizon,greedy_approximate_GPU_days=str(D(gwall)),nongreedy_approximate_GPU_days=str(D(ngwall)*nggpus),measurement_quality='Very approximate policy-training table only; excludes reconstruction pretraining/inference/I-O attribution'))
fr=[]
for k,r,p,d in [(4,'51.2','59.4','54.8'),(8,'57.9','65.5','61.7'),(16,'63.9','70.6','66.8')]:
 assert all(s in ft for s in (r,p,d))
 fr.append(dict(K=k,proposed_minus_random_percentage_points=str(D(p)-D(r)),proposed_minus_DVRL_percentage_points=str(D(p)-D(d)),support_plus_reward_validation_label_slots=k+8,unique_subject_annotation_count_confirmed=False))
r=dict(complete=True,errors=[],OpenMASC=open_results,Greedy=gr,approximate_training_cost=costs,active_fewshot=fr,
 OpenMASC_test_subjects=20,OpenMASC_test_slices=720,slice_to_subject_ratio=36,paired_P_values_recomputed=False,
 source_bindings=[entry(Path(__file__)),entry(HERE/'CPU_EXPLORATION_PROTOCOL.md')]+list({s['path']:s for s in sources}.values()),
 warnings=['Contrasts are not additive causal contribution shares','Reported means cannot recover patient-level paired variance or significance','Few-shot K+8 counts label slots only; annotation reuse and unique ID accounting unresolved','Printed rounded means may differ from prose differences by 0.1 pp'],
 MRI_arrays_loaded=0,GT_arrays_loaded=0,GPU_calls=0,optimizer_updates=0,medical_effect_scored=False,publication_claim_confirmed=False,
 resources_before=before,resources_after=guard(started),elapsed_seconds=time.perf_counter()-started)
dump(out/'receipt.json',r);print(json.dumps({k:r[k] for k in ('complete','OpenMASC','Greedy','approximate_training_cost','active_fewshot')}))
