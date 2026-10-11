"""Publish only the completed all45 analytic producer and independent replay."""
import csv,json,math,os,sys
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import numpy as np
from vs_seg_task_cpu_support import ROOT,resource_gate
from vs_seg_full_volume_runtime import sha
OUT=ROOT/'experiments/vs_seg_resampling_order_cpu'
REPORT=ROOT/'VS_SEG_RESAMPLING_ORDER_CPU_RESULT_2026-10-03.md'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_gate();d=read(OUT/'attempt_01.json');proof=read(OUT/'independent_replay_attempt_01.json')
    if not d['complete'] or d['errors'] or not proof['complete'] or proof['errors'] or proof['result_sha256']!=sha(OUT/'attempt_01.json'): raise ValueError('All45 independent proof required')
    data=[read(ROOT/r['file']) for r in d['patients']];rows=[]
    for endpoint in d['analysis']:
        e=endpoint['estimate'];rows.append({k:endpoint[k] for k in ('kernel','region','weighting','comparison')}|dict(patients=45,mean_difference=e['mean_difference'],ci_low=e['ci95_percentile'][0],ci_high=e['ci95_percentile'][1],negative_patients=e['negative_patients'],zero_patients=e['zero_patients'],positive_patients=45-e['negative_patients']-e['zero_patients']))
    p=OUT/'all36_descriptive_endpoints.csv'
    with p.open('x',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    lookup={(r['kernel'],r['region'],r['weighting'],r['comparison']):r for r in rows}
    means={name:{region:math.fsum(x['conditions'][name]['image_metrics'][region]['target_equal_nmse'] for x in data)/45 for region in ('support','original_json_lesion','rtstruct_lesion')} for name in data[0]['conditions']}
    order={kernel:dict(minimum=min(x['kernels'][kernel]['order']['max_abs_normalized_difference_full_image'] for x in data),median=float(np.median([x['kernels'][kernel]['order']['max_abs_normalized_difference_full_image'] for x in data])),maximum=max(x['kernels'][kernel]['order']['max_abs_normalized_difference_full_image'] for x in data)) for kernel in ('linear','pchip')}
    support=lookup['pchip','support','target_equal_nmse','pipeline-post_resize'];total=lookup['pchip','support','target_equal_nmse','pipeline-raw'];fraction=support['mean_difference']/total['mean_difference']
    lines=['# 全45处理顺序对照：裁剪未激活，PCHIP顺序效应小于整体处理效应','',
           '固定45已见CISS、2,565内部缺层、两原参考，producer和独立verifier均实际exit0。180既有解析体积逐位重放一致，90新post体积由另一表达式重新构造且SHA一致；36完整端点/逐患者/逐层ROI与标量bootstrap全部复核通过，errors=[]。新增神经forward为0，科学独立确认患者0。后续新任务队列是另一合同，尚未将其结果混入本报告。','',
           '本实验只能诊断处理因素，不能复活原HAT负向主张。新post先在原网格插值，再同observed min/max归一化、缩256及恢复；pipeline先缩observed layers再插值。anchors和不可插值tail逐位保留。全45不换病例，TSE不并入。','',
           '## 1. 显式裁剪实际改变了多少','',
           'linear/PCHIP、before/post四组合全部0像素、0层、0越界。因此这些解析条件间的差异不能归因于显式clip[0,1]。这不评价HAT残差后的clip；也不排除skimage内部clip、空间滤波/抗混叠/量化等其他因素。','',
           '## 2. 插值顺序是否改变输出','',
           '| 核 | 全图最大归一化差的患者min / median / max | 超过预写1e-6 |','| --- | --- | --- |']
    for kernel in ('linear','pchip'):
        v=order[kernel];lines.append(f"| {kernel} | {v['minimum']:.9g} / {v['median']:.9g} / {v['maximum']:.9g} | {d['order_above_linear_tolerance'][kernel]}/45 |")
    lines+=['',
            '线性对照符合预写解释容差。PCHIP的局部差可达观测范围约0.91%–1.98%，但“超过浮点容差”不等于有任务意义。独立Hermite/linear另一公式最大归一化误差≤预写5e-7，实际全队列最大'+f"{max(x['max_independent_constructor_normalized_error'] for x in proof['patients']):.9g}"+'；这些顺序差异不是PCHIP重算程序错误的证据。','',
            '## 3. 图像误差效应有多大','',
            '以下为患者等权、患者内缺层等权NMSE。负值表示左条件误差更小；45患者共享5000draw、seed20261031。所有区间均描述性、未familywise校正。','',
            '| 核/区域 | 比较 | 平均差 | 描述性95% CI | 负/零/正患者 |','| --- | --- | --- | --- | --- |']
    for row in rows:
        if row['weighting']!='target_equal_nmse': continue
        lines.append(f"| {row['kernel']}/{row['region']} | {row['comparison']} | {row['mean_difference']:.9g} | [{row['ci_low']:.9g}, {row['ci_high']:.9g}] | {row['negative_patients']}/{row['zero_patients']}/{row['positive_patients']} |")
    lines+=['',f'PCHIP支持域整体pipeline−raw为{total["mean_difference"]:.9g}；顺序pipeline−post为{support["mean_difference"]:.9g}，两均值比{fraction*100:.4f}%。这是已固定路径的描述性分解，不是“{fraction*100:.2f}%因果中介”或新理论。双病灶平均顺序差的两个加权版本CI均跨0，不能声称病灶平均收益，也不能声称等效。','',
            '## 4. NMSE降低不能等同结构保护','',
            '| 条件 | support mean NMSE | JSON lesion mean NMSE | RT lesion mean NMSE |','| --- | --- | --- | --- |']
    for name,values in means.items(): lines.append('| '+name+' | '+' | '.join(f'{values[r]:.9g}' for r in ('support','original_json_lesion','rtstruct_lesion'))+' |')
    lines+=['',
            '这里的roundtrip反而让support NMSE全部45人降低；两个病灶域也多数降低。旧已完成分割记录中raw PCHIP Dice .74459750、pipeline PCHIP .65476150，因此图像误差均值不能单独解释任务变化。不能预先把roundtrip称“恶化图像”；它可能平滑误差，但任务因果仍需直接控制。新post的Dice尚待[独立CPU任务合同](VS_SEG_POST_RESIZE_TASK_CPU_PLAN_2026-10-03.md)，不在本报告推断。','',
            '## 5. 可复核范围和下一步','',
            'NMSE沿用旧float32差后float64归一化；pipeline/post输出差另用float64，二者不可混称。独立复核共享native decoder、observed min/max/skimage和RNG；采用另一Hermite公式、另一post构造、fresh ROI dot-product、math.fsum、标量bootstrap和手写分位，不是全软件栈独立，更不是新患者验证。','',
            'PCHIP顺序在本项目确有数值效应，但当前图像均值证据不支持将其作为主要创新或解释全部Dice差。继续直接测post条件的冻结任务输出，随后准备跨输入训练矩阵和另一个任务评估器；未来新方法必须使用未参与选择的患者。原网格旁路/特征重采样等宽创新已被[本批三篇正文](literature/2026-10-03_resampling_order_fulltext_reading.md)排除。','',
            '[全部36端点CSV](experiments/vs_seg_resampling_order_cpu/all36_descriptive_endpoints.csv)；[全部患者与逐层结果](experiments/vs_seg_resampling_order_cpu/attempt_01.json)；[独立复核](experiments/vs_seg_resampling_order_cpu/independent_replay_attempt_01.json)；[计划](VS_SEG_RESAMPLING_ORDER_CPU_PLAN_2026-10-03.md)。']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    write(OUT/'report_provenance.json',dict(result_sha256=sha(OUT/'attempt_01.json'),proof_sha256=sha(OUT/'independent_replay_attempt_01.json'),script_sha256=sha(__file__),report_sha256=sha(REPORT),csv_sha256=sha(p),means=means,order_patient_summary=order,descriptive_support_order_fraction=fraction,publication_claim_confirmed=False))
    print(json.dumps(dict(report=str(REPORT),all_endpoints=36,all_patients=45,post_task_result_included=False,errors=[]),ensure_ascii=False))

if __name__=='__main__': main()
