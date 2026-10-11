"""Report authenticated completed analytic diagnostics, including first failure."""
import csv,hashlib,json,math,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/anchor_bandwidth_diagnostic_cpu'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.stdout.reconfigure(encoding='utf-8');r=read(OUT/'attempt_01.json');p=read(OUT/'independent_gradient_and_identities.json');assert r['complete'] and p['complete'] and not r['errors'] and not p['errors'] and p['result_sha256']==sha(OUT/'attempt_01.json');assert len(r['patients'])==len(p['patients'])==45;records=[read(ROOT/x['file']) for x in r['patients']];names=list(records[0]['summaries']);lines=['# anchors/缺层相位梯度能量：45人解析结果','',
 '固定45已见CISS，855完整四层间隔、2,565缺层。producer session44318与verifier15909均实际exit0；90旧raw/post体积逐位SHA重放、四条件体积身份和全部梯度dot-product/四汇总复核errors=[]。GPU未用，0新神经前向，新科学确认患者0。','',
 '预写指标L=log(Eanchor/mean(Einserted))，E是在同一个observed-only ROI内的面内梯度能量，每患者先对间隔等权平均。它是所测纹理统计，不是解剖保真、病灶保真或任务Dice。','',
 '| 条件 | E0 | E1 | E2 | E3 | 患者平均L | exp(平均L) |','| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
 for name in names:
  means=[math.fsum(x['summaries'][name]['phase_mean_energy'][q] for x in records)/45 for q in range(4)];logs=[x['summaries'][name]['log_anchor_to_inserted_energy'] for x in records];assert all(x is not None for x in logs);mean=math.fsum(logs)/45;lines.append(f"| {name} | "+' | '.join(f'{x:.9g}' for x in means)+f' | {mean:+.8f} | {math.exp(mean):.6f} |')
 lines += ['', 'exp(平均L)是患者能量比的几何平均，不是上表患者平均能量的比，也不是个体增长百分比的算术平均。', '', '| 预定配对差 | n | 平均ΔL | min | max | 正/负/零人数 |','| --- | ---: | ---: | ---: | ---: | --- |']
 for x in r['analysis']:lines.append(f"| {x['comparison']} | {x['included_patients']} | {x['mean']:+.8f} | {x['minimum']:+.8f} | {x['maximum']:+.8f} | {x['positive_patients']}/{x['negative_patients']}/{x['zero_patients']} |")
 lines += ['', 'mixed_post−raw的L全45升高，平均+.93863810；同时处理anchors后，slab_roundtrip−mixed_post全45降低，平均−.96664477，平均L从1.26286697回到.29622220（raw为.32422887）。这支持本合同中面内处理扩大了观测相位与插入相位的梯度能量差。','',
 '两个改变anchors的条件仅是解释性干预，不满足原observed-preserving SR合同。slab_roundtrip的缺层与mixed_post逐位相同；raw_anchor_roundtrip的缺层与raw逐位相同；四条件tail相同。把这些控制当SR性能改进会违反原任务定义。','',
 '该log ratio可分为log(Eanchor)−log(Einserted)，所以本2×2的两组配对差按构造相同到浮点容差。这是指标可分离性，不能把四行当四个独立机制发现或任务无交互证据。原raw已有PCHIP带来的phase差，真实解剖也随z变化，common ROI不是组织跟踪mask；本结果不证明所有周期纹理为伪影。','',
 '没有网络前向就没有本干预的Dice或activation结论。将来只改anchors的任务对照还需固定paired baseline的全volume归一化，见[三个患者预检](ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md)。共享decoder/resize/NumPy，独立复算不是新科学队列。', '',
 '数据：[45人CSV](experiments/anchor_bandwidth_diagnostic_cpu/all45_phase_energies.csv)、[预写方案](ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_PLAN_2026-10-03.md)、[独立复核](experiments/anchor_bandwidth_diagnostic_cpu/independent_gradient_and_identities.json)。']
 report=ROOT/'ANCHOR_BANDWIDTH_DIAGNOSTIC_CPU_RESULT_2026-10-03.md';report.write_text('\n'.join(lines)+'\n',encoding='utf-8');csvpath=OUT/'all45_phase_energies.csv';rows=[]
 for x in records:
  row=dict(patient=x['patient'],intervals=len(x['intervals']['raw']),changed_anchor_pixels=x['changed_anchor_pixels'])
  for name in names:
   row.update({f'{name}_phase{q}_gradient_energy':x['summaries'][name]['phase_mean_energy'][q] for q in range(4)});row[f'{name}_log_ratio']=x['summaries'][name]['log_anchor_to_inserted_energy']
  rows.append(row)
 with csvpath.open('w',encoding='utf-8-sig',newline='') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 nout=ROOT/'experiments/anchor_normalization_control_cpu_attempt_02';n=read(nout/'attempt_01.json');assert n['complete'] and not n['errors'] and n['cuda_initialized'] is False;assert len(n['patients'])==3 and n['all_six_fixed_stats_missing_and_tail_bitwise_equal'];nlines=['# anchors-only对照必须控制全volume归一化','',
 '固定VS-SEG-202/203/204，raw及mixed_post两基线，共6个真实体积对照。修正版session90226实际exit0、CUDA未初始化、0神经前向。共享模块间接导入torch，未加载checkpoint；MONAI NormalizeIntensity类从已认证wheel/vendored文件隔离执行，Transform基类替换为object，未导入完整MONAI环境。该技术预检没有独立第二实现/科学患者复核，不等同于任务成功。','',
 '| 患者/基线 | 原缺层像素不变 | ownstats归一化后缺层变化像素 | 最大绝对差 | RMS | 固定stats缺层变化像素 |','| --- | --- | ---: | ---: | ---: | ---: |']
 for patient in n['patients']:
  for x in patient['conditions']:
   own=x['missing_own_stats_minus_baseline'];fixed=x['missing_fixed_stats_minus_baseline'];nlines.append(f"| {patient['patient']}/{x['baseline']} | 是 | {own['changed_pixels']}/{own['pixels']} | {own['max_abs']:.8f} | {own['rms']:.8f} | {fixed['changed_pixels']} |")
 nlines += ['', '六对均保持原缺层数组完全相同；更换anchors后使用各自mean/std，全部缺层像素的网络前归一化数值改变。固定对应基线的mean/std后，六对missing与tail逐位一致。这是输入层面的直接反例：重建数组中的missing不变，并不保证任务网络接收的missing不变。最大差单位为归一化强度，不是原MRI值、解剖误差或Dice。', '',
 '首session51036实际exit1，最后的torch未导入断言错误；先前六组数组断言已经通过。首计划/脚本/contract/failed attempt均完整保留，追加[修正说明](ANCHOR_NORMALIZATION_CONTROL_CPU_REPAIR_2026-10-03.md)与attempt02，只修过程标记、不改变患者/条件/计算。首结果静态torch_imported=false不是实际状态证据。','',
 '后续任务应比较2×2输入条件×own/fixed normalization，而非只比较改anchors前后。固定stats技术控制可用原解析baseline由anchors构造，但改变observed anchors的图像条件仍不符合原SR合同。未执行此任务矩阵，0新Dice结论。','',
 '证据：[初方案](ANCHOR_NORMALIZATION_CONTROL_CPU_PLAN_2026-10-03.md)、[首失败](experiments/anchor_normalization_control_cpu/attempt_01.json)、[实际修正版结果](experiments/anchor_normalization_control_cpu_attempt_02/attempt_01.json)。']
 nreport=ROOT/'ANCHOR_NORMALIZATION_CONTROL_CPU_RESULT_2026-10-03.md';nreport.write_text('\n'.join(nlines)+'\n',encoding='utf-8');prov=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),proof_sha256=sha(OUT/'independent_gradient_and_identities.json'),normalizer_result_sha256=sha(nout/'attempt_01.json'),normalizer_first_failure_sha256=sha(ROOT/'experiments/anchor_normalization_control_cpu/attempt_01.json'),outputs=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in (report,csvpath,nreport)],terminal_exit_codes={'producer_44318':0,'verifier_15909':0,'normalization_first_51036':1,'normalization_repair_90226':0},publication_claim_confirmed=False)
 (OUT/'report_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(prov,ensure_ascii=False))
if __name__=='__main__':main()
