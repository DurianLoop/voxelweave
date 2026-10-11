"""All18 task contrasts after all45 completion and the saved-output proof."""
import csv,json,math,sys
from pathlib import Path
from datetime import datetime,timezone
from vs_seg_full_volume_runtime import sha
from vs_seg_task_cpu_support import ROOT
from vs_seg_selection_sensitivity import load_verified_records
OUT=ROOT/'experiments/vs_seg_post_resize_task_cpu'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 sys.stdout.reconfigure(encoding='utf-8');r=read(OUT/'attempt_01.json');v=read(OUT/'independent_all_tasks_and_estimates.json');c=read(OUT/'run_contract.json');assert r['complete'] and v['complete'] and not r['errors'] and not v['errors'];assert len(r['patients'])==len(v['checked_patients'])==45 and len(r['analysis'])==len(v['endpoints'])==18;assert v['result_sha256']==sha(OUT/'attempt_01.json') and v['run_contract_sha256']==sha(OUT/'run_contract.json');coverage=read(ROOT/'experiments/vs_seg_full_volume_coverage/attempt_01.json');old,_=load_verified_records(c['main_roster'],{x['patient']:x for x in coverage['patients']});new={}
 for e in r['patients']:
  assert sha(ROOT/e['record_file'])==e['record_sha256'] and sha(ROOT/e['verification_file'])==e['verification_sha256'];p=read(ROOT/e['record_file']);q=read(ROOT/e['verification_file']);assert p['complete'] and q['complete'] and not q['errors'] and not p['cuda_initialized'];new[e['patient']]=p
 lines=['# 处理顺序与下游分割：post任务完整45人结果','',
 '固定原45已见CISS，一人仅新增一次post_resize_pchip冻结分割CPU forward；原raw/pipeline七条件没有重跑。session20644实际exit0，全45保存预测/全网格物理边界混淆计数及18标量bootstrap独立复核errors=[]。GPU未用，新方法独立确认患者0；结果是开发机制诊断，不是新的临床或科学确认。','',
 '| 标签 | raw PCHIP full Dice均值 | pipeline PCHIP均值 | post_resize PCHIP均值 |','| --- | ---: | ---: | ---: |'];means={}
 for ref in ('original_json','rtstruct'):
  m={name:math.fsum((new[p]['task_metrics'][ref]['full']['dice'] if name=='post' else old[p][name+'_pchip']['task_metrics'][ref]['full']['dice']) for p in c['main_roster'])/45 for name in ('raw','pipeline','post')};means[ref]=m;lines.append(f"| {ref} | {m['raw']:.8f} | {m['pipeline']:.8f} | {m['post']:.8f} |")
 lines += ['', 'post与pipeline的顺序不同，均仅处理插入缺层、保留原anchors/tail；raw省去面内256 down/up。三者使用相同observed-only强度范围和原网格。post−pipeline回答顺序的任务差，post−raw包含空间处理；不能把已知support NMSE的0.84%直接映射为Dice贡献。','',
 '| 标签 | 域 | 固定配对比较 | n/45 | 平均ΔDice | 95%患者bootstrap区间 | 负/零人数 |','| --- | --- | --- | ---: | ---: | --- | --- |']
 endpoint_rows=[]
 for e in r['analysis']:
  est=e['estimate'];lo,hi=est['ci95_percentile'] if est else (None,None);row=dict(reference=e['reference'],domain=e['domain'],comparison=e['comparison'],original_denominator=45,defined_n=len(e['included_patients']),undefined_patients=';'.join(e['undefined_patients']),mean_difference=est['mean_difference'] if est else None,ci_low=lo,ci_high=hi,negative_patients=est['negative_patients'] if est else None,zero_patients=est['zero_patients'] if est else None,seed=20261101,draws=5000,descriptive_without_familywise_claim=True);endpoint_rows.append(row)
  lines.append(f"| {e['reference']} | {e['domain']} | {e['comparison']} | {row['defined_n']}/45 | {row['mean_difference']:+.8f} | [{lo:+.8f}, {hi:+.8f}] | {row['negative_patients']}/{row['zero_patients']} |" if est else f"| {e['reference']} | {e['domain']} | {e['comparison']} | 0/45 | undefined | undefined | undefined |")
 lines += ['', '全部18端点均保留。full/slab固定45人；reference 1mm core为空时，三比较共同保留配对undefined名单，不填零。5000draw、seed20261101，区间是描述性患者配对bootstrap，未作familywise校正；区间跨0不能证明等效，区间不跨0不能单独证明临床因果。', '',
 '冻结任务模型与科学限制：官方相同2.5D attention/hardness网络、相同checkpoint、相同RAS/grid与阈值。独立程序复核共享来源标签、decoder和NumPy RNG；没有第二任务模型，也没有新的未见患者。当前原HAT−pipelinePCHIP负向主张被全45原实验反证的状态保持。', '',
 '所有患者反例及两参考完整输出见[45人任务CSV](experiments/vs_seg_post_resize_task_cpu/all45_task_dice.csv)，完整端点/undefined名单见[18端点CSV](experiments/vs_seg_post_resize_task_cpu/all18_descriptive_task_endpoints.csv)，[固定计划](VS_SEG_POST_RESIZE_TASK_CPU_PLAN_2026-10-03.md)及[独立proof](experiments/vs_seg_post_resize_task_cpu/independent_all_tasks_and_estimates.json)。', '',
 '下一步区分空间bandwidth、anchors混合与整volume归一化；[45人带宽诊断](ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_RESULT_2026-10-03.md)与[三人归一化预检](ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md)已完成，但尚未得到只改anchors的任务结果。改变anchors只能作为解释性干预。']
 report=ROOT/'VS_SEG_POST_RESIZE_TASK_CPU_RESULT_2026-10-03.md';report.write_text('\n'.join(lines)+'\n',encoding='utf-8');csv18=OUT/'all18_descriptive_task_endpoints.csv'
 with csv18.open('w',encoding='utf-8-sig',newline='') as stream:
  w=csv.DictWriter(stream,fieldnames=list(endpoint_rows[0]));w.writeheader();w.writerows(endpoint_rows)
 rows=[]
 for patient in c['main_roster']:
  row=dict(patient=patient)
  for ref in ('original_json','rtstruct'):
   for domain in ('full','observed_anchor_slab','exclude_reference_boundary_1mm'):
    values={name:(new[patient]['task_metrics'][ref][domain]['dice'] if name=='post' else old[patient][name+'_pchip']['task_metrics'][ref][domain]['dice']) for name in ('raw','pipeline','post')};row.update({f'{ref}_{domain}_{k}':value for k,value in values.items()});row.update({f'{ref}_{domain}_{left}_minus_{right}':values[left]-values[right] if values[left] is not None and values[right] is not None else None for left,right in [('post','pipeline'),('post','raw'),('pipeline','raw')]})
  rows.append(row)
 csv45=OUT/'all45_task_dice.csv'
 with csv45.open('w',encoding='utf-8-sig',newline='') as stream:
  w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 prov=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),proof_sha256=sha(OUT/'independent_all_tasks_and_estimates.json'),outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (report,csv18,csv45)],full_dice_means=means,all_endpoints=18,patients=45,actual_process_exit_code=0,new_method_confirmation_patients=0,publication_claim_confirmed=False)
 (OUT/'report_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(prov,ensure_ascii=False))
if __name__=='__main__':main()
