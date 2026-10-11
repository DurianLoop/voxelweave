"""Produce complete all45 statistics report and all twelve associations."""
import csv,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/full45_normalization_drift_cpu'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    r=read(OUT/'attempt_01.json');q=read(OUT/'independent_scalar_csv_and_correlations.json')
    assert r['complete'] and q['complete'] and not r['errors'] and not q['errors'] and q['result_sha256']==sha(OUT/'attempt_01.json')
    csvpath=OUT/'all12_descriptive_associations.csv'
    with csvpath.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(r['associations'][0]));writer.writeheader();writer.writerows(r['associations'])
    lines=['# 固定完整45人：整volume统计反馈审计','',
           '90个既有raw/post数组逐位重放通过。此次新增神经前向0，GPU使用0。单线程低优先级CPU，每人均通过15GB磁盘/8GB可用内存门槛。另一个不导入torch的标量复核通过45患者、270采集域矩单元、90相同图像域RMS、90 Fraction Dice差、12手工关联和45行CSV。',
           '', '此方案在原任务结果已知之后制定，是事后开发审计。所有45人均保留；统计从候选图像计算，没有用missing真值或labels选择患者/阈值。科学独立确认患者仍为0。','',
           'raw与post的anchors/tail图像值相同，但各自整volume归一化后有实数关系 `Ypost=a*Yraw+b`，`a=std_raw/std_post`、`b=(mean_raw-mean_post)/std_post`。float32实际数组与解析关系仅在浮点容差内一致，不声称逐位相同。','',
           '| 输入统计指标 | 45人均值 | 最小 | 最大 |','| --- | ---: | ---: |']
    for feature,s in r['summary'].items():lines.append(f"| {feature} | {s['mean']:+.12f} | {s['minimum']:+.12f} | {s['maximum']:+.12f} |")
    lines+=['', '所有45人的post std都减少，平均−2.4882%；于是相同anchors归一化后的scale平均增加2.5525%。归一化anchors RMS平均.026642，不是图像物理误差或病灶损失。均值offset较小也不能推出网络对它不敏感。三人pilot的scale/RMS落在全45范围内，但这不保证任务响应代表性。','',
            '| 原post−raw full Dice | JSON均值 | RT均值 |','| --- | ---: | ---: |']
    for group in ('full45','fixed_pilot3','remaining42'):
        a,b=r['cohort_dice']['original_json'][group],r['cohort_dice']['rtstruct'][group]
        lines.append(f"| {group}，n={a['n']} | {a['mean']:+.12f} | {b['mean']:+.12f} |")
    lines+=['', '固定pilot三人原post−raw为正、其余42人及全45为负。不能把三人微小统计互换效果外推到全45，也不把排除三人的42人称为新确认集。这里仅分组说明已知技术预检的限制。','',
            '| 预列输入指标 | JSON Pearson / Spearman | RT Pearson / Spearman |','| --- | ---: | ---: |']
    for feature in ('a_minus_one','b','observed_normalized_rms'):
        def value(ref,method):return next(e['coefficient'] for e in r['associations'] if e['feature']==feature and e['reference']==ref and e['method']==method)
        lines.append(f"| {feature} | {value('original_json','pearson'):+.6f} / {value('original_json','spearman'):+.6f} | {value('rtstruct','pearson'):+.6f} / {value('rtstruct','spearman'):+.6f} |")
    lines+=['', 'scale/RMS的Pearson约−.30，但Spearman接近0，不能支持稳定单调的部署风险排序；offset的关联也只是同一事后队列关联。原图像、病灶、模型曝光与其他因素共同变化，没有因果识别。没有bootstrap、p值、风险挑人、政策阈值或归因比例。所有12关联保留，不因最大值选择新动作。','',
            '当前可成立的是：observed-preserving图像合同不自动等于observed网络输入保持，生成缺层可经整volume统计反馈改变anchors输入。宽机制在[Region Normalization及Partial Convolution](literature/2026-10-03_masked_normalization_primary_reading.md)已有明确先例。这是本管线中的可复核实例，尚不构成首次机制发现或有效新方法。','',
            '[45行统计和全部原任务差](experiments/full45_normalization_drift_cpu/all45_statistics_and_saved_dice.csv)、[12完整关联](experiments/full45_normalization_drift_cpu/all12_descriptive_associations.csv)、[全部患者矩及输入hash](experiments/full45_normalization_drift_cpu/attempt_01.json)、[独立标量复核](experiments/full45_normalization_drift_cpu/independent_scalar_csv_and_correlations.json)。',
            '', '后续保留anchor-only统计作为训练/推理一致的控制。现有证据不足以扩大三人统计互换到45人或重新调anchors模糊。先明确任务训练来源/曝光、共享患者身份和未见确认角色，再用完整模型×输入矩阵检验输入域适应后是否仍有缺层任务损失。GPU训练尚未执行。']
    report=ROOT/'FULL45_NORMALIZATION_DRIFT_CPU_RESULT_2026-10-03.md';assert not report.exists();report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    prov=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),result_sha256=sha(OUT/'attempt_01.json'),proof_sha256=sha(OUT/'independent_scalar_csv_and_correlations.json'),outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (report,csvpath)])
    (OUT/'report_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(patients=45,associations=12,new_neural_forwards=0)))
if __name__=='__main__':main()
