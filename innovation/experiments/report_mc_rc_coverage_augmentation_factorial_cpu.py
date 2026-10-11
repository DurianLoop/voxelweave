"""Report all four fixed arms, descriptive contrasts and a standalone scientific plot."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/mc_rc_coverage_augmentation_factorial_cpu'
ARMS = ('legacy_aug', 'legacy_none', 'coverage_aug', 'coverage_none')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def contrasts(values):
    la, ln, ca, cn = [values[k] for k in ARMS]
    if any(x is None for x in (la, ln, ca, cn)):
        return {key: None for key in ('coverage_when_aug', 'coverage_when_none',
            'augmentation_when_legacy', 'augmentation_when_coverage', 'coverage_mean_difference',
            'augmentation_mean_difference', 'coverage_x_augmentation_difference_in_differences')}
    return dict(coverage_when_aug=ca-la, coverage_when_none=cn-ln,
        augmentation_when_legacy=la-ln, augmentation_when_coverage=ca-cn,
        coverage_mean_difference=((ca-la)+(cn-ln))/2,
        augmentation_mean_difference=((la-ln)+(ca-cn))/2,
        coverage_x_augmentation_difference_in_differences=(ca-cn)-(la-ln))


def format_value(value):
    return 'undefined' if value is None else str(value) if isinstance(value, int) else '%.9f' % value


def main():
    from vs_seg_task_cpu_support import resource_gate
    resource_gate()
    source = OUT / 'attempt_01.json'
    proof = OUT / 'independent_all_arms_metrics_draws_checkpoint_attempt_01.json'
    r, q = read(source), read(proof)
    assert r['complete'] and q['complete'] and not r['errors'] and not q['errors']
    assert q['result_sha256'] == sha(source) and q['checkpoint_replayed_planes'] == 12
    dpath = ROOT / r['source_bindings'][0]['path']
    d = read(dpath)
    assert sha(dpath) == r['source_bindings'][0]['sha256']
    arms = {a['name']: a for a in r['arms']}
    assert tuple(arms) == ARMS
    fields = ('dice', 'precision', 'recall', 'signed_relative_volume_error',
              'absolute_relative_volume_error', 'tp', 'fp', 'fn')
    summary = {}
    for domain in ('full', 'missing', 'anchors', 'tail'):
        summary[domain] = {field: contrasts({name: arms[name]['evaluation']['metrics'][domain][field]
                            for name in ARMS}) for field in fields}
    for field in ('assd_mm', 'hd95_mm'):
        summary[field] = contrasts({name: arms[name]['evaluation']['metrics']['full_surface'][field]
                                   for name in ARMS})
    stats = {name: dict(mean=sum(d['foreground_mass_by_arm'][name])/4000,
             total=sum(d['foreground_mass_by_arm'][name]),
             zero_foreground_updates=sum(value == 0 for value in d['foreground_mass_by_arm'][name])) for name in ARMS}
    analysis = dict(created_utc=datetime.now(timezone.utc).isoformat(), script_sha256=sha(__file__),
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for p in (source, proof, dpath)],
        contrasts=summary, foreground_exposure=stats, training_patients=1, training_seeds=1,
        descriptive_only=True, patient_inference_performed=False, scientific_confirmation_patients=0,
        publication_claim_confirmed=False)
    ap = OUT / 'descriptive_factorial_analysis.json'
    assert not ap.exists()
    ap.write_text(json.dumps(analysis, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines = ['# 单012覆盖×增强：固定预算完整结果', '',
        '四臂全部完成并独立复核。三臂从头各4000步，共12000新训练更新；legacy_aug 精确匹配旧4000输入后复用，零新训练/生产前向。单个已见开发患者、单seed，无患者显著性、泛化或重建方法收益结论。', '',
        '预写 fit gate：full/missing Dice≥.90、full recall≥.90、full absRVE≤.10。最后checkpoint、完整native FOV/72层、阈值.5，不使用GT裁剪/后处理。', '',
        '| 条件 | full Dice | missing Dice | recall | precision | signed RVE | absRVE | ASSD mm | HD95 mm | fit gate |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for name in ARMS:
        e=arms[name]['evaluation']; m=e['metrics']; f=m['full']; s=m['full_surface']
        values = [name, f['dice'], m['missing']['dice'], f['recall'], f['precision'],
                  f['signed_relative_volume_error'], f['absolute_relative_volume_error'], s['assd_mm'], s['hd95_mm']]
        lines.append('| '+' | '.join(v if isinstance(v,str) else format_value(v) for v in values)+' | '+('通过' if e['fit_gate_passed'] else '失败')+' |')
    lines += ['', '## 全部域的计数和指标', '',
        '| 条件/域 | TP | FP | FN | GT | pred | Dice | precision | recall | signed RVE | absRVE | 空GT/预测 |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for name in ARMS:
        for domain in ('full','missing','anchors','tail'):
            m=arms[name]['evaluation']['metrics'][domain]
            values=[m[k] for k in ('tp','fp','fn','gt_foreground','pred_foreground','dice','precision','recall',
                                   'signed_relative_volume_error','absolute_relative_volume_error')]
            lines.append('| '+name+'/'+domain+' | '+' | '.join(map(format_value,values))+' | '+str(m['empty_ground_truth'])+'/'+str(m['empty_prediction'])+' |')
    lines += ['', '## 描述性因子差', '',
        'C=覆盖(1)/原采样(0)，A=增强开(1)/关(0)。覆盖主差平均 C1−C0；增强主差平均 A1−A0；交互=(coverage_aug−coverage_none)−(legacy_aug−legacy_none)。Dice 为绝对差，乘100才是百分点；距离/RVE是原量纲，负值通常表示降低。这些是固定单病例的数值分解，无误差条/患者p值。', '',
        '| 指标 | 覆盖差(增强开) | 覆盖差(增强关) | 增强差(原采样) | 增强差(覆盖) | 覆盖主差 | 增强主差 | 差中之差 |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    keys=('coverage_when_aug','coverage_when_none','augmentation_when_legacy','augmentation_when_coverage',
          'coverage_mean_difference','augmentation_mean_difference','coverage_x_augmentation_difference_in_differences')
    for domain, field in (('full','dice'),('missing','dice'),('full','recall'),('full','precision'),
                           ('full','absolute_relative_volume_error'),('', 'assd_mm'),('', 'hd95_mm')):
        row=summary[domain][field] if domain else summary[field]
        lines.append('| '+(domain+'/'+field if domain else field)+' | '+' | '.join(format_value(row[k]) for k in keys)+' |')
    lines += ['', '## 曝光与核验边界', '',
        '| 条件 | 两patch平均前景mass | 总mass | 零前景updates |', '|---|---:|---:|---:|']
    for name in ARMS:
        lines.append('| '+name+' | '+format_value(stats[name]['mean'])+' | '+format_value(stats[name]['total'])+' | '+str(stats[name]['zero_foreground_updates'])+' |')
    lines += ['',
        '覆盖采样改变了前景曝光，不能称两类采样仅空间覆盖不同而前景量相同。增强开关共享同原空间支撑，关闭的是几何+强度整个bundle，不能定位单一操作。全部72z均出现，逐z19–96更新，覆盖每z16tile都被访问。', '',
        '原draw独立核16000输入SHA与16000完整patch源像素映射；本核验再次逐项绑定四臂16000训练输入SHA，独立重读标签/计数/完整affine表面距离，并同架构不同几何代码重放4×3完整plane，全体素相同。重放不是第二独立训练模型或新患者确认。', '',
        '本次生产分支调用：global '+str(r['global_forward_calls'])+'，local '+str(r['local_forward_calls'])+
        '；核验：global '+str(q['global_forward_calls'])+'，local '+str(q['local_forward_calls'])+
        '。复用旧臂的旧训练/评估不再次计作新调用。GPU初始化0、确认效果0。', '',
        '至少一臂通过仅说明当前实现能拟合这一完整训练病例；多患者/四验证能力仍需单独固定协议。正式native与6×5公平矩阵、直接任务/随机分辨率、observed-only修正与八患者确认未执行。', '',
        '来源：[生产](experiments/mc_rc_coverage_augmentation_factorial_cpu/attempt_01.json)、[独立核验](experiments/mc_rc_coverage_augmentation_factorial_cpu/independent_all_arms_metrics_draws_checkpoint_attempt_01.json)、[全部描述性分析](experiments/mc_rc_coverage_augmentation_factorial_cpu/descriptive_factorial_analysis.json)、[协议](MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_PROTOCOL_2026-10-03.md)、[两篇阅读](literature/2026-10-03_coverage_augmentation_followup_fulltext_reading.md)。', '',
        '科学图：[PNG](figures/mc_rc_coverage_augmentation_factorial_cpu/dice_factorial.png)、[SVG](figures/mc_rc_coverage_augmentation_factorial_cpu/dice_factorial.svg)。']
    report=ROOT/'MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_RESULT_2026-10-03.md'
    assert not report.exists()
    report.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    # Publication-style static visualization; no model calls or exploratory endpoint selection.
    import os
    figdir=ROOT/'figures/mc_rc_coverage_augmentation_factorial_cpu'
    figdir.mkdir(parents=True,exist_ok=False)
    os.environ['MPLCONFIGDIR']=str(ROOT/'figures/mc_rc_coverage_augmentation_factorial_cpu/mplconfig')
    os.environ['OMP_NUM_THREADS']='1'
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes=plt.subplots(1,2,figsize=(9,4),sharey=True)
    for ax, domain in zip(axes,('full','missing')):
        for prefix, color, label in (('legacy','#2563eb','Legacy sampling'),('coverage','#e27524','Coverage sampling')):
            values=[arms[prefix+suffix]['evaluation']['metrics'][domain]['dice'] for suffix in ('_none','_aug')]
            ax.plot([0,1],values,'o-',color=color,label=label,linewidth=2)
            for x,value in enumerate(values):
                ax.annotate('%.3f'%value,(x,value),xytext=(0,7),textcoords='offset points',ha='center',fontsize=9)
        ax.axhline(.90,color='#777777',linestyle='--',linewidth=1)
        ax.set_xticks([0,1],['Augmentation off','Augmentation on'])
        ax.set_title('Full native volume' if domain=='full' else 'Supported missing slices')
        ax.set_ylim(0,1.045);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Dice (training patient 012)');axes[1].legend(loc='lower left',frameon=False)
    fig.suptitle('Fixed 4,000-update factorial: one patient, one seed',fontsize=12)
    fig.tight_layout()
    outputs=[]
    for suffix in ('png','svg'):
        fp=figdir/('dice_factorial.'+suffix)
        fig.savefig(fp,dpi=180,bbox_inches='tight')
        outputs.append(dict(path=fp.relative_to(ROOT).as_posix(),sha256=sha(fp)))
    plt.close(fig)
    provenance=dict(script_sha256=sha(__file__),source_bindings=analysis['source_bindings'],outputs=outputs,
                    report_file=report.relative_to(ROOT).as_posix(),report_sha256=sha(report),scientific_inference=False)
    (figdir/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(report_file=report.relative_to(ROOT).as_posix(),fit_gates={n:arms[n]['evaluation']['fit_gate_passed'] for n in ARMS},
        new_training_updates=r['new_training_updates_completed'],complete=True)))


if __name__=='__main__':
    main()
