"""Publish all37 results only after completed training and independent111-plane checks."""
import json,sys
from datetime import datetime,timezone
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mc_rc_global_local_task_cpu_support import ROOT,read,sha


def f(value):return 'undefined' if value is None else '%.6f'%value


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    evaldir=ROOT/'experiments/mc_rc_no_augmentation_full_task_evaluation_gpu'
    paths=[ROOT/'experiments/mc_rc_no_augmentation_all_development_cpu/attempt_01.json',
        ROOT/'experiments/mc_rc_no_augmentation_all_development_cpu/independent_all20000_draws_and_checkpoint_attempt_01.json',
        evaldir/'attempt_01.json',evaldir/'independent_all37_metrics_and111_planes_attempt_01.json',
        ROOT/'experiments/mc_rc_global_local_task_validation_cpu/attempt_01.json',
        ROOT/'experiments/mc_rc_frozen_global_local_development_diagnosis_cpu_attempt02/attempt_01.json',
        ROOT/'experiments/mc_rc_no_augmentation_checkpoint_device_spotcheck/attempt_01.json']
    t,tq,r,q,oldval,olddev,spot=[read(p) for p in paths]
    assert all(v['complete'] and not v['errors'] for v in (t,tq,r,q,oldval,olddev,spot))
    assert tq['result_sha256']==sha(paths[0]) and q['result_sha256']==sha(paths[2])
    assert tq['full_patch_source_mapping_checks']==40000 and q['checkpoint_replayed_planes']==111
    figdir=ROOT/'figures/mc_rc_no_augmentation_full_task';figdir.mkdir(exist_ok=False)
    report=ROOT/'MC_RC_NO_AUGMENTATION_FULL_TASK_RESULT_2026-10-03.md';assert not report.exists()
    passed=r['capability_gate_passed']
    lines=['# 无增强20k完整任务能力：开发与四验证结果','',
        '**原能力门槛：'+('通过' if passed else '未通过')+'。** 这是任务基线能力开发；四验证已用，八确认效果关闭，尚无可发表且独立确认的新claim。','',
        '11开发患者19系列，从头981602参数、seed20261004、固定20000更新，最后checkpoint/.5。输入为observed-only raw PCHIP/observed_shared，native完整标签监督。原初权重/采样外生流/架构/loss/优化器/预算保留，仅关闭整个增强bundle；不能从本轮分离几何与强度因素。','',
        '用户随后明确允许GPU。原CPU训练完成后，全部20000draw/RNG/旧增强SHA/新reference SHA/primitive及40000完整patch支撑和最后权重独立核验通过。37完整输入使用GPU计算global/local网络分支，context/resize/grid_sample/融合/native概率映射沿用冻结CPU几何；float32/TF32关闭/无AMP。原CPU37评价是保留且未执行的准备方案。','',
        '以下开发是训练内诊断、四验证是已见开发验证；每患者先平均其series，再患者等权。undefined保持原分母，不能选择性删除。','',
        '| 队列/输入 | full Dice | missing Dice | recall | precision | absRVE | TP=0系列 | 空预测系列 |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for group,methods in (('development',('raw_pchip',)),('validation',('raw_pchip','raw_linear'))):
        for method in methods:
            a=r[group+'_aggregate'][method];v=a['patient_first_means'];full=v['full']
            lines.append('| %s/%s | %s | %s | %s | %s | %s | %d | %d |'%(group,method,f(full['dice']),f(v['missing']['dice']),f(full['recall']),f(full['precision']),f(full['absolute_relative_volume_error']),len(a['complete_miss_series']),len(a['empty_prediction_series'])))
    lines+=['','| 预写检查 | 结果 |','|---|---|']
    for name,value in r['capability_gate_checks'].items():lines.append('| %s | %s |'%(name,'通过' if value else '失败'))
    lines+=['','## 全患者结果','','| 队列/患者/输入 | series | full Dice | missing Dice | recall | absRVE |','|---|---:|---:|---:|---:|---:|']
    for group,methods in (('development',('raw_pchip',)),('validation',('raw_pchip','raw_linear'))):
        for method in methods:
            for patient,v in r[group+'_aggregate'][method]['patients'].items():
                full=v['metrics']['full'];missing=v['metrics']['missing']
                lines.append('| %s/%s/%s | %d | %s | %s | %s | %s |'%(group,patient,method,v['series'],f(full['dice']),f(missing['dice']),f(full['recall']),f(full['absolute_relative_volume_error'])))
    lines+=['','## 全部37完整预测','','| 队列/患者/UID/输入 | full Dice | missing Dice | TP | FP | FN | ASSD mm | HD95 mm | tail FP |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for e in r['evaluations']:
        m=e['metrics'];full=m['full'];surface=m['full_surface']
        lines.append('| %s/%s/%s/%s | %s | %s | %d | %d | %d | %s | %s | %d |'%(e['group'],e['patient'],e['uid'],e['method'],f(full['dice']),f(m['missing']['dice']),full['tp'],full['fp'],full['fn'],f(surface['assd_mm']),f(surface['hd95_mm']),m['tail']['fp']))
    domains={}
    for group in ('development','validation'):
        domains[group]={}
        for method in r[group+'_aggregate']:
            rows=[e for e in r['evaluations'] if e['group']==group and e['method']==method]
            domains[group][method]={d:dict(tp=sum(e['metrics'][d]['tp'] for e in rows),
                fp=sum(e['metrics'][d]['fp'] for e in rows),fn=sum(e['metrics'][d]['fn'] for e in rows),
                empty_ground_truth_series=sum(e['metrics'][d]['empty_ground_truth'] for e in rows),
                empty_prediction_series=sum(e['metrics'][d]['empty_prediction'] for e in rows),
                dice_undefined_series=sum(e['metrics'][d]['dice'] is None for e in rows),
                recall_undefined_series=sum(e['metrics'][d]['recall'] is None for e in rows)) for d in ('full','missing','anchors','tail')}
    lines+=['','## 四域计数与空结果','','总计数是series合计，能力端点仍按患者等权，二者不得混用。','',
        '| 队列/输入/域 | TP | FP | FN | GT空series | 预测空series | Dice undefined | recall undefined |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for group,methods in domains.items():
        for method,rows in methods.items():
            for d,v in rows.items():lines.append('| %s/%s/%s | %s |'%(group,method,d,' | '.join(str(x) for x in v.values())))
    newdev=r['development_aggregate']['raw_pchip']['patient_first_means']['full']['dice']
    newval=r['validation_aggregate']['raw_pchip']['patient_first_means']['full']['dice']
    prior_dev=olddev['aggregate']['patient_first_means']['full']['dice']
    prior_val=oldval['aggregate']['raw_pchip']['patient_first_means']['full']['dice']
    lines+=['','## 与旧增强配方的描述性比较','',
        '旧同容量/seed/20k配方的训练内full Dice %s→%s，四验证full Dice %s→%s。只有一个训练seed，四验证此前已看过；旧评分CPU、新评分GPU，合成运行库预检的概率误差较小，但尚未对37完整患者输入作逐值跨设备复现。此比较不证明群体因果、统计显著性、去增强泛化优越或重建方法创新。'%(f(prior_dev),f(newdev),f(prior_val),f(newval)),
        '', '111完整plane使用同GPUcheckpoint、独立NumPy物理坐标/context/pixel-center及全部37独立label/bincount/full-affine surface核验。primitive与距离库有共享；这是实现复核，不是第二独立训练任务网络。',
        '', '另有固定首开发/首验证series各首中末共6完整plane的同checkpoint CPU/GPU核对，mask不一致体素%d，六张CPU mask中%d张有预测前景。只核这些阈值mask，没有核全部37体积的概率一致；不作为准确率证明。CPU与GPU各global/local %d/%d次另计。'%(spot['mismatched_voxels'],sum(p['cpu_foreground_voxels']>0 for p in spot['planes']),spot['cpu_global_forward_calls'],spot['cpu_local_forward_calls']), '',
        '训练global/local各20000次；37评价global/local %d/%d次，111plane复核%d/%d次。GPU合成预检另有global/local各2次，不计为患者效果。'%(r['global_forward_calls'],r['local_forward_calls'],q['global_forward_calls'],q['local_forward_calls']),
        '', '两个partial因素臂已完成608draw/1216新输入的零前向预检，但没有新训练结果。'+('下一步先原生能力控制和同信息公平矩阵。' if passed else '门槛未过，先继续任务能力开发；不能用本模型给SR损害或选择性修正的科学结论。'),
        '', '文献两篇/185块原始正文见[阅读报告](literature/2026-10-03_no_augmentation_task_fulltext_reading.md)。TTA不确定性、物理伪影增强、直接任务对恢复已有先例，精确剩余问题见后续创新判断。','',
        '原件：[训练](experiments/mc_rc_no_augmentation_all_development_cpu/attempt_01.json)、[20000draw核验](experiments/mc_rc_no_augmentation_all_development_cpu/independent_all20000_draws_and_checkpoint_attempt_01.json)、[37评价](experiments/mc_rc_no_augmentation_full_task_evaluation_gpu/attempt_01.json)、[111plane核验](experiments/mc_rc_no_augmentation_full_task_evaluation_gpu/independent_all37_metrics_and111_planes_attempt_01.json)。']
    report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
    fig,axes=plt.subplots(1,2,figsize=(11,4.4),layout='constrained')
    for ax,group,old in zip(axes,('development','validation'),(olddev['aggregate'],oldval['aggregate']['raw_pchip'])):
        new=r[group+'_aggregate']['raw_pchip'];patients=sorted(new['patients']);xx=list(range(len(patients)))
        before=[old['patients'][p]['metrics']['full']['dice'] for p in patients]
        after=[new['patients'][p]['metrics']['full']['dice'] for p in patients]
        for i,a,b in zip(xx,before,after):ax.plot([i,i],[a,b],color='#b1b6be',lw=1)
        ax.scatter(xx,before,s=34,color='#b67b3e',label='Legacy augmentation (CPU)')
        ax.scatter(xx,after,s=34,color='#237b91',label='No augmentation (GPU)')
        if group=='validation':ax.axhline(.70,color='#6f777f',ls='--',lw=1,label='Mean gate: 0.70')
        ax.set_xticks(xx,[p[-3:] for p in patients]);ax.set_ylim(-.035,1.03)
        ax.set_title('Training patients' if group=='development' else 'Previously used validation patients')
        ax.set_xlabel('Patient; series averaged within patient');ax.set_ylabel('Full-volume Dice')
        ax.grid(axis='y',alpha=.18);ax.spines[['top','right']].set_visible(False)
    axes[1].legend(loc='upper left',fontsize=8)
    fig.suptitle('Capability development: one seed; no independent scientific confirmation',fontsize=12)
    png=figdir/'patient_dice.png';svg=figdir/'patient_dice.svg'
    fig.savefig(png,dpi=180);fig.savefig(svg);plt.close(fig)
    outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (png,svg)]
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths],
        report_file=report.relative_to(ROOT).as_posix(),report_sha256=sha(report),outputs=outputs,
        descriptive_old_new_full_dice=dict(development=[prior_dev,newdev],validation=[prior_val,newval]),
        domains=domains,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    (figdir/'provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(report=report.relative_to(ROOT).as_posix(),capability_gate_passed=passed,
        full_development_dice=newdev,full_validation_dice=newval,figures=outputs)))


if __name__=='__main__':main()
