"""All37 single intensity-only results; source-bound report, no causal/publication claim."""
import json,sys
from datetime import datetime,timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mc_rc_global_local_task_cpu_support import ROOT,read,sha


def fmt(x):return 'undefined' if x is None else '%.6f'%x


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    train=ROOT/'experiments/mc_rc_intensity_only_gpu_capability'
    evaluation=ROOT/'experiments/mc_rc_intensity_only_full_task_evaluation_gpu'
    files=[train/'attempt_01.json',train/'independent_all20000_draws_and_checkpoint_attempt_01.json',
        evaluation/'attempt_01.json',evaluation/'independent_all37_metrics_and111_planes_attempt_01.json',
        ROOT/'experiments/mc_rc_no_augmentation_full_task_evaluation_gpu/attempt_01.json']
    t,tq,r,q,old=[read(p) for p in files]
    assert all(v['complete'] and not v['errors'] for v in (t,tq,r,q,old))
    assert tq['result_sha256']==sha(files[0]) and q['result_sha256']==sha(files[2])
    assert tq['intensity_reference_example_checks']==20000 and tq['full_patch_source_mapping_checks']==40000
    assert q['checkpoint_replayed_planes']==111
    output=ROOT/'MC_RC_INTENSITY_ONLY_FULL_TASK_RESULT_2026-10-03.md';assert not output.exists()
    figdir=ROOT/'figures/mc_rc_intensity_only_full_task';figdir.mkdir(exist_ok=False)
    lines=['# 单配方intensity-only GPU20k：完整能力结果','',
        '**原能力gate：'+('通过' if r['capability_gate_passed'] else '未通过')+'。** 四验证已经见过，科学确认0；这个单GPU配方不是完成四因素或新重建方法。','',
        '同初权重a146c0c4.../981602参数/seed20261004、11开发19series、真实observed-only raw PCHIP/observed_shared、原空间patch支撑与patient/series/z/patch外生流；只用scale [.9,1.1]/shift [-.1,.1]，不做D4。固定20000、原loss/AdamW/cosine、最后checkpoint/.5，没有模型预训练或中途验证。','',
        '训练network/context grid_sample/loss在GPU，physical/标签/坐标生成在CPU；评价网络GPU、context/融合/概率映射CPU。synthetic值/梯度/loss预检通过，CUDAgrid backward不保证整个训练逐位确定；CPU旧noaug与GPU新intensity的比较只作描述。全部20000新tensor reference/旧sampler/primitive/RNG及40000整patch/最后权重独立认证通过，0额外训练/前向。','',
        '| 队列/输入 | full Dice | missing Dice | recall | precision | absRVE | TP0 | 全空 |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for group in ('development','validation'):
        for method,a in r[group+'_aggregate'].items():
            f=a['patient_first_means']['full'];m=a['patient_first_means']['missing']
            lines.append('| %s/%s | %s | %s | %s | %s | %s | %d | %d |'%(group,method,fmt(f['dice']),fmt(m['dice']),fmt(f['recall']),fmt(f['precision']),fmt(f['absolute_relative_volume_error']),len(a['complete_miss_series']),len(a['empty_prediction_series'])))
    lines+=['','| 原gate | 结果 |','|---|---|']
    for k,v in r['capability_gate_checks'].items():lines.append('| %s | %s |'%(k,'通过' if v else '失败'))
    lines+=['','## 全部患者均值','','按患者内series平均，再患者等权；None不缩小分母。','',
        '| 队列/患者/输入 | series | full Dice | missing Dice | recall | absRVE |','|---|---:|---:|---:|---:|---:|']
    for group in ('development','validation'):
        for method,a in r[group+'_aggregate'].items():
            for patient,v in a['patients'].items():
                f=v['metrics']['full'];m=v['metrics']['missing']
                lines.append('| %s/%s/%s | %d | %s | %s | %s | %s |'%(group,patient,method,v['series'],fmt(f['dice']),fmt(m['dice']),fmt(f['recall']),fmt(f['absolute_relative_volume_error'])))
    lines+=['','## 全部37预测','','| 队列/患者/UID/输入 | full Dice | missing Dice | TP | FP | FN | ASSD | HD95 | tail FP |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for e in r['evaluations']:
        m=e['metrics'];f=m['full'];s=m['full_surface']
        lines.append('| %s/%s/%s/%s | %s | %s | %d | %d | %d | %s | %s | %d |'%(e['group'],e['patient'],e['uid'],e['method'],fmt(f['dice']),fmt(m['missing']['dice']),f['tp'],f['fp'],f['fn'],fmt(s['assd_mm']),fmt(s['hd95_mm']),m['tail']['fp']))
    lines+=['','## 原无增强的描述性参考','','两训练执行设备不同，单seed、已见验证，不作增强因素的精确因果或显著性。','',
        '| 队列/指标 | 原CPU无增强、GPU评分 | 新GPU仅强度、GPU评分 | 差 |','|---|---:|---:|---:|']
    for group in ('development','validation'):
        for domain,field in (('full','dice'),('missing','dice'),('full','recall'),('full','absolute_relative_volume_error')):
            a=old[group+'_aggregate']['raw_pchip']['patient_first_means'][domain][field]
            b=r[group+'_aggregate']['raw_pchip']['patient_first_means'][domain][field]
            lines.append('| %s/%s/%s | %s | %s | %s |'%(group,domain,field,fmt(a),fmt(b),fmt(b-a) if a is not None and b is not None else 'undefined'))
    lines+=['','训练global/local各20000；37评价%d/%d，111独立重放%d/%d。全四域/空/undefined及原生label/source/code/protocol/checkpoint SHA保留JSON；边界完整affine欧氏距离，不用正交EDT近似。'%(r['global_forward_calls'],r['local_forward_calls'],q['global_forward_calls'],q['local_forward_calls']),
        '', '能力充分后才原生/公平矩阵与具体observable残余，'+('当前可以准备下一强对照。' if r['capability_gate_passed'] else '当前仍需继续任务能力开发，不能据弱模型解释SR危害。'),
        '', '原GPU80k两资源失败各10updates仍保留；本单20k不等于四臂80k/148/444完成。八确认/第二独立训练任务网络未启用，没有可发表且独立确认新claim。',
        '', '原件：[训练](experiments/mc_rc_intensity_only_gpu_capability/attempt_01.json)、[20000draw核验](experiments/mc_rc_intensity_only_gpu_capability/independent_all20000_draws_and_checkpoint_attempt_01.json)、[37评价](experiments/mc_rc_intensity_only_full_task_evaluation_gpu/attempt_01.json)、[111plane核验](experiments/mc_rc_intensity_only_full_task_evaluation_gpu/independent_all37_metrics_and111_planes_attempt_01.json)。']
    output.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
    for ax,group in zip(axes,('development','validation')):
        new=r[group+'_aggregate']['raw_pchip'];previous=old[group+'_aggregate']['raw_pchip'];patients=sorted(new['patients']);xx=list(range(len(patients)))
        a=[previous['patients'][p]['metrics']['full']['dice'] for p in patients]
        b=[new['patients'][p]['metrics']['full']['dice'] for p in patients]
        for i,x,y in zip(xx,a,b):ax.plot([i,i],[x,y],c='#bbc0c8',lw=1)
        ax.scatter(xx,a,color='#647a86',s=35,label='No augmentation (CPU train)')
        ax.scatter(xx,b,color='#157a78',s=35,label='Intensity only (GPU train)')
        ax.set_xticks(xx,[p[-3:] for p in patients]);ax.set_ylim(-.03,1.03)
        ax.set_title('Training patients' if group=='development' else 'Previously used validation patients')
        ax.set_xlabel('Patient; series averaged within patient');ax.set_ylabel('Full-volume Dice');ax.grid(axis='y',alpha=.2)
        ax.spines[['top','right']].set_visible(False)
    axes[1].legend(loc='upper left',fontsize=8)
    fig.suptitle('Capability development: different training devices; one seed',fontsize=12)
    png=figdir/'patient_dice.png';svg=figdir/'patient_dice.svg';fig.savefig(png,dpi=180);fig.savefig(svg);plt.close(fig)
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in files],
        report_file=output.relative_to(ROOT).as_posix(),report_sha256=sha(output),
        outputs=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (png,svg)],
        scientific_confirmation_patients=0,publication_claim_confirmed=False)
    (figdir/'provenance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(report=output.relative_to(ROOT).as_posix(),capability_gate_passed=r['capability_gate_passed'],
        development_full_dice=r['development_aggregate']['raw_pchip']['patient_first_means']['full']['dice'],
        validation_full_dice=r['validation_aggregate']['raw_pchip']['patient_first_means']['full']['dice'])))


if __name__=='__main__':main()
