"""Read completed last checkpoints' results only; preserve every original gate/domain."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    lowpath=ROOT/'experiments/mc_rc_3d_backbone_context_low_lr_2026_10_07/attempt01.json'
    highpath=ROOT/'experiments/mc_rc_3d_backbone_context_refit_v2_2026_10_07/attempt01.json'
    proofpath=lowpath.parent/'independent_both1024_and_full_fov_attempt01.json'
    exits=read(ROOT/'SESSION_OBSERVED_EXITS_LOW_LR_CONTEXT_2026-10-07.json');low,high,proof=read(lowpath),read(highpath),read(proofpath)
    assert all(d['complete'] and not d['errors'] for d in (low,high,proof))
    assert exits['training_observed_tool_exit']==exits['independent_verifier_observed_tool_exit']==0
    assert exits['training_result_sha256']==sha(lowpath) and exits['verifier_result_sha256']==sha(proofpath)
    assert proof['result_sha256']==sha(lowpath)
    rows=[]
    for learning_rate,data in ((.001,high),(.0001,low)):
        for arm in data['arms']:
            rows.append(dict(learning_rate=learning_rate,kind=arm['kind'],full_metrics=arm['metrics']['full'],
                all_domains=arm['metrics'],original_augmented_crops=arm['original_augmented_patch_metrics'],
                original_fit_gate=arm['training_fit_gate'],fit_gate_passed=arm['training_fit_gate_passed']))
    def value(v):return 'undefined' if v is None else f'{v:.6f}'
    lines=['# 低学习率完整 context 对照：实测结果','',
        '两臂各1024次全骨干更新，共2048次CPU更新；原session89014已实际退出0，独立module/functional、完整history/GT流、四域计数及坐标重放亦实际退出0。没有重启该训练，GPU更新0。两臂均在评分前保存最后模型，阈值.5，原gate不改。',
        '', '## 单开发series的同初始化/同流LR控制','',
        '| LR | 输入 | full Dice | recall | absRVE | 原foreground crop Dice | 原背景crop FP | 原拟合gate |',
        '|---:|---|---:|---:|---:|---:|---:|---|']
    for row in rows:
        m=row['full_metrics'];crops=row['original_augmented_crops']
        lines.append(f"| {row['learning_rate']} | {row['kind']} | {value(m['dice'])} | {value(m['recall'])} | {value(m['absRVE'])} | {value(crops[0]['dice'])} | {crops[1]['fp']} | {'通过' if row['fit_gate_passed'] else '失败'} |")
    lines+=['','唯一训练配置变化为恒定LR .001 -> .0001；各臂自身初始checkpoint和128轮完整16tile流相同。从各自初始全tile head模型重启，非从崩塌后权重继续。各臂初始模型此前已用不同图像训练，所以两臂的最终差异不能视为MRI恢复收益；这是标准优化/能力对照，训练患者1、series1、独立科学确认0。旧高LR失败保留。',
        '',f"低LR主训练实测总墙钟 {low['elapsed_seconds']:.2f} 秒；独立核验 {proof['elapsed_seconds']:.2f} 秒。完整原始分母、空值、TP/FP/FN/TN 在下表及原JSON保留。",
        '', '## 低LR四域原始计数','',
        '| 输入 | 域 | GT foreground | pred foreground | TP | FP | FN | TN | Dice | recall | absRVE |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for arm in low['arms']:
        for domain,m in arm['metrics'].items():
            lines.append(f"| {arm['kind']} | {domain} | {m['gt_foreground']} | {m['pred_foreground']} | {m['tp']} | {m['fp']} | {m['fn']} | {m['tn']} | {value(m['dice'])} | {value(m['recall'])} | {value(m['absRVE'])} |")
    lines+=['','## 原门槛与独立坐标状态','']
    for arm,p in zip(low['arms'],proof['arms']):
        lines+=[f"- {arm['kind']} 原gate: `{json.dumps(arm['training_fit_gate'],ensure_ascii=False)}`。",
                f"- {arm['kind']} 生产module/functional重放概率最大差 {p['production_coordinate_replay_max_probability_error']:.9g}，二值差异 {p['production_coordinate_replay_threshold_disagreements']}；生产float32 vs NumPy: `{json.dumps(p['production_float32_vs_numpy_coordinate'])}`；独立float64: `{json.dumps(p['independent_float64_coordinate'])}`。"]
    all_gates=low['both_original_fit_gates_passed'];coords=all(p['production_float32_vs_numpy_coordinate']['original_strict_gate_passed'] for p in proof['arms'])
    eligible=all_gates and coords
    lines+=['',f"19series资源资格启动条件：两臂原拟合gate全部通过={all_gates}；两臂生产float32严格坐标门槛全部通过={coords}；合并条件={eligible}。没有用float64成功替代float32失败。",
        '', '11开发患者/19series、4已见验证/9series、8保留确认/12series角色不变；本训练/重放没有加载新验证或确认效果，也不是正式19series充分适配。下一步资格/诊断按真实合并条件决定，不根据指标临时改变端点。',
        '', '[完整主结果](experiments/mc_rc_3d_backbone_context_low_lr_2026_10_07/attempt01.json) · [独立重放](experiments/mc_rc_3d_backbone_context_low_lr_2026_10_07/independent_both1024_and_full_fov_attempt01.json) · [原协议](MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_CONTROL_PROTOCOL_2026-10-07.md) · [创新收窄](INNOVATION_DECISION_AFTER_DEFER_READING_2026-10-07.md)。']
    report=ROOT/'MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_RESULT_2026-10-07.md'
    with report.open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    directory=ROOT/'figures/mc_rc_3d_backbone_context_low_lr_2026_10_07';directory.mkdir(exist_ok=False)
    data=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),rows=rows,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (lowpath,highpath,proofpath)],
        developmental_patients=1,developmental_series=1,scientific_confirmation_patients=0,publication_claim_confirmed=False,
        formal19series_resource_qualification_eligible=eligible)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,3.8));labels=['native\nLR .001','PCHIP\nLR .001','native\nLR .0001','PCHIP\nLR .0001']
    for ax,title,values in zip(axes,['Complete FOV Dice','Original foreground crop Dice'],
        [[r['full_metrics']['dice'] for r in rows],[r['original_augmented_crops'][0]['dice'] for r in rows]]):
        ax.bar(range(4),values,color=['#315d88','#cc8c2e','#315d88','#cc8c2e']);ax.set_xticks(range(4),labels);ax.set_ylim(0,1.12)
        ax.axhline(.9,color='#ac3047',linestyle='--',linewidth=1,label='Original threshold .90');ax.set_title(title)
        for i,v in enumerate(values):ax.text(i,v+.025,f'{v:.4f}',ha='center',fontsize=9)
        ax.spines[['top','right']].set_visible(False);ax.set_ylabel('Dice');ax.legend(fontsize=8,loc='upper left')
    fig.suptitle('Development fit control: one patient / one series',fontsize=12);fig.tight_layout()
    for suffix in ('png','svg'):fig.savefig(directory/f'last_checkpoint_fit_comparison.{suffix}',dpi=160)
    plt.close(fig)
    with (directory/'plot_data.json').open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(report=report.name,qualification_eligible=eligible,low_lr_fit_gates={a['kind']:a['training_fit_gate_passed'] for a in low['arms']})))
    return 0
if __name__=='__main__':raise SystemExit(main())
