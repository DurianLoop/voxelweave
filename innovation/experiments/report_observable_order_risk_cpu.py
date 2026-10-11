"""Report all frozen policies only after the independent all45 replay."""
import csv,json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/observable_order_risk_cpu'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');r=read(OUT/'attempt_01.json');v=read(OUT/'independent_observables_and_rankings.json')
 assert r['complete'] and v['complete'] and not r['errors'] and not v['errors']
 assert v['result_sha256']==sha(OUT/'attempt_01.json') and v['run_contract_sha256']==sha(OUT/'run_contract.json')
 assert len(r['patients'])==len(v['patients'])==45 and v['old_analytic_volumes_replayed']==180
 features=['order_rms','order_max','raw_pipeline_rms','anchor_roundtrip_rms','pchip_linear_rms'];policies={**r['policies'],'oracle':r['oracle']}
 names={'order_rms':'主候选 order_rms','order_max':'次要 order_max','raw_pipeline_rms':'raw−pipeline RMS','anchor_roundtrip_rms':'anchor roundtrip RMS','pchip_linear_rms':'raw PCHIP−linear RMS','oracle':'真值辅助 oracle'}
 lines=['# 仅观测层顺序差风险候选：固定配置停止','',
 '45名已见CISS、2,565内部缺层，固定15人使用pipeline PCHIP、其余使用raw PCHIP。新方法独立确认患者0，0新神经前向、GPU未使用。producer实际exit0，独立verifier session35552实际exit0、errors=[]；实现复核通过，主候选科学开发门槛失败。','',
 '特征只由观测层构造，不使用缺层真值/标签。每个信号选最低15人，平局按冻结原名单；评分使用既有两标签full Dice的pipeline−raw，未读取运行中的post任务结果。不能改预算、排名方向、标签或用次要max替代失败主候选。','',
 '| 固定规则 | JSON选中15人平均ΔDice | RTSTRUCT平均ΔDice | JSON全45政策ΔDice | RTSTRUCT全45政策ΔDice | 双标签逐人−.01守卫 |','| --- | ---: | ---: | ---: | ---: | --- |']
 for name,p in policies.items():
  a=p['task']['original_json'];b=p['task']['rtstruct'];lines.append(f"| {names[name]} | {a['selected_mean_utility']:+.8f} | {b['selected_mean_utility']:+.8f} | {a['whole45_policy_minus_all_raw']:+.8f} | {b['whole45_policy_minus_all_raw']:+.8f} | {'通过' if p['all_selected_both_label_guard'] else '失败'} |")
 lines += ['', '主候选两标签均未优于全部三个强比较和随机同预算97.5分位；自身逐患者guard也失败。次要max亦失败，不能换作主候选。raw−pipeline与anchor roundtrip选择相同15人、顺序不同，均比主候选均值较好；这些强比较自身也未满足guard，不视作成功政策。','',
 '| 随机同预算（5000次无放回，seed20261102） | 选中15人的平均ΔDice | 中央95%经验分布 |','| --- | ---: | --- |']
 for ref in ('original_json','rtstruct'):
  p=r['random_same_budget'][ref];lines.append(f"| {ref} | {p['mean']:+.8f} | [{p['ci95_percentile'][0]:+.8f}, {p['ci95_percentile'][1]:+.8f}] |")
 c=policies['order_rms'];a=c['task']['original_json'];b=c['task']['rtstruct']
 lines += ['', '这里的区间是固定45人中随机15人选择的经验分布，不是新患者泛化均值的置信区间，也不是familywise显著性证据。', '',
 f"主候选选中者在JSON下{a['negative_selected_patients']}/15人ΔDice<0，RTSTRUCT下{b['negative_selected_patients']}/15人<0；最差分别{a['minimum_selected_utility']:+.8f}和{b['minimum_selected_utility']:+.8f}。平均support NMSE变化{c['selected_mean_support_nmse_change']:+.10g}，图像误差下降未满足任务守卫。完整患者数值和规则入选列表保存于[45人CSV](experiments/observable_order_risk_cpu/all45_observables_and_old_utilities.csv)和原JSON。", '',
 f"全45有{r['patients_meeting_both_label_guard']}人符合双标签−.01guard。真值辅助oracle固定选15人并通过guard，证明本动作/预算下不是完全不可行；其全45ΔDice仅+0.00254166/+0.00274201（JSON/RT）。这是使用实际任务标签的不可部署上界，且本oracle排序最大化两标签较小效用，不能声称是分别最大化每标签均值的精确全局上界。", '',
 '| 观测信号 | JSON描述性Spearman | RTSTRUCT描述性Spearman |','| --- | ---: | ---: |']
 for f in features: lines.append(f"| {f} | {r['descriptive_spearman'][f]['original_json']:+.6f} | {r['descriptive_spearman'][f]['rtstruct']:+.6f} |")
 lines += ['', '主信号方向符合原假设但相关较弱；没有分布外预测或显著性结论。失败仅关闭这套固定特征/排名/动作/预算配置，不证明所有观测信息都不能预测任务变化。','',
 '复核覆盖：重新解码观测MR，独立ROI dot-product与math.fsum、另一anchor归一化/roundtrip表达、fresh pipeline/post数组、显式平均秩相关、全部6政策、逐人guard及5000随机排名/手写分位核对。producer实际只重放3条件×45=135旧解析体积，原计划写180；verifier额外覆盖pipeline_linear，4条件×45=180满足计划覆盖。保留producer覆盖不足的历史记录，不修改冻结计划或producer。共享解码器、skimage/NumPy RNG；不是独立软件栈或独立科学队列。','',
 '接续：等待post任务全45完成及18端点复核，再决定面内带宽/anchors不一致是否值得单独解释性对照。不得复活原HAT−pipelinePCHIP负向claim。',[ ]]
 lines=lines[:-1]
 report=ROOT/'OBSERVABLE_ORDER_RISK_CPU_RESULT_2026-10-03.md';report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 patients=[]
 for entry in r['patients']:
  p=ROOT/entry['file'];assert sha(p)==entry['sha256'];x=read(p);u=x['utility'];row={'patient':x['patient'],**x['features'],'json_full_dice_pipeline_minus_raw':u['original_json'],'rt_full_dice_pipeline_minus_raw':u['rtstruct'],'support_nmse_pipeline_minus_raw':u['support_nmse'],'both_label_guard':all(u[ref]>=-.01 for ref in ('original_json','rtstruct'))}
  row.update({f'selected_by_{k}':x['patient'] in y['selected_patients'] for k,y in policies.items()});patients.append(row)
 csvpath=OUT/'all45_observables_and_old_utilities.csv'
 with csvpath.open('w',encoding='utf-8-sig',newline='') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(patients[0]));writer.writeheader();writer.writerows(patients)
 provenance=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),proof_sha256=sha(OUT/'independent_observables_and_rankings.json'),report=report.relative_to(ROOT).as_posix(),report_sha256=sha(report),csv=csvpath.relative_to(ROOT).as_posix(),csv_sha256=sha(csvpath),patients=45,policies=6,independent_old_volumes_replayed=180,main_candidate_stopped=True,new_method_confirmation_patients=0,publication_claim_confirmed=False,actual_terminal_exit_codes={'producer_34708':0,'verifier_35552':0})
 (OUT/'report_provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(provenance,ensure_ascii=False))
if __name__=='__main__': main()
