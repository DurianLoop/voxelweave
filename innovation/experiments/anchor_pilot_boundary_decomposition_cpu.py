"""Post-hoc count partitions of already verified pilot outputs; no inference."""
import csv,hashlib,json,math,sys
from datetime import datetime,timezone
from pathlib import Path
from vs_seg_task_cpu_support import resource_gate
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/anchor_pilot_boundary_decomposition_cpu'
PILOT=ROOT/'experiments/anchor_bandwidth_task_cpu_pilot'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dice(x):
 d=2*x['tp']+x['fp']+x['fn'];return 2*x['tp']/d if d else None
def write_csv(p,rows):
 with p.open('w',encoding='utf-8-sig',newline='') as stream:
  w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 sys.stdout.reconfigure(encoding='utf-8');gate=resource_gate();OUT.mkdir(exist_ok=False)
 r=read(PILOT/'attempt_01.json');p=read(PILOT/'independent_inputs_and_all36_estimates.json')
 assert r['complete'] and p['complete'] and not r['errors'] and not p['errors'] and p['result_sha256']==sha(PILOT/'attempt_01.json')
 sources={};records={}
 def load(path):
  v=read(path);assert v['complete'];assert sha(ROOT/v['prediction_file'])==v['prediction_sha256'];sources[path.relative_to(ROOT).as_posix()]=sha(path);return v
 for patient in ('VS-SEG-202','VS-SEG-203','VS-SEG-204'):
  records[patient]={'raw':load(ROOT/'experiments/vs_seg_full_volume_cohort/patients'/patient/'raw_pchip_attempt_01.json'),
   'post':load(ROOT/'experiments/vs_seg_post_resize_task_cpu'/f'{patient}.json')}
 for e in r['patients']:
  assert sha(ROOT/e['file'])==e['sha256'];records[e['patient']][e['condition']]=load(ROOT/e['file'])
 counts={};partition_rows=[]
 for patient,conditions in records.items():
  counts[patient]={}
  for condition,record in conditions.items():
   counts[patient][condition]={}
   for ref,m in record['task_metrics'].items():
    full={k:m['full'][k] for k in ('tp','fp','fn')};outside={k:m['exclude_reference_boundary_1mm'][k] for k in full};band={k:full[k]-outside[k] for k in full}
    assert all(x>=0 for x in band.values());assert all(full[k]==outside[k]+band[k] for k in full)
    assert math.isclose(dice(full),m['full']['dice'],abs_tol=1e-12)
    assert math.isclose(dice(outside),m['exclude_reference_boundary_1mm']['dice'],abs_tol=1e-12)
    counts[patient][condition][ref]={'full':full,'outside_1mm_band':outside,'excluded_1mm_band':band}
    for domain,x in counts[patient][condition][ref].items():partition_rows.append(dict(patient=patient,condition=condition,reference=ref,domain=domain,**x,dice=dice(x)))
  for ref in ('original_json','rtstruct'):
   for domain in ('full','outside_1mm_band','excluded_1mm_band'):
    assert len({v[ref][domain]['tp']+v[ref][domain]['fn'] for v in counts[patient].values()})==1
 paired=[];summaries=[]
 for e in r['analysis']:
  if e['domain']!='full':continue
  left,right=e['comparison'].split('-');ref=e['reference']
  for domain in ('full','outside_1mm_band','excluded_1mm_band'):
   rows=[]
   for patient in records:
    a=counts[patient][left][ref][domain];b=counts[patient][right][ref][domain]
    d=dice(a)-dice(b) if dice(a) is not None and dice(b) is not None else None
    row=dict(patient=patient,comparison=e['comparison'],reference=ref,domain=domain,
      delta_tp=a['tp']-b['tp'],delta_fp=a['fp']-b['fp'],delta_fn=a['fn']-b['fn'],delta_dice=d)
    rows.append(row);paired.append(row)
   defined=[x['delta_dice'] for x in rows if x['delta_dice'] is not None]
   summary=dict(comparison=e['comparison'],reference=ref,domain=domain,original_n=3,defined_n=len(defined),
      mean_delta_dice=math.fsum(defined)/len(defined) if defined else None,
      mean_delta_tp=math.fsum(x['delta_tp'] for x in rows)/3,
      mean_delta_fp=math.fsum(x['delta_fp'] for x in rows)/3,
      mean_delta_fn=math.fsum(x['delta_fn'] for x in rows)/3)
   summaries.append(summary)
   if domain=='full':assert math.isclose(summary['mean_delta_dice'],e['mean'],abs_tol=1e-12)
 assert len(paired)==108 and len(summaries)==36 and len(partition_rows)==108
 outputs=[]
 for name,rows in [('all108_condition_partitions.csv',partition_rows),('all108_paired_partition_differences.csv',paired),('all36_partition_summaries.csv',summaries)]:
  path=OUT/name;write_csv(path,rows);outputs.append(path)
 result=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),plan_sha256=sha(ROOT/'ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_CPU_PLAN_2026-10-03.md'),resource_gate=gate,
  complete=True,errors=[],posthoc_after_all36_results_read=True,new_neural_forwards=0,torch_imported='torch' in sys.modules,
  new_method_confirmation_patients=0,publication_claim_confirmed=False,
  source_bindings=[dict(path=k,sha256=v) for k,v in sorted(sources.items())],summaries=summaries)
 (OUT/'attempt_01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 lines=['# 三人边界反向结果：事后计数分解','','固定两标签/六比较，读取18个已复核条件记录。无新MRI解码或神经前向、未导入torch。full−去1mm带混淆计数非负，三个分区reference体素跨条件相同；完整36个汇总和108个逐人比较已保存。','','本分析写于全部pilot端点已见之后，是开发性事后解释。分区Dice分母不同，不能相加或互相替代；“outside”还含远离reference的背景，并非纯病灶核心。','',
  '| 标签 | post_fixed−post 域 | 平均ΔTP | 平均ΔFP | 平均ΔFN | 平均ΔDice |','| --- | --- | ---: | ---: | ---: | ---: |']
 for s in summaries:
  if s['comparison']=='post_anchor_fixed-post':lines.append(f"| {s['reference']} | {s['domain']} | {s['mean_delta_tp']:+.2f} | {s['mean_delta_fp']:+.2f} | {s['mean_delta_fn']:+.2f} | {s['mean_delta_dice']:+.8f} |")
 lines += ['','完整逐人计数见[108配对值](experiments/anchor_pilot_boundary_decomposition_cpu/all108_paired_partition_differences.csv)，包括反例；[36汇总](experiments/anchor_pilot_boundary_decomposition_cpu/all36_partition_summaries.csv)及[108条件分区](experiments/anchor_pilot_boundary_decomposition_cpu/all108_condition_partitions.csv)保留全部条件。','','这些变化仅定位保存预测在参考标注附近的错误。它们不证明MRI解剖改变、标注错误、临床损害或某个因果机制，也不恢复已失败的post带宽主张。两标签及三人开发诊断不是科学独立确认。']
 report=ROOT/'ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_CPU_RESULT_2026-10-03.md';report.write_text('\n'.join(lines)+'\n',encoding='utf-8');outputs.append(report)
 provenance=dict(script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),outputs=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in outputs])
 (OUT/'report_provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(complete=True,errors=[],summaries=len(summaries),paired=len(paired),selected=[s for s in summaries if s['comparison']=='post_anchor_fixed-post']),ensure_ascii=False))
if __name__=='__main__':main()
